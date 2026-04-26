import psycopg2

conn = psycopg2.connect(
    host='localhost', 
    port=5432, 
    database='hr_analytics_db', 
    user='hr_user', 
    password='hr_password123', 
    client_encoding='utf8'
)
cur = conn.cursor()
cur.execute('SELECT id, username, email, is_active, role FROM users ORDER BY id')
rows = cur.fetchall()
print('Utilisateurs dans hr_analytics_db:')
for row in rows:
    print(f'  ID={row[0]}, Username={row[1]}, Email={row[2]}, Active={row[3]}, Role={row[4]}')
cur.close()
conn.close()
