from sklearn.ensemble import RandomForestClassifier
import joblib

def create_strawberry_model(num_classes=3):
    """
    Create a lightweight Random Forest classifier for strawberry disease detection
    """
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=20,
        random_state=42,
        n_jobs=-1,
        verbose=1
    )
    return model