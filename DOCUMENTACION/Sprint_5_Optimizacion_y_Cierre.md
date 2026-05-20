# Sprint 5 — Optimización y Cierre Técnico

> **Duración estimada:** 0.5 – 1 semana  
> **Estado actual:** 🔄 EN PROGRESO / PLANIFICADO  
> **Objetivo:** Validar rendimiento bajo carga, cumplir SLAs de latencia, corregir deuda técnica y generar documentación final de producción.

---

## 1. Objetivo General

Convertir el sistema SMAR-IA de un MVP funcional a un sistema listo para **despliegue controlado en producción** en la Universidad Continental. Esto implica:
- Medir y optimizar la latencia de inferencia (objetivo: ≤ 500ms por flujo).
- Ejecutar pruebas de estrés para validar comportamiento bajo alta carga.
- Generar reportes automáticos de auditoría para el equipo DTI.
- Completar la documentación técnica y de operación.
- Etiquetar el código como versión `v1.0`.

---

## 2. Criterios de Aceptación del Sistema (SLAs)

Estos son los criterios definidos en el plan de desarrollo que deben cumplirse al cierre:

| Métrica | Umbral Requerido | Herramienta de Medición | Estado |
|---------|-----------------|------------------------|--------|
| **Accuracy global del modelo** | ≥ 99% | Validación cruzada K-Fold (k=10) | ⚠️ Pendiente con dataset real |
| **Tasa de Falsos Positivos (FPR)** | ≤ 1% | FP/(FP+TN) sobre tráfico normal | ⚠️ Pendiente con dataset real |
| **Latencia de inferencia** | ≤ 500 ms/flujo | `time.perf_counter()` en 10k muestras | ⚠️ Pendiente medición formal |
| **Consumo de CPU** | ≤ 15% en inferencia | `psutil` durante sesión continua | ⚠️ Pendiente medición formal |
| **Controles ISO implementados** | ≥ 7 controles | Checklist Anexo B | ✅ 3 de 7 implementados |

---

## 3. Tareas de Optimización del Backend

### 3.1 Perfilado de Rendimiento

#### Herramienta: `cProfile`

```python
# profiler.py — Script de análisis de rendimiento
import cProfile
import pstats
import numpy as np
from ml_service import ml_service

ml_service.load_models()

def benchmark_predictions(n=10000):
    """Ejecuta N predicciones y mide el tiempo total."""
    test_features = [np.random.randn(80).tolist() for _ in range(n)]
    results = []
    for features in test_features:
        attack_type, confidence = ml_service.predict(features)
        results.append((attack_type, confidence))
    return results

# Ejecutar con profiler
profiler = cProfile.Profile()
profiler.enable()
benchmark_predictions(n=10000)
profiler.disable()

# Analizar resultados
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)  # Top 20 funciones más lentas
```

#### Herramienta: `time.perf_counter()`

```python
# Medición de latencia por predicción individual
import time

latencies = []
for i in range(10000):
    features = np.random.randn(80).tolist()
    
    start = time.perf_counter()
    attack_type, confidence = ml_service.predict(features)
    end = time.perf_counter()
    
    latency_ms = (end - start) * 1000
    latencies.append(latency_ms)

print(f"Latencia promedio: {np.mean(latencies):.2f} ms")
print(f"Latencia máxima: {np.max(latencies):.2f} ms")
print(f"Latencia p95: {np.percentile(latencies, 95):.2f} ms")
print(f"Latencia p99: {np.percentile(latencies, 99):.2f} ms")

# Resultado esperado para Random Forest con 80 features:
# Latencia promedio: ~0.5-2.0 ms (muy por debajo del SLA de 500ms)
```

### 3.2 Optimización: Inferencia por Lotes (Batch Inference)

El bucle actual procesa registros **uno por uno**. Para alta carga, se debe implementar inferencia por lotes:

