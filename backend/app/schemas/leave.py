"""
Pydantic schemas for Leave Request validation
"""
from pydantic import BaseModel, Field, field_validator
from datetime import date, datetime
from typing import Optional
from enum import Enum


class LeaveType(str, Enum):
    annual = "annual"
    sick = "sick"
    unpaid = "unpaid"


class LeaveStatus(str, Enum):
    pending = "pending"
    manager_approved = "manager_approved"
    hr_approved = "hr_approved"
    rejected = "rejected"
    cancelled = "cancelled"


# ============ CREATE ============
class LeaveRequestCreate(BaseModel):
    """Schéma pour créer une demande de congé"""
    leave_type: LeaveType
    start_date: date
    end_date: date
    reason: Optional[str] = None
    
    @field_validator('end_date')
    @classmethod
    def end_date_must_be_after_start(cls, v, info):
        if 'start_date' in info.data and v < info.data['start_date']:
            raise ValueError('La date de fin doit être après la date de début')
        return v


# ============ UPDATE ============
class LeaveRequestUpdate(BaseModel):
    """Schéma pour mettre à jour une demande (avant approbation)"""
    leave_type: Optional[LeaveType] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    reason: Optional[str] = None


# ============ APPROVE/REJECT ============
class LeaveApproval(BaseModel):
    """Schéma pour approuver une demande"""
    pass  # Aucun champ requis


class LeaveRejection(BaseModel):
    """Schéma pour rejeter une demande"""
    rejection_reason: str = Field(..., min_length=5, description="Motif du refus")


# ============ RESPONSE ============
class LeaveRequestResponse(BaseModel):
    """Schéma de réponse pour une demande de congé"""
    id: int
    employee_id: int
    employee_name: Optional[str] = None
    leave_type: LeaveType
    start_date: date
    end_date: date
    days_requested: int
    reason: Optional[str] = None
    status: LeaveStatus
    approved_by: Optional[int] = None
    approver_name: Optional[str] = None
    approval_date: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class LeaveRequestList(BaseModel):
    """Schéma pour la liste paginée des demandes"""
    items: list[LeaveRequestResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ============ STATISTICS ============
class LeaveBalance(BaseModel):
    """Solde de congés d'un employé"""
    employee_id: int
    employee_name: str
    annual_total: int = 25  # Jours annuels par défaut
    annual_used: int = 0
    annual_remaining: int = 25
    sick_used: int = 0
    unpaid_used: int = 0


class LeaveStatistics(BaseModel):
    """Statistiques globales des congés"""
    total_requests: int
    pending_count: int
    approved_count: int
    rejected_count: int
    by_type: dict[str, int]
