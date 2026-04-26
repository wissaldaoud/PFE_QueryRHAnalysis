"""
Script pour lier les comptes utilisateurs existants aux employés
Basé sur la correspondance email ou username
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.base import SessionLocal


def link_users_to_employees():
    """Lier automatiquement les Users aux Employees correspondants"""
    db: Session = SessionLocal()
    
    try:
        # Récupérer tous les users sans employee_id (via SQL direct)
        result = db.execute(text("""
            SELECT id, username, email, full_name 
            FROM users 
            WHERE employee_id IS NULL
        """))
        users_without_link = result.fetchall()
        
        print(f"🔍 Trouvé {len(users_without_link)} comptes utilisateurs sans liaison employé\n")
        
        linked_count = 0
        not_found_count = 0
        
        for user in users_without_link:
            user_id, username, email, full_name = user
            print(f"👤 User: {username} ({email})")
            
            # Essayer de trouver un employé correspondant par email
            employee = None
            
            if email:
                result = db.execute(text("""
                    SELECT id, first_name, last_name 
                    FROM employees 
                    WHERE email = :email 
                    LIMIT 1
                """), {"email": email})
                employee = result.fetchone()
                
                if employee:
                    print(f"   ✅ Trouvé par email: {employee[1]} {employee[2]}")
            
            # Si pas trouvé par email, essayer par nom
            if not employee and full_name and ' ' in full_name:
                parts = full_name.split(' ', 1)
                first_name = parts[0]
                last_name = parts[1] if len(parts) > 1 else ''
                
                result = db.execute(text("""
                    SELECT id, first_name, last_name 
                    FROM employees 
                    WHERE LOWER(first_name) LIKE LOWER(:first) 
                    AND LOWER(last_name) LIKE LOWER(:last)
                    LIMIT 1
                """), {"first": f"%{first_name}%", "last": f"%{last_name}%"})
                employee = result.fetchone()
                
                if employee:
                    print(f"   ✅ Trouvé par nom: {employee[1]} {employee[2]}")
            
            # Si trouvé, créer le lien
            if employee:
                employee_id = employee[0]
                db.execute(text("""
                    UPDATE users 
                    SET employee_id = :emp_id 
                    WHERE id = :user_id
                """), {"emp_id": employee_id, "user_id": user_id})
                db.commit()
                print(f"   ✔️  Lié au Employee ID: {employee_id}")
                linked_count += 1
            else:
                print(f"   ❌ Aucun employé correspondant trouvé")
                not_found_count += 1
            
            print()
        
        print(f"\n📊 Résumé:")
        print(f"   ✅ Liés: {linked_count}")
        print(f"   ❌ Non trouvés: {not_found_count}")
        
        # Afficher les users toujours sans lien
        if not_found_count > 0:
            print(f"\n⚠️  Comptes sans liaison (nécessitent intervention manuelle):")
            result = db.execute(text("""
                SELECT username, email, full_name 
                FROM users 
                WHERE employee_id IS NULL
            """))
            users_still_unlinked = result.fetchall()
            
            for user in users_still_unlinked:
                print(f"   - {user[0]} ({user[1]}) - {user[2]}")
            
            print(f"\n💡 Pour les lier manuellement:")
            print(f"   1. Trouvez l'employee_id: SELECT id, first_name, last_name, email FROM employees;")
            print(f"   2. Liez: python link_users_to_employees.py <username> <employee_id>")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


def link_user_manual(username: str, employee_id: int):
    """Lier manuellement un user à un employee"""
    db: Session = SessionLocal()
    
    try:
        # Vérifier que le user existe
        result = db.execute(text("""
            SELECT id, username FROM users WHERE username = :username
        """), {"username": username})
        user = result.fetchone()
        
        if not user:
            print(f"❌ User '{username}' non trouvé")
            return
        
        # Vérifier que l'employee existe
        result = db.execute(text("""
            SELECT id, first_name, last_name FROM employees WHERE id = :emp_id
        """), {"emp_id": employee_id})
        employee = result.fetchone()
        
        if not employee:
            print(f"❌ Employee ID {employee_id} non trouvé")
            return
        
        # Faire le lien
        db.execute(text("""
            UPDATE users SET employee_id = :emp_id WHERE username = :username
        """), {"emp_id": employee_id, "username": username})
        db.commit()
        
        print(f"✅ User '{username}' lié à Employee '{employee[1]} {employee[2]}' (ID: {employee_id})")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) > 2:
        # Mode manuel: python link_users_to_employees.py <username> <employee_id>
        link_user_manual(sys.argv[1], int(sys.argv[2]))
    else:
        # Mode automatique
        link_users_to_employees()
