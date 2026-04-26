import os
import sys
import time
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from model import ResNet9_SE

# Device
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

# Data transforms
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

# Class mapping
class_names = ["Strawberry___Leaf_scorch", "Strawberry___healthy", "powdery_mildew"]

# Load datasets
train_dataset = datasets.ImageFolder(root="../dataset/train", transform=transform)
test_dataset = datasets.ImageFolder(root="../dataset/test", transform=transform)

print(f"Loaded {len(train_dataset)} images from ../dataset/train")
print(f"Loaded {len(test_dataset)} images from ../dataset/test")

# Data loaders
train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True, num_workers=0)
test_loader = DataLoader(test_dataset, batch_size=16, shuffle=False, num_workers=0)

# Model, loss, optimizer
num_classes = len(class_names)
model = ResNet9_SE(num_classes=num_classes).to(device)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# Training
epochs = 5  # Reduced for faster training
best_acc = 0.0

for epoch in range(epochs):
    start_time = time.time()
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0
    batch_count = 0
    
    for images, labels in train_loader:
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        
        running_loss += loss.item()
        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()
        batch_count += 1
        
        if batch_count % 20 == 0:
            print(f"  Epoch {epoch+1} - Batch {batch_count}/{len(train_loader)} - Loss: {loss.item():.4f}")
            sys.stdout.flush()
    
    train_acc = 100 * correct / total
    
    # Evaluation
    model.eval()
    test_correct = 0
    test_total = 0
    with torch.no_grad():
        for images, labels in test_loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            _, predicted = torch.max(outputs.data, 1)
            test_total += labels.size(0)
            test_correct += (predicted == labels).sum().item()
    
    test_acc = 100 * test_correct / test_total
    epoch_time = time.time() - start_time
    
    print(f"Epoch [{epoch+1}/{epochs}] - Time: {epoch_time:.1f}s - Train Acc: {train_acc:.2f}% - Test Acc: {test_acc:.2f}%")
    sys.stdout.flush()
    
    # Save every epoch and best
    torch.save(model.state_dict(), "../model.pth")
    print(f"  Saved model to ../model.pth")
    sys.stdout.flush()
    if test_acc > best_acc:
        best_acc = test_acc
        torch.save(model.state_dict(), "../model_best.pth")
        print(f"  New best accuracy! Saved to ../model_best.pth")
        sys.stdout.flush()

print(f"Training complete. Best test accuracy: {best_acc:.2f}%")

