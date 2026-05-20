"""
SMAR-IA — Pipeline de Preprocesamiento
Clase reutilizable para normalización, transformación y selección de features.
"""
import numpy as np
import joblib
import os
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer


class PreprocessingPipeline:
    """
    Pipeline de preprocesamiento para features de tráfico de red.
    
    Pasos aplicados:
    1. Imputación de valores faltantes (media)
    2. Log-transform de features con alta asimetría
    3. Normalización (StandardScaler: media=0, std=1)
    
    Uso:
        # Entrenamiento
        pipeline = PreprocessingPipeline()
        X_processed = pipeline.fit_transform(X_raw)
        pipeline.save("models/")
        
        # Inferencia
        pipeline = PreprocessingPipeline.load("models/")
        X_processed = pipeline.transform(X_new)
    """
    
    def __init__(self, log_transform_threshold=2.0):
        self.scaler = StandardScaler()
        self.imputer = SimpleImputer(strategy='mean')
        self.log_transform_threshold = log_transform_threshold
        self._log_transform_cols = []
        self._is_fitted = False
    
    def _detect_skewed_columns(self, X):
        """Detecta columnas con alta asimetría para aplicar log-transform."""
        skewed = []
        for col_idx in range(X.shape[1]):
            col = X[:, col_idx]
            col_clean = col[~np.isnan(col)]
            if len(col_clean) > 0 and col_clean.min() >= 0:
                # Calcular skewness manualmente
                mean = np.mean(col_clean)
                std = np.std(col_clean)
                if std > 0:
                    skewness = np.mean(((col_clean - mean) / std) ** 3)
                    if abs(skewness) > self.log_transform_threshold:
                        skewed.append(col_idx)
        return skewed
    
    def _apply_log_transform(self, X, columns):
        """Aplica log(1+x) a las columnas especificadas."""
        X_transformed = X.copy()
        for col_idx in columns:
            col = X_transformed[:, col_idx]
            # Solo aplicar a valores no negativos
            mask = col >= 0
            X_transformed[mask, col_idx] = np.log1p(col[mask])
        return X_transformed
    
    def fit_transform(self, X):
        """
        Ajusta el pipeline al dataset y transforma los datos.
        
        Args:
            X: numpy array de shape (n_samples, n_features)
        
        Returns:
            X_processed: numpy array transformado
        """
        X = np.array(X, dtype=np.float64)
        
        # Paso 1: Imputación de valores faltantes
        X = self.imputer.fit_transform(X)
        
        # Paso 2: Detectar y aplicar log-transform
        self._log_transform_cols = self._detect_skewed_columns(X)
        if self._log_transform_cols:
            X = self._apply_log_transform(X, self._log_transform_cols)
        
        # Paso 3: Normalización StandardScaler
        X = self.scaler.fit_transform(X)
        
        self._is_fitted = True
        return X
    
    def transform(self, X):
        """
        Transforma nuevos datos usando el pipeline ya ajustado.
        
        Args:
            X: numpy array de shape (n_samples, n_features)
        
        Returns:
            X_processed: numpy array transformado
        """
        if not self._is_fitted:
            raise RuntimeError("Pipeline no ajustado. Llama fit_transform() primero.")
        
        X = np.array(X, dtype=np.float64)
        
        # Paso 1: Imputación
        X = self.imputer.transform(X)
        
        # Paso 2: Log-transform (mismas columnas que en fit)
        if self._log_transform_cols:
            X = self._apply_log_transform(X, self._log_transform_cols)
        
        # Paso 3: Normalización
        X = self.scaler.transform(X)
        
        return X
    
    def save(self, output_dir):
        """Guarda el pipeline completo en disco."""
        os.makedirs(output_dir, exist_ok=True)
        
        pipeline_data = {
            "scaler": self.scaler,
            "imputer": self.imputer,
            "log_transform_cols": self._log_transform_cols,
            "log_transform_threshold": self.log_transform_threshold,
            "is_fitted": self._is_fitted,
        }
        
        filepath = os.path.join(output_dir, "preprocessing_pipeline.pkl")
        joblib.dump(pipeline_data, filepath)
        print(f"[PIPELINE] Guardado en {filepath}")
        return filepath
    
    @classmethod
    def load(cls, models_dir):
        """Carga un pipeline previamente guardado."""
        filepath = os.path.join(models_dir, "preprocessing_pipeline.pkl")
        data = joblib.load(filepath)
        
        pipeline = cls(log_transform_threshold=data["log_transform_threshold"])
        pipeline.scaler = data["scaler"]
        pipeline.imputer = data["imputer"]
        pipeline._log_transform_cols = data["log_transform_cols"]
        pipeline._is_fitted = data["is_fitted"]
        
        print(f"[PIPELINE] Cargado desde {filepath}")
        return pipeline
    
    def get_info(self):
        """Retorna metadata del pipeline."""
        return {
            "is_fitted": self._is_fitted,
            "log_transform_columns": len(self._log_transform_cols),
            "log_transform_threshold": self.log_transform_threshold,
            "scaler_type": "StandardScaler",
            "imputer_strategy": self.imputer.strategy,
        }
