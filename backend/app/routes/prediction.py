"""
Routes API FastAPI pour prédictions de turnover RH
Endpoints: /api/predict/turnover/{employe_id}, /api/predict/all, /api/predict/simulate
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from app.db.base import get_db
from app.services.ml_service import MLService


router = APIRouter(prefix="/ml", tags=["Prédictions ML"])


# ===== MODÈLES PYDANTIC =====

class TurnoverPredictionResponse(BaseModel):
    """Réponse de prédiction de turnover"""
    success: bool
    employe_id: int
    score: float = Field(..., description="Probabilité de départ (0-100%)")
    niveau: str = Field(..., description="Niveau de risque: Faible, Moyen, Élevé")
    recommandation: str = Field(..., description="Action recommandée en français")
    details: Optional[Dict[str, Any]] = None
    features_used: Optional[Dict[str, Any]] = None
    model_path: Optional[str] = None
    computed_at: Optional[str] = None


class WhatIfRequest(BaseModel):
    """Requête de simulation what-if"""
    employe_id: Optional[int] = Field(None, description="ID de l'employé (mode DWH)")
    base_data: Optional[Dict[str, Any]] = Field(None, description="Données de base (mode formulaire)")
    modifications: Dict[str, Any] = Field(
        ..., 
        description="Modifications à simuler",
        example={
            "nb_absences": 2,
            "salaire_mensuel": 7000,
            "anciennete_annees": 6
        }
    )


class WhatIfResponse(BaseModel):
    """Réponse de simulation what-if"""
    success: bool
    employe_id: Optional[int] = None
    avant: Dict[str, Any]
    apres: Dict[str, Any]
    delta: float = Field(..., description="Différence de score")
    impact: str = Field(..., description="Description de l'impact")
    modifications: Dict[str, Any]
    recommandation: str


class ErrorResponse(BaseModel):
    """Réponse d'erreur standard"""
    success: bool = False
    error: str


# ===== ENDPOINTS =====

@router.get(
    "/employees",
    summary="Liste des employés disponibles pour prédiction",
    description="Retourne la liste de tous les employés actifs depuis le DWH avec leur ID et nom complet"
)
async def get_employees_list(
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None, description="Recherche par nom ou prénom")
):
    """
    Récupère la liste des employés actifs depuis le DWH
    
    Args:
        db: Session de base de données
        search: Terme de recherche optionnel pour filtrer par nom/prénom
        
    Returns:
        Liste d'employés avec nudoss, nom complet et département
    """
    try:
        ml_service = MLService(db)
        
        if not ml_service.dwh_engine:
            raise HTTPException(
                status_code=503,
                detail="DWH non disponible"
            )
        
        from sqlalchemy import text
        
        # Requête pour récupérer les employés actifs avec noms valides
        query = text("""
            SELECT DISTINCT
                e.nudoss,
                TRIM(REPLACE(COALESCE(e.nom, ''), '''', '')) as nom,
                TRIM(REPLACE(COALESCE(e.prenom, ''), '''', '')) as prenom,
                TRIM(REPLACE(CONCAT(COALESCE(e.nom, ''), ' ', COALESCE(e.prenom, '')), '''', '')) as nom_complet,
                COALESCE(af.libelle_poste, 'Non affecté') as poste
            FROM dim.dim_employe e
            LEFT JOIN fait.fait_affectation af ON e.nudoss = af.nudoss 
                AND af.flag_affectation_active = 1
            WHERE e.flag_employe_actif = 1
                AND TRIM(COALESCE(e.nom, '')) != ''
                AND TRIM(COALESCE(e.prenom, '')) != ''
                AND LENGTH(TRIM(e.nom)) >= 2
                AND LENGTH(TRIM(e.prenom)) >= 2
                -- Exclure les données de test
                AND e.nom NOT LIKE '%XXXXX%'
                AND e.nom NOT LIKE '%yyyyy%'
                AND e.prenom NOT LIKE '%XXXXX%'
                AND e.prenom NOT LIKE '%yyyyy%'
                AND e.nom !~ '^[0-9A]'  -- Ne commence pas par un chiffre ou A suivi de chiffre
                AND e.nom !~ '[?]'     -- Pas de points d'interrogation
                -- Exclure les patterns de test (AA, AAA, etc.)
                AND NOT (e.nom ~ '^[A-Z]+$' AND e.prenom ~ '^[A-Z][a-z]+$' AND LENGTH(e.nom) <= 3)
                -- Noms réalistes: au moins 3 caractères avec des minuscules
                AND (e.nom ~ '[a-z]' OR LENGTH(e.nom) > 3)
            ORDER BY nom, prenom
            LIMIT 500
        """)
        
        with ml_service.dwh_engine.connect() as conn:
            result = conn.execute(query)
            employees = []
            
            for row in result:
                nudoss = str(row[0])
                nom = row[1]
                prenom = row[2]
                nom_complet = row[3]
                poste = row[4]
                
                # Double vérification côté Python
                if not nom_complet or nom_complet.strip() == '':
                    continue
                
                # Filtrer par recherche si fournie
                if search and search.lower() not in nom_complet.lower():
                    continue
                
                employees.append({
                    "nudoss": nudoss,
                    "nom": nom,
                    "prenom": prenom,
                    "nom_complet": nom_complet,
                    "poste": poste
                })
        
        return {
            "success": True,
            "count": len(employees),
            "employees": employees
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération des employés: {str(e)}"
        )


