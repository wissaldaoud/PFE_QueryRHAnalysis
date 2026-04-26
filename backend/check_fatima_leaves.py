from sqlalchemy import text
from app.db.base import SessionLocal

db = SessionLocal()

print("\n=== VÉRIFICATION DEMANDES DE CONGÉ ET NOTIFICATIONS ===\n")

# 1. Vérifier l'employé Fatima
print("1. EMPLOYÉ FATIMA:")
fatima_employee = db.execute(text("""
    SELECT e.id, e.first_name, e.last_name, e.email, e.manager_id,
           m.first_name as manager_first_name, m.last_name as manager_last_name
    FROM employees e
    LEFT JOIN employees m ON e.manager_id = m.id
    WHERE e.email = 'fatima.alaoui@soprahr.com'
""")).fetchone()

if fatima_employee:
    print(f"   ID: {fatima_employee.id}")
    print(f"   Nom: {fatima_employee.first_name} {fatima_employee.last_name}")
    print(f"   Manager ID: {fatima_employee.manager_id}")
    if fatima_employee.manager_id:
        print(f"   Manager: {fatima_employee.manager_first_name} {fatima_employee.manager_last_name}")
    else:
        print(f"   ⚠️ PAS DE MANAGER ASSIGNÉ!")
    print()
else:
    print("   ❌ Employé Fatima non trouvé!")
    print()

# 2. Vérifier les demandes de congé de Fatima
print("2. DEMANDES DE CONGÉ DE FATIMA:")
if fatima_employee:
    leaves = db.execute(text("""
        SELECT id, leave_type, start_date, end_date, status, created_at, reason
        FROM leave_requests
        WHERE employee_id = :emp_id
        ORDER BY created_at DESC
        LIMIT 5
    """), {"emp_id": fatima_employee.id}).fetchall()
    
    if leaves:
        for leave in leaves:
            print(f"   - ID: {leave.id}")
            print(f"     Type: {leave.leave_type}")
            print(f"     Dates: {leave.start_date} → {leave.end_date}")
            print(f"     Statut: {leave.status}")
            print(f"     Créé le: {leave.created_at}")
            if leave.reason:
                print(f"     Raison: {leave.reason}")
            print()
    else:
        print("   ℹ️ Aucune demande de congé trouvée")
        print()

# 3. Vérifier le user Karim
print("3. UTILISATEUR KARIM (MANAGER):")
karim_user = db.execute(text("""
    SELECT id, email, username, role, employee_id
    FROM users
    WHERE email = 'karim.alaoui@soprahr.com'
""")).fetchone()

if karim_user:
    print(f"   User ID: {karim_user.id}")
    print(f"   Email: {karim_user.email}")
    print(f"   Rôle: {karim_user.role}")
    print(f"   Employee ID: {karim_user.employee_id}")
    print()

# 4. Vérifier les notifications de Karim
print("4. NOTIFICATIONS DE KARIM:")
if karim_user:
    notifications = db.execute(text("""
        SELECT id, type, message, is_read, created_at, leave_request_id
        FROM notifications
        WHERE user_id = :user_id
        ORDER BY created_at DESC
        LIMIT 10
    """), {"user_id": karim_user.id}).fetchall()
    
    if notifications:
        for notif in notifications:
            print(f"   - ID: {notif.id}")
            print(f"     Type: {notif.type}")
            print(f"     Message: {notif.message}")
            print(f"     Lu: {notif.is_read}")
            print(f"     Leave Request ID: {notif.leave_request_id}")
            print(f"     Créé le: {notif.created_at}")
            print()
    else:
        print("   ℹ️ Aucune notification trouvée")
        print()

# 5. Vérifier tous les managers dans la base
print("5. TOUS LES MANAGERS:")
managers = db.execute(text("""
    SELECT DISTINCT e.id, e.first_name, e.last_name, e.email, u.email as user_email
    FROM employees e
    LEFT JOIN users u ON e.id = u.employee_id
    WHERE e.id IN (SELECT DISTINCT manager_id FROM employees WHERE manager_id IS NOT NULL)
    ORDER BY e.id
""")).fetchall()

for mgr in managers:
    print(f"   - {mgr.first_name} {mgr.last_name} (ID: {mgr.id})")
    print(f"     Email employé: {mgr.email}")
    print(f"     Email user: {mgr.user_email}")
    print()

db.close()
