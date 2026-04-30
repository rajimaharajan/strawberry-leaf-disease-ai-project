const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const dotenv = require('dotenv');
const multer = require('multer');
const axios = require('axios');
const path = require('path');
const fs = require('fs');

// Load environment variables
dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));

// Ensure uploads directory exists
const uploadsDir = path.join(__dirname, 'uploads');
if (!fs.existsSync(uploadsDir)) {
  fs.mkdirSync(uploadsDir, { recursive: true });
}

// ==============================
// MONGODB CONNECTION
// ==============================
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/strawberryguard';

mongoose.connect(MONGODB_URI)
  .then(() => console.log('✅ MongoDB Connected'))
  .catch(err => console.error('❌ MongoDB Connection Error:', err));

// ==============================
// MONGODB MODELS
// ==============================
// User Model
const userSchema = new mongoose.Schema({
  username: { type: String, required: true, unique: true },
  email: { type: String, required: true, unique: true },
  password: { type: String, required: true },
  createdAt: { type: Date, default: Date.now }
});

const User = mongoose.model('User', userSchema);

// Prediction History Model
const predictionSchema = new mongoose.Schema({
  userId: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
  imageUrl: { type: String },
  prediction: { type: String, required: true },
  confidence: { type: Number, required: true },
  timestamp: { type: Date, default: Date.now }
});

const Prediction = mongoose.model('Prediction', predictionSchema);

// ==============================
// FILE UPLOAD CONFIG
// ==============================
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, 'uploads/');
  },
  filename: (req, file, cb) => {
    cb(null, Date.now() + '-' + file.originalname);
  }
});

const upload = multer({ storage });

// ==============================
// AUTH MIDDLEWARE
// ==============================
const authMiddleware = (req, res, next) => {
  const token = req.header('Authorization')?.replace('Bearer ', '');
  if (!token) {
    return res.status(401).json({ error: 'Access denied. No token provided.' });
  }
  try {
    const decoded = require('jsonwebtoken').verify(token, process.env.JWT_SECRET || 'strawberryguard_secret');
    req.userId = decoded.id;
    next();
  } catch (err) {
    res.status(401).json({ error: 'Invalid token.' });
  }
};

// ==============================
// PYTHON ML SERVICE CONFIG
// ==============================
const PYTHON_ML_URL = process.env.PYTHON_ML_URL || 'http://localhost:5000';

// ==============================
// API ROUTES
// ==============================

// Health Check - Also checks Python ML service
app.get('/api/health', async (req, res) => {
  try {
    // Try to connect to Python ML service
    const mlResponse = await axios.get(`${PYTHON_ML_URL}/health`, { timeout: 2000 });
    res.json({ 
      status: 'ok', 
      mern_server: 'running',
      ml_service: 'connected',
      model_loaded: mlResponse.data.model_loaded || false
    });
  } catch (err) {
    // ML service not available
    res.json({ 
      status: 'ok', 
      mern_server: 'running',
      ml_service: 'disconnected',
      model_loaded: false
    });
  }
});

// Register User
app.post('/api/auth/register', async (req, res) => {
  try {
    const { username, email, password } = req.body;
    
    // Check if user exists
    const existingUser = await User.findOne({ $or: [{ email }, { username }] });
    if (existingUser) {
      return res.status(400).json({ error: 'User already exists' });
    }
    
    // Hash password
    const bcrypt = require('bcryptjs');
    const hashedPassword = await bcrypt.hash(password, 10);
    
    // Create user
    const newUser = new User({ username, email, password: hashedPassword });
    await newUser.save();
    
    res.status(201).json({ message: 'User registered successfully' });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Login User
app.post('/api/auth/login', async (req, res) => {
  try {
    const { email, password } = req.body;
    
    // Find user
    const user = await User.findOne({ email });
    if (!user) {
      return res.status(400).json({ error: 'Invalid credentials' });
    }
    
    // Verify password
    const bcrypt = require('bcryptjs');
    const isMatch = await bcrypt.compare(password, user.password);
    if (!isMatch) {
      return res.status(400).json({ error: 'Invalid credentials' });
    }
    
    // Generate JWT
    const jwt = require('jsonwebtoken');
    const token = jwt.sign(
      { id: user._id, username: user.username },
      process.env.JWT_SECRET || 'strawberryguard_secret',
      { expiresIn: '24h' }
    );
    
    res.json({ token, username: user.username, email: user.email });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Get User Profile
app.get('/api/auth/profile', authMiddleware, async (req, res) => {
  try {
    const user = await User.findById(req.userId).select('-password');
    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }
    res.json(user);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Predict Disease (Calls Python ML Service)
app.post('/api/predict', authMiddleware, upload.single('file'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No file uploaded' });
    }
    
    const imagePath = req.file.path;
    
    // Send to Python ML Service
    const formData = new (require('form-data'))();
    formData.append('file', fs.createReadStream(imagePath));
    
    const mlResponse = await axios.post(`${PYTHON_ML_URL}/predict`, formData, {
      headers: {
        ...formData.getHeaders()
      }
    });
    
    const { prediction, confidence } = mlResponse.data;
    
    // Save prediction to database
    const newPrediction = new Prediction({
      userId: req.userId,
      imageUrl: `/uploads/${req.file.filename}`,
      prediction,
      confidence
    });
    await newPrediction.save();
    
    res.json({ prediction, confidence, imageUrl: `/uploads/${req.file.filename}` });
  } catch (err) {
    console.error('ML Prediction Error:', err.message);
    res.status(500).json({ error: 'Prediction failed. Please try again.' });
  }
});

// Get Prediction History
app.get('/api/history', authMiddleware, async (req, res) => {
  try {
    const history = await Prediction.find({ userId: req.userId })
      .sort({ timestamp: -1 })
      .limit(50);
    res.json(history);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Delete Prediction
app.delete('/api/history/:id', authMiddleware, async (req, res) => {
  try {
    await Prediction.findOneAndDelete({ _id: req.params.id, userId: req.userId });
    res.json({ message: 'Prediction deleted' });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// ==============================
// START SERVER
// ==============================
app.listen(PORT, () => {
  console.log(`✅ MERN Server running on port ${PORT}`);
  console.log(`📡 Connect Python ML Service on port 5000`);
});
