"""
User model for authentication and RBAC
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db.base import Base


class UserRole(str, enum.Enum):
    admin = "admin"
    hr_manager = "hr_manager"
    manager = "manager"  # Chef d'équipe - gère son équipe
    analyst = "analyst"
    employee = "employee"


class AccountStatus(str, enum.Enum):
    pending = "pending"      # En attente de validation admin
    approved = "approved"    # Approuvé - peut se connecter
    rejected = "rejected"    # Rejeté - ne peut pas se connecter


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    role = Column(Enum(UserRole), default=UserRole.employee)
    is_active = Column(Boolean, default=True)
    sso_provider = Column(String, nullable=True)  # microsoft, google, saml, or null for local
    profile_picture = Column(String, nullable=True)  # URL de la photo de profil
    
    # Nouveau: Statut du compte (validation admin)
    account_status = Column(Enum(AccountStatus), default=AccountStatus.pending)
    verified_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Lien vers l'employé (pour les utilisateurs de type employee)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    employee = relationship("Employee", backref="user_account")
    
    # Notifications
    notifications = relationship("Notification", back_populates="user")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
