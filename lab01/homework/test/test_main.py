import pytest
from fastapi.testclient import TestClient

from homework.settings import Settings
from homework.app import app

client = TestClient(app)


def assert_model_prediction(input_text: str, expected_output: str) -> None:
    response = client.post("/predict", json={"text": input_text})
    assert response.status_code == 200
    assert response.json().get("prediction") == expected_output


def test_read_main():

    settings = Settings()

    print("APP_NAME: ", settings.APP_NAME)
    print("ENVIRONMENT: ", settings.ENVIRONMENT)

    assert_model_prediction("I am happy", "positive")
    assert_model_prediction("I am sad", "negative")
    assert_model_prediction("I am neutral", "positive")


@pytest.mark.parametrize(
    ("input_text", "expected_output"),
    [
        ("I am happy", "positive"),
        ("I am sad", "negative"),
        ("I am neutral", "positive"),
    ],
)
def test_predict(input_text: str, expected_output: str) -> None:
    response = client.post("/predict", json={"text": input_text})
    assert response.status_code == 200
    assert response.json()["prediction"] == expected_output
