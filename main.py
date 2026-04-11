import os
from pathlib import Path as _Path
from dotenv import load_dotenv
load_dotenv(_Path(__file__).resolve().parent / ".env")

import asyncio
import requests
from datetime import datetime
from uuid import uuid4
from pathlib import Path
from fastapi import FastAPI, Form, Request, UploadFile, File, Depends, Query
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from xai_sdk import Client
from typing import Optional

from auth import APP_PASSWORD, check_rate_limit, record_failed_attempt, clear_attempts

app = FastAPI(title="MenguyGen")
BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Session middleware
SESSION_SECRET = os.getenv("SESSION_SECRET", "dev-secret-change-in-production")
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET)

# API xAI
api_key = os.getenv("XAI_API_KEY")
if not api_key:
    raise ValueError("XAI_API_KEY non trouvée dans les variables d'environnement !")

client = Client(api_key=api_key)

# Répertoire de sauvegarde configurable
SAVE_DIR = os.getenv("SAVE_DIR", os.path.join(os.getcwd(), "downloads"))
os.makedirs(SAVE_DIR, exist_ok=True)

# Upload : types autorisés et taille max (10 Mo)
ALLOWED_MIME_TYPES = {"image/png", "image/jpeg", "image/webp"}
MAX_UPLOAD_SIZE = 10 * 1024 * 1024


# --- Vérification d'authentification (dépendance) ---

async def require_auth(request: Request):
    if not request.session.get("authenticated") and not request.session.get("guest"):
        raise RedirectException()

class RedirectException(Exception):
    pass

class GuestKeyMissing(Exception):
    """Raised when a guest tries to generate without providing an API key."""
    pass

@app.exception_handler(RedirectException)
async def redirect_to_login(request: Request, exc: RedirectException):
    return RedirectResponse("/auth/login")

@app.exception_handler(GuestKeyMissing)
async def redirect_to_guest(request: Request, exc: GuestKeyMissing):
    return RedirectResponse("/guest")


# --- Routes d'authentification ---

@app.get("/auth/login", response_class=HTMLResponse)
async def auth_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/auth/check")
async def auth_check(request: Request, password: str = Form(...)):
    client_ip = request.client.host if request.client else "unknown"

    if check_rate_limit(client_ip):
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Trop de tentatives. Réessayez dans 5 minutes."
        })

    if password == APP_PASSWORD:
        clear_attempts(client_ip)
        request.session["authenticated"] = True
        return RedirectResponse("/", status_code=303)

    record_failed_attempt(client_ip)
    return templates.TemplateResponse("login.html", {
        "request": request,
        "error": "Mot de passe incorrect."
    })


@app.get("/auth/logout")
async def auth_logout(request: Request):
    request.session.clear()
    return RedirectResponse("/auth/login")


# --- Mode invité ---

@app.get("/guest", response_class=HTMLResponse)
async def guest_page(request: Request):
    return templates.TemplateResponse("guest.html", {"request": request})


@app.post("/auth/guest")
async def auth_guest(request: Request):
    request.session["guest"] = True
    return RedirectResponse("/", status_code=303)


# --- Helpers ---

def _get_client(request: Request, api_key: Optional[str] = None) -> Client:
    """Return a per-request Client for guests, or the global client for admins."""
    if request.session.get("guest"):
        if not api_key:
            raise GuestKeyMissing()
        return Client(api_key=api_key)
    return client

def _download_media(url: str, filepath: str):
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    with open(filepath, 'wb') as f:
        f.write(response.content)


ALLOWED_ASPECT_RATIOS = {
    "1:1", "4:3", "3:4", "16:9", "9:16",
    "3:2", "2:3", "2:1", "1:2",
    "19.5:9", "9:19.5", "20:9", "9:20", "auto"
}
ALLOWED_RESOLUTIONS = {"1k", "2k"}

MODEL_CONFIG = {
    "standard": {
        "model_id": "grok-imagine-image",
        "label": "Standard",
        "price": 0.02,
        "rpm": 300,
        "archived": False,
    },
    "pro": {
        "model_id": "grok-imagine-image-pro",
        "label": "Pro",
        "price": 0.07,
        "rpm": 30,
        "archived": False,
    },
}
ALLOWED_MODELS = {k: v["model_id"] for k, v in MODEL_CONFIG.items()}

VIDEO_CONFIG = {
    "model_id": "grok-imagine-video",
    "price_per_second": 0.05,
    "rpm": 60,
    "min_duration": 1,
    "max_duration": 15,
    "resolutions": ["480p", "720p"],
}
ALLOWED_VIDEO_RESOLUTIONS = {"480p", "720p"}


