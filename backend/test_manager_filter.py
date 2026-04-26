import requests

BASE_URL = "http://127.0.0.1:8001/api/v1"

def login(email, password):
    response = requests.post(f"{BASE_URL}/auth/login", data={
        "username": email,
        "password": password
    })
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Login failed for {email}: {response.json()}")
        return None

def get_employees(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/employees/", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return []

# Test avec Admin
print("=== TEST ADMIN ===")
admin_token = login("admin@company.com", "admin123")
if admin_token:
    employees = get_employees(admin_token)
    print(f"Admin voit {len(employees)} employés")

# Test avec Manager Karim
print("\n=== TEST MANAGER KARIM ===")
karim_token = login("karim.alaoui@soprahr.com", "Manager2026!")
if karim_token:
    employees = get_employees(karim_token)
    print(f"Karim (Manager IT) voit {len(employees)} employés:")
    for emp in employees[:10]:
        print(f"  - {emp['first_name']} {emp['last_name']} (Dept: {emp['department_id']})")
else:
    print("Impossible de se connecter avec Karim")
