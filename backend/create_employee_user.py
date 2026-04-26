from sqlalchemy import text
from app.db.base import engine
from app.core.security import get_password_hash

# Créer un utilisateur employé lié à l'employé ID 1
conn = engine.connect()

# Hasher le mot de passe
hashed = get_password_hash("Employee123!")

# Insérer l'utilisateur
conn.execute(text("""
    INSERT INTO users (email, username, hashed_password, full_name, role, is_active, employee_id)
    VALUES (:email, :username, :password, :name, 'employee', true, 1)
"""), {
    "email": "ahmed.bennani@company.com",
    "username": "ahmed.bennani",
    "password": hashed,
    "name": "Ahmed Bennani"
})

conn.commit()
conn.close()

print("✅ Utilisateur employé créé: ahmed.bennani@company.com / Employee123!")
