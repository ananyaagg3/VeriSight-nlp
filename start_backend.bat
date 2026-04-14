@echo off
echo Starting Backend Server...
cd /d "D:\explainable-misinformation-detection\backend"
call .\venv\Scripts\activate.bat
python -m uvicorn app.main:app --reload
pause
