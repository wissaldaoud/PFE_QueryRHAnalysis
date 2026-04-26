import httpx
import time

# Attendre que le backend reload
time.sleep(2)

# 1. Login en tant que Karim
print("=== CONNEXION KARIM ===")
r = httpx.post('http://127.0.0.1:8000/api/v1/auth/login', 
               data={'username':'karim.alaoui@soprahr.com','password':'password123'},
               timeout=15.0)
print(f"Status: {r.status_code}")
if r.status_code != 200:
    print(f"Erreur: {r.text}")
    exit(1)

token_data = r.json()
token = token_data['access_token']
user = token_data['user']
print(f"Connecté: {user['email']} - Role: {user['role']}")
print(f"Employee ID: {user.get('employee_id', 'N/A')}")
print()

# 2. Récupérer les demandes de congé
print("=== DEMANDES DE CONGÉ (Vue Manager) ===")
r = httpx.get('http://127.0.0.1:8000/api/v1/leaves/?page=1&page_size=20',
              headers={'Authorization': f'Bearer {token}'},
              timeout=15.0,
              follow_redirects=True)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    leaves = data.get('items', [])
    print(f"Nombre total de demandes: {len(leaves)}")
    
    # Filtrer les demandes "pending" (en attente d'approbation manager)
    pending = [l for l in leaves if l.get('status') == 'pending']
    print(f"Demandes EN ATTENTE (pending): {len(pending)}")
    
    if pending:
        for leave in pending:
            print(f"\n  ✓ ID: {leave['id']}")
            print(f"    Employé: {leave.get('employee_name', 'N/A')}")
            print(f"    Type: {leave['leave_type']}")
            print(f"    Dates: {leave['start_date']} → {leave['end_date']}")
            print(f"    Jours: {leave['days_requested']}")
            print(f"    Statut: {leave['status']}")
    else:
        print("\n  ℹ️ Aucune demande en attente")
        
    # Afficher toutes les demandes
    print(f"\n  TOUTES LES DEMANDES VISIBLES ({len(leaves)}):")
    for leave in leaves[:10]:
        print(f"    - {leave.get('employee_name', 'N/A')}: {leave['status']}")
else:
    print(f"Erreur: {r.text}")
print()

# 3. Récupérer les notifications
print("=== NOTIFICATIONS DE KARIM ===")
r = httpx.get('http://127.0.0.1:8000/api/v1/notifications/',
              headers={'Authorization': f'Bearer {token}'},
              timeout=15.0,
              follow_redirects=True)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    notifs = r.json()
    print(f"Nombre de notifications: {len(notifs)}")
    for notif in notifs[:5]:
        status = "✓ Lu" if notif.get('is_read', False) else "⚪ Non lu"
        print(f"\n  {status} - {notif.get('title', 'No title')}")
        print(f"      {notif.get('message', 'No message')}")
else:
    print(f"Erreur: {r.text}")

