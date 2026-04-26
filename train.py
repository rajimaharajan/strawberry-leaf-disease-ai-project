import cv2
import os
import numpy as np
from sklearn.preprocessing import LabelEncoder
import joblib
import sys
from model import create_strawberry_model

print("Starting lightweight training...", flush=True)

# Paths
train_path = "dataset/train"
classes = ["powdery_mildew", "Strawberry___Leaf_scorch", "Strawberry___healthy"]

# Extract features from images
X = []
y = []

print("Loading and processing images...", flush=True)
for class_idx, class_name in enumerate(classes):
    class_path = os.path.join(train_path, class_name)
    if not os.path.exists(class_path):
        print(f"Warning: {class_path} not found", flush=True)
        continue
    
    image_count = 0
    for img_name in os.listdir(class_path):
        img_path = os.path.join(class_path, img_name)
        if not os.path.isfile(img_path):
            continue
        
        try:
            # Read and resize image
            img = cv2.imread(img_path)
            if img is None:
                continue
            
            img = cv2.resize(img, (64, 64))
            
            # Extract simple histogram features
            hist_b = cv2.calcHist([img], [0], None, [32], [0, 256])
            hist_g = cv2.calcHist([img], [1], None, [32], [0, 256])
            hist_r = cv2.calcHist([img], [2], None, [32], [0, 256])
            
            # Flatten and combine features
            features = np.concatenate([hist_b.flatten(), hist_g.flatten(), hist_r.flatten()])
            
            X.append(features)
            y.append(class_idx)
            image_count += 1
            
            if image_count % 10 == 0:
                print(f"  Processed {image_count} images from {class_name}", flush=True)
        
        except Exception as e:
            print(f"  Error processing {img_path}: {e}", flush=True)
            continue
    
    print(f"Total images loaded from {class_name}: {image_count}", flush=True)

X = np.array(X)
y = np.array(y)

print(f"\nDataset shape: {X.shape}", flush=True)
print(f"Classes: {classes}", flush=True)

if X.shape[0] == 0:
    print("ERROR: No images found! Make sure images are in dataset/train/", flush=True)
    sys.exit(1)

print("\nCreating and training model...", flush=True)
model = create_strawberry_model()

print("Fitting model...", flush=True)
model.fit(X, y)

print("Saving model...", flush=True)
joblib.dump(model, "model_strawberry.pkl")
joblib.dump(classes, "classes.pkl")

print("Model saved successfully ✅", flush=True)
print(f"Training complete! Model saved to model_strawberry.pkl")