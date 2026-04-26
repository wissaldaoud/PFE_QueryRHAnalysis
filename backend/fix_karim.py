from app.db.base import SessionLocal
from sqlalchemy import text
db = SessionLocal()

print('=== Users avec karim ===')
r = db.execute(text("SELECT id, email, role, employee_id FROM users WHERE email ILIKE '%karim%'"))
for u in r:
    print(f'  User: {u}')

print()
print('=== Employees avec karim ===')
r2 = db.execute(text("SELECT id, email, department_id FROM employees WHERE email ILIKE '%karim%'"))
for e in r2:
    print(f'  Employee: {e}')

# Créer un employee pour karim.alaoui si n'existe pas
print()
print('=== Création Employee pour karim.alaoui ===')
check = db.execute(text("SELECT id FROM employees WHERE email = 'karim.alaoui@soprahr.com'")).fetchone()
if not check:
    db.execute(text("""
        INSERT INTO employees (employee_code, first_name, last_name, email, hire_date, job_title, department_id, salary, employment_status)
        VALUES ('MGR-0001', 'Karim', 'Alaoui', 'karim.alaoui@soprahr.com', '2026-01-20', 'Manager IT', 1, 55000, 'active')
    """))
    db.commit()
    print('Employee créé!')
    
    # Récupérer l'ID
    new_id = db.execute(text("SELECT id FROM employees WHERE email = 'karim.alaoui@soprahr.com'")).fetchone()
    print(f'Nouveau Employee ID: {new_id[0]}')
    
    # Lier au user
    db.execute(text(f"UPDATE users SET employee_id = {new_id[0]} WHERE email = 'karim.alaoui@soprahr.com'"))
    db.commit()
    print('User lié!')
else:
    print(f'Employee existe déjà: ID={check[0]}')
    # Lier au user
    db.execute(text(f"UPDATE users SET employee_id = {check[0]} WHERE email = 'karim.alaoui@soprahr.com'"))
    db.commit()
    print('User lié!')

# Vérifier
print()
print('=== Vérification finale ===')
final = db.execute(text("SELECT id, email, role, employee_id FROM users WHERE email = 'karim.alaoui@soprahr.com'")).fetchone()
print(f'User Karim: {final}')

# Son équipe
print()
print('=== Équipe de Karim (dept IT) ===')
team = db.execute(text("SELECT first_name, last_name, job_title FROM employees WHERE department_id = 1"))
for e in team:
    print(f'  - {e[0]} {e[1]} ({e[2]})')

db.close()
