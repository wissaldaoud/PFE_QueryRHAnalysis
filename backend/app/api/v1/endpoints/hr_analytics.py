"""
API Routes pour HR Analytics
Endpoints pour CV matching, recommandation de formation et scoring prédictif
"""

from typing import List, Optional, Dict
from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File
from pydantic import BaseModel, Field, validator
from sqlalchemy.orm import Session
from datetime import date, datetime
import logging

from app.services.hr_analytics import HRAnalyticsService
from app.services.cv_matching import CVData, JobOffer, MatchingResult
from app.services.training_recommendation import (
    EmployeeProfile,
    TrainingCourse,
    TrainingRecommendation
)
from app.services.predictive_scoring import EmployeeHistory, PredictiveScore
from app.services.cv_parser import CVParser
from app.db.base import get_db
from app.models.employee import Employee, EmploymentStatus
from app.models.department import Department

# Import cache and metrics (if available)
try:
    from app.utils.cache import embedding_cache, performance_metrics
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False

logger = logging.getLogger(__name__)

router = APIRouter()

# Instance globale du service (sera initialisée au démarrage)
hr_analytics_service: Optional[HRAnalyticsService] = None


def get_hr_analytics_service() -> HRAnalyticsService:
    """Dependency pour obtenir le service HR Analytics"""
    if hr_analytics_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="HR Analytics service not initialized"
        )
    return hr_analytics_service


# ==================== Models Pydantic ====================

class CVDataRequest(BaseModel):
    """Modèle de requête pour un CV"""
    skills: List[str] = Field(..., description="Liste des compétences")
    experiences: List[str] = Field(..., description="Descriptions d'expériences")
    job_titles: List[str] = Field(..., description="Intitulés des postes précédents")
    education: List[str] = Field(..., description="Formations et diplômes")
    years_of_experience: Optional[float] = Field(None, description="Années d'expérience")
    full_text: Optional[str] = Field(None, description="Texte complet du CV")


class JobOfferRequest(BaseModel):
    """Modèle de requête pour une offre d'emploi"""
    required_skills: List[str] = Field(..., description="Compétences requises")
    preferred_skills: List[str] = Field(default_factory=list, description="Compétences préférées")
    job_title: str = Field(..., description="Intitulé du poste")
    description: str = Field(..., description="Description du poste")
    required_experience_years: Optional[float] = Field(None, description="Années d'expérience requises")
    required_education: Optional[List[str]] = Field(None, description="Formation requise")


class CVMatchingRequest(BaseModel):
    """Requête pour le CV matching"""
    cv: CVDataRequest
    job_offer: JobOfferRequest


class EmployeeProfileRequest(BaseModel):
    """Modèle de requête pour un profil d'employé"""
    employee_id: str = Field(..., description="Identifiant de l'employé")
    current_skills: List[str] = Field(..., description="Compétences actuelles")
    training_history: List[str] = Field(default_factory=list, description="Formations suivies")
    current_position: str = Field(..., description="Poste actuel")
    target_position: Optional[str] = Field(None, description="Poste visé")
    interests: Optional[List[str]] = Field(None, description="Centres d'intérêt")
    department: Optional[str] = Field(None, description="Département")


class TrainingCourseRequest(BaseModel):
    """Modèle de requête pour une formation"""
    course_id: str = Field(..., description="Identifiant de la formation")
    title: str = Field(..., description="Titre de la formation")
    description: str = Field(..., description="Description")
    skills_taught: List[str] = Field(..., description="Compétences enseignées")
    level: str = Field(..., description="Niveau (débutant, intermédiaire, avancé)")
    duration_hours: float = Field(..., description="Durée en heures")
    category: str = Field(..., description="Catégorie")
    prerequisites: Optional[List[str]] = Field(None, description="Prérequis")
    
    @validator("level")
    def validate_level(cls, v):
        allowed = ["débutant", "intermédiaire", "avancé", "beginner", "intermediate", "advanced"]
        if v.lower() not in allowed:
            raise ValueError(f"Level must be one of: {allowed}")
        return v


class TrainingRecommendationRequest(BaseModel):
    """Requête pour recommandation de formation"""
    employee: EmployeeProfileRequest
    available_courses: List[TrainingCourseRequest]
    required_skills_map: Optional[Dict[str, List[str]]] = Field(
        None,
        description="Mapping poste -> compétences requises"
    )
    top_n: int = Field(5, ge=1, le=20, description="Nombre de recommandations")


