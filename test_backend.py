"""
Test script to verify the Flask backend /predict endpoint works correctly.
Run this after starting the backend: python backend/app.py
"""
import requests
import sys
from pathlib import Path

BASE_URL = "http://localhost:5000"
TEST_IMAGE = Path("dataset/test/Strawberry___healthy/1d92fcef-79d0-469b-b9b1-71a318505821___RS_HL 4487.JPG")

def test_health():
    print("[TEST] Checking /health endpoint...")
    try:
        resp = requests.get(f"{BASE_URL}/health", timeout=5)
        data = resp.json()
        print(f"  Status: {data.get('status')}")
        print(f"  Model: {data.get('model_status')}")
        print(f"  Classes: {data.get('classes')}")
        return data.get('model_status') == 'loaded'
    except Exception as e:
        print(f"  FAILED: {e}")
        return False

def test_predict(image_path):
    print(f"[TEST] Sending prediction request with {image_path.name}...")
    try:
        with open(image_path, 'rb') as f:
            files = {'file': (image_path.name, f, 'image/jpeg')}
            resp = requests.post(f"{BASE_URL}/predict", files=files, timeout=30)
        
        print(f"  HTTP Status: {resp.status_code}")
        data = resp.json()
        
        if resp.status_code == 200:
            print(f"  Prediction: {data.get('prediction')}")
            print(f"  Confidence: {data.get('confidence'):.2f}%")
            return True
        else:
            print(f"  Error: {data.get('error')}")
            return False
    except Exception as e:
        print(f"  FAILED: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("StrawberryGuard Backend Test")
    print("=" * 50)
    
    health_ok = test_health()
    if not health_ok:
        print("\n[ERROR] Backend not healthy. Make sure Flask is running on port 5000.")
        print("        Run: cd backend && python app.py")
        sys.exit(1)
    
    if not TEST_IMAGE.exists():
        print(f"\n[ERROR] Test image not found: {TEST_IMAGE}")
        sys.exit(1)
    
    predict_ok = test_predict(TEST_IMAGE)
    
    print("\n" + "=" * 50)
    if predict_ok:
        print("ALL TESTS PASSED ✅")
    else:
        print("TESTS FAILED ❌")
    print("=" * 50)

