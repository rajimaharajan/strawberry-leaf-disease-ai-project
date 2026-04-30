# StrawberryGuard MERN Server

This is the Node.js/Express backend for the StrawberryGuard AI application.

## Prerequisites

- Node.js (v14+)
- MongoDB (running locally or connection string to MongoDB Atlas)

## Installation

```bash
cd server
npm install
```

## Environment Variables

Create a `.env` file in the `server` directory:

```env
PORT=3000
MONGODB_URI=mongodb://localhost:27017/strawberryguard
JWT_SECRET=your_secret_key
PYTHON_ML_URL=http://localhost:5000
```

## Running the Server

### Development Mode
```bash
npm run dev
```

### Production Mode
```bash
npm start
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login user |
| GET | `/api/auth/profile` | Get user profile (protected) |
| POST | `/api/predict` | Predict disease (protected, multipart/form-data) |
| GET | `/api/history` | Get prediction history (protected) |
| DELETE | `/api/history/:id` | Delete prediction (protected) |

## Architecture

```
React Frontend (Port 3000/5173)
        ↓
   MERN Server (Node.js/Express - Port 3000)
        ↓
   Python ML Service (Flask - Port 5000)
        ↓
   PyTorch Model (ResNet9_SE)
```

## Running the Full Stack

1. **Start MongoDB** (if running locally)
2. **Start Python ML Service**:
   ```bash
   cd backend
   python app.py
   ```
3. **Start MERN Server**:
   ```bash
   cd server
   npm run dev
   ```
4. **Start React Frontend**:
   ```bash
   cd frontend
   npm start
   ```

## Tech Stack

- **Runtime**: Node.js
- **Framework**: Express.js
- **Database**: MongoDB with Mongoose
- **Authentication**: JWT + bcryptjs
- **File Upload**: Multer
- **ML Integration**: Axios → Python Flask service
