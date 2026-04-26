"""
Query Engine API Router - FastAPI endpoints pour le moteur de requêtes RH
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from app.db.base import get_db
from app.services.query_engine_service_new import QueryEngineService
from app.api.deps import get_current_active_user
from app.models.user import User

router = APIRouter()


class QueryRequest(BaseModel):
    """Requête pour le moteur de requêtes"""
    question: str = Field(..., description="Question en français", example="Combien d'employés actifs?")


class QueryResponse(BaseModel):
    """Réponse du moteur de requêtes"""
    success: bool
    answer: str
    query_type: str
    sql_query: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    visualization: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class HistoryResponse(BaseModel):
    """Historique des requêtes"""
    history: List[Dict[str, Any]]


@router.post("/execute", response_model=QueryResponse, summary="Exécuter une requête en langage naturel")
async def execute_query(
    request: QueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Exécuter une requête RH en langage naturel
    
    Le moteur de requêtes utilise Claude API pour:
    1. Transformer la question en français en requête SQL
    2. Exécuter la requête sur la base de données datawarehouse (DWH_DB)
    3. Formatter la réponse en français avec suggestions de visualisation
    
    **Exemples de questions:**
    - "Combien d'employés actifs?"
    - "Liste des employés du département IT"
    - "Salaire moyen par département"
    - "Quel est le taux de turnover?"
    - "Statistiques des congés par type"
    - "Top 10 des salaires les plus élevés"
    
    **Base de données:**
    - Les requêtes sont exécutées sur `hr_datawarehouse` (DWH_DB)
    - Seules les requêtes SELECT sont autorisées
    - La base APP principale (users/auth) n'est jamais interrogée
    
    **Sécurité:**
    - Validation user authentifié
    - Blocage des requêtes non-SELECT
    - Pas d'exposition des credentials
    """
    try:
        # Validation user
        if not current_user:
            raise HTTPException(status_code=401, detail="Utilisateur non authentifié")
        
        # Créer service avec connexion DWH séparée
        query_service = QueryEngineService(db)
        
        # Traiter la requête
        result = await query_service.process_query(
            question=request.question,
            user_id=current_user.id
        )
        
        return QueryResponse(**result)
        
    except Exception as e:
        return QueryResponse(
            success=False,
            answer=f"Une erreur s'est produite: {str(e)}",
            query_type="error",
            error=str(e)
        )


@router.get("/history", response_model=HistoryResponse, summary="Historique des requêtes")
async def get_query_history(
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Récupérer l'historique des requêtes de l'utilisateur
    
    **Paramètres:**
    - `limit`: Nombre maximum de requêtes à retourner (défaut: 20)
    
    **Retourne:**
    - Liste des requêtes exécutées avec timestamp, question, succès, aperçu résultat
    """
    try:
        # Validation user
        if not current_user:
            raise HTTPException(status_code=401, detail="Utilisateur non authentifié")
        
        query_service = QueryEngineService(db)
        history = query_service.get_history(current_user.id, limit)
        
        return HistoryResponse(history=history)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")


@router.get("/health", summary="Vérifier la santé du service")
async def health_check(
    db: Session = Depends(get_db)
):
    """
    Vérifier que le moteur de requêtes est opérationnel
    
    **Vérifie:**
    - Connexion à APP_DB (SQLAlchemy)
    - Connexion à DWH_DB (PostgreSQL)
    - Disponibilité Claude API
    
    **Retourne:**
    - `status`: "healthy" ou "degraded"
    - `details`: Détails de chaque composant
    """
    import os
    import psycopg2
    
    health = {
        "status": "healthy",
        "details": {
            "app_db": "unknown",
            "dwh_db": "unknown",
            "claude_api": "unknown"
        }
    }
    
    # Test APP_DB
    try:
        db.execute("SELECT 1")
        health["details"]["app_db"] = "connected"
    except Exception as e:
        health["details"]["app_db"] = f"error: {str(e)}"
        health["status"] = "degraded"
    
    # Test DWH_DB
    try:
        dwh_config = {
            'host': os.getenv('DWH_HOST', 'localhost'),
            'port': os.getenv('DWH_PORT', '5432'),
            'database': os.getenv('DWH_DB', 'hr_datawarehouse'),
            'user': os.getenv('DWH_USER', 'hr_user'),
            'password': os.getenv('DWH_PASSWORD', 'hr_password123')
        }
        conn = psycopg2.connect(**dwh_config)
        conn.close()
        health["details"]["dwh_db"] = "connected"
    except Exception as e:
        health["details"]["dwh_db"] = f"error: {str(e)}"
        health["status"] = "degraded"
    
    # Test Claude API
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    if anthropic_key:
        health["details"]["claude_api"] = "configured"
    else:
        health["details"]["claude_api"] = "missing_api_key"
        health["status"] = "degraded"
    
    return health
