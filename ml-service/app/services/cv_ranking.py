from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import json
import logging

from app.services.cv_matching import get_cv_matcher, CVData, JobOffer
from app.services.cv_parser import CVParser

logger = logging.getLogger(__name__)

router = APIRouter(tags=["CV Ranking"])


@router.post("/cv-ranking/rank")
async def rank_cvs(
    files: List[UploadFile] = File(...),
    title: str = "",
    description: str = "",
    category: str = None,
    required_skills: str = "[]",
    preferred_skills: str = "[]",
    required_education: str = "[]",
    required_experience_years: float = None,
):
    if len(files) == 0:
        raise HTTPException(status_code=400, detail="Aucun CV envoyé")

    parser = CVParser()
    matcher = get_cv_matcher()

    job = JobOffer(
        title=title,
        description=description,
        category=category,
        required_skills=json.loads(required_skills),
        preferred_skills=json.loads(preferred_skills),
        required_education=json.loads(required_education),
        required_experience_years=required_experience_years,
    )

    results = []

    for f in files:
        try:
            content = await f.read()

            parsed = parser.parse_cv(f.filename, content)
            if not parsed.get("success"):
                continue

            data = parsed["data"]

            cv = CVData(
                skills=data.get("skills", []),
                experiences=data.get("experiences", []),
                job_titles=data.get("job_titles", []),
                education=data.get("education", []),
                years_of_experience=data.get("years_of_experience"),
                full_text=data.get("full_text", ""),
            )

            match = matcher.match(cv, job).to_dict()

            results.append({
                "filename": f.filename,
                "score": match["overall_score"],
                "skills_score": match["skills_score"],
                "experience_score": match["experience_score"],
                "education_score": match["education_score"],
                "category_score": match["category_match_score"],
                "matching_skills": match["matching_skills"],
                "missing_skills": match["missing_required_skills"],
                "recommendations": match["recommendations"],
            })

        except Exception as e:
            logger.error(f"CV error {f.filename}: {e}")

    # 🔥 RANKING SIMPLE (LE CŒUR DU FEATURE)
    results.sort(key=lambda x: x["score"], reverse=True)

    return {
        "success": True,
        "total": len(results),
        "best_cv": results[0] if results else None,
        "ranked_cvs": results
    }