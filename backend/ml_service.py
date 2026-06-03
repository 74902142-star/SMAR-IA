"""SMAR-IA — Servicio de Machine Learning: carga, predicción y metadatos."""

import os
import logging
from datetime import datetime, timezone

import joblib
import numpy as np

from config import MODELS_DIR, NUM_FEATURES

logger = logging.getLogger("smar-ia-ml")


class MLService:
    """Abstrae la carga y predicción del modelo clasificador RandomForest."""

    def __init__(self, models_dir: str = None):
        self.models_dir = models_dir or MODELS_DIR
        self.rf_classifier = None
        self.scaler = None
        self.label_encoder = None
        self.is_loaded = False
        self._load_time = None

    def load_models(self):
        """Carga los modelos RandomForest, scaler y label_encoder desde disco."""
        try:
            logger.info("Cargando modelos ML...")
            self.rf_classifier = joblib.load(os.path.join(self.models_dir, "random_forest.pkl"))
            self.scaler = joblib.load(os.path.join(self.models_dir, "scaler.pkl"))
            self.label_encoder = joblib.load(os.path.join(self.models_dir, "label_encoder.pkl"))
            self.is_loaded = True
            self._load_time = datetime.now(timezone.utc)

            logger.info("Modelos cargados exitosamente.")
            info = self.get_model_info()
            logger.info("  → Modelo: %s", info["model_type"])
            logger.info("  → Clases: %d (%s)", info["num_classes"], ", ".join(info["classes"]))
            logger.info("  → Features esperadas: %d", info["num_features"])
        except FileNotFoundError as exc:
            logger.error("Archivo de modelo no encontrado: %s. Ejecuta ml_pipeline/train_model.py", exc)
        except (joblib.JoblibException, EOFError) as exc:
            logger.error("Error al cargar modelo corrupto: %s", exc)
        except Exception as exc:
            logger.error("Error inesperado cargando modelos: %s", exc)

    def _validate_features(self, features_array):
        """Valida que el vector tenga exactamente NUM_FEATURES características."""
        if len(features_array) != NUM_FEATURES:
            logger.warning(
                "Número de features incorrecto: esperado %d, recibido %d",
                NUM_FEATURES, len(features_array)
            )
            return False
        return True

    def predict(self, features_array):
        """Predice el tipo de ataque y confianza para un vector de 80 features."""
        if not self.is_loaded:
            return "Unknown", 0.0
        if not self._validate_features(features_array):
            return "Error", 0.0

        try:
            scaled_features = self.scaler.transform([features_array])
            prediction_encoded = self.rf_classifier.predict(scaled_features)
            probabilities = self.rf_classifier.predict_proba(scaled_features)
            predicted_class = self.label_encoder.inverse_transform(prediction_encoded)[0]
            confidence = float(np.max(probabilities))
            return predicted_class, confidence
        except ValueError as exc:
            logger.error("Error de valor en predicción: %s", exc)
            return "Error", 0.0
        except (AttributeError, TypeError) as exc:
            logger.error("Error de tipo en predicción: %s", exc)
            return "Error", 0.0

    def predict_batch(self, features_batch):
        """Predice para un lote de vectores de 80 features. Retorna lista de (clase, confianza)."""
        if not self.is_loaded:
            return [("Unknown", 0.0)] * len(features_batch)
        for feats in features_batch:
            if not self._validate_features(feats):
                return [("Error", 0.0)] * len(features_batch)

        try:
            scaled = self.scaler.transform(features_batch)
            preds_encoded = self.rf_classifier.predict(scaled)
            probs = self.rf_classifier.predict_proba(scaled)
            classes = self.label_encoder.inverse_transform(preds_encoded)
            confidences = np.max(probs, axis=1)
            return list(zip(classes, [float(c) for c in confidences]))
        except Exception as exc:
            logger.error("Error en batch prediction: %s", exc)
            return [("Error", 0.0)] * len(features_batch)

    def get_model_info(self) -> dict:
        """Retorna metadata del modelo para endpoints de salud y diagnóstico."""
        if not self.is_loaded:
            return {
                "is_loaded": False,
                "model_type": "N/A",
                "num_classes": 0,
                "classes": [],
                "num_features": NUM_FEATURES,
                "loaded_at": None,
            }
        classes = []
        try:
            classes = list(self.label_encoder.classes_)
        except (AttributeError, TypeError):
            pass
        n_estimators = 0
        try:
            n_estimators = self.rf_classifier.n_estimators
        except (AttributeError, TypeError):
            pass
        return {
            "is_loaded": True,
            "model_type": f"RandomForest (n_estimators={n_estimators})",
            "num_classes": len(classes),
            "classes": classes,
            "num_features": NUM_FEATURES,
            "loaded_at": self._load_time.isoformat() if self._load_time else None,
        }


ml_service = MLService()
