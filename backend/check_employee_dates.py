"""
Check if employees have date_of_birth and hire_date
"""
from app.db.base import SessionLocal
from app.models.employee import Employee

db = SessionLocal()

try:
    # Get first 10 employees
    employees = db.query(Employee).limit(10).all()
    
    print(f"Checking {len(employees)} employees:\n")
    
    has_birth = 0
    has_hire = 0
    
    for emp in employees:
        print(f"Employee ID={emp.id}, Code={emp.employee_code}")
        print(f"  Name: {emp.first_name} {emp.last_name}")
        print(f"  Date of birth: {emp.date_of_birth} (type: {type(emp.date_of_birth)})")
        print(f"  Hire date: {emp.hire_date} (type: {type(emp.hire_date)})")
        print(f"  Contract: {emp.contract_type}")
        print()
        
        if emp.date_of_birth:
            has_birth += 1
        if emp.hire_date:
            has_hire += 1
    
    print(f"\nSummary:")
    print(f"  Employees with date_of_birth: {has_birth}/{len(employees)}")
    print(f"  Employees with hire_date: {has_hire}/{len(employees)}")
    
finally:
    db.close()
