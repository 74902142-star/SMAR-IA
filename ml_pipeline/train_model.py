import os
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
import joblib

ATTACK_CLASSES = [
    'Normal',
    'DDoS SYN Flood',
    'DDoS UDP Flood',
    'Sniffing Pasivo',
    'DHCP Starvation',
    'DHCP Spoofing',
    'Port Scanning',
    'Brute Force'
]

NUM_FEATURES = 80
NUM_SAMPLES = 10000
np.random.seed(42)

def generate_attack_features(attack_type: str, n: int) -> np.ndarray:
    X = np.random.randn(n, NUM_FEATURES) * 0.5
    if attack_type == 'DDoS SYN Flood':
        X[:, 0:10] += np.random.uniform(2.0, 4.0, (n, 10))
        X[:, 15:20] += np.random.uniform(1.5, 3.0, (n, 5))
    elif attack_type == 'DDoS UDP Flood':
        X[:, 10:20] += np.random.uniform(2.5, 4.5, (n, 10))
        X[:, 25:30] += np.random.uniform(1.0, 2.5, (n, 5))
    elif attack_type == 'Port Scanning':
        X[:, 20:35] += np.random.uniform(1.5, 3.5, (n, 15))
        X[:, 40:45] += np.random.uniform(1.0, 2.0, (n, 5))
    elif attack_type == 'Brute Force':
        X[:, 30:40] += np.random.uniform(2.0, 5.0, (n, 10))
        X[:, 50:55] += np.random.uniform(1.0, 3.0, (n, 5))
    elif attack_type == 'DHCP Starvation':
        X[:, 35:45] += np.random.uniform(2.0, 4.0, (n, 10))
        X[:, 60:65] += np.random.uniform(1.5, 3.0, (n, 5))
    elif attack_type == 'DHCP Spoofing':
        X[:, 40:50] += np.random.uniform(2.0, 4.5, (n, 10))
        X[:, 70:75] += np.random.uniform(1.0, 2.5, (n, 5))
    elif attack_type == 'Sniffing Pasivo':
        X[:, 45:55] += np.random.uniform(1.0, 2.0, (n, 10))
        X[:, 55:60] += np.random.uniform(0.5, 1.5, (n, 5))
    return X

def generate_mock_data():
    print("Generando dataset con patrones de ataque...")
    n_per_class = NUM_SAMPLES // len(ATTACK_CLASSES)
    X_list, y_list = [], []

    for cls in ATTACK_CLASSES:
        n = n_per_class
        if cls == 'Normal':
            X = np.random.randn(n, NUM_FEATURES) * 0.8
        else:
            X = generate_attack_features(cls, n)
        X_list.append(X)
        y_list.extend([cls] * n)

    X = np.vstack(X_list)
    y = np.array(y_list)

    perm = np.random.permutation(len(X))
    return X[perm], y[perm]

def train_pipeline():
    os.makedirs('models', exist_ok=True)
    X, y = generate_mock_data()
    print(f"Dataset: {X.shape[0]} muestras, {X.shape[1]} features")

    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y_encoded, test_size=0.2, random_state=42
    )

    print("Entrenando Random Forest...")
    rf_clf = RandomForestClassifier(
        n_estimators=150, max_depth=20,
        class_weight='balanced', random_state=42,
        n_jobs=-1
    )
    rf_clf.fit(X_train, y_train)

    train_acc = rf_clf.score(X_train, y_train)
    test_acc = rf_clf.score(X_test, y_test)
    print(f"Precisión entrenamiento: {train_acc:.4f}")
    print(f"Precisión prueba: {test_acc:.4f}")

    print("Guardando modelos...")
    joblib.dump(rf_clf, 'models/random_forest.pkl')
    joblib.dump(scaler, 'models/scaler.pkl')
    joblib.dump(le, 'models/label_encoder.pkl')

    # Validación rápida
    test_samples = np.random.randn(10, NUM_FEATURES) * 0.8
    preds = le.inverse_transform(rf_clf.predict(scaler.transform(test_samples)))
    print(f"Muestras normales → {np.unique(preds)}")

    attack_samples = generate_attack_features('DDoS SYN Flood', 5)
    preds = le.inverse_transform(rf_clf.predict(scaler.transform(attack_samples)))
    print(f"DDoS SYN Flood → {np.unique(preds)}")

    attack_samples = generate_attack_features('Brute Force', 5)
    preds = le.inverse_transform(rf_clf.predict(scaler.transform(attack_samples)))
    print(f"Brute Force → {np.unique(preds)}")

    print("¡Entrenamiento completado!")

if __name__ == "__main__":
    train_pipeline()
