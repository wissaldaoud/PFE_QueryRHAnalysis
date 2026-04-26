import httpx

print("Test connexion backend...")
r = httpx.post('http://127.0.0.1:8000/api/v1/auth/login', 
               data={'username':'admin@soprahr.com','password':'admin123456789'}, 
               timeout=10)
print("Auth OK - Status:", r.status_code)

token = r.json()['access_token']
print("Token reçu")

r2 = httpx.post('http://127.0.0.1:8000/api/v1/query/execute', 
                json={'query': 'Combien d employés actifs?'}, 
                headers={'Authorization': f'Bearer {token}'}, 
                timeout=30)

print('Status Query:', r2.status_code)
result = r2.json()

if result.get('success'):
    print('✓ SUCCESS!')
    print('Answer:', result.get('answer'))
    print('SQL:', result.get('sql_query'))
else:
    print('✗ FAILED')
    print('Error:', result.get('detail', result.get('error', 'Unknown')))
