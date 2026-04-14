from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from datetime import datetime
import hashlib
import logging

from app.models.request import AnalysisRequest, FeedbackRequest
from app.models.response import AnalysisResponse, ErrorResponse
from app.services.ml_pipeline import ml_pipeline
from app.services import knowledge_graph
from app.db.mongo import get_database
from app.utils.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/analyze-text", response_model=AnalysisResponse)
async def analyze_text(request: AnalysisRequest):
    """
    Analyze text for misinformation
    
    Args:
        request: Analysis request with text (English-only)
        
    Returns:
        Analysis results with verdict, confidence, and evidence
    """
    try:
        # Check cache first (only if database is available)
        text_hash = hashlib.md5(request.text.encode()).hexdigest()
        db = get_database()
        
        if db is not None:
            cached = await db.analyses.find_one({"text_hash": text_hash})
            if cached:
                logger.info(f"Cache hit for text_hash: {text_hash}")
                cached_result = dict(cached["result"])
                # Safeguard: if any detailed claim is MISINFORMATION, overall verdict must be MISINFORMATION
                detailed_claims = cached_result.get("detailed_claims") or []
                if detailed_claims and any(c.get("verdict") == "MISINFORMATION" for c in detailed_claims):
                    cached_result["verdict"] = "MISINFORMATION"
                    misinfo = [c for c in detailed_claims if c.get("verdict") == "MISINFORMATION"]
                    cached_result["confidence"] = max(c.get("confidence", 0.5) for c in misinfo)
                return AnalysisResponse(**cached_result)
        
        # Process image if provided (decode base64)
        image_data = None
        if request.analyze_image and request.image_url:
            try:
                import base64
                # Handle data:image/... prefix
                if request.image_url.startswith('data:image'):
                    # Format: data:image/png;base64,ACTUALDATA
                    base64_data = request.image_url.split(',')[1]
                else:
                    base64_data = request.image_url
                    
                image_data = base64.b64decode(base64_data)
                logger.info(f"Decoded image: {len(image_data)} bytes")
            except Exception as e:
                logger.error(f"Failed to decode image: {e}")
                image_data = None
        
        # Run ML pipeline with image_data (bytes) instead of image_path
        result = await ml_pipeline.run_pipeline(
            text=request.text,
            language="en",
            image_data=image_data
        )
        
        # ------------------------------------------------------------------
        # API-FIRST STRATEGY: Knowledge Graph is the PRIMARY source of truth
        # ------------------------------------------------------------------
        # Access the verified instance dynamically
        verifier = knowledge_graph.knowledge_verifier
        
        if verifier:
            # ------------------------------------------------------------------
            # DETAILED EXPLAINABILITY: Analyze each claim separately
            # ------------------------------------------------------------------
            from app.services.explainability import analyze_claims_with_evidence
            
            detailed_analysis = await analyze_claims_with_evidence(
                text=request.text,
                knowledge_verifier=verifier,
                language="en"
            )
            
            # Use detailed analysis results
            if detailed_analysis["overall_verdict"] == "AUTHENTIC":
                result["verdict"] = "AUTHENTIC"
                result["confidence"] = detailed_analysis["overall_confidence"]
            elif detailed_analysis["overall_verdict"] == "MIXED":
                result["verdict"] = "MISINFORMATION"  # Conservative: flag mixed content
                result["confidence"] = detailed_analysis["overall_confidence"]
            elif detailed_analysis["overall_verdict"] == "NEEDS_VERIFICATION":
                result["verdict"] = "NEEDS_VERIFICATION"
                result["confidence"] = detailed_analysis["overall_confidence"]
            else:
                # Backward-compatible fallback: treat unknown verdicts as needs verification
                result["verdict"] = "NEEDS_VERIFICATION"
                result["confidence"] = detailed_analysis.get("overall_confidence", 0.5)

            # Safeguard: if any detailed claim is MISINFORMATION, overall must show MISINFORMATION
            detailed_claims = detailed_analysis.get("detailed_analysis") or []
            if detailed_claims and any(c.get("verdict") == "MISINFORMATION" for c in detailed_claims):
                result["verdict"] = "MISINFORMATION"
                misinfo_claims = [c for c in detailed_claims if c.get("verdict") == "MISINFORMATION"]
                result["confidence"] = max(c.get("confidence", 0.5) for c in misinfo_claims)
            
            # Add detailed explanation
            result["explanation"] = detailed_analysis["summary"]
            result["detailed_claims"] = detailed_analysis["detailed_analysis"]
            
            # Aggregate sources from all claims
            all_sources = []
            for claim_result in detailed_analysis["detailed_analysis"]:
                all_sources.extend(claim_result.get("sources", []))
            
            # Remove duplicates and limit to top 5
            seen_urls = set()
            unique_sources = []
            for source in all_sources:
                url = source.get("url", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    unique_sources.append(source)
                    if len(unique_sources) >= 5:
                        break
            
            result["sources"] = unique_sources

        # Related articles from News API (optional)
        try:
            from app.services.news_api import fetch_related_articles
            result["related_articles"] = await fetch_related_articles(
                claim_text=request.text,
                page_size=5,
            )
        except Exception as e:
            logger.debug("Related articles fetch skipped: %s", e)
            result["related_articles"] = []
        
        # Store in database (only if available)
        if db is not None:
            await db.analyses.insert_one({
                "text": request.text,
                "text_hash": text_hash,
                "language": "en",
                "result": result,
                "timestamp": datetime.utcnow(),
                "feedback": None
            })
        
        return AnalysisResponse(**result)
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-image", response_model=AnalysisResponse)
async def analyze_image(
    file: UploadFile = File(...),
    text: str = Form(None)
):
    """
    Analyze uploaded image (and optional text) for misinformation
    """
    try:
        # Read image file
        contents = await file.read()
        
        # Calculate hash for caching
        import hashlib
        image_hash = hashlib.md5(contents).hexdigest()
        
        db = get_database()
        
        # Check cache
        if db is not None:
            cached = await db.analyses.find_one({"image_hash": image_hash, "text": text or ""})
            if cached:
                logger.info(f"Cache hit for image_hash: {image_hash}")
                return AnalysisResponse(**cached["result"])

        # Run pipeline
        # If text is provided, run full multimodal
        # If no text, run image-only analysis
        target_text = text or "Image analysis only"
        
        result = await ml_pipeline.run_pipeline(
            text=target_text,
            language="en",
            image_data=contents
        )
        
        # Store in db
        if db is not None:
            await db.analyses.insert_one({
                "text": target_text,
                "image_hash": image_hash,
                "language": "en",
                "result": result,
                "max_sim_matches": [], # Placeholder for consistent schema
                "timestamp": datetime.utcnow()
            })
            
        return AnalysisResponse(**result)

    except Exception as e:
        logger.error(f"Image analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feedback")
async def submit_feedback(request: FeedbackRequest):
    """Submit user feedback for an analysis"""
    try:
        db = get_database()
        
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")
        
        # Store feedback
        await db.feedback.insert_one({
            "analysis_id": request.analysis_id,
            "rating": request.rating,
            "comment": request.comment,
            "is_correct": request.is_correct,
            "timestamp": datetime.utcnow()
        })
        
        return {"message": "Feedback submitted successfully"}
        
    except Exception as e:
        logger.error(f"Feedback submission failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_history(limit: int = 10):
    """Get analysis history"""
    try:
        db = get_database()
        
        if db is None:
            return {"history": [], "database_available": False}
        
        cursor = db.analyses.find().sort("timestamp", -1).limit(limit)
        history = await cursor.to_list(length=limit)
        
        formatted = []
        for item in history:
            result = item.get("result") or {}
            text = item.get("text") or ""
            ts = item.get("timestamp")
            aid = result.get("analysis_id")
            if (not aid and not text) or ts is None:
                continue
            formatted.append({
                "analysis_id": aid or "",
                "text": text[:100] + "..." if len(text) > 100 else text,
                "verdict": result.get("verdict", "NEEDS_VERIFICATION"),
                "confidence": result.get("confidence", 0.5),
                "timestamp": ts
            })
        
        return {"history": formatted, "database_available": True}
        
    except Exception as e:
        logger.error(f"Failed to get history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/clear-history")
async def clear_history():
    """Clear all analysis history"""
    try:
        db = get_database()
        
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")
        
        # Delete all documents from analyses collection
        result = await db.analyses.delete_many({})
        
        logger.info(f"Cleared {result.deleted_count} analysis records from history")
        
        return {
            "success": True,
            "deleted_count": result.deleted_count,
            "message": f"Successfully cleared {result.deleted_count} analysis records"
        }
        
    except Exception as e:
        logger.error(f"Failed to clear history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
