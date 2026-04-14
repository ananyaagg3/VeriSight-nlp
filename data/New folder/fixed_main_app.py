from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.api.endpoints import analysis, languages, health, docs_endpoints
from app.db.mongo import connect_to_mongo, close_mongo_connection
from app.utils.config import settings
from app.services.knowledge_graph import initialize_knowledge_verifier

# Setup logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info("="*60)
    logger.info("🚀 Starting FactWeave Misinformation Detection System")
    logger.info("="*60)
    
    # Connect to MongoDB in background (non-blocking)
    import asyncio
    asyncio.create_task(connect_to_mongo())
    logger.info("⏳ Connecting to MongoDB in background...")
    
    # Initialize knowledge graph verifier
    logger.info("🔧 Initializing knowledge graph verifier...")
    initialize_knowledge_verifier(
        google_api_key=settings.GOOGLE_FACT_CHECK_KEY,
        claimbuster_key=settings.CLAIMBUSTER_API_KEY
    )
    logger.info("✅ Knowledge graph verifier initialized")
    
    # Verify ML models are loaded
    from app.services.ml_pipeline import ml_pipeline
    if ml_pipeline.models_loaded:
        logger.info("✅ ML models loaded and ready!")
        logger.info(f"   - Text Model: {'LOADED' if ml_pipeline.text_model else 'FAILED'}")
        logger.info(f"   - Semantic Model: {'LOADED' if ml_pipeline.semantic_model else 'FAILED'}")
        logger.info(f"   - Image Model: {'LOADED' if ml_pipeline.image_model else 'FAILED'}")
    else:
        logger.error("❌ CRITICAL: ML models failed to load!")
        logger.error("   The system will NOT work properly!")
    
    logger.info("="*60)
    logger.info("✨ FactWeave System READY for requests!")
    logger.info("="*60)
    
    yield
    
    # Shutdown
    logger.info("🔄 Shutting down application...")
    await close_mongo_connection()
    logger.info("✅ Closed MongoDB connection")


# Create FastAPI app
app = FastAPI(
    title="FactWeave - Misinformation Detection API",
    description="Knowledge-enhanced multimodal misinformation detection with 15-language support",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.FRONTEND_URL.split(",") if settings.FRONTEND_URL else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(analysis.router, prefix="/api/analysis", tags=["Analysis"])
app.include_router(languages.router, prefix="/api/languages", tags=["Languages"])
app.include_router(docs_endpoints.router, prefix="/api/models", tags=["Models"])
app.include_router(health.router, tags=["Health"])


@app.get("/")
async def root():
    """Root endpoint with system info"""
    from app.services.ml_pipeline import ml_pipeline
    
    return {
        "name": "FactWeave AI",
        "version": "1.0.0",
        "status": "operational" if ml_pipeline.models_loaded else "loading",
        "models_loaded": ml_pipeline.models_loaded,
        "description": "Knowledge-Enhanced Multimodal Misinformation Detection",
        "features": [
            "Multilingual text analysis (15+ languages)",
            "Semantic classification with SentenceTransformers",
            "Image authenticity verification (CLIP Zero-Shot)",
            "Cross-modal consistency checking",
            "Knowledge graph verification (Google Fact Check + Wikidata)",
            "Explainable AI with evidence links"
        ],
        "models": {
            "text": "XLM-RoBERTa (FacebookAI/xlm-roberta-base)",
            "semantic": "paraphrase-multilingual-mpnet-base-v2",
            "image": "CLIP (openai/clip-vit-base-patch32)",
        },
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
