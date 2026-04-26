"""
Lier eya.mhir à son employé
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.base import SessionLocal


def link_eya_mhir():
    db: Session = SessionLocal()
    
    try:
        # Chercher l'employé avec email similaire
        print("🔍 Recherche de l'employé Eya Mhir...")
        result = db.execute(text("""
            SELECT id, first_name, last_name, email, employee_code 
            FROM employees 
            WHERE email LIKE '%eya%' OR first_name LIKE '%Eya%' OR first_name LIKE '%eya%'
            LIMIT 10
        """))
        employees = result.fetchall()
        
        if not employees:
            print("❌ Aucun employé trouvé avec le prénom Eya")
            print("\n📋 Affichage des 10 derniers employés:")
            result = db.execute(text("""
                SELECT id, first_name, last_name, email, employee_code 
                FROM employees 
                ORDER BY id DESC 
                LIMIT 10
            """))
            for emp in result.fetchall():
                print(f"   ID {emp[0]}: {emp[1]} {emp[2]} - {emp[3]} ({emp[4]})")
            return
        
        print(f"✅ Trouvé {len(employees)} employé(s):")
        for emp in employees:
            print(f"   ID {emp[0]}: {emp[1]} {emp[2]} - {emp[3]} ({emp[4]})")
        
        # Lier au premier résultat
        emp_id = employees[0][0]
        emp_name = f"{employees[0][1]} {employees[0][2]}"
        
        print(f"\n🔗 Liaison du compte 'eya.mhir' à l'employé ID {emp_id} ({emp_name})...")
        
        db.execute(text("""
            UPDATE users 
            SET employee_id = :emp_id 
            WHERE username = 'eya.mhir'
        """), {"emp_id": emp_id})
        db.commit()
        
        print(f"✅ Liaison réussie!")
        
        # Vérification
        result = db.execute(text("""
            SELECT username, employee_id 
            FROM users 
            WHERE username = 'eya.mhir'
        """))
        check = result.fetchone()
        print(f"✔️  Vérification: {check[0]} -> employee_id = {check[1]}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    link_eya_mhir()
