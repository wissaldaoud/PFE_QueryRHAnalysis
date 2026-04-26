"""
Script pour insérer des données de test dans PostgreSQL
Exécutez: python scripts/seed_data.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.base import SessionLocal, engine
from app.models.employee import Employee, EmploymentStatus
from app.models.department import Department
from app.models.user import User
from app.core.security import get_password_hash
from datetime import date


def seed_data():
    """Insérer des données de test"""
    db = SessionLocal()
    
    try:
        print("🌱 Insertion des données de test...")
        
        # Départements
        departments = [
            Department(name="IT", code="IT", description="Information Technology"),
            Department(name="HR", code="HR", description="Human Resources"),
            Department(name="Finance", code="FIN", description="Finance Department"),
            Department(name="Marketing", code="MKT", description="Marketing Department"),
            Department(name="Sales", code="SAL", description="Sales Department"),
        ]
        
        db.add_all(departments)
        db.commit()
        print("✅ 5 départements créés")
        
        # Employés
        employees = [
            Employee(
                employee_code="EMP001",
                first_name="Ahmed",
                last_name="Ben Ali",
                email="ahmed.benali@company.com",
                phone="+212 6 12 34 56 78",
                date_of_birth=date(1990, 5, 15),
                hire_date=date(2020, 1, 15),
                job_title="Senior Developer",
                department_id=1,
                salary=65000,
                employment_status=EmploymentStatus.ACTIVE
            ),
            Employee(
                employee_code="EMP002",
                first_name="Fatima",
                last_name="Mansouri",
                email="fatima.mansouri@company.com",
                phone="+212 6 23 45 67 89",
                date_of_birth=date(1992, 8, 20),
                hire_date=date(2021, 6, 1),
                job_title="HR Manager",
                department_id=2,
                salary=55000,
                employment_status=EmploymentStatus.ACTIVE
            ),
            Employee(
                employee_code="EMP003",
                first_name="Mohamed",
                last_name="Khalil",
                email="mohamed.khalil@company.com",
                phone="+212 6 34 56 78 90",
                date_of_birth=date(1988, 3, 10),
                hire_date=date(2019, 3, 20),
                job_title="Financial Analyst",
                department_id=3,
                salary=58000,
                employment_status=EmploymentStatus.ACTIVE
            ),
            Employee(
                employee_code="EMP004",
                first_name="Sarah",
                last_name="El Amrani",
                email="sarah.elamrani@company.com",
                phone="+212 6 45 67 89 01",
                date_of_birth=date(1995, 11, 5),
                hire_date=date(2022, 9, 1),
                job_title="Marketing Specialist",
                department_id=4,
                salary=45000,
                employment_status=EmploymentStatus.ACTIVE
            ),
            Employee(
                employee_code="EMP005",
                first_name="Youssef",
                last_name="Alami",
                email="youssef.alami@company.com",
                phone="+212 6 56 78 90 12",
                date_of_birth=date(1987, 7, 25),
                hire_date=date(2018, 5, 10),
                job_title="Sales Manager",
                department_id=5,
                salary=62000,
                employment_status=EmploymentStatus.ACTIVE,
                manager_id=None
            ),
            Employee(
                employee_code="EMP006",
                first_name="Imane",
                last_name="Bennis",
                email="imane.bennis@company.com",
                phone="+212 6 67 89 01 23",
                date_of_birth=date(1993, 2, 18),
                hire_date=date(2021, 1, 15),
                job_title="Junior Developer",
                department_id=1,
                salary=40000,
                employment_status=EmploymentStatus.ACTIVE,
                manager_id=1  # Ahmed is manager
            ),
            Employee(
                employee_code="EMP007",
                first_name="Karim",
                last_name="Ezzahiri",
                email="karim.ezzahiri@company.com",
                phone="+212 6 78 90 12 34",
                date_of_birth=date(1991, 9, 30),
                hire_date=date(2020, 8, 20),
                job_title="Accountant",
                department_id=3,
                salary=48000,
                employment_status=EmploymentStatus.ACTIVE
            ),
            Employee(
                employee_code="EMP008",
                first_name="Nadia",
                last_name="Tazi",
                email="nadia.tazi@company.com",
                date_of_birth=date(1985, 4, 12),
                hire_date=date(2017, 2, 1),
                termination_date=date(2023, 12, 31),
                job_title="Former Sales Rep",
                department_id=5,
                salary=50000,
                employment_status=EmploymentStatus.TERMINATED
            ),
        ]
        
        db.add_all(employees)
        db.commit()
        print("✅ 8 employés créés")
        
        # Utilisateurs
        users = [
            User(
                email="admin@company.com",
                username="admin",
                hashed_password=get_password_hash("admin123"),
                full_name="Admin User",
                role="admin",
                is_active=True
            ),
            User(
                email="hr@company.com",
                username="hr_manager",
                hashed_password=get_password_hash("hr123"),
                full_name="HR Manager",
                role="hr_manager",
                is_active=True
            ),
        ]
        
        db.add_all(users)
        db.commit()
        print("✅ 2 utilisateurs créés")
        
        print("\n" + "="*60)
        print("✅ DONNÉES DE TEST INSÉRÉES AVEC SUCCÈS!")
        print("="*60)
        print("\n📊 Résumé:")
        print(f"  • 5 départements")
        print(f"  • 8 employés (7 actifs, 1 terminé)")
        print(f"  • 2 utilisateurs")
        print("\n🔐 Comptes de test:")
        print("  • admin@company.com / admin123 (Admin)")
        print("  • hr@company.com / hr123 (HR Manager)")
        print("\n🌐 Testez sur: http://localhost:8000/docs")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
