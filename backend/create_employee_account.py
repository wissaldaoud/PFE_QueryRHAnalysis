"""
Créer un compte utilisateur employé pour tester le workflow de congés
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
from app.core.config import settings

# Configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_employee_test_account():
    """Créer un compte employé de test"""
    engine = create_engine(settings.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Trouver un employé sans compte utilisateur
        result = session.execute(text("""
            SELECT e.id, e.first_name, e.last_name, e.email, e.department_id
            FROM employees e
            LEFT JOIN users u ON u.employee_id = e.id
            WHERE u.id IS NULL
            AND e.employment_status = 'active'
            LIMIT 1
        """))
        
        employee = result.fetchone()
        
        if not employee:
            print("❌ Aucun employé disponible sans compte utilisateur")
            return
        
        emp_id, first_name, last_name, email, dept_id = employee
        
        # Créer le compte utilisateur
        hashed_password = pwd_context.hash("password123")
        
        session.execute(text("""
            INSERT INTO users (
                email, username, full_name, hashed_password, 
                role, is_active, account_status, employee_id
            ) VALUES (
                :email, :username, :full_name, :hashed_password,
                'employee', TRUE, 'approved', :employee_id
            )
        """), {
            'email': email,
            'username': email.split('@')[0],
            'full_name': f"{first_name} {last_name}",
            'hashed_password': hashed_password,
            'employee_id': emp_id
        })
        
        session.commit()
        
        print("\n✅ Compte employé créé avec succès!")
        print(f"\n📧 Email: {email}")
        print(f"🔑 Mot de passe: password123")
        print(f"👤 Nom: {first_name} {last_name}")
        print(f"🆔 Employee ID: {emp_id}")
        print(f"🏢 Département ID: {dept_id}")
        
        return email
        
    except Exception as e:
        session.rollback()
        print(f"❌ Erreur: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    print("🔄 Création d'un compte employé de test...")
    create_employee_test_account()
