# Sprint 0 — Setup e Infraestructura (Base Técnica)

> **Duración estimada:** 1 semana  
> **Estado actual:** ✅ COMPLETADO  
> **Objetivo:** Tener un entorno de ejecución reproducible con modelo exportable y cargable.

---

## 1. Objetivo General

Preparar el entorno completo de desarrollo, establecer el pipeline de datos desde el origen (tráfico simulado/real) hasta la inferencia del modelo, y garantizar que todos los componentes del stack tecnológico estén integrados y operativos.

Al finalizar este sprint, debe ser posible:
- Levantar el backend FastAPI sin errores.
- Cargar los modelos ML (Random Forest + Scaler + LabelEncoder) desde disco.
- Conectar el frontend React al backend a través de REST y WebSocket.
- Ejecutar el simulador de tráfico y ver datos llegar al sistema.

---

## 2. Stack Tecnológico Definido

| Capa | Tecnología | Versión | Propósito |
|------|-----------|---------|-----------|
| **Backend API** | FastAPI | Latest | Servidor REST + WebSocket |
| **Servidor ASGI** | Uvicorn | Latest | Servidor de producción para FastAPI |
| **ORM / Base de Datos** | SQLAlchemy + SQLite | Latest | Persistencia de eventos y tráfico |
| **ML Classifier** | Scikit-learn (Random Forest) | Latest | Motor de clasificación de ataques |
| **Serialización ML** | Joblib | Latest | Carga/guardado de modelos `.pkl` |
| **Autenticación** | python-jose + passlib (bcrypt) | Latest | JWT + hash de contraseñas |
| **Frontend** | React 19 + Vite 8 | Latest | Interfaz de usuario SPA |
| **Comunicación en Tiempo Real** | WebSocket nativo (FastAPI) | — | Streaming de eventos al frontend |
| **Gráficos** | Recharts | ^3.8.1 | Visualización de datos |
| **UI Components** | React-Bootstrap 2.x | Latest | Layout y componentes |

---

## 3. Estructura de Directorios Creada

```
SMAR-IA/
├── backend/                     ← Servidor FastAPI
│   ├── main.py
│   ├── auth.py
│   ├── database.py
│   ├── ml_service.py
│   ├── simulation.py
│   ├── requirements.txt
│   └── routers/
│       ├── auth.py
│       └── mitigation.py
│
├── frontend/                    ← Aplicación React
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── App.jsx
│       ├── main.jsx
│       ├── index.css
│       ├── context/
│       │   └── AuthContext.jsx
│       └── pages/
│           ├── Login.jsx
│           ├── Layout.jsx
│           ├── Dashboard.jsx
│           ├── TrafficMonitor.jsx
│           ├── MitigationZone.jsx
│           ├── Logs.jsx
│           └── Settings.jsx
│
└── ml_pipeline/                 ← Entrenamiento y exportación de modelos
    ├── train_model.py
    ├── requirements.txt
    └── models/
        ├── random_forest.pkl   (~30 MB)
        ├── scaler.pkl
        └── label_encoder.pkl
```

---

## 4. ML Pipeline — Entrenamiento y Exportación

### Archivo: `ml_pipeline/train_model.py`

Este script es el punto de entrada del pipeline de Machine Learning. Genera un dataset simulado, entrena el modelo y exporta todos los artefactos necesarios.

#### 4.1 Clases de Ataque Definidas

```python
ATTACK_CLASSES = [
    'Normal',           # Tráfico legítimo (50% del dataset)
    'DDoS SYN Flood',   # 10%
    'DDoS UDP Flood',   # 5%
    'Sniffing Pasivo',  # 5%
    'DHCP Starvation',  # 5%
    'DHCP Spoofing',    # 5%
    'Port Scanning',    # 10%
    'Brute Force'       # 10%
]
```

> **Nota de Arquitectura:** La arquitectura final es CNN-BiLSTM + Random Forest. En la implementación actual, se usa **exclusivamente Random Forest** como clasificador funcional, ya que TensorFlow no es compatible con Python 3.14+. El modelo CNN-BiLSTM se integrará cuando el entorno soporte TensorFlow 2.x estable.

#### 4.2 Parámetros del Dataset Simulado

| Parámetro | Valor | Justificación |
|-----------|-------|---------------|
| `NUM_FEATURES` | 80 | Simula el vector de características de flujos de red (CICFlowMeter genera ~80 features) |
| `NUM_SAMPLES` | 5,000 | Dataset pequeño optimizado para demostración sin sobrecargar hardware |
| `random_state` | 42 | Reproducibilidad garantizada |
| `test_size` | 0.2 | Split 80/20 entrenamiento/prueba |

#### 4.3 Configuración del Modelo Random Forest

```python
RandomForestClassifier(
    n_estimators=100,      # 100 árboles de decisión
    max_depth=None,        # Sin límite de profundidad (overfitting mínimo en RF)
    class_weight='balanced', # Compensa el desbalance de clases
    random_state=42
)
```

#### 4.4 Preprocesamiento

