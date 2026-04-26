"""Vérifier si les tables/colonnes contiennent des accents"""
import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='hr_analytics_db',
    user='hr_user',
    password='hr_password123',
    client_encoding='utf8'
)

cur = conn.cursor()

# Lister toutes les tables
cur.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public'
    ORDER BY table_name;
""")

tables = [row[0] for row in cur.fetchall()]

print("=" * 60)
print("TABLES DANS hr_analytics_db:")
print("=" * 60)
for table in tables:
    print(f"  - {table}")
    # Vérifier les colonnes de chaque table
    cur.execute(f"""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = '{table}'
        LIMIT 5;
    """)
    columns = cur.fetchall()
    for col_name, col_type in columns:
        # Vérifier si le nom contient des caractères non-ASCII
        if any(ord(c) > 127 for c in col_name):
            print(f"    ⚠ COLONNE AVEC ACCENT: {col_name} ({col_type})")

conn.close()
print("\n✓ Vérification terminée")
