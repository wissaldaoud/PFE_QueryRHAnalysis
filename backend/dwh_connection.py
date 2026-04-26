"""
DWH Database Connection - Connexion à la base de données datawarehouse (Qlik)
Utilise SQLAlchemy pour se connecter à hr_datawarehouse (séparé de APP_DB)
"""
import os
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from typing import Optional


# Global engine instance (singleton pattern)
_dwh_engine: Optional[Engine] = None


def get_dwh_engine() -> Engine:
    """
    Récupérer ou créer l'engine SQLAlchemy pour la base DWH
    
    Variables d'environnement requises:
    - DWH_HOST: Hôte PostgreSQL (default: localhost)
    - DWH_PORT: Port PostgreSQL (default: 5432)
    - DWH_DB: Nom de la base de données (default: hr_datawarehouse)
    - DWH_USER: Utilisateur PostgreSQL (default: hr_user)
    - DWH_PASSWORD: Mot de passe PostgreSQL (default: hr_password123)
    
    Returns:
        Engine: SQLAlchemy engine pour DWH_DB
    
    Raises:
        Exception: Si les credentials sont invalides ou la connexion échoue
    
    Example:
        >>> engine = get_dwh_engine()
        >>> with engine.connect() as conn:
        >>>     result = conn.execute("SELECT COUNT(*) FROM fact_employes")
        >>>     count = result.fetchone()[0]
    """
    global _dwh_engine
    
    # Retourner l'engine existant si déjà créé (singleton)
    if _dwh_engine is not None:
        return _dwh_engine
    
    # Récupérer les variables d'environnement
    dwh_host = os.getenv('DWH_HOST', 'localhost')
    dwh_port = os.getenv('DWH_PORT', '5432')
    dwh_db = os.getenv('DWH_DB', 'hr_datawarehouse')
    dwh_user = os.getenv('DWH_USER', 'hr_user')
    dwh_password = os.getenv('DWH_PASSWORD', 'hr_password123')
    
    # Construire l'URL de connexion PostgreSQL
    # Format: postgresql://user:password@host:port/database
    database_url = f"postgresql://{dwh_user}:{dwh_password}@{dwh_host}:{dwh_port}/{dwh_db}"
    
    # Créer l'engine avec configuration appropriée
    _dwh_engine = create_engine(
        database_url,
        pool_size=5,              # Nombre de connexions dans le pool
        max_overflow=10,          # Connexions supplémentaires autorisées
        pool_pre_ping=True,       # Vérifier la connexion avant utilisation
        pool_recycle=3600,        # Recycler les connexions après 1h
        echo=False                # Debug SQL (mettre True pour voir les requêtes)
    )
    
    return _dwh_engine


def test_dwh_connection() -> bool:
    """
    Tester la connexion à la base DWH
    
    Returns:
        bool: True si la connexion réussit, False sinon
    """
    try:
        engine = get_dwh_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT current_database(), version()"))
            row = result.fetchone()
            db_name = row[0]
            db_version = row[1].split(',')[0]  # Première partie de la version
            
            print(f"✅ Connexion DWH réussie!")
            print(f"   Base de données: {db_name}")
            print(f"   Version: {db_version}")
            return True
            
    except Exception as e:
        print(f"❌ Erreur de connexion DWH: {e}")
        return False


def get_dwh_tables() -> list:
    """
    Lister toutes les tables dans la base DWH
    
    Returns:
        list: Liste des noms de tables
    """
    try:
        engine = get_dwh_engine()
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """))
            tables = [row[0] for row in result]
            return tables
            
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des tables: {e}")
        return []


# Pour tester le module directement
if __name__ == "__main__":
    print("🔌 Test de connexion à DWH_DB...")
    print("=" * 50)
    
    # Charger .env si disponible
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Variables .env chargées")
    except ImportError:
        print("⚠️  python-dotenv non installé, utilisation des variables système")
    
    print("")
    
    # Test connexion
    if test_dwh_connection():
        print("")
        print("📊 Tables disponibles dans DWH:")
        print("-" * 50)
        tables = get_dwh_tables()
        if tables:
            for table in tables:
                print(f"  - {table}")
        else:
            print("  Aucune table trouvée")
    
    print("")
    print("=" * 50)
