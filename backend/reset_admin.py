from app.db.base import engine
from app.core.security import get_password_hash
from sqlalchemy import text

hashed = get_password_hash('admin123')
with engine.connect() as conn:
    conn.execute(text("UPDATE users SET hashed_password = :pwd WHERE email = 'admin@company.com'"), {"pwd": hashed})
    conn.commit()
    print('Mot de passe admin reset!')
