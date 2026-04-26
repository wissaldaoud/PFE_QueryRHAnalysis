"""Vérifier les commentaires et métadonnées PostgreSQL"""
import psycopg2
import os

os.environ['PGCLIENTENCODING'] = 'UTF8'

try:
    conn = psycopg2.connect(
        host='localhost',
        port='5432',
        database='hr_analytics_db',
        user='hr_user',
        password='hr_password123',
        client_encoding='utf8'
    )
    
    cur = conn.cursor()
    
    # Vérifier les commentaires sur les tables
    print("=" * 60)
    print("COMMENTAIRES SUR LES TABLES:")
    print("=" * 60)
    cur.execute("""
        SELECT 
            c.table_name,
            pg_catalog.obj_description(pgc.oid, 'pg_class') as comment
        FROM information_schema.tables c
        JOIN pg_catalog.pg_class pgc ON c.table_name = pgc.relname
        WHERE c.table_schema = 'public' 
        AND pg_catalog.obj_description(pgc.oid, 'pg_class') IS NOT NULL;
    """)
    
    results = cur.fetchall()
    if results:
        for table, comment in results:
            print(f"  {table}: {comment}")
            # Vérifier accents
            if any(ord(c) > 127 for c in str(comment)):
                print(f"    ⚠ ACCENT DETECTE")
    else:
        print("  Aucun commentaire")
    
    # Vérifier les commentaires sur les colonnes
    print("\n" + "=" * 60)
    print("COMMENTAIRES SUR LES COLONNES:")
    print("=" * 60)
    cur.execute("""
        SELECT 
            c.table_name,
            c.column_name,
            pg_catalog.col_description(pgc.oid, c.ordinal_position::int) as comment
        FROM information_schema.columns c
        JOIN pg_catalog.pg_class pgc ON c.table_name = pgc.relname
        WHERE c.table_schema = 'public'
        AND pg_catalog.col_description(pgc.oid, c.ordinal_position::int) IS NOT NULL
        LIMIT 20;
    """)
    
    results = cur.fetchall()
    if results:
        for table, column, comment in results:
            print(f"  {table}.{column}: {comment}")
            if any(ord(c) > 127 for c in str(comment)):
                print(f"    ⚠ ACCENT DETECTE")
    else:
        print("  Aucun commentaire")
    
    # Vérifier l'encodage de la base
    print("\n" + "=" * 60)
    print("ENCODAGE DE LA BASE:")
    print("=" * 60)
    cur.execute("SHOW server_encoding;")
    print(f"  Server encoding: {cur.fetchone()[0]}")
    
    cur.execute("SHOW client_encoding;")
    print(f"  Client encoding: {cur.fetchone()[0]}")
    
    conn.close()
    print("\n✓ Vérification terminée")
    
except Exception as e:
    print(f"\n✗ Erreur: {e}")
    import traceback
    traceback.print_exc()
