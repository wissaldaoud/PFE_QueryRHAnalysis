"""
HR Analytics and prediction endpoints
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any
from app.db.base import get_db
from app.models.employee import Employee, EmploymentStatus
from app.models.department import Department
from app.models.user import User, UserRole
from app.models.leave import LeaveRequest, LeaveStatus
from app.api.deps import get_current_user, require_analyst

router = APIRouter()


@router.get("/dashboard-stats")
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # Tous les utilisateurs
) -> Dict[str, Any]:
    """
    Statistiques du dashboard adaptées au rôle de l'utilisateur.
    
    - Employee: Stats personnelles
    - Manager: Stats de son équipe
    - HR/Admin/Analyst: Stats globales
    """
    
    # ROLE EMPLOYEE - Stats personnelles uniquement
    if current_user.role == UserRole.employee:
        if not current_user.employee_id:
            return {
                "role": "employee",
                "total_employees": 0,
                "active_employees": 0,
                "pending_leaves": 0,
                "departments_count": 0,
                "message": "Compte non lié à un employé"
            }
        
        # Compter les congés de l'employé
        my_leaves = db.query(LeaveRequest).filter(
            LeaveRequest.employee_id == current_user.employee_id
        ).count()
        
        my_pending = db.query(LeaveRequest).filter(
            LeaveRequest.employee_id == current_user.employee_id,
            LeaveRequest.status == LeaveStatus.pending
        ).count()
        
        return {
            "role": "employee",
            "total_employees": 1,
            "active_employees": 1,
            "my_leaves_count": my_leaves,
            "my_pending_leaves": my_pending,
            "departments_count": 1
        }
    
    # ROLE MANAGER - Stats de son équipe
    elif current_user.role == UserRole.manager:
        if not current_user.employee_id:
            return {
                "role": "manager",
                "total_employees": 0,
                "active_employees": 0,
                "pending_leaves": 0,
                "departments_count": 0
            }
        
        # Trouver tous les employés qui reportent à ce manager
        team_employees = db.query(Employee).filter(
            Employee.manager_id == current_user.employee_id
        ).all()
        
        team_ids = [emp.id for emp in team_employees]
        team_count = len(team_employees)
        active_count = sum(1 for emp in team_employees if emp.employment_status == EmploymentStatus.active)
        
        # Compter les départements uniques dans l'équipe
        departments = set(emp.department_id for emp in team_employees if emp.department_id)
        
        # Congés en attente de l'équipe (pour validation manager)
        pending_leaves = db.query(LeaveRequest).filter(
            LeaveRequest.employee_id.in_(team_ids) if team_ids else False,
            LeaveRequest.status == LeaveStatus.pending
        ).count()
        
        return {
            "role": "manager",
            "total_employees": team_count,
            "active_employees": active_count,
            "pending_leaves": pending_leaves,
            "departments_count": len(departments),
            "team_employee_ids": team_ids
        }
    
    # ROLE HR/ADMIN/ANALYST - Stats globales
    else:
        total_employees = db.query(Employee).count()
        active_employees = db.query(Employee).filter(
            Employee.employment_status == EmploymentStatus.active
        ).count()
        terminated = db.query(Employee).filter(
            Employee.employment_status == EmploymentStatus.terminated
        ).count()
        departments_count = db.query(Department).count()
        
        # Congés en attente (tous)
        pending_leaves = db.query(LeaveRequest).filter(
            LeaveRequest.status == LeaveStatus.pending
        ).count()
        
        # Congés en attente validation RH
        hr_pending = db.query(LeaveRequest).filter(
            LeaveRequest.status == LeaveStatus.manager_approved
        ).count()
        
        return {
            "role": current_user.role.value,
            "total_employees": total_employees,
            "active_employees": active_employees,
            "terminated_employees": terminated,
            "pending_leaves": pending_leaves,
            "hr_pending_leaves": hr_pending,
            "departments_count": departments_count
        }


@router.get("/dashboard")
async def get_dashboard_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst)  # Analyst, HR or Admin
) -> Dict[str, Any]:
    """
    Get key HR metrics for dashboard (Analyst, HR Manager or Admin)
    """
    # Real data from database
    total_employees = db.query(Employee).count()
    active_employees = db.query(Employee).filter(
        Employee.employment_status == EmploymentStatus.active
    ).count()
    terminated = db.query(Employee).filter(
        Employee.employment_status == EmploymentStatus.terminated
    ).count()
    departments_count = db.query(Department).count()
    
    # Calculate turnover rate
    turnover_rate = (terminated / total_employees * 100) if total_employees > 0 else 0
    
    # Average salary
    avg_salary = db.query(func.avg(Employee.salary)).scalar() or 0
    
    return {
        "total_employees": total_employees,
        "active_employees": active_employees,
        "terminated_employees": terminated,
        "turnover_rate": round(turnover_rate, 2),
        "average_salary": round(float(avg_salary), 2),
        "departments_count": departments_count
    }


@router.get("/departments/stats")
async def get_departments_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst)
) -> Dict[str, Any]:
    """
    Get employee count and average salary per department
    """
    stats = db.query(
        Department.name,
        func.count(Employee.id).label('employee_count'),
        func.avg(Employee.salary).label('avg_salary')
    ).outerjoin(Employee).group_by(Department.id, Department.name).all()
    
    return {
        "departments": [
            {
                "name": stat[0],
                "employee_count": stat[1],
                "average_salary": round(float(stat[2] or 0), 2)
            }
            for stat in stats
        ]
    }


@router.get("/turnover/prediction")
async def predict_turnover(
    employee_id: int = Query(..., description="Employee ID for prediction"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst)
) -> Dict[str, Any]:
    """
    Predict employee turnover probability (Analyst, HR Manager or Admin)
    """
    # Verify employee exists
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        return {"error": "Employee not found"}
    
    # TODO: Implement ML prediction - placeholder for now
    return {
        "employee_id": employee_id,
        "employee_name": f"{employee.first_name} {employee.last_name}",
        "turnover_probability": 0.15,
        "risk_level": "low",
        "factors": ["tenure", "salary_satisfaction"],
        "note": "ML model integration pending"
    }


@router.get("/absenteeism/trends")
async def get_absenteeism_trends(
    start_date: str = Query(...),
    end_date: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst)
) -> Dict[str, Any]:
    """
    Get absenteeism trends for a period (Analyst, HR Manager or Admin)
    """
    # TODO: Implement with attendance data
    return {
        "period": {"start": start_date, "end": end_date},
        "total_absences": 0,
        "average_rate": 0.0,
        "trends": [],
        "note": "Attendance data integration pending"
    }


@router.get("/departments/comparison")
async def compare_departments(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst)
) -> Dict[str, Any]:
    """
    Compare metrics across departments (Analyst, HR Manager or Admin)
    """
    departments = db.query(Department).all()
    comparison = []
    
    for dept in departments:
        employees = db.query(Employee).filter(Employee.department_id == dept.id).all()
        emp_count = len(employees)
        avg_sal = sum(e.salary or 0 for e in employees) / emp_count if emp_count > 0 else 0
        
        comparison.append({
            "department_id": dept.id,
            "department_name": dept.name,
            "employee_count": emp_count,
            "average_salary": round(avg_sal, 2)
        })
    
    return {"departments": comparison}
