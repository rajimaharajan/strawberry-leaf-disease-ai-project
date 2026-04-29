from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import numpy as np
import torch
import torch.nn.functional as F
from torchvision import transforms
import os
import threading
from datetime import datetime
from pathlib import Path


from model import build_model, ResNet9_SE

<<<<<<< HEAD
BASE_DIR = Path(__file__).resolve().parent.parent  # project root

app = Flask(__name__)
CORS(app)  # Enable CORS for all domains on all routes

DISABLE_TRAINING = os.environ.get('PORT') != '5000'

# ========== LOAD PYTORCH MODEL ==========
# ImageFolder sorts class names alphabetically:
# 0: Strawberry___Leaf_scorch, 1: Strawberry___healthy, 2: powdery_mildew
=======
# ==============================
# APP SETUP
# ==============================
app = Flask(__name__)
CORS(app)

BASE_DIR = Path(__file__).resolve().parent.parent

# ==============================
# MODEL CONFIG
# ==============================
>>>>>>> f6beff1610c54fcc2b6e3c4fb1c3c20002869f46
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
        "model_loaded": model_loaded
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

        # Save to DB
        try:
            collection.insert_one({
                "prediction": result,
                "confidence": confidence_value,
                "time": str(datetime.now())
            })
        except Exception as e:
            print(f"[DB ERROR]: {e}")

        return jsonify({
            "prediction": result,
            "confidence": confidence_value
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/history", methods=["GET"])
def history():
    try:
        data = list(collection.find({}, {"_id": 0}))
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


<<<<<<< HEAD
@app.route("/health", methods=["GET"])
def health():
    model_status = "loaded" if model_loaded else "not_loaded"
    return jsonify({
        "status": "ok",
        "model_status": model_status,
        "classes": PYTORCH_CLASSES
    })


@app.route("/train", methods=["POST"])
def start_training():
    if DISABLE_TRAINING:
        return jsonify({"error": "Training disabled in production."}), 503
    if training_status["is_training"]:
        return jsonify({"error": "Training already in progress"}), 409

    data = request.get_json(silent=True) or {}
    epochs = data.get("epochs", 5)
    epochs = min(max(epochs, 1), 20)  # Clamp between 1-20

    thread = threading.Thread(target=run_training_async, args=(epochs,))
    thread.daemon = True
    thread.start()

    return jsonify({
        "message": "Training started",
        "epochs": epochs,
        "status": training_status
    })


@app.route("/train-status", methods=["GET"])
def get_training_status():
    return jsonify(training_status)


# Frontend served separately by Netlify (pure API backend)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

=======
# ==============================
# RUN APP (RENDER FIX)
# ==============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
>>>>>>> f6beff1610c54fcc2b6e3c4fb1c3c20002869f46
