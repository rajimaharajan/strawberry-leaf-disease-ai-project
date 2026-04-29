@echo off
cd /d "%~dp0"
echo Starting FastAPI backend...
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
pause
