"""
SMAR-IA — Evaluación del modelo ML con validación cruzada y métricas
de generalización (Punto 6 de la tesis).
"""

import os
import sys
import json
import csv
import logging
import warnings

import numpy as np
import joblib

from sklearn.base import clone
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("ml_evaluate")
warnings.filterwarnings(
    "ignore",
    message=".*sklearn.utils.parallel.delayed.*",
    category=UserWarning,
)

ATTACK_CLASSES = [
    "Normal", "DDoS SYN Flood", "DDoS UDP Flood",
    "Sniffing Pasivo", "DHCP Starvation", "DHCP Spoofing",
    "Port Scanning", "Brute Force",
]
NUM_FEATURES = 80
N_SAMPLES_PER_CLASS = 500
N_SPLITS = 10
RANDOM_STATE = 42

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "..", "..", "ml_pipeline", "models")
OUTPUT_DIR = BASE_DIR


def generate_attack_features(attack_type: str, n: int) -> np.ndarray:
    X = np.random.randn(n, NUM_FEATURES) * 0.5
    if attack_type == "DDoS SYN Flood":
        X[:, 0:10] += np.random.uniform(2.0, 4.0, (n, 10))
        X[:, 15:20] += np.random.uniform(1.5, 3.0, (n, 5))
    elif attack_type == "DDoS UDP Flood":
        X[:, 10:20] += np.random.uniform(2.5, 4.5, (n, 10))
        X[:, 25:30] += np.random.uniform(1.0, 2.5, (n, 5))
    elif attack_type == "Port Scanning":
        X[:, 20:35] += np.random.uniform(1.5, 3.5, (n, 15))
        X[:, 40:45] += np.random.uniform(1.0, 2.0, (n, 5))
    elif attack_type == "Brute Force":
        X[:, 30:40] += np.random.uniform(2.0, 5.0, (n, 10))
        X[:, 50:55] += np.random.uniform(1.0, 3.0, (n, 5))
    elif attack_type == "DHCP Starvation":
        X[:, 35:45] += np.random.uniform(2.0, 4.0, (n, 10))
        X[:, 60:65] += np.random.uniform(1.5, 3.0, (n, 5))
    elif attack_type == "DHCP Spoofing":
        X[:, 40:50] += np.random.uniform(2.0, 4.5, (n, 10))
        X[:, 70:75] += np.random.uniform(1.0, 2.5, (n, 5))
    elif attack_type == "Sniffing Pasivo":
        X[:, 45:55] += np.random.uniform(1.0, 2.0, (n, 10))
        X[:, 55:60] += np.random.uniform(0.5, 1.5, (n, 5))
    return X


def generate_dataset() -> tuple:
    X_list, y_list = [], []
    for cls in ATTACK_CLASSES:
        n = N_SAMPLES_PER_CLASS
        if cls == "Normal":
            X = np.random.randn(n, NUM_FEATURES) * 0.8
        else:
            X = generate_attack_features(cls, n)
        X_list.append(X)
        y_list.extend([cls] * n)
    X = np.vstack(X_list)
    y = np.array(y_list)
    perm = np.random.permutation(len(X))
    return X[perm], y[perm]


def load_models() -> tuple:
    rf = joblib.load(os.path.join(MODELS_DIR, "random_forest.pkl"))
    scaler = joblib.load(os.path.join(MODELS_DIR, "scaler.pkl"))
    le = joblib.load(os.path.join(MODELS_DIR, "label_encoder.pkl"))
    return rf, scaler, le


def compute_metrics(y_true_str, y_pred_str, classes):
    n_classes = len(classes)

    accuracy = accuracy_score(y_true_str, y_pred_str)
    precision = precision_score(y_true_str, y_pred_str, labels=classes, average=None, zero_division=0)
    recall = recall_score(y_true_str, y_pred_str, labels=classes, average=None, zero_division=0)
    f1 = f1_score(y_true_str, y_pred_str, labels=classes, average=None, zero_division=0)
    cm = confusion_matrix(y_true_str, y_pred_str, labels=classes)

    precision_macro = float(np.mean(precision))
    recall_macro = float(np.mean(recall))
    f1_macro = float(np.mean(f1))

    per_class = {}
    for i, cls in enumerate(classes):
        per_class[cls] = {
            "precision": round(float(precision[i]), 4),
            "recall": round(float(recall[i]), 4),
            "f1_score": round(float(f1[i]), 4),
        }

    return {
        "accuracy": round(float(accuracy), 4),
        "precision_macro": round(precision_macro, 4),
        "recall_macro": round(recall_macro, 4),
        "f1_macro": round(f1_macro, 4),
        "per_class": per_class,
        "confusion_matrix": cm.tolist(),
    }


