"""
Guide: Processus d'Affectation d'Équipe à un Manager
=====================================================

Ce document explique comment fonctionne le système de hiérarchie manager-employé
dans l'application HR Analytics.
"""
import sys
sys.path.insert(0, r'C:\Users\wdaoud\Desktop\test\backend')

import httpx
from typing import List, Dict

API_BASE = "http://127.0.0.1:8000/api/v1"

# ============================================================================
# EXPLICATION DU MODÈLE
# ============================================================================
"""
1. MODÈLE DE DONNÉES (Self-Referential Relationship)
   
   Employee:
   ├── id (primary key)
   ├── first_name
   ├── last_name
   ├── email
   ├── department_id  → Département de l'employé
   └── manager_id     → ID de l'employé qui est son manager
   
   IMPORTANT: manager_id fait référence à employees.id (même table)
   
   Exemple:
   - Karim (employee_id: 269, manager_id: NULL) = Manager (pas de manager au-dessus)
   - Fatima (employee_id: 2, manager_id: 269) = Employée de Karim
"""

# ============================================================================
# MÉTHODES D'AFFECTATION
# ============================================================================
"""
2. COMMENT AFFECTER DES EMPLOYÉS À UN MANAGER?

   Méthode 1: Lors de la CRÉATION d'un employé
   -------------------------------------------
   POST /api/v1/employees/
   {
     "first_name": "Fatima",
     "last_name": "Alaoui",
     "email": "fatima@soprahr.com",
     "manager_id": 269,  ← ID du manager
     ...
   }

   Méthode 2: Par MODIFICATION d'un employé existant
   -------------------------------------------------
   PUT /api/v1/employees/{employee_id}
   {
     "manager_id": 269  ← Assigner/Changer le manager
   }

   Méthode 3: Via un script SQL direct (pour données existantes)
   ------------------------------------------------------------
   UPDATE employees 
   SET manager_id = 269 
   WHERE id IN (2, 5, 10);  -- IDs des employés de l'équipe
"""


def login(email: str, password: str) -> str:
    """Se connecter et obtenir le token"""
    response = httpx.post(
        f"{API_BASE}/auth/login",
        data={"username": email, "password": password}
    )
    return response.json()["access_token"] if response.status_code == 200 else None


def get_employee_details(token: str, employee_id: int) -> Dict:
    """Récupérer les détails d'un employé"""
    response = httpx.get(
        f"{API_BASE}/employees/{employee_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    return response.json() if response.status_code == 200 else None


def assign_manager_to_employee(token: str, employee_id: int, manager_id: int) -> bool:
    """
    Affecter un manager à un employé existant
    
    Args:
        token: Token d'authentification (Admin/HR)
        employee_id: ID de l'employé à modifier
        manager_id: ID du manager à assigner
    
    Returns:
        True si succès, False sinon
    """
    response = httpx.put(
        f"{API_BASE}/employees/{employee_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"manager_id": manager_id}
    )
    
    if response.status_code == 200:
        print(f"✅ Manager {manager_id} assigné à l'employé {employee_id}")
        return True
    else:
        print(f"❌ Erreur {response.status_code}: {response.text}")
        return False


def get_team_members(token: str, manager_employee_id: int) -> List[Dict]:
    """
    Récupérer tous les membres de l'équipe d'un manager
    
    Cette fonction interroge tous les employés et filtre ceux qui ont
    le manager_id correspondant.
    """
    # Récupérer tous les employés
    response = httpx.get(
        f"{API_BASE}/employees/?page_size=1000",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code != 200:
        return []
    
    data = response.json()
    all_employees = data.get("items", [])
    
    # Filtrer les membres de l'équipe
    team_members = [
        emp for emp in all_employees 
        if emp.get("manager_id") == manager_employee_id
    ]
    
    return team_members


def demo_affectation():
    """
    Démonstration du processus d'affectation
    """
    print("="*70)
    print("DÉMONSTRATION: AFFECTATION D'ÉQUIPE À UN MANAGER")
    print("="*70)
    
    # Se connecter en tant qu'admin
    token = login("admin@soprahr.com", "admin123456789")
    if not token:
        print("❌ Erreur de connexion")
        return
    
    print("✅ Connecté en tant qu'Admin\n")
    
    # Exemple: Karim est manager (employee_id = 269)
    manager_id = 269
    
    print(f"📊 ÉTAPE 1: Vérifier qui est le manager (ID: {manager_id})")
    manager = get_employee_details(token, manager_id)
    if manager:
        print(f"   Manager: {manager.get('first_name')} {manager.get('last_name')}")
        print(f"   Email: {manager.get('email')}")
        print(f"   Poste: {manager.get('job_title')}")
    
    print(f"\n📊 ÉTAPE 2: Récupérer l'équipe actuelle de Karim")
    team = get_team_members(token, manager_id)
    print(f"   Membres de l'équipe: {len(team)}")
    
    if team:
        for member in team:
            print(f"   - {member.get('first_name')} {member.get('last_name')} (ID: {member.get('id')})")
    else:
        print("   Aucun membre dans l'équipe")
    
    print(f"\n📊 ÉTAPE 3: Comment affecter un nouvel employé à Karim?")
    print("""
    Méthode 1 (API - Modification):
    --------------------------------
    PUT /api/v1/employees/{employee_id}
    Authorization: Bearer {token}
    Content-Type: application/json
    
    {
      "manager_id": 269
    }
    
    Méthode 2 (SQL Direct):
    -----------------------
    UPDATE employees 
    SET manager_id = 269 
    WHERE id = {employee_id};
    
    Méthode 3 (Via Interface):
    --------------------------
    1. Aller sur http://localhost:3000/employees
    2. Cliquer sur un employé
    3. Cliquer "Modifier"
    4. Dans le champ "Manager", sélectionner "Karim Alaoui"
    5. Sauvegarder
    """)
    
    print("\n" + "="*70)
    print("RÉSUMÉ DU PROCESSUS")
    print("="*70)
    print("""
    1️⃣  CRÉATION D'EMPLOYÉ:
        - Lors de la création, spécifier manager_id
        - Le nouvel employé apparaît automatiquement dans l'équipe du manager
    
    2️⃣  MODIFICATION D'EMPLOYÉ:
        - Mettre à jour manager_id via PUT /employees/{id}
        - Changement immédiat de l'affectation
    
    3️⃣  VÉRIFICATION:
        - Manager se connecte → Dashboard affiche le nombre d'employés
        - Manager va à "Congés" → Voit les demandes de son équipe
        - Stats s'actualisent automatiquement
    
    4️⃣  IMPACTS:
        - Dashboard stats: Compteur "Total Employés" et "Employés Actifs"
        - Congés: Seules les demandes de l'équipe sont visibles
        - Notifications: Envoyées au bon manager
    
    ⚠️  RÈGLES IMPORTANTES:
        - Un employé ne peut avoir qu'1 seul manager
        - Un manager peut avoir plusieurs employés
        - manager_id peut être NULL (pour les top managers)
        - Le manager doit exister dans la table employees
    """)


if __name__ == "__main__":
    demo_affectation()
