"""
Client HTTP pour communiquer avec le ML Microservice
"""
import httpx
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)

class MLServiceClient:
    """Client pour le ML Microservice"""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url.rstrip("/")
        self.timeout = 30.0
        
    async def get_categories(self) -> Dict[str, Any]:
        """Récupérer les catégories ML"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}/api/v1/ml/cv-matching/categories")
            response.raise_for_status()
            return response.json()
    
    async def predict_category(self, cv_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prédire la catégorie d'un CV"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/api/v1/ml/cv-matching/predict-category",
                json=cv_data
            )
            response.raise_for_status()
            return response.json()
    
    async def match_cv(self, cv_data: Dict[str, Any], job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Matcher un CV avec une offre"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            # Préparer le payload avec cv et job
            payload = {
                "cv": cv_data,
                "job": job_data
            }
            response = await client.post(
                f"{self.base_url}/api/v1/ml/cv-matching/match",
                json=payload
            )
            response.raise_for_status()
            return response.json()
    
    async def parse_cv(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Parser un CV via le ML service"""
        async with httpx.AsyncClient(timeout=60.0) as client:
            files = {"file": (filename, file_content)}
            response = await client.post(
                f"{self.base_url}/api/v1/ml/cv-matching/parse-cv",
                files=files
            )
            response.raise_for_status()
            return response.json()
    
    async def health_check(self) -> bool:
        """Vérifier si le ML service est disponible"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/health")
                return response.status_code == 200
        except Exception as e:
            logger.error(f"ML Service unreachable: {e}")
            return False

# Singleton
_ml_client: Optional[MLServiceClient] = None

def get_ml_client(base_url: str = "http://localhost:8001") -> MLServiceClient:
    """Obtenir le client ML (singleton)"""
    global _ml_client
    if _ml_client is None:
        _ml_client = MLServiceClient(base_url)
    return _ml_client
