import os
import pickle

from tensorflow import keras

from iris_sklearn.service import IrisSKClassifier


def pack() -> str:
    model_path = os.path.join(os.path.dirname(__file__), "model")
    iris_sk_classifier_model = pickle.load(open(model_path, "rb"))
    iris_sk_classifier_service = IrisSKClassifier()
    iris_sk_classifier_service.pack("model", iris_sk_classifier_model)
    saved_path = iris_sk_classifier_service.save()
    return saved_path


if __name__ == "__main__":
    pack()
