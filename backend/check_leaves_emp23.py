"""
Check leave_requests for employee EMP23
"""
from sqlalchemy import create_engine, text

engine = create_engine('postgresql://hranalytics:hranalytics2026@localhost:5432/hr_analytics_db?client_encoding=utf8')

with engine.connect() as conn:
    # D'abord, trouver l'ID de l'employé EMP23
    result = conn.execute(text("SELECT id FROM employees WHERE employee_code = 'EMP23'"))
    employee = result.fetchone()
    
    if employee:
        employee_id = employee[0]
        print(f"✓ Employé EMP23 trouvé, ID: {employee_id}")
        
        # Vérifier s'il y a des congés pour cet employé
        result = conn.execute(text("""
            SELECT id, leave_type, start_date, end_date, days_requested, status, created_at
            FROM leave_requests 
            WHERE employee_id = :emp_id
            ORDER BY created_at DESC
            LIMIT 10
        """), {"emp_id": employee_id})
        
        leaves = result.fetchall()
        
        if leaves:
            print(f"\n✓ {len(leaves)} congé(s) trouvé(s) pour EMP23:")
            for leave in leaves:
                print(f"  - ID={leave[0]}, Type={leave[1]}, Dates={leave[2]} to {leave[3]}, Jours={leave[4]}, Status={leave[5]}")
            
            # Compter par statut
            result = conn.execute(text("""
                SELECT status, COUNT(*), SUM(days_requested)
                FROM leave_requests 
                WHERE employee_id = :emp_id
                GROUP BY status
            """), {"emp_id": employee_id})
            
            print("\nRépartition par statut:")
            for row in result:
                print(f"  - {row[0]}: {row[1]} congé(s), {row[2]} jours au total")
        else:
            print("\n❌ Aucun congé trouvé pour EMP23")
    else:
        print("❌ Employé EMP23 non trouvé")
