from sqlalchemy import create_engine, text
import os

# DWH connection
dwh_url = (
    f"postgresql://{os.getenv('DWH_USER','hr_user')}"
    f":{os.getenv('DWH_PASSWORD','hr_password123')}"
    f"@{os.getenv('DWH_HOST','localhost')}"
    f":{os.getenv('DWH_PORT','5432')}"
    f"/{os.getenv('DWH_DB','hr_datawarehouse')}"
)

engine = create_engine(dwh_url)
conn = engine.connect()

# 1. Vérifier les colonnes disponibles
print("🔍 Colonnes de dim.dim_employe:")
result = conn.execute(text("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_schema = 'dim' AND table_name = 'dim_employe'
    ORDER BY ordinal_position
"""))
for row in result:
    print(f"   - {row[0]}: {row[1]}")

print("\n📋 Premiers employés actifs:")
result = conn.execute(text("""
    SELECT nudoss, nom, prenom
    FROM dim.dim_employe 
    WHERE flag_employe_actif = 1
    LIMIT 10
"""))
for row in result:
    print(f"   #{row[0]}: '{row[1]}' '{row[2]}'")

conn.close()
engine.dispose()
