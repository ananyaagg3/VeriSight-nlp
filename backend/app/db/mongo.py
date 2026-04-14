"""
MongoDB module - with lazy loading to speed up startup
Database is completely optional - system works without it
"""
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Database instance - lazy loaded 
_db = None
_db_initialized = False


async def connect_to_mongo():
    """Connect to MongoDB (optional - system works without it)"""
    global _db, _db_initialized
    _db_initialized = True
    
    try:
        # Lazy import motor (in thread to avoid blocking loop on Windows)
        import asyncio
        from app.utils.config import settings
        
        def _import_motor():
            from motor.motor_asyncio import AsyncIOMotorClient
            return AsyncIOMotorClient
            
        loop = asyncio.get_running_loop()
        AsyncIOMotorClient = await loop.run_in_executor(None, _import_motor)
        
        client = AsyncIOMotorClient(
            settings.MONGODB_URI,
            serverSelectionTimeoutMS=5000  # 5 second timeout
        )
        _db = client[settings.MONGODB_DB_NAME]
        
        # Test connection
        await client.admin.command('ping')
        logger.info(f"✅ Connected to MongoDB database: {settings.MONGODB_DB_NAME}")
        
        # Create indexes
        await create_indexes()
        
    except Exception as e:
        logger.warning(f"⚠️ Could not connect to MongoDB: {e}")
        logger.info("Running without database - results will not be persisted")
        _db = None


async def close_mongo_connection():
    """Close MongoDB connection"""
    global _db
    if _db is not None:
        try:
            _db.client.close()
            logger.info("Closed MongoDB connection")
        except:
            pass
    _db = None


async def create_indexes():
    """Create database indexes for performance"""
    global _db
    if _db is None:
        return
        
    try:
        await _db.analyses.create_index([("timestamp", -1)])
        await _db.analyses.create_index([("language", 1), ("verdict", 1)])
        await _db.analyses.create_index([("text_hash", 1)], unique=True, sparse=True)
        await _db.sessions.create_index([("user_id", 1)])
        await _db.sessions.create_index([("created_at", -1)])
        await _db.feedback.create_index([("analysis_id", 1)])
        logger.info("Created database indexes")
    except Exception as e:
        logger.warning(f"Error creating indexes: {e}")


def get_database():
    """Get database instance (may be None if not connected)"""
    global _db
    return _db
