"""Vérifier les colonnes de la table fait_contrat"""
from sqlalchemy import create_engine, inspect, text
import os
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(os.getenv('DWH_CONNECTION_STRING'))
inspector = inspect(engine)

print("=" * 70)
print("COLONNES fait.fait_contrat")
print("=" * 70)
cols = inspector.get_columns('fait_contrat', schema='fait')
for c in cols:
    print(f"{c['name']:<35} {c['type']}")

print("\n" + "=" * 70)
print("ÉCHANTILLON de données")
print("=" * 70)

with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT 
            id_contrat,
            date_debut,
            date_fin,
            date_embauche,
            type_contrat,
            flag_contrat_actif
        FROM fait.fait_contrat
        WHERE date_embauche IS NOT NULL
        LIMIT 5
    """))
    
    for row in result:
        print(row)
