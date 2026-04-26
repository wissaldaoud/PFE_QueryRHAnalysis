"""Test simple de la connexion DWH"""
from dotenv import load_dotenv
load_dotenv()

from dwh_connection import test_dwh_connection, get_dwh_tables

print("=" * 60)
print("TEST CONNEXION DWH")
print("=" * 60)

# Test connexion
success = test_dwh_connection()

if success:
    print("\n📊 Récupération des tables...")
    tables = get_dwh_tables()
    print(f"\n✅ {len(tables)} table(s) trouvée(s):")
    for table in tables:
        print(f"   - {table}")
else:
    print("\n❌ La connexion a échoué. Vérifiez:")
    print("   1. PostgreSQL est démarré")
    print("   2. La base 'hr_datawarehouse' existe")
    print("   3. Les credentials dans .env sont corrects")

print("\n" + "=" * 60)
