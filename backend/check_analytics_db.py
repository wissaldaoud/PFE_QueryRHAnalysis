"""
Vérifier si les tables dim/fait existent dans hr_analytics_db
"""
from dotenv import load_dotenv
load_dotenv()

import psycopg2
import os

print("=" * 70)
print("RECHERCHE TABLES QLIK DANS hr_analytics_db")
print("=" * 70)

# Connexion à hr_analytics_db (base APP principale)
conn = psycopg2.connect(
    host=os.getenv('POSTGRES_SERVER', 'localhost'),
    port=os.getenv('POSTGRES_PORT', '5432'),
    database=os.getenv('POSTGRES_DB', 'hr_analytics_db'),
    user=os.getenv('POSTGRES_USER', 'hr_user'),
    password=os.getenv('POSTGRES_PASSWORD', 'hr_password123')
)

cursor = conn.cursor()

print(f"\n🔍 Connexion à: {conn.info.dbname}")
print("-" * 70)

# Vérifier les schémas
cursor.execute("""
    SELECT schema_name 
    FROM information_schema.schemata 
    WHERE schema_name NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
    ORDER BY schema_name
""")
schemas = [row[0] for row in cursor.fetchall()]

print(f"\n📁 Schémas trouvés: {', '.join(schemas)}")

# Chercher les tables dim/fait
print("\n📊 Tables par schéma:")
print("-" * 70)

for schema in schemas:
    cursor.execute(f"""
        SELECT table_name
        FROM information_schema.tables 
        WHERE table_schema = '{schema}' 
        AND table_type = 'BASE TABLE'
        ORDER BY table_name
    """)
    tables = cursor.fetchall()
    
    if tables:
        print(f"\n  {schema}:")
        for (table_name,) in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {schema}.{table_name}")
                row_count = cursor.fetchone()[0]
                print(f"    - {table_name} ({row_count:,} lignes)")
            except Exception as e:
                print(f"    - {table_name} (erreur comptage)")

# Chercher spécifiquement les tables Qlik
tables_qlik = ['dim_employe', 'dim_calendrier', 'fait_contrat', 'fait_affectation', 'fait_absence']

print("\n" + "=" * 70)
print("🎯 RECHERCHE TABLES QLIK")
print("=" * 70)

tables_qlik_trouvees = []

for schema in schemas:
    for table in tables_qlik:
        cursor.execute(f"""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables 
                WHERE table_schema = '{schema}' 
                AND table_name = '{table}'
            )
        """)
        exists = cursor.fetchone()[0]
        
        if exists:
            cursor.execute(f"SELECT COUNT(*) FROM {schema}.{table}")
            count = cursor.fetchone()[0]
            tables_qlik_trouvees.append((schema, table, count))
            print(f"✅ {schema}.{table} ({count:,} lignes)")

if not tables_qlik_trouvees:
    print("\n❌ Aucune table Qlik trouvée dans hr_analytics_db")
    print("\n💡 Les tables dim.* et fait.* n'existent dans aucune base!")
    print("\n🔧 SOLUTIONS POSSIBLES:")
    print("   1. Les créer en transformant les tables existantes (employees → dim_employe)")
    print("   2. Vérifier si Qlik se connecte à une AUTRE base PostgreSQL")
    print("   3. Créer un script ETL pour peupler dim/fait depuis les tables actuelles")

cursor.close()
conn.close()

print("\n" + "=" * 70)
