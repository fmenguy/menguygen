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
from translatepy import Translator

app = FastAPI(title="Grok Image & Video Generator Local")

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

api_key = os.getenv("XAI_API_KEY")
if not api_key:
    raise ValueError("XAI_API_KEY non trouvée dans les variables d'environnement !")

client = Client(api_key=api_key)
translator = Translator()  # Instance pour traduction

SAVE_DIR = r"C:\Users\François\Desktop\SeaArt tests" if os.path.exists(r"C:\Users\François\Desktop\SeaArt tests") else os.path.join(os.getcwd(), "downloads")
os.makedirs(SAVE_DIR, exist_ok=True)

def _download_media(url: str, filepath: str):
    response = requests.get(url)
    response.raise_for_status()
    with open(filepath, 'wb') as f:
        f.write(response.content)

def translate_to_english(text: str) -> str:
    """Traduit le texte en anglais si nécessaire."""
    try:
        if text.strip():
            translated = translator.translate(text, src='auto', dest='en')
            return translated.text
    except:
        pass  # En cas d'erreur, retourne le texte original
    return text

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "image_urls": None, "video_url": None, "log": "Ready to generate images or videos!", "prompt": ""}
    )

@app.post("/generate_image", response_class=HTMLResponse)
async def generate_image(request: Request, prompt: str = Form(...), num_images: int = Form(1)):
    if not prompt.strip():
        return templates.TemplateResponse("index.html", {"request": request, "image_urls": None, "video_url": None, "log": "Error: Empty prompt for image!", "prompt": ""})
    
    num_images = min(max(num_images, 1), 4)
    english_prompt = translate_to_english(prompt)
    log = f"Generating {num_images} image(s): \"{english_prompt}\" (translated from: \"{prompt}\") ...\n"
    image_urls = []
    try:
        for i in range(num_images):
            response = client.image.sample(
                model="grok-imagine-image",
                prompt=english_prompt,
                image_format="url"
            )
            image_url = getattr(response, 'url', None) or (response.get('url') if isinstance(response, dict) else None)
            if image_url:
                image_urls.append(image_url)
                log += f"Image {i+1} generated.\n"
            else:
                log += f"Error for image {i+1}: URL missing.\n"
        if image_urls:
            log += "Success: Images generated!\n"
        return templates.TemplateResponse("index.html", {"request": request, "image_urls": image_urls, "video_url": None, "log": log, "prompt": prompt})
    except Exception as e:
        log += f"Error generating images: {str(e)}\nCheck API key, model, quota, or response structure.\nIf NSFW, try a less sensitive prompt.\n"
        return templates.TemplateResponse("index.html", {"request": request, "image_urls": None, "video_url": None, "log": log, "prompt": ""})

@app.post("/generate_video", response_class=HTMLResponse)
async def generate_video(request: Request, prompt: str = Form(...), image_file: UploadFile = File(None)):
    if not prompt.strip() and not image_file:
        return templates.TemplateResponse("index.html", {"request": request, "image_urls": None, "video_url": None, "log": "Error: Empty prompt and no image uploaded for video!", "prompt": ""})
    
    english_prompt = translate_to_english(prompt)
    log = f"Generating video: \"{english_prompt}\""
    if image_file:
        log += f" (from uploaded image: {image_file.filename})"
    log += " ...\n"
    try:
        if image_file:
            temp_path = os.path.join(SAVE_DIR, f"temp_{image_file.filename}")
            with open(temp_path, "wb") as f:
                f.write(await image_file.read())
            image_url = f"file://{temp_path}"
            response = client.video.generate(
                model="grok-imagine-video",
                prompt=english_prompt,
                image_url=image_url
            )
        else:
            response = client.video.generate(
                model="grok-imagine-video",
                prompt=english_prompt
            )
        video_url = getattr(response, 'url', None) or (response.get('url') if isinstance(response, dict) else None)
        if video_url:
            log += "Success: Video generated!\n"
        else:
            log += "Error: Video URL missing.\n"
        return templates.TemplateResponse("index.html", {"request": request, "image_urls": None, "video_url": video_url, "log": log, "prompt": prompt})
    except Exception as e:
        log += f"Error generating video: {str(e)}\nCheck xAI SDK, model, or if image-to-video is supported.\nIf NSFW, moderation may block it – try a different prompt.\n"
        return templates.TemplateResponse("index.html", {"request": request, "image_urls": None, "video_url": None, "log": log, "prompt": ""})

@app.post("/animate_image", response_class=HTMLResponse)
async def animate_image(request: Request, image_url: str = Form(...), prompt: Optional[str] = Form(None), allow_nsfw: bool = Form(False)):
    animate_prompt = prompt.strip() if prompt else "Animate this image with smooth and natural movement"
    english_prompt = translate_to_english(animate_prompt)
    log = f"Animating image to video: \"{english_prompt}\" ...\n"
    if allow_nsfw:
        log += "NSFW allowed: Proceeding, but moderation may still block.\n"
    try:
        response = client.video.generate(
            model="grok-imagine-video",
            prompt=english_prompt,
            image_url=image_url
        )
        video_url = getattr(response, 'url', None) or (response.get('url') if isinstance(response, dict) else None)
        if video_url:
            log += "Success: Animation completed!\n"
        else:
            log += "Error: Video URL missing.\n"
        return templates.TemplateResponse("index.html", {"request": request, "image_urls": [image_url], "video_url": video_url, "log": log, "prompt": animate_prompt})
    except Exception as e:
        log += f"Error animating: {str(e)}\nEnsure the image is valid and image-to-video is supported.\nIf NSFW, try enabling 'Allow NSFW' or use a less sensitive prompt.\n"
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
        
        log = f"Download successful: {filepath}"
    except Exception as e:
        log = f"Download error: {str(e)}"
    
    img_urls = [media_url] if media_type == "image" else None
    vid_url = media_url if media_type == "video" else None
    return templates.TemplateResponse("index.html", {"request": request, "image_urls": img_urls, "video_url": vid_url, "log": log, "prompt": prompt})