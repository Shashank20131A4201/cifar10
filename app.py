import tensorflow as tf
from keras import datasets, layers, models
import numpy as np
from flask import Flask, redirect, url_for, request, render_template
from werkzeug.utils import secure_filename
from gevent.pywsgi import WSGIServer
from main import load_model


# Define a flask app
app = Flask(__name__)

# Model saved with Keras model.save()
MODEL_PATH = '/workspace/cifar10/model.pkl'

# Load your trained model
model = load_model()
model._make_predict_function()          

@app.route('/', methods=['GET'])
def index():
    # Main page
    return render_template('index.html')


# @app.route('/predict', methods=['GET', 'POST'])
# def upload():
#     if request.method == 'POST':
#         # Get the file from post request
#         f = request.files['file']

#         # Save the file to ./uploads
#         basepath = os.path.dirname(__file__)
#         file_path = os.path.join(
#             basepath, 'uploads', secure_filename(f.filename))
#         f.save(file_path)

#         # Make prediction
#         preds = model_predict(file_path, model)

#         # Process your result for human
#         # pred_class = preds.argmax(axis=-1)            # Simple argmax
#         pred_class = decode_predictions(preds, top=1)   # ImageNet Decode
#         result = str(pred_class[0][0][1])               # Convert to string
#         return result
#     return None


if __name__ == '__main__':
    app.run(debug=True)