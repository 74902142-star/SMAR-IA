# Sprint 1 — Motor de Clasificación Offline

> **Duración estimada:** 1.5 semanas  
> **Estado actual:** ✅ COMPLETADO (integrado en el backend)  
> **Objetivo:** Clasificar tráfico de red desde archivos o datos preprocesados y obtener predicciones multiclase con nivel de confianza.

---

## 1. Objetivo General

Construir y validar el núcleo de clasificación ML del sistema IDS. En este sprint se implementa la capacidad de tomar un vector de características de red y clasificarlo en una de las 8 categorías definidas, registrando el tipo de ataque y el nivel de confianza del modelo.

Al finalizar este sprint debe ser posible:
- Recibir features de tráfico de red (80 columnas numéricas).
- Aplicar preprocesamiento (`StandardScaler`).
- Obtener predicción del modelo Random Forest.
- Retornar el nombre del ataque y la confianza (0.0–1.0).
- Registrar los resultados en `security_logs.db`.

---

## 2. Clases de Ataque del Sistema

El modelo clasifica el tráfico en **8 categorías**:

| Índice | Clase | Distribución Dataset | Descripción |
|--------|-------|---------------------|-------------|
| 0 | `Normal` | 50% | Tráfico de red legítimo |
| 1 | `DDoS SYN Flood` | 10% | Inundación de paquetes SYN para saturar conexiones |
| 2 | `DDoS UDP Flood` | 5% | Inundación UDP para saturar ancho de banda |
| 3 | `Sniffing Pasivo` | 5% | Captura pasiva de paquetes en la red |
| 4 | `DHCP Starvation` | 5% | Agotamiento del pool DHCP |
| 5 | `DHCP Spoofing` | 5% | Servidor DHCP malicioso en la red |
| 6 | `Port Scanning` | 10% | Exploración de puertos abiertos |
| 7 | `Brute Force` | 10% | Ataques de fuerza bruta a servicios |

---

## 3. Pipeline de Clasificación — Diseño Detallado

```
  Tráfico de Red
       │
       ▼
  [features_csv]          ← Almacenado en traffic.db
  "0.12, -1.45, 3.78, ..."   (80 valores separados por comas)
       │
       ▼
  [Parseo a lista Python]
  features = [float(x) for x in features_csv.split(",")]
       │
       ▼
  [StandardScaler.transform()]    ← scaler.pkl
  scaled = scaler.transform([features])
       │
       ▼
  [RandomForestClassifier.predict()]   ← random_forest.pkl
  prediction_encoded = [4]  (índice numérico)
       │
       ▼
  [LabelEncoder.inverse_transform()]   ← label_encoder.pkl
  predicted_class = "Normal" | "DDoS SYN Flood" | ...
       │
       ▼
  [predict_proba()]
  confidence = max(probabilities)  → 0.0 – 1.0
       │
       ▼
  (predicted_class, confidence)
```

---

## 4. Implementación: `ml_service.py`

### 4.1 Clase `MLService` — Análisis Completo

```python
class MLService:
    def __init__(self, models_dir="../ml_pipeline/models"):
        self.rf_classifier = None       # RandomForestClassifier
        self.scaler = None              # StandardScaler
        self.label_encoder = None       # LabelEncoder
        self.is_loaded = False          # Flag de disponibilidad
```

### 4.2 Método `load_models()` — Detalle

```python
def load_models(self):
    try:
        # Carga el clasificador principal (~30 MB desde disco)
        self.rf_classifier = joblib.load(
            os.path.join(self.models_dir, "random_forest.pkl")
        )
        # Carga el normalizador ajustado al dataset de entrenamiento
        self.scaler = joblib.load(
            os.path.join(self.models_dir, "scaler.pkl")
        )
        # Carga el codificador de etiquetas (índice ↔ nombre)
        self.label_encoder = joblib.load(
            os.path.join(self.models_dir, "label_encoder.pkl")
        )
        self.is_loaded = True
        print("Modelos cargados exitosamente.")
    except Exception as e:
        print(f"Error cargando modelos: {e}")
        # is_loaded permanece False → predict() retornará ("Unknown", 0.0)
```

### 4.3 Método `predict()` — Detalle

