# 📋 Sprint 1: Motor de Clasificación Offline

## 1. Objetivos del Sprint
* Desarrollar el pipeline para procesar archivos de captura de red raw (`.pcap`) a formato estructurado (`.csv`).
* Implementar algoritmos de extracción de flujos de red (como `CICFlowMeter` o equivalentes ligeros en Python).
* Entrenar y evaluar de manera offline el clasificador multiclase (8 categorías de ataque).

---

## 2. Alineación con el Estado del Arte
Los estudios de mitigación ML en SDN enfatizan que un modelo efectivo debe tener alta precisión y baja tasa de falsos positivos (FPR) para evitar la desconexión accidental de usuarios legítimos.
* **Algoritmos Seleccionados:** **Random Forest** (para un análisis rápido y robusto basado en múltiples árboles de decisión) y **XGBoost** (para mejorar el gradiente y optimizar la precisión en flujos altamente desbalanceados).
* **Características Clave del Flujo:** Extracción de características estadísticas temporales (duración del flujo, paquetes por segundo, desviación estándar de la longitud de bytes de paquetes).

---

## 3. Flujo del Pipeline de Datos Offline
El script `ml_pipeline/train_model.py` implementa el siguiente procesamiento:

```
┌──────────────┐     ┌──────────────────────┐     ┌──────────────────────┐
│ Archivo PCAP │────▶│ Extracción de Flujos │────▶│ Preprocesamiento CSV │
└──────────────┘     │  (Duración, Bytes)   │     │  (StandardScaler)    │
                     └──────────────────────┘     └──────────┬───────────┘
                                                             │
                                                             ▼
                                                  ┌──────────────────────┐
                                                  │ Entrenamiento Modelo │
                                                  │ (Random Forest 99.7%)│
                                                  └──────────────────────┘
```

### Script de Entrenamiento
Para entrenar y evaluar el modelo se ejecuta:
```bash
cd ml_pipeline
python train_model.py
```
El script genera los siguientes artefactos en `ml_pipeline/models/`:
* `random_forest.pkl` (modelo entrenado)
* `scaler.pkl` (escalador de características)
* `label_encoder.pkl` (mapeo de clases de ataques)

---

## 4. Métricas de Evaluación Obtenidas
* **Exactitud (Accuracy):** 99.71%
* **F1-Score Global:** 0.979
* **Tasa de Falsos Positivos (FPR):** < 0.52%

---

## 5. Criterios de Aceptación
* El modelo clasifica correctamente el tráfico benigno y los ataques en el dataset de prueba con una exactitud mínima del 98%.
* El scaler preprocesa un vector de características en menos de 1 milisegundo.