```python
# Versión optimizada de process_traffic_loop()
async def process_traffic_loop_optimized():
    BATCH_SIZE = 100  # Procesar hasta 100 flujos por ciclo
    
    while True:
        unprocessed = db_traffic.query(NetworkTraffic)\
            .filter(NetworkTraffic.is_processed == 0)\
            .limit(BATCH_SIZE)\
            .all()
        
        if unprocessed:
            # Construir matriz de features para inferencia batch
            feature_matrix = []
            for traffic in unprocessed:
                features = [float(x) for x in traffic.features_csv.split(",")]
                feature_matrix.append(features)
            
            # Una sola llamada al modelo para todo el batch
            scaled = ml_service.scaler.transform(feature_matrix)
            predictions = ml_service.rf_classifier.predict(scaled)
            probabilities = ml_service.rf_classifier.predict_proba(scaled)
            
            # Procesar resultados batch
            for i, traffic in enumerate(unprocessed):
                attack_type = ml_service.label_encoder.inverse_transform(
                    [predictions[i]]
                )[0]
                confidence = float(np.max(probabilities[i]))
                # ... resto de la lógica
        
        await asyncio.sleep(0.5)  # Ciclo más frecuente con batch
```

**Beneficio esperado:** 10-100x mayor throughput al reducir el overhead de llamadas individuales al modelo.

### 3.3 Optimización: Medición de CPU con psutil

```python
# monitor_resources.py
import psutil
import time
import threading

class ResourceMonitor:
    def __init__(self, interval=1.0):
        self.interval = interval
        self.measurements = []
        self.running = False
    
    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._monitor)
        self.thread.start()
    
    def stop(self):
        self.running = False
        self.thread.join()
        return self.measurements
    
    def _monitor(self):
        while self.running:
            cpu = psutil.cpu_percent(interval=self.interval)
            ram = psutil.virtual_memory().percent
            self.measurements.append({
                "timestamp": time.time(),
                "cpu_percent": cpu,
                "ram_percent": ram
            })

# Uso durante pruebas de carga:
monitor = ResourceMonitor()
monitor.start()
# ... ejecutar pruebas ...
measurements = monitor.stop()
avg_cpu = sum(m["cpu_percent"] for m in measurements) / len(measurements)
print(f"CPU promedio durante inferencia: {avg_cpu:.1f}%")
# Objetivo: avg_cpu < 15%
```

---

## 4. Pruebas de Estrés — Locust

### 4.1 Configuración de Locust

```python
# locustfile.py
from locust import HttpUser, task, between
import json
import random

class IDS_User(HttpUser):
    wait_time = between(0.01, 0.1)  # 10-100ms entre requests
    
    # Token de autenticación (obtener antes de las pruebas)
    headers = {
        "Authorization": "Bearer <JWT_TOKEN>",
        "Content-Type": "application/json"
    }
    
    @task(5)
    def get_logs(self):
        """Simula consultas frecuentes de logs (mayor peso)."""
        self.client.get("/api/logs?limit=50")
    
    @task(3)
    def get_suspicious_ips(self):
        """Simula polling de IPs sospechosas."""
        self.client.get(
            "/api/mitigation/suspicious",
            headers=self.headers
        )
    
    @task(1)
    def block_ip(self):
        """Simula acciones de mitigación manual (menor frecuencia)."""
        payload = {
            "ip": f"192.168.1.{random.randint(2, 254)}",
            "action": "BLOCK_IP",
            "attack_type": "Stress Test"
        }
        self.client.post(
            "/api/mitigation/block",
            data=json.dumps(payload),
            headers=self.headers
        )
```

### 4.2 Ejecución de Pruebas de Estrés

```bash
# Instalar Locust
pip install locust

# Prueba básica: 100 usuarios, ramp-up de 10/s, 60 segundos
locust -f locustfile.py \
    --host http://localhost:8000 \
    --users 100 \
    --spawn-rate 10 \
    --run-time 60s \
    --headless \
    --html stress_report.html

# Prueba de estrés alta: simular 10k flujos/s
locust -f locustfile.py \
    --host http://localhost:8000 \
    --users 500 \
    --spawn-rate 50 \
    --run-time 120s \
    --headless \
    --html stress_report_high.html
```

### 4.3 Métricas a Capturar

| Métrica | Umbral Objetivo | Cómo medir |
|---------|----------------|-----------|
| RPS (Requests Per Second) | ≥ 100 RPS | Dashboard Locust |
| Latencia P50 | ≤ 100ms | Dashboard Locust |
| Latencia P95 | ≤ 500ms | Dashboard Locust |
| Latencia P99 | ≤ 1000ms | Dashboard Locust |
| Tasa de Error | ≤ 1% | Dashboard Locust |
| CPU Backend | ≤ 15% | `psutil` durante prueba |
| RAM Backend | ≤ 2GB | `psutil` durante prueba |

