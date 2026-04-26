"""Vérification directe des données CDD dans la base"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# Connexion DWH
conn = psycopg2.connect(
    host=os.getenv("DWH_DB_HOST"),
    port=os.getenv("DWH_DB_PORT"),
    database=os.getenv("DWH_DB_NAME"),
    user=os.getenv("DWH_DB_USER"),
    password=os.getenv("DWH_DB_PASSWORD")
)

cursor = conn.cursor()

print("="*80)
print("📊 Vérification des données CDD")
print("="*80)

# Test 1: Total employés
cursor.execute("SELECT COUNT(*) FROM dim.dim_employe;")
total = cursor.fetchone()[0]
print(f"\n1️⃣ Total employés: {total}")

# Test 2: Total hommes
cursor.execute("SELECT COUNT(*) FROM dim.dim_employe WHERE code_sexe = 'M';")
total_hommes = cursor.fetchone()[0]
print(f"2️⃣ Total hommes (code_sexe='M'): {total_hommes}")

# Test 3: Total contrats actifs
cursor.execute("SELECT COUNT(*) FROM fait.fait_contrat WHERE flag_contrat_actif = 1;")
total_contrats_actifs = cursor.fetchone()[0]
print(f"3️⃣ Total contrats actifs: {total_contrats_actifs}")

# Test 4: Types de contrats disponibles
cursor.execute("SELECT DISTINCT libelle_type_contrat FROM fait.fait_contrat WHERE libelle_type_contrat IS NOT NULL ORDER BY libelle_type_contrat;")
types = cursor.fetchall()
print(f"\n4️⃣ Types de contrats dans la base ({len(types)}):")
for t in types:
    print(f"   - {t[0]}")

# Test 5: Contrats CDD (tous)
cursor.execute("SELECT COUNT(*) FROM fait.fait_contrat WHERE UPPER(libelle_type_contrat) LIKE '%CDD%';")
total_cdd = cursor.fetchone()[0]
print(f"\n5️⃣ Total contrats CDD (tous): {total_cdd}")

# Test 6: Contrats CDD actifs
cursor.execute("SELECT COUNT(*) FROM fait.fait_contrat WHERE UPPER(libelle_type_contrat) LIKE '%CDD%' AND flag_contrat_actif = 1;")
total_cdd_actifs = cursor.fetchone()[0]
print(f"6️⃣ Total contrats CDD actifs: {total_cdd_actifs}")

# Test 7: La requête exacte qui pose problème avec LEFT JOIN
query_left = """
SELECT COUNT(*) as total
FROM dim.dim_employe e
LEFT JOIN fait.fait_contrat c ON e.nudoss = c.nudoss
WHERE c.flag_contrat_actif = 1 AND e.code_sexe = 'M' AND UPPER(c.libelle_type_contrat) LIKE UPPER('%CDD%');
"""
cursor.execute(query_left)
result_left = cursor.fetchone()[0]
print(f"\n7️⃣ Requête avec LEFT JOIN: {result_left}")

# Test 8: Même requête avec INNER JOIN
query_inner = """
SELECT COUNT(*) as total
FROM dim.dim_employe e
INNER JOIN fait.fait_contrat c ON e.nudoss = c.nudoss
WHERE c.flag_contrat_actif = 1 AND e.code_sexe = 'M' AND UPPER(c.libelle_type_contrat) LIKE UPPER('%CDD%');
"""
cursor.execute(query_inner)
result_inner = cursor.fetchone()[0]
print(f"8️⃣ Requête avec INNER JOIN: {result_inner}")

# Test 9: Hommes sans condition sur contrat actif
query_hommes = """
SELECT COUNT(*) as total
FROM dim.dim_employe e
INNER JOIN fait.fait_contrat c ON e.nudoss = c.nudoss
WHERE e.code_sexe = 'M' AND UPPER(c.libelle_type_contrat) LIKE UPPER('%CDD%');
"""
cursor.execute(query_hommes)
result_hommes = cursor.fetchone()[0]
print(f"9️⃣ Hommes CDD (sans flag_contrat_actif): {result_hommes}")

# Test 10: Échantillon de contrats CDD
cursor.execute("""
SELECT e.nudoss, e.nom, e.prenom, e.code_sexe, c.libelle_type_contrat, c.flag_contrat_actif
FROM dim.dim_employe e
INNER JOIN fait.fait_contrat c ON e.nudoss = c.nudoss
WHERE UPPER(c.libelle_type_contrat) LIKE '%CDD%'
LIMIT 5;
""")
sample = cursor.fetchall()
print(f"\n🔍 Échantillon de contrats CDD:")
for row in sample:
    print(f"   {row[1]} {row[2]} ({row[3]}) - {row[4]} - Actif: {row[5]}")

print("\n" + "="*80)

cursor.close()
conn.close()
