from app.db.base import SessionLocal
from sqlalchemy import text

db = SessionLocal()

r = db.execute(text("SELECT id, role, employee_id FROM users WHERE email = 'karim.alaoui@soprahr.com'"))
user = r.fetchone()
print(f"User Karim: ID={user[0]}, Role='{user[1]}', Employee_ID={user[2]}")

# Check employee
r2 = db.execute(text(f"SELECT id, department_id FROM employees WHERE id = {user[2]}"))
emp = r2.fetchone()
print(f"Employee: ID={emp[0]}, Dept={emp[1]}")

# Check UserRole enum
from app.models.user import UserRole
print(f"\nUserRole.manager = '{UserRole.manager}'")
print(f"UserRole.manager.value = '{UserRole.manager.value}'")
print(f"Karim role == UserRole.manager? {user[1] == UserRole.manager.value}")

db.close()
