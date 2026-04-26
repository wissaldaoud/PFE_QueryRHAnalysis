"""Test complet de la stack auth pour identifier l'erreur encodage"""
import sys
import os

# Forcer UTF-8
os.environ['PYTHONUTF8'] = '1'
os.environ['PGCLIENTENCODING'] = 'UTF8'

sys.path.insert(0, '/Users/wdaoud/Desktop/test/backend')

print("=" * 60)
print("TEST 1: Importer les settings")
print("=" * 60)
try:
    from app.core.config import settings
    print("✓ Settings importés")
    print(f"  POSTGRES_SERVER: {settings.POSTGRES_SERVER}")
    print(f"  DATABASE_URL: {settings.DATABASE_URL[:50]}...")
except Exception as e:
    print(f"✗ Erreur: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("TEST 2: Créer le moteur SQLAlchemy")
print("=" * 60)
try:
    from sqlalchemy import create_engine
    engine = create_engine(
        settings.DATABASE_URL, 
        pool_pre_ping=True,
        connect_args={"client_encoding": "utf8"}
    )
    print("✓ Moteur créé")
except Exception as e:
    print(f"✗ Erreur: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("TEST 3: Se connecter à la base")
print("=" * 60)
try:
    with engine.connect() as conn:
        result = conn.execute("SELECT 1 as test")
        print(f"✓ Connexion réussie: {result.fetchone()}")
except Exception as e:
    print(f"✗ Erreur: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("TEST 4: Créer une session et charger un user")
print("=" * 60)
try:
    from sqlalchemy.orm import sessionmaker
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    from app.models.user import User
    user = db.query(User).filter(User.email == "admin@soprahr.com").first()
    
    if user:
        print(f"✓ User trouvé: {user.email}")
    else:
        print("⚠ User admin non trouvé")
    
    db.close()
except Exception as e:
    print(f"✗ Erreur: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("TESTS TERMINÉS")
print("=" * 60)