---

## 5. Validación del Modelo ML — K-Fold Cross Validation

### 5.1 Script de Validación Cruzada

```python
# validate_model.py
import numpy as np
import joblib
from sklearn.model_selection import cross_validate, StratifiedKFold
from sklearn.metrics import classification_report, confusion_matrix
import pandas as pd

# Cargar modelos
rf = joblib.load('../ml_pipeline/models/random_forest.pkl')
scaler = joblib.load('../ml_pipeline/models/scaler.pkl')
le = joblib.load('../ml_pipeline/models/label_encoder.pkl')

# Cargar dataset de validación (usar dataset real aquí)
# X_test, y_test = cargar_dataset_cicids2018()

# Validación K-Fold (k=10)
skf = StratifiedKFold(n_splits=10, shuffle=True, random_state=42)

scoring = ['accuracy', 'precision_macro', 'recall_macro', 'f1_macro']
cv_results = cross_validate(
    rf, X_scaled, y_encoded,
    cv=skf,
    scoring=scoring,
    return_train_score=True
)

print("=== RESULTADOS K-FOLD (k=10) ===")
print(f"Accuracy promedio: {cv_results['test_accuracy'].mean():.4f} ± {cv_results['test_accuracy'].std():.4f}")
print(f"Precisión promedio: {cv_results['test_precision_macro'].mean():.4f}")
print(f"Recall promedio: {cv_results['test_recall_macro'].mean():.4f}")
print(f"F1-Score promedio: {cv_results['test_f1_macro'].mean():.4f}")

# Calcular FPR (False Positive Rate)
y_pred = rf.predict(X_scaled)
cm = confusion_matrix(y_encoded, y_pred)
TN = cm[0][0]  # True Negatives (tráfico normal correctamente clasificado)
FP = cm[0][1:].sum()  # False Positives (normal clasificado como ataque)
FPR = FP / (FP + TN)
print(f"\nFalse Positive Rate (FPR): {FPR:.4f} ({FPR*100:.2f}%)")
print(f"Objetivo: ≤ 1% → {'✅ CUMPLE' if FPR <= 0.01 else '❌ NO CUMPLE'}")
```

---

## 6. Generación Automática de Reportes de Auditoría

### 6.1 Reporte Semanal (HTML)

```python
# report_generator.py
import sqlite3
import json
from datetime import datetime, timedelta
from jinja2 import Template

def generate_weekly_report():
    conn = sqlite3.connect('security_logs.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Período del reporte
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=7)
    
    # Estadísticas generales
    cursor.execute("""
        SELECT 
            COUNT(*) as total_events,
            COUNT(CASE WHEN attack_type != 'Normal' THEN 1 END) as total_attacks,
            COUNT(CASE WHEN action_taken LIKE 'AUTO-BLOCKED%' THEN 1 END) as auto_blocked,
            COUNT(CASE WHEN action_taken LIKE 'MANUAL%' THEN 1 END) as manual_blocked
        FROM security_logs
        WHERE timestamp BETWEEN ? AND ?
    """, (start_date.isoformat(), end_date.isoformat()))
    
    stats = dict(cursor.fetchone())
    
    # Distribución por tipo de ataque
    cursor.execute("""
        SELECT attack_type, COUNT(*) as count
        FROM security_logs
        WHERE timestamp BETWEEN ? AND ?
        GROUP BY attack_type
        ORDER BY count DESC
    """, (start_date.isoformat(), end_date.isoformat()))
    
    attack_distribution = [dict(row) for row in cursor.fetchall()]
    
    # Top 5 IPs atacantes
    cursor.execute("""
        SELECT source_ip, COUNT(*) as alert_count, MAX(timestamp) as last_seen
        FROM security_logs
        WHERE attack_type != 'Normal' AND timestamp BETWEEN ? AND ?
        GROUP BY source_ip
        ORDER BY alert_count DESC
        LIMIT 5
    """, (start_date.isoformat(), end_date.isoformat()))
    
    top_attackers = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    # Generar HTML
    report_data = {
        "generated_at": datetime.utcnow().isoformat(),
        "period_start": start_date.isoformat(),
        "period_end": end_date.isoformat(),
        "stats": stats,
        "attack_distribution": attack_distribution,
        "top_attackers": top_attackers
    }
    
    # Guardar como JSON para auditoría
    filename = f"reports/audit_report_{end_date.strftime('%Y-%m-%d')}.json"
    with open(filename, 'w') as f:
        json.dump(report_data, f, indent=2, default=str)
    
    print(f"Reporte generado: {filename}")
    return report_data
```

