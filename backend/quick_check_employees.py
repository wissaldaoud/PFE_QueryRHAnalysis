"""Quick check for employees in database"""
from sqlalchemy import create_engine, text

# Connecter directement à la base de données
engine = create_engine('postgresql://postgres:password@localhost:5432/hr_analytics')

with engine.connect() as conn:
    # Compter les employés
    result = conn.execute(text('SELECT COUNT(*) FROM employees'))
    total = result.scalar()
    print(f"✓ Total employees in database: {total}")
    
    if total > 0:
        # Afficher quelques exemples
        result = conn.execute(text('SELECT id, employee_code, first_name, last_name, employment_status FROM employees LIMIT 5'))
        print("\nFirst 5 employees:")
        for row in result:
            print(f"  ID={row[0]}, Code={row[1]}, Name={row[2]} {row[3]}, Status={row[4]}")
    else:
        print("\n❌ No employees found in database!")
