from app.db.base import SessionLocal
from sqlalchemy import text
db = SessionLocal()

# Mettre Karim Alaoui dans le dept IT (id=1)
db.execute(text("UPDATE employees SET department_id = 1, job_title = 'Manager IT' WHERE id = 269"))
db.commit()
print('✅ Employee Karim Alaoui mis dans le dept IT!')

# Verifier
r = db.execute(text('SELECT id, first_name, last_name, department_id, job_title FROM employees WHERE id = 269'))
print(f'Employee: {r.fetchone()}')

# Son equipe
print()
print('=== Équipe de Karim (dept IT) ===')
team = db.execute(text('SELECT first_name, last_name, job_title FROM employees WHERE department_id = 1'))
count = 0
for e in team:
    print(f'  - {e[0]} {e[1]} ({e[2]})')
    count += 1
print(f'\nTotal: {count} membres')

db.close()