class EmployeeHistoryRequest(BaseModel):
    """Modèle de requête pour l'historique RH"""
    employee_id: str = Field(..., description="Identifiant de l'employé")
    tenure_months: float = Field(..., ge=0, description="Ancienneté en mois")
    absences_last_year: int = Field(..., ge=0, description="Nombre d'absences (12 mois)")
    average_performance_score: float = Field(..., ge=0, le=10, description="Score de performance moyen (0-10)")
    promotion_count: int = Field(..., ge=0, description="Nombre de promotions")
    training_hours_last_year: float = Field(..., ge=0, description="Heures de formation (12 mois)")
    salary_percentile: float = Field(..., ge=0, le=100, description="Percentile salarial (0-100)")
    department: str = Field(..., description="Département")
    manager_changes_count: int = Field(..., ge=0, description="Nombre de changements de manager")
    overtime_hours_monthly: float = Field(..., ge=0, description="Heures sup. mensuelles moyennes")
    team_size: int = Field(..., ge=1, description="Taille de l'équipe")
    remote_work_percentage: float = Field(..., ge=0, le=100, description="% de télétravail")
    last_salary_increase_months: Optional[int] = Field(None, ge=0, description="Mois depuis dernière augmentation")
    feedback_score: Optional[float] = Field(None, ge=0, le=10, description="Score de feedback 360° (0-10)")
    engagement_survey_score: Optional[float] = Field(None, ge=0, le=10, description="Score d'engagement (0-10)")


class TurnoverPredictionRequest(BaseModel):
    """Modèle de requête pour la prédiction de turnover (nouveau modèle)"""
    date_naissance: str = Field(..., description="Date de naissance (YYYY-MM-DD)")
    date_embauche: str = Field(..., description="Date d'embauche (YYYY-MM-DD)")
    sexe: str = Field(..., description="Sexe (Masculin/Féminin)")
    type_contrat: str = Field(..., description="Type de contrat (CDI/CDD/Inconnu)")
    total_jours_absence: int = Field(0, ge=0, description="Total jours d'absence")
    nb_absences: int = Field(0, ge=0, description="Nombre d'absences")


class EmployeeListItem(BaseModel):
    """Modèle de réponse pour un employé dans la liste"""
    id: int
    employee_code: str
    first_name: str
    last_name: str
    full_name: str
    job_title: Optional[str]
    department_name: Optional[str]
    department_id: Optional[int]
    hire_date: date
    tenure_months: int
    employment_status: str
    email: Optional[str]
    
    class Config:
        from_attributes = True


# ==================== Endpoints ====================

@router.get("/employees", tags=["Employees"], response_model=List[EmployeeListItem])
async def get_active_employees(
    db: Session = Depends(get_db),
    status_filter: Optional[str] = None,
    department_id: Optional[int] = None,
    all: bool = False
):
    """
    Récupère la liste des employés de la base de données
    
    Args:
        status_filter: Filtrer par statut (active, inactive, on_leave, terminated)
        department_id: Filtrer par département
        all: Si True, retourne TOUS les employés sans filtre de statut
    
    Returns:
        Liste des employés avec leurs informations de base
    """
    try:
        query = db.query(Employee).outerjoin(Department, Employee.department_id == Department.id)
        
        # Filtrer par statut (par défaut: actifs uniquement, sauf si all=True)
        if not all:
            if status_filter:
                query = query.filter(Employee.employment_status == status_filter)
            else:
                query = query.filter(Employee.employment_status == EmploymentStatus.active)
        
        # Filtrer par département si spécifié
        if department_id:
            query = query.filter(Employee.department_id == department_id)
        
        # Trier par nom
        query = query.order_by(Employee.last_name, Employee.first_name)
        
        employees = query.all()
        
        # Construire la réponse
        result = []
        for emp in employees:
            # Calculer l'ancienneté en mois
            today = datetime.now().date()
            tenure_days = (today - emp.hire_date).days
            tenure_months = int(tenure_days / 30)
            
            result.append(EmployeeListItem(
                id=emp.id,
                employee_code=emp.employee_code,
                first_name=emp.first_name,
                last_name=emp.last_name,
                full_name=f"{emp.first_name} {emp.last_name}",
                job_title=emp.job_title,
                department_name=emp.department.name if emp.department else None,
                department_id=emp.department_id,
                hire_date=emp.hire_date,
                tenure_months=tenure_months,
                employment_status=emp.employment_status.value,
                email=emp.email
            ))
        
        return result
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des employés: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des employés: {str(e)}"
        )


