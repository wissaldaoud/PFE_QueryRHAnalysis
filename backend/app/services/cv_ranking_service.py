"""
Service de Ranking Multi-CV
Utilise SentenceTransformers pour classer plusieurs CVs par rapport à une offre d'emploi
"""

from typing import List, Dict, Any
from dataclasses import dataclass
import numpy as np
from sentence_transformers import SentenceTransformer, util
import logging

logger = logging.getLogger(__name__)


@dataclass
class CVCandidate:
    """Candidat avec son CV"""
    name: str
    cv_text: str
    filename: str


@dataclass
class RankedCandidate:
    """Candidat classé avec son score"""
    name: str
    filename: str
    score: float  # 0-100
    rank: int
    similarity: float  # 0-1
    matching_keywords: List[str]


class CVRankingService:
    """
    Service de classement de CVs basé sur la similarité sémantique
    Utilise SentenceTransformers (all-MiniLM-L6-v2) pour calculer la similarité
    """
    
    def __init__(self):
        """Initialise le modèle SentenceTransformer"""
        try:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("✅ Modèle SentenceTransformer chargé: all-MiniLM-L6-v2")
        except Exception as e:
            logger.error(f"❌ Erreur chargement modèle: {e}")
            raise
    
    def extract_keywords(self, text: str, job_description: str) -> List[str]:
        """
        Extrait les mots-clés correspondants entre le CV et l'offre
        """
        # Mots-clés techniques communs
        keywords = [
            'python', 'java', 'javascript', 'react', 'angular', 'vue',
            'docker', 'kubernetes', 'aws', 'azure', 'gcp',
            'machine learning', 'deep learning', 'nlp', 'ml', 'ai',
            'sql', 'postgresql', 'mongodb', 'redis',
            'fastapi', 'django', 'flask', 'spring', 'node.js',
            'git', 'ci/cd', 'devops', 'agile', 'scrum'
        ]
        
        text_lower = text.lower()
        job_lower = job_description.lower()
        
        matching = []
        for kw in keywords:
            if kw in text_lower and kw in job_lower:
                matching.append(kw)
        
        return matching[:10]  # Limiter à 10 keywords
    
    def rank_cvs(
        self, 
        candidates: List[CVCandidate], 
        job_description: str
    ) -> List[RankedCandidate]:
        """
        Classe plusieurs CVs par rapport à une description de poste
        
        Args:
            candidates: Liste des candidats avec leurs CVs
            job_description: Description du poste cible
        
        Returns:
            Liste de candidats classés par score décroissant
        """
        if not candidates:
            logger.warning("⚠️ Aucun candidat à classer")
            return []
        
        if not job_description or job_description.strip() == "":
            logger.warning("⚠️ Description de poste vide")
            return []
        
        logger.info(f"📊 Classement de {len(candidates)} CVs")
        
        # Encoder la description du poste
        job_embedding = self.model.encode(
            job_description, 
            convert_to_tensor=True
        )
        
        # Encoder tous les CVs
        cv_texts = [c.cv_text for c in candidates]
        cv_embeddings = self.model.encode(
            cv_texts, 
            convert_to_tensor=True, 
            show_progress_bar=False
        )
        
        # Calculer les similarités cosinus
        similarities = util.cos_sim(cv_embeddings, job_embedding)
        similarities = similarities.cpu().numpy().flatten()
        
        # Créer les résultats avec scores (0-100)
        results = []
        for idx, candidate in enumerate(candidates):
            similarity = float(similarities[idx])
            score = similarity * 100  # Convertir en 0-100
            
            # Extraire les mots-clés correspondants
            keywords = self.extract_keywords(candidate.cv_text, job_description)
            
            results.append(RankedCandidate(
                name=candidate.name,
                filename=candidate.filename,
                score=round(score, 2),
                rank=0,  # Sera assigné après le tri
                similarity=round(similarity, 4),
                matching_keywords=keywords
            ))
        
        # Trier par score décroissant
        results.sort(key=lambda x: x.score, reverse=True)
        
        # Assigner les rangs
        for rank, result in enumerate(results, start=1):
            result.rank = rank
        
        logger.info(f"✅ Classement terminé - Top 1: {results[0].name} ({results[0].score:.1f}%)")
        
        return results
    
    def get_ranking_summary(self, ranked_candidates: List[RankedCandidate]) -> Dict[str, Any]:
        """
        Génère un résumé statistique du classement
        """
        if not ranked_candidates:
            return {
                "total_candidates": 0,
                "avg_score": 0,
                "top_score": 0,
                "low_score": 0
            }
        
        scores = [c.score for c in ranked_candidates]
        
        return {
            "total_candidates": len(ranked_candidates),
            "avg_score": round(np.mean(scores), 2),
            "median_score": round(np.median(scores), 2),
            "top_score": round(max(scores), 2),
            "low_score": round(min(scores), 2),
            "std_dev": round(np.std(scores), 2)
        }
