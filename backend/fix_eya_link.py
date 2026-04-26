"""
Corriger la liaison eya.mhir -> employé ID 293
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.base import SessionLocal


db = SessionLocal()

try:
    # Mettre à jour la liaison
    db.execute(text("""
        UPDATE users 
        SET employee_id = :emp_id 
        WHERE username = :username
    """), {"emp_id": 293, "username": "eya.mhir"})
    db.commit()
    
    print("✅ Compte 'eya.mhir' lié à l'employé ID 293 (Eya Mhir avec email eya.mhir@soprahr.com)")
    
    # Vérification
    result = db.execute(text("""
        SELECT u.username, u.employee_id, e.first_name, e.last_name, e.email
        FROM users u
        LEFT JOIN employees e ON u.employee_id = e.id
        WHERE u.username = :username
    """), {"username": "eya.mhir"})
    
    row = result.fetchone()
    if row:
        print(f"✔️  Vérification: {row[0]} -> Employé: {row[2]} {row[3]} ({row[4]})")
    
except Exception as e:
    print(f"❌ Erreur: {e}")
    db.rollback()
finally:
    db.close()
