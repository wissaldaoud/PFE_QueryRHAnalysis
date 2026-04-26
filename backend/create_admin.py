"""
Script pour créer ou réinitialiser le compte administrateur - Version SQL directe
"""
import sys
sys.path.insert(0, ".")

from sqlalchemy import text
from app.db.base import SessionLocal, engine
from app.core.security import get_password_hash

def create_admin():
    """Créer ou réinitialiser le compte admin avec SQL direct"""
    db = SessionLocal()
    
    try:
        # Hash du mot de passe
        hashed_password = get_password_hash("admin123456789")
        
        # Vérifier si admin existe avec SQL direct
        result = db.execute(text("SELECT id FROM users WHERE username = 'admin'"))
        admin_row = result.fetchone()
        
        if admin_row:
            print("✅ Compte admin trouvé. Réinitialisation du mot de passe...")
            db.execute(text("""
                UPDATE users 
                SET hashed_password = :pwd, is_active = true, role = 'admin'
                WHERE username = 'admin'
            """), {"pwd": hashed_password})
            db.commit()
            print("✅ Mot de passe admin réinitialisé!")
        else:
            print("📝 Création du compte admin...")
            db.execute(text("""
                INSERT INTO users (email, username, full_name, hashed_password, is_active, role, account_status)
                VALUES ('admin@soprahr.com', 'admin', 'Administrateur', :pwd, true, 'admin', 'approved')
            """), {"pwd": hashed_password})
            db.commit()
            print("✅ Compte admin créé avec succès!")
        
        print(f"""
╔════════════════════════════════════════╗
║   COMPTE ADMINISTRATEUR                ║
╠════════════════════════════════════════╣
║ Username: admin                        ║
║ Password: admin123456789               ║
║ Email: admin@soprahr.com               ║
║ Role: admin                            ║
╚════════════════════════════════════════╝
        """)
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()
