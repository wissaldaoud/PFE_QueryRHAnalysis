from app.db.base import SessionLocal
from app.core.security import get_password_hash
from sqlalchemy import text

db = SessionLocal()

# Reset password for Karim
new_hash = get_password_hash('Manager2026!')
db.execute(text(f"UPDATE users SET hashed_password = '{new_hash}' WHERE email = 'karim.alaoui@soprahr.com'"))
db.commit()
print('Mot de passe de Karim reinitialise a: Manager2026!')
db.close()
