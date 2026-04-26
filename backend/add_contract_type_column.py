"""
Add contract_type column to employees table
"""
from sqlalchemy import create_engine, text
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)

with engine.connect() as conn:
    try:
        # Check if column already exists
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='employees' 
            AND column_name='contract_type'
        """))
        
        if result.fetchone():
            print("✓ Column contract_type already exists")
        else:
            # Add the column
            conn.execute(text("""
                ALTER TABLE employees 
                ADD COLUMN contract_type VARCHAR
            """))
            conn.commit()
            print("✓ Added contract_type column to employees table")
            
    except Exception as e:
        print(f"❌ Error: {e}")
