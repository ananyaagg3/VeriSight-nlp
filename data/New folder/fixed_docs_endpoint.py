from fastapi import APIRouter
from app.services.ml_pipeline import ml_pipeline  # Direct import

router = APIRouter()


@router.get("/info", response_model=dict)
async def get_model_info():
    """
    Get information about the loaded models
    """
    return {
        "models": {
            "text_analysis": {
                "name": "XLM-RoBERTa",
                "type": "Multilingual Transformer",
                "id": "FacebookAI/xlm-roberta-base",
                "status": "loaded" if ml_pipeline.text_model else "not loaded",
                "description": "Analyzes text in 100+ languages for misinformation patterns"
            },
            "semantic_analysis": {
                "name": "SentenceTransformer",
                "type": "Semantic Embeddings",
                "id": "paraphrase-multilingual-mpnet-base-v2",
                "status": "loaded" if ml_pipeline.semantic_model else "not loaded",
                "description": "Primary classification using semantic similarity"
            },
            "image_analysis": {
                "name": "CLIP",
                "type": "Vision Transformer",
                "id": "openai/clip-vit-base-patch32",
                "status": "loaded" if ml_pipeline.image_model else "not loaded",
                "description": "Analyzes images for content and authenticity"
            },
            "knowledge_graph": {
                "name": "Knowledge Graph Verifier",
                "components": ["Google Fact Check API", "Wikidata SPARQL", "spaCy NER"],
                "status": "active"
            }
        },
        "device": str(ml_pipeline.device),
        "all_loaded": ml_pipeline.models_loaded
    }
