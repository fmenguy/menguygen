import os
from pathlib import Path as _Path
from dotenv import load_dotenv
load_dotenv(_Path(__file__).resolve().parent / ".env")

import asyncio
import requests
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

app = FastAPI(title="Image Studio")
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
    if not request.session.get("authenticated"):
        raise RedirectException()

class RedirectException(Exception):
    pass

@app.exception_handler(RedirectException)
async def redirect_to_login(request: Request, exc: RedirectException):
    return RedirectResponse("/auth/login")


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


# --- Helpers ---

def _download_media(url: str, filepath: str):
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    with open(filepath, 'wb') as f:
        f.write(response.content)


async def _generate_one_image(prompt: str):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, lambda: client.image.sample(
        model="grok-imagine-image",
        prompt=prompt,
        image_format="url"
    ))


# --- Routes principales (protégées par require_auth) ---

@app.get("/", response_class=HTMLResponse, dependencies=[Depends(require_auth)])
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "image_urls": None, "video_url": None,
         "log": "Prêt à générer (images ou vidéos) !", "prompt": ""}
    )


@app.post("/generate_image", response_class=HTMLResponse, dependencies=[Depends(require_auth)])
async def generate_image(request: Request, prompt: str = Form(...), num_images: int = Form(1)):
    if not prompt.strip():
        return templates.TemplateResponse("index.html", {
            "request": request, "image_urls": None, "video_url": None,
            "log": "Erreur : Prompt vide pour image !", "prompt": ""
        })

    num_images = min(max(num_images, 1), 4)
    log = f"Génération de {num_images} image(s) en cours : \"{prompt}\" ...\n"
    try:
        results = await asyncio.gather(
            *[_generate_one_image(prompt) for _ in range(num_images)],
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
            log += "Succès : Images générées !\n"
        return templates.TemplateResponse("index.html", {
            "request": request, "image_urls": image_urls, "video_url": None,
            "log": log, "prompt": prompt
        })
    except Exception as e:
        log += f"Erreur génération images : {e}\n"
        return templates.TemplateResponse("index.html", {
            "request": request, "image_urls": None, "video_url": None,
            "log": log, "prompt": ""
        })


@app.post("/generate_video", response_class=HTMLResponse, dependencies=[Depends(require_auth)])
async def generate_video(request: Request, prompt: str = Form(...), image_file: UploadFile = File(None)):
    if not prompt.strip() and not image_file:
        return templates.TemplateResponse("index.html", {
            "request": request, "image_urls": None, "video_url": None,
            "log": "Erreur : Prompt vide et aucune image uploadée pour vidéo !", "prompt": ""
        })

    log = f"Génération vidéo en cours : \"{prompt}\""
    if image_file:
        log += " (depuis image uploadée)"
    log += " ...\n"

    temp_path = None
    try:
        if image_file:
            if image_file.content_type not in ALLOWED_MIME_TYPES:
                return templates.TemplateResponse("index.html", {
                    "request": request, "image_urls": None, "video_url": None,
                    "log": f"Erreur : Type de fichier non autorisé ({image_file.content_type}). Formats acceptés : PNG, JPEG, WebP.", "prompt": prompt
                })

            content = await image_file.read()
            if len(content) > MAX_UPLOAD_SIZE:
                return templates.TemplateResponse("index.html", {
                    "request": request, "image_urls": None, "video_url": None,
                    "log": "Erreur : Fichier trop volumineux (max 10 Mo).", "prompt": prompt
                })

            ext = os.path.splitext(image_file.filename or "")[1] or ".png"
            temp_path = os.path.join(SAVE_DIR, f"temp_{uuid4().hex}{ext}")
            with open(temp_path, "wb") as f:
                f.write(content)

            image_url = f"file://{temp_path}"
            response = client.video.generate(
                model="grok-imagine-video",
                prompt=prompt,
                image_url=image_url
            )
        else:
            response = client.video.generate(
                model="grok-imagine-video",
                prompt=prompt
            )

        video_url = getattr(response, 'url', None) or (response.get('url') if isinstance(response, dict) else None)
        if video_url:
            log += "Succès : Vidéo générée !\n"
        else:
            log += "Erreur : URL de vidéo manquante.\n"
        return templates.TemplateResponse("index.html", {
            "request": request, "image_urls": None, "video_url": video_url,
            "log": log, "prompt": prompt
        })
    except Exception as e:
        log += f"Erreur génération vidéo : {e}\n"
        return templates.TemplateResponse("index.html", {
            "request": request, "image_urls": None, "video_url": None,
            "log": log, "prompt": ""
        })
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass


@app.post("/animate_image", response_class=HTMLResponse, dependencies=[Depends(require_auth)])
async def animate_image(request: Request, image_url: str = Form(...), prompt: Optional[str] = Form(None)):
    animate_prompt = prompt.strip() if prompt else "Animer cette image avec mouvement fluide et naturel"
    log = f"Animation image→vidéo en cours : \"{animate_prompt}\" ...\n"
    try:
        response = client.video.generate(
            model="grok-imagine-video",
            prompt=animate_prompt,
            image_url=image_url
        )
        video_url = getattr(response, 'url', None) or (response.get('url') if isinstance(response, dict) else None)
        if video_url:
            log += "Succès : Animation terminée !\n"
        else:
            log += "Erreur : URL de vidéo manquante.\n"
        return templates.TemplateResponse("index.html", {
            "request": request, "image_urls": [image_url], "video_url": video_url,
            "log": log, "prompt": animate_prompt
        })
    except Exception as e:
        log += f"Erreur animation : {e}\n"
        return templates.TemplateResponse("index.html", {
            "request": request, "image_urls": [image_url], "video_url": None,
            "log": log, "prompt": ""
        })


@app.post("/refine_image", response_class=HTMLResponse, dependencies=[Depends(require_auth)])
async def refine_image(request: Request, image_url: str = Form(...), refine_prompt: str = Form(...)):
    if not refine_prompt.strip():
        return templates.TemplateResponse("index.html", {
            "request": request, "image_urls": [image_url], "video_url": None,
            "log": "Erreur : Prompt de refinement vide !", "prompt": ""
        })

    log = f"Refinement image en cours : \"{refine_prompt}\" ...\n"
    try:
        response = client.image.sample(
            model="grok-imagine-image",
            prompt=refine_prompt,
            image_url=image_url,
            image_format="url"
        )
        refined_image_url = getattr(response, 'url', None) or (response.get('url') if isinstance(response, dict) else None)
        if refined_image_url:
            log += "Succès : Image raffinée !\n"
            return templates.TemplateResponse("index.html", {
                "request": request, "image_urls": [refined_image_url], "video_url": None,
                "log": log, "prompt": refine_prompt
            })
        else:
            log += "Erreur : URL de l'image raffinée manquante.\n"
    except Exception as e:
        log += f"Erreur refinement : {e}\n"
    return templates.TemplateResponse("index.html", {
        "request": request, "image_urls": [image_url], "video_url": None,
        "log": log, "prompt": ""
    })


@app.get("/download", dependencies=[Depends(require_auth)])
async def download_media(url: str = Query(...)):
    """Proxy de téléchargement pour contourner les CORS"""
    try:
        response = requests.get(url, stream=True, timeout=30)
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
        filename = f"image_studio_{uuid4().hex[:8]}{extension}"

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
