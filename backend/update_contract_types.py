"""
Mettre à jour les types de contrats vides avec des valeurs par défaut
"""
from sqlalchemy import create_engine, text

engine = create_engine('postgresql://hranalytics:hranalytics2026@localhost:5432/hr_analytics_db?client_encoding=utf8')

with engine.connect() as conn:
    # Vérifier combien d'employés ont contract_type NULL
    result = conn.execute(text("""
        SELECT 
            COUNT(*) as total,
            COUNT(contract_type) as with_contract,
            COUNT(*) - COUNT(contract_type) as without_contract
        FROM employees
    """))
    
    stats = result.fetchone()
    print(f"📊 Statistiques:")
    print(f"  Total employés: {stats[0]}")
    print(f"  Avec type contrat: {stats[1]}")
    print(f"  Sans type contrat (NULL): {stats[2]}")
    
    if stats[2] > 0:
        print(f"\n🔧 Mise à jour de {stats[2]} employés...")
        
        # Mettre CDI par défaut pour tous les employés sans type de contrat
        # (vous pouvez ajuster selon vos besoins)
        result = conn.execute(text("""
            UPDATE employees 
            SET contract_type = 'CDI'
            WHERE contract_type IS NULL
        """))
        conn.commit()
        
        print(f"✅ {result.rowcount} employés mis à jour avec type 'CDI'")
        
        # Afficher quelques exemples
        result = conn.execute(text("""
            SELECT employee_code, first_name, last_name, contract_type
            FROM employees
            LIMIT 5
        """))
        
        print("\n📋 Exemples:")
        for row in result:
            print(f"  {row[0]} - {row[1]} {row[2]} - {row[3]}")
    else:
        print("\n✅ Tous les employés ont déjà un type de contrat!")