```python
# Paso 1: Codificación de etiquetas
le = LabelEncoder()
y_encoded = le.fit_transform(y)  # Normal→4, DDoS SYN→0, etc.

# Paso 2: Normalización de features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)  # Media=0, StdDev=1
```

#### 4.5 Artefactos Exportados

```
ml_pipeline/models/
├── random_forest.pkl    # Clasificador principal (~30 MB)
├── scaler.pkl           # StandardScaler ajustado al dataset
└── label_encoder.pkl    # Mapeo índice ↔ nombre de ataque
```

#### 4.6 Cómo Ejecutar el Entrenamiento

```bash
cd ml_pipeline
pip install scikit-learn joblib pandas numpy
python train_model.py
```

**Salida esperada:**
```
Generando dataset simulado...
Preprocesando datos...
Entrenando Random Forest...
Precisión de RF en entrenamiento: 0.9998
Precisión de RF en prueba: 0.9412
Guardando modelos...
¡Entrenamiento y exportación completados!
```

---

## 5. Backend — Servicio de Carga de Modelos

### Archivo: `backend/ml_service.py`

La clase `MLService` abstrae toda la lógica de ML del resto del backend.

```python
class MLService:
    def __init__(self, models_dir="../ml_pipeline/models"):
        self.rf_classifier = None
        self.scaler = None
        self.label_encoder = None
        self.is_loaded = False
```

#### 5.1 Método `load_models()`

Carga los tres artefactos desde disco usando `joblib`. Se invoca automáticamente al iniciar la aplicación FastAPI mediante el evento `startup`.

```python
# En main.py — evento de inicio
@app.on_event("startup")
async def startup_event():
    init_db()
    ml_service.load_models()   # ← Aquí se cargan los modelos
    asyncio.create_task(process_traffic_loop())
```

#### 5.2 Método `predict(features_array)`

Recibe un array de 80 features numéricas y retorna:
- `predicted_class` (str): Nombre del ataque o "Normal"
- `confidence` (float 0.0–1.0): Probabilidad máxima de la predicción

```python
def predict(self, features_array):
    scaled_features = self.scaler.transform([features_array])
    prediction_encoded = self.rf_classifier.predict(scaled_features)
    probabilities = self.rf_classifier.predict_proba(scaled_features)
    
    predicted_class = self.label_encoder.inverse_transform(prediction_encoded)[0]
    confidence = float(np.max(probabilities))
    
    return predicted_class, confidence
```

#### 5.3 Manejo de Errores

| Escenario | Respuesta |
|-----------|-----------|
| Modelos no cargados (`is_loaded=False`) | Retorna `("Unknown", 0.0)` |
| Excepción durante predicción | Retorna `("Error", 0.0)` y loguea el error |
| Archivo `.pkl` no encontrado | Imprime mensaje de error y `is_loaded` queda en `False` |

---

## 6. Base de Datos — Modelo Dual de Persistencia

### Archivo: `backend/database.py`

El sistema usa **dos bases de datos SQLite independientes** para separar responsabilidades:

#### 6.1 `security_logs.db` — Eventos de Seguridad (ISO A.8.15)

```python
# URL de conexión
SECURITY_DB_URL = "sqlite:///./security_logs.db"
```

**Tabla `security_logs`:**

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `id` | Integer PK | Identificador único del evento |
| `timestamp` | DateTime | Fecha y hora UTC del evento |
| `source_ip` | String | IP origen del tráfico analizado |
| `destination_ip` | String | IP destino |
| `attack_type` | String | Tipo de ataque detectado o "Normal" |
| `confidence` | Float | Confianza del modelo (0.0–1.0) |
| `action_taken` | String | Acción ejecutada (NONE, AUTO-BLOCKED, MANUAL) |
| `iso_control` | String | Control ISO aplicado (default: "A.8.15") |

**Tabla `users`:**

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `id` | Integer PK | ID del usuario |
| `username` | String (único) | Nombre de usuario |
| `hashed_password` | String | Contraseña en bcrypt |
| `is_active` | Integer | 1=Activo, 0=Inactivo |

#### 6.2 `traffic.db` — Tráfico de Red Simulado

```python
TRAFFIC_DB_URL = "sqlite:///./traffic.db"
```

**Tabla `network_traffic`:**

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `id` | Integer PK | ID del registro |
| `timestamp` | DateTime | Momento de captura |
| `source_ip` | String | IP origen (simulada: 192.168.1.X) |
| `destination_ip` | String | IP destino (fija: 192.168.1.1) |
| `features_csv` | String | Vector de 80 features como CSV separado por comas |
| `is_processed` | Integer | 0=Pendiente, 1=Procesado por el bucle ML |

#### 6.3 Inicialización de Base de Datos

La función `init_db()` se ejecuta al importar el módulo y crea automáticamente el usuario `admin` si no existe:

```python
def init_db():
    # Crea las tablas si no existen (SQLAlchemy)
    SecurityBase.metadata.create_all(bind=security_engine)
    TrafficBase.metadata.create_all(bind=traffic_engine)
    
    # Crea usuario admin por defecto
    hashed_pw = pwd_context.hash("admin123")
    new_admin = User(username="admin", hashed_password=hashed_pw)
```

