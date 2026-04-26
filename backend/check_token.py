import httpx
from jose import jwt

# Login
r = httpx.post('http://127.0.0.1:8000/api/v1/auth/login-simple', 
               json={'username':'admin@soprahr.com','password':'admin123456789'})
token = r.json()['access_token']
print(f"Token obtenu: {token[:50]}...")

# Decode without verification
decoded = jwt.decode(token, options={"verify_signature": False})
print(f"\nContenu du token JWT:")
for key, value in decoded.items():
    print(f"  {key}: {value}")
