from app.db.base import engine
from sqlalchemy import text

with engine.connect() as conn:
    # Vérifier Karim (manager)
    result = conn.execute(text("""
        SELECT u.id, u.email, u.role, u.employee_id, e.department_id, d.name as dept_name
        FROM users u
        LEFT JOIN employees e ON u.employee_id = e.id
        LEFT JOIN departments d ON e.department_id = d.id
        WHERE u.role = 'manager'
    """))
    print('=== MANAGERS ===')
    for row in result.fetchall():
        print(f'User ID: {row[0]}, Email: {row[1]}, Role: {row[2]}, Employee_ID: {row[3]}, Dept_ID: {row[4]}, Dept: {row[5]}')
    
    # Vérifier les employés du département IT (id=1)
    result2 = conn.execute(text("""
        SELECT id, first_name, last_name, department_id
        FROM employees
        WHERE department_id = 1
        LIMIT 10
    """))
    print('\n=== EMPLOYES DEPT IT (id=1) ===')
    for row in result2.fetchall():
        print(f'ID: {row[0]}, Nom: {row[1]} {row[2]}, Dept: {row[3]}')
    
    # Total employés
    result3 = conn.execute(text('SELECT COUNT(*) FROM employees'))
    print(f'\nTotal employes: {result3.fetchone()[0]}')