```python
def predict(self, features_array):
    # Guard: si el modelo no está disponible
    if not self.is_loaded:
        return "Unknown", 0.0
    
    try:
        # Paso 1: Normalizar con el scaler entrenado
        # CRÍTICO: usar transform(), NO fit_transform()
        scaled_features = self.scaler.transform([features_array])
        
        # Paso 2: Clasificar con Random Forest
        # Retorna array de índices: ej. [2] = "DDoS UDP Flood"
        prediction_encoded = self.rf_classifier.predict(scaled_features)
        
        # Paso 3: Obtener probabilidades por clase
        # Retorna array 2D: [[p_class0, p_class1, ..., p_class7]]
        probabilities = self.rf_classifier.predict_proba(scaled_features)
        
        # Paso 4: Decodificar el índice al nombre de clase
        predicted_class = self.label_encoder.inverse_transform(
            prediction_encoded
        )[0]
        
        # Paso 5: Confianza = probabilidad máxima del ensemble
        confidence = float(np.max(probabilities))
        
        return predicted_class, confidence
        
    except Exception as e:
        print(f"Error en predicción: {e}")
        return "Error", 0.0
```

---

## 5. Integración en el Bucle de Procesamiento

### Archivo: `backend/main.py` — Función `process_traffic_loop()`

El clasificador offline está integrado en el bucle asíncrono que procesa continuamente la tabla `network_traffic` de la base de datos.

```python
async def process_traffic_loop():
    while True:
        # Obtener registros no procesados de traffic.db
        unprocessed_traffic = db_traffic.query(NetworkTraffic)\
            .filter(NetworkTraffic.is_processed == 0)\
            .all()
        
        for traffic in unprocessed_traffic:
            # 1. Parsear el vector CSV → lista de floats
            features = [float(x) for x in traffic.features_csv.split(",")]
            
            # 2. CLASIFICACIÓN: invocar el modelo
            attack_type, confidence = ml_service.predict(features)
            
            # 3. Lógica de respuesta basada en resultado
            if attack_type != "Normal" and attack_type != "Unknown":
                # Es un ataque → registrar en security_logs.db
                new_log = SecurityLog(
                    source_ip=traffic.source_ip,
                    destination_ip=traffic.destination_ip,
                    attack_type=attack_type,
                    confidence=confidence,
                    action_taken=action_taken
                )
                db_security.add(new_log)
            
            # 4. Marcar como procesado
            traffic.is_processed = 1
            db_traffic.commit()
        
        await asyncio.sleep(1)  # Ciclo cada 1 segundo
```

---

## 6. Lógica de Decisión Post-Clasificación

Una vez obtenida la predicción, el sistema aplica la siguiente lógica de decisión:

```
¿La IP origen está en lista de bloqueadas?
    └─ SÍ → Omitir procesamiento (marcar como procesado y continuar)
    └─ NO → Continuar...

¿El tipo de ataque es "Normal" o "Unknown"?
    └─ SÍ → action_taken = "NONE", no registrar en security_logs
    └─ NO → Es un ataque...
         ├─ Incrementar contador de actividad sospechosa para esa IP
         ├─ ¿Confianza >= 0.95?
         │    └─ SÍ → AUTO-BLOQUEO
         │         action_taken = "AUTO-BLOCKED: iptables -A INPUT -s {IP} -j DROP"
         │         blocked_ips.add(source_ip)
         └─ NO (confianza < 0.95) →
              action_taken = "ALERTED (Pending Manual Review)"
              Queda visible en MitigationZone para acción manual
```

### Umbrales de Decisión

| Confianza del Modelo | Acción |
|---------------------|--------|
| >= 0.95 (95%) | **AUTO-BLOCK**: IP bloqueada automáticamente |
| 0.50 – 0.94 | **ALERTA**: Pendiente revisión manual del operador |
| < 0.50 | Clasificado como no confiable (treated as Unknown) |

---

## 7. Registro de Clasificaciones — `SecurityLog`

Cada evento de ataque detectado genera un registro en `security_logs.db`:

```python
SecurityLog(
    timestamp    = datetime.utcnow(),      # UTC automático
    source_ip    = "192.168.1.47",         # IP del atacante
    destination_ip = "192.168.1.1",        # IP objetivo
    attack_type  = "DDoS SYN Flood",       # Clase predicha
    confidence   = 0.9823,                 # Confianza del RF (0-1)
    action_taken = "AUTO-BLOCKED: iptables -A INPUT -s 192.168.1.47 -j DROP",
    iso_control  = "A.8.15"               # Control ISO documentado
)
```

---

## 8. API de Consulta de Logs

### `GET /api/logs?limit=N`

Retorna los últimos N registros de `security_logs.db` ordenados por timestamp descendente.

**Ejemplo de respuesta:**
```json
[
  {
    "id": 142,
    "timestamp": "2026-05-18T23:12:45.123456",
    "source_ip": "192.168.1.47",
    "destination_ip": "192.168.1.1",
    "attack_type": "DDoS SYN Flood",
    "confidence": 0.9823,
    "action_taken": "AUTO-BLOCKED: iptables -A INPUT -s 192.168.1.47 -j DROP",
    "iso_control": "A.8.15"
  },
  ...
]
```

