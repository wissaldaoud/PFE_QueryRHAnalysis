"""Vérifier les employés dans la base"""
from sqlalchemy import create_engine, text
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/hr_analytics")
engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    # Compter tous les employés
    result = conn.execute(text("SELECT COUNT(*) FROM employees"))
    total = result.scalar()
    print(f"📊 Total employés dans la base : {total}")
    
    # Compter par statut
    result = conn.execute(text("""
        SELECT employment_status, COUNT(*) 
        FROM employees 
        GROUP BY employment_status
    """))
    print("\n📋 Par statut :")
    for row in result:
        print(f"   - {row[0]}: {row[1]}")
    
    # Afficher les 10 premiers
    result = conn.execute(text("""
        SELECT id, employee_code, first_name, last_name, job_title, employment_status
        FROM employees 
        LIMIT 10
    """))
    
    print(f"\n👥 Vos employés :\n")
    print(f"{'ID':<5} | {'CODE':<10} | {'NOM':<30} | {'POSTE':<20} | {'STATUT'}")
    print("-" * 90)
    for row in result:
        name = f"{row[2] or ''} {row[3] or ''}".strip() or "Non renseigné"
        print(f"{row[0]:<5} | {row[1] or 'N/A':<10} | {name:<30} | {row[4] or 'N/A':<20} | {row[5]}")

print("\n💡 Pour faire des prédictions, vos employés doivent avoir :")
print("   - employment_status = 'active'")
print("   - date_of_birth et hire_date renseignés")
