"""
Routes CV Ranking - Sans dépendances DB
Même pattern que cv_matching.py du ML Service
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import asyncio
import logging

from app.services.cv_matching import get_cv_matcher, CVData, JobOffer
from app.services.cv_parser import CVParser

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/cv-ranking", tags=["CV Ranking"])


# ===== MODÈLES PYDANTIC =====

class JobRequest(BaseModel):
    title: str
    description: str
    category: Optional[str] = None
    required_skills: List[str] = []
    preferred_skills: List[str] = []
    required_education: List[str] = []
    required_experience_years: Optional[float] = None


class RankRequest(BaseModel):
    job: JobRequest


class RankedCV(BaseModel):
    rank: int
    filename: str
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


class CVRankingResponse(BaseModel):
    success: bool
    total_uploaded: int
    total_ranked: int
    failed_files: List[str]
    ranked_cvs: List[RankedCV]
    best_cv: Optional[RankedCV]


# ===== ENDPOINT =====

@router.post("/rank", response_model=CVRankingResponse)
async def rank_cvs(
    files: List[UploadFile] = File(...),
    title: str = "",
    description: str = "",
    category: Optional[str] = None,
    required_skills: str = "[]",
    preferred_skills: str = "[]",
    required_education: str = "[]",
    required_experience_years: Optional[float] = None,
):
    """
    Upload plusieurs CVs et les ranker contre une offre.
    Les données de l'offre sont passées en form fields.
    """
    import json

    if len(files) > 50:
        raise HTTPException(status_code=400, detail="Maximum 50 CVs par requête")

    # Construire l'objet JobOffer (même pattern que /match)
    job_offer = JobOffer(
        title=title,
        description=description,
        category=category,
        required_skills=json.loads(required_skills),
        preferred_skills=json.loads(preferred_skills),
        required_education=json.loads(required_education),
        required_experience_years=required_experience_years,
    )

    parser = CVParser()
    matcher = get_cv_matcher()

    ranked_list = []
    failed_files = []

    for f in files:
        try:
            content = await f.read()

            # Parser le CV (même appel que /parse-cv)
            parse_result = parser.parse_cv(f.filename, content)
            if not parse_result.get("success"):
                failed_files.append(f.filename)
                continue

            data = parse_result["data"]

            # Construire CVData (même pattern que /match)
            cv_data = CVData(
                skills=data.get("skills", []),
                experiences=data.get("experiences", []),
                job_titles=data.get("job_titles", []),
                education=data.get("education", []),
                years_of_experience=data.get("years_of_experience"),
                full_text=data.get("full_text", ""),
            )

            # Scorer (même appel que /match)
            result = matcher.match(cv_data, job_offer)
            result_dict = result.to_dict()

            ranked_list.append({
                "filename": f.filename,
                "result": result_dict,
            })

        except Exception as e:
            logger.error(f"Erreur pour {f.filename}: {e}")
            failed_files.append(f.filename)

    # Trier par score décroissant
    ranked_list.sort(key=lambda x: x["result"]["overall_score"], reverse=True)

    ranked_cvs = [
        RankedCV(
            rank=i + 1,
            filename=item["filename"],
            overall_score=item["result"]["overall_score"],
            skills_score=item["result"]["skills_score"],
            experience_score=item["result"]["experience_score"],
            category_match_score=item["result"]["category_match_score"],
            education_score=item["result"]["education_score"],
            matching_skills=item["result"]["matching_skills"],
            missing_required_skills=item["result"]["missing_required_skills"],
            missing_preferred_skills=item["result"]["missing_preferred_skills"],
            recommendations=item["result"]["recommendations"],
            predicted_category=item["result"].get("predicted_category"),
            job_category=item["result"].get("job_category"),
        )
        for i, item in enumerate(ranked_list)
    ]

    return CVRankingResponse(
        success=True,
        total_uploaded=len(files),
        total_ranked=len(ranked_cvs),
        failed_files=failed_files,
        ranked_cvs=ranked_cvs,
        best_cv=ranked_cvs[0] if ranked_cvs else None,
    )