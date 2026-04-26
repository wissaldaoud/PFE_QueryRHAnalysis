from dwh_connection import get_dwh_engine
from sqlalchemy import text

engine = get_dwh_engine()

print("Test regex pour filtrer caractères répétés")
print("=" * 80)

# Test 1: Pattern basique
with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT 
            nom_complet,
            nom_complet ~ '(.)\\1{3,}' AS has_repeats
        FROM dim.dim_employe
        WHERE nom_complet IN ('AAAA Aaaa', 'AAAAA Aaaaaa', 'ABASSI Mehdi', 'GASCOIGNE Lawrence')
    """))
    
    print("\nTest du pattern '(.)\\1{3,}' :")
    for row in result:
        print(f"  {row[0]:<30} → Match: {row[1]}")

# Compter combien seraient filtrés
with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT 
            COUNT(*) FILTER (WHERE nom_complet ~ '(.)\\1{3,}') as avec_repeats,
            COUNT(*) as total
        FROM dim.dim_employe
        WHERE flag_employe_actif = 1
        AND age BETWEEN 18 AND 70
    """))
    
    stats = result.fetchone()
    print(f"\n📊 Sur {stats[1]} employés actifs :")
    print(f"   {stats[0]} ont 4+ caractères identiques consécutifs")