def _add_to_history(request: Request, entry_type: str, urls: list, prompt: str):
    if "history" not in request.session:
        request.session["history"] = []
    request.session["history"].insert(0, {
        "type": entry_type,
        "urls": urls,
        "prompt": prompt,
        "timestamp": datetime.now().strftime("%H:%M"),
    })


FRANCOIS_PRESET = (
    "A young geeky man with short black hair, brown eyes, 3-day stubble beard, "
    "wearing glasses and a hoodie with the hood down, sitting in front of a PC "
    "with an ultrawide curved monitor displaying VSCode with a dark theme"
)


def _expand_prompt(prompt: str) -> str:
    """Replace 'François' keyword with the creator's visual preset."""
    import re
    return re.sub(
        r'\bFran[cç]ois\b',
        FRANCOIS_PRESET,
        prompt,
        flags=re.IGNORECASE,
    )


async def _generate_one_image(prompt: str, aspect_ratio: str = "1:1", resolution: str = "1k", model_key: str = "standard", xai_client: Client = None):
    c = xai_client or client
    model_name = ALLOWED_MODELS.get(model_key, ALLOWED_MODELS["standard"])
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, lambda: c.image.sample(
        model=model_name,
        prompt=prompt,
        image_format="url",
        aspect_ratio=aspect_ratio,
        resolution=resolution
    ))


# --- Routes principales (protégées par require_auth) ---

def _tpl_ctx(request: Request, **kwargs):
    """Build template context with common fields."""
    ctx = {
        "request": request,
        "image_urls": None,
        "video_url": None,
        "log": "",
        "prompt": "",
        "history": request.session.get("history", []),
        "is_guest": request.session.get("guest", False),
        "test_mode": None,
        "model_config": MODEL_CONFIG,
        "video_config": VIDEO_CONFIG,
    }
    ctx.update(kwargs)
    return ctx


def _tpl(request: Request, template: str, **kwargs):
    """Render a template."""
    return templates.TemplateResponse(template, _tpl_ctx(request, **kwargs))


@app.get("/", response_class=HTMLResponse, dependencies=[Depends(require_auth)])
async def home(request: Request):
    return _tpl(request, "index.html", log="Prêt à générer (images ou vidéos) !")


@app.post("/generate_image", response_class=HTMLResponse, dependencies=[Depends(require_auth)])
async def generate_image(
    request: Request,
    prompt: str = Form(...),
    num_images: str = Form("4"),
    aspect_ratio: str = Form("9:16"),
    resolution: str = Form("1k"),
    model_quality: str = Form("standard"),
    test_mode: Optional[str] = Form(None),
    api_key: Optional[str] = Form(None),
):
    if not prompt.strip():
        return _tpl(request, "index.html", log="Erreur : Prompt vide pour image !")

    xai_client = _get_client(request, api_key)
    # "infinite" mode starts with a batch of 4, then JS handles the rest
    num_images = 4 if num_images == "infinite" else min(max(int(num_images), 1), 10)
    aspect_ratio = aspect_ratio if aspect_ratio in ALLOWED_ASPECT_RATIOS else "9:16"
    resolution = resolution if resolution in ALLOWED_RESOLUTIONS else "1k"
    model_quality = model_quality if model_quality in ALLOWED_MODELS else "standard"
    expanded_prompt = _expand_prompt(prompt)
    model_label = "Pro" if model_quality == "pro" else "Standard"
    log = f"Génération de {num_images} image(s) [{aspect_ratio}, {resolution}, {model_label}] en cours : \"{prompt}\" ...\n"
    if expanded_prompt != prompt:
        log += f"Preset appliqué.\n"
    try:
        results = await asyncio.gather(
            *[_generate_one_image(expanded_prompt, aspect_ratio, resolution, model_key=model_quality, xai_client=xai_client) for _ in range(num_images)],
            return_exceptions=True
        )
        image_urls = []
        for i, response in enumerate(results):
            if isinstance(response, Exception):
                log += f"Erreur pour image {i+1} : {response}\n"
                continue
            image_url = getattr(response, 'url', None) or (response.get('url') if isinstance(response, dict) else None)
            if image_url:
                image_urls.append(image_url)
                log += f"Image {i+1} générée.\n"
            else:
                log += f"Erreur pour image {i+1} : URL manquante.\n"
        if image_urls:
            cost = len(image_urls) * MODEL_CONFIG[model_quality]["price"]
            log += f"Succès : Images générées ! Coût : ~${cost:.2f} ({len(image_urls)} × ${MODEL_CONFIG[model_quality]['price']})\n"
            if not test_mode:
                _add_to_history(request, "image", image_urls, prompt)
        return _tpl(request, "index.html", image_urls=image_urls, log=log, prompt=prompt, test_mode=test_mode)
    except Exception as e:
        log += f"Erreur génération images : {e}\n"
        return _tpl(request, "index.html", log=log)