@router.get(
    "/turnover/{employe_id}",
    response_model=TurnoverPredictionResponse,
    summary="Prédire le risque de turnover d'un employé",
    description="""
    Prédit la probabilité qu'un employé quitte l'entreprise.
    
    **Fonctionnement:**
    1. Récupère les données de l'employé depuis le DWH (PostgreSQL)
    2. Transforme les données au format IBM HR Analytics
    3. Applique le modèle XGBoost entraîné
    4. Retourne un score (0-100%), un niveau de risque et une recommandation
    
    **Niveaux de risque:**
    - Faible (0-30%): Employé stable
    - Moyen (30-60%): Surveiller
    - Élevé (60-100%): Intervention urgente requise
    """
)
async def predict_turnover(
    employe_id: int,
    db: Session = Depends(get_db)
):
    """
    Prédit le risque de turnover pour un employé spécifique
    Utilise MLService pour faire la prédiction depuis le DWH
    
    Args:
        employe_id: Identifiant unique de l'employé (nudoss)
        db: Session de base de données
        
    Returns:
        Prédiction avec score, niveau et recommandation en français
        
    Raises:
        HTTPException: Si l'employé n'existe pas ou erreur de prédiction
    """
    try:
        ml_service = MLService(db)
        result = ml_service.predict_from_dwh(str(employe_id))
        
        # Vérifier si la prédiction a réussi
        if not result.get("success", False):
            error_msg = result.get("error", "Erreur inconnue")
            
            # Si l'employé est introuvable dans la base locale
            if "introuvable dans la base de données" in error_msg.lower():
                raise HTTPException(
                    status_code=404,
                    detail=error_msg
                )
            else:
                raise HTTPException(status_code=500, detail=error_msg)
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la prédiction: {str(e)}"
        )


# Alias pour compatibilité avec le frontend
@router.get(
    "/predict/employee/{employe_id}",
    response_model=TurnoverPredictionResponse,
    summary="[ALIAS] Prédire le risque de turnover d'un employé",
    description="Alias de /turnover/{employe_id} pour compatibilité frontend"
)
async def predict_employee_alias(
    employe_id: int,
    db: Session = Depends(get_db)
):
    """Alias pour predict_turnover - compatibilité frontend"""
    return await predict_turnover(employe_id, db)


@router.get(
    "/all",
    response_model=List[TurnoverPredictionResponse],
    summary="Prédire le turnover de tous les employés",
    description="""
    Analyse tous les employés actifs et retourne une liste triée par risque décroissant.
    
    **Utilisation:**
    - Permet d'identifier rapidement les employés à risque élevé
    - Liste triée du plus risqué au moins risqué
    - Par défaut, analyse les 50 premiers employés
    
    **Paramètres:**
    - limit: Nombre maximum d'employés à analyser (défaut: 50, max: 200)
    """
)
async def predict_all_turnover(
    limit: int = Query(
        default=50,
        ge=1,
        le=200,
        description="Nombre maximum d'employés à analyser"
    ),
    db: Session = Depends(get_db)
):
    """
    Prédit le risque de turnover pour tous les employés actifs
    
    Args:
        limit: Nombre maximum d'employés à analyser (1-200)
        db: Session de base de données
        
    Returns:
        Liste des prédictions triée par risque décroissant
        
    Raises:
        HTTPException: En cas d'erreur de traitement
    """
    try:
        ml_service = MLService(db)
        results = ml_service.predict_all_employees(limit=limit)
        
        if not results:
            return []
        
        return results
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'analyse globale: {str(e)}"
        )


