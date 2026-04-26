from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from pydantic import BaseModel
from typing import List, Optional
from dataclasses import asdict
import json
import logging

from app.services.cv_matching import get_cv_matcher, CVData, JobOffer
from app.services.cv_parser import CVParser

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cv-ranking", tags=["CV Ranking"])


# ================= MODELS =================

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


# ================= ROUTE =================

@router.post("/rank", response_model=CVRankingResponse)
async def rank_cvs(
    files: List[UploadFile] = File(...),
    title: str = Form(...),
    description: str = Form(...),
    category: Optional[str] = Form(None),
    required_skills: str = Form("[]"),
    preferred_skills: str = Form("[]"),
    required_education: str = Form("[]"),
    required_experience_years: float = Form(0),
):
    """
    Rank multiple CVs against a job offer
    """
    if len(files) == 0:
        raise HTTPException(status_code=400, detail="No files uploaded")

    if len(files) > 50:
        raise HTTPException(status_code=400, detail="Max 50 CVs allowed")

    parser = CVParser()
    matcher = get_cv_matcher()

    job_offer = JobOffer(
        title=title,
        description=description,
        category=category,
        required_skills=json.loads(required_skills),
        preferred_skills=json.loads(preferred_skills),
        required_education=json.loads(required_education),
        required_experience_years=required_experience_years,
    )

    results = []
    failed = []

    for f in files:
        try:
            content = await f.read()

            parsed = parser.parse_cv(f.filename, content)
            if not parsed.get("success"):
                failed.append(f.filename)
                continue

            data = parsed["data"]

            cv = CVData(
                skills=data.get("skills", []),
                experiences=data.get("experiences", []),
                job_titles=data.get("job_titles", []),
                education=data.get("education", []),
                years_of_experience=data.get("years_of_experience"),
                full_text=data.get("full_text", "")
            )

            result = asdict(matcher.match(cv, job_offer))  # ✅ corrigé

            results.append({
                "filename": f.filename,
                "result": result
            })

        except Exception as e:
            logger.error(f"Error {f.filename}: {e}")
            failed.append(f.filename)

    # Trier par score décroissant
    results.sort(key=lambda x: x["result"]["overall_score"], reverse=True)

    ranked = [
        RankedCV(
            rank=i + 1,
            filename=r["filename"],
            overall_score=r["result"]["overall_score"],
            skills_score=r["result"]["skills_score"],
            experience_score=r["result"]["experience_score"],
            category_match_score=r["result"]["category_match_score"],
            education_score=r["result"]["education_score"],
            matching_skills=r["result"]["matching_skills"],
            missing_required_skills=r["result"]["missing_required_skills"],
            missing_preferred_skills=r["result"]["missing_preferred_skills"],
            recommendations=r["result"]["recommendations"],
            predicted_category=r["result"].get("predicted_category"),
            job_category=r["result"].get("job_category"),
        )
        for i, r in enumerate(results)
    ]

    return CVRankingResponse(
        success=True,
        total_uploaded=len(files),
        total_ranked=len(ranked),
        failed_files=failed,
        ranked_cvs=ranked,
        best_cv=ranked[0] if ranked else None
    )