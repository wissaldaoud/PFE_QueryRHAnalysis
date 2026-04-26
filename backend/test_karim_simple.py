import httpx
import time

time.sleep(2)

# 1. Test de connexion Karim
print("=== TEST KARIM ===\n")
try:
    r = httpx.post('http://127.0.0.1:8000/api/v1/auth/login', 
                   data={'username':'karim.alaoui@soprahr.com','password':'password123'},
                   timeout=10.0)
    
    if r.status_code != 200:
        print(f"Erreur connexion: {r.status_code}")
        print(r.text)
        exit(1)
    
    data = r.json()
    token = data['access_token']
    user = data['user']
    
    print(f"Connecte: {user['email']}")
    print(f"Role: {user['role']}")
    print(f"Employee ID dans user: {user.get('employee_id', 'N/A')}")
    print()
    
    # 2. Récupérer les demandes de congé
    print("=== DEMANDES DE CONGE ===\n")
    r = httpx.get('http://127.0.0.1:8000/api/v1/leaves/?page=1&page_size=20',
                  headers={'Authorization': f'Bearer {token}'},
                  timeout=10.0,
                  follow_redirects=True)
    
    print(f"Status: {r.status_code}")
    
    if r.status_code == 200:
        leaves_data = r.json()
        leaves = leaves_data.get('items', [])
        print(f"Nombre de demandes: {len(leaves)}")
        
        pending = [l for l in leaves if l.get('status') == 'pending']
        print(f"En attente: {len(pending)}\n")
        
        if pending:
            for l in pending:
                print(f"  ID {l['id']}: {l.get('employee_name')} - {l['leave_type']}")
                print(f"    Dates: {l['start_date']} -> {l['end_date']}")
                print(f"    Employee ID: {l['employee_id']}")
                print()
        else:
            print("  Aucune demande en attente")
    else:
        print(f"Erreur: {r.text[:200]}")
    
    # 3. Vérifier l'employee_id de Karim dans la DB
    print("\n=== VERIFICATION DB ===\n")
    r2 = httpx.get('http://127.0.0.1:8000/api/v1/employees/me',
                   headers={'Authorization': f'Bearer {token}'},
                   timeout=10.0,
                   follow_redirects=True)
    
    if r2.status_code == 200:
        emp_data = r2.json()
        print(f"Employee ID: {emp_data.get('id', 'N/A')}")
        print(f"Manager ID: {emp_data.get('manager_id', 'N/A')}")
        print(f"Department ID: {emp_data.get('department_id', 'N/A')}")
    else:
        print(f"Erreur employee/me: {r2.status_code}")

except Exception as e:
    print(f"Erreur: {e}")
    import traceback
    traceback.print_exc()
