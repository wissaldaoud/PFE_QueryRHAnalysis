from sqlalchemy import text
from app.db.base import SessionLocal

db = SessionLocal()

try:
    # 1. Trouver l'ID de l'employé Karim (lié au user Karim)
    karim_user = db.execute(text("""
        SELECT employee_id FROM users WHERE email = 'karim.alaoui@soprahr.com'
    """)).fetchone()
    
    if not karim_user or not karim_user.employee_id:
        print("❌ Karim n'a pas d'employee_id")
        exit(1)
    
    karim_employee_id = karim_user.employee_id
    print(f"✓ Karim Employee ID: {karim_employee_id}")
    
    # 2. Assigner Karim comme manager de Fatima
    db.execute(text("""
        UPDATE employees
        SET manager_id = :manager_id
        WHERE email = 'fatima.alaoui@soprahr.com'
    """), {"manager_id": karim_employee_id})
    
    db.commit()
    
    # 3. Vérifier
    fatima = db.execute(text("""
        SELECT e.id, e.first_name, e.last_name, e.manager_id,
               m.first_name as mgr_first_name, m.last_name as mgr_last_name
        FROM employees e
        LEFT JOIN employees m ON e.manager_id = m.id
        WHERE e.email = 'fatima.alaoui@soprahr.com'
    """)).fetchone()
    
    print(f"\n✅ Manager assigné avec succès!")
    print(f"   Employé: {fatima.first_name} {fatima.last_name}")
    print(f"   Manager: {fatima.mgr_first_name} {fatima.mgr_last_name} (ID: {fatima.manager_id})")
    
except Exception as e:
    print(f"❌ Erreur: {e}")
    db.rollback()
finally:
    db.close()
