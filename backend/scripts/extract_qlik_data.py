"""
Extraction des vraies données Qlik / PostgreSQL pour le modèle de turnover
"""

import pandas as pd
from sqlalchemy import create_engine, text
from pathlib import Path

def get_dwh_engine():
    """Change les identifiants si nécessaire"""
    return create_engine(
        "postgresql://hr_user:hr_password123@localhost:5432/hr_datawarehouse"
        # Si ton mot de passe ou utilisateur est différent, modifie ici
    )

def extract_employee_history():
    print("🔌 Connexion au DWH PostgreSQL...")
    engine = get_dwh_engine()

    query = text("""
        WITH ABSENCES_AGG AS (
            SELECT 
                nudoss,
                COUNT(*) AS nb_absences,
                SUM(duree_absence_jours) AS total_jours_absence
            FROM fait.fait_absence
            WHERE date_debut_absence >= CURRENT_DATE - INTERVAL '12 months'
            GROUP BY nudoss
        ),
        CONTRAT_ACTUEL AS (
            SELECT 
                nudoss,
                categorie_contrat AS type_contrat,
                date_debut_contrat,
                ROW_NUMBER() OVER (PARTITION BY nudoss ORDER BY date_debut_contrat DESC) AS rn
            FROM fait.fait_contrat
        )
        SELECT 
            e.nudoss,
            e.matricule,
            e.nom_complet,
            e.age,
            CASE WHEN e.code_sexe = 'M' THEN 1 ELSE 0 END AS sexe_code,
            COALESCE(c.type_contrat, 'CDI') AS type_contrat,
            ROUND(EXTRACT(EPOCH FROM (CURRENT_DATE - COALESCE(c.date_debut_contrat, CURRENT_DATE))) / (365.25 * 86400), 2) AS anciennete_annees,
            COALESCE(a.nb_absences, 0) AS nb_absences,
            COALESCE(a.total_jours_absence, 0) AS total_jours_absence,
            CASE WHEN e.flag_employe_actif = 0 THEN 1 ELSE 0 END AS est_parti
        FROM dim.dim_employe e
        LEFT JOIN CONTRAT_ACTUEL c ON e.nudoss = c.nudoss AND c.rn = 1
        LEFT JOIN ABSENCES_AGG a ON e.nudoss = a.nudoss
        WHERE e.age BETWEEN 18 AND 70;
    """)

    print("📊 Extraction en cours...")
    df = pd.read_sql(query, engine)

    print(f"✅ {len(df)} employés extraits avec succès")
    print(f"   - Taux turnover : {df['est_parti'].mean()*100:.1f}%")

    # Création du dossier data s'il n'existe pas
    output_path = Path("data/employes_qlik_historique.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)

    print(f"💾 Fichier sauvegardé : {output_path.resolve()}")
    return df

# ====================== LANCEMENT AUTOMATIQUE ======================
if __name__ == "__main__":
    extract_employee_history()