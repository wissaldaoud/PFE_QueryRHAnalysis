"""
Pydantic schemas for Department
"""
from pydantic import BaseModel, Field, computed_field
from typing import Optional


class DepartmentBase(BaseModel):
    name: str
    code: str
    description: Optional[str] = None


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None


class DepartmentResponse(DepartmentBase):
    id: int
    employee_count: int = Field(default=0, description="Number of employees in department")
    
    class Config:
        from_attributes = True