@router.get("/employees-dwh", tags=["Employees DWH"])
async def get_dwh_employees(
    limit: Optional[int] = 1000,
    active_only: bool = True
):
    """
    🔥 NOUVEAU : Charge les employés depuis le DWH Qlik avec ancienneté CORRIGÉE
    
    Args:
        limit: Nombre max d'employés à retourner (défaut: 1000)
        active_only: Si True, retourne uniquement les employés actifs
    
    Returns:
        Liste des employés DWH au format compatible frontend
    """
    try:
        from dwh_connection import get_dwh_engine
        from sqlalchemy import text
        
        engine = get_dwh_engine()
        
        query = text("""
            WITH CONTRAT_ACTUEL AS (
                SELECT 
                    nudoss,
                    categorie_contrat AS type_contrat,
                    MIN(date_debut_contrat) OVER (PARTITION BY nudoss) AS date_premiere_embauche,
                    date_debut_contrat,
                    ROW_NUMBER() OVER (PARTITION BY nudoss ORDER BY date_debut_contrat DESC) AS rn
                FROM fait.fait_contrat
            ),
            AFFECTATION_ACTUELLE AS (
                SELECT
                    nudoss,
                    libelle_poste,
                    ROW_NUMBER() OVER (PARTITION BY nudoss ORDER BY date_debut_affectation DESC) AS rn
                FROM fait.fait_affectation
            )
            SELECT 
                e.nudoss,
                e.matricule,
                e.nom_complet,
                e.age,
                e.code_sexe,
                COALESCE(c.type_contrat, 'CDI') AS type_contrat,
                ROUND(
                    CAST(
                        EXTRACT(EPOCH FROM (CURRENT_DATE - COALESCE(c.date_premiere_embauche, c.date_debut_contrat, CURRENT_DATE))) 
                        / (365.25 * 86400) 
                    AS NUMERIC), 
                    2
                ) AS anciennete_annees,
                c.date_premiere_embauche AS hire_date,
                COALESCE(a.libelle_poste, 'Non renseigné') AS job_title,
                'Non renseigné' AS department_name,
                e.flag_employe_actif
            FROM dim.dim_employe e
            LEFT JOIN CONTRAT_ACTUEL c ON e.nudoss = c.nudoss AND c.rn = 1
            LEFT JOIN AFFECTATION_ACTUELLE a ON e.nudoss = a.nudoss AND a.rn = 1
            WHERE e.age BETWEEN 18 AND 70
            AND e.date_naissance IS NOT NULL
            AND (:active_only = FALSE OR e.flag_employe_actif = 1)
            -- Filtrer données de test
            AND e.nom_complet !~* 'test|xxx|tmp'
            AND COALESCE(e.matricule, '') !~* 'test|frw|tmp|xxx'
            AND e.nom_complet !~* '^[A-Z]{1,3} [A-Z]{1,3}$'
            AND e.nom_complet !~ '[?]{2,}'
            AND LENGTH(e.nom_complet) >= 5
            AND e.nom_complet !~ '(.)\1{3,}'
            AND e.nom_complet !~ '^([A-Z])\1+ \1\1+'
            ORDER BY e.nom_complet
            LIMIT :limit
        """)
        
        with engine.connect() as conn:
            result = conn.execute(
                query, 
                {"limit": limit, "active_only": active_only}
            )
            rows = result.fetchall()
        
        # Convertir au format attendu par le frontend
        employees = []
        for row in rows:
            # Calculer tenure_months depuis anciennete_annees
            tenure_months = int(float(row[6] or 0) * 12) if row[6] else 0
            
            employees.append({
                "id": row[0],  # nudoss comme ID
                "employee_code": row[1] or row[0],  # matricule ou nudoss
                "first_name": row[2].split()[0] if row[2] and ' ' in row[2] else row[2],
                "last_name": ' '.join(row[2].split()[1:]) if row[2] and ' ' in row[2] else "",
                "full_name": row[2] or "",
                "job_title": row[8],
                "department_name": row[9],
                "department_id": None,
                "hire_date": row[7].isoformat() if row[7] else None,
                "tenure_months": tenure_months,
                "employment_status": "active" if row[10] == 1 else "terminated",
                "email": None,
                # Infos supplémentaires pour le ML
                "age": row[3],
                "anciennete_annees": float(row[6]) if row[6] else 0.0,
                "type_contrat": row[5],
                "sexe": row[4]
            })
        
        return employees
        
    except Exception as e:
        logger.error(f"Erreur DWH employees: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur DWH: {str(e)}"
        )


@router.get("/health", tags=["Health"])
async def health_check(
    service: HRAnalyticsService = Depends(get_hr_analytics_service)
):
    """Vérifie l'état de santé du service HR Analytics"""
    return service.health_check()


@router.get("/metrics", tags=["Monitoring"])
async def get_performance_metrics():
    """
    Retourne les métriques de performance du système
    
    Inclut :
    - Statistiques du cache (hit rate, taille)
    - Métriques de performance (latence, throughput)
    - Statistiques par endpoint
    """
    metrics = {
        "status": "success",
        "cache_available": CACHE_AVAILABLE
    }
    
    if CACHE_AVAILABLE:
        # Statistiques du cache
        cache_stats = embedding_cache.get_stats()
        metrics["cache"] = cache_stats
        
        # Métriques de performance
        perf_stats = performance_metrics.get_stats()
        metrics["performance"] = perf_stats
    else:
        metrics["message"] = "Cache et métriques non activés. Importer app.utils.cache pour activer."
    
    return metrics


# ==================== CV PARSING ====================

@router.post("/parse-cv", tags=["CV Parsing"])
async def parse_cv_file(
    file: UploadFile = File(...)
):
    """
    Parse un fichier CV (PDF, DOCX, TXT) et extrait les données structurées
    
    Supporte :
    - PDF (.pdf)
    - Word (.docx, .doc)
    - Texte (.txt)
    
    Retourne le texte complet et les données extraites :
    - Compétences
    - Expériences
    - Postes
    - Formation
    - Années d'expérience
    - Email, téléphone
    """
    try:
        # Vérifier l'extension du fichier
        filename = file.filename or "unknown.txt"
        allowed_extensions = ['txt', 'pdf', 'doc', 'docx']
        file_ext = filename.lower().split('.')[-1]
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Type de fichier non supporté: {file_ext}. Utilisez: {', '.join(allowed_extensions)}"
            )
        
        # Lire le contenu du fichier
        content = await file.read()
        
        if not content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Le fichier est vide"
            )
        
        # Parser le CV
        parser = CVParser()
        result = parser.parse_cv(filename, content)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Erreur lors du parsing du CV")
            )
        
        return {
            "status": "success",
            "filename": filename,
            "text": result["text"],
            "extracted_data": result["data"],
            "message": f"{result['data']['extracted_skills_count']} compétences détectées automatiquement"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors du parsing du CV: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du parsing: {str(e)}"
        )


