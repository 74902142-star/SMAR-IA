"""
SMAR-IA — Servicio de Machine Learning
Abstrae la carga, predicción y metadatos del modelo clasificador.
"""
import os
import joblib
import numpy as np
from config import MODELS_DIR, NUM_FEATURES

class MLService:
    def __init__(self, models_dir=None):
        self.models_dir = models_dir or MODELS_DIR
        self.rf_classifier = None
        self.scaler = None
        self.label_encoder = None
        self.is_loaded = False
        self._load_time = None

    def load_models(self):
        try:
            print("Cargando modelos ML...")
            # En esta demostración omitimos CNN-BiLSTM por compatibilidad con Python 3.14
            self.rf_classifier = joblib.load(os.path.join(self.models_dir, "random_forest.pkl"))
            self.scaler = joblib.load(os.path.join(self.models_dir, "scaler.pkl"))
            self.label_encoder = joblib.load(os.path.join(self.models_dir, "label_encoder.pkl"))
            self.is_loaded = True

            from datetime import datetime, timezone
            self._load_time = datetime.now(timezone.utc)

            print("Modelos cargados exitosamente.")
            info = self.get_model_info()
            print(f"  → Modelo: {info['model_type']}")
            print(f"  → Clases: {info['num_classes']} ({', '.join(info['classes'])})")
            print(f"  → Features esperadas: {info['num_features']}")
        except Exception as e:
            print(f"Error cargando modelos: {e}. Ejecuta ml_pipeline/train_model.py")

    def predict(self, features_array):
        if not self.is_loaded:
            return "Unknown", 0.0
        
        try:
            scaled_features = self.scaler.transform([features_array])
            
            prediction_encoded = self.rf_classifier.predict(scaled_features)
            probabilities = self.rf_classifier.predict_proba(scaled_features)
            
            predicted_class = self.label_encoder.inverse_transform(prediction_encoded)[0]
            confidence = float(np.max(probabilities))
            
            return predicted_class, confidence
        except Exception as e:
            print(f"Error en predicción: {e}")
            return "Error", 0.0

    def get_model_info(self):
        """
        Retorna metadata del modelo para endpoints de salud y diagnóstico.
        """
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
        num_classes = 0
        try:
            classes = list(self.label_encoder.classes_)
            num_classes = len(classes)
        except Exception:
            pass

        n_estimators = 0
        try:
            n_estimators = self.rf_classifier.n_estimators
        except Exception:
            pass

        return {
            "is_loaded": True,
            "model_type": f"RandomForest (n_estimators={n_estimators})",
            "num_classes": num_classes,
            "classes": classes,
            "num_features": NUM_FEATURES,
            "loaded_at": self._load_time.isoformat() if self._load_time else None,
        }

ml_service = MLService()
