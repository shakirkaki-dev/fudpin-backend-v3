from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_login_invalid_user():
    response = client.post("/auth/login", json={
        "email": "fakeuser@test.com",
        "password": "wrongpassword"
    })

    assert response.status_code == 401
