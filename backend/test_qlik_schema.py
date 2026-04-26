"""
Test du schéma DWH utilisé par Qlik Sense
Vérifie que les tables dim et fait existent
"""
from dotenv import load_dotenv
load_dotenv()

from dwh_connection import get_dwh_engine
from sqlalchemy import text

print("=" * 70)
print("TEST SCHEMA QLIK SENSE - DATAWAREHOUSE HR")
print("=" * 70)

# Tables attendues
tables_attendues = {
    'dim': ['dim_employe', 'dim_calendrier'],
    'fait': ['fait_contrat', 'fait_affectation', 'fait_absence']
}

engine = get_dwh_engine()

print("\n🔍 Vérification des schémas...")
with engine.connect() as conn:
    # Lister les schémas
    result = conn.execute(text("""
        SELECT schema_name 
        FROM information_schema.schemata 
        WHERE schema_name IN ('dim', 'fait')
        ORDER BY schema_name
    """))
    schemas = [row[0] for row in result]
    
    if schemas:
        print(f"✅ Schémas trouvés: {', '.join(schemas)}")
    else:
        print("❌ Aucun schéma 'dim' ou 'fait' trouvé!")
        print("⚠️  La base de données n'a pas encore été chargée avec le script Qlik")

print("\n📊 Vérification des tables...")

tables_trouvees = {}
tables_manquantes = []

with engine.connect() as conn:
    for schema, tables in tables_attendues.items():
        print(f"\n  📁 Schéma: {schema}")
        tables_trouvees[schema] = []
        
        for table in tables:
            # Vérifier si la table existe
            result = conn.execute(text(f"""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_schema = '{schema}' 
                    AND table_name = '{table}'
                )
            """))
            exists = result.fetchone()[0]
            
            if exists:
                # Compter les lignes
                result_count = conn.execute(text(f"SELECT COUNT(*) FROM {schema}.{table}"))
                count = result_count.fetchone()[0]
                print(f"     ✅ {schema}.{table} ({count:,} lignes)")
                tables_trouvees[schema].append((table, count))
            else:
                print(f"     ❌ {schema}.{table} (manquante)")
                tables_manquantes.append(f"{schema}.{table}")

print("\n" + "=" * 70)
print("📈 RÉSUMÉ")
print("=" * 70)

total_tables_trouvees = sum(len(t) for t in tables_trouvees.values())
total_tables_attendues = sum(len(t) for t in tables_attendues.values())

print(f"\nTables trouvées: {total_tables_trouvees}/{total_tables_attendues}")

if total_tables_trouvees == total_tables_attendues:
    print("✅ Toutes les tables Qlik sont présentes!")
    
    # Total des enregistrements
    total_records = sum(count for tables in tables_trouvees.values() for _, count in tables)
    print(f"\n📊 Total enregistrements: {total_records:,}")
    
    print("\n✨ Le moteur de requêtes peut être utilisé avec cette base!")
    
elif total_tables_trouvees > 0:
    print("⚠️  Certaines tables sont manquantes:")
    for table_manquante in tables_manquantes:
        print(f"   - {table_manquante}")
    print("\n💡 Vérifiez que le script Qlik a bien chargé toutes les tables")
    
else:
    print("\n❌ Aucune table trouvée!")
    print("\n💡 ACTIONS À FAIRE:")
    print("   1. Vérifiez que vous êtes connecté à la bonne base:")
    print(f"      Base actuelle: {engine.url.database}")
    print("   2. Exécutez le script de chargement Qlik pour créer les tables")
    print("   3. Ou migrez les données depuis hr_analytics_db")

print("\n" + "=" * 70)

# Test d'une requête simple si possible
if 'dim_employe' in [t[0] for t in tables_trouvees.get('dim', [])]:
    print("\n🧪 TEST REQUÊTE: Exemples d'employés actifs")
    print("-" * 70)
    
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT nom_complet, age, tranche_age, libelle_sexe
            FROM dim.dim_employe
            WHERE flag_employe_actif = true
            ORDER BY nom_complet
            LIMIT 5
        """))
        
        rows = result.fetchall()
        if rows:
            for row in rows:
                print(f"  • {row[0]} - {row[1]} ans ({row[2]}) - {row[3]}")
        else:
            print("  Aucun employé actif trouvé")
    
    print("-" * 70)

print("")
