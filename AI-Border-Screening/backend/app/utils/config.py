from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    APP_NAME: str = "AI-Based Document Screening and Tamper Detection System"
    DEBUG: bool = True
    
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/border_screening"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    
    UPLOAD_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "storage", "documents")
    HEATMAP_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "storage", "heatmaps")
    NOISE_RESIDUAL_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "storage", "noise_residuals")
    FACE_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "storage", "faces")
    
    MAX_FILE_SIZE: int = 10 * 1024 * 1024
    ALLOWED_EXTENSIONS: set = {".jpg", ".jpeg", ".png", ".pdf", ".tiff", ".bmp"}
    
    OCR_LANG: str = "en"
    FACE_SIMILARITY_THRESHOLD: float = 0.75
    TAMPER_THRESHOLD: float = 0.70
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()