def evaluate():
    np.random.seed(RANDOM_STATE)
    logger.info("Generando dataset de evaluación...")
    X, y_str = generate_dataset()
    logger.info("Dataset: %d muestras, %d features", X.shape[0], X.shape[1])

    logger.info("Cargando modelos desde %s...", MODELS_DIR)
    rf, _scaler, le = load_models()
    if hasattr(rf, "n_jobs"):
        rf.n_jobs = 1
    logger.info("Modelos cargados: %s", type(rf).__name__)

    y_encoded = le.transform(y_str)
    classes = list(le.classes_)

    skf = StratifiedKFold(n_splits=N_SPLITS, shuffle=True, random_state=RANDOM_STATE)
    all_y_true, all_y_pred = [], []
    fold_results = []

    for fold_idx, (train_idx, test_idx) in enumerate(skf.split(X, y_encoded)):
        X_train_fold = X[train_idx]
        X_test_fold = X[test_idx]
        y_train_fold = y_encoded[train_idx]
        y_test_fold = y_encoded[test_idx]

        fold_scaler = StandardScaler()
        X_train_fold = fold_scaler.fit_transform(X_train_fold)
        X_test_fold = fold_scaler.transform(X_test_fold)

        fold_model = clone(rf)
        fold_model.fit(X_train_fold, y_train_fold)

        y_pred_fold_enc = fold_model.predict(X_test_fold)
        y_true_fold = le.inverse_transform(y_test_fold)
        y_pred_fold = le.inverse_transform(y_pred_fold_enc)

        all_y_true.extend(y_true_fold)
        all_y_pred.extend(y_pred_fold)

        metrics = compute_metrics(y_true_fold, y_pred_fold, classes)
        fold_results.append(metrics)
        logger.info(
            "Fold %d/%d — Acc: %.4f, F1: %.4f",
            fold_idx + 1, N_SPLITS,
            metrics["accuracy"], metrics["f1_macro"],
        )

    overall = compute_metrics(np.array(all_y_true), np.array(all_y_pred), classes)
    fold_summary = {
        "accuracy_mean": round(float(np.mean([m["accuracy"] for m in fold_results])), 4),
        "accuracy_std": round(float(np.std([m["accuracy"] for m in fold_results])), 4),
        "f1_macro_mean": round(float(np.mean([m["f1_macro"] for m in fold_results])), 4),
        "f1_macro_std": round(float(np.std([m["f1_macro"] for m in fold_results])), 4),
    }

    report = classification_report(
        np.array(all_y_true), np.array(all_y_pred),
        labels=classes, zero_division=0, output_dict=True,
    )

    results = {
        "experiment": "Validación Cruzada SMAR-IA (10-Fold)",
        "n_samples": len(y_str),
        "n_splits": N_SPLITS,
        "n_features": NUM_FEATURES,
        "model_type": type(rf).__name__,
        "class_names": classes,
        "fold_summary": fold_summary,
        "fold_results": [
            {"fold": i + 1, **m} for i, m in enumerate(fold_results)
        ],
        "overall": overall,
        "classification_report": report,
    }

    json_path = os.path.join(OUTPUT_DIR, "ml_evaluation_results.json")
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2)
    logger.info("Resultados guardados en %s", json_path)

    csv_path = os.path.join(OUTPUT_DIR, "ml_evaluation_results.csv")
    with open(csv_path, "w", newline="") as f:
        fieldnames = ["class", "precision", "recall", "f1_score"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for cls in classes:
            row = {"class": cls}
            row.update(overall["per_class"].get(cls, {}))
            writer.writerow(row)
        writer.writerow({})
        writer.writerow({"class": "MACRO_AVG"})
        writer.writerow({
            "class": "overall",
            "precision": overall["precision_macro"],
            "recall": overall["recall_macro"],
            "f1_score": overall["f1_macro"],
        })
    logger.info("Resultados guardados en %s", csv_path)

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import seaborn as sns

        fig, axes = plt.subplots(1, 2, figsize=(18, 7))

        cm = np.array(overall["confusion_matrix"])
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                    xticklabels=classes, yticklabels=classes, ax=axes[0])
        axes[0].set_title("Matriz de Confusión — Validación Cruzada (10-Fold)")
        axes[0].set_xlabel("Predicción")
        axes[0].set_ylabel("Real")

        metrics_df = {
            cls: overall["per_class"][cls] for cls in classes
        }
        x_pos = np.arange(len(classes))
        width = 0.25
        for i, metric in enumerate(["precision", "recall", "f1_score"]):
            values = [metrics_df[cls][metric] for cls in classes]
            axes[1].bar(x_pos + i * width, values, width, label=metric.capitalize())
        axes[1].set_xticks(x_pos + width)
        axes[1].set_xticklabels(classes, rotation=45, ha="right")
        axes[1].set_ylabel("Puntaje")
        axes[1].set_title("Métricas por Clase — Validación Cruzada (10-Fold)")
        axes[1].legend()
        axes[1].set_ylim(0, 1.1)

        plt.tight_layout()
        png_path = os.path.join(OUTPUT_DIR, "ml_evaluation_confusion.png")
        plt.savefig(png_path, dpi=150)
        plt.close()
        logger.info("Gráfico guardado en %s", png_path)
    except ImportError as e:
        logger.warning("No se pudo generar gráfico: %s", e)

    logger.info("")
    logger.info("=" * 60)
    logger.info("RESULTADOS GLOBALES — Validación Cruzada %d-Fold", N_SPLITS)
    logger.info("=" * 60)
    logger.info("  Accuracy:       %.4f", overall["accuracy"])
    logger.info("  Precision (macro): %.4f", overall["precision_macro"])
    logger.info("  Recall (macro):    %.4f", overall["recall_macro"])
    logger.info("  F1-Score (macro):  %.4f", overall["f1_macro"])
    logger.info("  F1 Macro CV:       %.4f ± %.4f", fold_summary["f1_macro_mean"], fold_summary["f1_macro_std"])
    logger.info("=" * 60)

    return results


if __name__ == "__main__":
    evaluate()
