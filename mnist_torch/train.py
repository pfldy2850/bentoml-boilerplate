import argparse
import os
import random

import bentoml
import numpy as np
import torch
import torch.nn.functional as F
from sklearn.model_selection import KFold
from torch import nn
from torch.utils.data import ConcatDataset, DataLoader
from torchvision import transforms
from torchvision.datasets import MNIST

import torch


class SimpleConvNet(torch.nn.Module):
    """
    Simple Convolutional Neural Network
    """

    def __init__(self):
        super().__init__()
        self.layers = torch.nn.Sequential(
            torch.nn.Conv2d(1, 10, kernel_size=3),
            torch.nn.ReLU(),
            torch.nn.Flatten(),
            torch.nn.Linear(26 * 26 * 10, 50),
            torch.nn.ReLU(),
            torch.nn.Linear(50, 20),
            torch.nn.ReLU(),
            torch.nn.Linear(20, 10),
        )

    def forward(self, x):
        return self.layers(x)

    def predict(self, inp):
        """predict digit for input"""
        self.eval()
        with torch.no_grad():
            raw_output = self(inp)
            _, pred = torch.max(raw_output, 1)
            return pred


def train():
    K_FOLDS = 1
    NUM_EPOCHS = 3
    LOSS_FUNCTION = nn.CrossEntropyLoss()

    # reproducible setup for testing
    seed = 42
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True

    def _dataloader_init_fn(worker_id):
        np.random.seed(seed)

    def get_dataset():
        # Prepare MNIST dataset by concatenating Train/Test part; we split later.
        train_set = MNIST(
            os.getcwd(), download=True, transform=transforms.ToTensor(), train=True
        )
        test_set = MNIST(
            os.getcwd(), download=True, transform=transforms.ToTensor(), train=False
        )
        return train_set, test_set

    def train_epoch(model, optimizer, loss_function, train_loader, epoch, device="cpu"):
        # Mark training flag
        model.train()
        for batch_idx, (inputs, targets) in enumerate(train_loader):
            inputs, targets = inputs.to(device), targets.to(device)
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = loss_function(outputs, targets)
            loss.backward()
            optimizer.step()
            if batch_idx % 499 == 0:
                print(
                    "Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}".format(
                        epoch,
                        batch_idx * len(inputs),
                        len(train_loader.dataset),
                        100.0 * batch_idx / len(train_loader),
                        loss.item(),
                    )
                )

    def test_model(model, test_loader, device="cpu"):
        correct, total = 0, 0
        model.eval()
        with torch.no_grad():
            for batch_idx, (inputs, targets) in enumerate(test_loader):
                inputs, targets = inputs.to(device), targets.to(device)
                outputs = model(inputs)
                _, predicted = torch.max(outputs.data, 1)
                total += targets.size(0)
                correct += (predicted == targets).sum().item()

        return correct, total

    def cross_validate(dataset, epochs=NUM_EPOCHS, k_folds=K_FOLDS):
        results = {}

        # Define the K-fold Cross Validator
        kfold = KFold(n_splits=k_folds, shuffle=True)

        print("--------------------------------")

        # K-fold Cross Validation model evaluation
        for fold, (train_ids, test_ids) in enumerate(kfold.split(dataset)):

            print(f"FOLD {fold}")
            print("--------------------------------")

            # Sample elements randomly from a given list of ids, no replacement.
            train_subsampler = torch.utils.data.SubsetRandomSampler(train_ids)
            test_subsampler = torch.utils.data.SubsetRandomSampler(test_ids)

            # Define data loaders for training and testing data in this fold
            train_loader = torch.utils.data.DataLoader(
                dataset,
                batch_size=10,
                sampler=train_subsampler,
                worker_init_fn=_dataloader_init_fn,
            )
            test_loader = torch.utils.data.DataLoader(
                dataset,
                batch_size=10,
                sampler=test_subsampler,
                worker_init_fn=_dataloader_init_fn,
            )

            # Train this fold
            model = SimpleConvNet()
            optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)
            loss_function = nn.CrossEntropyLoss()
            for epoch in range(epochs):
                train_epoch(model, optimizer, loss_function, train_loader, epoch)

            # Evaluation for this fold
            correct, total = test_model(model, test_loader)
            print("Accuracy for fold %d: %d %%" % (fold, 100.0 * correct / total))
            print("--------------------------------")
            results[fold] = 100.0 * (correct / total)

        # Print fold results
        print(f"K-FOLD CROSS VALIDATION RESULTS FOR {K_FOLDS} FOLDS")
        print("--------------------------------")
        sum = 0.0
        for key, value in results.items():
            print(f"Fold {key}: {value} %")
            sum += value

        print(f"Average: {sum / len(results.items())} %")

        return results

    def _train(dataset, epochs=NUM_EPOCHS, device="cpu"):
        train_sampler = torch.utils.data.RandomSampler(dataset)
        train_loader = torch.utils.data.DataLoader(
            dataset,
            batch_size=10,
            sampler=train_sampler,
            worker_init_fn=_dataloader_init_fn,
        )
        model = SimpleConvNet()
        optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)
        loss_function = nn.CrossEntropyLoss()
        for epoch in range(epochs):
            train_epoch(model, optimizer, loss_function, train_loader, epoch, device)
        return model

    use_cuda = torch.cuda.is_available()

    device = torch.device("cuda" if use_cuda else "cpu")

    train_set, test_set = get_dataset()
    test_loader = torch.utils.data.DataLoader(
        test_set,
        batch_size=10,
        sampler=torch.utils.data.RandomSampler(test_set),
        worker_init_fn=_dataloader_init_fn,
    )

    if K_FOLDS > 1:
        cv_results = cross_validate(train_set, NUM_EPOCHS, K_FOLDS)
    else:
        cv_results = {}

    trained_model = _train(train_set, NUM_EPOCHS, device)
    correct, total = test_model(trained_model, test_loader, device)

    # training related
    metadata = {
        "acc": float(correct) / total,
        "cv_stats": cv_results,
    }

    model_path = os.path.join(os.path.dirname(__file__), "model_scripted.pt")
    model_scripted = torch.jit.script(trained_model)  # Export to TorchScript
    model_scripted.save(model_path)  # Save


if __name__ == "__main__":
    train()