# ==================== CV MATCHING ====================

@router.post("/cv-matching", tags=["CV Matching"], response_model=Dict)
async def match_cv_to_job(
    request: CVMatchingRequest,
    service: HRAnalyticsService = Depends(get_hr_analytics_service)
):
    """
    Compare un CV avec une offre d'emploi
    
    Retourne un score de correspondance global ainsi que des scores détaillés
    par catégorie (compétences, expérience, titre, éducation) et des recommandations.
    """
    try:
        # Conversion des modèles Pydantic vers les dataclasses
        cv = CVData(
            skills=request.cv.skills,
            experiences=request.cv.experiences,
            job_titles=request.cv.job_titles,
            education=request.cv.education,
            years_of_experience=request.cv.years_of_experience,
            full_text=request.cv.full_text
        )
        
        job = JobOffer(
            required_skills=request.job_offer.required_skills,
            preferred_skills=request.job_offer.preferred_skills,
            job_title=request.job_offer.job_title,
            description=request.job_offer.description,
            required_experience_years=request.job_offer.required_experience_years,
            required_education=request.job_offer.required_education
        )
        
        result = service.match_cv_to_job(cv, job)
        
        return {
            "status": "success",
            "data": {
                "overall_score": result.overall_score,
                "skills_score": result.skills_score,
                "experience_score": result.experience_score,
                "title_score": result.title_score,
                "education_score": result.education_score,
                "matching_skills": result.matching_skills,
                "missing_required_skills": result.missing_required_skills,
                "missing_preferred_skills": result.missing_preferred_skills,
                "recommendations": result.recommendations
            }
        }
        
    except Exception as e:
        logger.error(f"Erreur CV matching: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during CV matching: {str(e)}"
        )


@router.post("/cv-matching/batch", tags=["CV Matching"])
async def batch_match_cvs(
    cvs: List[CVDataRequest],
    job_offer: JobOfferRequest,
    service: HRAnalyticsService = Depends(get_hr_analytics_service)
):
    """
    Compare plusieurs CVs avec une offre d'emploi
    
    Retourne les résultats triés par score décroissant.
    """
    try:
        cv_data_list = [
            CVData(
                skills=cv.skills,
                experiences=cv.experiences,
                job_titles=cv.job_titles,
                education=cv.education,
                years_of_experience=cv.years_of_experience,
                full_text=cv.full_text
            )
            for cv in cvs
        ]
        
        job = JobOffer(
            required_skills=job_offer.required_skills,
            preferred_skills=job_offer.preferred_skills,
            job_title=job_offer.job_title,
            description=job_offer.description,
            required_experience_years=job_offer.required_experience_years,
            required_education=job_offer.required_education
        )
        
        results = service.batch_match_cvs(cv_data_list, job)
        
        return {
            "status": "success",
            "total_cvs": len(cvs),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Erreur batch CV matching: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during batch CV matching: {str(e)}"
        )


# ==================== TRAINING RECOMMENDATION ====================

@router.post("/training-recommendation", tags=["Training"])
async def recommend_trainings(
    request: TrainingRecommendationRequest,
    service: HRAnalyticsService = Depends(get_hr_analytics_service)
):
    """
    Recommande les meilleures formations pour un employé
    
    Basé sur les compétences actuelles, l'historique de formation,
    le poste actuel/cible et les centres d'intérêt.
    """
    try:
        employee = EmployeeProfile(
            employee_id=request.employee.employee_id,
            current_skills=request.employee.current_skills,
            training_history=request.employee.training_history,
            current_position=request.employee.current_position,
            target_position=request.employee.target_position,
            interests=request.employee.interests,
            department=request.employee.department
        )
        
        courses = [
            TrainingCourse(
                course_id=course.course_id,
                title=course.title,
                description=course.description,
                skills_taught=course.skills_taught,
                level=course.level,
                duration_hours=course.duration_hours,
                category=course.category,
                prerequisites=course.prerequisites
            )
            for course in request.available_courses
        ]
        
        recommendations = service.recommend_trainings(
            employee=employee,
            available_courses=courses,
            required_skills_map=request.required_skills_map,
            top_n=request.top_n
        )
        
        return {
            "status": "success",
            "employee_id": employee.employee_id,
            "recommendations": [
                {
                    "course_id": rec.course.course_id,
                    "course_title": rec.course.title,
                    "relevance_score": rec.relevance_score,
                    "priority": rec.priority,
                    "skill_gap_addressed": rec.skill_gap_addressed,
                    "reasoning": rec.reasoning,
                    "duration_hours": rec.course.duration_hours,
                    "level": rec.course.level
                }
                for rec in recommendations
            ]
        }
        
    except Exception as e:
        logger.error(f"Erreur recommandation formation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during training recommendation: {str(e)}"
        )


