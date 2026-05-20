import os
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
import joblib

# Definir clases de ataque
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
NUM_SAMPLES = 5000  # Pequeño dataset simulado para no sobrecargar la PC

def generate_mock_data(num_samples=NUM_SAMPLES, num_features=NUM_FEATURES):
    print("Generando dataset simulado...")
    np.random.seed(42)
    X = np.random.randn(num_samples, num_features)
    y_indices = np.random.choice(len(ATTACK_CLASSES), num_samples, p=[0.5, 0.1, 0.05, 0.05, 0.05, 0.05, 0.1, 0.1])
    y = [ATTACK_CLASSES[i] for i in y_indices]
    return X, np.array(y)

def train_pipeline():
    os.makedirs('models', exist_ok=True)
    
    X, y = generate_mock_data()
    
    print("Preprocesando datos...")
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y_encoded, test_size=0.2, random_state=42
    )
    
    # Entrenar Random Forest
    print("Entrenando Random Forest...")
    # Nota: Arquitectura CNN-BiLSTM requeriría TensorFlow (no soportado en Py 3.14 actualmente). 
    # Usamos RF directo para demostración funcional.
    rf_clf = RandomForestClassifier(n_estimators=100, max_depth=None, class_weight='balanced', random_state=42)
    rf_clf.fit(X_train, y_train)
    
    print(f"Precisión de RF en entrenamiento: {rf_clf.score(X_train, y_train):.4f}")
    print(f"Precisión de RF en prueba: {rf_clf.score(X_test, y_test):.4f}")
    
    print("Guardando modelos...")
    joblib.dump(rf_clf, 'models/random_forest.pkl')
    joblib.dump(scaler, 'models/scaler.pkl')
    joblib.dump(le, 'models/label_encoder.pkl')
    
    print("¡Entrenamiento y exportación completados!")

if __name__ == "__main__":
    train_pipeline()
