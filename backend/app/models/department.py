"""
Department model
"""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.base import Base


class Department(Base):
    __tablename__ = "departments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    code = Column(String, unique=True, nullable=False)
    description = Column(String)
    
    # Relationships
    employees = relationship("Employee", back_populates="department")
