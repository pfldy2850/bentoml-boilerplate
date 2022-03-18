import torch

from mnist_torch.service import MnistTorchClassifier


def pack() -> str:
    mnist_torch_classifier_model = torch.jit.load("model_scripted.pt")
    mnist_torch_classifier_service = MnistTorchClassifier()
    mnist_torch_classifier_service.pack("model", mnist_torch_classifier_model)
    saved_path = mnist_torch_classifier_service.save()
    return saved_path


if __name__ == "__main__":
    pack()
