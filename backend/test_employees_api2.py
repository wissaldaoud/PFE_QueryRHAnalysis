"""Quick test of employees API endpoint"""
import requests
import json

# Test sans authentification d'abord
print("Testing employees API endpoint...")

# Test 1: Sans token
print("\n1. Test sans token:")
response = requests.get("http://localhost:8000/api/v1/hr-analytics/employees?all=true")
print(f"   Status: {response.status_code}")
if response.status_code == 401:
    print("   ✓ Authentification requise (attendu)")
else:
    print(f"   Response: {response.text[:200]}")

# Test 2: Avec un faux token
print("\n2. Test avec faux token:")
headers = {"Authorization": "Bearer fake_token"}
response = requests.get("http://localhost:8000/api/v1/hr-analytics/employees?all=true", headers=headers)
print(f"   Status: {response.status_code}")
print(f"   Response: {response.text[:200]}")

print("\n3. Instructions:")
print("   - Si vous voyez 401: L'API requiert un token valide")
print("   - Connectez-vous à l'application web")
print("   - Ouvrez la console (F12)")
print("   - Tapez: localStorage.getItem('access_token')")
print("   - Copiez le token et testez à nouveau")
