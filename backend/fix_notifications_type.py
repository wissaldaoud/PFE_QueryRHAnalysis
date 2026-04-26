from sqlalchemy import text
from app.db.base import SessionLocal

db = SessionLocal()

try:
    result = db.execute(text("""
        UPDATE notifications 
        SET type = 'leave_request' 
        WHERE type = 'leave_pending'
    """))
    db.commit()
    print(f"✅ {result.rowcount} notifications corrigées (leave_pending → leave_request)")
except Exception as e:
    print(f"❌ Erreur: {e}")
    db.rollback()
finally:
    db.close()
