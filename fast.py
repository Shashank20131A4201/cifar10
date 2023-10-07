import uvicorn
from fastapi import FastAPI, UploadFile, File, Request,Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import io
from PIL import Image
import os
import cv2
import shutil
from main import process_and_return


app = FastAPI()
app.mount("/static", StaticFiles(directory = "static"), name = "static")

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

templates = Jinja2Templates(directory="templates")

@app.get("/")
def read_root():
    with open("templates/index.html", 'r') as file:
        content = file.read()
    return HTMLResponse(content=content)

@app.post("/upload")
async def upload_image(image: UploadFile):
    if image.filename != '':
        # Save the uploaded image to the specified directory
        image_path = os.path.join(UPLOAD_FOLDER, image.filename)
        with open(image_path, "wb") as f:
            shutil.copyfileobj(image.file, f)

        # Process the uploaded image using Pillow (PIL)
        img = Image.open(image_path)
        predictions = process_and_return(image_path)

        return {"message": "Image uploaded and processed successfully.","Pred":predictions}
    return {"error": "No image selected."}

if __name__ == '__main__':
   uvicorn.run(app, host='0.0.0.0', port=8000)