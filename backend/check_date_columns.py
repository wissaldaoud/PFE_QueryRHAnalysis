"""Vérifier les colonnes de date disponibles"""
from dwh_connection import get_dwh_engine
from sqlalchemy import text

engine = get_dwh_engine()

print("=" * 70)
print("COLONNES DE DATE dans dim.dim_employe")
print("=" * 70)

with engine.connect() as conn:
    # Toutes les colonnes
    result = conn.execute(text("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_schema = 'dim' 
        AND table_name = 'dim_employe'
        ORDER BY ordinal_position
    """))
    
    for row in result:
        if 'date' in row[0].lower() or 'embauche' in row[0].lower() or 'naiss' in row[0].lower():
            print(f"  ✓ {row[0]:<35} {row[1]}")

print("\n" + "=" * 70)
print("ÉCHANTILLON de données")
print("=" * 70)

with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT 
            nudoss,
            age,
            date_naissance,
            flag_employe_actif
        FROM dim.dim_employe
        LIMIT 5
    """))
    
    for row in result:
        print(row)

print("\n" + "=" * 70)
print("COLONNES DE DATE dans fait.fait_contrat")
print("=" * 70)

with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_schema = 'fait' 
        AND table_name = 'fait_contrat'
        ORDER BY ordinal_position
    """))
    
    for row in result:
        if 'date' in row[0].lower() or 'embauche' in row[0].lower() or 'debut' in row[0].lower():
            print(f"  ✓ {row[0]:<35} {row[1]}")

print("\n" + "=" * 70)
print("TEST: Ancienneté calculée vs duree_contrat")
print("=" * 70)

with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT 
            nudoss,
            date_debut_contrat,
            duree_contrat_jours,
            ROUND(duree_contrat_jours / 365.25, 2) AS anciennete_from_duree,
            ROUND(EXTRACT(EPOCH FROM (CURRENT_DATE - date_debut_contrat)) / (365.25 * 86400), 2) AS anciennete_from_date
        FROM fait.fait_contrat
        WHERE date_debut_contrat IS NOT NULL
        LIMIT 5
    """))
    
    print("NUDOSS | date_debut | duree_jours | anc_duree | anc_date")
    print("-" * 70)
    for row in result:
        print(f"{row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]}")
