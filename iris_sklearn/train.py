import os
import pickle

from sklearn import svm
from sklearn import datasets


def train():
    # Load training data
    iris = datasets.load_iris()
    X, y = iris.data, iris.target

    # Model Training
    clf = svm.SVC(gamma="scale")
    clf.fit(X, y)

    model_path = os.path.join(os.path.dirname(__file__), "model")
    pickle.dump(clf, open(model_path, "wb"))


if __name__ == "__main__":
    train()
