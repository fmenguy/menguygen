# main.py
import os
import asyncio
import requests
from datetime import datetime
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from xai_sdk import Client


app = FastAPI(title="Grok Image Generator Local")

# Templates
templates = Jinja2Templates(directory="templates")

# Client xAI
api_key = os.getenv("XAI_API_KEY")
if not api_key:
    raise ValueError("XAI_API_KEY non trouvée dans les variables d'environnement !")

client = Client(api_key=api_key)

# Save directory for downloads (your specified path)
SAVE_DIR = r"C:\Users\François\Desktop\SeaArt tests"

# Helper function to download and save image
def _download_image(url: str, filepath: str):
    response = requests.get(url)
    response.raise_for_status()  # Raise error if download fails
    with open(filepath, 'wb') as f:
        f.write(response.content)



@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "image_url": None, "log": "Prêt à générer une image !", "prompt": ""}
    )

@app.post("/generate", response_class=HTMLResponse)
async def generate(request: Request, prompt: str = Form(...)):
    if not prompt.strip():
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "image_url": None, "log": "Erreur : prompt vide !", "prompt": ""}
        )

    log = f"Génération en cours pour : \"{prompt}\" ...\n"

    try:
        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(
            None,
            lambda: client.image.sample(
                model="grok-imagine-image",  # Change si besoin (ex. grok-2-image-1212)
                prompt=prompt,
                image_format="url"
            )
        )
        image_url = response.url  # ou response.image_url si différent
        log += "Succès ! Image générée.\n"
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "image_url": image_url, "log": log, "prompt": prompt}
        )
    except Exception as e:
        log += f"Erreur : {str(e)}\nVérifie ta clé API, le modèle ou les quotas.\n"
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "image_url": None, "log": log, "prompt": ""}
        )



@app.post("/download", response_class=HTMLResponse)
async def download(request: Request, image_url: str = Form(...), prompt: str = Form(...)):
    try:
        # Ensure save directory exists
        os.makedirs(SAVE_DIR, exist_ok=True)
        
        # Generate a timestamped filename (e.g., image_20231001_123456.png)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"image_{timestamp}.png"  # Assumes PNG; adjust if needed based on API
        filepath = os.path.join(SAVE_DIR, filename)
        
        # Download and save the image in a thread
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, lambda: _download_image(image_url, filepath))
        
        log = f"Image téléchargée avec succès dans : {filepath}"
    except Exception as e:
        log = f"Erreur lors du téléchargement : {str(e)}"
    
    # Return to the page with the image still displayed and updated log
    return templates.TemplateResponse(
        "index.html",
                    {"request": request, "image_url": image_url, "log": log, "prompt": prompt}
    )