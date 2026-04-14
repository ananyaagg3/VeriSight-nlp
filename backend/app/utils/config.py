from pydantic_settings import BaseSettings
from pydantic import Field, AliasChoices
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # MongoDB (optional for demo)
    MONGODB_URI: Optional[str] = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "misinformation_db"
    MONGODB_TIMEOUT_MS: Optional[int] = 10000
    
    # APIs (optional)
    GOOGLE_FACT_CHECK_KEY: Optional[str] = None
    CLAIMBUSTER_API_KEY: Optional[str] = None
    NEWSAPI_KEY: Optional[str] = Field(None, validation_alias=AliasChoices("NEWS_API_KEY", "NEWSAPI_KEY"))  # NewsAPI.org
    
    # URLs
    FRONTEND_URL: str = "http://localhost:5173"
    BACKEND_URL: str = "http://localhost:8000"
    
    # Redis (optional)
    REDIS_URL: Optional[str] = None
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Model paths
    TEXT_MODEL_PATH: str = "ml-models/trained_models/text_model_quantized.pt"
    IMAGE_MODEL_PATH: str = "ml-models/trained_models/image_model_quantized.pt"
    MULTIMODAL_MODEL_PATH: str = "ml-models/trained_models/multimodal_quantized.pt"
    
    # Performance
    MAX_TEXT_LENGTH: int = 2048  # Increased to handle long paragraphs (up to ~1500 words)
    MAX_IMAGE_SIZE: int = 5 * 1024 * 1024  # 5MB
    CACHE_TTL: int = 86400  # 24 hours
    
    # API Quotas
    GOOGLE_FACT_CHECK_DAILY_LIMIT: int = 1000
    WIKIDATA_HOURLY_LIMIT: int = 5000
    
    class Config:
        env_file = "../.env"  # Look in parent directory (project root)
        env_file_encoding = 'utf-8'
        case_sensitive = True
        extra = 'ignore'  # Ignore extra fields in .env


settings = Settings()
