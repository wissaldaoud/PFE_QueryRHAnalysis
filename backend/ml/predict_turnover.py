"""
Endpoint de prédiction de turnover avec modèle Gradient Boosting
Compatible avec FastAPI
"""
import joblib
import pandas as pd
from pathlib import Path
from datetime import datetime, date
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

# Chemins des modèles
MODEL_PATH = Path(r"C:\Users\wdaoud\Documents\Models\gradient_boosting_turnover.pkl")
FEATURES_PATH = Path(r"C:\Users\wdaoud\Documents\Models\turnover_features.pkl")

class TurnoverPredictor:
    """Classe pour charger et utiliser le modèle de prédiction de turnover"""
    
    def __init__(self):
        self.model = None
        self.feature_columns = None
        self._load_model()
    
    def _load_model(self):
        """Charge le modèle et les features"""
        try:
            if MODEL_PATH.exists():
                self.model = joblib.load(MODEL_PATH)
                logger.info(f"Modèle chargé depuis {MODEL_PATH}")
            else:
                logger.error(f"Modèle introuvable: {MODEL_PATH}")
                return
            
            if FEATURES_PATH.exists():
                self.feature_columns = joblib.load(FEATURES_PATH)
                logger.info(f"Features chargées: {self.feature_columns}")
            else:
                # Features par défaut si le fichier n'existe pas
                self.feature_columns = [
                    'age', 'anciennete_annees', 'total_jours_absence', 
                    'nb_absences', 'duree_presence_jours',
                    'sexe_Féminin', 'sexe_Masculin',
                    'type_contrat_CDD', 'type_contrat_CDI', 'type_contrat_Inconnu'
                ]
                logger.warning(f"Fichier features introuvable, utilisation des features par défaut")
        
        except Exception as e:
            logger.error(f"Erreur lors du chargement du modèle: {e}")
            raise
    
    def _calculate_age(self, date_naissance: str) -> int:
        """Calcule l'âge à partir de la date de naissance"""
        if isinstance(date_naissance, str):
            birth_date = datetime.strptime(date_naissance, "%Y-%m-%d").date()
        else:
            birth_date = date_naissance
        
        today = date.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return age
    
    def _calculate_anciennete(self, date_embauche: str) -> float:
        """Calcule l'ancienneté en années"""
        if isinstance(date_embauche, str):
            hire_date = datetime.strptime(date_embauche, "%Y-%m-%d").date()
        else:
            hire_date = date_embauche
        
        today = date.today()
        days_diff = (today - hire_date).days
        return round(days_diff / 365.25, 2)
    
    def _calculate_duree_presence(self, date_embauche: str) -> int:
        """Calcule la durée de présence en jours"""
        if isinstance(date_embauche, str):
            hire_date = datetime.strptime(date_embauche, "%Y-%m-%d").date()
        else:
            hire_date = date_embauche
        
        today = date.today()
        return (today - hire_date).days
    
    def _prepare_features(self, employee_data: Dict[str, Any]) -> pd.DataFrame:
        """Prépare les features pour la prédiction"""
        
        # Calcul des features dérivées
        age = self._calculate_age(employee_data['date_naissance'])
        anciennete_annees = self._calculate_anciennete(employee_data['date_embauche'])
        duree_presence_jours = self._calculate_duree_presence(employee_data['date_embauche'])
        
        # Features numériques de base (5 features)
        features = {
            'age': age,
            'anciennete_annees': anciennete_annees,
            'total_jours_absence': int(employee_data.get('total_jours_absence', 0)),
            'nb_absences': int(employee_data.get('nb_absences', 0)),
            'duree_presence_jours': duree_presence_jours,
        }
        
        # Encodage one-hot pour sexe (1 feature)
        sexe = employee_data.get('sexe', 'Masculin')
        features['sexe_Masculin'] = 1 if sexe == 'Masculin' else 0
        
        # Encodage one-hot pour type_contrat (32 features)
        # Initialiser toutes les colonnes de type_contrat à 0
        type_contrat_input = employee_data.get('type_contrat', 'Inconnu')
        
        for col in self.feature_columns:
            if col.startswith('type_contrat_'):
                # Extraire le nom du type de contrat de la colonne
                contrat_name = col.replace('type_contrat_', '')
                # Activer la colonne si ça correspond au type de contrat fourni
                features[col] = 1 if contrat_name == type_contrat_input else 0
        
        # Créer DataFrame
        df = pd.DataFrame([features])
        
        # S'assurer que toutes les colonnes du modèle sont présentes dans le bon ordre
        for col in self.feature_columns:
            if col not in df.columns:
                df[col] = 0
        
        # Réorganiser selon l'ordre exact du modèle
        df = df[self.feature_columns]
        
        return df
    
    def predict(self, employee_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Effectue la prédiction de turnover
        
        Args:
            employee_data: Dictionnaire contenant les données de l'employé
        
        Returns:
            Dictionnaire avec la prédiction et les détails
        """
        if self.model is None:
            raise ValueError("Modèle non chargé")
        
        try:
            # Préparer les features
            X = self._prepare_features(employee_data)
            
            # Prédiction
            prediction = self.model.predict(X)[0]
            probability = self.model.predict_proba(X)[0][1]  # Probabilité de turnover (classe 1)
            
            # Déterminer le niveau de risque
            if probability < 0.30:
                risk_level = "Faible"
                risk_color = "green"
                risk_emoji = "🟢"
            elif probability < 0.60:
                risk_level = "Moyen"
                risk_color = "orange"
                risk_emoji = "🟡"
            else:
                risk_level = "Élevé"
                risk_color = "red"
                risk_emoji = "🔴"
            
            return {
                "prediction": int(prediction),
                "turnover_probability": round(float(probability), 4),
                "turnover_probability_percent": round(float(probability * 100), 2),
                "risk_level": risk_level,
                "risk_color": risk_color,
                "risk_emoji": risk_emoji,
                "features_used": X.to_dict(orient='records')[0],
                "model_path": str(MODEL_PATH),
            }
        
        except Exception as e:
            logger.error(f"Erreur lors de la prédiction: {e}")
            raise


# Instance globale du prédicteur
predictor = TurnoverPredictor()


def predict_turnover(employee_data: Dict[str, Any]) -> Dict[str, Any]:
    """Fonction wrapper pour la prédiction"""
    return predictor.predict(employee_data)
