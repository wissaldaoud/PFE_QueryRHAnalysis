"""
Application configuration settings
"""
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import validator


class Settings(BaseSettings):
    # API Configuration
    PROJECT_NAME: str = "Query HR Analytics Online"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database Configuration
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "hranalytics"
    POSTGRES_PASSWORD: str = "hranalytics2026"
    POSTGRES_DB: str = "hr_analytics_db"
    POSTGRES_PORT: str = "5432"
    DATABASE_URL: str = ""
    
    @validator("DATABASE_URL", pre=True)
    def assemble_db_connection(cls, v, values):
        if isinstance(v, str) and v:
            return v
        return f"postgresql://{values.get('POSTGRES_USER')}:{values.get('POSTGRES_PASSWORD')}@{values.get('POSTGRES_SERVER')}:{values.get('POSTGRES_PORT')}/{values.get('POSTGRES_DB')}?client_encoding=utf8"
    
    # Security
    SECRET_KEY: str = "YOUR_SECRET_KEY_CHANGE_IN_PRODUCTION"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001", 
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:8000"
    ]
    
    # MLflow Configuration
    MLFLOW_TRACKING_URI: str = "http://localhost:5000"
    
    # Qlik Sense Configuration
    QLIK_SERVER: str = ""
    QLIK_APP_ID: str = ""
    
    # ============================================
    # SSO Configuration (OAuth2 / SAML)
    # ============================================
    
    # Microsoft Azure AD
    MICROSOFT_CLIENT_ID: str = ""
    MICROSOFT_CLIENT_SECRET: str = ""
    MICROSOFT_TENANT_ID: str = "common"
    
    # Google OAuth2
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    
    # SAML Configuration
    SAML_ENABLED: bool = False
    SAML_IDP_METADATA_URL: str = ""
    SAML_SP_ENTITY_ID: str = "hr-analytics-online"
    SAML_ACS_URL: str = "http://localhost:8000/api/v1/auth/saml/acs"
    
    # ============================================
    # Keycloak SSO Configuration (OIDC)
    # ============================================
    KEYCLOAK_SERVER_URL: str = "http://localhost:8080"
    KEYCLOAK_REALM: str = "hr-analytics"
    KEYCLOAK_CLIENT_ID: str = "hr-analytics-app"
    KEYCLOAK_CLIENT_SECRET: str = ""
    
    # ============================================
    # Email SMTP Configuration
    # ============================================
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = ""
    SMTP_FROM_NAME: str = "Query HR Analytics"
    EMAIL_SIMULATION_MODE: bool = True
    
    # ============================================
    # DWH Database Configuration (Qlik Analytics)
    # ============================================
    DWH_HOST: str = "localhost"
    DWH_PORT: str = "5432"
    DWH_DB: str = "hr_datawarehouse"
    DWH_USER: str = "hr_user"
    DWH_PASSWORD: str = "hr_password123"
    
    # ============================================
    # Ollama Local API Configuration
    # ============================================
    OLLAMA_API_URL: str = "http://localhost:11434/api/generate"
    OLLAMA_MODEL: str = "sqlcoder"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