# ==================== PREDICTIVE SCORING ====================

@router.get("/predictive-scoring/ml/{employee_id}", tags=["Predictive Scoring ML"])
async def calculate_turnover_ml(
    employee_id: str,
    db: Session = Depends(get_db)
):
    """
    🤖 Prédiction de turnover XGBoost + SHAP
    
    🔥 Charge depuis VOTRE base de données app (table employees)
    
    Args:
        employee_id: ID de l'employé dans votre base
    
    Returns:
        Score ML avec SHAP top 5 facteurs, recommandations RH, niveau de risque.
    """
    try:
        from app.services.predictive_scoring import PredictiveScorerML
        from app.models.leave import LeaveRequest
        from sqlalchemy import func
        from datetime import timedelta

        try:
            scorer_ml = PredictiveScorerML()
        except FileNotFoundError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(e)
            )

        # 🔥 CHARGER DEPUIS VOTRE BASE APP
        try:
            eid_int = int(employee_id)
            employee = db.query(Employee).filter(Employee.id == eid_int).first()
        except (ValueError, TypeError):
            employee = None

        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Employé {employee_id} introuvable"
            )
        
        # Calculer âge et ancienneté
        today = datetime.now().date()
        age = (today - employee.date_of_birth).days // 365 if employee.date_of_birth else 30
        anciennete_mois = int((today - employee.hire_date).days / 30.44) if employee.hire_date else 0
        
        # Absences sur 24 mois
        cutoff = today - timedelta(days=730)
        nb_absences = db.query(func.count(LeaveRequest.id)).filter(
            LeaveRequest.employee_id == employee.id,
            LeaveRequest.start_date >= cutoff
        ).scalar() or 0
        
        total_jours = db.query(func.coalesce(func.sum(LeaveRequest.days_requested), 0)).filter(
            LeaveRequest.employee_id == employee.id,
            LeaveRequest.start_date >= cutoff
        ).scalar() or 0
        
        # Préparer les données
        employee_data = {
            "employee_id": str(employee.id),
            "employee_code": employee.employee_code,
            "age": age,
            "anciennete_annees": anciennete_mois / 12,
            "anciennete_mois": anciennete_mois,
            "nb_absences": nb_absences,
            "total_jours_absence": float(total_jours),
            "type_contrat": "CDI",
            "poste": employee.job_title or "Unknown",
            "job_title": employee.job_title or "Unknown",
            "department_name": employee.department.name if employee.department else "Unknown",
            "salary": float(employee.salary) if employee.salary else 0.0,
            "employment_status": employee.employment_status.value if employee.employment_status else "active",
            "gender": "M",
        }

        score = scorer_ml.score(employee_data)

        # Convertir numpy types en types Python natifs
        def to_python_type(val):
            """Convertit les types numpy en types Python natifs"""
            if hasattr(val, 'item'):  # numpy scalar
                return val.item()
            if isinstance(val, (np.integer, np.floating)):
                return float(val)
            return val

        # Normaliser key_factors
        def normalize_factor(f):
            if isinstance(f, dict):
                return {
                    "feature": str(f.get("feature") or f.get("factor") or "unknown"),
                    "shap_value": float(f.get("shap_value") or f.get("contribution") or 0),
                    "direction": "positive" if float(f.get("shap_value") or f.get("contribution") or 0) > 0 else "negative",
                }
            if isinstance(f, (list, tuple)) and len(f) >= 2:
                return {
                    "feature": str(f[0]),
                    "shap_value": float(f[1]),
                    "direction": "positive" if float(f[1]) > 0 else "negative",
                }
            return {"feature": str(f), "shap_value": 0.0, "direction": "neutral"}

        churn_pct = float(score.churn_risk_score * 100)
        action_priority = str(score.action_priority) if hasattr(score, 'action_priority') and score.action_priority else (
            "critique" if churn_pct >= 70 else "élevée" if churn_pct >= 40 else "normale"
        )

        return {
            "employee_id": int(employee.id),
            "employee_name": f"{employee.first_name} {employee.last_name}",
            "churn_risk_score": float(score.churn_risk_score),
            "churn_risk_percent": round(churn_pct, 1),
            "risk_level": str(score.risk_level),
            "action_priority": action_priority,
            "performance_score": float(score.performance_score),
            "engagement_score": float(score.engagement_score),
            "prediction_confidence": float(score.prediction_confidence) if hasattr(score, 'prediction_confidence') else 0.7,
            "key_factors": [normalize_factor(f) for f in (score.key_factors or [])],
            "recommendations": [str(r) for r in (score.recommendations or [])],
            "features_used": {
                "age": int(age),
                "anciennete_annees": float(anciennete_mois / 12),
                "nb_absences": int(nb_absences),
                "total_jours_absence": float(total_jours),
                "type_contrat": "CDI",
                "department": employee.department.name if employee.department else "Unknown",
            },
            "model_version": str(score.model_version) if hasattr(score, 'model_version') else "v1",
            "computed_at": datetime.now().isoformat(),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors du scoring ML pour employé {employee_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du calcul du score ML: {str(e)}"
        )


@router.post("/predictive-scoring", tags=["Predictive Scoring"])
async def calculate_predictive_scores(
    history: EmployeeHistoryRequest,
    service: HRAnalyticsService = Depends(get_hr_analytics_service)
):
    """
    Calcule les scores prédictifs pour un employé
    
    Retourne :
    - Score de risque de churn (0-1)
    - Score de performance prédictif (0-1)
    - Score d'engagement (0-1)
    - Niveau de risque (faible/moyen/élevé)
    - Facteurs clés
    - Recommandations RH
    """
    try:
        employee_history = EmployeeHistory(
            employee_id=history.employee_id,
            tenure_months=history.tenure_months,
            absences_last_year=history.absences_last_year,
            average_performance_score=history.average_performance_score,
            promotion_count=history.promotion_count,
            training_hours_last_year=history.training_hours_last_year,
            salary_percentile=history.salary_percentile,
            department=history.department,
            manager_changes_count=history.manager_changes_count,
            overtime_hours_monthly=history.overtime_hours_monthly,
            team_size=history.team_size,
            remote_work_percentage=history.remote_work_percentage,
            last_salary_increase_months=history.last_salary_increase_months,
            feedback_score=history.feedback_score,
            engagement_survey_score=history.engagement_survey_score
        )
        
        score = service.calculate_predictive_scores(employee_history)
        
        return {
            "status": "success",
            "data": {
                "employee_id": score.employee_id,
                "churn_risk_score": score.churn_risk_score,
                "performance_score": score.performance_score,
                "engagement_score": score.engagement_score,
                "risk_level": score.risk_level,
                "recommendations": score.recommendations,
                "prediction_confidence": score.prediction_confidence,
                "key_factors": [
                    {"factor": f.get("feature", f) if isinstance(f, dict) else f[0],
                     "contribution": round(f.get("shap_value", 0) if isinstance(f, dict) else f[1], 3)}
                    for f in score.key_factors
                ]
            }
        }
        
    except Exception as e:
        logger.error(f"Erreur scoring prédictif: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during predictive scoring: {str(e)}"
        )


@router.post("/predictive-scoring/batch", tags=["Predictive Scoring"])
async def batch_calculate_scores(
    histories: List[EmployeeHistoryRequest],
    service: HRAnalyticsService = Depends(get_hr_analytics_service)
):
    """Calcule les scores prédictifs pour plusieurs employés"""
    try:
        employee_histories = [
            EmployeeHistory(
                employee_id=h.employee_id,
                tenure_months=h.tenure_months,
                absences_last_year=h.absences_last_year,
                average_performance_score=h.average_performance_score,
                promotion_count=h.promotion_count,
                training_hours_last_year=h.training_hours_last_year,
                salary_percentile=h.salary_percentile,
                department=h.department,
                manager_changes_count=h.manager_changes_count,
                overtime_hours_monthly=h.overtime_hours_monthly,
                team_size=h.team_size,
                remote_work_percentage=h.remote_work_percentage,
                last_salary_increase_months=h.last_salary_increase_months,
                feedback_score=h.feedback_score,
                engagement_survey_score=h.engagement_survey_score
            )
            for h in histories
        ]
        
        scores = service.batch_calculate_scores(employee_histories)
        
        return {
            "status": "success",
            "total_employees": len(scores),
            "scores": [
                {
                    "employee_id": s.employee_id,
                    "churn_risk_score": s.churn_risk_score,
                    "performance_score": s.performance_score,
                    "engagement_score": s.engagement_score,
                    "risk_level": s.risk_level
                }
                for s in scores
            ]
        }
        
    except Exception as e:
        logger.error(f"Erreur batch scoring: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during batch scoring: {str(e)}"
        )


@router.post("/predictive-scoring/high-risk", tags=["Predictive Scoring"])
async def identify_high_risk_employees(
    histories: List[EmployeeHistoryRequest],
    risk_threshold: float = 0.6,
    service: HRAnalyticsService = Depends(get_hr_analytics_service)
):
    """Identifie les employés à risque élevé de départ"""
    try:
        employee_histories = [
            EmployeeHistory(
                employee_id=h.employee_id,
                tenure_months=h.tenure_months,
                absences_last_year=h.absences_last_year,
                average_performance_score=h.average_performance_score,
                promotion_count=h.promotion_count,
                training_hours_last_year=h.training_hours_last_year,
                salary_percentile=h.salary_percentile,
                department=h.department,
                manager_changes_count=h.manager_changes_count,
                overtime_hours_monthly=h.overtime_hours_monthly,
                team_size=h.team_size,
                remote_work_percentage=h.remote_work_percentage,
                last_salary_increase_months=h.last_salary_increase_months,
                feedback_score=h.feedback_score,
                engagement_survey_score=h.engagement_survey_score
            )
            for h in histories
        ]
        
        high_risk = service.identify_high_risk_employees(
            employee_histories,
            risk_threshold
        )
        
        return {
            "status": "success",
            "risk_threshold": risk_threshold,
            "high_risk_count": len(high_risk),
            "employees": [
                {
                    "employee_id": s.employee_id,
                    "churn_risk_score": s.churn_risk_score,
                    "risk_level": s.risk_level,
                    "recommendations": s.recommendations
                }
                for s in high_risk
            ]
        }
        
    except Exception as e:
        logger.error(f"Erreur identification haut risque: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error identifying high-risk employees: {str(e)}"
        )


# ==================== BATCH TURNOVER PREDICTION ====================

@router.get("/predict-turnover-batch", tags=["Predictive Scoring"])
async def predict_turnover_batch(
    db: Session = Depends(get_db),
    limit: Optional[int] = None
):
    """
    🚀 Prédiction batch - Calcule le risque de turnover pour TOUS les employés
    
    Charge tous les employés actifs de la base web, calcule leurs prédictions
    avec le modèle XGBoost + SHAP, et retourne un JSON complet.
    
    Args:
        limit: Limiter le nombre d'employés (optionnel, pour tests)
    
    Returns:
        Liste complète des prédictions avec scores, niveaux de risque, 
        facteurs SHAP et recommandations RH.
    """
    try:
        from app.services.predictive_scoring import PredictiveScorer
        from app.models.leave import LeaveRequest
        from sqlalchemy import func
        from datetime import timedelta
        
        # Initialiser le scorer
        try:
            scorer = PredictiveScorer()
            logger.info(f"✅ Modèle chargé : {scorer.model_version}")
        except FileNotFoundError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(e)
            )
        
        # Charger les employés actifs
        query = db.query(Employee).filter(
            Employee.employment_status == EmploymentStatus.active
        )
        
        if limit:
            query = query.limit(limit)
        
        employees = query.all()
        logger.info(f"📊 Traitement de {len(employees)} employés...")
        
        # Calculer les prédictions pour chaque employé
        predictions = []
        today = datetime.now().date()
        cutoff = today - timedelta(days=730)  # 24 mois
        
        for emp in employees:
            try:
                # Calculer âge et ancienneté
                age = (today - emp.date_of_birth).days // 365 if emp.date_of_birth else 30
                anciennete_mois = int((today - emp.hire_date).days / 30.44) if emp.hire_date else 0
                
                # Absences sur 24 mois
                nb_absences = db.query(func.count(LeaveRequest.id)).filter(
                    LeaveRequest.employee_id == emp.id,
                    LeaveRequest.start_date >= cutoff
                ).scalar() or 0
                
                total_jours = db.query(func.coalesce(func.sum(LeaveRequest.days_requested), 0)).filter(
                    LeaveRequest.employee_id == emp.id,
                    LeaveRequest.start_date >= cutoff
                ).scalar() or 0
                
                # Préparer les données
                employee_data = {
                    "employee_id": str(emp.id),
                    "employee_code": emp.employee_code,
                    "age": age,
                    "anciennete_annees": anciennete_mois / 12,
                    "anciennete_mois": anciennete_mois,
                    "nb_absences": nb_absences,
                    "total_jours_absence": float(total_jours),
                    "type_contrat": "CDI",
                    "poste": emp.job_title or "Unknown",
                    "job_title": emp.job_title or "Unknown",
                    "department_name": emp.department.name if emp.department else "Unknown",
                    "salary": float(emp.salary) if emp.salary else 0.0,
                    "employment_status": emp.employment_status.value if emp.employment_status else "active",
                    "sexe": "M",
                }
                
                # Calculer le score
                score = scorer.score(employee_data)
                
                # Normaliser key_factors
                def normalize_factor(f):
                    if isinstance(f, dict):
                        return {
                            "feature": f.get("feature") or f.get("factor") or str(f),
                            "shap_value": round(float(f.get("shap_value") or f.get("contribution") or 0), 4),
                            "direction": "positive" if (f.get("shap_value") or f.get("contribution") or 0) > 0 else "negative",
                        }
                    if isinstance(f, (list, tuple)) and len(f) >= 2:
                        return {
                            "feature": str(f[0]),
                            "shap_value": round(float(f[1]), 4),
                            "direction": "positive" if f[1] > 0 else "negative",
                        }
                    return {"feature": str(f), "shap_value": 0.0, "direction": "neutral"}
                
                churn_pct = round(score.churn_risk_score * 100, 1)
                action_priority = getattr(score, "action_priority", None)
                if not action_priority:
                    action_priority = "critique" if churn_pct >= 70 else "élevée" if churn_pct >= 40 else "normale"
                
                predictions.append({
                    "employee_id": emp.id,
                    "employee_code": emp.employee_code,
                    "employee_name": f"{emp.first_name} {emp.last_name}",
                    "job_title": emp.job_title,
                    "department": emp.department.name if emp.department else None,
                    "churn_risk_score": round(score.churn_risk_score, 4),
                    "churn_risk_percent": churn_pct,
                    "risk_level": score.risk_level,
                    "action_priority": action_priority,
                    "performance_score": round(score.performance_score, 4),
                    "engagement_score": round(score.engagement_score, 4),
                    "prediction_confidence": round(getattr(score, "prediction_confidence", 0.7), 4),
                    "key_factors": [normalize_factor(f) for f in (score.key_factors or [])],
                    "recommendations": score.recommendations or [],
                    "features_used": {
                        "age": age,
                        "anciennete_annees": anciennete_mois / 12,
                        "nb_absences": nb_absences,
                        "total_jours_absence": float(total_jours),
                        "type_contrat": "CDI",
                    },
                    "model_version": getattr(score, "model_version", "v1"),
                })
                
            except Exception as e:
                logger.warning(f"⚠️ Erreur employé {emp.id}: {e}")
                continue
        
        logger.info(f"✅ {len(predictions)} prédictions calculées")
        
        return {
            "status": "success",
            "total_employees": len(employees),
            "predictions_count": len(predictions),
            "model_version": scorer.model_version,
            "computed_at": datetime.now().isoformat(),
            "predictions": predictions
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur batch prediction: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la prédiction batch: {str(e)}"
        )


