from app.db.base import SessionLocal
from sqlalchemy import text

db = SessionLocal()

print("=== Vérification Karim ===")
r = db.execute(text("SELECT id, email, role, employee_id FROM users WHERE email LIKE '%karim%'"))
users = r.fetchall()
for u in users:
    print(f"User: ID={u[0]}, Email={u[1]}, Role={u[2]}, Employee_id={u[3]}")

print()
r2 = db.execute(text("SELECT id, first_name, last_name, email, department_id FROM employees WHERE email LIKE '%karim%'"))
emps = r2.fetchall()
for e in emps:
    print(f"Employee: ID={e[0]}, Nom={e[1]} {e[2]}, Email={e[3]}, Dept={e[4]}")

db.close()
