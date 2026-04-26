"""
Test et mise à jour via requête SQL simple
"""
import psycopg2

# Connexion à la base de données
conn = psycopg2.connect(
    host="localhost",
    database="hr_analytics_db",
    user="hranalytics",
    password="hranalytics2026"
)

cur = conn.cursor()

# Vérifier les types de contrats actuels
cur.execute("""
    SELECT 
        contract_type,
        COUNT(*) as count
    FROM employees
    GROUP BY contract_type
    ORDER BY count DESC
""")

print("📊 Types de contrats actuels:")
for row in cur.fetchall():
    contract_type = row[0] if row[0] else "NULL (vide)"
    count = row[1]
    print(f"  {contract_type}: {count} employés")

# Compter les NULL
cur.execute("SELECT COUNT(*) FROM employees WHERE contract_type IS NULL")
null_count = cur.fetchone()[0]

if null_count > 0:
    print(f"\n🔧 Mise à jour de {null_count} employés sans type de contrat...")
    
    # Mettre CDI par défaut
    cur.execute("""
        UPDATE employees 
        SET contract_type = 'CDI'
        WHERE contract_type IS NULL
    """)
    
    conn.commit()
    print(f"✅ {cur.rowcount} employés mis à jour avec 'CDI'")
else:
    print("\n✅ Tous les employés ont déjà un type de contrat")

cur.close()
conn.close()
