"""
Configuration settings for the Clinical Decision Support System
"""

# Fallback import for pydantic_settings to handle uvicorn subprocess issues
try:
    from pydantic_settings import BaseSettings
except ImportError:
    # Fallback for cases where pydantic_settings isn't available in subprocess
    try:
        from pydantic import BaseSettings  # Older pydantic versions
    except ImportError:
        # Final fallback - create a basic BaseSettings class
        from pydantic import BaseModel
        class BaseSettings(BaseModel):
            class Config:
                env_file = ".env"
                case_sensitive = False

from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    app_name: str = "Preliminary Disease Prediction and Clinical Decision Support"
    app_version: str = "1.0.0"
    debug: bool = False
    secret_key: str = "your-secret-key-change-in-production"
    
    # Database
    database_url: str = "sqlite:///./pdpcds_dev.db"  # Default to SQLite for development
    database_host: str = "localhost"
    database_port: int = 5432
    database_name: str = "pdpcds_db"
    database_user: str = "username"
    database_password: str = "password"
    
    # API
    api_v1_str: str = "/api/v1"
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # ML Model
    model_path: str = "./models/"
    model_version: str = "v1.0"
    confidence_threshold: float = 0.5
    max_predictions: int = 3
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    # Security
    jwt_secret_key: str = "your-jwt-secret-key"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # External APIs
    icd10_api_key: Optional[str] = None
    drug_database_api_key: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = False
        protected_namespaces = ()  # Resolves model_version field conflict
        env_file_encoding = 'utf-8'


# Global settings instance
settings = Settings()