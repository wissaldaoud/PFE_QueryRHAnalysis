"""
Module de recommandation de formation avec NLP
Utilise des embeddings sémantiques pour recommander les meilleures formations
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

# Import conditionnel de numpy
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    logger.warning("⚠️ NumPy non disponible")

# Import conditionnel de SentenceTransformers
try:
    from sentence_transformers import SentenceTransformer, util
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    logger.warning("⚠️ SentenceTransformers non disponible dans training_recommendation, utilisation du fallback")
    SENTENCE_TRANSFORMERS_AVAILABLE = False


@dataclass
class EmployeeProfile:
    """Profil d'un employé pour la recommandation de formation"""
    employee_id: str
    current_skills: List[str]
    training_history: List[str]  # Formations déjà suivies
    current_position: str
    target_position: Optional[str] = None
    interests: Optional[List[str]] = None
    department: Optional[str] = None


@dataclass
class TrainingCourse:
    """Représentation d'une formation"""
    course_id: str
    title: str
    description: str
    skills_taught: List[str]
    level: str  # "débutant", "intermédiaire", "avancé"
    duration_hours: float
    category: str
    prerequisites: Optional[List[str]] = None


@dataclass
class TrainingRecommendation:
    """Recommandation de formation avec score"""
    course: TrainingCourse
    relevance_score: float  # Score de pertinence 0-1
    skill_gap_addressed: List[str]  # Compétences manquantes comblées
    reasoning: str  # Explication de la recommandation
    priority: str  # "haute", "moyenne", "basse"


