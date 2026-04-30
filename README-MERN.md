# 🍓 StrawberryGuard - MERN Stack Setup Guide

This guide explains how to run the StrawberryGuard project using the MERN Stack (MongoDB, Express.js, React, Node.js) with the Python ML model for disease detection.

## 📋 Prerequisites

| Requirement | Version | Download |
|-------------|---------|----------|
| Node.js | 18+ | [nodejs.org](https://nodejs.org) |
| Python | 3.8+ | [python.org](https://python.org) |
| MongoDB | 6.0+ | [mongodb.com](https://www.mongodb.com/try/download/community) |

## 🚀 Quick Start (One-Click)

Simply run the launcher script:

```bash
run_mern.bat
```

This will automatically:
1. Install Node.js dependencies
2. Install Python dependencies
3. Start Python ML Service (port 5000)
4. Start MERN Server (port 3000)
5. Open React Frontend in browser

---

## 📝 Manual Setup (Step-by-Step)

### Step 1: Install Dependencies

**Node.js:**
```bash
cd server
npm install
```

**Python:**
```bash
pip install flask flask-cors pillow numpy torch torchvision
```

### Step 2: Setup MongoDB

**Option A: Local MongoDB**
1. Download MongoDB Community Server
2. Run: `mongod`
3. Connection string: `mongodb://localhost:27017`

**Option B: MongoDB Atlas (Cloud - Recommended)**
1. Go to [cloud.mongodb.com](https://cloud.mongodb.com)
2. Create free account → Create Cluster
3. Create database user and get connection string
4. Update `server/.env`:
```env
MONGODB_URI=your_connection_string_here
```

### Step 3: Start All Services

**Terminal 1 - Python ML Service:**
```bash
cd backend
python app.py
```
Expected output:
```
[OK] Model loaded successfully
 * Running on http://0.0.0.0:5000
```

**Terminal 2 - MERN Server:**
```bash
cd server
npm run dev
```
Expected output:
```
Server running on port 3000
Connected to MongoDB
```

**Terminal 3 - React Frontend:**
```bash
cd frontend
npm start
```

### Step 4: Access the Application

Open your browser and go to:
```
http://localhost:3000
```

---

## 🔐 How to Use

### 1. Sign Up (First Time)
- Click "Sign Up"
- Enter username, email, password
- Click "Sign Up"

### 2. Login
- Enter email and password
- Click "Login to Dashboard"

### 3. Analyze Image
- Upload a strawberry plant photo (JPG/PNG)
- Click "Analyze"
- View disease diagnosis and confidence score
- Download PDF report (optional)

### 4. Explore Features
- Treatment Videos
- Nearby Pathologists
- Pesticides Guide
- Fertilizers Guide

---

## 🔧 Troubleshooting

### "MongoDB connection failed"
- Make sure MongoDB is running (`mongod`)
- Or check your Atlas connection string in `.env`

### "ML Model not loaded"
- Make sure Python service is running on port 5000
- Check model file exists: `model_best.pth`

### "Port already in use"
- Stop other services using that port
- Or change port in configuration files

### "React not starting"
```bash
cd frontend
rm -rf node_modules
npm install
npm start
```

---

## 📁 Project Structure (MERN)

```
strawberry-project/
├── server/                 # Express.js MERN Backend
│   ├── server.js          # Main server file
│   ├── package.json      # Node dependencies
│   └── .env             # Environment config
│
├── backend/              # Python ML Service
│   ├── app.py          # Flask ML API
│   ├── model.py        # PyTorch model
│   └── model_best.pth  # Trained weights
│
├── frontend/           # React Frontend
│   ├── src/           # React components
│   ├── public/        # Static files
│   └── package.json  # Frontend dependencies
│
└── run_mern.bat      # One-click launcher
```

---

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/register` | POST | Register new user |
| `/api/auth/login` | POST | User login |
| `/api/predict` | POST | Image disease prediction |
| `/api/health` | GET | Check ML service status |

---

## ✅ Verification

After starting all services, you should see:

1. **React Frontend:** http://localhost:3000
   - Login page with strawberry logo

2. **Health Check:** http://localhost:3000/api/health
   ```json
   {"status": "ok", "model_loaded": true}
   ```

3. **MongoDB Connection:** Server logs
   ```
   Connected to MongoDB
   ```

---

## 📞 Support

If you encounter issues:
1. Check all terminals for error messages
2. Ensure MongoDB is running
3. Verify all dependencies are installed
4. Check Python and Node.js versions

---

**Happy Farming! 🍓**
