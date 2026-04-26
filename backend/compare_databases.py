"""
Vérifier où sont les données
"""
from sqlalchemy import create_engine, text

print("=" * 60)
print("VÉRIFICATION DES DEUX BASES DE DONNÉES")
print("=" * 60)

# Test hr_analytics_db
print("\n1️⃣  BASE: hr_analytics_db")
print("-" * 60)
try:
    engine = create_engine('postgresql://hr_user:hr_password123@localhost:5432/hr_analytics_db')
    conn = engine.connect()
    
    result = conn.execute(text("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name
    """))
    tables = [row[0] for row in result]
    print(f"   Tables: {len(tables)}")
    
    if 'employees' in tables:
        result = conn.execute(text("SELECT COUNT(*) FROM employees"))
        print(f"   👥 Employés: {result.fetchone()[0]}")
    
    if 'departments' in tables:
        result = conn.execute(text("SELECT COUNT(*) FROM departments"))
        print(f"   🏢 Départements: {result.fetchone()[0]}")
    
    if 'leave_requests' in tables:
        result = conn.execute(text("SELECT COUNT(*) FROM leave_requests"))
        print(f"   📋 Congés: {result.fetchone()[0]}")
    
    conn.close()
    status_analytics = "✅ CONTIENT DES DONNÉES"
except Exception as e:
    status_analytics = f"❌ ERREUR: {str(e)}"
    print(f"   {status_analytics}")

# Test hr_datawarehouse
print("\n2️⃣  BASE: hr_datawarehouse")
print("-" * 60)
try:
    engine = create_engine('postgresql://hr_user:hr_password123@localhost:5432/hr_datawarehouse')
    conn = engine.connect()
    
    result = conn.execute(text("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name
    """))
    tables = [row[0] for row in result]
    print(f"   Tables: {len(tables)}")
    
    if len(tables) == 0:
        status_warehouse = "⚠️  BASE VIDE"
    else:
        if 'employees' in tables:
            result = conn.execute(text("SELECT COUNT(*) FROM employees"))
            print(f"   👥 Employés: {result.fetchone()[0]}")
        
        if 'departments' in tables:
            result = conn.execute(text("SELECT COUNT(*) FROM departments"))
            print(f"   🏢 Départements: {result.fetchone()[0]}")
        
        status_warehouse = "✅ CONTIENT DES DONNÉES"
    
    conn.close()
except Exception as e:
    status_warehouse = f"❌ ERREUR: {str(e)}"
    print(f"   {status_warehouse}")

print("\n" + "=" * 60)
print("DIAGNOSTIC:")
print("=" * 60)
print(f"hr_analytics_db   : {status_analytics}")
print(f"hr_datawarehouse  : {status_warehouse}")
print("\n💡 RECOMMANDATION:")
if "VIDE" in status_warehouse:
    print("   Option 1: Utiliser hr_analytics_db (contient les données)")
    print("   Option 2: Migrer hr_analytics_db → hr_datawarehouse")
