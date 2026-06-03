import os
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix

try:
    from xgboost import XGBClassifier
    XGB_AVAILABLE = True
except ImportError:
    XGB_AVAILABLE = False
    print("XGBoost no instalado. Ejecute: pip install xgboost")

ATTACK_CLASSES = [
    'Normal', 'DDoS SYN Flood', 'DDoS UDP Flood',
    'Sniffing Pasivo', 'DHCP Starvation', 'DHCP Spoofing',
    'Port Scanning', 'Brute Force'
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


def generate_dataset():
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


def evaluate(y_true, y_pred, model_name):
    acc = accuracy_score(y_true, y_pred)
    p, r, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='weighted', zero_division=0)
    cm = confusion_matrix(y_true, y_pred)
    tn = cm[0][0] if cm.shape[0] > 1 and cm.shape[1] > 1 else 0
    fp = cm[0][1:].sum() if cm.shape[0] > 1 else 0
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
    print(f"\n{'='*50}")
    print(f"  {model_name}")
    print(f"{'='*50}")
    print(f"  Accuracy:  {acc:.4f}")
    print(f"  Precision: {p:.4f}")
    print(f"  Recall:    {r:.4f}")
    print(f"  F1-Score:  {p:.4f}")
    print(f"  FPR:       {fpr:.4f} ({fpr*100:.2f}%)")
    print(f"  {'SLA ≥98%: ✅' if acc >= 0.98 else 'SLA ≥98%: ❌'}")
    print(f"  {'FPR ≤2%:  ✅' if fpr <= 0.02 else 'FPR ≤2%:  ❌'}")
    return {'accuracy': acc, 'precision': p, 'recall': r, 'f1': f1, 'fpr': fpr}


def main():
    os.makedirs('models', exist_ok=True)
    X, y = generate_dataset()
    print(f"Dataset: {X.shape[0]} muestras, {X.shape[1]} features")

    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y_encoded, test_size=0.2, random_state=42
    )

    results = []

    # Random Forest
    print("\nEntrenando Random Forest...")
    rf = RandomForestClassifier(
        n_estimators=150, max_depth=20,
        class_weight='balanced', random_state=42, n_jobs=-1
    )
    rf.fit(X_train, y_train)
    rf_preds = rf.predict(X_test)
    joblib.dump(rf, 'models/random_forest.pkl')
    results.append(('Random Forest', evaluate(y_test, rf_preds, 'Random Forest')))

    # XGBoost
    if XGB_AVAILABLE:
        print("\nEntrenando XGBoost...")
        xgb = XGBClassifier(
            n_estimators=150, max_depth=8,
            learning_rate=0.1, subsample=0.8,
            colsample_bytree=0.8, random_state=42,
            use_label_encoder=False, eval_metric='mlogloss',
            n_jobs=-1
        )
        xgb.fit(X_train, y_train)
        xgb_preds = xgb.predict(X_test)
        joblib.dump(xgb, 'models/xgboost.pkl')
        results.append(('XGBoost', evaluate(y_test, xgb_preds, 'XGBoost')))
    else:
        print("\n⚠️ XGBoost no disponible — entrenando solo Random Forest")

    # Guardar scaler y label encoder (compartidos)
    joblib.dump(scaler, 'models/scaler.pkl')
    joblib.dump(le, 'models/label_encoder.pkl')

    print(f"\n{'='*50}")
    print("  COMPARATIVA DE MODELOS")
    print(f"{'='*50}")
    print(f"  {'Modelo':<20} {'Acc':>6} {'Prec':>6} {'Rec':>6} {'F1':>6} {'FPR':>6}")
    print(f"  {'-'*50}")
    for name, metrics in results:
        print(f"  {name:<20} {metrics['accuracy']:.4f} {metrics['precision']:.4f} {metrics['recall']:.4f} {metrics['f1']:.4f} {metrics['fpr']:.4f}")

    print("\n✅ Modelos guardados en ml_pipeline/models/")
    return results


if __name__ == "__main__":
    main()
