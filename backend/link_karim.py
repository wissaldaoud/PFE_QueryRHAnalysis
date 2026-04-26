"""Script pour lier Karim à un employé et département"""
from app.db.base import SessionLocal
from sqlalchemy import text

db = SessionLocal()

# 1. Trouver l'employee Karim
print("=== Recherche Employee Karim ===")
result = db.execute(text("SELECT id, email, department_id FROM employees WHERE email ILIKE '%karim%'"))
karim_emp = result.fetchone()

if karim_emp:
    print(f"Employee trouvé: ID={karim_emp[0]}, Email={karim_emp[1]}, Dept={karim_emp[2]}")
    
    # 2. Mettre à jour le User
    db.execute(text(f"UPDATE users SET employee_id = {karim_emp[0]} WHERE email ILIKE '%karim%'"))
    db.commit()
    print("✅ User Karim lié à son Employee!")
    
    # 3. Voir son équipe
    print(f"\n=== Équipe de Karim (dept {karim_emp[2]}) ===")
    team = db.execute(text(f"SELECT first_name, last_name, job_title FROM employees WHERE department_id = {karim_emp[2]} LIMIT 10"))
    for e in team:
        print(f"  - {e[0]} {e[1]} ({e[2]})")
else:
    print("❌ Employee Karim non trouvé")
    # Voir tous les users
    print("\nUsers existants:")
    users = db.execute(text("SELECT email, role FROM users"))
    for u in users:
        print(f"  - {u[0]} ({u[1]})")

db.close()
print("\n✅ Terminé!")
