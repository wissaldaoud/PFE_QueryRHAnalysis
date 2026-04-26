"""
Database session management
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import os

# Force UTF-8 au niveau système AVANT toute connexion
os.environ.setdefault('PGCLIENTENCODING', 'UTF8')
os.environ.setdefault('PYTHONUTF8', '1')

# CRITICAL: Ne PAS utiliser settings.DATABASE_URL qui est construit par un validator
# Construire l'URL directement pour éviter les problèmes d'encodage du validator
db_url = (
    f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
    f"@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
)

# Force UTF-8 encoding avec connect_args explicites
engine = create_engine(
    db_url,
    pool_pre_ping=True,
    connect_args={
        "client_encoding": "utf8",
        "application_name": "hr_analytics",
        "connect_timeout": 10
    },
    echo=False  # Ne pas logger les requêtes SQL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