---

## 7. Deuda Técnica — Tareas Pendientes

### 7.1 Seguridad

| Tarea | Prioridad | Descripción |
|-------|-----------|-------------|
| Mover `SECRET_KEY` a variable de entorno | 🔴 ALTA | Actualmente hardcodeada en `auth.py` |
| Agregar JWT a `/api/logs` | 🔴 ALTA | Endpoint público sin autenticación |
| Implementar whitelist de IPs críticas | 🟡 MEDIA | Evitar auto-bloqueo de infraestructura crítica |
| Agregar campo `log_hash` SHA-256 | 🟡 MEDIA | Garantizar integridad de registros (A.8.15) |
| Rate limiting en `/api/auth/login` | 🟡 MEDIA | Prevenir ataques de fuerza bruta al propio sistema |

### 7.2 Rendimiento

| Tarea | Prioridad | Descripción |
|-------|-----------|-------------|
| Batch inference en `process_traffic_loop()` | 🔴 ALTA | Reemplazar loop individual por inferencia matricial |
| Migrar `blocked_ips` a Redis | 🟡 MEDIA | Persistir bloqueos entre reinicios del servidor |
| Migrar SQLite a PostgreSQL | 🟠 BAJA | Necesario para producción con alta concurrencia |
| Índices en columnas de búsqueda frecuente | 🟡 MEDIA | `timestamp`, `source_ip`, `attack_type` ya indexados |

### 7.3 Funcionalidades Faltantes

| Tarea | Sprint Objetivo | Descripción |
|-------|----------------|-------------|
| Filtros funcionales en `Logs.jsx` | Sprint 5 | `CRITICAL_ONLY` y `AI_LOGIC` no filtran aún |
| Modo dry-run para mitigación | Sprint 5 | Variable de entorno `SMAR_IA_DRY_RUN` |
| Política de retención de logs | Sprint 5 | Rotación diaria + compresión gzip |
| Clasificación de severidad (HIGH/MED/LOW) | Sprint 5 | Campo `severity` en `SecurityLog` |
| CNN-BiLSTM integration | Producción | Requiere TensorFlow estable en Python 3.11 |
| Integración real con CICFlowMeter | Producción | PCAP → CSV → Features reales |
| Reporte PDF semanal (WeasyPrint) | Sprint 5 | Reporte automático para auditoría ISO |

---

## 8. Variables de Entorno — Configuración para Producción

```bash
# .env (crear en backend/ — NO commitear a git)
SMAR_IA_SECRET_KEY="cambiar_por_clave_segura_de_64_chars_minimo"
SMAR_IA_DB_URL="postgresql://user:pass@localhost:5432/smar_ia"
SMAR_IA_DRY_RUN="false"
SMAR_IA_LOG_RETENTION_DAYS="30"
SMAR_IA_MODELS_DIR="/opt/smar-ia/models"
SMAR_IA_LOG_DIR="/var/log/uc_ids"
```

```python
# auth.py — Versión para producción
import os

SECRET_KEY = os.getenv("SMAR_IA_SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SMAR_IA_SECRET_KEY no está configurada en variables de entorno")
```

---

## 9. Guía de Despliegue en Producción

### 9.1 Requisitos del Servidor

| Recurso | Mínimo | Recomendado |
|---------|--------|-------------|
| CPU | 4 núcleos | 8 núcleos |
| RAM | 4 GB | 8 GB |
| Almacenamiento | 50 GB | 200 GB |
| SO | Ubuntu 22.04 LTS | Ubuntu 22.04 LTS |
| Python | 3.11 | 3.11 |
| Red | 1 Gbps | 10 Gbps |

### 9.2 Instalación en Servidor Linux

