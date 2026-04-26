"""
Liste toutes les bases de données PostgreSQL disponibles
"""
import psycopg2
import os

# Connexion au serveur PostgreSQL (database postgres par défaut)
conn = psycopg2.connect(
    host=os.getenv('DWH_HOST', 'localhost'),
    port=os.getenv('DWH_PORT', '5432'),
    database='postgres',  # Base système pour lister toutes les BDs
    user=os.getenv('DWH_USER', 'hr_user'),
    password=os.getenv('DWH_PASSWORD', 'hr_password123')
)

cursor = conn.cursor()

# Liste toutes les bases de données
cursor.execute("""
    SELECT datname 
    FROM pg_database 
    WHERE datistemplate = false
    ORDER BY datname;
""")

databases = cursor.fetchall()

print("\n📊 BASES DE DONNÉES POSTGRESQL DISPONIBLES:")
print("=" * 50)
for db in databases:
    print(f"  ✅ {db[0]}")

print("\n🔍 RECHERCHE DE 'hr_data...':")
hr_databases = [db[0] for db in databases if 'hr_data' in db[0].lower()]
if hr_databases:
    for db_name in hr_databases:
        print(f"  🎯 {db_name}")
else:
    print("  ❌ Aucune base 'hr_data...' trouvée")

cursor.close()
conn.close()

print("\n💡 Configuration actuelle dans .env:")
print(f"   DWH_DB = {os.getenv('DWH_DB', 'NON DÉFINI')}")
