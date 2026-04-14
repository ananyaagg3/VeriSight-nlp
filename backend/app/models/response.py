from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime


class KeywordEvidence(BaseModel):
    """Keyword with confidence score"""
    word: str
    score: float = Field(..., ge=0.0, le=1.0)
    importance: str  # "high", "medium", "low"


class SourceLink(BaseModel):
    """Source link with metadata"""
    name: str
    url: Optional[str] = None  # Made optional for Wikidata entries without URLs
    verdict: Optional[str] = None
    credibility: Optional[float] = None
    # Additional fields for Wikidata compatibility
    info: Optional[str] = None
    label: Optional[str] = None
    claim: Optional[str] = None


class ClaimAnalysis(BaseModel):
    """Individual claim analysis with evidence"""
    claim: str
    verdict: str
    confidence: float
    evidence: str
    sources: List[SourceLink] = []


class AnalysisResponse(BaseModel):
    """Response model for analysis"""
    verdict: str = Field(..., description="AUTHENTIC, MISINFORMATION, or NEEDS_VERIFICATION")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    keywords: List[KeywordEvidence] = Field(default=[], description="Top evidence keywords")
    sources: List[SourceLink] = Field(default=[], description="Source links")
    explanation: str = Field(..., description="Human-readable explanation")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    language: str = Field(..., description="Detected language")
    analysis_id: str = Field(..., description="Unique analysis ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Optional multimodal fields
    image_analysis: Optional[Dict] = None
    sentiment: Optional[str] = None
    
    # NEW: Score breakdown per FactWeave guide
    score_breakdown: Optional[Dict] = None
    fusion_method: Optional[str] = None
    final_score: Optional[float] = None
    cross_modal_consistency: Optional[float] = None
    model_info: Optional[Dict] = None
    
    # Detailed explainability
    detailed_claims: Optional[List[ClaimAnalysis]] = None

    # Related news articles (from News API)
    related_articles: Optional[List[Dict]] = None


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: str
    status_code: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    database: str
    models_loaded: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)
