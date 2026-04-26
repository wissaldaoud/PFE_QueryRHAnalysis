#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Grant database permissions for query engine"""
from sqlalchemy import create_engine, text
import os

# Connect as postgres superuser using SQLAlchemy (avoids encoding issues)
try:
    # Build connection URL for postgres user
    db_url = f"postgresql://postgres:postgres@localhost:5432/hr_datawarehouse"
    engine = create_engine(db_url, isolation_level="AUTOCOMMIT")
    
    print("Connection to database established...")
    
    with engine.connect() as conn:
        print("\nGranting permissions to hr_user...")
        
        # Grant schema usage
        conn.execute(text("GRANT USAGE ON SCHEMA dim TO hr_user;"))
        print("✓ Granted USAGE on schema dim")
        
        conn.execute(text("GRANT SELECT ON ALL TABLES IN SCHEMA dim TO hr_user;"))
        print("✓ Granted SELECT on all tables in schema dim")
        
        conn.execute(text("GRANT USAGE ON SCHEMA fait TO hr_user;"))
        print("✓ Granted USAGE on schema fait")
        
        conn.execute(text("GRANT SELECT ON ALL TABLES IN SCHEMA fait TO hr_user;"))
        print("✓ Granted SELECT on all tables in schema fait")
        
        # Grant default privileges
        conn.execute(text("ALTER DEFAULT PRIVILEGES IN SCHEMA dim GRANT SELECT ON TABLES TO hr_user;"))
        print("✓ Set default privileges for dim schema")
        
        conn.execute(text("ALTER DEFAULT PRIVILEGES IN SCHEMA fait GRANT SELECT ON TABLES TO hr_user;"))
        print("✓ Set default privileges for fait schema")
        
        print("\n✅ All permissions granted successfully!")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import sys
    sys.exit(1)

cursor.close()
conn.close()
