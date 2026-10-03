import joblib
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression


def load_data():
    iris = load_iris()
    return iris.data, iris.target


def train_model(X, y):
    model = LogisticRegression(max_iter=200)
    model.fit(X, y)
    return model


def save_model(model, path="iris_model.joblib"):
    joblib.dump(model, path)


if __name__ == "__main__":
    X, y = load_data()

    print(X)
    print("")
    print(y)
    model = train_model(X, y)
    save_model(model)
