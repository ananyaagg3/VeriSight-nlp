from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class AnalysisRequest(BaseModel):
    """Request model for analysis"""
    text: str = Field(..., min_length=10, max_length=5000, description="Text to analyze")
    image_url: Optional[str] = Field(None, description="Optional image URL")
    analyze_image: bool = Field(default=False, description="Whether to analyze image")


class FeedbackRequest(BaseModel):
    """Request model for user feedback"""
    analysis_id: str = Field(..., description="Analysis ID")
    rating: int = Field(..., ge=1, le=5, description="Rating 1-5")
    comment: Optional[str] = Field(None, max_length=500, description="Optional comment")
    is_correct: bool = Field(..., description="Whether the verdict was correct")


class BatchAnalysisRequest(BaseModel):
    """Request model for batch analysis"""
    texts: List[str] = Field(..., max_items=10, description="List of texts to analyze")
