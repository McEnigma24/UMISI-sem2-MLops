from fastapi.testclient import TestClient

from lab01.app import app

client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the ML API"}

    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

    response = client.get("/asdf")
    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}