@app.post("/generate_video", response_class=HTMLResponse, dependencies=[Depends(require_auth)])
async def generate_video(
    request: Request,
    prompt: str = Form(...),
    image_file: UploadFile = File(None),
    video_resolution: str = Form("480p"),
    video_duration: int = Form(5),
    test_mode: Optional[str] = Form(None),
    api_key: Optional[str] = Form(None),
):
    if not prompt.strip() and not image_file:
        return _tpl(request, "index.html", log="Erreur : Prompt vide et aucune image uploadée pour vidéo !")

    video_resolution = video_resolution if video_resolution in ALLOWED_VIDEO_RESOLUTIONS else "480p"
    video_duration = max(VIDEO_CONFIG["min_duration"], min(VIDEO_CONFIG["max_duration"], video_duration))

    xai_client = _get_client(request, api_key)
    expanded_prompt = _expand_prompt(prompt)
    log = f"Génération vidéo en cours : \"{prompt}\""
    if image_file:
        log += " (depuis image uploadée)"
    log += f" [{video_resolution}, {video_duration}s] ...\n"
    if expanded_prompt != prompt:
        log += "Preset appliqué.\n"

    temp_path = None
    try:
        loop = asyncio.get_running_loop()
        if image_file:
            if image_file.content_type not in ALLOWED_MIME_TYPES:
                return _tpl(request, "index.html", log=f"Erreur : Type de fichier non autorisé ({image_file.content_type}). Formats acceptés : PNG, JPEG, WebP.", prompt=prompt)

            content = await image_file.read()
            if len(content) > MAX_UPLOAD_SIZE:
                return _tpl(request, "index.html", log="Erreur : Fichier trop volumineux (max 10 Mo).", prompt=prompt)

            ext = os.path.splitext(image_file.filename or "")[1] or ".png"
            temp_path = os.path.join(SAVE_DIR, f"temp_{uuid4().hex}{ext}")
            with open(temp_path, "wb") as f:
                f.write(content)

            image_url = f"file://{temp_path}"
            response = await loop.run_in_executor(None, lambda: xai_client.video.generate(
                model="grok-imagine-video",
                prompt=expanded_prompt,
                image_url=image_url,
                resolution=video_resolution,
                duration=video_duration,
            ))
        else:
            response = await loop.run_in_executor(None, lambda: xai_client.video.generate(
                model="grok-imagine-video",
                prompt=expanded_prompt,
                resolution=video_resolution,
                duration=video_duration,
            ))

        video_url = getattr(response, 'url', None) or (response.get('url') if isinstance(response, dict) else None)
        if video_url:
            cost = video_duration * VIDEO_CONFIG["price_per_second"]
            log += f"Succès : Vidéo générée ! Coût : ~${cost:.2f} ({video_duration}s × $0.05/s)\n"
            if not test_mode:
                _add_to_history(request, "video", [video_url], prompt)
        else:
            log += "Erreur : URL de vidéo manquante.\n"
        return _tpl(request, "index.html", video_url=video_url, log=log, prompt=prompt)
    except Exception as e:
        log += f"Erreur génération vidéo : {e}\n"
        return _tpl(request, "index.html", log=log)
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass


@app.post("/animate_image", response_class=HTMLResponse, dependencies=[Depends(require_auth)])
async def animate_image(
    request: Request,
    image_url: str = Form(...),
    prompt: Optional[str] = Form(None),
    video_duration: int = Form(5),
    test_mode: Optional[str] = Form(None),
    api_key: Optional[str] = Form(None),
):
    xai_client = _get_client(request, api_key)
    video_duration = max(VIDEO_CONFIG["min_duration"], min(VIDEO_CONFIG["max_duration"], video_duration))
    animate_prompt = prompt.strip() if prompt else "Animer cette image avec mouvement fluide et naturel"
    log = f"Animation image→vidéo en cours : \"{animate_prompt}\" [{video_duration}s] ...\n"
    try:
        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(None, lambda: xai_client.video.generate(
            model="grok-imagine-video",
            prompt=animate_prompt,
            image_url=image_url,
            duration=video_duration,
        ))
        video_url = getattr(response, 'url', None) or (response.get('url') if isinstance(response, dict) else None)
        if video_url:
            cost = video_duration * VIDEO_CONFIG["price_per_second"]
            log += f"Succès : Animation terminée ! Coût : ~${cost:.2f} ({video_duration}s × $0.05/s)\n"
            if not test_mode:
                _add_to_history(request, "video", [video_url], animate_prompt)
        else:
            log += "Erreur : URL de vidéo manquante.\n"
        return _tpl(request, "index.html", image_urls=[image_url], video_url=video_url, log=log, prompt=animate_prompt)
    except Exception as e:
        log += f"Erreur animation : {e}\n"
        return _tpl(request, "index.html", image_urls=[image_url], log=log)


