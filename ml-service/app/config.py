"""Configuration du microservice ML"""
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    """Settings for ML Microservice"""
    
    # Service
    SERVICE_NAME: str = "ML Microservice"
    SERVICE_VERSION: str = "1.0.0"
    SERVICE_PORT: int = 8001
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent
    MODELS_DIR: Path = BASE_DIR / "app" / "models"
    
    # ML Models
    CV_MODEL_PATH: Path = MODELS_DIR / "cv_matching_model.pkl"
    CV_TFIDF_PATH: Path = MODELS_DIR / "cv_tfidf.pkl"
    CV_ENCODER_PATH: Path = MODELS_DIR / "cv_label_encoder.pkl"
    TURNOVER_MODEL_PATH: Path = MODELS_DIR / "turnover_model.pkl"
    TURNOVER_FEATURES_PATH: Path = MODELS_DIR / "turnover_features.pkl"
    
    # OCR Configuration
    TESSERACT_CMD: str = r'C:\Users\wdaoud\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
    POPPLER_PATH: str = r'C:\Users\wdaoud\AppData\Local\Programs\poppler\Library\bin'
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