@router.post(
    "/simulate",
    response_model=WhatIfResponse,
    summary="Simuler l'impact de modifications (What-If)",
    description="""
    Simule l'impact de modifications sur le risque de turnover d'un employé.
    
    **Cas d'usage:**
    - Évaluer l'effet d'une augmentation de salaire
    - Tester l'impact d'une réduction des absences
    - Simuler un changement de département
    
    **Modifications supportées:**
    - nb_absences: Nombre d'absences
    - salaire_mensuel: Salaire mensuel brut
    - anciennete_annees: Années d'ancienneté
    - total_jours_absence: Total de jours d'absence
    - department: Département
    
    **Retour:**
    - Scores avant/après
    - Delta (différence)
    - Impact descriptif
    - Recommandation
    """
)
async def simulate_whatif(
    request: WhatIfRequest,
    db: Session = Depends(get_db)
):
    """
    Simule l'impact de modifications sur le risque de turnover
    
    Args:
        request: Requête contenant soit l'ID employé (mode DWH) soit les données de base (mode formulaire)
        db: Session de base de données
        
    Returns:
        Comparaison avant/après avec analyse de l'impact
        
    Raises:
        HTTPException: Si simulation impossible
    """
    try:
        ml_service = MLService(db)
        
        # Mode DWH : avec employe_id
        if request.employe_id is not None:
            result = ml_service.simulate_whatif_dwh(
                str(request.employe_id),
                request.modifications
            )
        # Mode formulaire : avec base_data
        elif request.base_data is not None:
            result = ml_service.simulate_whatif(
                request.base_data,
                request.modifications
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="Vous devez fournir soit 'employe_id' soit 'base_data'"
            )
        
        if not result.get('success'):
            raise HTTPException(
                status_code=400,
                detail=result.get('error', 'Simulation impossible')
            )
        
        # Normaliser la réponse pour correspondre au modèle Pydantic
        if 'interpretation' in result and 'impact' not in result:
            result['impact'] = result['interpretation']
        if 'modifications' not in result:
            result['modifications'] = request.modifications
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la simulation: {str(e)}"
        )


# Alias pour compatibilité avec le frontend
@router.post(
    "/predict/whatif",
    response_model=WhatIfResponse,
    summary="[ALIAS] Simuler l'impact de modifications (What-If)",
    description="Alias de /simulate pour compatibilité frontend"
)
async def simulate_whatif_alias(
    request: WhatIfRequest,
    db: Session = Depends(get_db)
):
    """Alias pour simulate_whatif - compatibilité frontend"""
    return await simulate_whatif(request, db)


@router.get(
    "/health",
    summary="Vérifier le statut du service ML",
    description="Endpoint de santé pour vérifier que le modèle est chargé et opérationnel"
)
async def health_check(db: Session = Depends(get_db)):
    """
    Vérifie le statut du service de prédiction
    
    Returns:
        Statut du service et informations du modèle
    """
    try:
        ml_service = MLService(db)
        
        return {
            "status": "operational",
            "model_loaded": ml_service.model is not None,
            "features_count": len(ml_service.feature_names) if ml_service.feature_names else 0,
            "dwh_connected": ml_service.dwh_engine is not None,
            "message": "Service de prédiction de turnover opérationnel"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "model_loaded": False,
            "error": str(e),
            "message": "Service de prédiction non disponible"
        }


# ===== EXEMPLES DE RÉPONSES =====

@router.get(
    "/example",
    summary="Exemple de réponse",
    description="Retourne un exemple de réponse de prédiction pour documentation"
)
async def get_example_response():
    """Retourne un exemple de réponse pour la documentation"""
    return {
        "prediction_individuelle": {
            "success": True,
            "employe_id": 12345,
            "score": 67.8,
            "niveau": "Élevé",
            "recommandation": "Risque critique! Intervention immédiate recommandée: entretien RH, analyse des motivations, plan de rétention.",
            "details": {
                "age": 35,
                "anciennete": 5,
                "absences": 8,
                "department": "Sales"
            }
        },
        "simulation_whatif": {
            "success": True,
            "employe_id": 12345,
            "avant": {
                "score": 67.8,
                "niveau": "Élevé"
            },
            "apres": {
                "score": 45.2,
                "niveau": "Moyen"
            },
            "delta": 22.6,
            "impact": "Réduction du risque de 22.60%",
            "modifications": {
                "nb_absences": 2,
                "salaire_mensuel": 7000
            },
            "recommandation": "Modifications bénéfiques"
        }
    }
