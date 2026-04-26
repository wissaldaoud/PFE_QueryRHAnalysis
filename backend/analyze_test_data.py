"""
Analyser les patterns de données de test dans le DWH
"""
from dwh_connection import get_dwh_engine
from sqlalchemy import text
import pandas as pd

engine = get_dwh_engine()

print("=" * 80)
print("ANALYSE DES DONNÉES DE TEST")
print("=" * 80)

with engine.connect() as conn:
    # Employés avec patterns suspects
    result = conn.execute(text("""
        SELECT 
            COUNT(*) FILTER (WHERE nom_complet ~ '[x]{3,}') as nb_xxx,
            COUNT(*) FILTER (WHERE nom_complet ~* 'test') as nb_test,
            COUNT(*) FILTER (WHERE nom_complet ~ '^[A-Z]{1,3} [A-Z]{1,3}$') as nb_aa_aa,
            COUNT(*) FILTER (WHERE nom_complet ~ '[?]{2,}') as nb_interrogation,
            COUNT(*) FILTER (WHERE matricule ~* 'test|frw|tmp|xxx') as nb_matricule_test,
            COUNT(*) FILTER (WHERE nom_complet IS NULL OR nom_complet = '') as nb_null,
            COUNT(*) FILTER (WHERE LENGTH(nom_complet) < 5) as nb_trop_court,
            COUNT(*) as total
        FROM dim.dim_employe
        WHERE flag_employe_actif = 1
        AND age BETWEEN 18 AND 70
    """))
    
    stats = result.fetchone()
    print(f"\n📊 STATISTIQUES :")
    print(f"   Total employés actifs : {stats[7]}")
    print(f"   - Avec 'xxx'          : {stats[0]}")
    print(f"   - Avec 'test'         : {stats[1]}")
    print(f"   - Pattern 'AA Aa'     : {stats[2]}")
    print(f"   - Avec '????'         : {stats[3]}")
    print(f"   - Matricule test      : {stats[4]}")
    print(f"   - Nom null/vide       : {stats[5]}")
    print(f"   - Nom < 5 caractères  : {stats[6]}")
    
    print(f"\n❌ TOTAL LIGNES SUSPECTES : {max(stats[0], stats[1], stats[2], stats[3])}")
    
    # Exemples de données de test
    result = conn.execute(text("""
        SELECT nudoss, matricule, nom_complet, age
        FROM dim.dim_employe
        WHERE flag_employe_actif = 1
        AND (
            nom_complet ~* 'test|xxx|tmp'
            OR nom_complet ~ '^[A-Z]{1,3} [A-Z]{1,3}$'
            OR nom_complet ~ '[?]{2,}'
            OR matricule ~* 'test|frw|tmp'
            OR LENGTH(nom_complet) < 5
        )
        LIMIT 20
    """))
    
    print(f"\n🔍 EXEMPLES DE DONNÉES DE TEST :")
    print(f"{'NUDOSS':<10} | {'MATRICULE':<15} | {'NOM':<30} | {'AGE'}")
    print("-" * 80)
    for row in result:
        print(f"{row[0]:<10} | {row[1] or 'N/A':<15} | {row[2] or 'N/A':<30} | {row[3]}")

print("\n" + "=" * 80)
print("SOLUTION : Ajouter filtres SQL pour exclure ces données")
print("=" * 80)
print("""
WHERE clauses à ajouter :
  AND nom_complet !~* 'test|xxx|tmp|frw'
  AND nom_complet !~ '^[A-Z]{1,3} [A-Z]{1,3}$'
  AND nom_complet !~ '[?]{2,}'
  AND LENGTH(nom_complet) >= 5
  AND matricule !~* 'test|frw|tmp|xxx'
""")
