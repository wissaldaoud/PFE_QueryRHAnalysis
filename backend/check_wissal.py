from app.db.base import engine
from sqlalchemy import text

conn = engine.connect()
result = conn.execute(text("SELECT id, email, role FROM users WHERE email = 'daoudwissal2000@gmail.com'"))
row = result.fetchone()
print('User daoudwissal2000:', row)
conn.close()
