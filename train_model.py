"""
Script for creating a simple trained ML model
Used for demonstrating the gRPC service
"""

import pickle
import os
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

def create_model():
    """Create and train model"""
    print("Loading Iris dataset...")
    iris = load_iris()
    X, y = iris.data, iris.target
    
    print("Splitting data into train/test...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print("Training RandomForest model...")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate model
    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)
    
    print(f"Train accuracy: {train_score:.4f}")
    print(f"Test accuracy: {test_score:.4f}")
    
    return model

def save_model(model, path='models/model.pkl'):
    """Save model"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    with open(path, 'wb') as f:
        pickle.dump(model, f)
    
    print(f"Model successfully saved to {path}")
    print(f"File size: {os.path.getsize(path)} bytes")

if __name__ == '__main__':
    model = create_model()
    save_model(model)
    
    print("\nTesting model loading...")
    with open('models/model.pkl', 'rb') as f:
        loaded_model = pickle.load(f)
    
    # Test prediction
    test_features = [[5.1, 3.5, 1.4, 0.2]]
    prediction = loaded_model.predict(test_features)[0]
    probabilities = loaded_model.predict_proba(test_features)[0]
    
    print(f"Test prediction: {prediction}")
    print(f"Class probabilities: {probabilities}")
    print("\nModel is ready for use!")