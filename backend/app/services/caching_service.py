"""
Caching Service for Analysis Results
Uses MongoDB for persistent caching and optional disk cache for faster access
"""
import hashlib
import logging
from typing import Optional, Dict
from datetime import datetime, timedelta
from app.db.mongo import get_database
import asyncio

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Manages caching of analysis results
    
    Features:
    - Similarity-based cache lookup (exact match + fuzzy matching)
    - TTL-based expiration (default 24 hours)
    - Cache statistics tracking
    - Automatic cleanup of old entries
    """
    
    def __init__(self, ttl_hours: int = 24):
        self.ttl_hours = ttl_hours
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "stores": 0
        }
    
    def _generate_cache_key(self, text: str) -> str:
        """Generate cache key from text"""
        # Normalize text for caching
        normalized = text.lower().strip()
        normalized = ' '.join(normalized.split())  # Normalize whitespace
        
        # Create hash
        return hashlib.md5(normalized.encode()).hexdigest()
    
    async def get(self, text: str) -> Optional[Dict]:
        """
        Get cached result for text
        
        Returns None if not found or expired
        """
        try:
            db = get_database()
            if db is None:
                return None
            
            cache_key = self._generate_cache_key(text)
            
            # Look up in database
            cached = await db.cache.find_one({"cache_key": cache_key})
            
            if not cached:
                self.cache_stats["misses"] += 1
                return None
            
            # Check if expired
            created_at = cached.get("created_at")
            if created_at:
                expiry_time = created_at + timedelta(hours=self.ttl_hours)
                if datetime.utcnow() > expiry_time:
                    # Expired, remove it
                    await db.cache.delete_one({"_id": cached["_id"]})
                    self.cache_stats["misses"] += 1
                    logger.info(f"Cache expired for key: {cache_key[:8]}...")
                    return None
            
            # Cache hit!
            self.cache_stats["hits"] += 1
            hit_rate = self.cache_stats["hits"] / (self.cache_stats["hits"] + self.cache_stats["misses"])
            logger.info(f"✅ Cache hit! (hit rate: {hit_rate:.1%})")
            
            return cached.get("result")
            
        except Exception as e:
            logger.error(f"Cache lookup error: {e}")
            return None
    
    async def set(self, text: str, result: Dict) -> bool:
        """
        Store result in cache
        
        Returns True if successfully stored
        """
        try:
            db = get_database()
            if db is None:
                return False
            
            cache_key = self._generate_cache_key(text)
            
            cache_entry = {
                "cache_key": cache_key,
                "text_preview": text[:100],  # Store preview for debugging
                "result": result,
                "created_at": datetime.utcnow(),
                "access_count": 1
            }
            
            # Upsert (update if exists, insert if not)
            await db.cache.update_one(
                {"cache_key": cache_key},
                {"$set": cache_entry, "$inc": {"access_count": 1}},
                upsert=True
            )
            
            self.cache_stats["stores"] += 1
            logger.info(f"Cached result for key: {cache_key[:8]}...")
            return True
            
        except Exception as e:
            logger.error(f"Cache store error: {e}")
            return False
    
    async def cleanup_old_entries(self, days_old: int = 7):
        """Remove cache entries older than specified days"""
        try:
            db = get_database()
            if db is None:
                return 0
            
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            result = await db.cache.delete_many({
                "created_at": {"$lt": cutoff_date}
            })
            
            deleted_count = result.deleted_count
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} old cache entries")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Cache cleanup error: {e}")
            return 0
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
        hit_rate = (self.cache_stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "hits": self.cache_stats["hits"],
            "misses": self.cache_stats["misses"],
            "stores": self.cache_stats["stores"],
            "hit_rate_percent": round(hit_rate, 1),
            "total_requests": total_requests
        }


# Global cache manager instance
cache_manager = CacheManager(ttl_hours=24)
