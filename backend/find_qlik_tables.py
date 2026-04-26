"""
Cherche les tables Qlik (dim/fait) dans TOUTES les bases de données
"""
import psycopg2
import os

QLIK_TABLES = [
    ('dim', 'dim_employe'),
    ('dim', 'dim_calendrier'),
    ('fait', 'fait_contrat'),
    ('fait', 'fait_affectation'),
    ('fait', 'fait_absence')
]

def check_database(db_name):
    """Vérifie si les tables Qlik existent dans une base donnée"""
    try:
        conn = psycopg2.connect(
            host='localhost',
            port='5432',
            database=db_name,
            user='hr_user',
            password='hr_password123'
        )
        cursor = conn.cursor()
        
        print(f"\n🔍 BASE DE DONNÉES: {db_name}")
        print("=" * 60)
        
        # Vérifier les schémas
        cursor.execute("""
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name IN ('dim', 'fait')
            ORDER BY schema_name;
        """)
        schemas = [row[0] for row in cursor.fetchall()]
        print(f"  Schémas dim/fait: {', '.join(schemas) if schemas else '❌ Aucun'}")
        
        # Vérifier chaque table Qlik
        found_tables = []
        for schema, table in QLIK_TABLES:
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = %s AND table_name = %s;
            """, (schema, table))
            exists = cursor.fetchone()[0] > 0
            
            if exists:
                # Compter les lignes
                cursor.execute(f"SELECT COUNT(*) FROM {schema}.{table};")
                row_count = cursor.fetchone()[0]
                print(f"  ✅ {schema}.{table} ({row_count} lignes)")
                found_tables.append(f"{schema}.{table}")
            else:
                print(f"  ❌ {schema}.{table} (manquante)")
        
        # Lister TOUTES les tables de la base
        cursor.execute("""
            SELECT table_schema, table_name 
            FROM information_schema.tables 
            WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
            ORDER BY table_schema, table_name;
        """)
        all_tables = cursor.fetchall()
        print(f"\n  📊 Total de {len(all_tables)} tables dans cette base:")
        for schema, table in all_tables[:10]:  # Montrer les 10 premières
            print(f"     - {schema}.{table}")
        if len(all_tables) > 10:
            print(f"     ... et {len(all_tables) - 10} autres tables")
        
        cursor.close()
        conn.close()
        
        return len(found_tables) > 0
        
    except Exception as e:
        print(f"  ❌ Erreur: {str(e)}")
        return False

# Vérifier toutes les bases de données HR
print("\n" + "=" * 60)
print("🔍 RECHERCHE DES TABLES QLIK (dim/fait)")
print("=" * 60)

databases_to_check = ['hr_datawarehouse', 'hr_analytics_db']
results = {}

for db in databases_to_check:
    results[db] = check_database(db)

print("\n" + "=" * 60)
print("📊 RÉSUMÉ")
print("=" * 60)
for db, found in results.items():
    status = "✅ TABLES TROUVÉES" if found else "❌ AUCUNE TABLE"
    print(f"  {db}: {status}")

print("\n💡 RECOMMANDATION:")
if results['hr_datawarehouse']:
    print("   Utiliser DWH_DB=hr_datawarehouse")
elif results['hr_analytics_db']:
    print("   ⚠️  Les tables sont dans hr_analytics_db, pas hr_datawarehouse!")
    print("   Changer DWH_DB=hr_analytics_db dans .env")
else:
    print("   ❌ Les tables dim/fait n'existent dans AUCUNE base!")
    print("   Vous devez exécuter le script de chargement Qlik")
