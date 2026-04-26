"""
Routes ML pures - Sans dépendances DB
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import logging

from app.services.cv_matching import get_cv_matcher, CVData, JobOffer
from app.services.cv_parser import CVParser

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/cv-matching", tags=["CV Matching"])

class CVRequest(BaseModel):
    cv_text: Optional[str] = None
    skills: Optional[List[str]] = None
    experiences: Optional[List[str]] = None
    job_titles: Optional[List[str]] = None
    education: Optional[List[str]] = None
    years_of_experience: Optional[float] = None

class JobRequest(BaseModel):
    title: str
    description: str
    category: Optional[str] = None
    required_skills: List[str] = []
    preferred_skills: List[str] = []
    required_education: List[str] = []
    required_experience_years: Optional[float] = None

@router.get("/categories")
async def get_categories():
    try:
        matcher = get_cv_matcher()
        categories = matcher.get_categories()
        return {"success": True, "total": len(categories), "categories": categories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class MatchRequest(BaseModel):
    cv: CVRequest
    job: JobRequest

@router.post("/match")
async def match_cv(request: MatchRequest):
    try:
        matcher = get_cv_matcher()
        cv = request.cv
        job = request.job
        cv_data = CVData(
            skills=cv.skills or [],
            experiences=cv.experiences or [],
            job_titles=cv.job_titles or [],
            education=cv.education or [],
            years_of_experience=cv.years_of_experience,
            full_text=cv.cv_text or ""
        )
        job_offer = JobOffer(
            title=job.title,
            description=job.description,
            category=job.category,
            required_skills=job.required_skills,
            preferred_skills=job.preferred_skills,
            required_education=job.required_education,
            required_experience_years=job.required_experience_years
        )
        result = matcher.match(cv_data, job_offer)
        return {"success": True, "result": result.to_dict()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/parse-cv")
async def parse_cv(file: UploadFile = File(...)):
    try:
        content = await file.read()
        parser = CVParser()
        result = parser.parse_cv(file.filename, content)
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error"))
        return {"success": True, "data": result["data"], "text_length": len(result["text"])}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
