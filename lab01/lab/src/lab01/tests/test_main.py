from fastapi.testclient import TestClient

from lab01.app import app

client = TestClient(app)


def test_read_main():

    response = client.get("/asdf")
    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}

    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the ML API"}

    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

    response = client.post(
        "/predict",
        json={
            "sepal_length": 5.1,
            "sepal_width": 3.5,
            "petal_length": 1.4,
            "petal_width": 0.2,
        },
    )

    assert response.status_code == 200
    assert response.json() == {"prediction": "setosa"}

    response = client.post(
        "/predict",
        json={
            "sepal_length": 5,
            "sepal_width": 5,
            "petal_length": 5,
            "petal_width": 0.5,
        },
    )

    assert response.status_code == 200
    assert response.json() == {"prediction": "versicolor"}
