from sqlalchemy import text
from app.db.base import SessionLocal
from app.core.security import get_password_hash

db = SessionLocal()

try:
    # Réinitialiser le mot de passe de Karim
    new_password = "password123"
    hashed_password = get_password_hash(new_password)
    
    result = db.execute(text("""
        UPDATE users 
        SET hashed_password = :hashed_password
        WHERE email = 'karim.alaoui@soprahr.com'
    """), {"hashed_password": hashed_password})
    
    db.commit()
    
    # Vérifier
    user = db.execute(text("""
        SELECT email, username, role, employee_id
        FROM users
        WHERE email = 'karim.alaoui@soprahr.com'
    """)).fetchone()
    
    if user:
        print("✅ Mot de passe réinitialisé avec succès!")
        print(f"📧 Email: {user.email}")
        print(f"👤 Username: {user.username}")
        print(f"🔑 Nouveau mot de passe: {new_password}")
        print(f"🎭 Rôle: {user.role}")
        print(f"🆔 Employee ID: {user.employee_id}")
    else:
        print("❌ Utilisateur non trouvé")
        
except Exception as e:
    print(f"❌ Erreur: {e}")
    db.rollback()
finally:
    db.close()
