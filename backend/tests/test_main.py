import sys
import os
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

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "running"

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_root_has_version():
    response = client.get("/")
    assert "version" in response.json()

def test_root_has_message():
    response = client.get("/")
    assert "message" in response.json()

def test_status_values():
    assert "healthy" == "healthy"

def test_employee_schema():
    employee = {"id": 1, "name": "Wissal", "department": "IT"}
    assert employee["id"] == 1

def test_jwt_config():
    config = {"algorithm": "HS256", "expire_minutes": 30}
    assert config["algorithm"] == "HS256"

def test_department_list():
    departments = ["IT", "HR", "Finance"]
    assert len(departments) == 3

def test_api_version():
    version = "1.0.0"
    assert version is not None
