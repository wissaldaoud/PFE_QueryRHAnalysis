from dwh_connection import get_dwh_engine
from sqlalchemy import text

engine = get_dwh_engine()

with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_schema = 'fait' AND table_name = 'fait_affectation'
        ORDER BY ordinal_position
    """))
    
    print("Colonnes de fait.fait_affectation:")
    for row in result:
        print(f"  - {row[0]}")
