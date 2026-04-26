
import pickle
import os
import joblib
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session


# ══════════════════════════════════════════════════════════════════════
# CONSTANTES IBM HR DATASET
# Valeurs issues du vrai dataset WA_Fn-UseC_-HR-Employee-Attrition.csv
# ══════════════════════════════════════════════════════════════════════

# Moyennes du dataset IBM HR (1470 employés)
IBM_DEFAULTS = {
    "Age":                       37,
    "BusinessTravel":            1,    # Travel_Rarely=2, Non-Travel=0, Frequently=1
    "DailyRate":                 802,
    "Department":                2,    # R&D=2, Sales=1, HR=0
    "DistanceFromHome":          9,
    "Education":                 3,    # 1=Below College ... 5=Doctor
    "EducationField":            1,    # Life Sciences=1
    "EmployeeCount":             1,
    "EmployeeNumber":            1024,
    "EnvironmentSatisfaction":   3,
    "Gender":                    1,    # Male=1, Female=0
    "HourlyRate":                66,
    "JobInvolvement":            3,
    "JobLevel":                  2,
    "JobRole":                   6,    # Sales Executive=7, Research Scientist=6
    "JobSatisfaction":           3,
    "MaritalStatus":             1,    # Married=1, Single=2, Divorced=0
    "MonthlyIncome":             6503,
    "MonthlyRate":               14314,
    "NumCompaniesWorked":        3,
    "Over18":                    1,
    "OverTime":                  0,    # No=0, Yes=1
    "PercentSalaryHike":         15,
    "PerformanceRating":         3,
    "RelationshipSatisfaction":  3,
    "StandardHours":             80,
    "StockOptionLevel":          1,
    "TotalWorkingYears":         11,
    "TrainingTimesLastYear":     3,
    "WorkLifeBalance":           3,
    "YearsAtCompany":            7,
    "YearsInCurrentRole":        4,
    "YearsSinceLastPromotion":   2,
    "YearsWithCurrManager":      4,
}

# Encodages LabelEncoder (ordre alphabétique = sklearn LabelEncoder)
IBM_ENCODINGS = {
    "BusinessTravel":  {"Non-Travel": 0, "Travel_Frequently": 1, "Travel_Rarely": 2},
    "Department":      {"Human Resources": 0, "Research & Development": 2, "Sales": 1},
    "EducationField":  {
        "Human Resources": 0, "Life Sciences": 1, "Marketing": 2,
        "Medical": 3, "Other": 4, "Technical Degree": 5
    },
    "Gender":          {"Female": 0, "Male": 1},
    "JobRole":         {
        "Healthcare Representative": 0, "Human Resources": 1,
        "Laboratory Technician": 2, "Manager": 3,
        "Manufacturing Director": 4, "Research Director": 5,
        "Research Scientist": 6, "Sales Executive": 7,
        "Sales Representative": 8
    },
    "MaritalStatus":   {"Divorced": 0, "Married": 1, "Single": 2},
    "OverTime":        {"No": 0, "Yes": 1},
}

# Niveaux de risque
RISK_LEVELS = [
    (70, 101, "CRITIQUE", "#DC2626", "Départ très probable — intervention urgente requise."),
    (45,  70, "ÉLEVÉ",    "#EA580C", "Risque significatif — action RH dans les 15 jours."),
    (25,  45, "MODÉRÉ",   "#D97706", "Signaux d'alerte — surveiller et planifier entretien."),
    ( 0,  25, "FAIBLE",   "#16A34A", "Employé stable — maintenir les conditions actuelles."),
]


