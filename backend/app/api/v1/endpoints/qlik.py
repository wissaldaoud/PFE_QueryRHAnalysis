"""
Qlik Sense Integration - Backend Endpoints
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any
from datetime import datetime, date
from app.db.base import get_db

router = APIRouter()


@router.get("/employees-export")
async def export_employees_for_qlik(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """
    Export formatted employee data for Qlik Sense
    Returns all employee information with calculated fields
    """
    query = text("""
        SELECT 
            e.id,
            e.employee_code,
            e.first_name,
            e.last_name,
            e.first_name || ' ' || e.last_name as full_name,
            e.email,
            e.phone,
            e.date_of_birth,
            EXTRACT(YEAR FROM AGE(CURRENT_DATE, e.date_of_birth)) as age,
            e.hire_date,
            e.termination_date,
            EXTRACT(YEAR FROM AGE(COALESCE(e.termination_date, CURRENT_DATE), e.hire_date)) as tenure_years,
            e.job_title,
            e.salary,
            e.employment_status,
            d.name as department_name,
            d.code as department_code,
            d.description as department_description,
            CASE 
                WHEN e.employment_status = 'terminated' THEN 1 
                ELSE 0 
            END as has_left,
            CASE 
                WHEN e.salary < 30000 THEN 'Entry Level'
                WHEN e.salary < 60000 THEN 'Mid Level'
                WHEN e.salary < 100000 THEN 'Senior Level'
                ELSE 'Executive'
            END as salary_bracket,
            CASE
                WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, e.hire_date)) < 1 THEN 'Less than 1 year'
                WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, e.hire_date)) < 3 THEN '1-3 years'
                WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, e.hire_date)) < 5 THEN '3-5 years'
                WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, e.hire_date)) < 10 THEN '5-10 years'
                ELSE 'More than 10 years'
            END as tenure_bracket
        FROM employees e
        LEFT JOIN departments d ON e.department_id = d.id
        ORDER BY e.id
    """)
    
    result = db.execute(query)
    rows = result.fetchall()
    
    # Convert to list of dicts
    columns = result.keys()
    data = []
    for row in rows:
        row_dict = {}
        for i, col in enumerate(columns):
            value = row[i]
            # Convert date objects to ISO format strings
            if isinstance(value, (date, datetime)):
                value = value.isoformat()
            row_dict[col] = value
        data.append(row_dict)
    
    return data


@router.get("/attendance-export")
async def export_attendance_for_qlik(
    start_date: str = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Export attendance data for Qlik Sense
    """
    where_clause = ""
    if start_date and end_date:
        where_clause = f"WHERE a.date BETWEEN '{start_date}' AND '{end_date}'"
    
    query = text(f"""
        SELECT 
            a.id,
            a.employee_id,
            e.employee_code,
            e.first_name || ' ' || e.last_name as employee_name,
            d.name as department_name,
            a.date,
            EXTRACT(YEAR FROM a.date) as year,
            EXTRACT(MONTH FROM a.date) as month,
            TO_CHAR(a.date, 'Month') as month_name,
            EXTRACT(QUARTER FROM a.date) as quarter,
            TO_CHAR(a.date, 'Day') as day_of_week,
            a.check_in_time,
            a.check_out_time,
            a.attendance_type,
            a.notes,
            CASE 
                WHEN a.attendance_type = 'absent' THEN 1 
                ELSE 0 
            END as is_absent,
            CASE 
                WHEN a.attendance_type = 'late' THEN 1 
                ELSE 0 
            END as is_late,
            CASE 
                WHEN a.attendance_type IN ('present', 'work_from_home') THEN 1 
                ELSE 0 
            END as is_present
        FROM attendance a
        LEFT JOIN employees e ON a.employee_id = e.id
        LEFT JOIN departments d ON e.department_id = d.id
        {where_clause}
        ORDER BY a.date DESC
    """)
    
    result = db.execute(query)
    rows = result.fetchall()
    
    columns = result.keys()
    data = []
    for row in rows:
        row_dict = {}
        for i, col in enumerate(columns):
            value = row[i]
            if isinstance(value, (date, datetime)):
                value = value.isoformat()
            row_dict[col] = value
        data.append(row_dict)
    
    return data


@router.get("/departments-summary")
async def departments_summary_for_qlik(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """
    Department-level summary statistics for Qlik Sense
    """
    query = text("""
        SELECT 
            d.id as department_id,
            d.name as department_name,
            d.code as department_code,
            COUNT(e.id) as total_employees,
            COUNT(CASE WHEN e.employment_status = 'active' THEN 1 END) as active_employees,
            COUNT(CASE WHEN e.employment_status = 'terminated' THEN 1 END) as terminated_employees,
            COALESCE(AVG(e.salary), 0) as avg_salary,
            COALESCE(MIN(e.salary), 0) as min_salary,
            COALESCE(MAX(e.salary), 0) as max_salary,
            COALESCE(AVG(EXTRACT(YEAR FROM AGE(CURRENT_DATE, e.hire_date))), 0) as avg_tenure_years,
            COALESCE(
                COUNT(CASE WHEN e.employment_status = 'terminated' THEN 1 END)::float / 
                NULLIF(COUNT(e.id), 0) * 100, 
                0
            ) as turnover_rate
        FROM departments d
        LEFT JOIN employees e ON e.department_id = d.id
        GROUP BY d.id, d.name, d.code
        ORDER BY d.name
    """)
    
    result = db.execute(query)
    rows = result.fetchall()
    
    columns = result.keys()
    data = []
    for row in rows:
        row_dict = {}
        for i, col in enumerate(columns):
            value = row[i]
            # Round float values
            if isinstance(value, float):
                value = round(value, 2)
            row_dict[col] = value
        data.append(row_dict)
    
    return data


@router.get("/kpi-summary")
async def kpi_summary_for_qlik(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Global KPIs for Qlik Sense dashboard
    """
    query = text("""
        SELECT 
            COUNT(*) as total_employees,
            COUNT(CASE WHEN employment_status = 'active' THEN 1 END) as active_employees,
            COUNT(CASE WHEN employment_status = 'terminated' THEN 1 END) as terminated_employees,
            COUNT(CASE WHEN employment_status = 'on_leave' THEN 1 END) as on_leave_employees,
            COALESCE(AVG(salary), 0) as avg_salary,
            COALESCE(SUM(salary), 0) as total_salary_cost,
            COALESCE(AVG(EXTRACT(YEAR FROM AGE(CURRENT_DATE, hire_date))), 0) as avg_tenure_years,
            COUNT(CASE WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, hire_date)) < 1 THEN 1 END) as new_hires_last_year,
            COALESCE(
                COUNT(CASE WHEN employment_status = 'terminated' THEN 1 END)::float / 
                NULLIF(COUNT(*), 0) * 100, 
                0
            ) as turnover_rate
        FROM employees
    """)
    
    result = db.execute(query)
    row = result.fetchone()
    
    columns = result.keys()
    data = {}
    for i, col in enumerate(columns):
        value = row[i]
        if isinstance(value, float):
            value = round(value, 2)
        data[col] = value
    
    return data


@router.get("/health")
async def health_check():
    """Health check for Qlik connection"""
    return {
        "status": "healthy",
        "service": "Qlik Integration API",
        "timestamp": datetime.now().isoformat()
    }
