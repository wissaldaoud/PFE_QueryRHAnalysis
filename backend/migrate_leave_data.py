"""
Script pour migrer les anciennes demandes de congés vers le nouveau workflow
Convertit les demandes 'approved' en 'hr_approved'
"""
from sqlalchemy import create_engine, text
from app.core.config import settings

def migrate_leave_data():
    """Migrer les données de congés existantes"""
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        # Migrer approved → hr_approved
        result = conn.execute(text("""
            UPDATE leave_requests 
            SET status = 'hr_approved', 
                hr_approved_by = approved_by,
                hr_approval_date = approval_date
            WHERE status = 'approved'
        """))
        
        conn.commit()
        print(f"✅ Migration terminée: {result.rowcount} demandes migrées vers hr_approved")
        
        # Afficher un résumé
        counts = conn.execute(text("""
            SELECT status, COUNT(*) as count
            FROM leave_requests
            GROUP BY status
            ORDER BY count DESC
        """))
        
        print("\n📊 Résumé des statuts:")
        for row in counts:
            print(f"  - {row[0]}: {row[1]}")

if __name__ == "__main__":
    print("🔄 Migration des données de congés...")
    migrate_leave_data()
    print("\n✅ Migration complétée!")
