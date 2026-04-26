from app.db.base import engine
from sqlalchemy import text

conn = engine.connect()

print("=== Tous les utilisateurs ===")
result = conn.execute(text("SELECT id, email, role FROM users ORDER BY id LIMIT 20"))
for row in result.fetchall():
    print(row)

conn.close()
