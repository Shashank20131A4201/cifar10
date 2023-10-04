import uvicorn
from fastapi import FastAPI, UploadFile, File
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import io
from PIL import Image
import os


app = FastAPI()
app.mount("/static", StaticFiles(directory = "static"), name = "static")

templates = Jinja2Templates(directory="templates")

@app.get("/")
async def dynamic_file(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})


def process_image(image: UploadFile, patient_details: dict, probabilities: dict):
    # Upload image to Cloud Storage
    folder_name = 'Lung_Images'
    bucket_name = 'lung_abn'
    bucket = storage_client.bucket(bucket_name)

    # Upload the image to the specified folder within the bucket
    blob = bucket.blob(f'{folder_name}/{image.filename}')
    blob.upload_from_file(image.file)

    # Get the image path in Cloud Storage
    image_path = f'gs://{bucket_name}/{blob.name}'

    # Create an instance of the ImageData model with the collected data
    image_data = ImageData(
        img_file=image_path,
        patient_id=patient_details['patient_id'],
        patient_name=patient_details['patient_name'],
        patient_dob=patient_details['patient_dob'],
        patient_gender=patient_details['patient_gender'],
        patient_email=patient_details['patient_email'],
        pneumonia_prob=probabilities['pneumonia_prob'],
        tuberculosis_prob=probabilities['tuberculosis_prob'],
        cancer_prob=probabilities['cancer_prob'],
        covid19_prob=probabilities['covid19_prob']
    )

    # Insert the image data into BigQuery
    table_id = 'cloudkarya-internship.ImageData.ImageDataTable'
    rows_to_insert = [image_data.dict()]
    errors = bigquery_client.insert_rows_json(table_id, rows_to_insert)

    if errors:
        raise Exception(f'Error inserting rows into BigQuery: {errors}')


@app.post("/upload")
async def upload_image(image: UploadFile = Form(...)):
    # Predict probabilities using your model
    contents = await image.read()
    img = Image.open(io.BytesIO(contents))
    img = img.resize((32, 32))
    img = np.array(img) / 255.0
    img = np.expand_dims(img, axis=0)
        
    # Retrieve the blob
    pred=[]
    model_file = "modell.h5"
    model = tf.keras.models.load_model(model_file)
    predictions = model.predict(img)
    os.remove(model_file)
    pred.append(predictions)

    pred1 = pred[0]*100
    pred2 = pred[1]*100
    pred3 = pred[2]*100
    pred4=pred[3]*100
   
    pred1 = pred1[0][0]
    pred2 = pred2[0][0]
    pred3 = pred3[0][0]
    pred4=pred4[0][0]

    probabilities = {
        'pneumonia_prob': pred1,
        'tuberculosis_prob': pred2,
        'covid19_prob': 0.60,
        'cancer_prob':pred4,
    }

    process_image(image, patient_details, probabilities)

    return {"message": "Image uploaded and processed successfully."}