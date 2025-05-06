from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import base64
import cv2
import numpy as np
from PIL import Image
import io
from werkzeug.utils import secure_filename
from image_analyzer import analyze_eye_image
from ml_predictor import predict_jaundice_ml

app = Flask(__name__)

# Folder for uploaded images
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ▶️ Route to load info.html first
@app.route('/')
def home():
    return render_template('info.html')

# ▶️ Route for the actual tool page (previously default)
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def handle_submission():
    form_data = request.form.to_dict()
    eye_image = request.files.get('eye_image')

    if eye_image:
        filename = secure_filename(eye_image.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        eye_image.save(image_path)
        form_data['image_filename'] = filename

        # Read image and convert to base64
        with open(image_path, "rb") as f:
            image_data = f.read()
            encoded_image = base64.b64encode(image_data).decode('utf-8')
            eye_image_b64 = f"data:image/jpeg;base64,{encoded_image}"

        # Eye image analysis
        try:
            header, b64data = eye_image_b64.split(",")
            image_bytes = base64.b64decode(b64data)
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            image_np = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            eye_risk = analyze_eye_image(image_np)
        except Exception as e:
            eye_risk = False
    else:
        form_data['image_filename'] = ''
        eye_risk = False

    # ML features
    try:
        features = [
            float(form_data["age"]),
            1.0 if form_data["gender"].lower() == "male" else 0.0,
            float(form_data["total_bilirubin"]),
            float(form_data["direct_bilirubin"]),
            float(form_data["alt"]),
            float(form_data["ast"]),
            float(form_data["alk_phos"]),
            float(form_data["hemoglobin"]),
            1.0 if form_data["fatigue"].lower() == "yes" else 0.0,
            1.0 if form_data["stool_color"].lower() == "dark" else 0.0,
            1.0 if form_data["itching"].lower() == "yes" else 0.0,
            1.0 if form_data["urine_color"].lower() == "dark" else 0.0
        ]
    except Exception as e:
        return f"Error in form data: {e}", 400

    # ML Prediction
    model_result = predict_jaundice_ml(features)
    form_data["risk"] = "High" if model_result == "Jaundice Detected" or eye_risk else "Low"

    # Custom result message
    model_flag = "Jaundice" if model_result == "Jaundice Detected" else "No"
    eye_flag = "Jaundice" if eye_risk else "No"

    if model_flag == "Jaundice" and eye_flag == "Jaundice":
        result_message = '🔴 High risk of jaundice'
    elif model_flag == "No" and eye_flag == "No":
        result_message = '🟢 No jaundice detected. You are normal.'
    elif model_flag == "Jaundice" and eye_flag == "No":
        result_message = '🟠 Your eyes are normal but your medical reports are not good. You may have some liver disorder.'
    elif model_flag == "No" and eye_flag == "Jaundice":
        result_message = '🟡 Your medical reports are clear, but your eyes appear yellow — could be due to other reasons.'
    else:
        result_message = '❓ Inconclusive result. Please try again.'

    form_data["model_flag"] = model_flag
    form_data["eye_flag"] = eye_flag
    form_data["result_message"] = result_message

    return render_template("result.html", data=form_data)

@app.route('/result')
def result_page():
    return render_template('result.html', data={})

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json

    try:
        features = [
            float(data["age"]),
            1.0 if data["gender"].lower() == "male" else 0.0,
            float(data["total_bilirubin"]),
            float(data["direct_bilirubin"]),
            float(data["alt"]),
            float(data["ast"]),
            float(data["alk_phos"]),
            float(data["hemoglobin"]),
            1.0 if data["fatigue"].lower() == "yes" else 0.0,
            1.0 if data["stool_color"].lower() == "dark" else 0.0,
            1.0 if data["itching"].lower() == "yes" else 0.0,
            1.0 if data["urine_color"].lower() == "dark" else 0.0
        ]
    except Exception as e:
        return jsonify({"error": f"Invalid input data: {e}"}), 400

    eye_image_b64 = data.get("eyeImageBase64")
    if eye_image_b64:
        try:
            header, b64data = eye_image_b64.split(",")
            image_data = base64.b64decode(b64data)
            image = Image.open(io.BytesIO(image_data)).convert("RGB")
            image_np = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            eye_risk = analyze_eye_image(image_np)
        except Exception as e:
            return jsonify({"error": f"Error processing image: {e}"}), 500
    else:
        eye_risk = False

    model_result = predict_jaundice_ml(features)
    risk = "High" if model_result == "Jaundice Detected" or eye_risk else "Low"

    return jsonify({
        "riskLevel": risk,
        "factors": ["Eye discoloration detected"] if eye_risk else [],
        "recommendation": "Consult a physician for confirmation." if risk == "High" else "Maintain healthy liver habits."
    })

if __name__ == '__main__':
    app.run(debug=True)
