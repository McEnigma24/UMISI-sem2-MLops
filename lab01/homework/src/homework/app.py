from fastapi import FastAPI

from api.models.sentiment import PredictRequest, PredictResponse
from api.models.sentiment import load_model
from api.models.sentiment import get_sentiment

app = FastAPI()
encoder, classifier = load_model()


@app.post("/predict")
def predict(request: PredictRequest) -> PredictResponse:
    return get_sentiment(encoder, classifier, request)
