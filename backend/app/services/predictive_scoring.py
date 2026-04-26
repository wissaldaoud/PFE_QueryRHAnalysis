"""
Scoring Prédictif RH — XGBoost Qlik
===================================
Prédit le risque de départ (turnover) d'un employé à partir des données Qlik.
Fournit une explication SHAP et des recommandations actionnables.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List
import joblib
import numpy as np
import pandas as pd
from dataclasses import dataclass

try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════
# DATACLASSES
# ═══════════════════════════════════════════════════════════

@dataclass
class PredictiveScore:
    employee_id: str
    churn_risk_score: float
    risk_level: str
    action_priority: str
    key_factors: List[Dict[str, Any]]
    recommendations: List[str]
    performance_score: float = 0.70
    engagement_score: float = 0.65
    prediction_confidence: float = 0.75
    model_version: str = "XGBoost_Qlik_v1"

# ═══════════════════════════════════════════════════════════
# CLASSE PRINCIPALE
# ═══════════════════════════════════════════════════════════

class PredictiveScorer:
    """Scoring de turnover RH — XGBoost Qlik + SHAP"""

    def __init__(self):
        self.model = None
        self.model_name = "XGBoost_Qlik"
        self.model_version = "XGBoost_Qlik_v1"
        self.threshold = 0.3
        self.feature_names = ['age', 'anciennete_annees', 'sexe_code', 'is_cdi',
                              'nb_absences', 'total_jours_absence', 'taux_absenteisme']
        self.explainer = None
        self._load_model()

    def _load_model(self):
        """Charge le modèle XGBoost Qlik."""
        base_dir = Path(__file__).parent.parent.parent
        model_path = base_dir / "ml" / "models" / "turnover_model.pkl"
        if not model_path.exists():
            raise FileNotFoundError(f"Modèle introuvable : {model_path}")
        self.model = joblib.load(model_path)

        if SHAP_AVAILABLE:
            try:
                self.explainer = shap.TreeExplainer(self.model)
            except Exception as exc:
                logger.warning("SHAP TreeExplainer non disponible : %s", exc)
                self.explainer = None
        else:
            logger.warning("SHAP non disponible - Les explications seront désactivées")
            self.explainer = None
        logger.info(f"Modèle chargé : {self.model_name} — {len(self.feature_names)} features")

    def _prepare_features(self, data: Dict[str, Any]) -> pd.DataFrame:
        """Feature engineering sur les 7 features réelles du modèle Qlik."""
        anc = max(float(data.get("anciennete_annees", 3)), 0)
        abs_n = max(int(data.get("nb_absences", 0)), 0)
        jours = max(float(data.get("total_jours_absence", 0)), 0)
        age = int(data.get("age", 35))
        sexe_code = 1 if str(data.get("sexe", "M")).upper() == "M" else 0
        is_cdi = 1 if "CDI" in str(data.get("type_contrat", "")).upper() else 0

        X_dict = {
            "age": age,
            "anciennete_annees": anc,
            "sexe_code": sexe_code,
            "is_cdi": is_cdi,
            "nb_absences": abs_n,
            "total_jours_absence": jours,
            "taux_absenteisme": jours / max(anc * 12, 1) if anc > 0 else 0,
        }

        return pd.DataFrame([X_dict])[self.feature_names].fillna(0)

    def _predict_churn(self, X: pd.DataFrame) -> float:
        """Retourne la probabilité de turnover."""
        return float(self.model.predict_proba(X)[:, 1][0])

    def _compute_shap(self, X: pd.DataFrame, top_n: int = 5):
        if self.explainer is None:
            return [], np.array([])
        
        try:
            sv = self.explainer.shap_values(X)
            
            # Extraire les valeurs SHAP correctement
            if isinstance(sv, list):
                # Classification binaire : sv[0] pour classe 0, sv[1] pour classe 1
                values = sv[1][0] if len(sv) > 1 else sv[0][0]
            elif hasattr(sv, 'ndim'):
                # Array numpy
                if sv.ndim > 1:
                    values = sv[0]
                else:
                    values = sv
            else:
                values = np.array(sv).flatten()
            
            # S'assurer que c'est un array 1D
            values = np.atleast_1d(values).flatten()
            
            features = list(X.columns)
            
            # Vérifier que les dimensions correspondent
            if len(values) != len(features):
                logger.warning(f"SHAP values length ({len(values)}) != features length ({len(features)})")
                return [], values
            
            indices = np.argsort(np.abs(values))[::-1][:top_n]
            factors = [{
                "feature": features[i],
                "feature_raw": features[i],
                "shap_value": round(float(values[i]), 4),
                "direction": "↑ augmente le risque" if values[i] > 0 else "↓ diminue le risque"
            } for i in indices]
            
            return factors, values
            
        except Exception as e:
            logger.error(f"Erreur calcul SHAP: {e}")
            return [], np.array([])

    @staticmethod
    def _classify_risk(churn: float):
        if churn >= 0.65: return "élevé", "critique"
        if churn >= 0.40: return "moyen", "élevée"
        return "faible", "normale"

    @staticmethod
    def _compute_confidence(churn: float, shap_values: np.ndarray) -> float:
        dist = abs(churn - 0.50)
        distance_score = min(dist / 0.50, 1.0)
        shap_score = min(np.sum(np.abs(shap_values)) / 5.0, 1.0) if shap_values is not None else 0.0
        return round(np.clip(0.50 + 0.30*distance_score + 0.15*shap_score, 0.50, 0.95), 3)

    @staticmethod
    def _generate_recommendations(churn, factors, data, priority):
        recs = []
        if priority == "critique":
            recs.append("🚨 Risque critique — entretien sous 48 h")
            recs.append("👥 Impliquer le manager direct et HRBP")
        elif priority == "élevée":
            recs.append("⚠️ Risque significatif — point individuel sous 15 jours")
        for f in factors:
            if f["shap_value"] <= 0.03: continue
            if f["feature_raw"] in ("anciennete_annees","nb_absences"):
                recs.append("📅 Renforcer accompagnement et mentorat")
        recs += ["💬 Feedback régulier", "🎓 Formations alignées projet", "🏆 Valoriser contributions"]
        return recs[:6]

    @staticmethod
    def _performance_score(data):
        base = 0.7
        anc = float(data.get("anciennete_annees", 0))
        if anc > 3: base += 0.1
        if anc > 7: base += 0.1
        if data.get("nb_absences", 0) == 0: base += 0.05
        return min(1.0, base)

    @staticmethod
    def _engagement_score(churn):
        return round((1.0 - churn) ** 0.8, 3)

    def score(self, employee_data) -> PredictiveScore:
        eid = str(employee_data.get("employee_id", "inconnu"))
        X = self._prepare_features(employee_data)
        churn = self._predict_churn(X)
        factors, shap_values = self._compute_shap(X)
        risk_level, action_priority = self._classify_risk(churn)
        confidence = self._compute_confidence(churn, shap_values)
        recs = self._generate_recommendations(churn, factors, employee_data, action_priority)
        perf = self._performance_score(employee_data)
        eng = self._engagement_score(churn)
        return PredictiveScore(
            employee_id=eid,
            churn_risk_score=round(churn,3),
            risk_level=risk_level,
            action_priority=action_priority,
            key_factors=factors,
            recommendations=recs,
            performance_score=perf,
            engagement_score=eng,
            prediction_confidence=confidence,
            model_version=self.model_version,
        )


# ═══════════════════════════════════════════════════════════
# CLASSE POUR COMPATIBILITÉ
# ═══════════════════════════════════════════════════════════

@dataclass
class EmployeeHistory:
    """Données historiques d'un employé (pour compatibilité)"""
    employee_id: str
    age: int
    anciennete_annees: float
    nb_absences: int
    total_jours_absence: float
    type_contrat: str = "CDI"
    sexe: str = "M"


# Alias pour compatibilité
PredictiveScorerML = PredictiveScorer