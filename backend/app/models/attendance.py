"""
Attendance model for tracking employee presence
"""
from sqlalchemy import Column, Integer, Date, Time, ForeignKey, Enum, String
from sqlalchemy.orm import relationship
import enum
from app.db.base import Base


class AttendanceType(str, enum.Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    HALF_DAY = "half_day"
    WORK_FROM_HOME = "work_from_home"


class Attendance(Base):
    __tablename__ = "attendance"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    date = Column(Date, nullable=False, index=True)
    check_in_time = Column(Time)
    check_out_time = Column(Time)
    attendance_type = Column(Enum(AttendanceType), default=AttendanceType.PRESENT)
    notes = Column(String)
    
    # Relationships
    employee = relationship("Employee")
