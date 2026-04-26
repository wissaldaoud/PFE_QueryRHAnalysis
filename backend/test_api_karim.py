import requests

# Login Karim
print("=== Test API avec Karim ===")
login_response = requests.post('http://127.0.0.1:8000/api/v1/auth/login', 
    data={'username': 'karim.alaoui@soprahr.com', 'password': 'Manager2026!'})
print(f'Login status: {login_response.status_code}')

if login_response.status_code == 200:
    token = login_response.json().get('access_token')
    print(f'Token obtenu!')
    
    # Get employees
    emp_response = requests.get('http://127.0.0.1:8000/api/v1/employees',
        headers={'Authorization': f'Bearer {token}'})
    print(f'Employees status: {emp_response.status_code}')
    
    employees = emp_response.json()
    print(f'\nNombre employes visibles: {len(employees)}')
    print("Liste:")
    for e in employees:
        print(f'  - {e.get("first_name")} {e.get("last_name")} (dept: {e.get("department_id")})')
else:
    print(f'Erreur login: {login_response.text}')
