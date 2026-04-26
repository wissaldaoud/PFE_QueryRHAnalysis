from sqlalchemy import text, inspect
from app.db.base import SessionLocal, engine

db = SessionLocal()

print("\n=== STRUCTURE DE LA TABLE NOTIFICATIONS ===\n")

# Méthode 1: Utiliser l'inspecteur SQLAlchemy
inspector = inspect(engine)
if 'notifications' in inspector.get_table_names():
    columns = inspector.get_columns('notifications')
    print("Colonnes de la table notifications:")
    for col in columns:
        print(f"  - {col['name']} ({col['type']})")
else:
    print("❌ La table notifications n'existe pas!")

db.close()
