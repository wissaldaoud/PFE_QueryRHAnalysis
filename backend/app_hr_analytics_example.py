"""
Exemple d'intégration des routes HR Analytics dans l'application FastAPI
À ajouter dans app/main.py ou créer un nouveau fichier pour tester
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Import des routes HR Analytics
from app.api.v1.endpoints.hr_analytics import router as hr_analytics_router
from app.api.v1.endpoints.hr_analytics import initialize_hr_analytics_service

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Création de l'application FastAPI
app = FastAPI(
    title="HR Analytics API",
    description="API avancée pour CV Matching, Recommandation de Formation et Scoring RH Prédictif",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À configurer selon vos besoins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """
    Événement de démarrage : initialisation des services
    """
    logger.info("🚀 Démarrage de l'application HR Analytics API")
    
    try:
        # Initialiser le service HR Analytics
        logger.info("📦 Initialisation du service HR Analytics...")
        initialize_hr_analytics_service()
        logger.info("✅ Service HR Analytics initialisé avec succès")
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'initialisation: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """
    Événement d'arrêt : nettoyage des ressources
    """
    logger.info("👋 Arrêt de l'application HR Analytics API")


@app.get("/")
async def root():
    """
    Route racine avec informations de l'API
    """
    return {
        "message": "Welcome to HR Analytics API",
        "version": "1.0.0",
        "features": [
            "CV Matching with NLP",
            "Training Recommendation",
            "Predictive HR Scoring"
        ],
        "documentation": "/docs",
        "health_check": "/api/v1/hr-analytics/health"
    }


@app.get("/health")
async def health():
    """
    Health check global
    """
    return {
        "status": "healthy",
        "service": "HR Analytics API"
    }


# Inclusion des routes HR Analytics
app.include_router(
    hr_analytics_router,
    prefix="/api/v1/hr-analytics",
    tags=["HR Analytics"]
)

# Vous pouvez ajouter d'autres routes ici
# app.include_router(other_router, prefix="/api/v1/other")


if __name__ == "__main__":
    import uvicorn
    
    # Démarrage du serveur
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,  # Mode développement
        log_level="info"
    )
