"""
Script pour ajouter les colonnes de validation de compte
"""
from sqlalchemy import text
from app.db.base import engine

def add_columns():
    conn = engine.connect()
    try:
        # Ajouter account_status
        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS account_status VARCHAR(20) DEFAULT 'approved'"))
        # Ajouter verified_by
        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS verified_by INTEGER"))
        # Ajouter verified_at
        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS verified_at TIMESTAMP"))
        # Ajouter rejection_reason
        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS rejection_reason TEXT"))
        conn.commit()
        print("✅ Colonnes ajoutées avec succès!")
    except Exception as e:
        print(f"Note: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    add_columns()
