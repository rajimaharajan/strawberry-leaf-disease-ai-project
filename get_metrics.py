import torch
import torch.nn.functional as F
from pathlib import Path
from PIL import Image
from torchvision import transforms
from backend.model import ResNet9_SE

CLASSES = [
    "Strawberry___Leaf_scorch",
    "Strawberry___healthy",
    "powdery_mildew"
]

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = ResNet9_SE(num_classes=3).to(device)
model_path = Path("model_best.pth")
model.load_state_dict(torch.load(model_path, map_location=device))
model.eval()

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

test_root = Path("dataset/test")
overall_correct = 0
overall_total = 0
class_correct = {}
class_total = {}
predictions = []

for class_dir in sorted(test_root.iterdir()):
    if not class_dir.is_dir():
        continue
    true_class = class_dir.name
    class_correct[true_class] = 0
    class_total[true_class] = 0
    
    for img_path in sorted(class_dir.iterdir()):
        if not img_path.is_file():
            continue
        try:
            img = Image.open(img_path).convert("RGB")
            tensor = transform(img).unsqueeze(0).to(device)
            with torch.no_grad():
                outputs = model(tensor)
                probs = F.softmax(outputs, dim=1)
                conf, pred_idx = torch.max(probs, 1)
            pred_class = CLASSES[pred_idx.item()]
            confidence = conf.item() * 100
            is_correct = pred_class == true_class
            
            if is_correct:
                class_correct[true_class] += 1
                overall_correct += 1
            class_total[true_class] += 1
            overall_total += 1
            
            predictions.append({
                "file": img_path.name,
                "true": true_class,
                "predicted": pred_class,
                "confidence": round(confidence, 2),
                "correct": is_correct
            })
        except Exception as e:
            print(f"ERROR on {img_path.name}: {e}")

print("\n" + "="*60)
print("TEST SET EVALUATION RESULTS")
print("="*60)
print(f"\nOverall Test Accuracy: {overall_correct}/{overall_total} = {100*overall_correct/overall_total:.2f}%\n")

for cls in sorted(class_total.keys()):
    acc = 100 * class_correct[cls] / class_total[cls] if class_total[cls] > 0 else 0
    print(f"  {cls}: {class_correct[cls]}/{class_total[cls]} = {acc:.2f}%")

print("\n" + "="*60)
print("SAMPLE PREDICTIONS (first 20)")
print("="*60)
for p in predictions[:20]:
    status = "✓" if p["correct"] else "✗"
    print(f"  {status} {p['file']}: true={p['true']} pred={p['predicted']} ({p['confidence']}%)")

# Save full results
import json
with open("evaluation_results.json", "w") as f:
    json.dump({
        "overall_accuracy": round(100*overall_correct/overall_total, 2),
        "overall_correct": overall_correct,
        "overall_total": overall_total,
        "class_accuracy": {cls: round(100*class_correct[cls]/class_total[cls], 2) for cls in class_total},
        "predictions": predictions
    }, f, indent=2)
print("\n[OK] Full results saved to evaluation_results.json")

