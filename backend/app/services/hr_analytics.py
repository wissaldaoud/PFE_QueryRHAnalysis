"""
Service principal HR Analytics
Orchestre les différents modules d'analytics RH avancés
"""

from typing import List, Dict, Optional
import logging
from .cv_matching import CVMatcher, CVData, JobOffer, MatchingResult
from .training_recommendation import (
    TrainingRecommender,
    EmployeeProfile,
    TrainingCourse,
    TrainingRecommendation
)
from .predictive_scoring import (
    PredictiveScorer,
    EmployeeHistory,
    PredictiveScore
)

logger = logging.getLogger(__name__)


class HRAnalyticsService:
    """
    Service principal pour les fonctionnalités HR Analytics avancées
    
    Fonctionnalités :
    - CV Matching avec NLP
    - Recommandation de formation personnalisée
    - Scoring prédictif (churn, performance, engagement)
    """
    
    def __init__(
        self,
        model_name: str = "paraphrase-multilingual-MiniLM-L12-v2",
        enable_cv_matching: bool = True,
        enable_training_recommendation: bool = True,
        enable_predictive_scoring: bool = True
    ):
        """
        Initialise le service HR Analytics
        
        Args:
            model_name: Nom du modèle Sentence Transformer à utiliser
            enable_cv_matching: Activer le module CV matching
            enable_training_recommendation: Activer les recommandations de formation
            enable_predictive_scoring: Activer le scoring prédictif
        """
        self.model_name = model_name
        
        # Initialisation des modules
        self.cv_matcher = None
        self.training_recommender = None
        self.predictive_scorer = None
        
        try:
            if enable_cv_matching:
                self.cv_matcher = CVMatcher()
                logger.info("Module CV Matching initialisé")
            
            if enable_training_recommendation:
                self.training_recommender = TrainingRecommender(model_name=model_name)
                logger.info("Module Training Recommendation initialisé")
            
            if enable_predictive_scoring:
                self.predictive_scorer = PredictiveScorer()
                logger.info("Module Predictive Scoring initialisé")
            
            logger.info("HRAnalyticsService initialisé avec succès")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du service: {e}")
            raise
    
    # ==================== CV MATCHING ====================
    
    def match_cv_to_job(
        self,
        cv: CVData,
        job: JobOffer
    ) -> Optional[MatchingResult]:
        """
        Compare un CV avec une offre d'emploi
        
        Args:
            cv: Données du CV
            job: Données de l'offre d'emploi
            
        Returns:
            Résultat du matching avec scores et recommandations
            
        Raises:
            RuntimeError: Si le module CV matching n'est pas activé
        """
        if self.cv_matcher is None:
            raise RuntimeError("Module CV Matching non activé")
        
        try:
            result = self.cv_matcher.match(cv, job)
            logger.info(f"CV matching effectué avec score: {result.overall_score}")
            return result
        except Exception as e:
            logger.error(f"Erreur lors du CV matching: {e}")
            raise
    
    def batch_match_cvs(
        self,
        cvs: List[CVData],
        job: JobOffer
    ) -> List[Dict]:
        """
        Compare plusieurs CVs avec une offre d'emploi
        
        Args:
            cvs: Liste de CVs à évaluer
            job: Offre d'emploi cible
            
        Returns:
            Liste des résultats triés par score décroissant
        """
        if self.cv_matcher is None:
            raise RuntimeError("Module CV Matching non activé")
        
        results = []
        
        for i, cv in enumerate(cvs):
            try:
                match_result = self.cv_matcher.match(cv, job)
                results.append({
                    "cv_index": i,
                    "overall_score": match_result.overall_score,
                    "skills_score": match_result.skills_score,
                    "experience_score": match_result.experience_score,
                    "title_score": match_result.title_score,
                    "matching_skills": match_result.matching_skills,
                    "missing_required_skills": match_result.missing_required_skills,
                    "recommendations": match_result.recommendations
                })
            except Exception as e:
                logger.error(f"Erreur lors du matching du CV {i}: {e}")
                continue
        
        # Tri par score décroissant
        results.sort(key=lambda x: x["overall_score"], reverse=True)
        
        logger.info(f"Batch matching de {len(cvs)} CVs effectué")
        return results
    
    # ==================== TRAINING RECOMMENDATION ====================
    
    def recommend_trainings(
        self,
        employee: EmployeeProfile,
        available_courses: List[TrainingCourse],
        required_skills_map: Optional[Dict[str, List[str]]] = None,
        top_n: int = 5
    ) -> Optional[List[TrainingRecommendation]]:
        """
        Recommande des formations pour un employé
        
        Args:
            employee: Profil de l'employé
            available_courses: Formations disponibles
            required_skills_map: Mapping poste -> compétences requises
            top_n: Nombre de recommandations
            
        Returns:
            Liste de recommandations triées par pertinence
            
        Raises:
            RuntimeError: Si le module n'est pas activé
        """
        if self.training_recommender is None:
            raise RuntimeError("Module Training Recommendation non activé")
        
        try:
            recommendations = self.training_recommender.recommend_trainings(
                employee=employee,
                available_courses=available_courses,
                required_skills_map=required_skills_map,
                top_n=top_n
            )
            logger.info(f"Recommandations générées pour {employee.employee_id}")
            return recommendations
        except Exception as e:
            logger.error(f"Erreur lors de la recommandation: {e}")
            raise
    
    def batch_recommend_trainings(
        self,
        employees: List[EmployeeProfile],
        available_courses: List[TrainingCourse],
        required_skills_map: Optional[Dict[str, List[str]]] = None,
        top_n: int = 5
    ) -> Dict[str, List[TrainingRecommendation]]:
        """
        Recommande des formations pour plusieurs employés
        
        Args:
            employees: Liste de profils d'employés
            available_courses: Formations disponibles
            required_skills_map: Mapping poste -> compétences requises
            top_n: Nombre de recommandations par employé
            
        Returns:
            Dictionnaire employee_id -> recommandations
        """
        if self.training_recommender is None:
            raise RuntimeError("Module Training Recommendation non activé")
        
        results = {}
        
        for employee in employees:
            try:
                recommendations = self.training_recommender.recommend_trainings(
                    employee=employee,
                    available_courses=available_courses,
                    required_skills_map=required_skills_map,
                    top_n=top_n
                )
                results[employee.employee_id] = recommendations
            except Exception as e:
                logger.error(f"Erreur pour employé {employee.employee_id}: {e}")
                continue
        
        logger.info(f"Recommandations générées pour {len(results)} employés")
        return results
    
    def explain_recommendation(
        self,
        recommendation: TrainingRecommendation
    ) -> str:
        """
        Génère une explication détaillée d'une recommandation
        
        Args:
            recommendation: La recommandation à expliquer
            
        Returns:
            Texte d'explication formaté
        """
        if self.training_recommender is None:
            raise RuntimeError("Module Training Recommendation non activé")
        
        return self.training_recommender.explain_recommendation(recommendation)
    
    # ==================== PREDICTIVE SCORING ====================
    
    def calculate_predictive_scores(
        self,
        history: EmployeeHistory
    ) -> Optional[PredictiveScore]:
        """
        Calcule les scores prédictifs pour un employé
        
        Args:
            history: Historique RH de l'employé
            
        Returns:
            Scores prédictifs (churn, performance, engagement)
            
        Raises:
            RuntimeError: Si le module n'est pas activé
        """
        if self.predictive_scorer is None:
            raise RuntimeError("Module Predictive Scoring non activé")
        
        try:
            score = self.predictive_scorer.score(history)
            logger.info(
                f"Scoring calculé pour {history.employee_id}: "
                f"churn={score.churn_risk_score}, "
                f"performance={score.performance_score}"
            )
            return score
        except Exception as e:
            logger.error(f"Erreur lors du scoring: {e}")
            raise
    
    def batch_calculate_scores(
        self,
        histories: List[EmployeeHistory]
    ) -> List[PredictiveScore]:
        """
        Calcule les scores prédictifs pour plusieurs employés
        
        Args:
            histories: Liste d'historiques RH
            
        Returns:
            Liste de scores prédictifs
        """
        if self.predictive_scorer is None:
            raise RuntimeError("Module Predictive Scoring non activé")
        
        scores = []
        
        for history in histories:
            try:
                score = self.predictive_scorer.score(history)
                scores.append(score)
            except Exception as e:
                logger.error(f"Erreur pour employé {history.employee_id}: {e}")
                continue
        
        logger.info(f"Scores calculés pour {len(scores)} employés")
        return scores
    
    def identify_high_risk_employees(
        self,
        histories: List[EmployeeHistory],
        risk_threshold: float = 0.6
    ) -> List[PredictiveScore]:
        """
        Identifie les employés à risque élevé de départ
        
        Args:
            histories: Liste d'historiques RH
            risk_threshold: Seuil de risque (par défaut 0.6)
            
        Returns:
            Liste de scores pour employés à risque, triés par score décroissant
        """
        if self.predictive_scorer is None:
            raise RuntimeError("Module Predictive Scoring non activé")
        
        all_scores = []
        
        for history in histories:
            try:
                score = self.predictive_scorer.score(history)
                if score.churn_risk_score >= risk_threshold:
                    all_scores.append(score)
            except Exception as e:
                logger.error(f"Erreur pour employé {history.employee_id}: {e}")
                continue
        
        # Tri par risque décroissant
        all_scores.sort(key=lambda x: x.churn_risk_score, reverse=True)
        
        logger.info(
            f"{len(all_scores)} employés identifiés avec risque >= {risk_threshold}"
        )
        return all_scores
    
    def identify_top_performers(
        self,
        histories: List[EmployeeHistory],
        performance_threshold: float = 0.8
    ) -> List[PredictiveScore]:
        """
        Identifie les meilleurs performers
        
        Args:
            histories: Liste d'historiques RH
            performance_threshold: Seuil de performance (par défaut 0.8)
            
        Returns:
            Liste de scores pour top performers, triés par performance
        """
        if self.predictive_scorer is None:
            raise RuntimeError("Module Predictive Scoring non activé")
        
        top_performers = []
        
        for history in histories:
            try:
                score = self.predictive_scorer.score(history)
                if score.performance_score >= performance_threshold:
                    top_performers.append(score)
            except Exception as e:
                logger.error(f"Erreur pour employé {history.employee_id}: {e}")
                continue
        
        # Tri par performance décroissante
        top_performers.sort(key=lambda x: x.performance_score, reverse=True)
        
        logger.info(
            f"{len(top_performers)} top performers identifiés (>= {performance_threshold})"
        )
        return top_performers
    
    # ==================== ANALYTICS GLOBALES ====================
    
    def generate_workforce_analytics(
        self,
        histories: List[EmployeeHistory]
    ) -> Dict:
        """
        Génère des analytics globales sur l'ensemble des employés
        
        Args:
            histories: Liste de tous les historiques RH
            
        Returns:
            Dictionnaire avec statistiques agrégées
        """
        if self.predictive_scorer is None:
            raise RuntimeError("Module Predictive Scoring non activé")
        
        scores = self.batch_calculate_scores(histories)
        
        if not scores:
            return {}
        
        # Calculs statistiques
        churn_scores = [s.churn_risk_score for s in scores]
        performance_scores = [s.performance_score for s in scores]
        engagement_scores = [s.engagement_score for s in scores]
        
        analytics = {
            "total_employees": len(scores),
            "average_churn_risk": round(sum(churn_scores) / len(churn_scores), 3),
            "average_performance": round(sum(performance_scores) / len(performance_scores), 3),
            "average_engagement": round(sum(engagement_scores) / len(engagement_scores), 3),
            "high_risk_count": len([s for s in scores if s.churn_risk_score >= 0.6]),
            "medium_risk_count": len([s for s in scores if 0.4 <= s.churn_risk_score < 0.6]),
            "low_risk_count": len([s for s in scores if s.churn_risk_score < 0.4]),
            "top_performers_count": len([s for s in scores if s.performance_score >= 0.8]),
            "low_engagement_count": len([s for s in scores if s.engagement_score < 0.4]),
            "risk_distribution": {
                "élevé": len([s for s in scores if s.risk_level == "élevé"]),
                "moyen": len([s for s in scores if s.risk_level == "moyen"]),
                "faible": len([s for s in scores if s.risk_level == "faible"])
            }
        }
        
        logger.info("Analytics globales générées")
        return analytics
    
    def health_check(self) -> Dict[str, bool]:
        """
        Vérifie l'état de santé des modules
        
        Returns:
            Dictionnaire avec le statut de chaque module
        """
        return {
            "cv_matching": self.cv_matcher is not None,
            "training_recommendation": self.training_recommender is not None,
            "predictive_scoring": self.predictive_scorer is not None,
            "service_status": "healthy"
        }
