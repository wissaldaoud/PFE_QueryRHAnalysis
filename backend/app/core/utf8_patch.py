"""
Patch psycopg2 pour forcer UTF-8 partout
À importer AVANT tout autre import de sqlalchemy ou psycopg2
"""
import os
import sys

# Force UTF-8 au niveau système AVANT tout import
os.environ['PYTHONUTF8'] = '1'
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PGCLIENTENCODING'] = 'UTF8'
os.environ['LC_ALL'] = 'C.UTF-8'
os.environ['LANG'] = 'C.UTF-8'

# Nettoyer les variables PostgreSQL qui peuvent causer des problèmes
for key in list(os.environ.keys()):
    if key.startswith('PG') and key not in ['PGCLIENTENCODING']:
        del os.environ[key]

# Forcer sys.stdout et stderr en UTF-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# Patcher psycopg2 avant import
import psycopg2.extensions
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)

print("✓ Patch UTF-8 appliqué pour psycopg2")