class TrainingRecommender:
    """
    Système de recommandation de formation basé sur NLP
    Utilise des embeddings pour matcher profils et formations
    """
    
    def __init__(self, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"):
        """
        Initialise le recommandeur avec un modèle Sentence Transformer
        
        Args:
            model_name: Nom du modèle à utiliser
        """
        try:
            if SENTENCE_TRANSFORMERS_AVAILABLE:
                self.model = SentenceTransformer(model_name)
                logger.info(f"Modèle {model_name} chargé pour recommandation de formation")
            else:
                self.model = None
                logger.warning("⚠️ SentenceTransformer non disponible, utilisation du fallback basique")
        except Exception as e:
            logger.error(f"Erreur lors du chargement du modèle: {e}")
            self.model = None
    
    def _safe_encode(self, texts: List[str], convert_to_tensor: bool = True):
        """Encode les textes de manière sécurisée, retourne un fallback si modèle non disponible"""
        if self.model and SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                return self.model.encode(texts, convert_to_tensor=convert_to_tensor)
            except Exception as e:
                logger.warning(f"Erreur lors de l'encoding: {e}")
                return [] if not NUMPY_AVAILABLE else np.array([])
        else:
            # Fallback: retourner un array vide
            return [] if not NUMPY_AVAILABLE else np.array([])
    
    def compute_skill_gap(
        self,
        current_skills: List[str],
        target_position: str,
        required_skills_map: Dict[str, List[str]]
    ) -> List[str]:
        """
        Calcule les compétences manquantes pour atteindre un poste cible
        
        Args:
            current_skills: Compétences actuelles de l'employé
            target_position: Poste visé
            required_skills_map: Mapping poste -> compétences requises
            
        Returns:
            Liste des compétences manquantes
        """
        # Si le modèle n'est pas disponible, retourner toutes les compétences requises comme manquantes
        if not self.model or not SENTENCE_TRANSFORMERS_AVAILABLE:
            if not target_position or target_position not in required_skills_map:
                return []
            return required_skills_map.get(target_position, [])
        
        if not target_position or target_position not in required_skills_map:
            return []
        
        required_skills = required_skills_map.get(target_position, [])
        current_skills_lower = [s.lower() for s in current_skills]
        
        # Utiliser les embeddings pour identifier les compétences manquantes
        skill_gap = []
        
        if not current_skills:
            return required_skills
        
        try:
            current_embeddings = self.model.encode(current_skills_lower, convert_to_tensor=True)
            
            for req_skill in required_skills:
                req_embedding = self.model.encode([req_skill.lower()], convert_to_tensor=True)
                similarities = util.cos_sim(req_embedding, current_embeddings)
                max_sim = float(similarities.max())
                
                # Seuil de 0.75 pour considérer qu'une compétence est acquise
                if max_sim < 0.75:
                    skill_gap.append(req_skill)
            
            return skill_gap
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul du skill gap: {e}")
            return []
    
    def compute_relevance_score(
        self,
        employee: EmployeeProfile,
        course: TrainingCourse,
        skill_gap: List[str]
    ) -> Tuple[float, List[str], str]:
        """
        Calcule le score de pertinence d'une formation pour un employé
        
        Args:
            employee: Profil de l'employé
            course: Formation à évaluer
            skill_gap: Compétences manquantes identifiées
            
        Returns:
            Tuple (score, compétences_comblées, raisonnement)
        """
        # Si le modèle n'est pas disponible, retourner un score basique
        if not self.model or not SENTENCE_TRANSFORMERS_AVAILABLE:
            logger.warning("Modèle non disponible, retour d'un score basique")
            return (0.5, [], "Score basique (modèle ML non disponible)")
        
        scores = []
        skill_gap_addressed = []
        reasoning_parts = []
        
        # 1. Score basé sur le skill gap (40%)
        skill_gap_score = 0.0
        if skill_gap and course.skills_taught:
            try:
                gap_embeddings = self.model.encode(
                    [s.lower() for s in skill_gap],
                    convert_to_tensor=True
                )
                course_embeddings = self.model.encode(
                    [s.lower() for s in course.skills_taught],
                    convert_to_tensor=True
                )
                
                similarities = util.cos_sim(gap_embeddings, course_embeddings)
                
                for i, gap_skill in enumerate(skill_gap):
                    max_sim = float(similarities[i].max())
                    if max_sim >= 0.7:
                        skill_gap_addressed.append(gap_skill)
                        skill_gap_score += max_sim
                
                if len(skill_gap) > 0:
                    skill_gap_score = skill_gap_score / len(skill_gap)
                
                if skill_gap_addressed:
                    reasoning_parts.append(
                        f"Comble {len(skill_gap_addressed)} compétence(s) manquante(s)"
                    )
                    
            except Exception as e:
                logger.error(f"Erreur calcul skill gap score: {e}")
                skill_gap_score = 0.0
        
        scores.append(("skill_gap", 0.40, skill_gap_score))
        
        # 2. Score basé sur l'alignement avec le poste actuel/cible (30%)
        position_score = 0.0
        positions_to_check = [employee.current_position]
        if employee.target_position:
            positions_to_check.append(employee.target_position)
        
        try:
            position_text = " ".join(positions_to_check)
            course_text = f"{course.title} {course.description}"
            
            position_embedding = self.model.encode([position_text.lower()], convert_to_tensor=True)
            course_embedding = self.model.encode([course_text.lower()], convert_to_tensor=True)
            
            position_score = float(util.cos_sim(position_embedding, course_embedding)[0][0])
            
            if position_score > 0.6:
                reasoning_parts.append("Alignée avec le poste actuel/cible")
                
        except Exception as e:
            logger.error(f"Erreur calcul position score: {e}")
        
        scores.append(("position", 0.30, position_score))
        
        # 3. Score basé sur les intérêts de l'employé (15%)
        interest_score = 0.0
        if employee.interests and course.category:
            try:
                interest_embeddings = self.model.encode(
                    [i.lower() for i in employee.interests],
                    convert_to_tensor=True
                )
                category_embedding = self.model.encode(
                    [course.category.lower()],
                    convert_to_tensor=True
                )
                
                similarities = util.cos_sim(interest_embeddings, category_embedding)
                interest_score = float(similarities.max())
                
                if interest_score > 0.6:
                    reasoning_parts.append("Correspond aux centres d'intérêt")
                    
            except Exception as e:
                logger.error(f"Erreur calcul interest score: {e}")
        
        scores.append(("interest", 0.15, interest_score))
        
        # 4. Pénalité si formation déjà suivie (15%)
        novelty_score = 1.0
        if course.title in employee.training_history:
            novelty_score = 0.0
            reasoning_parts.append("⚠ Formation déjà suivie")
        elif any(
            self.model.encode([course.title.lower()], convert_to_tensor=True)
            .cpu().numpy() @ 
            self.model.encode([h.lower()], convert_to_tensor=True)
            .cpu().numpy().T > 0.85
            for h in employee.training_history
        ):
            novelty_score = 0.3
            reasoning_parts.append("Formation similaire déjà suivie")
        
        scores.append(("novelty", 0.15, novelty_score))
        
        # Calcul du score final pondéré
        final_score = sum(weight * score for _, weight, score in scores)
        
        # Génération du raisonnement
        if not reasoning_parts:
            reasoning_parts.append("Formation peu adaptée au profil")
        
        reasoning = " | ".join(reasoning_parts)
        
        return round(final_score, 3), skill_gap_addressed, reasoning
    
    def determine_priority(self, score: float, skill_gap_addressed: List[str]) -> str:
        """
        Détermine la priorité d'une recommandation
        
        Args:
            score: Score de pertinence
            skill_gap_addressed: Compétences manquantes comblées
            
        Returns:
            "haute", "moyenne", ou "basse"
        """
        if score >= 0.7 and len(skill_gap_addressed) >= 2:
            return "haute"
        elif score >= 0.5 or len(skill_gap_addressed) >= 1:
            return "moyenne"
        else:
            return "basse"
    
    def recommend_trainings(
        self,
        employee: EmployeeProfile,
        available_courses: List[TrainingCourse],
        required_skills_map: Dict[str, List[str]] = None,
        top_n: int = 5
    ) -> List[TrainingRecommendation]:
        """
        Recommande les meilleures formations pour un employé
        
        Args:
            employee: Profil de l'employé
            available_courses: Liste des formations disponibles
            required_skills_map: Mapping poste -> compétences requises
            top_n: Nombre de recommandations à retourner
            
        Returns:
            Liste des top N recommandations triées par pertinence
            
        Raises:
            ValueError: Si les paramètres sont invalides
        """
        if not isinstance(employee, EmployeeProfile):
            raise ValueError("employee doit être une instance de EmployeeProfile")
        
        if not available_courses:
            logger.warning("Aucune formation disponible pour recommandation")
            return []
        
        # Calcul du skill gap si poste cible spécifié
        skill_gap = []
        if employee.target_position and required_skills_map:
            skill_gap = self.compute_skill_gap(
                employee.current_skills,
                employee.target_position,
                required_skills_map
            )
            logger.info(f"Skill gap identifié: {skill_gap}")
        
        # Calcul des scores pour chaque formation
        recommendations = []
        
        for course in available_courses:
            try:
                score, skills_addressed, reasoning = self.compute_relevance_score(
                    employee,
                    course,
                    skill_gap
                )
                
                priority = self.determine_priority(score, skills_addressed)
                
                recommendation = TrainingRecommendation(
                    course=course,
                    relevance_score=score,
                    skill_gap_addressed=skills_addressed,
                    reasoning=reasoning,
                    priority=priority
                )
                
                recommendations.append(recommendation)
                
            except Exception as e:
                logger.error(f"Erreur lors de l'évaluation de la formation {course.course_id}: {e}")
                continue
        
        # Tri par score décroissant
        recommendations.sort(key=lambda x: x.relevance_score, reverse=True)
        
        # Retour du top N
        return recommendations[:top_n]
    
    def explain_recommendation(self, recommendation: TrainingRecommendation) -> str:
        """
        Génère une explication détaillée d'une recommandation
        
        Args:
            recommendation: La recommandation à expliquer
            
        Returns:
            Texte d'explication formaté
        """
        course = recommendation.course
        explanation = f"""
📚 Formation recommandée : {course.title}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Score de pertinence : {recommendation.relevance_score:.1%}
🎯 Priorité : {recommendation.priority.upper()}

📝 Description : {course.description}

🎓 Compétences enseignées :
{chr(10).join(f'  • {skill}' for skill in course.skills_taught)}

✅ Compétences manquantes comblées :
{chr(10).join(f'  • {skill}' for skill in recommendation.skill_gap_addressed) if recommendation.skill_gap_addressed else '  Aucune compétence manquante spécifique'}

💡 Justification : {recommendation.reasoning}

⏱️  Durée : {course.duration_hours}h | Niveau : {course.level}
"""
        return explanation
