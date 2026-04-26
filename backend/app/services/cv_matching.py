

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict
import re
import numpy as np
import joblib
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity
import logging

logger = logging.getLogger(__name__)


@dataclass
class CVData:
    """Structure pour les données d'un CV"""
    skills: List[str]
    experiences: List[str]
    job_titles: List[str]
    education: List[str]
    years_of_experience: Optional[float] = None
    full_text: Optional[str] = None


@dataclass
class JobOffer:
    """Structure pour une offre d'emploi"""
    id: Optional[int] = None
    title: str = ""
    description: str = ""  
    required_skills: List[str] = None
    preferred_skills: List[str] = None
    required_experience_years: Optional[float] = None
    required_education: List[str] = None
    category: Optional[str] = None
    location: Optional[str] = None
    salary_range: Optional[str] = None
    
    def __post_init__(self):
        if self.required_skills is None:
            self.required_skills = []
        if self.preferred_skills is None:
            self.preferred_skills = []
        if self.required_education is None:
            self.required_education = []


@dataclass
class MatchingResult:
    """Résultat du matching CV-Offre"""
    overall_score: float  # Score global de 0 à 100
    skills_score: float
    experience_score: float
    category_match_score: float
    education_score: float
    missing_required_skills: List[str]
    matching_skills: List[str]
    missing_preferred_skills: List[str]
    recommendations: List[str]
    predicted_category: Optional[str] = None
    job_category: Optional[str] = None


