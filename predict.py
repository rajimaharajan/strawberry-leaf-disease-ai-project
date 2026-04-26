import torch
import torch.nn.functional as F
import cv2
import numpy as np
from pathlib import Path
from PIL import Image
from torchvision import transforms

from backend.model import ResNet9_SE

# ------------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------------
MODEL_PATH = Path("model_best.pth")
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ImageFolder sorts alphabetically:
# 0: Strawberry___Leaf_scorch, 1: Strawberry___healthy, 2: powdery_mildew
CLASSES = [
    "Strawberry___Leaf_scorch",
    "Strawberry___healthy",
    "powdery_mildew"
]

# Load model once at module import
model = ResNet9_SE(num_classes=len(CLASSES)).to(DEVICE)
if MODEL_PATH.exists():
    model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
    model.eval()
    print(f"[OK] Loaded ResNet9+SE model from {MODEL_PATH}")
else:
    raise FileNotFoundError(f"Model not found: {MODEL_PATH}")

# ------------------------------------------------------------------
# TRANSFORMS
# ------------------------------------------------------------------
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

# ------------------------------------------------------------------
# LEAF SEGMENTATION
# ------------------------------------------------------------------
def segment_leaf(image_bgr: np.ndarray) -> np.ndarray:
    """
    Simple green-color based segmentation to isolate leaf from background.
    Returns the masked BGR image (leaf pixels kept, background black).
    """
    hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)

    # Green color range for healthy/diseased leaves
    lower_green = np.array([25, 40, 40])
    upper_green = np.array([90, 255, 255])

    # Additional brown/yellow range for diseased parts
    lower_brown = np.array([10, 50, 50])
    upper_brown = np.array([30, 255, 200])

    mask_green = cv2.inRange(hsv, lower_green, upper_green)
    mask_brown = cv2.inRange(hsv, lower_brown, upper_brown)
    mask = cv2.bitwise_or(mask_green, mask_brown)

    # Morphological cleanup
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    # Apply mask
    masked = cv2.bitwise_and(image_bgr, image_bgr, mask=mask)
    return masked

# ------------------------------------------------------------------
# GRAD-CAM VISUALIZATION
# ------------------------------------------------------------------
class GradCAM:
    def __init__(self, model, target_layer):
        self.model = model
        self.target_layer = target_layer
        self.gradients = None
        self.activations = None

        self.target_layer.register_forward_hook(self.save_activation)
        self.target_layer.register_full_backward_hook(self.save_gradient)

    def save_activation(self, module, input, output):
        self.activations = output.detach()

    def save_gradient(self, module, grad_input, grad_output):
        self.gradients = grad_output[0].detach()

    def generate(self, input_tensor, target_class=None):
        self.model.zero_grad()
        output = self.model(input_tensor)

        if target_class is None:
            target_class = output.argmax(dim=1).item()

        one_hot = torch.zeros_like(output)
        one_hot[0, target_class] = 1
        output.backward(gradient=one_hot, retain_graph=True)

        weights = self.gradients.mean(dim=(2, 3), keepdim=True)
        cam = (weights * self.activations).sum(dim=1, keepdim=True)
        cam = F.relu(cam)
        cam = F.interpolate(cam, size=(224, 224), mode='bilinear', align_corners=False)
        cam = cam.squeeze().cpu().numpy()

        # Normalize to 0-1
        cam = (cam - cam.min()) / (cam.max() - cam.min() + 1e-8)
        return cam, target_class


def apply_heatmap(original_bgr, cam, alpha=0.5):
    """Overlay Grad-CAM heatmap on original image."""
    heatmap = cv2.applyColorMap(np.uint8(255 * cam), cv2.COLORMAP_JET)
    overlay = cv2.addWeighted(original_bgr, 1 - alpha, heatmap, alpha, 0)
    return overlay


# Instantiate Grad-CAM on the last conv layer (conv4 output before classifier)
gradcam = GradCAM(model, target_layer=model.conv4[-1] if hasattr(model.conv4, '__getitem__') else model.conv4)

