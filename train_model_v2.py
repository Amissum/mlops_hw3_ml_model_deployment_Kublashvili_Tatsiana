# create_model_v2.py
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import pickle
import os

def create_model_v2():
    print("Loading Iris dataset for v2...")
    iris = load_iris()
    X, y = iris.data, iris.target
    
    print("Splitting data into train/test...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Улучшенная модель с большим числом деревьев
    print("Training RandomForest v2 model (200 estimators)...")
    model = RandomForestClassifier(n_estimators=200, random_state=42, max_depth=5)
    model.fit(X_train, y_train)
    
    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)
    print(f"Train accuracy: {train_score:.4f}")
    print(f"Test accuracy: {test_score:.4f}")
    
    return model

def save_model(model, path='models/model_v2.pkl'):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as f:
        pickle.dump(model, f)
    print(f"Model v2 successfully saved to {path}")
    print(f"File size: {os.path.getsize(path)} bytes")

if __name__ == '__main__':
    model = create_model_v2()
    save_model(model)
    
    print("\nTesting model v2 loading...")
    with open('models/model_v2.pkl', 'rb') as f:
        loaded_model = pickle.load(f)
    
    test_features = [[5.1, 3.5, 1.4, 0.2]]
    prediction = loaded_model.predict(test_features)[0]
    probabilities = loaded_model.predict_proba(test_features)[0]
    
    print(f"Test prediction: {prediction}")
    print(f"Class probabilities: {probabilities}")
    print("\nModel v2 is ready for use!")