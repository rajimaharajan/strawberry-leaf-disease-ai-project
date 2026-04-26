from flask import Flask, request, jsonify, send_from_directory
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

from db import collection
from model import build_model, ResNet9_SE

BASE_DIR = Path(__file__).resolve().parent.parent  # project root
BUILD_DIR = BASE_DIR / "frontend" / "build"

app = Flask(__name__, static_folder=str(BUILD_DIR / "static" ), static_url_path='/static')
CORS(app)  # Enable CORS for all domains on all routes

# ========== LOAD PYTORCH MODEL ==========
# ImageFolder sorts class names alphabetically:
# 0: Strawberry___Leaf_scorch, 1: Strawberry___healthy, 2: powdery_mildew
PYTORCH_CLASSES = [
    "Strawberry___Leaf_scorch",
    "Strawberry___healthy",
    "powdery_mildew"
]

MODEL_PATH = BASE_DIR / "model_best.pth"
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Architecture selector: 'resnet9_se' | 'resnet18_se' | 'resnet18'
# For IEEE paper experiments, switch to 'resnet18_se' after training.
MODEL_ARCH = os.environ.get("MODEL_ARCH", "resnet9_se")

pytorch_model = None
model_loaded = False

def load_pytorch_model():
    global pytorch_model, model_loaded
    if not MODEL_PATH.exists():
        print(f"[WARNING] PyTorch model not found at {MODEL_PATH}")
        return
    try:
        pytorch_model = build_model(arch=MODEL_ARCH, num_classes=3).to(DEVICE)
        pytorch_model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
        pytorch_model.eval()
        model_loaded = True
        print(f"[OK] PyTorch {MODEL_ARCH} model loaded from {MODEL_PATH}")
        print(f"[OK] Classes: {PYTORCH_CLASSES}")
    except Exception as e:
        print(f"[ERROR] Failed to load PyTorch model: {e}")

load_pytorch_model()

# ========== IMAGE PREPROCESSING ==========
def preprocess_image(pil_image):
    """Preprocess PIL image for ResNet9 model (same as training)."""
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    tensor = transform(pil_image).unsqueeze(0).to(DEVICE)
    return tensor

# ========== TRAINING STATUS ==========
training_status = {
    "is_training": False,
    "progress": 0,
    "current_epoch": 0,
    "total_epochs": 0,
    "message": "Not started",
    "last_result": None
}

def update_training_status(**kwargs):
    for k, v in kwargs.items():
        training_status[k] = v

# ========== TRAINING BACKGROUND THREAD ==========
def run_training_async(epochs=5):
    """Run training in background thread."""
    global training_status, pytorch_model, model_loaded
    import sys
    import time
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import DataLoader
    from torchvision import datasets

    update_training_status(
        is_training=True,
        progress=0,
        current_epoch=0,
        total_epochs=epochs,
        message="Initializing training...",
        last_result=None
    )

    try:
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])

        train_dataset = datasets.ImageFolder(root=str(BASE_DIR / "dataset" / "train"), transform=transform)
        test_dataset = datasets.ImageFolder(root=str(BASE_DIR / "dataset" / "test"), transform=transform)

        if len(train_dataset) == 0:
            update_training_status(is_training=False, message="ERROR: No training images found!")
            return

        train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True, num_workers=0)
        test_loader = DataLoader(test_dataset, batch_size=16, shuffle=False, num_workers=0)

        model = ResNet9_SE(num_classes=3).to(device)
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(model.parameters(), lr=0.001)

        best_acc = 0.0

        for epoch in range(epochs):
            start_time = time.time()
            update_training_status(
                current_epoch=epoch + 1,
                message=f"Training epoch {epoch + 1}/{epochs}...",
                progress=int((epoch / epochs) * 100)
            )

            model.train()
            running_loss = 0.0
            correct = 0
            total = 0
            batch_count = 0

            for images, labels in train_loader:
                images, labels = images.to(device), labels.to(device)
                optimizer.zero_grad()
                outputs = model(images)
                loss = criterion(outputs, labels)
                loss.backward()
                optimizer.step()

                running_loss += loss.item()
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
                batch_count += 1

            train_acc = 100 * correct / total

            # Evaluation
            model.eval()
            test_correct = 0
            test_total = 0
            with torch.no_grad():
                for images, labels in test_loader:
                    images, labels = images.to(device), labels.to(device)
                    outputs = model(images)
                    _, predicted = torch.max(outputs.data, 1)
                    test_total += labels.size(0)
                    test_correct += (predicted == labels).sum().item()

            test_acc = 100 * test_correct / test_total if test_total > 0 else 0
            epoch_time = time.time() - start_time

            update_training_status(
                message=f"Epoch {epoch + 1}/{epochs} complete - Test Acc: {test_acc:.2f}%",
                progress=int(((epoch + 1) / epochs) * 100)
            )

            # Save model
            torch.save(model.state_dict(), str(BASE_DIR / "model.pth"))
            
            if test_acc > best_acc:
                best_acc = test_acc
                torch.save(model.state_dict(), str(BASE_DIR / "model_best.pth"))

        # Reload the best model for predictions
        pytorch_model = model
        pytorch_model.eval()
        model_loaded = True

        update_training_status(
            is_training=False,
            progress=100,
            message=f"Training complete! Best accuracy: {best_acc:.2f}%",
            last_result={"best_accuracy": round(best_acc, 2), "epochs": epochs}
        )

    except Exception as e:
        update_training_status(is_training=False, message=f"Training failed: {str(e)}")
        import traceback
        traceback.print_exc()

# ========== API ROUTES ==========

@app.route("/predict", methods=["POST"])
def predict():
    if not model_loaded or pytorch_model is None:
        return jsonify({"error": "Model not loaded. Train model first."}), 503

    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    try:
        file = request.files["file"]
        image = Image.open(file).convert("RGB")
        
        # Preprocess and predict
        tensor = preprocess_image(image)
        
        with torch.no_grad():
            outputs = pytorch_model(tensor)
            probabilities = F.softmax(outputs, dim=1)
            confidence, predicted_idx = torch.max(probabilities, 1)
        
        predicted_idx = predicted_idx.item()
        confidence_value = confidence.item() * 100
        result = PYTORCH_CLASSES[predicted_idx]

        # Save to MongoDB
        try:
            collection.insert_one({
                "prediction": result,
                "confidence": confidence_value,
                "time": str(datetime.now())
            })
        except Exception as db_err:
            print(f"[DB Warning] Could not save prediction: {db_err}")

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


# ========== SERVE REACT FRONTEND ==========
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
    """Serve React app for all non-API routes."""
    if path.startswith('predict') or path.startswith('history') or path.startswith('health') or path.startswith('train'):
        return jsonify({"error": "Not found"}), 404
    file_path = BUILD_DIR / path
    if file_path.exists() and file_path.is_file():
        return send_from_directory(BUILD_DIR, path)
    return send_from_directory(BUILD_DIR, 'index.html')


if __name__ == "__main__":
    app.run(debug=True, port=5000, use_reloader=False)

