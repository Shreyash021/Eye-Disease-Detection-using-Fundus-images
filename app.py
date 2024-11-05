from flask import Flask, render_template, request, redirect, url_for
from keras.models import load_model
import numpy as np
import cv2
import os
import requests   

app = Flask(__name__)

# Load the trained model
model = load_model('final_model.keras')

# Define the disease labels and their full names
disease_labels = {
    'N': 'Normal',
    'D': 'Diabetes',
    'G': 'Glaucoma',
    'C': 'Cataract',
    'A': 'Age-related Macular Degeneration',
    'H': 'Hypertension',
    'M': 'Pathological Myopia',
    'O': 'Other diseases/abnormalities'
}

# Load the second trained model
model2 = load_model('Model.h5')

# Define class names for the second model
class_names = ["Normal", "Mild", "Moderate", "Severe", "Proliferative"]

# Function to preprocess the image
def preprocess_image(image):
    image = cv2.resize(image, (50, 50))
    image = image / 255.0
    return np.expand_dims(image, axis=0)

# Path where uploaded images are stored
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/input')
def input_form():
    return render_template('input.html')

@app.route('/predict', methods=['POST'])
def predict():
    if 'left_image' not in request.files or 'right_image' not in request.files:
        return redirect(request.url)

    left_image = request.files['left_image']
    right_image = request.files['right_image']

    if left_image.filename == '' or right_image.filename == '':
        return redirect(request.url)

    # Save uploaded images
    left_image_path = os.path.join(app.config['UPLOAD_FOLDER'], left_image.filename)
    right_image_path = os.path.join(app.config['UPLOAD_FOLDER'], right_image.filename)
    left_image.save(left_image_path)
    right_image.save(right_image_path)

    # Preprocess left image for model2
    left_img = cv2.imread(left_image_path)
    if left_img is None:
        return "Error loading left image", 400  # Return an error if the image is not loaded
    processed_left_image = preprocess_image(left_img)

    # Make predictions with model2
    predictions = model2.predict(processed_left_image)
    predicted_class_index = np.argmax(predictions)
    predicted_class_name = class_names[predicted_class_index]

    # Preprocess right image for model
    right_img = cv2.imread(right_image_path)
    if right_img is None:
        return "Error loading right image", 400  # Return an error if the image is not loaded

    # Combine left and right eye images into one input
    combined_img = np.concatenate((cv2.resize(left_img, (128, 128)), cv2.resize(right_img, (128, 128))), axis=-1)
    combined_img = np.expand_dims(combined_img, axis=0)  # Add batch dimension
    combined_img = combined_img.astype('float32') / 255.0  # Normalize

    # Make prediction with the main model
    prediction = model.predict(combined_img)

    # Get the predicted labels and confidence scores
    predicted_labels = (prediction > 0.5).astype(int)
    confidence_scores = prediction[0]  # All class probabilities

    # Prepare predicted diseases and their confidence scores
    predicted_diseases = [
        {
            'label': disease_labels[key],
            'probability': confidence_scores[idx] * 100  # Store the probability in percentage
        }
        for idx, key in enumerate(disease_labels.keys()) if predicted_labels[0][idx] == 1
    ]
    
    # Collect all diseases with their probabilities
    all_diseases_with_probabilities = [
        {
            'label': disease_labels[key],
            'probability': confidence_scores[idx] * 100  # Store the probability in percentage
        }
        for idx, key in enumerate(disease_labels.keys())
    ]

    # Handle cases where no diseases are detected
    if not predicted_diseases:
        predicted_diseases = [{'label': 'No diseases detected', 'probability': 0.0}]

    # Collect patient data
    patient_data = {
        'name': request.form['name'],
        'email': request.form['email'],
        'mobile': request.form['mobile'],
        'diseases': predicted_diseases,  # Use the new format
        'all_diseases_probabilities': all_diseases_with_probabilities,
          'type': predicted_class_name  # Add this line
    }

    # Optionally send patient data to another backend
    response = requests.post('http://localhost:3000/savePatientData', json=patient_data)

    # Return the results to result.html
    return render_template(
        'result.html',
        patient_name=patient_data['name'],
        patient_email=patient_data['email'],
        patient_mobile=patient_data['mobile'],
        predicted_diseases=patient_data['diseases'],  # Pass the diseases data
        all_diseases_probabilities=patient_data['all_diseases_probabilities'],  # Pass all probabilities
        left_image=left_image.filename,
        right_image=right_image.filename,
        type_of_diabetes=predicted_class_name
    )

if __name__ == '__main__':
    app.run(debug=True)
