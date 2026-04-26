"""
FIX : Créer endpoint pour charger employés DWH avec ancienneté correcte
"""
from dwh_connection import get_dwh_engine
from sqlalchemy import text
import pandas as pd

engine = get_dwh_engine()

print("=" * 80)
print("VÉRIFICATION DES DONNÉES DWH")
print("=" * 80)

with engine.connect() as conn:
    # Compter employés actifs
    result = conn.execute(text("""
        SELECT COUNT(*) 
        FROM dim.dim_employe 
        WHERE age BETWEEN 18 AND 70
        AND flag_employe_actif = 1
    """))
    print(f"\n✅ Employés ACTIFS dans DWH : {result.scalar()}")
    
    # Vérifier ancienneté avec nouveau calcul
    result = conn.execute(text("""
        WITH CONTRAT_ACTUEL AS (
            SELECT 
                nudoss,
                MIN(date_debut_contrat) OVER (PARTITION BY nudoss) AS date_premiere_embauche,
                ROW_NUMBER() OVER (PARTITION BY nudoss ORDER BY date_debut_contrat DESC) AS rn
            FROM fait.fait_contrat
        )
        SELECT 
            e.nudoss,
            e.nom_complet,
            e.age,
            ROUND(
                CAST(
                    EXTRACT(EPOCH FROM (CURRENT_DATE - COALESCE(c.date_premiere_embauche, CURRENT_DATE))) 
                    / (365.25 * 86400) 
                AS NUMERIC), 
                2
            ) AS anciennete_annees,
            e.flag_employe_actif
        FROM dim.dim_employe e
        LEFT JOIN CONTRAT_ACTUEL c ON e.nudoss = c.nudoss AND c.rn = 1
        WHERE e.flag_employe_actif = 1
        AND e.age BETWEEN 18 AND 70
        ORDER BY e.nudoss
        LIMIT 10
    """))
    
    print("\n📊 ÉCHANTILLON avec ancienneté corrigée :")
    print(f"{'NUDOSS':<10} | {'NOM':<30} | {'AGE':<5} | {'ANCIENNETÉ':<12} | {'ACTIF'}")
    print("-" * 80)
    
    for row in result:
        print(f"{row[0]:<10} | {row[1]:<30} | {row[2]:<5} | {row[3]:<12} | {row[4]}")

print("\n" + "=" * 80)
print("SOLUTION : Créer endpoint /api/v1/hr-analytics/employees-dwh")
print("=" * 80)
print("""
Endpoint à créer qui :
1. Charge les employés ACTIFS du DWH avec ancienneté correcte
2. Retourne format compatible avec le frontend
3. Le frontend appelle ce nouvel endpoint au lieu de /employees
""")
