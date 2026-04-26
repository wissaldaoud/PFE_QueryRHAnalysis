from app.db.base import engine
from sqlalchemy import text

conn = engine.connect()

# Vérifier les utilisateurs admin
result = conn.execute(text("SELECT id, email, username, role FROM users WHERE role = 'admin'"))
print("=== ADMINS ===")
for row in result.fetchall():
    print(row)

# Vérifier les demandes pending
result = conn.execute(text("SELECT COUNT(*) FROM leave_requests WHERE status = 'pending'"))
print(f"\n=== Demandes en attente: {result.fetchone()[0]} ===")

conn.close()
