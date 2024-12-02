from flask import Flask, request, jsonify
from flask_cors import CORS
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array, load_img
import numpy as np
import json
from PIL import Image
from io import BytesIO
import os

app = Flask(__name__)
CORS(app)

# Paths to model and labels map
try:
    model = load_model('./face_mask_detection_model.h5')
    print("Model loaded successfully!")
except Exception as e:
    print(f"Model load error: {e}")

try:
    with open('labels_map.json', 'r') as f:
        labels_map = json.load(f)
    labels_map = {int(k): v for k, v in labels_map.items()}
    print(f"Labels map loaded successfully: {labels_map}")
except Exception as e:
    print(f"Labels map error: {e}")

def preprocess_image(img, target_size=(150, 150)):
    """Preprocess the uploaded image."""
    try:
        img = img.resize(target_size)
        img_array = img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = img_array / 255.0
        print(f"Preprocessed image shape: {img_array.shape}")
        return img_array
    except Exception as e:
        raise ValueError(f"Error during image preprocessing: {e}")

@app.route('/predict', methods=['POST'])
def predict():
    """Handle image prediction requests."""
    if model is None or not labels_map:
        return jsonify({"error": "Model or labels map not properly loaded"}), 500

    # Check for image in request
    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No image selected"}), 400

    try:
        print(f"Received file: {file.filename}")
        print(f"Content type: {file.content_type}")

        # Check if file is an image
        if not file.content_type.startswith('image/'):
            return jsonify({"error": "Invalid file type. Please upload an image."}), 400

        # Open image from file.stream using PIL
        img = Image.open(file.stream)
        img = img.convert('RGB')  # Ensure it's in RGB format

        # Preprocess the image
        img_array = preprocess_image(img)

        print("Running model prediction...")
        predictions = model.predict(img_array)
        class_idx = np.argmax(predictions[0])

        # Retrieve label and confidence
        confidence = float(predictions[0][class_idx])

        if class_idx not in labels_map:
            return jsonify({"error": f"Predicted class index {class_idx} not found in labels map"}), 500

        predicted_label = labels_map[class_idx]

        # Check if "with_mask" confidence is below 70%
        if predicted_label == "with_mask" and confidence < 0.7:
            predicted_label = "incorrect_mask"

        print(f"Prediction: {predicted_label}, Confidence: {confidence}")
        return jsonify({
            "prediction": predicted_label,
            "confidence": confidence
        })
    except Exception as e:
        print(f"Error during prediction: {e}")
        return jsonify({"error": f"An error occurred during prediction: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True)
