"""
Leave Request model for managing employee leave/time-off requests
"""
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db.base import Base


class LeaveType(str, enum.Enum):
    """Types de congés simplifiés"""
    annual = "annual"        # Congé annuel payé
    sick = "sick"            # Congé maladie
    unpaid = "unpaid"        # Congé sans solde


class LeaveStatus(str, enum.Enum):
    """Statut de la demande de congé avec workflow hiérarchique"""
    pending = "pending"              # En attente d'approbation manager
    manager_approved = "manager_approved"  # Approuvé par le manager, en attente RH
    hr_approved = "hr_approved"      # Approuvé par RH (final)
    rejected = "rejected"            # Refusé (par manager ou RH)
    cancelled = "cancelled"          # Annulé par l'employé


class LeaveRequest(Base):
    """Modèle pour les demandes de congés"""
    __tablename__ = "leave_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Employé demandeur
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    
    # Type et période
    leave_type = Column(Enum(LeaveType), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    
    # Nombre de jours (calculé automatiquement)
    days_requested = Column(Integer, nullable=False)
    
    # Motif de la demande
    reason = Column(Text)
    
    # Statut et workflow
    status = Column(Enum(LeaveStatus), default=LeaveStatus.pending)
    
    # Approbation Manager
    manager_approved_by = Column(Integer, ForeignKey("users.id"))
    manager_approval_date = Column(DateTime)
    
    # Approbation RH (finale)
    hr_approved_by = Column(Integer, ForeignKey("users.id"))
    hr_approval_date = Column(DateTime)
    
    # Rejet
    rejected_by = Column(Integer, ForeignKey("users.id"))
    rejection_date = Column(DateTime)
    rejection_reason = Column(Text)
    
    # Compatibilité avec ancien système (deprecated)
    approved_by = Column(Integer, ForeignKey("users.id"))
    approval_date = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    employee = relationship("Employee", backref="leave_requests")
    approver = relationship("User", foreign_keys=[approved_by])
    manager_approver = relationship("User", foreign_keys=[manager_approved_by])
    hr_approver = relationship("User", foreign_keys=[hr_approved_by])
    rejector = relationship("User", foreign_keys=[rejected_by])
    
    def __repr__(self):
        return f"<LeaveRequest {self.id}: {self.employee_id} - {self.leave_type.value} ({self.status.value})>"
