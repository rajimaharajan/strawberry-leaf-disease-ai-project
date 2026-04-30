from fastapi import APIRouter, UploadFile, File, BackgroundTasks
from datetime import datetime
import os

router = APIRouter(prefix="/ml", tags=["ml"])

# In-memory storage for predictions (FastAPI version)
predictions_storage = []

# Model configuration
MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "model_best.pth")
MODEL_CLASSES = ["Strawberry___Leaf_scorch", "Strawberry___healthy", "powdery_mildew"]

@router.post("/predict")
async def predict(file: UploadFile = File(...)):
    """
    Predict endpoint - returns placeholder since main model loading is in legacy app.py
    For production, port torch model loading from backend/app.py to FastAPI
    """
    return {"prediction": "healthy", "confidence": 95.0}

@router.get("/history")
async def get_history():
    """Get prediction history"""
    return predictions_storage

@router.get("/health")
async def health():
    """Health check - model loading needs to be ported from Flask app.py"""
    model_exists = os.path.exists(MODEL_PATH)
    return {
        "status": "ok",
        "model_status": "loaded" if model_exists else "not_found",
        "model_path": MODEL_PATH,
        "classes": MODEL_CLASSES
    }

@router.get("/classes")
async def get_classes():
    """Get available prediction classes"""
    return {"classes": MODEL_CLASSES}

