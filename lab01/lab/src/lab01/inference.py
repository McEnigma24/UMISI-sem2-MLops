from pathlib import Path

import joblib

MODEL_PATH = Path(__file__).with_name("iris_model.joblib")


def load_model(path=MODEL_PATH):
    return joblib.load(path)


def predict(model, flower_params):
    class_id = int(model.predict(flower_params)[0])

    match class_id:
        case 0:
            return "setosa"
        case 1:
            return "versicolor"
        case 2:
            return "virginica"
        case _:
            raise ValueError(f"unknown class: {class_id}")


if __name__ == "__main__":
    model = load_model()
    print(f"predict {predict(model, [[8, 4, 6, 2]])}")
