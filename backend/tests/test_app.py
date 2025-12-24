from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_endpoint_internal():
    response = client.get("/api/health")
    assert response.status_code == 200
