"""
Shared dependencies for FastAPI endpoints.
"""
from typing import Optional, Generator
from functools import lru_cache

from .config import Settings, settings
from .auth import get_current_user


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached application settings.
    Use as dependency: settings = Depends(get_settings)
    """
    return settings


# TODO: Add MongoDB database dependency
# Example implementation:
#
# from motor.motor_asyncio import AsyncIOMotorClient
# from pymongo.database import Database
#
# _mongo_client: Optional[AsyncIOMotorClient] = None
#
#
# async def get_database() -> Database:
#     """
#     Get MongoDB database connection.
#     Use as dependency: db = Depends(get_database)
#     """
#     global _mongo_client
#     if _mongo_client is None:
#         _mongo_client = AsyncIOMotorClient(settings.MONGODB_URI)
#     return _mongo_client[settings.MONGODB_DB_NAME]
#
#
# async def close_database():
#     """Close MongoDB connection on shutdown."""
#     global _mongo_client
#     if _mongo_client is not None:
#         _mongo_client.close()
#         _mongo_client = None


class MockDatabase:
    """
    Mock database for development.
    TODO: Replace with actual MongoDB collections.
    """

    def __init__(self):
        self.users: dict = {}
        self.shops: dict = {}
        self.products: dict = {}
        self.template_schemas: dict = {}
        self.mapping_jobs: dict = {}

    def get_collection(self, name: str) -> dict:
        return getattr(self, name, {})


# Global mock database instance
_mock_db = MockDatabase()


def get_mock_db() -> MockDatabase:
    """Get mock database for development."""
    return _mock_db


# Re-export auth dependency for convenience
__all__ = [
    "get_settings",
    "get_current_user",
    "get_mock_db",
]
