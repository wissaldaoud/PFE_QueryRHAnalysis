"""
Notification model for admin alerts
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.db.base import Base


class NotificationType(str, enum.Enum):
    new_account = "new_account"
    account_approved = "account_approved"
    account_rejected = "account_rejected"
    leave_request = "leave_request"
    leave_manager_approved = "leave_manager_approved"
    leave_hr_approved = "leave_hr_approved"
    leave_rejected = "leave_rejected"
    system = "system"


class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Destinataire
    type = Column(Enum(NotificationType), default=NotificationType.system)
    title = Column(String(255), nullable=False)
    message = Column(String(500), nullable=False)
    is_read = Column(Boolean, default=False)
    link = Column(String(255), nullable=True)  # Lien vers la page concernée
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    user = relationship("User", back_populates="notifications")
