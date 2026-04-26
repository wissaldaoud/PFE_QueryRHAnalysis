import sys
sys.path.insert(0, 'C:/Users/wdaoud/Desktop/test/backend')

from app.core.config import settings
from sqlalchemy import create_engine, text

engine = create_engine(settings.SOPRA_DWH_URL)
with engine.connect() as conn:
    result = conn.execute(text('SELECT nudoss, nom, prenom FROM dim.dim_employe LIMIT 10'))
    print("Employee IDs:")
    for row in result:
        print(f"  - ID: {row[0]} | {row[1]} {row[2]}")
