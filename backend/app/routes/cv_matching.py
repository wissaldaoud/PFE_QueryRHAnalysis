"""
Routes API pour le matching CV et gestion des offres d'emploi
API Gateway : Route vers ML Microservice pour les opérations ML
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import json
import os

from app.db.base import get_db
from app.models.job_offer import JobOffer as JobOfferModel
from app.services.ml_client import get_ml_client

# Configuration ML Service URL
ML_SERVICE_URL = os.getenv("ML_SERVICE_URL", "http://localhost:8001")


router = APIRouter(prefix="/cv-matching", tags=["CV Matching"])


# ===== MODÈLES PYDANTIC =====

class JobOfferCreate(BaseModel):
    """Modèle pour créer une offre d'emploi"""
    title: str = Field(..., min_length=3, max_length=255)
    description: str = Field(..., min_length=10)
    category: Optional[str] = Field(None, max_length=100)
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    required_education: List[str] = Field(default_factory=list)
    required_experience_years: Optional[float] = None
    location: Optional[str] = None
    salary_range: Optional[str] = None
    contract_type: Optional[str] = None
    department: Optional[str] = None


class JobOfferUpdate(BaseModel):
    """Modèle pour mettre à jour une offre"""
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    required_skills: Optional[List[str]] = None
    preferred_skills: Optional[List[str]] = None
    required_education: Optional[List[str]] = None
    required_experience_years: Optional[float] = None
    location: Optional[str] = None
    salary_range: Optional[str] = None
    contract_type: Optional[str] = None
    department: Optional[str] = None
    is_active: Optional[bool] = None


class JobOfferResponse(BaseModel):
    """Réponse avec une offre d'emploi"""
    id: int
    title: str
    description: str
    category: Optional[str]
    required_skills: List[str]
    preferred_skills: List[str]
    required_education: List[str]
    required_experience_years: Optional[float]
    location: Optional[str]
    salary_range: Optional[str]
    contract_type: Optional[str]
    department: Optional[str]
    is_active: bool
    created_at: Optional[str]
    updated_at: Optional[str]


class CVMatchRequest(BaseModel):
    """Requête de matching CV"""
    cv_text: Optional[str] = None
    skills: Optional[List[str]] = None
    experiences: Optional[List[str]] = None
    job_titles: Optional[List[str]] = None
    education: Optional[List[str]] = None
    years_of_experience: Optional[float] = None


class CVMatchResponse(BaseModel):
    """Réponse de matching CV"""
    success: bool
    job_offer_id: int
    job_title: str
    overall_score: float
    skills_score: float
    experience_score: float
    category_match_score: float
    education_score: float
    matching_skills: List[str]
    missing_required_skills: List[str]
    missing_preferred_skills: List[str]
    recommendations: List[str]
    predicted_category: Optional[str]
    job_category: Optional[str]


class BulkMatchResponse(BaseModel):
    """Réponse de matching multiple"""
    success: bool
    total_jobs: int
    matches: List[CVMatchResponse]
    best_match: Optional[CVMatchResponse]


# ===== ENDPOINTS OFFRES D'EMPLOI =====

@router.post("/jobs", response_model=JobOfferResponse, status_code=201)
async def create_job_offer(
    job: JobOfferCreate,
    db: Session = Depends(get_db)
):
    """
    Créer une nouvelle offre d'emploi
    """
    try:
        db_job = JobOfferModel(
            title=job.title,
            description=job.description,
            category=job.category,
            required_skills=job.required_skills,
            preferred_skills=job.preferred_skills,
            required_education=job.required_education,
            required_experience_years=job.required_experience_years,
            location=job.location,
            salary_range=job.salary_range,
            contract_type=job.contract_type,
            department=job.department
        )
        
        db.add(db_job)
        db.commit()
        db.refresh(db_job)
        
        return JobOfferResponse(**db_job.to_dict())
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur création offre: {str(e)}")