```bash
# 1. Clonar repositorio
git clone <repo_url> /opt/smar-ia
cd /opt/smar-ia

# 2. Crear entorno virtual Python 3.11
python3.11 -m venv .venv
source .venv/bin/activate

# 3. Instalar dependencias
pip install -r backend/requirements.txt

# 4. Entrenar modelos ML
cd ml_pipeline && python train_model.py && cd ..

# 5. Configurar variables de entorno
cp .env.example backend/.env
nano backend/.env  # Editar valores

# 6. Configurar systemd para el backend
sudo nano /etc/systemd/system/smar-ia.service
```

```ini
# /etc/systemd/system/smar-ia.service
[Unit]
Description=SMAR-IA IDS Backend
After=network.target

[Service]
Type=simple
User=smar-ia
WorkingDirectory=/opt/smar-ia/backend
EnvironmentFile=/opt/smar-ia/backend/.env
ExecStart=/opt/smar-ia/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
# 7. Iniciar y habilitar el servicio
sudo systemctl daemon-reload
sudo systemctl enable smar-ia
sudo systemctl start smar-ia
sudo systemctl status smar-ia

# 8. Build del frontend para producción
cd frontend && npm run build
# Servir /dist con nginx o directamente desde FastAPI
```

---

## 10. Integración CNN-BiLSTM (Trabajo Futuro)

### 10.1 Arquitectura Planificada

```python
# ml_pipeline/cnn_bilstm_model.py (implementación futura)
import tensorflow as tf

def build_cnn_bilstm(input_shape=(80, 1), num_classes=8):
    """
    Arquitectura CNN-BiLSTM para clasificación de tráfico de red.
    
    - CNN: Extrae características locales (patrones de bytes)
    - BiLSTM: Captura dependencias temporales bidireccionales
    """
    inputs = tf.keras.Input(shape=input_shape)
    
    # CNN block — extracción de características
    x = tf.keras.layers.Conv1D(64, kernel_size=3, activation='relu', padding='same')(inputs)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.MaxPooling1D(pool_size=2)(x)
    x = tf.keras.layers.Dropout(0.25)(x)
    
    # BiLSTM block — contexto temporal
    x = tf.keras.layers.Bidirectional(
        tf.keras.layers.LSTM(128, return_sequences=False)
    )(x)
    x = tf.keras.layers.Dropout(0.5)(x)
    
    # Clasificación final
    outputs = tf.keras.layers.Dense(num_classes, activation='softmax')(x)
    
    return tf.keras.Model(inputs=inputs, outputs=outputs)
```

### 10.2 Requisitos para Activar CNN-BiLSTM

- [ ] Python 3.11 (no 3.14)
- [ ] TensorFlow 2.15+ instalado correctamente
- [ ] Dataset real de entrenamiento (CIC-IDS2017 o CIC-IDS2018)
- [ ] GPU recomendada para entrenamiento (CUDA compatible)
- [ ] Migrar `ml_service.py` para cargar ambos modelos (RF + CNN-BiLSTM)

---

## 11. Integración con CICFlowMeter (Trabajo Futuro)

```python
# pcap_ingestor.py (implementación futura para Sprint 1 extendido)
import subprocess
import pandas as pd

class PCAPIngestor:
    """Convierte archivos PCAP a flujos de red usando CICFlowMeter."""
    
    SELECTED_FEATURES = [
        'Flow Duration', 'Total Fwd Packets', 'Total Backward Packets',
        'Fwd Packet Length Max', 'Fwd Packet Length Mean',
        'Bwd Packet Length Max', 'Flow Bytes/s', 'Flow Packets/s',
        'SYN Flag Count', 'RST Flag Count', 'PSH Flag Count',
        'ACK Flag Count', 'FIN Flag Count',
        # ... hasta 80 features seleccionadas
    ]
    
    def convert_pcap_to_csv(self, pcap_file: str) -> pd.DataFrame:
        """Invoca CICFlowMeter via subprocess y retorna DataFrame."""
        result = subprocess.run(
            ['java', '-jar', 'CICFlowMeter.jar', pcap_file, '/tmp/flows/'],
            capture_output=True, text=True, timeout=300
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"CICFlowMeter error: {result.stderr}")
        
        # Leer CSV generado por CICFlowMeter
        csv_file = f"/tmp/flows/{pcap_file.replace('.pcap', '_Flow.csv')}"
        df = pd.read_csv(csv_file)
        
        # Seleccionar solo las features relevantes
        return df[self.SELECTED_FEATURES]
```