**Uso desde el frontend (Dashboard.jsx):**
```javascript
fetch('http://localhost:8000/api/logs?limit=10')
  .then(res => res.json())
  .then(data => {
    setLogs(data);
    setStats({
      total_alerts: data.length,
      actions_taken: data.filter(
        l => l.action_taken !== 'NONE' && l.action_taken !== 'ALERTED'
      ).length
    });
  });
```

---

## 9. Vector de Características — Descripción

El sistema actual usa **80 features numéricas** que en un entorno de producción real corresponden a métricas extraídas de flujos de red (CICFlowMeter). En la simulación se usan valores gaussianos, pero la estructura es la misma.

### Features típicas de CICFlowMeter (referencia)

| Grupo | Ejemplos de Features |
|-------|---------------------|
| **Duración** | `Flow Duration`, `Fwd IAT Mean` |
| **Conteos** | `Total Fwd Packets`, `Total Backward Packets` |
| **Longitudes** | `Fwd Packet Length Max`, `Bwd Packet Length Mean` |
| **Flags TCP** | `SYN Flag Count`, `ACK Flag Count`, `FIN Flag Count` |
| **Velocidad** | `Flow Bytes/s`, `Flow Packets/s` |
| **Ventanas** | `Init_Win_bytes_forward`, `Init_Win_bytes_backward` |

---

## 10. Resultados de Clasificación Esperados

### Ejemplo de salida en consola del sistema

```
[2026-05-18 23:12:45 UTC] Tráfico normal desde 192.168.1.133
[2026-05-18 23:12:46 UTC] Tráfico normal desde 192.168.1.87

--- NUEVA RÁFAGA DE ATAQUE DETECTADA DESDE 192.168.1.47 ---

[2026-05-18 23:12:47 UTC] [ALERTA] Ráfaga de ataque desde 192.168.1.47 (Restantes: 7)
[2026-05-18 23:12:47 UTC] [ALERTA] Ráfaga de ataque desde 192.168.1.47 (Restantes: 6)
```

### Predicción resultante en frontend (Dashboard Log)
```
[23:12:47] CRÍTICO: DDoS SYN Flood DETECTADA DESDE 192.168.1.47
[23:12:46] FLUJO_NOMINAL: PETICIÓN DESDE 192.168.1.87 → NONE
```

---

## 11. Criterios de Aceptación del Sprint 1

| Criterio | Método de Verificación | Estado |
|----------|----------------------|--------|
| Modelo carga sin errores | Log "Modelos cargados exitosamente." al iniciar backend | ✅ |
| Predicción retorna clase válida | `predict([...])` retorna una de las 8 clases | ✅ |
| Confianza en rango [0, 1] | `0.0 <= confidence <= 1.0` | ✅ |
| Tráfico normal no genera log | `attack_type="Normal"` no se inserta en `security_logs` | ✅ |
| Ataque con conf≥95% auto-bloqueado | `blocked_ips` contiene la IP tras predicción alta | ✅ |
| Logs accesibles vía API | `GET /api/logs` retorna JSON válido | ✅ |

---

## 12. Prueba Manual del Clasificador

Para probar el clasificador de forma aislada:

```python
# test_classifier.py (ejecutar en backend/)
from ml_service import ml_service
import numpy as np

ml_service.load_models()

# Test 1: Features de tráfico normal (distribución gaussiana centrada)
normal_features = np.random.randn(80).tolist()
clase, confianza = ml_service.predict(normal_features)
print(f"Normal features → {clase} ({confianza:.1%})")

# Test 2: Features de ataque simulado (media desplazada)
attack_features = (np.random.randn(80) * 10 + 20).tolist()
clase, confianza = ml_service.predict(attack_features)
print(f"Attack features → {clase} ({confianza:.1%})")
```

**Salida típica:**
```
Normal features → Normal (87.2%)
Attack features → DDoS SYN Flood (99.4%)
```

---

## 13. Limitaciones Actuales y Trabajo Futuro

| Limitación | Impacto | Solución Planificada |
|------------|---------|---------------------|
| Random Forest en lugar de CNN-BiLSTM+RF | Menor precisión en secuencias temporales | Integrar TensorFlow cuando soporte Python 3.11+ estable |
| Dataset simulado (no real) | Modelo entrenado en datos sintéticos | Reemplazar por CIC-IDS2018 o dataset real |
| Features gaussianas (no reales) | No refleja flujos de red reales | Integrar CICFlowMeter PCAP→CSV en Sprint 1 extendido |
| No hay validación cruzada K-Fold | Métricas de precisión no validadas | Implementar K-Fold en Sprint 5 con dataset real |

---

*Sprint 1 — SMAR-IA — Universidad Continental*
