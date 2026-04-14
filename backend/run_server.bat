@echo off
echo ===================================================
echo 🚀 FactWeave Server Launcher
echo ===================================================

echo.
echo 🛑 Clearing port 8000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do taskkill /f /pid %%a >nul 2>&1

echo.
echo 🔧 Checking environment...
call venv\Scripts\activate
python verify_env.py

echo.
echo 🚀 Starting Backend Server on Port 8000...
echo ℹ️  Note: First request will take time to load models.
echo.
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

pause
