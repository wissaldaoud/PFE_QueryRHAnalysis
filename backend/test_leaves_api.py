import requests

# Login
login_resp = requests.post(
    "http://127.0.0.1:8001/api/v1/auth/login",
    data={"username": "admin@company.com", "password": "admin123"}
)
print("Login status:", login_resp.status_code)
token = login_resp.json().get("access_token")
print("Token:", token[:50] + "..." if token else "None")

# Get leaves
headers = {"Authorization": f"Bearer {token}"}
leaves_resp = requests.get(
    "http://127.0.0.1:8001/api/v1/leaves?status=pending",
    headers=headers
)
print("\nLeaves status:", leaves_resp.status_code)
if leaves_resp.status_code == 200:
    data = leaves_resp.json()
    print(f"Total pending: {data.get('total')}")
    for item in data.get('items', [])[:5]:
        print(f"  - ID {item['id']}: {item.get('employee_name', 'N/A')} - {item['status']}")
else:
    print("Error:", leaves_resp.text)
