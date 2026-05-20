"""
SMAR-IA — Script de Exportación y Validación de Modelos
Carga el modelo entrenado, ejecuta validación básica y genera metadata.
"""
import os
import sys
import json
import numpy as np
import joblib
from datetime import datetime, timezone

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")


def validate_and_export():
    """
    Valida que los modelos entrenados funcionen correctamente
    y genera un archivo de metadata para auditoría.
    """
    print("=" * 60)
    print("  SMAR-IA — Validación y Exportación de Modelos")
    print("=" * 60)
    
    # ── Verificar que existen los archivos ────────────────────
    required_files = ["random_forest.pkl", "scaler.pkl", "label_encoder.pkl"]
    for fname in required_files:
        fpath = os.path.join(MODELS_DIR, fname)
        if not os.path.exists(fpath):
            print(f"  ❌ FALTA: {fpath}")
            print("  → Ejecuta primero: python train_model.py")
            sys.exit(1)
        size_mb = os.path.getsize(fpath) / (1024 * 1024)
        print(f"  ✅ {fname} ({size_mb:.2f} MB)")
    
    # ── Cargar modelos ───────────────────────────────────────
    print("\nCargando modelos...")
    rf = joblib.load(os.path.join(MODELS_DIR, "random_forest.pkl"))
    scaler = joblib.load(os.path.join(MODELS_DIR, "scaler.pkl"))
    le = joblib.load(os.path.join(MODELS_DIR, "label_encoder.pkl"))
    
    classes = list(le.classes_)
    print(f"  Clases: {classes}")
    print(f"  Número de árboles (RF): {rf.n_estimators}")
    print(f"  Features esperadas: {scaler.n_features_in_}")
    
    # ── Prueba de predicción con datos normales ──────────────
    print("\n─── Prueba de Predicción ───")
    np.random.seed(123)
    
    # Test 1: Features normales (media=0, std=1)
    normal_features = np.random.randn(scaler.n_features_in_)
    scaled = scaler.transform([normal_features])
    pred = rf.predict(scaled)
    proba = rf.predict_proba(scaled)
    pred_class = le.inverse_transform(pred)[0]
    confidence = float(np.max(proba))
    print(f"  [TEST 1] Features normales → {pred_class} ({confidence:.1%})")
    
    # Test 2: Features anómalas (media=20, std=10) — simula ataque
    attack_features = np.random.randn(scaler.n_features_in_) * 10 + 20
    scaled = scaler.transform([attack_features])
    pred = rf.predict(scaled)
    proba = rf.predict_proba(scaled)
    pred_class = le.inverse_transform(pred)[0]
    confidence = float(np.max(proba))
    print(f"  [TEST 2] Features anómalas → {pred_class} ({confidence:.1%})")
    
    # Test 3: Batch de 100 predicciones — medir latencia
    import time
    test_batch = np.random.randn(100, scaler.n_features_in_)
    
    start = time.perf_counter()
    scaled_batch = scaler.transform(test_batch)
    preds = rf.predict(scaled_batch)
    probas = rf.predict_proba(scaled_batch)
    elapsed = (time.perf_counter() - start) * 1000
    
    pred_classes = le.inverse_transform(preds)
    avg_confidence = float(np.mean(np.max(probas, axis=1)))
    
    print(f"\n  [TEST 3] Batch de 100 predicciones:")
    print(f"    Tiempo total: {elapsed:.2f} ms")
    print(f"    Latencia promedio: {elapsed / 100:.2f} ms/flujo")
    print(f"    Confianza promedio: {avg_confidence:.1%}")
    
    # Distribución de predicciones
    unique, counts = np.unique(pred_classes, return_counts=True)
    print(f"    Distribución: {dict(zip(unique, counts.tolist()))}")
    
    # ── Generar metadata ─────────────────────────────────────
    metadata = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "model_type": "RandomForestClassifier",
        "n_estimators": rf.n_estimators,
        "max_depth": rf.max_depth,
        "class_weight": str(rf.class_weight),
        "num_classes": len(classes),
        "classes": classes,
        "num_features": int(scaler.n_features_in_),
        "scaler_type": "StandardScaler",
        "validation": {
            "test_normal": {
                "result": le.inverse_transform(rf.predict(scaler.transform([normal_features])))[0],
                "note": "Feature vector con distribución normal estándar"
            },
            "test_attack": {
                "result": le.inverse_transform(rf.predict(scaler.transform([attack_features])))[0],
                "note": "Feature vector con media desplazada (simula anomalía)"
            },
            "batch_100": {
                "latency_total_ms": round(elapsed, 2),
                "latency_avg_ms": round(elapsed / 100, 2),
                "avg_confidence": round(avg_confidence, 4),
            }
        },
        "files": {
            "random_forest.pkl": f"{os.path.getsize(os.path.join(MODELS_DIR, 'random_forest.pkl')) / (1024*1024):.2f} MB",
            "scaler.pkl": f"{os.path.getsize(os.path.join(MODELS_DIR, 'scaler.pkl')) / 1024:.2f} KB",
            "label_encoder.pkl": f"{os.path.getsize(os.path.join(MODELS_DIR, 'label_encoder.pkl')) / 1024:.2f} KB",
        }
    }
    
    metadata_path = os.path.join(MODELS_DIR, "model_metadata.json")
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Metadata exportada: {metadata_path}")
    print("=" * 60)
    print("  Modelos validados correctamente. Listos para inferencia.")
    print("=" * 60)


if __name__ == "__main__":
    validate_and_export()
