from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import numpy as np
import torch
import torch.nn.functional as F
from torchvision import transforms
import os
from datetime import datetime
from pathlib import Path

from model import build_model, ResNet9_SE


# ==============================
# APP SETUP
# ==============================
app = Flask(__name__)
CORS(app)

BASE_DIR = Path(__file__).resolve().parent.parent

# ==============================
# IN-MEMORY STORAGE (Simple)
# ==============================
# Simple in-memory list for storing predictions
predictions_storage = []


# ==============================
# MODEL CONFIG
# ==============================
PYTORCH_CLASSES = [
    "Strawberry___Leaf_scorch",
    "Strawberry___healthy",
    "powdery_mildew"
]

MODEL_PATH = BASE_DIR / "model_best.pth"
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
MODEL_ARCH = os.environ.get("MODEL_ARCH", "resnet9_se")

pytorch_model = None
model_loaded = False

# ==============================
# LOAD MODEL
# ==============================
def load_pytorch_model():
    global pytorch_model, model_loaded

    if not MODEL_PATH.exists():
        print(f"[WARNING] Model not found at {MODEL_PATH}")
        return

    try:
        pytorch_model = build_model(arch=MODEL_ARCH, num_classes=3).to(DEVICE)
        pytorch_model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
        pytorch_model.eval()
        model_loaded = True

        print("[OK] Model loaded successfully")

    except Exception as e:
        print(f"[ERROR] Failed to load model: {e}")

load_pytorch_model()

# ==============================
# IMAGE PREPROCESS
# ==============================
def preprocess_image(pil_image):
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406],
                             [0.229, 0.224, 0.225])
    ])
    return transform(pil_image).unsqueeze(0).to(DEVICE)

# ==============================
# API ROUTES
# ==============================

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "model_loaded": model_loaded,
        "classes": PYTORCH_CLASSES
    })


@app.route("/predict", methods=["POST"])
def predict():
    if not model_loaded:
        return jsonify({"error": "Model not loaded"}), 503

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    try:
        file = request.files["file"]
        image = Image.open(file).convert("RGB")

        tensor = preprocess_image(image)

        with torch.no_grad():
            outputs = pytorch_model(tensor)
            probs = F.softmax(outputs, dim=1)
            confidence, predicted = torch.max(probs, 1)

        result = PYTORCH_CLASSES[predicted.item()]
        confidence_value = confidence.item() * 100

        # Save to in-memory storage
        predictions_storage.append({
            "prediction": result,
            "confidence": confidence_value,
            "time": str(datetime.now())
        })

        return jsonify({
            "prediction": result,
            "confidence": confidence_value
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/history", methods=["GET"])
def history():
    try:
        return jsonify(predictions_storage)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==============================
# RUN APP
# ==============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
