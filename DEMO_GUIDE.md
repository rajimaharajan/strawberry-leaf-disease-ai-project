# 🍓 StrawberryGuard - Demo Guide for Teacher

## What is this project?
**StrawberryGuard** is an AI-powered web application that detects diseases in strawberry plant leaves using deep learning (PyTorch ResNet9 + SE blocks). Users upload a photo of a strawberry leaf, and the AI predicts whether the plant is:
- ✅ **Healthy**
- ⚠️ **Leaf Scorch** (disease)
- ⚠️ **Powdery Mildew** (disease)

The app also provides treatment recommendations, care tips, feeding schedules, and downloadable PDF reports.

---

## 🏗️ Architecture

| Component | Technology | Port |
|-----------|-----------|------|
| **Frontend** | React 19 + CSS3 | 3000 |
| **Backend API** | Flask (Python) + PyTorch | 5000 |
| **AI Model** | ResNet9-SE (trained on 3-class dataset) | - |
| **Database** | MongoDB (optional, for prediction history) | 27017 |

---

## 🚀 How to Run (Step-by-Step)

### Option 1: Automatic (Recommended for Demo)

1. **Open Terminal / Command Prompt**
2. **Navigate to project folder:**
   ```bash
   cd "C:\Users\KUMAR\Desktop\Documents\sem 6\project sem 6\strawberry-project"
   ```
3. **Run the unified script:**
   ```bash
   run.bat
   ```
   This will:
   - Install frontend dependencies (if needed)
   - Build the React app
   - Start Flask backend on port 5000
4. **Open browser:** Go to `http://localhost:5000`

---

### Option 2: Manual (For Development)

#### Terminal 1 — Start Backend
```bash
cd "C:\Users\KUMAR\Desktop\Documents\sem 6\project sem 6\strawberry-project\backend"
python app.py
```
- Backend runs on: `http://localhost:5000`
- You should see: `[OK] PyTorch resnet9_se model loaded`

#### Terminal 2 — Start Frontend
```bash
cd "C:\Users\KUMAR\Desktop\Documents\sem 6\project sem 6\strawberry-project\frontend"
npm start
```
- Frontend runs on: `http://localhost:3000`
- Browser will open automatically

---

## 🧪 How to Test the AI Prediction

### Method 1: Using the Web App
1. Open `http://localhost:3000` (or `http://localhost:5000` if using built version)
2. Login with any credentials (demo mode)
3. You will see a green banner: **"✅ AI Model Ready — Upload an image to analyze"**
4. Click the upload area and select a strawberry leaf image from:
   ```
   dataset/test/Strawberry___healthy/
   dataset/test/powdery_mildew/
   ```
5. Click **"🔍 Analyze"**
6. See the prediction result with confidence %, care tips, and remedies!
7. Click **"📄 Download PDF Report"** to save the diagnosis.

### Method 2: Backend API Test (Command Line)
```bash
cd "C:\Users\KUMAR\Desktop\Documents\sem 6\project sem 6\strawberry-project"
python test_backend.py
```
Expected output:
```
[TEST] Checking /health endpoint...
  Status: ok
  Model: loaded
[TEST] Sending prediction request...
  Prediction: Strawberry___healthy
  Confidence: 99.67%
ALL TESTS PASSED ✅
```

---

## 📁 Key Files Changed

| File | What Changed |
|------|-------------|
| `backend/app.py` | Added CORS, changed port to 5000 |
| `backend/model.py` | Fixed bias=True to match saved model weights |
| `frontend/src/api.js` | Updated API base URL to localhost:5000 |
| `frontend/src/Dashboard.js` | Added backend health check & status banner |
| `frontend/src/Dashboard.css` | Added banner styles |
| `frontend/package.json` | Updated proxy to localhost:5000 |
| `run.bat` | Updated port reference to 5000 |
| `test_backend.py` | New file to test backend API |

---

## 🎯 Demo Flow for Teacher

1. **Show the Login Page** — Clean, modern UI with strawberry branding
2. **Login and reach Dashboard** — Green banner confirms "AI Model Ready"
3. **Upload a Healthy Leaf** — From `dataset/test/Strawberry___healthy/`
   - Result: ✅ "Healthy" with high confidence
   - Show: Care tips, feeding schedule
4. **Upload a Diseased Leaf** — From `dataset/test/powdery_mildew/`
   - Result: ⚠️ "Powdery Mildew" detected
   - Show: Recommended remedies, treatment videos link
5. **Download PDF Report** — Professional diagnosis report with image
6. **Show Additional Features:**
   - 🎬 Treatment Videos
   - 👥 Nearby Pathologists
   - 🌿 Pesticides & Fertilizers guides
   - 📅 Seasonal Growing Calendar

---

## ⚠️ Troubleshooting

| Problem | Solution |
|---------|----------|
| "Backend disconnected" banner | Make sure Flask is running: `python backend/app.py` |
| "Model not loaded" error | Check that `model_best.pth` exists in project root |
| Port 5000 already in use | Kill other Python processes: `taskkill /F /IM python.exe` |
| CORS errors in browser | CORS is enabled in `backend/app.py` — restart backend |
| MongoDB errors | MongoDB is optional; predictions still work without it |

---

## 📊 Model Performance

- **Architecture:** ResNet9 with Squeeze-and-Excitation (SE) blocks
- **Classes:** 3 (Healthy, Leaf Scorch, Powdery Mildew)
- **Input Size:** 224×224 RGB images
- **Test Accuracy:** ~99%+ (as shown in demo)
- **Model File:** `model_best.pth` (26 MB)

---

**Developed with ❤️ by GJR**

