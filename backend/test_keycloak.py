import httpx
import asyncio

async def test_client_credentials():
    """Test client_credentials grant"""
    data = {
        'grant_type': 'client_credentials',
        'client_id': 'hr-analytics-app',
        'client_secret': 'vUFtV3go28MIO8LhPSaFWvSB9OpoWDjo'
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(
            'http://localhost:8080/realms/hr-analytics/protocol/openid-connect/token',
            data=data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        print(f'Client Credentials Grant:')
        print(f'  Status: {response.status_code}')
        print(f'  Response: {response.text[:500]}')
        print()

async def test_authorization_code():
    """Test if authorization_code grant is enabled"""
    # This simulates the callback - we can't test without a real code
    # But we can check the error message
    data = {
        'grant_type': 'authorization_code',
        'client_id': 'hr-analytics-app',
        'client_secret': 'vUFtV3go28MIO8LhPSaFWvSB9OpoWDjo',
        'code': 'fake_code_for_testing',
        'redirect_uri': 'http://localhost:3000/login'
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(
            'http://localhost:8080/realms/hr-analytics/protocol/openid-connect/token',
            data=data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        print(f'Authorization Code Grant (with fake code):')
        print(f'  Status: {response.status_code}')
        print(f'  Response: {response.text[:500]}')
        print()

async def main():
    await test_client_credentials()
    await test_authorization_code()

if __name__ == "__main__":
    asyncio.run(main())
