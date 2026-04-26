"""
Mapper de données DWH PostgreSQL vers features IBM HR Analytics
Transforme les données RH de l'entreprise en format compatible avec le modèle de turnover
"""
from typing import Dict, Any, Optional
import pandas as pd
from datetime import datetime


class DWHToIBMMapper:
    """Classe de mapping entre données DWH et features IBM HR"""
    
    def __init__(self):
        """Initialise le mapper avec les règles de transformation"""
        self.mapping_rules = {
            'age': 'Age',
            'anciennete_annees': 'YearsAtCompany',
            'nb_absences': 'WorkLifeBalance',
            'total_jours_absence': 'OverTime',
            'sexe_encoded': 'Gender'
        }
    
    def map_work_life_balance(self, nb_absences: int) -> int:
        """
        Convertit le nombre d'absences en score WorkLifeBalance
        
        Règles de mapping:
        - 0 absences → 4 (Excellent)
        - 1-3 absences → 3 (Bon)
        - 4-8 absences → 2 (Moyen)
        - 9+ absences → 1 (Faible)
        
        Args:
            nb_absences: Nombre d'absences de l'employé
            
        Returns:
            Score WorkLifeBalance (1-4)
        """
        try:
            if nb_absences == 0:
                return 4
            elif 1 <= nb_absences <= 3:
                return 3
            elif 4 <= nb_absences <= 8:
                return 2
            else:  # 9+
                return 1
        except Exception as e:
            print(f"⚠️  Erreur mapping WorkLifeBalance: {str(e)}")
            return 2  # Valeur par défaut
    
    def map_overtime(self, total_jours_absence: float) -> int:
        """
        Détermine si l'employé fait des heures supplémentaires basé sur les absences
        
        Règle: Plus de 15 jours d'absence → OverTime = 0 (moins d'heures sup)
               Moins de 15 jours → OverTime = 1 (plus d'heures sup)
        
        Args:
            total_jours_absence: Total de jours d'absence dans l'année
            
        Returns:
            1 si OverTime (<=15 jours), 0 sinon
        """
        try:
            return 0 if total_jours_absence > 15 else 1
        except Exception as e:
            print(f"⚠️  Erreur mapping OverTime: {str(e)}")
            return 1  # Valeur par défaut
    
    def map_gender(self, sexe_encoded: int) -> int:
        """
        Mappe le sexe encodé DWH vers Gender IBM
        
        Args:
            sexe_encoded: Code sexe (0=Femme, 1=Homme généralement)
            
        Returns:
            Code gender IBM
        """
        try:
            return sexe_encoded
        except Exception as e:
            print(f"⚠️  Erreur mapping Gender: {str(e)}")
            return 0
    
    def calculate_years_at_company(self, date_embauche: str) -> int:
        """
        Calcule l'ancienneté en années depuis la date d'embauche
        
        Args:
            date_embauche: Date d'embauche au format ISO ou date string
            
        Returns:
            Nombre d'années d'ancienneté
        """
        try:
            if isinstance(date_embauche, str):
                date_embauche = pd.to_datetime(date_embauche)
            
            today = datetime.now()
            years = (today - date_embauche).days / 365.25
            return int(years)
            
        except Exception as e:
            print(f"⚠️  Erreur calcul ancienneté: {str(e)}")
            return 0
    
    def map_employee_data(self, dwh_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mappe les données d'un employé DWH vers le format IBM HR
        
        Args:
            dwh_data: Dictionnaire avec données DWH:
                - age: int
                - anciennete_annees: int (ou date_embauche)
                - nb_absences: int
                - total_jours_absence: float
                - sexe_encoded: int
                - department: str
                - marital_status: str (optionnel)
                - job_role: str (optionnel)
                
        Returns:
            Dictionnaire avec features IBM HR formatées
        """
        try:
            ibm_data = {}
            
            # Age (direct mapping)
            ibm_data['Age'] = dwh_data.get('age', 30)
            
            # YearsAtCompany
            if 'anciennete_annees' in dwh_data:
                ibm_data['YearsAtCompany'] = dwh_data['anciennete_annees']
            elif 'date_embauche' in dwh_data:
                ibm_data['YearsAtCompany'] = self.calculate_years_at_company(
                    dwh_data['date_embauche']
                )
            else:
                ibm_data['YearsAtCompany'] = 0
            
            # WorkLifeBalance (basé sur nb_absences)
            nb_absences = dwh_data.get('nb_absences', 0)
            ibm_data['WorkLifeBalance'] = self.map_work_life_balance(nb_absences)
            
            # OverTime (basé sur total_jours_absence)
            total_jours = dwh_data.get('total_jours_absence', 0)
            ibm_data['OverTime'] = self.map_overtime(total_jours)
            
            # Gender
            sexe = dwh_data.get('sexe_encoded', 0)
            ibm_data['Gender'] = self.map_gender(sexe)
            
            # Department (si disponible)
            if 'department' in dwh_data:
                ibm_data['Department'] = dwh_data['department']
            
            # MaritalStatus (si disponible)
            if 'marital_status' in dwh_data:
                ibm_data['MaritalStatus'] = dwh_data['marital_status']
            
            # JobRole (si disponible)
            if 'job_role' in dwh_data:
                ibm_data['JobRole'] = dwh_data['job_role']
            
            # Champs additionnels avec valeurs par défaut
            ibm_data.update({
                'YearsInCurrentRole': min(ibm_data['YearsAtCompany'], 
                                         dwh_data.get('years_in_role', ibm_data['YearsAtCompany'])),
                'YearsSinceLastPromotion': dwh_data.get('years_since_promotion', 
                                                         ibm_data['YearsAtCompany'] // 2),
                'YearsWithCurrManager': dwh_data.get('years_with_manager', 
                                                      min(2, ibm_data['YearsAtCompany'])),
                'MonthlyIncome': dwh_data.get('salaire_mensuel', 5000),
                'DistanceFromHome': dwh_data.get('distance_domicile', 10),
                'EnvironmentSatisfaction': dwh_data.get('satisfaction_environnement', 3),
                'JobSatisfaction': dwh_data.get('satisfaction_poste', 3),
                'RelationshipSatisfaction': dwh_data.get('satisfaction_relations', 3),
                'NumCompaniesWorked': dwh_data.get('nb_entreprises_precedentes', 1),
                'TotalWorkingYears': ibm_data['Age'] - 18,  # Approximation
                'TrainingTimesLastYear': dwh_data.get('nb_formations', 2),
                'PercentSalaryHike': dwh_data.get('pct_augmentation', 10),
                'StockOptionLevel': dwh_data.get('niveau_stock_options', 0)
            })
            
            return ibm_data
            
        except Exception as e:
            print(f"❌ Erreur lors du mapping: {str(e)}")
            raise
    
    def map_dataframe(self, dwh_df: pd.DataFrame) -> pd.DataFrame:
        """
        Mappe un DataFrame complet depuis DWH vers format IBM
        
        Args:
            dwh_df: DataFrame avec colonnes DWH
            
        Returns:
            DataFrame avec colonnes IBM HR
        """
        try:
            mapped_records = []
            
            for idx, row in dwh_df.iterrows():
                try:
                    mapped_data = self.map_employee_data(row.to_dict())
                    mapped_records.append(mapped_data)
                except Exception as e:
                    print(f"⚠️  Erreur ligne {idx}: {str(e)}")
                    continue
            
            ibm_df = pd.DataFrame(mapped_records)
            
            print(f"✅ Mapping terminé: {len(ibm_df)} employés mappés sur {len(dwh_df)}")
            
            return ibm_df
            
        except Exception as e:
            print(f"❌ Erreur mapping DataFrame: {str(e)}")
            raise
    
    def get_feature_mapping_info(self) -> Dict[str, str]:
        """
        Retourne les informations sur les règles de mapping
        
        Returns:
            Dictionnaire décrivant les mappings
        """
        return {
            'age': 'Age - Mapping direct',
            'anciennete_annees': 'YearsAtCompany - Mapping direct ou calculé depuis date_embauche',
            'nb_absences': 'WorkLifeBalance - 0→4, 1-3→3, 4-8→2, 9+→1',
            'total_jours_absence': 'OverTime - >15 jours→0, ≤15→1',
            'sexe_encoded': 'Gender - Mapping direct',
            'department': 'Department - Mapping direct si disponible',
            'marital_status': 'MaritalStatus - Mapping direct si disponible'
        }


def test_mapper():
    """Fonction de test du mapper"""
    print("=" * 60)
    print("🧪 TEST DU MAPPER DWH → IBM HR")
    print("=" * 60)
    
    mapper = DWHToIBMMapper()
    
    # Données de test
    test_employee = {
        'age': 35,
        'anciennete_annees': 5,
        'nb_absences': 3,
        'total_jours_absence': 12,
        'sexe_encoded': 1,
        'department': 'Sales',
        'marital_status': 'Married',
        'salaire_mensuel': 6500
    }
    
    print("\n📥 Données DWH:")
    for key, value in test_employee.items():
        print(f"   {key}: {value}")
    
    # Mapping
    ibm_features = mapper.map_employee_data(test_employee)
    
    print("\n📤 Features IBM HR:")
    for key, value in ibm_features.items():
        print(f"   {key}: {value}")
    
    print("\n✅ Test réussi!")


if __name__ == "__main__":
    test_mapper()