@router.post("/analytics/workforce", tags=["Analytics"])
async def generate_workforce_analytics(
    histories: List[EmployeeHistoryRequest],
    service: HRAnalyticsService = Depends(get_hr_analytics_service)
):
    """
    Génère des analytics globales sur l'ensemble des employés
    
    Statistiques agrégées sur le churn, la performance et l'engagement.
    """
    try:
        employee_histories = [
            EmployeeHistory(
                employee_id=h.employee_id,
                tenure_months=h.tenure_months,
                absences_last_year=h.absences_last_year,
                average_performance_score=h.average_performance_score,
                promotion_count=h.promotion_count,
                training_hours_last_year=h.training_hours_last_year,
                salary_percentile=h.salary_percentile,
                department=h.department,
                manager_changes_count=h.manager_changes_count,
                overtime_hours_monthly=h.overtime_hours_monthly,
                team_size=h.team_size,
                remote_work_percentage=h.remote_work_percentage,
                last_salary_increase_months=h.last_salary_increase_months,
                feedback_score=h.feedback_score,
                engagement_survey_score=h.engagement_survey_score
            )
            for h in histories
        ]
        
        analytics = service.generate_workforce_analytics(employee_histories)
        
        return {
            "status": "success",
            "analytics": analytics
        }
        
    except Exception as e:
        logger.error(f"Erreur analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating workforce analytics: {str(e)}"
        )