@router.get("/jobs", response_model=List[JobOfferResponse])
async def list_job_offers(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Lister les offres d'emploi avec filtres
    """
    query = db.query(JobOfferModel)
    
    if active_only:
        query = query.filter(JobOfferModel.is_active == True)
    
    if category:
        query = query.filter(JobOfferModel.category == category)
    
    jobs = query.offset(skip).limit(limit).all()
    
    return [JobOfferResponse(**job.to_dict()) for job in jobs]


@router.get("/jobs/{job_id}", response_model=JobOfferResponse)
async def get_job_offer(
    job_id: int,
    db: Session = Depends(get_db)
):
    """
    Récupérer une offre d'emploi par ID
    """
    job = db.query(JobOfferModel).filter(JobOfferModel.id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Offre non trouvée")
    
    return JobOfferResponse(**job.to_dict())


@router.put("/jobs/{job_id}", response_model=JobOfferResponse)
async def update_job_offer(
    job_id: int,
    job_update: JobOfferUpdate,
    db: Session = Depends(get_db)
):
    """
    Mettre à jour une offre d'emploi
    """
    db_job = db.query(JobOfferModel).filter(JobOfferModel.id == job_id).first()
    
    if not db_job:
        raise HTTPException(status_code=404, detail="Offre non trouvée")
    
    # Mettre à jour les champs fournis
    update_data = job_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_job, field, value)
    
    try:
        db.commit()
        db.refresh(db_job)
        return JobOfferResponse(**db_job.to_dict())
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur mise à jour: {str(e)}")


@router.delete("/jobs/{job_id}")
async def delete_job_offer(
    job_id: int,
    db: Session = Depends(get_db)
):
    """
    Supprimer (désactiver) une offre d'emploi
    """
    db_job = db.query(JobOfferModel).filter(JobOfferModel.id == job_id).first()
    
    if not db_job:
        raise HTTPException(status_code=404, detail="Offre non trouvée")
    
    db_job.is_active = False
    db.commit()
    
    return {"success": True, "message": "Offre désactivée"}


@router.get("/categories")
async def get_categories():
    """
    Récupérer la liste des catégories disponibles depuis le ML Microservice
    """
    try:
        ml_client = get_ml_client(ML_SERVICE_URL)
        result = await ml_client.get_categories()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ML Service error: {str(e)}")


# ===== ENDPOINTS MATCHING =====

@router.post("/match/{job_id}", response_model=CVMatchResponse)
async def match_cv_to_job(
    job_id: int,
    cv_request: CVMatchRequest,
    db: Session = Depends(get_db)
):
    """
    Matcher un CV contre une offre d'emploi spécifique
    API Gateway: Récupère l'offre de la DB et délègue le matching au ML Service
    """
    # Récupérer l'offre depuis la DB
    db_job = db.query(JobOfferModel).filter(JobOfferModel.id == job_id).first()
    if not db_job:
        raise HTTPException(status_code=404, detail="Offre non trouvée")
    
    # Préparer les données pour le ML Service
    cv_data = {
        "cv_text": cv_request.cv_text,
        "skills": cv_request.skills or [],
        "experiences": cv_request.experiences or [],
        "job_titles": cv_request.job_titles or [],
        "education": cv_request.education or [],
        "years_of_experience": cv_request.years_of_experience
    }
    
    job_data = {
        "title": db_job.title,
        "description": db_job.description,
        "category": db_job.category,
        "required_skills": db_job.required_skills or [],
        "preferred_skills": db_job.preferred_skills or [],
        "required_education": db_job.required_education or [],
        "required_experience_years": db_job.required_experience_years
    }
    
    # Appeler le ML Service
    try:
        ml_client = get_ml_client(ML_SERVICE_URL)
        ml_result = await ml_client.match_cv(cv_data, job_data)
        
        if not ml_result.get("success"):
            raise HTTPException(status_code=500, detail="ML matching failed")
        
        result_data = ml_result["result"]
        
        return CVMatchResponse(
            success=True,
            job_offer_id=job_id,
            job_title=db_job.title,
            overall_score=result_data["overall_score"],
            skills_score=result_data["skills_score"],
            experience_score=result_data["experience_score"],
            category_match_score=result_data["category_match_score"],
            education_score=result_data["education_score"],
            matching_skills=result_data["matching_skills"],
            missing_required_skills=result_data["missing_required_skills"],
            missing_preferred_skills=result_data["missing_preferred_skills"],
            recommendations=result_data["recommendations"],
            predicted_category=result_data["predicted_category"],
            job_category=result_data.get("job_category")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ML Service error: {str(e)}")


@router.post("/match-all", response_model=BulkMatchResponse)
async def match_cv_to_all_jobs(
    cv_request: CVMatchRequest,
    limit: int = 10,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Matcher un CV contre toutes les offres actives et retourner les meilleures correspondances
    API Gateway: Récupère les offres de la DB et délègue chaque matching au ML Service
    """
    # Récupérer les offres actives depuis la DB
    query = db.query(JobOfferModel).filter(JobOfferModel.is_active == True)
    
    if category:
        query = query.filter(JobOfferModel.category == category)
    
    jobs = query.all()
    
    if not jobs:
        return BulkMatchResponse(
            success=True,
            total_jobs=0,
            matches=[],
            best_match=None
        )
    
    # Préparer les données CV pour le ML Service
    cv_data = {
        "cv_text": cv_request.cv_text,
        "skills": cv_request.skills or [],
        "experiences": cv_request.experiences or [],
        "job_titles": cv_request.job_titles or [],
        "education": cv_request.education or [],
        "years_of_experience": cv_request.years_of_experience
    }
    
    # Matcher contre chaque offre via ML Service
    ml_client = get_ml_client(ML_SERVICE_URL)
    matches = []
    
    for db_job in jobs:
        try:
            job_data = {
                "title": db_job.title,
                "description": db_job.description,
                "category": db_job.category,
                "required_skills": db_job.required_skills or [],
                "preferred_skills": db_job.preferred_skills or [],
                "required_education": db_job.required_education or [],
                "required_experience_years": db_job.required_experience_years
            }
            
            ml_result = await ml_client.match_cv(cv_data, job_data)
            
            if ml_result.get("success"):
                result_data = ml_result["result"]
                matches.append(CVMatchResponse(
                    success=True,
                    job_offer_id=db_job.id,
                    job_title=db_job.title,
                    overall_score=result_data["overall_score"],
                    skills_score=result_data["skills_score"],
                    experience_score=result_data["experience_score"],
                    category_match_score=result_data["category_match_score"],
                    education_score=result_data["education_score"],
                    matching_skills=result_data["matching_skills"],
                    missing_required_skills=result_data["missing_required_skills"],
                    missing_preferred_skills=result_data["missing_preferred_skills"],
                    recommendations=result_data["recommendations"],
                    predicted_category=result_data["predicted_category"],
                    job_category=result_data.get("job_category")
                ))
            
        except Exception as e:
            print(f"ML Service error for job {db_job.id}: {e}")
            continue
    
    # Trier par score
    matches.sort(key=lambda x: x.overall_score, reverse=True)
    
    # Limiter les résultats
    top_matches = matches[:limit]
    best_match = top_matches[0] if top_matches else None
    
    return BulkMatchResponse(
        success=True,
        total_jobs=len(jobs),
        matches=top_matches,
        best_match=best_match
    )


@router.post("/upload-and-match/{job_id}")
async def upload_cv_and_match(
    job_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload un CV (PDF/DOCX) et le matcher contre une offre
    API Gateway: Délègue le parsing au ML Service
    """
    try:
        # Parser le CV via ML Service
        content = await file.read()
        ml_client = get_ml_client(ML_SERVICE_URL)
        parse_result = await ml_client.parse_cv(content, file.filename)
        
        if not parse_result.get("success"):
            raise HTTPException(status_code=400, detail="CV parsing failed")
        
        cv_data_dict = parse_result["data"]
        
        # Construire la requête
        cv_request = CVMatchRequest(
            cv_text=cv_data_dict.get("full_text"),
            skills=cv_data_dict.get("skills", []),
            experiences=cv_data_dict.get("experiences", []),
            job_titles=cv_data_dict.get("job_titles", []),
            education=cv_data_dict.get("education", []),
            years_of_experience=cv_data_dict.get("years_of_experience")
        )
        
        # Matcher (utilise l'endpoint déjà modifié)
        return await match_cv_to_job(job_id, cv_request, db)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ML Service error: {str(e)}")