import os

from tensorflow import keras

from mnist_tf.service import MnistTFClassifier


def pack() -> str:
    model_path = os.path.join(os.path.dirname(__file__), "model")
    mnist_tf_classifier_model = keras.models.load_model(model_path)
    mnist_tf_classifier_service = MnistTFClassifier()
    mnist_tf_classifier_service.pack("model", mnist_tf_classifier_model)
    saved_path = mnist_tf_classifier_service.save()
    return saved_path


if __name__ == "__main__":
    pack()
