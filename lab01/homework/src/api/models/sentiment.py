from pydantic import BaseModel

from pathlib import Path
from sentence_transformers import SentenceTransformer
import joblib


class PredictRequest(BaseModel):
    text: str


class PredictResponse(BaseModel):
    prediction: str


def load_model():
    base = Path(__file__).parent
    encoder = SentenceTransformer(str(base / "sentence_transformer.model"))
    classifier = joblib.load(base / "classifier.joblib")
    return encoder, classifier


def get_model_prediction(encoder, classifier, req: PredictRequest) -> str:
    text_embedding = encoder.encode([req.text])  # shape (1, n_features)
    class_id = int(classifier.predict(text_embedding)[0])
    return LABELS[class_id]


LABELS = {0: "negative", 1: "neutral", 2: "positive"}


def get_sentiment(encoder, classifier, req: PredictRequest):

    # print(get_model_prediction(encoder, classifier,
    #     PredictRequest(text="This lab assignments are very cool and I will learn usefull things while going through them"))) # this one is true :)

    # print(get_model_prediction(encoder, classifier,
    #     PredictRequest(text="This lab is about beginner dev ops tasks")))

    # print(get_model_prediction(encoder, classifier,
    #     PredictRequest(text="This lab is a nothing burger")))

    return PredictResponse(prediction=get_model_prediction(encoder, classifier, req))
