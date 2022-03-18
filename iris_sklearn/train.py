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

    pickle.dump(clf, open("model", "wb"))


if __name__ == "__main__":
    train()