@router.post("/predict-turnover", tags=["Predictive Scoring"])
async def predict_employee_turnover(request: TurnoverPredictionRequest):
    """
    Prédiction de turnover avec nouveau modèle Gradient Boosting
    
    Utilise le modèle depuis C:\\Users\\wdaoud\\Documents\\Models\\turnover_model.pkl
    
    Features calculées automatiquement:
    - age (depuis date_naissance)
    - anciennete_annees (depuis date_embauche)
    - duree_presence_jours (depuis date_embauche)
    
    Retourne:
    - turnover_probability: probabilité de départ (0-1)
    - risk_level: Faible (<30%) / Moyen (30-60%) / Élevé (>60%)
    - prediction: 0 (reste) / 1 (part)
    """
    try:
        from ml.predict_turnover import predict_turnover
        
        # Préparer les données
        employee_data = {
            "date_naissance": request.date_naissance,
            "date_embauche": request.date_embauche,
            "sexe": request.sexe,
            "type_contrat": request.type_contrat,
            "total_jours_absence": request.total_jours_absence,
            "nb_absences": request.nb_absences,
        }
        
        # Effectuer la prédiction
        result = predict_turnover(employee_data)
        
        return {
            "status": "success",
            "prediction": result["prediction"],
            "turnover_probability": result["turnover_probability"],
            "turnover_probability_percent": result["turnover_probability_percent"],
            "risk_level": result["risk_level"],
            "risk_color": result["risk_color"],
            "risk_emoji": result["risk_emoji"],
            "features_used": result["features_used"],
            "model_path": result["model_path"],
            "computed_at": datetime.now().isoformat(),
        }
        
    except FileNotFoundError as e:
        logger.error(f"Modèle introuvable: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Modèle de prédiction introuvable. Vérifiez que turnover_model.pkl existe dans C:\\Users\\wdaoud\\Documents\\Models\\"
        )
    except Exception as e:
        logger.error(f"Erreur prédiction turnover: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la prédiction: {str(e)}"
        )


# ==================== Fonction d'initialisation ====================

def initialize_hr_analytics_service():
    """Initialise le service HR Analytics au démarrage de l'application"""
    global hr_analytics_service
    try:
        hr_analytics_service = HRAnalyticsService(
            enable_cv_matching=True,
            enable_training_recommendation=True,
            enable_predictive_scoring=True
        )
        logger.info("HR Analytics Service initialisé avec succès")
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation du service: {e}")
        raise