# ------------------------------------------------------------------
# PREDICTION FUNCTIONS (same signatures as before)
# ------------------------------------------------------------------
def preprocess_image(pil_image: Image.Image, apply_segmentation=True):
    """Preprocess PIL image for model inference."""
    # Convert to OpenCV for segmentation
    img_array = np.array(pil_image)
    img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)

    if apply_segmentation:
        img_bgr = segment_leaf(img_bgr)

    # Convert back to PIL and apply model transform
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    pil_processed = Image.fromarray(img_rgb)
    tensor = transform(pil_processed).unsqueeze(0).to(DEVICE)
    return tensor, img_bgr


def predict_image(image_path, apply_segmentation=True, save_heatmap_path=None):
    """
    Predict disease for a single image.
    Returns: (predicted_class_name, confidence_percentage)
    """
    img = Image.open(str(image_path)).convert("RGB")

    tensor, img_bgr = preprocess_image(img, apply_segmentation=apply_segmentation)

    with torch.no_grad():
        outputs = model(tensor)
        probabilities = F.softmax(outputs, dim=1)

    confidence, predicted_idx = torch.max(probabilities, 1)
    predicted_idx = predicted_idx.item()
    confidence_value = confidence.item() * 100
    result = CLASSES[predicted_idx]

    # Generate Grad-CAM heatmap
    cam, _ = gradcam.generate(tensor, target_class=predicted_idx)
    if save_heatmap_path:
        overlay = apply_heatmap(cv2.resize(img_bgr, (224, 224)), cam)
        cv2.imwrite(str(save_heatmap_path), overlay)
        print(f"[OK] Heatmap saved to {save_heatmap_path}")

    return result, confidence_value


def evaluate_test_set(test_folder="dataset/test", max_per_class=5, save_heatmaps=True):
    """
    Evaluate model on test dataset.
    Optionally saves Grad-CAM heatmaps for each tested image.
    """
    test_path = Path(test_folder)
    if not test_path.exists():
        raise FileNotFoundError(f"Test folder not found: {test_path}")

    results = {}
    for class_name in sorted(test_path.iterdir()):
        if not class_name.is_dir():
            continue

        correct = 0
        image_count = 0
        for img_file in sorted(class_name.iterdir()):
            if image_count >= max_per_class:
                break
            if not img_file.is_file():
                continue

            heatmap_path = None
            if save_heatmaps:
                heatmap_dir = Path("heatmaps") / class_name.name
                heatmap_dir.mkdir(parents=True, exist_ok=True)
                heatmap_path = heatmap_dir / f"{img_file.stem}_heatmap.jpg"

            try:
                predicted, confidence = predict_image(img_file, save_heatmap_path=heatmap_path)
            except Exception as e:
                print(f"  ERROR on {img_file.name}: {e}")
                continue

            is_correct = predicted == class_name.name
            results.setdefault(class_name.name, []).append((img_file.name, predicted, confidence, is_correct))
            if is_correct:
                correct += 1
            image_count += 1

        if image_count > 0:
            results[class_name.name].append(("accuracy", (correct / image_count) * 100, correct, image_count))
    return results


# ------------------------------------------------------------------
# CLI ENTRY POINT
# ------------------------------------------------------------------
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        image_path = Path(sys.argv[1])
        if not image_path.exists():
            print(f"Error: file not found: {image_path}")
            sys.exit(1)

        heatmap_path = image_path.with_stem(image_path.stem + "_heatmap")
        predicted_class, confidence = predict_image(image_path, save_heatmap_path=heatmap_path)
        print(f"Prediction for {image_path.name}: {predicted_class} ({confidence:.2f}%)")
        print(f"Heatmap saved to: {heatmap_path}")
    else:
        # Run full evaluation
        print("Running evaluation on dataset/test...")
        results = evaluate_test_set(max_per_class=10)

        print("\n" + "=" * 60)
        print("EVALUATION RESULTS")
        print("=" * 60)

        for class_name, items in results.items():
            print(f"\n{class_name}:")
            print("-" * 40)
            for row in items:
                if row[0] == "accuracy":
                    _, accuracy, correct, total = row
                    print(f"  Accuracy: {accuracy:.1f}% ({correct}/{total})")
                else:
                    name, predicted, confidence, is_correct = row
                    status = "✓" if is_correct else "✗"
                    print(f"  {status} {name}: {predicted} ({confidence:.2f}%)")
