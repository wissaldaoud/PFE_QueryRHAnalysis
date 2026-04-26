"""
Script pour vérifier et lier le compte eyamhir
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.base import SessionLocal


def check_and_link_eyamhir():
    db: Session = SessionLocal()
    
    try:
        # Vérifier le user eyamhir
        print("🔍 Recherche du compte eyamhir...")
        result = db.execute(text("""
            SELECT id, username, email, full_name, employee_id 
            FROM users 
            WHERE username = 'eyamhir'
        """))
        user = result.fetchone()
        
        if not user:
            print("❌ Compte 'eyamhir' non trouvé")
            return
        
        user_id, username, email, full_name, employee_id = user
        print(f"✅ User trouvé: {username}")
        print(f"   Email: {email}")
        print(f"   Full name: {full_name}")
        print(f"   Employee ID actuel: {employee_id}")
        
        if employee_id:
            print(f"\n✔️  Ce compte est déjà lié à l'employé ID: {employee_id}")
            return
        
        print("\n🔍 Recherche d'un employé correspondant...")
        
        # Chercher par email
        if email:
            result = db.execute(text("""
                SELECT id, first_name, last_name, email, employee_code 
                FROM employees 
                WHERE email = :email
            """), {"email": email})
            employee = result.fetchone()
            
            if employee:
                emp_id, first_name, last_name, emp_email, emp_code = employee
                print(f"✅ Trouvé par email: {first_name} {last_name} (Code: {emp_code})")
                
                # Lier
                db.execute(text("""
                    UPDATE users SET employee_id = :emp_id WHERE id = :user_id
                """), {"emp_id": emp_id, "user_id": user_id})
                db.commit()
                
                print(f"✔️  Compte '{username}' lié à l'employé ID: {emp_id}")
                return
        
        # Chercher par nom
        if full_name and ' ' in full_name:
            parts = full_name.split(' ', 1)
            first = parts[0]
            last = parts[1] if len(parts) > 1 else ''
            
            result = db.execute(text("""
                SELECT id, first_name, last_name, email, employee_code 
                FROM employees 
                WHERE LOWER(first_name) LIKE LOWER(:first) 
                AND LOWER(last_name) LIKE LOWER(:last)
            """), {"first": f"%{first}%", "last": f"%{last}%"})
            employee = result.fetchone()
            
            if employee:
                emp_id, first_name, last_name, emp_email, emp_code = employee
                print(f"✅ Trouvé par nom: {first_name} {last_name} (Code: {emp_code})")
                
                # Lier
                db.execute(text("""
                    UPDATE users SET employee_id = :emp_id WHERE id = :user_id
                """), {"emp_id": emp_id, "user_id": user_id})
                db.commit()
                
                print(f"✔️  Compte '{username}' lié à l'employé ID: {emp_id}")
                return
        
        # Pas trouvé automatiquement - afficher les employés disponibles
        print("\n⚠️  Aucune correspondance automatique trouvée")
        print("\n📋 Employés disponibles dans la base:")
        
        result = db.execute(text("""
            SELECT id, first_name, last_name, email, employee_code 
            FROM employees 
            ORDER BY id DESC
            LIMIT 20
        """))
        employees = result.fetchall()
        
        for emp in employees:
            emp_id, first_name, last_name, emp_email, emp_code = emp
            print(f"   ID {emp_id}: {first_name} {last_name} ({emp_code}) - {emp_email}")
        
        print(f"\n💡 Pour lier manuellement:")
        print(f"   python link_users_employees.py eyamhir <employee_id>")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    check_and_link_eyamhir()
