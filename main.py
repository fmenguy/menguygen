import os
import asyncio
import requests
from datetime import datetime
from fastapi import FastAPI, Form, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from xai_sdk import Client
from typing import Optional

app = FastAPI(title="Grok Image & Video Generator Local")

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

api_key = os.getenv("XAI_API_KEY")
if not api_key:
    raise ValueError("XAI_API_KEY non trouvée dans les variables d'environnement !")

client = Client(api_key=api_key)

SAVE_DIR = r"C:\Users\François\Desktop\SeaArt tests" if os.path.exists(r"C:\Users\François\Desktop\SeaArt tests") else os.path.join(os.getcwd(), "downloads")
os.makedirs(SAVE_DIR, exist_ok=True)

def _download_media(url: str, filepath: str):
    response = requests.get(url)
    response.raise_for_status()
    with open(filepath, 'wb') as f:
        f.write(response.content)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "image_urls": None, "video_url": None, "log": "Prêt à générer (images ou vidéos) !", "prompt": ""}
    )

@app.post("/generate_image", response_class=HTMLResponse)
async def generate_image(request: Request, prompt: str = Form(...), num_images: int = Form(1)):
    if not prompt.strip():
        return templates.TemplateResponse("index.html", {"request": request, "image_urls": None, "video_url": None, "log": "Erreur : Prompt vide pour image !", "prompt": ""})
    
    num_images = min(max(num_images, 1), 4)
    log = f"Génération de {num_images} image(s) en cours : \"{prompt}\" ...\n"
    image_urls = []
    try:
        for i in range(num_images):
            response = client.image.sample(
                model="grok-imagine-image",
                prompt=prompt,
                image_format="url"
            )
            image_url = getattr(response, 'url', None) or (response.get('url') if isinstance(response, dict) else None)
            if image_url:
                image_urls.append(image_url)
                log += f"Image {i+1} générée.\n"
            else:
                log += f"Erreur pour image {i+1} : URL manquante.\n"
        if image_urls:
            log += "Succès : Images générées !\n"
        return templates.TemplateResponse("index.html", {"request": request, "image_urls": image_urls, "video_url": None, "log": log, "prompt": prompt})
    except Exception as e:
        log += f"Erreur génération images : {str(e)}\nVérifie clé API, modèle, quota, ou structure de réponse.\n"
        return templates.TemplateResponse("index.html", {"request": request, "image_urls": None, "video_url": None, "log": log, "prompt": ""})

@app.post("/generate_video", response_class=HTMLResponse)
async def generate_video(request: Request, prompt: str = Form(...), image_file: UploadFile = File(None)):
    if not prompt.strip() and not image_file:
        return templates.TemplateResponse("index.html", {"request": request, "image_urls": None, "video_url": None, "log": "Erreur : Prompt vide et aucune image uploadée pour vidéo !", "prompt": ""})
    
    log = f"Génération vidéo en cours : \"{prompt}\""
    if image_file:
        log += f" (depuis image uploadée : {image_file.filename})"
    log += " ...\n"
    try:
        if image_file:
            temp_path = os.path.join(SAVE_DIR, f"temp_{image_file.filename}")
            with open(temp_path, "wb") as f:
                f.write(await image_file.read())
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
        return templates.TemplateResponse("index.html", {"request": request, "image_urls": None, "video_url": video_url, "log": log, "prompt": prompt})
    except Exception as e:
        log += f"Erreur génération vidéo : {str(e)}\nVérifie SDK xAI, modèle, ou si image-to-video est disponible.\n"
        return templates.TemplateResponse("index.html", {"request": request, "image_urls": None, "video_url": None, "log": log, "prompt": ""})

@app.post("/animate_image", response_class=HTMLResponse)
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
        return templates.TemplateResponse("index.html", {"request": request, "image_urls": [image_url], "video_url": video_url, "log": log, "prompt": animate_prompt})
    except Exception as e:
        log += f"Erreur animation : {str(e)}\nAssure-toi que l'image est valide.\n"
        return templates.TemplateResponse("index.html", {"request": request, "image_urls": [image_url], "video_url": None, "log": log, "prompt": ""})

@app.post("/download", response_class=HTMLResponse)
async def download(request: Request, media_url: str = Form(...), prompt: str = Form(...), media_type: str = Form("image")):
    try:
        os.makedirs(SAVE_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ext = ".mp4" if media_type == "video" else ".png"
        filename = f"grok_{media_type}_{timestamp}{ext}"
        filepath = os.path.join(SAVE_DIR, filename)
        
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, lambda: _download_media(media_url, filepath))
        
        log = f"Téléchargement réussi : {filepath}"
    except Exception as e:
        log = f"Erreur téléchargement : {str(e)}"
    
    img_urls = [media_url] if media_type == "image" else None
    vid_url = media_url if media_type == "video" else None
    return templates.TemplateResponse("index.html", {"request": request, "image_urls": img_urls, "video_url": vid_url, "log": log, "prompt": prompt})