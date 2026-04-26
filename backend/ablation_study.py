"""
Ablation Study for IEEE Paper
=============================
Trains three architectures side-by-side on the strawberry disease dataset:

  1. Simple CNN Baseline        (lightweight, no residual connections)
  2. ResNet-18                  (residual learning, NO SE blocks)
  3. ResNet-18 + SE (Proposed)  (residual learning + channel attention)

Outputs:
  - Per-epoch accuracy / loss logs
  - Final comparison table (console + saved to ../ablation_results.json)
  - Best model weights for each variant

Usage:
    cd backend
    python ablation_study.py
"""

import os
import sys
import json
import time
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

from model import ResNet18, ResNet18_SE, build_model

# ------------------------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------------------------
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
EPOCHS = 10
BATCH_SIZE = 16
LR = 0.001
DATASET_ROOT = "../dataset"
RESULTS_PATH = "../ablation_results.json"

# Class names (ImageFolder alphabetical order)
CLASS_NAMES = ["Strawberry___Leaf_scorch", "Strawberry___healthy", "powdery_mildew"]
NUM_CLASSES = len(CLASS_NAMES)

# ------------------------------------------------------------------------------
# SIMPLE CNN BASELINE (for ablation comparison)
# ------------------------------------------------------------------------------

class SimpleCNN(nn.Module):
    """
    Baseline CNN without residual connections or attention.
    4 conv blocks + 2 FC layers.
    """
    def __init__(self, num_classes=3):
        super(SimpleCNN, self).__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, 3, padding=1), nn.BatchNorm2d(32), nn.ReLU(),
            nn.MaxPool2d(2),

            nn.Conv2d(32, 64, 3, padding=1), nn.BatchNorm2d(64), nn.ReLU(),
            nn.MaxPool2d(2),

            nn.Conv2d(64, 128, 3, padding=1), nn.BatchNorm2d(128), nn.ReLU(),
            nn.MaxPool2d(2),

            nn.Conv2d(128, 256, 3, padding=1), nn.BatchNorm2d(256), nn.ReLU(),
            nn.AdaptiveAvgPool2d(1)
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, num_classes)
        )

    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x


# ------------------------------------------------------------------------------
# DATA LOADING
# ------------------------------------------------------------------------------

def get_data_loaders():
    train_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(10),
        transforms.ColorJitter(brightness=0.2, contrast=0.2),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    test_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    train_dataset = datasets.ImageFolder(root=f"{DATASET_ROOT}/train",
                                         transform=train_transform)
    test_dataset = datasets.ImageFolder(root=f"{DATASET_ROOT}/test",
                                        transform=test_transform)

    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE,
                              shuffle=True, num_workers=0)
    test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE,
                             shuffle=False, num_workers=0)

    print(f"[DATA] Train: {len(train_dataset)} | Test: {len(test_dataset)}")
    return train_loader, test_loader


# ------------------------------------------------------------------------------
# TRAINING & EVALUATION HELPERS
# ------------------------------------------------------------------------------

def train_one_epoch(model, loader, criterion, optimizer, device):
    model.train()
    total_loss = 0.0
    correct = 0
    total = 0

    for images, labels in loader:
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        total_loss += loss.item() * images.size(0)
        _, predicted = torch.max(outputs, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()

    avg_loss = total_loss / total
    accuracy = 100 * correct / total
    return avg_loss, accuracy


@torch.no_grad()
def evaluate(model, loader, criterion, device):
    model.eval()
    total_loss = 0.0
    correct = 0
    total = 0

    for images, labels in loader:
        images, labels = images.to(device), labels.to(device)
        outputs = model(images)
        loss = criterion(outputs, labels)

        total_loss += loss.item() * images.size(0)
        _, predicted = torch.max(outputs, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()

    avg_loss = total_loss / total
    accuracy = 100 * correct / total
    return avg_loss, accuracy


# ------------------------------------------------------------------------------
# SINGLE EXPERIMENT RUN
# ------------------------------------------------------------------------------

def run_experiment(name, model, train_loader, test_loader, epochs, device):
    print(f"\n{'='*60}")
    print(f"EXPERIMENT: {name}")
    print(f"{'='*60}")

    model = model.to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=LR)

    history = {
        "name": name,
        "epochs": [],
        "best_test_acc": 0.0,
        "params": sum(p.numel() for p in model.parameters())
    }

    best_acc = 0.0
    best_state = None

    for epoch in range(1, epochs + 1):
        t0 = time.time()
        train_loss, train_acc = train_one_epoch(model, train_loader, criterion,
                                                optimizer, device)
        test_loss, test_acc = evaluate(model, test_loader, criterion, device)
        elapsed = time.time() - t0

        history["epochs"].append({
            "epoch": epoch,
            "train_loss": round(train_loss, 4),
            "train_acc": round(train_acc, 2),
            "test_loss": round(test_loss, 4),
            "test_acc": round(test_acc, 2),
            "time_sec": round(elapsed, 1)
        })

        print(f"  Epoch {epoch:02d}/{epochs} | "
              f"Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.2f}% | "
              f"Test Loss: {test_loss:.4f} | Test Acc: {test_acc:.2f}% | "
              f"Time: {elapsed:.1f}s")

        if test_acc > best_acc:
            best_acc = test_acc
            best_state = model.state_dict()

    history["best_test_acc"] = round(best_acc, 2)

    # Save best weights
    weight_path = f"../model_{name.lower().replace(' ', '_')}.pth"
    if best_state is not None:
        torch.save(best_state, weight_path)
        print(f"  -> Best model saved: {weight_path} (Test Acc: {best_acc:.2f}%)")

    return history


# ------------------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------------------

def main():
    print(f"[DEVICE] {DEVICE}")
    print(f"[EPOCHS] {EPOCHS} | [BATCH] {BATCH_SIZE} | [LR] {LR}")

    train_loader, test_loader = get_data_loaders()

    experiments = [
        ("Simple CNN", SimpleCNN(num_classes=NUM_CLASSES)),
        ("ResNet-18", ResNet18(num_classes=NUM_CLASSES)),
        ("ResNet-18 SE", ResNet18_SE(num_classes=NUM_CLASSES, reduction=16)),
    ]

    all_results = []
    for name, model in experiments:
        result = run_experiment(name, model, train_loader, test_loader,
                                EPOCHS, DEVICE)
        all_results.append(result)

    # Save JSON report
    with open(RESULTS_PATH, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\n[SAVED] Results written to {RESULTS_PATH}")

    # Print final comparison table
    print(f"\n{'='*60}")
    print("FINAL COMPARISON TABLE")
    print(f"{'='*60}")
    print(f"{'Model':<18} {'Params':>12} {'Best Test Acc':>15}")
    print("-" * 50)
    for r in all_results:
        print(f"{r['name']:<18} {r['params']:>12,} {r['best_test_acc']:>14.2f}%")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()

