"""
Script to export HR data to CSV format for Qlik Sense
Usage: python export_data_for_qlik.py
"""
import sys
import os
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.append(str(Path(__file__).parent.parent))

import pandas as pd
from sqlalchemy import create_engine, text
from app.core.config import settings
from datetime import datetime


def export_data():
    """Export all relevant HR data to CSV files for Qlik Sense"""
    
    # Create output directory
    output_dir = Path("qlik_data")
    output_dir.mkdir(exist_ok=True)
    
    # Connect to database
    print("🔗 Connecting to database...")
    engine = create_engine(settings.DATABASE_URL)
    
    print("📊 Exporting data...")
    
    # 1. Export Employees with enriched data
    print("  ↳ Exporting employees...")
    employees_query = text("""
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
    """)
    
    with engine.connect() as conn:
        employees_df = pd.read_sql(employees_query, conn)
        employees_df.to_csv(output_dir / "employees.csv", index=False)
        print(f"    ✅ Exported {len(employees_df)} employees")
    
    # 2. Export Departments
    print("  ↳ Exporting departments...")
    departments_query = text("""
        SELECT 
            d.id,
            d.name,
            d.code,
            d.description,
            COUNT(e.id) as employee_count,
            COALESCE(AVG(e.salary), 0) as avg_salary
        FROM departments d
        LEFT JOIN employees e ON e.department_id = d.id AND e.employment_status = 'active'
        GROUP BY d.id, d.name, d.code, d.description
    """)
    
    with engine.connect() as conn:
        departments_df = pd.read_sql(departments_query, conn)
        departments_df.to_csv(output_dir / "departments.csv", index=False)
        print(f"    ✅ Exported {len(departments_df)} departments")
    
    # 3. Export Attendance
    print("  ↳ Exporting attendance...")
    attendance_query = text("""
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
            CASE 
                WHEN a.attendance_type = 'absent' THEN 1 
                ELSE 0 
            END as is_absent
        FROM attendance a
        LEFT JOIN employees e ON a.employee_id = e.id
        LEFT JOIN departments d ON e.department_id = d.id
    """)
    
    with engine.connect() as conn:
        attendance_df = pd.read_sql(attendance_query, conn)
        attendance_df.to_csv(output_dir / "attendance.csv", index=False)
        print(f"    ✅ Exported {len(attendance_df)} attendance records")
    
    # 4. Export Department Summary (pre-aggregated for KPIs)
    print("  ↳ Exporting department summary...")
    dept_summary_query = text("""
        SELECT 
            d.name as department_name,
            COUNT(e.id) as total_employees,
            COUNT(CASE WHEN e.employment_status = 'active' THEN 1 END) as active_employees,
            COUNT(CASE WHEN e.employment_status = 'terminated' THEN 1 END) as terminated_employees,
            COALESCE(AVG(e.salary), 0) as avg_salary,
            COALESCE(
                COUNT(CASE WHEN e.employment_status = 'terminated' THEN 1 END)::float / 
                NULLIF(COUNT(e.id), 0) * 100, 
                0
            ) as turnover_rate
        FROM departments d
        LEFT JOIN employees e ON e.department_id = d.id
        GROUP BY d.name
    """)
    
    with engine.connect() as conn:
        dept_summary_df = pd.read_sql(dept_summary_query, conn)
        dept_summary_df.to_csv(output_dir / "department_summary.csv", index=False)
        print(f"    ✅ Exported department summary")
    
    # Create metadata file
    metadata = {
        "export_date": datetime.now().isoformat(),
        "files": {
            "employees.csv": f"{len(employees_df)} records",
            "departments.csv": f"{len(departments_df)} records",
            "attendance.csv": f"{len(attendance_df)} records",
            "department_summary.csv": f"{len(dept_summary_df)} records"
        }
    }
    
    with open(output_dir / "export_metadata.txt", "w") as f:
        f.write(f"Export Date: {metadata['export_date']}\n\n")
        f.write("Files:\n")
        for file, count in metadata['files'].items():
            f.write(f"  - {file}: {count}\n")
    
    print(f"\n✅ Export complete! Files saved in: {output_dir.absolute()}")
    print("\n📋 Next steps:")
    print("1. Go to Qlik Sense Cloud (qlik.com)")
    print("2. Create a new app or open existing 'HR Analytics'")
    print("3. Click 'Add data' > 'Upload files'")
    print("4. Upload all CSV files from qlik_data folder")
    print("5. Create visualizations!")


if __name__ == "__main__":
    try:
        export_data()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
