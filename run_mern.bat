@echo off
echo ================================================
echo   StrawberryGuard MERN Stack Launcher
echo ================================================
echo.

REM Check if Node.js is installed
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js not found. Please install Node.js first.
    echo Download: https://nodejs.org
    pause
    exit /b 1
)

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python not found. Please install Python first.
    echo Download: https://python.org
    pause
    exit /b 1
)

echo [1/4] Installing Node.js dependencies...
cd server
npm install
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install Node dependencies
    pause
    exit /b 1
)
cd ..

echo.
echo [2/4] Installing Python dependencies...
pip install flask flask-cors pillow numpy torch torchvision --quiet
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Some Python packages may already be installed
)

echo.
echo ================================================
echo   IMPORTANT: MongoDB Setup
echo ================================================
echo You need MongoDB running for user authentication.
echo.
echo Option 1: Use MongoDB Atlas (Cloud)
echo   - Create free account at https://cloud.mongodb.com
echo   - Create cluster and get connection string
echo   - Update server/.env with your connection string
echo.
echo Option 2: Use Local MongoDB
echo   - Download: https://www.mongodb.com/try/download/community
echo   - Run: mongod
echo.
echo Press any key to continue (or close if MongoDB is ready)...
pause >nul

echo.
echo ================================================
echo   Starting Services...
echo ================================================
echo.

REM Start Python ML Service in background
echo [3/4] Starting Python ML Service (port 5000)...
start "ML Service" cmd /k "cd backend && python app.py"

REM Wait for ML service to start
timeout /t 3 /nobreak >nul

REM Start MERN Server
echo [4/4] Starting MERN Server (port 3000)...
start "MERN Server" cmd /k "cd server && npm run dev"

REM Wait for server to start
timeout /t 3 /nobreak >nul

REM Open React Frontend
echo.
echo Starting React Frontend...
start "" http://localhost:3000

echo.
echo ================================================
echo   ✅ All Services Started!
echo ================================================
echo.
echo URLs:
echo   - React Frontend: http://localhost:3000
echo   - MERN API:      http://localhost:3000/api
echo   - ML Service:   http://localhost:5000
echo.
echo Login credentials will be stored in MongoDB.
echo.
echo Close this window to stop all services.
echo To stop manually: close each terminal window.
echo.
pause
