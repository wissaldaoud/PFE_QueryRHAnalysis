from app.services.query_engine_service import QueryEngineService
from app.db.base import SessionLocal

db = SessionLocal()
s = QueryEngineService(db)

sql = "SELECT code_sexe, libelle_sexe, COUNT(*) as nb FROM dim.dim_employe GROUP BY code_sexe, libelle_sexe ORDER BY nb DESC;"
rows, _ = s._execute_on_dwh(sql)

print("\nMapping sexe dans la BDD:")
print("=" * 60)
for r in rows:
    print(f"code_sexe = '{r['code_sexe']}'  →  libelle_sexe = '{r['libelle_sexe']}'  ({r['nb']} employés)")

db.close()
