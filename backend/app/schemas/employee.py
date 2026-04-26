"""
Pydantic schemas for Employee
"""
from pydantic import BaseModel, field_validator, model_serializer
from typing import Optional, Any
from datetime import date
from app.models.employee import EmploymentStatus


class EmployeeBase(BaseModel):
    employee_code: str
    first_name: str
    last_name: str
    email: Optional[str] = None  # Changed from EmailStr to str to handle invalid emails in DB
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    hire_date: date
    job_title: Optional[str] = None
    department_id: Optional[int] = None
    manager_id: Optional[int] = None
    salary: Optional[float] = None
    employment_status: EmploymentStatus = EmploymentStatus.active
    
    @field_validator('email')
    @classmethod
    def clean_email(cls, v: Optional[str]) -> Optional[str]:
        """Nettoyer les emails en supprimant les espaces"""
        if v:
            return v.strip().replace(' ', '')
        return v


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None  # Changed from EmailStr to str
    phone: Optional[str] = None
    job_title: Optional[str] = None
    department_id: Optional[int] = None
    manager_id: Optional[int] = None
    salary: Optional[float] = None
    employment_status: Optional[EmploymentStatus] = None
    termination_date: Optional[date] = None
    
    @field_validator('email')
    @classmethod
    def clean_email(cls, v: Optional[str]) -> Optional[str]:
        """Nettoyer les emails en supprimant les espaces"""
        if v:
            return v.strip().replace(' ', '')
        return v


class EmployeeResponse(EmployeeBase):
    id: int
    termination_date: Optional[date] = None
    full_name: Optional[str] = None
    department_name: Optional[str] = None
    
    @model_serializer(mode='wrap', when_used='always')
    def serialize_model(self, serializer, info):
        """Ajoute full_name et department_name calculés"""
        data = serializer(self)
        # Calculer full_name depuis first_name et last_name
        if 'first_name' in data and 'last_name' in data:
            data['full_name'] = f"{data['first_name']} {data['last_name']}"
        return data
    
    class Config:
        from_attributes = True
