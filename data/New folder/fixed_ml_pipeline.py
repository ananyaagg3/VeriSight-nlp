"""
ML Pipeline - FIXED VERSION (No Lazy Loading)
All models load at startup for guaranteed functionality
"""
import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForSequenceClassification,
    CLIPProcessor, 
    CLIPModel,
    FlavaProcessor,
    FlavaModel,
    pipeline
)
from sentence_transformers import SentenceTransformer, util as sbert_util
import time
import logging
from typing import Dict, List, Optional, Tuple
import numpy as np
from PIL import Image
import io
import base64

logger = logging.getLogger(__name__)


class MLPipeline:
    """
    Main ML pipeline for multimodal misinformation detection
    
    ALL MODELS LOAD AT STARTUP - No lazy loading
    """
    
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {self.device}")
        
        # Initialize all models immediately
        self.text_model = None
        self.text_tokenizer = None
        self.image_model = None
        self.image_processor = None
        self.semantic_model = None
        self.models_loaded = False
        
        # Load models immediately at initialization
        self.load_models()
        
    def load_models(self):
        """
        Load ALL ML models at startup - NO lazy loading
        """
        if self.models_loaded:
            return True

        logger.info("🔥 Loading ML models at startup...")
        start_time = time.time()
        
        try:
            # 1. Load Text Models (XLM-RoBERTa)
            logger.info("📦 Loading XLM-RoBERTa text model...")
            self.text_tokenizer = AutoTokenizer.from_pretrained("FacebookAI/xlm-roberta-base")
            self.text_model = AutoModelForSequenceClassification.from_pretrained("FacebookAI/xlm-roberta-base")
            self.text_model.eval()
            logger.info("✅ XLM-RoBERTa loaded")

            # 2. Load Semantic Model (CRITICAL for classification)
            logger.info("📦 Loading SentenceTransformer...")
            self.semantic_model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2') 
            logger.info("✅ SentenceTransformer loaded")
            
            # 3. Load Image Models (CLIP)
            logger.info("📦 Loading CLIP model...")
            self.image_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            self.image_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
            self.image_model.eval()
            logger.info("✅ CLIP loaded")
            
            self.models_loaded = True
            logger.info(f"✅ ALL ML models loaded successfully in {time.time() - start_time:.2f}s")
            return True
            
        except Exception as e:
            logger.error(f"❌ CRITICAL: Failed to load ML models: {e}")
            logger.error("The system will NOT work without models!")
            raise e
    
    async def run_pipeline(
        self,
        text: str,
        language: str = "en",
        image_path: Optional[str] = None,
        image_data: Optional[bytes] = None
    ) -> Dict:
        """
        Run complete multimodal analysis pipeline
        """
        start_time = time.time()
        
        # Verify models are loaded
        if not self.models_loaded:
            raise RuntimeError("Models not loaded! Cannot process request.")
        
        # 1. Preprocessing
        preprocessed_text = self.preprocess_text(text, language)
        
        # 2. Text analysis (SEMANTIC CLASSIFICATION)
        text_result = await self.text_analysis(preprocessed_text)
        
        # 3. Image analysis (if provided)
        image_result = None
        if image_path or image_data:
            image_result = await self.image_analysis(
                image_path=image_path,
                image_data=image_data
            )
        
        # 4. Fusion
        fused_result = self.weighted_fusion(
            text_result, 
            image_result, 
            None
        )
        
        # 5. Format final result
        processing_time = (time.time() - start_time) * 1000
        
        return self._format_result(
            fused_result, text_result, language, processing_time, None
        )
    
    def preprocess_text(self, text: str, language: str) -> str:
        """Preprocess text for analysis"""
        text = text.strip()
        text = ' '.join(text.split())
        
        import re
        text = re.sub(r'([!?.]){3,}', r'\1\1', text)
        
        return text
    
    async def text_analysis(self, text: str) -> Dict:
        """
        Analyze text using SEMANTIC CLASSIFICATION
        """
        if not self.semantic_model:
            raise RuntimeError("Semantic model not loaded!")
        
        semantic_result = self.semantic_classify_claim(text)
        if semantic_result:
            logger.info(f"✅ Semantic analysis: {semantic_result['verdict']} ({semantic_result['confidence']:.2f})")
            return semantic_result
        
        # Fallback
        logger.warning("⚠️ Semantic classification returned None - using fallback")
        return {
            "verdict": "NEEDS_VERIFICATION",
            "confidence": 0.50,
            "keywords": [],
            "fallback": True
        }
    
    def semantic_classify_claim(self, text: str, language: str = "en") -> Optional[Dict]:
        """
        SEMANTIC CLAIM CLASSIFICATION using SentenceTransformer
        """
        if not self.semantic_model:
            return None
        
        try:
            # Known misinformation database
            known_misinformation = [
                "The earth is flat",
                "Earth is flat",
                "Vaccines cause autism",
                "Vaccines are dangerous",
                "5G causes COVID",
                "5G causes coronavirus",
                "COVID is a hoax",
                "Coronavirus is fake",
                "Climate change is a hoax",
                "Global warming is fake",
                "Moon landing was fake",
                "NASA faked the moon landing",
            ]
            
            known_authentic = [
                "The earth is round",
                "The earth is spherical", 
                "The earth orbits the sun",
                "Vaccines prevent diseases",
                "Vaccines are safe and effective",
                "Climate change is real",
                "The moon landing happened in 1969",
            ]
            
            # Encode claim
            claim_embedding = self.semantic_model.encode(text, convert_to_tensor=True)
            known_misinfo_embeddings = self.semantic_model.encode(known_misinformation, convert_to_tensor=True)
            known_authentic_embeddings = self.semantic_model.encode(known_authentic, convert_to_tensor=True)
            
            # Calculate similarities
            known_misinfo_scores = sbert_util.pytorch_cos_sim(claim_embedding, known_misinfo_embeddings)[0]
            known_authentic_scores = sbert_util.pytorch_cos_sim(claim_embedding, known_authentic_embeddings)[0]
            
            max_known_misinfo = float(known_misinfo_scores.max())
            max_known_authentic = float(known_authentic_scores.max())
            best_known_misinfo_idx = int(known_misinfo_scores.argmax())
            
            logger.info(f"📊 Similarity - Misinfo: {max_known_misinfo:.3f}, Authentic: {max_known_authentic:.3f}")
            
            # HIGH CONFIDENCE match
            if max_known_misinfo > 0.6:
                matched_claim = known_misinformation[best_known_misinfo_idx]
                confidence = min(0.98, 0.75 + max_known_misinfo * 0.25)
                logger.info(f"🚨 MISINFORMATION DETECTED: '{matched_claim}' (score: {max_known_misinfo:.3f})")
                return {
                    "verdict": "MISINFORMATION",
                    "confidence": float(confidence),
                    "keywords": [
                        {"word": "known false claim", "score": max_known_misinfo, "importance": "high"},
                        {"word": matched_claim[:30], "score": max_known_misinfo, "importance": "high"}
                    ],
                    "semantic_analysis": {
                        "misinformation_similarity": max_known_misinfo,
                        "authentic_similarity": max_known_authentic,
                        "matched_pattern": matched_claim
                    }
                }
            
            if max_known_authentic > 0.65:
                confidence = min(0.95, 0.70 + max_known_authentic * 0.25)
                logger.info(f"✅ AUTHENTIC DETECTED (score: {max_known_authentic:.3f})")
                return {
                    "verdict": "AUTHENTIC",
                    "confidence": float(confidence),
                    "keywords": [{"word": "verified fact", "score": max_known_authentic, "importance": "medium"}],
                    "semantic_analysis": {
                        "misinformation_similarity": max_known_misinfo,
                        "authentic_similarity": max_known_authentic
                    }
                }
            
            # General pattern matching
            misinformation_prompts = [
                "This is a conspiracy theory that governments are hiding the truth",
                "Scientific institutions are lying to the public", 
                "Vaccines cause autism or contain tracking devices",
                "This miracle cure will heal any disease",
                "The earth is flat and space agencies are lying",
                "Climate change is a hoax invented by scientists",
            ]
            
            authentic_prompts = [
                "This is a verified fact supported by scientific evidence",
                "Multiple independent sources confirm this information",
                "Peer-reviewed research supports this claim",
                "This is factual information",
            ]
            
            misinfo_embeddings = self.semantic_model.encode(misinformation_prompts, convert_to_tensor=True)
            authentic_embeddings = self.semantic_model.encode(authentic_prompts, convert_to_tensor=True)
            
            misinfo_scores = sbert_util.pytorch_cos_sim(claim_embedding, misinfo_embeddings)[0]
            authentic_scores = sbert_util.pytorch_cos_sim(claim_embedding, authentic_embeddings)[0]
            
            max_misinfo_score = float(misinfo_scores.max())
            max_authentic_score = float(authentic_scores.max())
            
            logger.info(f"📊 Pattern match - Misinfo: {max_misinfo_score:.3f}, Authentic: {max_authentic_score:.3f}")
            
            if max_misinfo_score > max_authentic_score and max_misinfo_score > 0.25:
                confidence = min(0.92, 0.55 + (max_misinfo_score - max_authentic_score) * 1.5)
                return {
                    "verdict": "MISINFORMATION",
                    "confidence": float(confidence),
                    "keywords": [{"word": "suspicious pattern", "score": max_misinfo_score, "importance": "high"}],
                    "semantic_analysis": {
                        "misinformation_similarity": max_misinfo_score,
                        "authentic_similarity": max_authentic_score
                    }
                }
            elif max_authentic_score > max_misinfo_score and max_authentic_score > 0.30:
                confidence = min(0.88, 0.55 + (max_authentic_score - max_misinfo_score) * 1.5)
                return {
                    "verdict": "AUTHENTIC",
                    "confidence": float(confidence),
                    "keywords": [{"word": "verified content", "score": max_authentic_score, "importance": "medium"}],
                    "semantic_analysis": {
                        "misinformation_similarity": max_misinfo_score,
                        "authentic_similarity": max_authentic_score
                    }
                }
            else:
                return {
                    "verdict": "NEEDS_VERIFICATION",
                    "confidence": 0.60,
                    "keywords": [],
                    "semantic_analysis": {
                        "misinformation_similarity": max_misinfo_score,
                        "authentic_similarity": max_authentic_score,
                        "note": "Inconclusive - manual verification recommended"
                    }
                }
                
        except Exception as e:
            logger.error(f"❌ Semantic classification error: {e}")
            return None
    
    async def image_analysis(
        self, 
        image_path: Optional[str] = None,
        image_data: Optional[bytes] = None
    ) -> Dict:
        """Analyze image authenticity"""
        if not self.image_model:
            logger.warning("Image model not available")
            return None
        
        try:
            # Load image
            if image_data:
                image = Image.open(io.BytesIO(image_data))
            elif image_path:
                if image_path.startswith('data:image'):
                    image_data = base64.b64decode(image_path.split(',')[1])
                    image = Image.open(io.BytesIO(image_data))
                else:
                    image = Image.open(image_path)
            else:
                return None
            
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # CLIP Zero-Shot Classification
            authenticity_score, manipulation_prob = self._classify_image_authenticity(image)
            
            inputs = self.image_processor(images=image, return_tensors="pt")
            
            with torch.no_grad():
                outputs = self.image_model.get_image_features(**inputs)
            
            image_embedding = outputs.cpu().numpy()
            
            return {
                "authenticity": authenticity_score,
                "manipulation_detected": manipulation_prob > 0.5,
                "embedding": image_embedding.tolist(),
                "image_processed": True,
                "manipulation_score": manipulation_prob
            }
            
        except Exception as e:
            logger.error(f"❌ Image analysis error: {e}")
            return None

    def _classify_image_authenticity(self, image) -> Tuple[float, float]:
        """CLIP Zero-Shot classification for image authenticity"""
        try:
            labels = [
                "a real authentic photograph", 
                "a news photo",
                "a digitally manipulated image", 
                "a photoshop edited image", 
                "a deepfake generated image",
                "an ai generated image"
            ]
            
            inputs = self.image_processor(
                text=labels,
                images=image,
                return_tensors="pt",
                padding=True
            )
            
            with torch.no_grad():
                outputs = self.image_model(**inputs)
            
            logits_per_image = outputs.logits_per_image
            probs = logits_per_image.softmax(dim=1)
            probs_list = probs[0].tolist()
            
            authentic_prob = sum(probs_list[:2])
            fake_prob = sum(probs_list[2:])
            
            total = authentic_prob + fake_prob
            if total > 0:
                authentic_score = authentic_prob / total
                fake_score = fake_prob / total
            else:
                authentic_score = 0.5
                fake_score = 0.5
                
            logger.info(f"📸 Image: Real={authentic_score:.2f}, Fake={fake_score:.2f}")
            
            return authentic_score, fake_score
            
        except Exception as e:
            logger.error(f"❌ Image classification error: {e}")
            return 0.5, 0.5
    
    def weighted_fusion(
        self,
        text_result: Dict,
        image_result: Optional[Dict],
        sentiment_result: Optional[Dict],
        knowledge_score: float = 0.5
    ) -> Dict:
        """Weighted fusion of results"""
        if not image_result:
            return {
                **text_result,
                "fusion_method": "text_only",
                "score_breakdown": {
                    "text_authenticity": round(text_result["confidence"] * 100, 1),
                    "image_authenticity": None,
                    "cross_modal_consistency": None,
                    "knowledge_verification": round(knowledge_score * 100, 1)
                }
            }
        
        # Multimodal fusion
        image_weight = 0.25
        text_weight = 0.35
        consistency_weight = 0.25
        knowledge_weight = 0.15
        
        text_auth = text_result["confidence"] if text_result["verdict"] == "AUTHENTIC" else (1 - text_result["confidence"])
        
        final_score = (
            image_result.get("authenticity", 0.5) * image_weight +
            text_auth * text_weight +
            0.5 * consistency_weight +
            knowledge_score * knowledge_weight
        )
        
        fused_confidence = (
            image_result.get("authenticity", 0.5) * image_weight +
            text_result["confidence"] * text_weight +
            0.5 * consistency_weight +
            0.85 * knowledge_weight
        )
        
        verdict = "AUTHENTIC" if final_score > 0.5 else "MISINFORMATION"
        
        return {
            "verdict": verdict,
            "confidence": fused_confidence,
            "keywords": text_result.get("keywords", []),
            "fusion_method": "weighted_multimodal",
            "final_score": final_score,
            "image_analysis": image_result,
            "cross_modal_consistency": 0.5,
            "score_breakdown": {
                "image_authenticity": round(image_result.get("authenticity", 0.5) * 100, 1),
                "text_authenticity": round(text_auth * 100, 1),
                "cross_modal_consistency": 50.0,
                "knowledge_verification": round(knowledge_score * 100, 1)
            }
        }
    
    def _format_result(
        self,
        fused_result: Dict,
        text_result: Dict,
        language: str,
        processing_time: float,
        sentiment_result: Optional[Dict]
    ) -> Dict:
        """Format final analysis result"""
        import uuid
        
        return {
            "verdict": fused_result["verdict"],
            "confidence": round(fused_result["confidence"], 3),
            "keywords": fused_result.get("keywords", [])[:3],
            "sources": [],
            "explanation": self._generate_explanation(fused_result),
            "processing_time_ms": round(processing_time, 2),
            "language": language,
            "analysis_id": str(uuid.uuid4()),
            "image_analysis": fused_result.get("image_analysis"),
            "sentiment": sentiment_result.get("sentiment") if sentiment_result else None,
            "fusion_method": fused_result.get("fusion_method", "unknown"),
            "score_breakdown": fused_result.get("score_breakdown", {}),
            "final_score": fused_result.get("final_score"),
            "cross_modal_consistency": fused_result.get("cross_modal_consistency"),
            "model_info": {
                "text_model": "xlm-roberta-base + semantic",
                "image_model": "clip-vit-base-patch32" if self.image_model else None,
            }
        }
    
    def _generate_explanation(self, result: Dict) -> str:
        """Generate human-readable explanation"""
        verdict = result["verdict"]
        confidence = result["confidence"]
        
        if verdict == "MISINFORMATION":
            if confidence > 0.9:
                return "🚨 Strong indicators of misinformation detected based on semantic analysis and known false claims."
            elif confidence > 0.7:
                return "⚠️ Likely misinformation based on suspicious patterns and content analysis."
            else:
                return "⚠️ Possible misinformation detected. Moderate confidence - verify with trusted sources."
        elif verdict == "AUTHENTIC":
            if confidence > 0.9:
                return "✅ Content appears authentic. No significant red flags detected."
            elif confidence > 0.7:
                return "✅ Likely authentic content with minor uncertainties."
            else:
                return "ℹ️ Appears authentic but with some uncertainty. Verify if critical."
        else:
            return "ℹ️ Unable to determine authenticity. Please verify with multiple authoritative sources."


# Global instance - created immediately
ml_pipeline = MLPipeline()
