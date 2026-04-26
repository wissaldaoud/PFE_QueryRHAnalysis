"""
Test de connexion directe en bypassant SQLAlchemy
"""
import os
os.environ['PGCLIENTENCODING'] = 'UTF8'
os.environ['PYTHONUTF8'] = '1'

print("=" * 60)
print("TEST CONNEXION DIRECTE PSYCOPG2")
print("=" * 60)

try:
    import psycopg2
    
    # Méthode 1: Connexion avec paramètres explicites
    print("\n1. Connexion avec paramètres séparés:")
    conn = psycopg2.connect(
        host='localhost',
        port=5432,
        database='hr_analytics_db',
        user='hr_user',
        password='hr_password123',
        client_encoding='utf8'
    )
    print("   ✓ Connexion réussie!")
    
    # Tester une requête
    cur = conn.cursor()
    cur.execute("SELECT email FROM users WHERE email = 'admin@soprahr.com' LIMIT 1")
    result = cur.fetchone()
    print(f"   User trouvé: {result[0] if result else 'None'}")
    
    conn.close()
    print("   ✓ Connexion fermée")
    
except Exception as e:
    print(f"   ✗ Erreur: {e}")
    import traceback
    traceback.print_exc()

# Méthode 2: Via SQLAlchemy sans DSN string
print("\n2. SQLAlchemy avec URL Engine:")
try:
    from sqlalchemy import create_engine
    from sqlalchemy.pool import NullPool
    from sqlalchemy import text
    
    # Créer URL manuellement sans passer par un DSN string
    engine = create_engine(
        "postgresql://hr_user:hr_password123@localhost:5432/hr_analytics_db",
        poolclass=NullPool,
        connect_args={
            "client_encoding": "utf8",
            "connect_timeout": 10
        }
    )
    
    with engine.connect() as conn:
        result = conn.execute(text("SELECT email FROM users WHERE email = 'admin@soprahr.com' LIMIT 1"))
        row = result.fetchone()
        print(f"   ✓ User trouvé: {row[0] if row else 'None'}")
        
except Exception as e:
    print(f"   ✗ Erreur SQLAlchemy: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("TESTS TERMINES")
print("=" * 60)
