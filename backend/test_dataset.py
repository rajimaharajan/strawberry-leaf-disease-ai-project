import os
import sys
from torchvision import datasets, transforms
from torch.utils.data import DataLoader

# Class mapping
class_names = ["Strawberry___Leaf_scorch", "Strawberry___healthy", "powdery_mildew"]

# Transforms
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

print("Loading dataset...")
train_dataset = datasets.ImageFolder(root="../dataset/train", transform=transform)
print(f"Train dataset size: {len(train_dataset)}")

print("Creating DataLoader...")
train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True, num_workers=0)
print(f"Number of batches: {len(train_loader)}")

print("Testing first batch...")
for i, (images, labels) in enumerate(train_loader):
    print(f"Batch {i}: images shape={images.shape}, labels={labels}")
    if i >= 2:
        break

print("Dataset loading works correctly!")

