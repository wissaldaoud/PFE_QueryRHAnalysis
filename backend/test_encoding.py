"""Test encodage PostgreSQL"""
import os
import sys

# Forcer l'encodage UTF-8
os.environ['PYTHONUTF8'] = '1'
os.environ['PGCLIENTENCODING'] = 'UTF8'

# Vérifier la DSN
from app.core.config import settings

dsn = settings.DATABASE_URL
print("=" * 60)
print("TEST ENCODAGE POSTGRESQL")
print("=" * 60)
print(f"DSN length: {len(dsn)}")
print(f"DSN: {dsn}")
if len(dsn) > 103:
    print(f"Char at position 103: '{dsn[103]}' (ord: {ord(dsn[103])})")

# Tester la connexion directe avec psycopg2
print("\n" + "=" * 60)
print("TEST CONNEXION PSYCOPG2")
print("=" * 60)

try:
    import psycopg2
    # Extraire les paramètres de connexion
    conn = psycopg2.connect(
        host=settings.POSTGRES_SERVER,
        port=settings.POSTGRES_PORT,
        database=settings.POSTGRES_DB,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        client_encoding='utf8'
    )
    print("✓ Connexion PostgreSQL réussie!")
    conn.close()
except Exception as e:
    print(f"✗ Erreur connexion: {e}")
    import traceback
    traceback.print_exc()
