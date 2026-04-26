"""
Modèle SQLAlchemy pour les offres d'emploi
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON, Boolean
from sqlalchemy.sql import func
from app.db.base import Base


class JobOffer(Base):
    """Table des offres d'emploi"""
    __tablename__ = "job_offers"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    category = Column(String(100), index=True, comment="Catégorie professionnelle (Data Science, Python Developer, etc.)")
    
    # Compétences en JSON
    required_skills = Column(JSON, default=list, comment="Liste des compétences requises")
    preferred_skills = Column(JSON, default=list, comment="Liste des compétences préférées")
    
    # Éducation
    required_education = Column(JSON, default=list, comment="Liste des diplômes/formations requis")
    
    # Expérience
    required_experience_years = Column(Float, nullable=True, comment="Années d'expérience requises")
    
    # Informations additionnelles
    location = Column(String(255), nullable=True)
    salary_range = Column(String(100), nullable=True, comment="Ex: 40000-60000 EUR")
    contract_type = Column(String(50), nullable=True, comment="CDI, CDD, Stage, etc.")
    department = Column(String(100), nullable=True)
    
    # Statut
    is_active = Column(Boolean, default=True, index=True)
    
    # Métadonnées
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, nullable=True, comment="ID de l'utilisateur créateur")
    
    def __repr__(self):
        return f"<JobOffer(id={self.id}, title='{self.title}', category='{self.category}')>"
    
    def to_dict(self):
        """Convertir en dictionnaire"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "required_skills": self.required_skills or [],
            "preferred_skills": self.preferred_skills or [],
            "required_education": self.required_education or [],
            "required_experience_years": self.required_experience_years,
            "location": self.location,
            "salary_range": self.salary_range,
            "contract_type": self.contract_type,
            "department": self.department,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
