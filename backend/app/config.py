"""
Application configuration settings.
Uses environment variables with sensible defaults for development.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "AutoList AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Security
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 24

    # TODO: Add MongoDB connection settings
    # MONGODB_URI: str = "mongodb://localhost:27017"
    # MONGODB_DB_NAME: str = "autolist_ai"
    MONGODB_URI: Optional[str] = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "autolist_ai"

    # TODO: Add Shopify API settings
    SHOPIFY_API_VERSION: str = "2024-01"

    # TODO: Add Claude/Anthropic API settings
    ANTHROPIC_API_KEY: Optional[str] = None

    # Encryption key for storing sensitive data (tokens)
    ENCRYPTION_KEY: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
