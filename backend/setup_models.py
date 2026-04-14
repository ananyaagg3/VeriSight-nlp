"""
Model Download and Setup Script
Downloads and prepares all ML models for the misinformation detection system
"""
import os
import sys
import logging
from pathlib import Path
import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForSequenceClassification,
    CLIPProcessor, 
    CLIPModel,
    FlavaProcessor,
    FlavaForPreTraining
)
from tqdm import tqdm

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Model directories
MODELS_DIR = Path(__file__).parent / "ml-models" / "cache"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

def download_model(model_name, model_class, tokenizer_class=None, processor_class=None):
    """Download and cache a model"""
    logger.info(f"📥 Downloading {model_name}...")
    
    try:
        if processor_class:
            processor = processor_class.from_pretrained(
                model_name,
                cache_dir=MODELS_DIR
            )
            logger.info(f"✅ Processor downloaded: {model_name}")
        
        if tokenizer_class:
            tokenizer = tokenizer_class.from_pretrained(
                model_name,
                cache_dir=MODELS_DIR
            )
            logger.info(f"✅ Tokenizer downloaded: {model_name}")
        
        model = model_class.from_pretrained(
            model_name,
            cache_dir=MODELS_DIR
        )
        logger.info(f"✅ Model downloaded: {model_name}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Error downloading {model_name}: {e}")
        return False

def quantize_model(model):
    """Quantize model for faster inference"""
    try:
        quantized = torch.quantization.quantize_dynamic(
            model, {torch.nn.Linear}, dtype=torch.qint8
        )
        logger.info("✅ Model quantized successfully")
        return quantized
    except Exception as e:
        logger.warning(f"⚠️ Quantization failed: {e}")
        return model

def download_spacy_model():
    """Download spaCy multilingual model"""
    logger.info("📥 Downloading spaCy multilingual model...")
    try:
        import spacy
        from spacy.cli import download
        
        # Try to load, download if not available
        try:
            nlp = spacy.load("xx_ent_wiki_sm")
            logger.info("✅ spaCy model already installed")
        except:
            logger.info("Downloading spaCy model...")
            download("xx_ent_wiki_sm")
            nlp = spacy.load("xx_ent_wiki_sm")
            logger.info("✅ spaCy model downloaded and loaded")
        
        return True
    except Exception as e:
        logger.error(f"❌ Error downloading spaCy model: {e}")
        logger.info("You can manually install with: python -m spacy download xx_ent_wiki_sm")
        return False

def main():
    """Main setup function"""
    logger.info("=" * 60)
    logger.info("🚀 Starting Model Download and Setup")
    logger.info("=" * 60)
    
    success_count = 0
    total_models = 4
    
    # 1. Download XLM-RoBERTa (Text Classification)
    logger.info("\n[1/4] XLM-RoBERTa (Multilingual Text Model)")
    # Using FacebookAI/xlm-roberta-base which is the updated official identifier
    if download_model(
        "FacebookAI/xlm-roberta-base",
        AutoModelForSequenceClassification,
        tokenizer_class=AutoTokenizer
    ):
        success_count += 1
    else:
        # Fallback to microsoft/xlm-roberta-base if the above fails
        logger.info("Retrying with alternative identifier...")
        if download_model(
            "microsoft/xlm-roberta-base",
            AutoModelForSequenceClassification,
            tokenizer_class=AutoTokenizer
        ):
            success_count += 1
    
    # 2. Download CLIP (Image Analysis)
    logger.info("\n[2/4] CLIP (Image Understanding)")
    if download_model(
        "openai/clip-vit-base-patch32",
        CLIPModel,
        processor_class=CLIPProcessor
    ):
        success_count += 1
    
    # 3. Download FLAVA (Multimodal Fusion)
    logger.info("\n[3/4] FLAVA (Multimodal Fusion)")
    if download_model(
        "facebook/flava-full",
        FlavaForPreTraining,
        processor_class=FlavaProcessor
    ):
        success_count += 1
    
    # 4. Download spaCy multilingual
    logger.info("\n[4/4] spaCy (Named Entity Recognition)")
    if download_spacy_model():
        success_count += 1
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info(f"✨ Setup Complete: {success_count}/{total_models} models ready")
    logger.info("=" * 60)
    
    if success_count == total_models:
        logger.info("✅ All models downloaded successfully!")
        logger.info(f"📁 Models cached in: {MODELS_DIR.absolute()}")
        logger.info("\n🎯 Next steps:")
        logger.info("   1. Configure your .env file with API keys")
        logger.info("   2. Start the backend: python -m uvicorn app.main:app --reload")
        logger.info("   3. Start the frontend: cd frontend && npm run dev")
        return 0
    else:
        logger.warning(f"⚠️ {total_models - success_count} model(s) failed to download")
        logger.info("The system will attempt to download them on first use.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
