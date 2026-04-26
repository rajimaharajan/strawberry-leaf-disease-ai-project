import torch
from pathlib import Path
from PIL import Image
from torchvision import transforms
from backend.model import ResNet9_SE

# Class mapping (ImageFolder alphabetical order)
CLASSES = [
    "Strawberry___Leaf_scorch",
    "Strawberry___healthy",
    "powdery_mildew"
]

# Load model
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = ResNet9_SE(num_classes=3).to(device)
model_path = Path("model_best.pth")
if not model_path.exists():
    print(f"Model not found: {model_path}")
    exit(1)

model.load_state_dict(torch.load(model_path, map_location=device))
model.eval()
print(f"Model loaded on {device}")

# Transform
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

# Test on sample images from each class
test_dirs = {
    "Strawberry___healthy": Path("dataset/test/Strawberry___healthy"),
    "Strawberry___Leaf_scorch": Path("dataset/test/Strawberry___Leaf_scorch"),
    "powdery_mildew": Path("dataset/test/powdery_mildew")
}

for true_class, dir_path in test_dirs.items():
    if not dir_path.exists():
        print(f"Directory not found: {dir_path}")
        continue
    
    images = list(dir_path.iterdir())[:3]  # Test first 3 images
    correct = 0
    print(f"\n{'='*60}")
    print(f"Testing {true_class}:")
    print(f"{'='*60}")
    
    for img_path in images:
        if not img_path.is_file():
            continue
        try:
            img = Image.open(img_path).convert("RGB")
            tensor = transform(img).unsqueeze(0).to(device)
            
            with torch.no_grad():
                outputs = model(tensor)
                probs = torch.nn.functional.softmax(outputs, dim=1)
                conf, pred_idx = torch.max(probs, 1)
            
            pred_class = CLASSES[pred_idx.item()]
            confidence = conf.item() * 100
            status = "✓" if pred_class == true_class else "✗"
            print(f"  {status} {img_path.name}: {pred_class} ({confidence:.2f}%)")
            if pred_class == true_class:
                correct += 1
        except Exception as e:
            print(f"  ERROR on {img_path.name}: {e}")
    
    print(f"  Accuracy: {correct}/{len(images)} ({100*correct/len(images):.0f}%)")

