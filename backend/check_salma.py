from app.db.base import engine
from sqlalchemy import text

conn = engine.connect()

# Check user account
print("=" * 60)
print("COMPTE USER SALMA:")
print("=" * 60)
result = conn.execute(text("SELECT id, email, username, role, employee_id, account_status FROM users WHERE email = 'Salma.d@soprahr.com'"))
row = result.fetchone()
if row:
    print(f"✅ User trouvé:")
    print(f"   ID: {row[0]}")
    print(f"   Email: {row[1]}")
    print(f"   Username: {row[2]}")
    print(f"   Role: {row[3]}")
    print(f"   Employee ID: {row[4]} {'❌ NON LIED' if row[4] is None else '✅ Lié'}")
    print(f"   Account Status: {row[5]}")
    user_id = row[0]
    employee_id = row[4]
else:
    print("❌ Aucun compte user trouvé pour Salma.d@soprahr.com")
    user_id = None
    employee_id = None

# Check employee profile
print("\n" + "=" * 60)
print("PROFIL EMPLOYÉ SALMA:")
print("=" * 60)
result = conn.execute(text("SELECT id, employee_code, first_name, last_name, email, department_id FROM employees WHERE email = 'Salma.d@soprahr.com'"))
row = result.fetchone()
if row:
    print(f"✅ Profil employé trouvé:")
    print(f"   ID: {row[0]}")
    print(f"   Code: {row[1]}")
    print(f"   Nom: {row[2]} {row[3]}")
    print(f"   Email: {row[4]}")
    print(f"   Department ID: {row[5]} {'❌ NON ASSIGNÉ' if row[5] is None else '✅ Assigné'}")
    emp_id = row[0]
    dept_id = row[5]
else:
    print("❌ Aucun profil employé trouvé pour Salma.d@soprahr.com")
    emp_id = None
    dept_id = None

# Check department if exists
if dept_id:
    print("\n" + "=" * 60)
    print("DÉPARTEMENT DE SALMA:")
    print("=" * 60)
    result = conn.execute(text(f"SELECT id, name FROM departments WHERE id = {dept_id}"))
    row = result.fetchone()
    if row:
        print(f"✅ Département: {row[1]} (ID: {row[0]})")
        
        # Count team members
        result = conn.execute(text(f"SELECT COUNT(*) FROM employees WHERE department_id = {dept_id}"))
        count = result.fetchone()[0]
        print(f"   Membres de l'équipe: {count}")

# Diagnostic
print("\n" + "=" * 60)
print("DIAGNOSTIC:")
print("=" * 60)
if user_id is None:
    print("❌ PROBLÈME: Aucun compte user pour Salma.d@soprahr.com")
    print("   SOLUTION: Créer le compte user en allant sur /register")
elif emp_id is None:
    print("❌ PROBLÈME: Aucun profil employé pour Salma.d@soprahr.com")
    print("   SOLUTION: Créer le profil employé dans la page /employees")
elif employee_id is None:
    print("❌ PROBLÈME: Le compte user n'est pas lié au profil employé")
    print(f"   User ID: {user_id}")
    print(f"   Employee ID à lier: {emp_id}")
    print("   SOLUTION: Exécuter la commande de liaison ci-dessous")
elif dept_id is None:
    print("❌ PROBLÈME: Le profil employé n'a pas de département")
    print("   SOLUTION: Modifier le profil employé et assigner un département")
else:
    print("✅ Tout est correct!")
    print(f"   User {user_id} lié à Employee {employee_id} dans Department {dept_id}")

conn.close()
