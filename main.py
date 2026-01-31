# main.py
import os
import asyncio
import requests
from datetime import datetime
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles  # Ajout pour servir les fichiers statiques
from xai_sdk import Client
from typing import Optional

app = FastAPI(title="Grok Image & Video Generator Local")

# Monter le dossier static pour servir CSS/JS
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

api_key = os.getenv("XAI_API_KEY")
if not api_key:
    raise ValueError("XAI_API_KEY non trouvée dans les variables d'environnement !")

client = Client(api_key=api_key)

# Amélioration : Utiliser un dossier temporaire si le chemin Windows n'existe pas (pour compatibilité multi-OS)
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
        {"request": request, "image_url": None, "video_url": None, "log": "Prêt à générer (images ou vidéos) !", "prompt": ""}
    )

@app.post("/generate_image", response_class=HTMLResponse)
async def generate_image(request: Request, prompt: str = Form(...)):
    if not prompt.strip():
        return templates.TemplateResponse("index.html", {"request": request, "image_url": None, "video_url": None, "log": "Erreur : Prompt vide pour image !", "prompt": ""})
    
    log = f"Génération image en cours : \"{prompt}\" ...\n"
    try:
        # Appel synchrone direct (pas d'await, car le SDK retourne un objet immédiat)
        response = client.image.sample(
            model="grok-imagine-image",  # Vérifiez la doc xAI pour le bon modèle (e.g., 'grok-2-image')
            prompt=prompt,
            image_format="url"
        )
        # Debug : Imprimer la réponse brute pour vérifier
        log += f"Réponse brute : {response} (type: {type(response)})\n"
        image_url = getattr(response, 'url', None) or (response.get('url') if isinstance(response, dict) else 'Erreur: URL manquante')
        if image_url == 'Erreur: URL manquante':
            raise ValueError("URL non trouvée dans la réponse")
        log += "Succès : Image générée !\n"
        return templates.TemplateResponse("index.html", {"request": request, "image_url": image_url, "video_url": None, "log": log, "prompt": prompt})
    except Exception as e:
        log += f"Erreur génération image : {str(e)}\nVérifie clé API, modèle, quota, ou structure de réponse.\n"
        return templates.TemplateResponse("index.html", {"request": request, "image_url": None, "video_url": None, "log": log, "prompt": ""})

@app.post("/generate_video", response_class=HTMLResponse)
async def generate_video(request: Request, prompt: str = Form(...)):
    if not prompt.strip():
        return templates.TemplateResponse("index.html", {"request": request, "image_url": None, "video_url": None, "log": "Erreur : Prompt vide pour vidéo !", "prompt": ""})
    
    log = f"Génération vidéo (texte→vidéo) en cours : \"{prompt}\" ...\n"
    try:
        # Appel synchrone direct, sans video_format (paramètre invalide)
        response = client.video.generate(
            model="grok-imagine-video",  # Vérifiez la doc xAI pour le bon modèle
            prompt=prompt
            # Retiré : video_format="url" (cause l'erreur)
        )
        log += f"Réponse brute : {response} (type: {type(response)})\n"
        video_url = getattr(response, 'url', None) or (response.get('url') if isinstance(response, dict) else 'Erreur: URL manquante')
        if video_url == 'Erreur: URL manquante':
            raise ValueError("URL non trouvée dans la réponse")
        log += "Succès : Vidéo générée (8-15s avec audio) !\n"
        return templates.TemplateResponse("index.html", {"request": request, "image_url": None, "video_url": video_url, "log": log, "prompt": prompt})
    except Exception as e:
        log += f"Erreur génération vidéo : {str(e)}\nVérifie SDK xAI, modèle, ou si text-to-video est disponible.\n"
        return templates.TemplateResponse("index.html", {"request": request, "image_url": None, "video_url": None, "log": log, "prompt": ""})

@app.post("/animate_image", response_class=HTMLResponse)
async def animate_image(request: Request, image_url: str = Form(...), prompt: Optional[str] = Form(None)):
    animate_prompt = prompt.strip() if prompt else "Animer cette image avec mouvement fluide et naturel"
    log = f"Animation image→vidéo en cours : \"{animate_prompt}\" ...\n"
    try:
        # Appel synchrone direct, sans video_format
        # Note : Si image_url n'est pas supporté, essayez une méthode séparée comme client.video.generate_from_image si disponible
        response = client.video.generate(
            model="grok-imagine-video",  # Vérifiez la doc xAI
            prompt=animate_prompt,
            image_url=image_url  # Si ça échoue, supprimez et utilisez text-to-video à la place
        )
        log += f"Réponse brute : {response} (type: {type(response)})\n"
        video_url = getattr(response, 'url', None) or (response.get('url') if isinstance(response, dict) else 'Erreur: URL manquante')
        if video_url == 'Erreur: URL manquante':
            raise ValueError("URL non trouvée dans la réponse")
        log += "Succès : Animation terminée !\n"
        return templates.TemplateResponse("index.html", {"request": request, "image_url": image_url, "video_url": video_url, "log": log, "prompt": animate_prompt})
    except Exception as e:
        log += f"Erreur animation : {str(e)}\nSi 'image_url' n'est pas supporté, xAI pourrait nécessiter une méthode différente (e.g., generate_from_image).\n"
        return templates.TemplateResponse("index.html", {"request": request, "image_url": image_url, "video_url": None, "log": log, "prompt": ""})

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
    
    img_url = media_url if media_type == "image" else None
    vid_url = media_url if media_type == "video" else None
    return templates.TemplateResponse("index.html", {"request": request, "image_url": img_url, "video_url": vid_url, "log": log, "prompt": prompt})