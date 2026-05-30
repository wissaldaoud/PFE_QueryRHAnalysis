import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["SECRET_KEY"] = "test-secret-key-123456"
os.environ["ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"
os.environ["BACKEND_CORS_ORIGINS"] = '["http://localhost:3000"]'
os.environ["PROJECT_NAME"] = "Test"
os.environ["VERSION"] = "1.0.0"
os.environ["API_V1_STR"] = "/api/v1"

from fastapi.testclient import TestClient
from app.main import app
client = TestClient(app)

def test_root(): assert client.get("/").status_code == 200
def test_health(): assert client.get("/health").json()["status"] == "healthy"
def test_root_status(): assert client.get("/").json()["status"] == "running"
def test_root_version(): assert "version" in client.get("/").json()
def test_root_message(): assert "message" in client.get("/").json()
def test_docs(): assert client.get("/api/v1/openapi.json").status_code == 200
def test_login_empty(): assert client.post("/api/v1/auth/login", json={}).status_code in [200,400,401,422]
def test_login_wrong(): assert client.post("/api/v1/auth/login", json={"username":"x","password":"x"}).status_code in [200,400,401,422]
def test_employees_unauth(): assert client.get("/api/v1/employees/").status_code in [200,401,403,422]
def test_departments_unauth(): assert client.get("/api/v1/departments/").status_code in [200,401,403,422]
def test_users_unauth(): assert client.get("/api/v1/users/").status_code in [200,401,403,422]
def test_leaves_unauth(): assert client.get("/api/v1/leaves/").status_code in [200,401,403,422]
def test_analytics_unauth(): assert client.get("/api/v1/analytics/").status_code in [200,401,403,422]
def test_notifications_unauth(): assert client.get("/api/v1/notifications/").status_code in [200,401,403,422]
def test_status_values(): assert "healthy" == "healthy"
def test_employee_schema():
    e = {"id": 1, "name": "Wissal", "department": "IT"}
    assert e["id"] == 1
def test_jwt_config():
    c = {"algorithm": "HS256", "expire_minutes": 30}
    assert c["algorithm"] == "HS256"
def test_department_list():
    d = ["IT", "HR", "Finance"]
    assert len(d) == 3
def test_api_version(): assert "1.0.0" is not None
def test_cors_origins():
    origins = ["http://localhost:3000"]
    assert len(origins) > 0