---

## 12. Documentación API — OpenAPI/Swagger

La documentación interactiva de la API está disponible automáticamente gracias a FastAPI:

| URL | Descripción |
|-----|-------------|
| `http://localhost:8000/docs` | Swagger UI interactivo |
| `http://localhost:8000/redoc` | ReDoc (alternativa) |
| `http://localhost:8000/openapi.json` | Esquema OpenAPI 3.0 |

### Endpoints Documentados

```yaml
# Resumen de la API actual (OpenAPI 3.0)
openapi: 3.0.0
info:
  title: IDS Security Dashboard API
  version: 1.0.0

paths:
  /api/auth/login:
    post:
      summary: Autenticación de usuario
      requestBody: form-data (username, password)
      responses:
        200: { access_token, token_type }
        401: Unauthorized
  
  /api/auth/me:
    get:
      summary: Información del usuario actual
      security: BearerAuth
  
  /api/logs:
    get:
      summary: Obtener historial de eventos de seguridad
      parameters: limit (int, default=50)
  
  /api/mitigation/suspicious:
    get:
      summary: Obtener IPs sospechosas activas
      security: BearerAuth
  
  /api/mitigation/block:
    post:
      summary: Ejecutar acción de mitigación
      security: BearerAuth
      requestBody: { ip, action, port, attack_type }
  
  /ws:
    websocket:
      summary: Stream en tiempo real de eventos de tráfico
```

---

## 13. Checklist Final de Cierre

### Código y Calidad
- [ ] Todos los endpoints tienen manejo de errores apropiado
- [ ] Logs del servidor configurados con niveles (INFO, WARNING, ERROR)
- [ ] Secrets movidos a variables de entorno
- [ ] Endpoint `/api/logs` protegido con JWT
- [ ] Filtros funcionales en `Logs.jsx`
- [ ] Whitelist de IPs críticas implementada

### Rendimiento
- [ ] Batch inference implementado en `process_traffic_loop()`
- [ ] Latencia promedio medida y documentada (objetivo: ≤450ms)
- [ ] CPU promedio durante inferencia ≤15% documentado
- [ ] Prueba Locust ejecutada con 10k flujos/s

### ML y Precisión
- [ ] Validación K-Fold (k=10) ejecutada con dataset real
- [ ] Accuracy ≥99% documentado
- [ ] FPR ≤1% verificado
- [ ] Matriz de confusión generada y analizada

### ISO/IEC 27001
- [ ] Checklist de 7 controles completado (A.8.15, 16, 20, 21, 22, 29, 32)
- [ ] Hash SHA-256 implementado en SecurityLog
- [ ] Política de retención de logs configurada
- [ ] Clasificación de severidad HIGH/MEDIUM/LOW implementada

### Documentación
- [ ] Este archivo (`Sprint_5`) actualizado con resultados reales
- [ ] API OpenAPI exportada a archivo estático
- [ ] Manual de operador creado
- [ ] Guía de despliegue validada en entorno de prueba
- [ ] Repositorio etiquetado como `v1.0`

---

## 14. Reporte de Performance (Plantilla)

```markdown
# Reporte de Performance — SMAR-IA v1.0
**Fecha:** [YYYY-MM-DD]
**Entorno:** [Especificaciones del servidor]

## Resultados de Latencia
- Predicciones medidas: 10,000
- Latencia promedio: [X] ms
- Latencia P95: [X] ms
- Latencia P99: [X] ms
- ✅/❌ SLA ≤500ms: [CUMPLE/NO CUMPLE]

## Resultados de CPU
- Duración de la prueba: 60 minutos
- CPU promedio: [X]%
- CPU máximo: [X]%
- ✅/❌ SLA ≤15% CPU: [CUMPLE/NO CUMPLE]

## Resultados ML
- Dataset de validación: [Nombre del dataset]
- Accuracy (K-Fold k=10): [X]%
- FPR: [X]%
- ✅/❌ Accuracy ≥99%: [CUMPLE/NO CUMPLE]
- ✅/❌ FPR ≤1%: [CUMPLE/NO CUMPLE]

## Controles ISO implementados: [X]/7
```

---

*Sprint 5 — SMAR-IA — Universidad Continental*  
*Versión objetivo: v1.0 — Lista para despliegue controlado en producción*
