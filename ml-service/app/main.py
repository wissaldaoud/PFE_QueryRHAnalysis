"""
ML Microservice - FastAPI Application
Fournit des endpoints pour les prédictions ML (CV Matching, Turnover)
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.routes import cv_matching
from app.routes import cv_ranking

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Création de l'application FastAPI
app = FastAPI(
    title="ML Microservice",
    description="Service de prédictions ML pour HR Analytics",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enregistrement des routes
app.include_router(cv_matching.router, prefix="/api/v1/ml", tags=["CV Matching"])
app.include_router(cv_ranking.router, prefix="/api/v1/ml", tags=["CV Ranking"]) 

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "ML Microservice",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "cv_matching": "/api/v1/ml/cv-matching",
              "cv_ranking": "/api/v1/ml/cv-ranking", 
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "ml-microservice"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
