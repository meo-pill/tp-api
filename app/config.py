"""
Configuration de l'application avec gestion des variables d'environnement
"""
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Configuration de l'application"""
    
    # Chemins
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    MODEL_PATH: Path = BASE_DIR / "models" / "credit_scoring_model.pkl"
    
    # Database
    DATABASE_URL: str = "postgresql://credit_user:credit_password@db:5432/credit_scoring_db"
    
    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # API
    API_TITLE: str = "Credit Scoring API"
    API_VERSION: str = "2.0.0"
    API_ENV: str = "development"
    DEBUG: bool = True
    
    # Model
    MODEL_CONFIG: dict = {
        "name": "Credit Scoring AutoML",
        "algorithm": "AutoML (FLAML)",
        "version": "1.0",
        "features": ["age", "income", "credit_amount", "duration"],
        "threshold": 0.5,
    }
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Instance globale
settings = Settings()