@app.post("/refine_image", response_class=HTMLResponse, dependencies=[Depends(require_auth)])
async def refine_image(request: Request, image_url: str = Form(...), refine_prompt: str = Form(...), test_mode: Optional[str] = Form(None), api_key: Optional[str] = Form(None)):
    if not refine_prompt.strip():
        return _tpl(request, "index.html", image_urls=[image_url], log="Erreur : Prompt de refinement vide !")

    xai_client = _get_client(request, api_key)
    log = f"Refinement image en cours : \"{refine_prompt}\" ...\n"
    try:
        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(None, lambda: xai_client.image.sample(
            model="grok-imagine-image",
            prompt=refine_prompt,
            image_url=image_url,
            image_format="url"
        ))
        refined_image_url = getattr(response, 'url', None) or (response.get('url') if isinstance(response, dict) else None)
        if refined_image_url:
            log += "Succès : Image raffinée !\n"
            if not test_mode:
                _add_to_history(request, "image", [refined_image_url], refine_prompt)
            return _tpl(request, "index.html", image_urls=[refined_image_url], log=log, prompt=refine_prompt)
        else:
            log += "Erreur : URL de l'image raffinée manquante.\n"
    except Exception as e:
        log += f"Erreur refinement : {e}\n"
    return _tpl(request, "index.html", image_urls=[image_url], log=log)


@app.post("/clear_history", dependencies=[Depends(require_auth)])
async def clear_history(request: Request):
    request.session.pop("history", None)
    return RedirectResponse("/", status_code=303)


from fastapi.responses import JSONResponse

@app.post("/api/generate_images", dependencies=[Depends(require_auth)])
async def api_generate_images(request: Request):
    """JSON endpoint for AJAX infinite scroll generation."""
    body = await request.json()
    prompt = body.get("prompt", "").strip()
    if not prompt:
        return JSONResponse({"error": "Prompt vide"}, status_code=400)

    num_images = min(max(body.get("num_images", 4), 1), 10)
    aspect_ratio = body.get("aspect_ratio", "9:16")
    resolution = body.get("resolution", "1k")
    model_quality = body.get("model_quality", "standard")
    api_key = body.get("api_key")

    aspect_ratio = aspect_ratio if aspect_ratio in ALLOWED_ASPECT_RATIOS else "9:16"
    resolution = resolution if resolution in ALLOWED_RESOLUTIONS else "1k"
    model_quality = model_quality if model_quality in ALLOWED_MODELS else "standard"

    xai_client = _get_client(request, api_key)
    expanded_prompt = _expand_prompt(prompt)

    results = await asyncio.gather(
        *[_generate_one_image(expanded_prompt, aspect_ratio, resolution, model_key=model_quality, xai_client=xai_client) for _ in range(num_images)],
        return_exceptions=True
    )

    image_urls = []
    errors = []
    for i, response in enumerate(results):
        if isinstance(response, Exception):
            errors.append(f"Image {i+1}: {response}")
            continue
        url = getattr(response, 'url', None) or (response.get('url') if isinstance(response, dict) else None)
        if url:
            image_urls.append(url)
        else:
            errors.append(f"Image {i+1}: URL manquante")

    if image_urls and not body.get("test_mode"):
        _add_to_history(request, "image", image_urls, prompt)

    return JSONResponse({"urls": image_urls, "errors": errors})


@app.get("/download", dependencies=[Depends(require_auth)])
async def download_media(url: str = Query(...)):
    """Proxy de téléchargement pour contourner les CORS"""
    try:
        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(None, lambda: requests.get(url, stream=True, timeout=30))
        response.raise_for_status()

        # Déterminer le type de contenu et l'extension
        content_type = response.headers.get('content-type', 'application/octet-stream')
        extension = '.png'
        if 'video' in content_type or url.endswith('.mp4'):
            extension = '.mp4'
        elif 'jpeg' in content_type or url.endswith('.jpg'):
            extension = '.jpg'
        elif 'webp' in content_type or url.endswith('.webp'):
            extension = '.webp'

        # Nom de fichier
        filename = f"menguygen_{uuid4().hex[:8]}{extension}"

        # Retourner le stream avec headers de téléchargement
        return StreamingResponse(
            response.iter_content(chunk_size=8192),
            media_type=content_type,
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
    except Exception as e:
        return RedirectResponse(url=url)  # Fallback : redirection directe
