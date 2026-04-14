# Helper script to start backend
cd d:\explainable-misinformation-detection\backend
.\venv\Scripts\activate
python -m uvicorn app.main:app --reload