class MLService:
    """
    Service ML Turnover — Double mode formulaire + DWH
    """

    def __init__(self, db: Session):
        self.db = db
        self.model = None
        self.threshold = 0.30
        self.selected_features = []
        self.label_encoders = {}
        self.model_name = "XGBoost"
        self.metrics = {}
        self._load_model()
        self._setup_dwh_connection()

    # ══════════════════════════════════════════════════════
    # CHARGEMENT MODELE
    # ══════════════════════════════════════════════════════

    def _load_model(self):
        # Utiliser le modèle pipeline_turnover.pkl depuis C:\Users\wdaoud\Documents\Models
        model_path = Path(r"C:\Users\wdaoud\Documents\Models\pipeline_turnover.pkl")
        
        # Fallback sur l'ancien chemin si le nouveau n'existe pas
        if not model_path.exists():
            base          = Path(__file__).parent.parent.parent
            model_path    = base / "ml" / "models" / "turnover_model.pkl"
        
        features_path = Path(__file__).parent.parent.parent / "ml" / "models" / "turnover_features.pkl"

        if not model_path.exists():
            raise FileNotFoundError(f"Modèle introuvable: {model_path}")
        
        # Stocker le chemin du modèle pour l'API
        self.model_path = str(model_path)

        model_data = joblib.load(model_path)

        # Gérer les deux formats: dict avec "model" ou modèle directement
        if isinstance(model_data, dict):
            self.model          = model_data["model"]
            self.model_name     = model_data.get("model_name", "XGBoost")
            self.threshold      = model_data.get("threshold", 0.30)
            self.label_encoders = model_data.get("label_encoders", {})
            self.metrics        = model_data.get("metrics", {})
            self.selected_features = model_data.get("selected_features", [])
        else:
            # Le fichier pkl contient directement le modèle
            self.model          = model_data
            self.model_name     = "XGBoost"
            self.threshold      = 0.30
            self.label_encoders = {}
            self.metrics        = {}
            self.selected_features = []

        # Charger les features depuis le fichier séparé si disponible
        if features_path.exists():
            features_data         = joblib.load(features_path)
            if isinstance(features_data, dict):
                self.selected_features = features_data.get("selected_features", [])
            elif isinstance(features_data, list):
                self.selected_features = features_data

        print(f"✅ Modèle chargé    : {self.model_name}")
        print(f"   Features         : {len(self.selected_features)}")
        print(f"   Threshold        : {self.threshold}")
        if self.selected_features:
            print(f"   Features liste   : {self.selected_features[:5]}...")

    # ══════════════════════════════════════════════════════
    # CONNEXION DWH
    # ══════════════════════════════════════════════════════

    def _setup_dwh_connection(self):
        try:
            dwh_url = (
                f"postgresql://{os.getenv('DWH_USER','hr_user')}:"
                f"{os.getenv('DWH_PASSWORD','hr_password123')}@"
                f"{os.getenv('DWH_HOST','localhost')}:"
                f"{os.getenv('DWH_PORT','5432')}/"
                f"{os.getenv('DWH_DB','hr_datawarehouse')}"
            )
            self.dwh_engine = create_engine(dwh_url, pool_pre_ping=True, pool_size=5)
            print("✅ Connexion DWH configurée")
        except Exception as e:
            print(f"⚠️  DWH non disponible: {e}")
            self.dwh_engine = None

    # ══════════════════════════════════════════════════════
    # PREPARATION FEATURES
    # ══════════════════════════════════════════════════════

    def _build_feature_vector(self, raw_data: Dict[str, Any]) -> pd.DataFrame:
        """
        Construit le vecteur de features dans le bon ordre
        à partir de données IBM HR (formulaire ou mappées).
        """
        row = IBM_DEFAULTS.copy()

        for key, val in raw_data.items():
            if key in row:
                # Convertir texte → code si label encoder disponible
                if key in IBM_ENCODINGS and isinstance(val, str):
                    val = IBM_ENCODINGS[key].get(val, row[key])
                row[key] = val

        if self.selected_features:
            input_row = {f: row.get(f, 0) for f in self.selected_features}
        else:
            input_row = row

        return pd.DataFrame([input_row]).fillna(0)

    # ══════════════════════════════════════════════════════
    # NIVEAU DE RISQUE
    # ══════════════════════════════════════════════════════

    def _get_risk(self, score: float) -> Dict[str, str]:
        for low, high, level, color, msg in RISK_LEVELS:
            if low <= score < high:
                return {"niveau": level, "couleur": color, "recommandation": msg}
        return {"niveau": "INCONNU", "couleur": "#6B7280", "recommandation": ""}

    # ══════════════════════════════════════════════════════
    # MODE 1 — FORMULAIRE IBM HR (données saisies manuellement)
    # Résultats FIABLES car features identiques à l'entraînement
    # ══════════════════════════════════════════════════════

    def predict_from_form(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prédit le turnover depuis un formulaire IBM HR.
        C'est le mode le plus PRÉCIS — données identiques au training.

        Paramètres attendus (tous optionnels, valeurs par défaut IBM HR) :
            Age, MonthlyIncome, JobSatisfaction (1-4),
            EnvironmentSatisfaction (1-4), WorkLifeBalance (1-4),
            OverTime (Yes/No), YearsAtCompany, TotalWorkingYears,
            NumCompaniesWorked, BusinessTravel, Department,
            Gender, MaritalStatus, JobRole, EducationField, etc.
        """
        try:
            X     = self._build_feature_vector(form_data)
            proba = float(self.model.predict_proba(X)[0][1])
            score = round(proba * 100, 1)
            pred  = int(proba >= self.threshold)
            risk  = self._get_risk(score)

            # Facteurs clés (top features présentes dans le formulaire)
            key_factors = self._get_key_factors(form_data)

            return {
                "success":      True,
                "mode":         "formulaire",
                "score":        score,
                "prediction":   pred,
                "probabilite":  round(proba, 4),
                "threshold":    self.threshold,
                "niveau":       risk["niveau"],
                "couleur":      risk["couleur"],
                "recommandation": risk["recommandation"],
                "key_factors":  key_factors,
                "modele":       self.model_name,
            }

        except Exception as e:
            return {"success": False, "error": f"Erreur prédiction formulaire: {e}"}

    # ══════════════════════════════════════════════════════
    # MODE 2 — DWH Sopra HR (données automatiques)
    # Résultats APPROXIMATIFS — mapping DWH → IBM HR
    # ══════════════════════════════════════════════════════

    def predict_from_dwh(self, employe_id: str) -> Dict[str, Any]:
        """
        Prédit le turnover depuis les données locales de la base hr_analytics.
        Utilise les congés de la table leave_requests comme absences.
        
        Args:
            employe_id: ID de l'employé dans la table employees locale
        """
        try:
            # Récupérer l'employé depuis la base locale
            from app.models.employee import Employee
            from app.models.leave import LeaveRequest, LeaveStatus
            from datetime import datetime, date
            from sqlalchemy import func
            
            employee = self.db.query(Employee).filter(Employee.id == int(employe_id)).first()
            
            if not employee:
                return {"success": False, "error": f"Employé ID {employe_id} introuvable dans la base de données"}
            
            # Calculer l'âge
            if employee.date_of_birth:
                age = (date.today() - employee.date_of_birth).days // 365
            else:
                age = 35  # valeur par défaut
            
            # Calculer l'ancienneté
            if employee.hire_date:
                duree_presence_jours = (date.today() - employee.hire_date).days
                anciennete_annees = round(duree_presence_jours / 365.25, 2)
            else:
                duree_presence_jours = 90
                anciennete_annees = 0.25
            
            # Récupérer les absences (congés approuvés par le manager ou RH)
            absences = self.db.query(
                func.count(LeaveRequest.id).label('nb_absences'),
                func.coalesce(func.sum(
                    LeaveRequest.end_date - LeaveRequest.start_date + 1
                ), 0).label('total_jours_absence')
            ).filter(
                LeaveRequest.employee_id == int(employe_id),
                LeaveRequest.status.in_([LeaveStatus.manager_approved, LeaveStatus.hr_approved])
            ).first()
            
            nb_absences = int(absences.nb_absences) if absences.nb_absences else 0
            total_jours_absence = int(absences.total_jours_absence) if absences.total_jours_absence else 0
            
            # Déterminer le sexe (supposer masculin par défaut si non renseigné)
            sexe_masculin = 1  # par défaut
            
            # Type de contrat
            type_contrat = employee.contract_type or "CDI"
            
            # Département
            department = employee.department.name if employee.department else "Non renseigné"

            # Liste complète des types de contrat attendus par le pipeline
            all_type_contrats = [
                'Administratif', 'Apprenti', 'CDD sur emploi permanent', 'CDI',
                'CONTRAT A DUREE DETERMINEE DE DROIT PRIVE',
                'CONTRAT A DUREE INDETERMINEE DE DROIT PRIVE',
                'Contrat de stagiaire', 'Contrat de travailleur de vacances',
                'Contrat intérimaire', 'Contrat stagiaire',
                'Contrat à durée déterminée', 'Contrat à durée indéterminée',
                'Contrat à durée indéterminée employé', 'Contrat à la prestation',
                'DUREE DETERMINEE', 'DUREE INDETERMINEE', 'Durée déterminée',
                'Durée déterminée employé', 'Durée indéterminée',
                'Employé durée indéterminée', 'Etudiant', 'Inconnu',
                'Ouvrier durée indéterminée', 'Permanent', 'Pré retraité',
                'Prépension conventionel', 'Stagiaire', 'Stagiaire petit statut',
                'Stagiaire transition', 'TEMPORAIRE', 'Temporaire', 'Travail temporaire'
            ]
            
            # Construire le DataFrame avec les features de base depuis les données locales
            data = {
                'age': age,
                'anciennete_annees': anciennete_annees,
                'total_jours_absence': total_jours_absence,
                'nb_absences': nb_absences,
                'duree_presence_jours': duree_presence_jours,
                'sexe_Masculin': sexe_masculin,
            }
            
            # Ajouter les colonnes one-hot pour type_contrat
            for tc in all_type_contrats:
                data[f'type_contrat_{tc}'] = 1 if tc == type_contrat else 0
            
            X = pd.DataFrame([data])
            
            # Prédire avec le pipeline
            proba = float(self.model.predict_proba(X)[0][1])
            score = round(proba * 100, 1)
            pred  = int(proba >= self.threshold)
            risk  = self._get_risk(score)

            return {
                "success":        True,
                "mode":           "local",
                "employe_id":     int(employe_id),
                "score":          score,
                "prediction":     pred,
                "probabilite":    round(proba, 4),
                "niveau":         risk["niveau"],
                "couleur":        risk["couleur"],
                "recommandation": risk["recommandation"],
                "details": {
                    "age":                age,
                    "anciennete_annees":  anciennete_annees,
                    "nb_absences":        nb_absences,
                    "total_jours_absence": total_jours_absence,
                    "department":         department,
                    "type_contrat":       type_contrat,
                },
                "features_used": {
                    "age":                age,
                    "anciennete_annees":  anciennete_annees,
                    "nb_absences":        nb_absences,
                    "total_jours_absence": total_jours_absence,
                    "department":         department,
                    "type_contrat":       type_contrat,
                },
                "model_path":     self.model_path,
                "computed_at":    datetime.now().isoformat(),
                "note": "Prédiction depuis base locale hr_analytics - congés approuvés utilisés comme absences",
                "modele": self.model_name,
            }

        except Exception as e:
            return {"success": False, "error": f"Erreur prédiction locale: {e}"}

    def _fetch_from_dwh(self, employe_id: str) -> Optional[Dict]:
        """Récupère les données d'un employé depuis le DWH Sopra HR - utilise absences (congés)."""
        try:
            query = text("""
                SELECT
                    e.nudoss,
                    COALESCE(e.age, 35) as age,
                    CASE WHEN UPPER(e.libelle_sexe) = 'MASCULIN' THEN 1 ELSE 0 END as sexe_masculin,
                    COALESCE(
                        EXTRACT(DAY FROM AGE(CURRENT_DATE, MIN(c.date_debut_contrat))),
                        90
                    )::int as duree_presence_jours,
                    MAX(c.libelle_type_contrat) as type_contrat,
                    MAX(af.libelle_poste) as department,
                    COUNT(DISTINCT a.id_absence) as nb_absences,
                    COALESCE(SUM(a.duree_absence_jours), 0)::int as total_jours_absence
                FROM dim.dim_employe e
                LEFT JOIN fait.fait_contrat c ON e.nudoss = c.nudoss
                LEFT JOIN fait.fait_absence a ON e.nudoss = a.nudoss
                LEFT JOIN fait.fait_affectation af ON e.nudoss = af.nudoss
                    AND af.flag_affectation_active = 1
                WHERE e.nudoss = :eid AND e.flag_employe_actif = 1
                GROUP BY e.nudoss, e.age, e.libelle_sexe
            """)
            with self.dwh_engine.connect() as conn:
                result = conn.execute(query, {"eid": employe_id})
                row = result.fetchone()
                if not row:
                    return None
                # Convertir Row en liste pour accès par index
                row_list = list(row)
                
                # Calculer les features dérivées
                duree_presence = max(row_list[3], 1)  # éviter division par zéro
                total_jours_absence = row_list[7] or 0
                nb_absences = row_list[6] or 0
                anciennete_annees = round(duree_presence / 365.25, 2)
                
                return {
                    "nudoss":              row_list[0],
                    "age":                 row_list[1],
                    "sexe_Masculin":       row_list[2],  # 0 ou 1
                    "duree_presence_jours": duree_presence,
                    "anciennete_annees":   anciennete_annees,
                    "type_contrat":        row_list[4] or "CDI",
                    "department":          row_list[5] or "Other",
                    "nb_absences":         nb_absences,
                    "total_jours_absence": total_jours_absence,
                }
        except Exception as e:
            print(f"ERROR in _fetch_from_dwh: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _map_dwh_to_ibm(self, d: Dict) -> Dict:
        """
        Mappe les données DWH Sopra HR → features IBM HR.
        Logique métier RH pour approximer les features manquantes.
        """
        anc  = float(d.get("anciennete", 3))
        abs_ = int(d.get("nb_absences", 0))
        jabs = float(d.get("total_jours_absence", 0))
        ctrs = int(d.get("nb_contrats", 1))

        # WorkLifeBalance 1-4 (absences élevées = mauvais équilibre)
        wlb = 4 if abs_ == 0 else 3 if abs_ <= 3 else 2 if abs_ <= 8 else 1

        # EnvironmentSatisfaction : absences courtes = insatisfaction
        env = 4 if abs_ == 0 else 3 if abs_ <= 2 else 2 if abs_ <= 5 else 1

        # JobSatisfaction : ancienneté élevée sans mobilité = baisse
        jsat = 4 if anc <= 1 else 3 if anc <= 4 else 2 if anc <= 8 else 2

        # OverTime : >15 jours absence peut indiquer surcharge
        ot = 1 if jabs > 15 else 0

        # MonthlyIncome approximé par ancienneté
        income = int(3000 + anc * 400)

        # NumCompaniesWorked = nombre de contrats (proxy)
        ncw = min(ctrs, 9)

        # JobLevel basé sur ancienneté
        jlevel = min(int(anc / 4) + 1, 5)

        return {
            "Age":                      d.get("age", 35),
            "Gender":                   d.get("sexe", 1),
            "MaritalStatus":            1,          # Married par défaut
            "OverTime":                 ot,
            "BusinessTravel":           1,          # Travel_Rarely
            "Department":               2,          # R&D par défaut
            "EducationField":           1,          # Life Sciences
            "JobRole":                  6,          # Research Scientist
            "JobLevel":                 jlevel,
            "JobSatisfaction":          jsat,
            "EnvironmentSatisfaction":  env,
            "WorkLifeBalance":          wlb,
            "JobInvolvement":           3,
            "RelationshipSatisfaction": 3,
            "YearsAtCompany":           anc,
            "YearsInCurrentRole":       round(anc * 0.65),
            "YearsSinceLastPromotion":  round(anc * 0.45),
            "YearsWithCurrManager":     round(anc * 0.40),
            "TotalWorkingYears":        anc,
            "NumCompaniesWorked":       ncw,
            "MonthlyIncome":            income,
            "PercentSalaryHike":        min(10 + int(anc), 25),
            "PerformanceRating":        3,
            "StockOptionLevel":         0,
            "TrainingTimesLastYear":    3,
            "Education":                3,
            "DistanceFromHome":         9,
        }

    # ══════════════════════════════════════════════════════
    # PRÉDICTION TOUS EMPLOYÉS DWH
    # ══════════════════════════════════════════════════════

    def predict_all_employees(self, limit: int = 50) -> Dict[str, Any]:
        """Analyse le risque de turnover pour tous les employés actifs."""
        try:
            if not self.dwh_engine:
                return {"success": False, "error": "DWH non disponible"}

            with self.dwh_engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT nudoss, nom, prenom
                    FROM dim.dim_employe
                    WHERE flag_employe_actif = 1
                    LIMIT :lim
                """), {"lim": limit})
                rows = result.fetchall()

            predictions = []
            for row in rows:
                # Convertir Row en liste pour accès par index
                row_list = list(row)
                pred = self.predict_from_dwh(str(row_list[0]))
                if pred.get("success"):
                    pred["nom"]    = row_list[1] or ""
                    pred["prenom"] = row_list[2] or ""
                    predictions.append(pred)

            predictions.sort(key=lambda x: x["score"], reverse=True)

            stats = {
                "critique": len([p for p in predictions if p["niveau"] == "CRITIQUE"]),
                "eleve":    len([p for p in predictions if p["niveau"] == "ÉLEVÉ"]),
                "modere":   len([p for p in predictions if p["niveau"] == "MODÉRÉ"]),
                "faible":   len([p for p in predictions if p["niveau"] == "FAIBLE"]),
                "total":    len(predictions),
                "taux_risque_eleve": round(
                    len([p for p in predictions if p["score"] >= 45]) / max(len(predictions), 1) * 100, 1
                )
            }

            return {"success": True, "predictions": predictions, "stats": stats}

        except Exception as e:
            return {"success": False, "error": str(e)}

    # ══════════════════════════════════════════════════════
    # SIMULATEUR WHAT-IF
    # ══════════════════════════════════════════════════════

    def simulate_whatif(self, base_data: Dict, modifications: Dict) -> Dict[str, Any]:
        """
        Compare le score avant/après une action RH simulée.
        Ex: simulate_whatif(form_data, {"JobSatisfaction": 4, "OverTime": "No"})
        """
        try:
            result_avant = self.predict_from_form(base_data)
            modified     = {**base_data, **modifications}
            result_apres = self.predict_from_form(modified)

            if not result_avant["success"] or not result_apres["success"]:
                return {"success": False, "error": "Erreur calcul simulation"}

            delta = round(result_avant["score"] - result_apres["score"], 1)

            if delta > 5:
                interpretation = f"Cette action réduirait le risque de {delta}% ({result_avant['niveau']} → {result_apres['niveau']})"
            elif delta < -5:
                interpretation = f"Cette action augmenterait le risque de {abs(delta)}% ({result_avant['niveau']} → {result_apres['niveau']})"
            else:
                interpretation = "Impact négligeable sur le risque de turnover"

            return {
                "success":        True,
                "avant":          {"score": result_avant["score"], "niveau": result_avant["niveau"]},
                "apres":          {"score": result_apres["score"], "niveau": result_apres["niveau"]},
                "delta":          delta,
                "interpretation": interpretation,
                "recommandation": "Action bénéfique" if delta > 0 else "Action à reconsidérer",
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def simulate_whatif_dwh(self, employe_id: str, modifications: Dict) -> Dict[str, Any]:
        """
        Simule l'impact de modifications pour un employé du DWH.
        Ex: simulate_whatif_dwh("234", {"nb_absences": 2, "anciennete": 8})
        """
        try:
            # Récupérer les données actuelles de l'employé
            dwh_data = self._fetch_from_dwh(employe_id)
            if not dwh_data:
                return {"success": False, "error": f"Employé {employe_id} introuvable"}
            
            # État actuel
            base_data = self._map_dwh_to_ibm(dwh_data)
            result_avant = self.predict_from_form(base_data)
            
            # Appliquer les modifications aux données DWH
            modified_dwh = {**dwh_data}
            for key, val in modifications.items():
                # Mapper les noms de champs frontend vers DWH
                if key in ["nb_absences", "anciennete", "anciennete_annees", "age", "sexe"]:
                    modified_dwh[key] = val
                elif key == "salaire_mensuel":
                    # Recalculer l'approximation de revenu
                    modified_dwh["anciennete"] = val / 400 - 7.5  # Inverse de la formule
            
            # État après modifications
            modified_ibm = self._map_dwh_to_ibm(modified_dwh)
            result_apres = self.predict_from_form(modified_ibm)
            
            if not result_avant["success"] or not result_apres["success"]:
                return {"success": False, "error": "Erreur calcul simulation"}
            
            delta = round(result_avant["score"] - result_apres["score"], 1)
            
            if delta > 5:
                impact = f"Réduction du risque de {delta}% ({result_avant['niveau']} → {result_apres['niveau']})"
            elif delta < -5:
                impact = f"Augmentation du risque de {abs(delta)}% ({result_avant['niveau']} → {result_apres['niveau']})"
            else:
                impact = "Impact négligeable sur le risque de turnover"
            
            return {
                "success": True,
                "employe_id": employe_id,
                "avant": {"score": result_avant["score"], "niveau": result_avant["niveau"]},
                "apres": {"score": result_apres["score"], "niveau": result_apres["niveau"]},
                "delta": delta,
                "impact": impact,
                "modifications": modifications,
                "recommandation": "Action bénéfique" if delta > 0 else "Action à reconsidérer",
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ══════════════════════════════════════════════════════
    # FACTEURS CLÉS
    # ══════════════════════════════════════════════════════

    def _get_key_factors(self, data: Dict) -> list:
        """Retourne les facteurs de risque principaux détectés."""
        factors = []
        if str(data.get("OverTime", "No")) in ["Yes", "1", 1]:
            factors.append({"facteur": "Heures supplémentaires", "impact": "Élevé", "valeur": "Oui"})
        jsat = int(data.get("JobSatisfaction", 3))
        if jsat <= 2:
            factors.append({"facteur": "Satisfaction au travail", "impact": "Élevé", "valeur": f"{jsat}/4"})
        wlb = int(data.get("WorkLifeBalance", 3))
        if wlb <= 2:
            factors.append({"facteur": "Équilibre vie pro/perso", "impact": "Modéré", "valeur": f"{wlb}/4"})
        anc = float(data.get("YearsAtCompany", 5))
        if anc <= 2:
            factors.append({"facteur": "Faible ancienneté", "impact": "Modéré", "valeur": f"{anc} ans"})
        ncw = int(data.get("NumCompaniesWorked", 3))
        if ncw >= 5:
            factors.append({"facteur": "Mobilité inter-entreprises", "impact": "Modéré", "valeur": f"{ncw} employeurs"})
        return factors

    # ══════════════════════════════════════════════════════
    # INFO MODÈLE
    # ══════════════════════════════════════════════════════

    def get_model_info(self) -> Dict[str, Any]:
        return {
            "model_name":      self.model_name,
            "threshold":       self.threshold,
            "nb_features":     len(self.selected_features),
            "features":        self.selected_features,
            "metrics":         self.metrics,
            "dataset":         "IBM HR Analytics (1470 employés)",
            "techniques":      ["XGBoost", "SMOTE", "SelectKBest", "GridSearchCV"],
        }