import os
import io
import re
import base64

from PIL import Image
from flask import Flask, request, render_template, flash, redirect
from werkzeug.utils import secure_filename

from tf_model_helper import TFModel

app = Flask(__name__, template_folder='templates')

print("Test")
# Path to signature.json and model file
ASSETS_PATH = os.path.join(".", "./model")
TF_MODEL = TFModel(ASSETS_PATH)

# Define the upload folder
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Define allowed extensions for uploaded files
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Function to check if a file has an allowed extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    # Check if the post request has the file part
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)

    file = request.files['file']

    # If the user does not select a file, browser also
    # submit an empty part without filename
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Process the uploaded image and get predictions
        image = Image.open(file_path)
        predictions = TF_MODEL.predict(image)

        # Remove the uploaded file after processing (optional)
        os.remove(file_path)

        return render_template('result.html', predictions=predictions)

    return render_template('index.html', error="Invalid file format. Please upload a valid image.")

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8000, debug=True)
