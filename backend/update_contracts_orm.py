"""
Mettre à jour les types de contrats via l'ORM
"""
import sys
sys.path.insert(0, 'C:/Users/wdaoud/Desktop/test/backend')

from app.db.base import SessionLocal
from app.models.employee import Employee

db = SessionLocal()

try:
    # Compter les employés sans type de contrat
    total = db.query(Employee).count()
    with_contract = db.query(Employee).filter(Employee.contract_type != None).count()
    without_contract = total - with_contract
    
    print(f"📊 Statistiques:")
    print(f"  Total employés: {total}")
    print(f"  Avec type contrat: {with_contract}")
    print(f"  Sans type contrat (NULL): {without_contract}")
    
    if without_contract > 0:
        print(f"\n🔧 Mise à jour de {without_contract} employés avec 'CDI'...")
        
        # Mettre à jour tous les employés sans contract_type
        employees = db.query(Employee).filter(Employee.contract_type == None).all()
        
        for emp in employees:
            emp.contract_type = "CDI"
        
        db.commit()
        print(f"✅ {len(employees)} employés mis à jour!")
        
        # Afficher quelques exemples
        print("\n📋 Exemples:")
        examples = db.query(Employee).limit(5).all()
        for emp in examples:
            print(f"  {emp.employee_code} - {emp.first_name} {emp.last_name} - {emp.contract_type}")
    else:
        print("\n✅ Tous les employés ont déjà un type de contrat!")
        
finally:
    db.close()
