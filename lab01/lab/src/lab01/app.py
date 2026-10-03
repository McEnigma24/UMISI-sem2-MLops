from fastapi import FastAPI

from lab01.api.models.iris import PredictRequest, PredictResponse
from lab01.inference import load_model
from lab01.inference import predict as predict_class

app = FastAPI()

model = load_model()


@app.get("/")
def welcome_root():
    return {"message": "Welcome to the ML API"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/predict")
def predict(request: PredictRequest) -> PredictResponse:
    features = [
        [
            request.sepal_length,
            request.sepal_width,
            request.petal_length,
            request.petal_width,
        ]
    ]
    return PredictResponse(prediction=predict_class(model, features))
