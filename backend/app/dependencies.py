"""
Shared dependencies for FastAPI endpoints.

Provides database connections and authentication dependencies.
"""
from typing import Optional
from functools import lru_cache

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from .config import Settings, settings
from .auth import get_current_user


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached application settings.
    Use as dependency: settings = Depends(get_settings)
    """
    return settings


# MongoDB connection state
_mongo_client: Optional[AsyncIOMotorClient] = None
_database: Optional[AsyncIOMotorDatabase] = None


async def connect_database() -> AsyncIOMotorDatabase:
    """
    Initialize MongoDB connection.
    Called during application startup.
    """
    global _mongo_client, _database
    
    if _mongo_client is None:
        print(f"Connecting to MongoDB: {settings.MONGODB_DB_NAME}")
        _mongo_client = AsyncIOMotorClient(settings.MONGODB_URI)
        _database = _mongo_client[settings.MONGODB_DB_NAME]
        
        # Verify connection by pinging the database
        try:
            await _mongo_client.admin.command('ping')
            print("✅ MongoDB connection successful")
        except Exception as e:
            print(f"❌ MongoDB connection failed: {e}")
            raise
    
    return _database


async def close_database():
    """
    Close MongoDB connection.
    Called during application shutdown.
    """
    global _mongo_client, _database
    
    if _mongo_client is not None:
        print("Closing MongoDB connection...")
        _mongo_client.close()
        _mongo_client = None
        _database = None
        print("MongoDB connection closed")


def get_database() -> AsyncIOMotorDatabase:
    """
    Get MongoDB database instance for dependency injection.
    
    Usage:
        @router.get("/items")
        async def get_items(db: AsyncIOMotorDatabase = Depends(get_database)):
            items = await db.items.find().to_list(100)
            return items
    """
    if _database is None:
        raise RuntimeError("Database not initialized. Call connect_database() first.")
    return _database


# Re-export auth dependency for convenience
__all__ = [
    "get_settings",
    "get_current_user",
    "connect_database",
    "close_database",
    "get_database",
]
