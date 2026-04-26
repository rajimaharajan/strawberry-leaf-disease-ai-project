@echo off
echo ==========================================
echo    StrawberryGuard - Unified Server
echo ==========================================
echo.

echo [1/3] Installing frontend dependencies (if needed)...
cd frontend
call npm install
echo.

echo [2/3] Building React frontend...
call npm run build
echo.
cd ..

echo [3/3] Starting Flask server on port 5000...
cd backend
python app.py
cd ..
