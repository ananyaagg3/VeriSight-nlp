from fastapi import APIRouter
from datetime import datetime

from app.models.response import HealthResponse
from app.services.ml_pipeline import ml_pipeline  # Direct import

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    models_loaded = ml_pipeline.models_loaded
    
    return HealthResponse(
        status="healthy" if models_loaded else "loading",
        database="connected",
        models_loaded=models_loaded,
        timestamp=datetime.utcnow()
    )
