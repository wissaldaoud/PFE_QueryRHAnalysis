from sqlalchemy.orm import Session
from app.db.base import SessionLocal, engine
from sqlalchemy import text

db = SessionLocal()

print("\n=== TOUS LES UTILISATEURS ===\n")

# Requête SQL directe pour éviter les problèmes d'imports
result = db.execute(text("""
    SELECT u.id, u.email, u.username, u.role, u.is_active, u.employee_id, u.hashed_password,
           e.first_name, e.last_name
    FROM users u
    LEFT JOIN employees e ON u.employee_id = e.id
    ORDER BY u.id
"""))

users = result.fetchall()

for user in users:
    print(f"📧 Email: {user.email}")
    print(f"   Username: {user.username}")
    print(f"   Role: {user.role}")
    print(f"   Active: {user.is_active}")
    print(f"   Employee ID: {user.employee_id}")
    if user.first_name:
        print(f"   Employee Name: {user.first_name} {user.last_name}")
    print(f"   Password Hash: {user.hashed_password[:50]}...")
    print()

db.close()