class CVMatcher:
    """
    Classe pour le matching CV-Offre d'emploi avec ML
    Utilise un RandomForest et TF-IDF pré-entraînés
    """
    
    def __init__(self):
        """Initialise le matcher en chargeant les modèles"""
        try:
            base_dir = Path(__file__).parent.parent.parent
            models_dir = base_dir / "ml" / "models"
            
            # Charger les modèles
            self.model = joblib.load(models_dir / "cv_matching_model.pkl")
            self.tfidf = joblib.load(models_dir / "cv_tfidf.pkl")
            self.label_encoder = joblib.load(models_dir / "cv_label_encoder.pkl")
            
            logger.info("Modèles CV matching chargés avec succès")
            logger.info(f"Catégories disponibles: {len(self.label_encoder.classes_)}")
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement des modèles: {e}")
            raise RuntimeError(f"Impossible de charger les modèles CV matching: {e}")
        
        # Poids pour le calcul du score global
        self.weights = {
            "skills": 0.35,
            "experience": 0.25,
            "category": 0.25,
            "education": 0.15
        }
    
    def normalize_text(self, text: str) -> str:
        """Normalise le texte"""
        if not text:
            return ""
        text = text.lower().strip()
        text = re.sub(r'\s+', ' ', text)
        return text
    
    def predict_cv_category(self, cv_text: str) -> Tuple[str, float]:
        """
        Prédit la catégorie professionnelle d'un CV
        
        Args:
            cv_text: Texte complet du CV
            
        Returns:
            Tuple (catégorie, probabilité)
        """
        try:
            # Vectoriser le CV
            cv_vector = self.tfidf.transform([self.normalize_text(cv_text)])
            
            # Prédiction
            prediction = self.model.predict(cv_vector)[0]
            proba = self.model.predict_proba(cv_vector)[0]
            category = self.label_encoder.inverse_transform([prediction])[0]
            confidence = float(max(proba))
            
            return category, confidence
            
        except Exception as e:
            logger.error(f"Erreur lors de la prédiction: {e}")
            return "Unknown", 0.0
    
    def compute_text_similarity(self, text1: str, text2: str) -> float:
        """
        Calcule la similarité cosinus entre deux textes avec TF-IDF
        
        Args:
            text1: Premier texte
            text2: Deuxième texte
            
        Returns:
            Score de similarité entre 0 et 1
        """
        if not text1 or not text2:
            return 0.0
        
        try:
            # Vectoriser les textes
            vectors = self.tfidf.transform([
                self.normalize_text(text1),
                self.normalize_text(text2)
            ])
            
            # Similarité cosinus
            similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
            return float(max(0.0, min(1.0, similarity)))
            
        except Exception as e:
            logger.error(f"Erreur calcul similarité: {e}")
            return 0.0
    
    def match_skills(
        self, 
        cv_skills: List[str], 
        required_skills: List[str],
        preferred_skills: List[str]
    ) -> Tuple[float, List[str], List[str], List[str]]:
        """
        Match les compétences du CV avec celles requises/préférées
        
        Returns:
            Tuple (score, matching_skills, missing_required, missing_preferred)
        """
        if not cv_skills:
            return 0.0, [], required_skills, preferred_skills
        
        cv_skills_norm = [self.normalize_text(s) for s in cv_skills]
        required_norm = [self.normalize_text(s) for s in required_skills]
        preferred_norm = [self.normalize_text(s) for s in preferred_skills]
        
        matching_required = []
        missing_required = []
        
        # Match des compétences requises
        for i, req in enumerate(required_norm):
            if any(req in cv_skill or cv_skill in req for cv_skill in cv_skills_norm):
                matching_required.append(required_skills[i])
            else:
                # Check similarité avec TF-IDF
                max_sim = 0.0
                for cv_skill in cv_skills:
                    sim = self.compute_text_similarity(cv_skill, required_skills[i])
                    if sim > max_sim:
                        max_sim = sim
                
                if max_sim >= 0.6:  # Seuil de similarité
                    matching_required.append(required_skills[i])
                else:
                    missing_required.append(required_skills[i])
        
        # Match des compétences préférées
        matching_preferred = []
        missing_preferred = []
        
        for i, pref in enumerate(preferred_norm):
            if any(pref in cv_skill or cv_skill in pref for cv_skill in cv_skills_norm):
                matching_preferred.append(preferred_skills[i])
            else:
                max_sim = max([self.compute_text_similarity(cv_skill, preferred_skills[i]) 
                              for cv_skill in cv_skills] or [0.0])
                if max_sim >= 0.6:
                    matching_preferred.append(preferred_skills[i])
                else:
                    missing_preferred.append(preferred_skills[i])
        
        # Calcul du score
        required_score = len(matching_required) / len(required_norm) if required_norm else 1.0
        preferred_score = len(matching_preferred) / len(preferred_norm) if preferred_norm else 1.0
        
        final_score = 0.75 * required_score + 0.25 * preferred_score
        all_matching = matching_required + matching_preferred
        
        return final_score, all_matching, missing_required, missing_preferred
    
    def match_experience(
        self,
        cv_text: str,
        job_description: str,
        cv_years: Optional[float],
        required_years: Optional[float]
    ) -> float:
        """Match l'expérience"""
        # Similarité sémantique
        semantic_score = self.compute_text_similarity(cv_text, job_description)
        
        # Score sur les années
        years_score = 1.0
        if cv_years is not None and required_years is not None:
            if cv_years >= required_years:
                years_score = 1.0
            else:
                years_score = max(0.0, cv_years / required_years)
        
        return 0.6 * semantic_score + 0.4 * years_score
    
    def match_category(self, predicted_category: str, job_category: Optional[str]) -> float:
        """Match la catégorie prédite avec la catégorie du job"""
        if not job_category:
            return 0.5  # Neutre si pas de catégorie
        
        # Match exact
        if predicted_category.lower() == job_category.lower():
            return 1.0
        
        # Similarité textuelle
        return self.compute_text_similarity(predicted_category, job_category)
    
    def match_education(
        self,
        cv_education: List[str],
        required_education: List[str]
    ) -> float:
        """Match l'éducation avec détection intelligente des niveaux"""
        if not required_education:
            return 1.0
        
        if not cv_education:
            return 0.0
        
        # Niveaux d'éducation avec scores
        education_levels = {
            "doctorat": 6, "phd": 6, "doctorate": 6,
            "master": 5, "m2": 5, "diplôme d'ingénieur": 5, "ingénieur": 5, "engineer": 5,
            "m1": 4, "maîtrise": 4,
            "licence": 3, "bachelor": 3, "l3": 3,
            "l2": 2,
            "bac+2": 2, "dut": 2, "bts": 2,
            "bac": 1, "baccalauréat": 1
        }
        
        def extract_level(edu_text: str) -> int:
            """Extrait le niveau d'éducation le plus élevé"""
            edu_lower = edu_text.lower()
            max_level = 0
            for keyword, level in education_levels.items():
                if keyword in edu_lower:
                    max_level = max(max_level, level)
            return max_level
        
        # Niveau du CV et requis
        cv_level = max([extract_level(edu) for edu in cv_education] or [0])
        required_level = max([extract_level(edu) for edu in required_education] or [0])
        
        # Si aucun niveau détecté, utiliser la similarité textuelle
        if cv_level == 0 or required_level == 0:
            cv_edu_text = " ".join(cv_education)
            req_edu_text = " ".join(required_education)
            return self.compute_text_similarity(cv_edu_text, req_edu_text)
        
        # Scoring basé sur le niveau
        if cv_level >= required_level:
            # Niveau suffisant ou supérieur
            return 1.0
        elif cv_level == required_level - 1:
            # Niveau juste en dessous (ex: Licence vs Master)
            return 0.7
        elif cv_level == required_level - 2:
            # Deux niveaux en dessous
            return 0.4
        else:
            # Trop bas
            return 0.2
    
    def generate_recommendations(
        self,
        matching_result: 'MatchingResult'
    ) -> List[str]:
        """Génère des recommandations"""
        recommendations = []
        
        if matching_result.missing_required_skills:
            skills_str = ", ".join(matching_result.missing_required_skills[:3])
            recommendations.append(
                f"❗ Développer les compétences requises: {skills_str}"
            )
        
        if matching_result.overall_score >= 75:
            recommendations.append(
                "✅ Excellent profil! Postulez avec confiance"
            )
        elif matching_result.overall_score >= 50:
            recommendations.append(
                "💡 Bon profil. Mettez en avant vos points forts"
            )
        else:
            recommendations.append(
                "⚠️ Profil en développement. Acquérir plus d'expérience"
            )
        
        if matching_result.category_match_score < 0.5:
            recommendations.append(
                f"🎯 Catégorie prédite: {matching_result.predicted_category}. "
                f"Considérez des postes dans ce domaine"
            )
        
        if matching_result.missing_preferred_skills:
            skills_str = ", ".join(matching_result.missing_preferred_skills[:2])
            recommendations.append(
                f"💪 Pour se démarquer: {skills_str}"
            )
        
        return recommendations
    
    def match(self, cv: CVData, job: JobOffer) -> MatchingResult:
        """
        Effectue le matching complet entre un CV et une offre
        
        Args:
            cv: Données du CV
            job: Offre d'emploi
            
        Returns:
            Résultat complet du matching
        """
        try:
            # Construire le texte complet du CV
            if not cv.full_text:
                cv_text_parts = []
                if cv.skills:
                    cv_text_parts.append(" ".join(cv.skills))
                if cv.experiences:
                    cv_text_parts.append(" ".join(cv.experiences))
                if cv.job_titles:
                    cv_text_parts.append(" ".join(cv.job_titles))
                if cv.education:
                    cv_text_parts.append(" ".join(cv.education))
                cv_text = " ".join(cv_text_parts)
            else:
                cv_text = cv.full_text
            
            # 1. Prédire la catégorie du CV
            predicted_category, confidence = self.predict_cv_category(cv_text)
            logger.info(f"Catégorie prédite: {predicted_category} (confiance: {confidence:.2%})")
            
            # 2. Match des compétences
            skills_score, matching_skills, missing_required, missing_preferred = self.match_skills(
                cv.skills or [],
                job.required_skills or [],
                job.preferred_skills or []
            )
            
            # 3. Match de l'expérience
            experience_score = self.match_experience(
                cv_text,
                job.description,
                cv.years_of_experience,
                job.required_experience_years
            )
            
            # 4. Match de la catégorie
            category_score = self.match_category(predicted_category, job.category)
            
            # 5. Match de l'éducation
            education_score = self.match_education(
                 cv.education or [],
                job.required_education or []
            )
            
            # 6. Score global pondéré
            overall_score = (
                self.weights["skills"] * skills_score +
                self.weights["experience"] * experience_score +
                self.weights["category"] * category_score +
                self.weights["education"] * education_score
            ) * 100  # Convert to percentage
            
            # 7. Créer le résultat
            result = MatchingResult(
                overall_score=round(overall_score, 1),
                skills_score=round(skills_score * 100, 1),
                experience_score=round(experience_score * 100, 1),
                category_match_score=round(category_score * 100, 1),
                education_score=round(education_score * 100, 1),
                missing_required_skills=missing_required,
                matching_skills=matching_skills,
                missing_preferred_skills=missing_preferred,
                recommendations=[],
                predicted_category=predicted_category,
                job_category=job.category
            )
            
            # 8. Générer les recommandations
            result.recommendations = self.generate_recommendations(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur lors du matching: {e}")
            raise


# Instance globale du matcher (singleton)
_matcher_instance = None

def get_cv_matcher() -> CVMatcher:
    """Retourne l'instance singleton du CV matcher"""
    global _matcher_instance
    if _matcher_instance is None:
        _matcher_instance = CVMatcher()
    return _matcher_instance
