"""
Employee model for HR data
"""
from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum
from app.db.base import Base


class EmploymentStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    on_leave = "on_leave"
    terminated = "terminated"


class Employee(Base):
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_code = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    date_of_birth = Column(Date)
    hire_date = Column(Date, nullable=False)
    termination_date = Column(Date)
    job_title = Column(String)
    contract_type = Column(String)  # Type de contrat: CDI, CDD, Stage, etc.
    department_id = Column(Integer, ForeignKey("departments.id"))
    manager_id = Column(Integer, ForeignKey("employees.id"))
    salary = Column(Float)
    employment_status = Column(Enum(EmploymentStatus), default=EmploymentStatus.active)
    
    # Relationships
    department = relationship("Department", back_populates="employees")
    manager = relationship("Employee", remote_side=[id])
    
    @property
    def full_name(self) -> str:
        """Retourne le nom complet de l'employé"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def department_name(self) -> str:
        """Retourne le nom du département"""
        return self.department.name if self.department else None
