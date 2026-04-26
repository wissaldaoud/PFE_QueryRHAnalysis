"""
Department management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.db.base import get_db
from app.schemas.department import DepartmentCreate, DepartmentUpdate, DepartmentResponse
from app.models.department import Department
from app.models.user import User
from app.api.deps import get_current_user, require_admin

router = APIRouter()


@router.get("/", response_model=List[DepartmentResponse])
async def list_departments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # Requires authentication
):
    """
    Retrieve list of all departments (Authenticated users)
    """
    departments = db.query(Department).offset(skip).limit(limit).all()
    
    # Add employee_count to each department
    result = []
    for dept in departments:
        dept_dict = {
            "id": dept.id,
            "name": dept.name,
            "code": dept.code,
            "description": dept.description,
            "employee_count": len(dept.employees) if dept.employees else 0
        }
        result.append(dept_dict)
    
    return result


@router.post("/", response_model=DepartmentResponse, status_code=201)
async def create_department(
    department: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)  # Only Admin can create
):
    """
    Create a new department (Admin only)
    """
    # Check if name already exists
    existing = db.query(Department).filter(Department.name == department.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Department name already exists")
    
    # Check if code already exists
    existing_code = db.query(Department).filter(Department.code == department.code).first()
    if existing_code:
        raise HTTPException(status_code=400, detail="Department code already exists")
    
    db_department = Department(**department.model_dump())
    db.add(db_department)
    db.commit()
    db.refresh(db_department)
    
    return {
        "id": db_department.id,
        "name": db_department.name,
        "code": db_department.code,
        "description": db_department.description,
        "employee_count": 0
    }


@router.get("/{department_id}", response_model=DepartmentResponse)
async def get_department(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get department by ID (Authenticated users)
    """
    department = db.query(Department).filter(Department.id == department_id).first()
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    
    return {
        "id": department.id,
        "name": department.name,
        "code": department.code,
        "description": department.description,
        "employee_count": len(department.employees) if department.employees else 0
    }


@router.put("/{department_id}", response_model=DepartmentResponse)
async def update_department(
    department_id: int,
    department: DepartmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)  # Only Admin
):
    """
    Update department information (Admin only)
    """
    db_department = db.query(Department).filter(Department.id == department_id).first()
    if not db_department:
        raise HTTPException(status_code=404, detail="Department not found")
    
    update_data = department.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_department, field, value)
    
    db.commit()
    db.refresh(db_department)
    
    return {
        "id": db_department.id,
        "name": db_department.name,
        "code": db_department.code,
        "description": db_department.description,
        "employee_count": len(db_department.employees) if db_department.employees else 0
    }


@router.delete("/{department_id}")
async def delete_department(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)  # Only Admin
):
    """
    Delete a department (Admin only)
    """
    db_department = db.query(Department).filter(Department.id == department_id).first()
    if not db_department:
        raise HTTPException(status_code=404, detail="Department not found")
    
    # Check if department has employees
    if db_department.employees:
        raise HTTPException(
            status_code=400, 
            detail="Cannot delete department with employees. Reassign employees first."
        )
    
    db.delete(db_department)
    db.commit()
    return {"message": "Department deleted successfully"}