---

## 7. Autenticación JWT — Módulo Base

### Archivo: `backend/auth.py`

```python
SECRET_KEY = "smar_ia_secret_key_super_secure"  # ⚠️ Mover a .env en producción
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 horas
```

**Flujo de autenticación:**

```
Cliente → POST /api/auth/login (username + password)
        → Verificación bcrypt en BD
        → JWT generado con HS256
        → Token retornado al cliente
        → Cliente incluye "Authorization: Bearer <token>" en cada request
        → get_current_user() valida el JWT en cada endpoint protegido
```

---

## 8. Simulador de Tráfico

### Archivo: `backend/simulation.py`

Genera tráfico de red sintético en la base de datos `traffic.db` para poder demostrar el sistema sin hardware de red real.

#### 8.1 Lógica de Generación

```python
# Tráfico normal: features gaussianas centradas en 0
features = np.random.randn(80)  # Distribución normal estándar

# Tráfico de ataque: features desplazadas (anómalas)
features = np.random.randn(80) * 10 + 20  # Media=20, StdDev=10
```

#### 8.2 Patrón de Ráfagas (Burst Attack)

```python
# 5% de probabilidad de iniciar un ataque tipo ráfaga
if random.random() < 0.05:
    attack_burst_remaining = random.randint(4, 8)  # 4-8 paquetes rápidos
    sleep_time = random.uniform(0.1, 0.3)          # Intervalos muy cortos
```

| Modo | Intervalo entre paquetes | Features | Descripción |
|------|--------------------------|----------|-------------|
| Normal | 0.5 – 2.0 segundos | `randn(80)` | Tráfico legítimo aleatorio |
| Ráfaga de ataque | 0.1 – 0.3 segundos | `randn(80)*10+20` | Simula DDoS/PortScan |

#### 8.3 Ejecución

```bash
# Terminal separada al backend
cd backend
python simulation.py
```

---

## 9. Dependencias del Backend

### Archivo: `backend/requirements.txt`

```
fastapi
uvicorn
sqlalchemy
websockets
pydantic
tensorflow        # Para CNN-BiLSTM (integración futura)
scikit-learn
joblib
pandas
numpy
python-jose[cryptography]   # JWT
passlib[bcrypt]             # Hash de contraseñas
```

---

## 10. Dependencias del Frontend

### Archivo: `frontend/package.json`

```json
{
  "dependencies": {
    "bootstrap": "^5.3.8",
    "lucide-react": "^1.14.0",
    "react": "^19.2.5",
    "react-bootstrap": "^2.10.10",
    "react-dom": "^19.2.5",
    "react-router-dom": "^7.14.2",
    "react-toastify": "^11.1.0",
    "recharts": "^3.8.1"
  }
}
```

---

## 11. Comandos de Setup Completo

```bash
# ── PASO 1: Entrenar y exportar modelos ──────────────────────────
cd SMAR-IA/ml_pipeline
pip install scikit-learn joblib pandas numpy
python train_model.py
# Verifica que existan: models/random_forest.pkl, models/scaler.pkl, models/label_encoder.pkl

# ── PASO 2: Levantar el backend ──────────────────────────────────
cd ../backend
pip install fastapi uvicorn sqlalchemy python-jose passlib joblib numpy scikit-learn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
# Verifica: http://localhost:8000/docs (Swagger UI)

# ── PASO 3: Simulador de tráfico ─────────────────────────────────
# (Terminal 2)
cd SMAR-IA/backend
python simulation.py

# ── PASO 4: Frontend ─────────────────────────────────────────────
cd SMAR-IA/frontend
npm install
npm run dev
# Acceso: http://localhost:5173
```

---

## 12. Criterios de Aceptación del Sprint 0

| Criterio | Cómo verificar | Estado |
|----------|---------------|--------|
| Modelos ML exportados a `models/` | `ls ml_pipeline/models/` muestra 3 archivos `.pkl` | ✅ |
| Backend inicia sin errores | `uvicorn main:app` → "Modelos cargados exitosamente" | ✅ |
| Swagger UI accesible | `http://localhost:8000/docs` carga correctamente | ✅ |
| Usuario admin creado | Login con admin/admin123 retorna JWT | ✅ |
| Frontend conecta al backend | Dashboard carga y se conecta vía WebSocket | ✅ |
| Simulador genera tráfico | `traffic.db` crece en tamaño durante ejecución | ✅ |

---

## 13. Problemas Conocidos y Mitigaciones

| Problema | Causa | Solución Aplicada |
|----------|-------|-------------------|
| TensorFlow incompatible con Python 3.14 | TF no soporta Python 3.14+ aún | Se usa Random Forest puro como proxy funcional |
| `SECRET_KEY` hardcodeada | Práctica insegura | Pendiente migración a variables de entorno (Sprint 5) |
| SQLite no apto para alta concurrencia | Limitación del motor | Aceptado para demo; migrar a PostgreSQL en producción |
| `check_same_thread=False` en SQLite | Necesario para asyncio | Aceptado; usar sesiones independientes por hilo |

---

*Sprint 0 — SMAR-IA — Universidad Continental*
