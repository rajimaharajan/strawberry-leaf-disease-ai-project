import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image
import os
import glob
from model import ResNet9_SE

# Class mapping: folder name -> class index
CLASS_MAP = {
    "Strawberry___Leaf_scorch": 0,
    "Strawberry___healthy": 1,
    "powdery_mildew": 2,
}

CLASS_NAMES = ["Leaf Scorch", "Healthy", "Powdery Mildew"]

class StrawberryDataset(Dataset):
    def __init__(self, root_dir, transform=None):
        self.root_dir = root_dir
        self.transform = transform
        self.samples = []
        
        for folder_name, class_idx in CLASS_MAP.items():
            folder_path = os.path.join(root_dir, folder_name)
            if not os.path.exists(folder_path):
                continue
            for ext in ['*.jpg', '*.jpeg', '*.png', '*.webp', '*.JPG', '*.JPEG', '*.PNG', '*.WEBP']:
                for img_path in glob.glob(os.path.join(folder_path, ext)):
                    self.samples.append((img_path, class_idx))
        
        print(f"Loaded {len(self.samples)} images from {root_dir}")
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        img_path, label = self.samples[idx]
        image = Image.open(img_path).convert("RGB")
        if self.transform:
            image = self.transform(image)
        return image, label

def train_model():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    # Transforms
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
    
    # Datasets
    train_dataset = StrawberryDataset("../dataset/train", transform=train_transform)
    test_dataset = StrawberryDataset("../dataset/test", transform=test_transform)
    
    if len(train_dataset) == 0:
        print("ERROR: No training images found!")
        return
    
    train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True, num_workers=0)
    test_loader = DataLoader(test_dataset, batch_size=16, shuffle=False, num_workers=0)
    
    # Model
    model = ResNet9_SE(num_classes=3).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    # Training
    epochs = 10
    best_acc = 0.0
    
    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0
        
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
        
        train_acc = 100 * correct / total
        
        # Validation
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
        
        test_acc = 100 * test_correct / test_total if test_total > 0 else 0
        
        print(f"Epoch [{epoch+1}/{epochs}] Loss: {running_loss/len(train_loader):.4f} | Train Acc: {train_acc:.2f}% | Test Acc: {test_acc:.2f}%")
        
        if test_acc > best_acc:
            best_acc = test_acc
            torch.save(model.state_dict(), "../model.pth")
            print(f"  -> Saved best model (Test Acc: {best_acc:.2f}%)")
    
    print(f"\nTraining complete! Best test accuracy: {best_acc:.2f}%")
    print(f"Model saved to ../model.pth")

if __name__ == "__main__":
    train_model()

