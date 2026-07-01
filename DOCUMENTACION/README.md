# 📋 DOCUMENTACIÓN TÉCNICA — SMAR-IA
## Sistema de Detección de Intrusiones (NIDS) — Universidad Continental

> **Arquitectura:** Random Forest (base) → CNN-BiLSTM+RF (producción)  
> **Cumplimiento:** ISO/IEC 27001:2022  
> **Metodología:** Ágil por Sprints  
> **Stack:** Python 3.11 · FastAPI · React 19 · Vite · SQLite  

---

## 🗂️ Índice de Documentación por Iteración

| Archivo | Sprint | Descripción |
|---------|--------|-------------|
| [Sprint_0_Setup_e_Infraestructura.md](./Sprint_0_Setup_e_Infraestructura.md) | Sprint 0 | Entorno, ML Pipeline, modelos, Docker |
| [Sprint_1_Motor_Clasificacion_Offline.md](./Sprint_1_Motor_Clasificacion_Offline.md) | Sprint 1 | Clasificador offline PCAP→CSV→Predicción |
| [Sprint_2_Pipeline_Tiempo_Real_Mitigacion.md](./Sprint_2_Pipeline_Tiempo_Real_Mitigacion.md) | Sprint 2 | WebSocket en vivo, iptables, mitigación |
| [Sprint_3_MVP_Cumplimiento_ISO.md](./Sprint_3_MVP_Cumplimiento_ISO.md) | Sprint 3 (MVP) | Logs JSON, hash SHA-256, controles ISO |
| [Sprint_4_Dashboard_y_UX.md](./Sprint_4_Dashboard_y_UX.md) | Sprint 4 | Frontend React, Dashboard, páginas |
| [Sprint_5_Optimizacion_y_Cierre.md](./Sprint_5_Optimizacion_y_Cierre.md) | Sprint 5 | Pruebas de estrés, rendimiento, docs finales |
| [Sprint_6_Implementacion_Final.md](./Sprint_6_Implementacion_Final.md) | Sprint 6 | Implementación final y despliegue en producción |
| [plan_de_pruebas/README_PLAN_PRUEBAS.md](./plan_de_pruebas/README_PLAN_PRUEBAS.md) | Pruebas | Plan integral de pruebas de calidad, rendimiento e integridad |

---

## 🏗️ Arquitectura General del Sistema

```
┌─────────────────────────────────────────────────────────┐
│                    SMAR-IA SYSTEM                        │
│                                                         │
│  ┌──────────────┐    WebSocket    ┌──────────────────┐  │
│  │   FRONTEND   │ ◄────────────► │    BACKEND       │  │
│  │  React 19    │                │   FastAPI        │  │
│  │  Vite 8.x    │   REST API     │   Uvicorn        │  │
│  │  Port: 5173  │ ◄────────────► │   Port: 8000     │  │
│  └──────────────┘                └──────┬───────────┘  │
│                                         │               │
│                              ┌──────────┼──────────┐   │
│                              │          │          │   │
│                    ┌─────────▼──┐  ┌────▼────┐  ┌─▼─┐ │
│                    │ security_  │  │traffic  │  │ML │ │
│                    │ logs.db    │  │  .db    │  │Svc│ │
│                    │ (SQLite)   │  │(SQLite) │  └───┘ │
│                    └────────────┘  └─────────┘        │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │               ML PIPELINE                        │  │
│  │  train_model.py → random_forest.pkl              │  │
│  │                 → scaler.pkl                     │  │
│  │                 → label_encoder.pkl              │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 Estructura del Repositorio

```
SMAR-IA/
├── backend/
│   ├── main.py              # App FastAPI + WebSocket + bucle de procesamiento
│   ├── auth.py              # JWT, bcrypt, OAuth2
│   ├── database.py          # SQLAlchemy: SecurityLog, NetworkTraffic, User
│   ├── ml_service.py        # Carga y predicción del modelo ML
│   ├── simulation.py        # Generador de tráfico simulado
│   ├── requirements.txt     # Dependencias Python
│   ├── security_logs.db     # BD de eventos de seguridad (ISO A.8.15)
│   ├── traffic.db           # BD de tráfico de red simulado
│   └── routers/
│       ├── auth.py          # Endpoints /api/auth/login, /api/auth/me
│       └── mitigation.py    # Endpoints /api/mitigation/suspicious, /block
│
├── frontend/
│   ├── package.json         # React 19, Vite 8, Recharts, React-Toastify
│   ├── vite.config.js
│   └── src/
│       ├── App.jsx          # Router principal + ProtectedRoute
│       ├── main.jsx
│       ├── index.css        # Sistema de diseño completo (cyber-theme)
│       ├── context/
│       │   └── AuthContext.jsx  # Estado global de autenticación
│       └── pages/
│           ├── Login.jsx        # Formulario de autenticación
│           ├── Layout.jsx       # Sidebar + navegación
│           ├── Dashboard.jsx    # Vista principal + mapa de red en vivo
│           ├── TrafficMonitor.jsx  # Monitor de tráfico
│           ├── MitigationZone.jsx  # Zona de mitigación manual
│           ├── Logs.jsx         # Terminal de logs en tiempo real
│           └── Settings.jsx     # Configuración del sistema
│
└── ml_pipeline/
    ├── train_model.py       # Entrenamiento Random Forest + exportación
    ├── requirements.txt
    └── models/
        ├── random_forest.pkl    # Clasificador entrenado (~30 MB)
        ├── scaler.pkl           # StandardScaler
        └── label_encoder.pkl   # Codificador de etiquetas
```

---

## 🔐 Controles ISO/IEC 27001:2022 Implementados

| Control | Descripción | Implementación en SMAR-IA |
|---------|-------------|--------------------------|
| **A.8.15** | Registro de actividades | `SecurityLog` en `security_logs.db`, cada evento con timestamp, IP, tipo, confianza |
| **A.8.16** | Actividades de monitoreo | WebSocket en tiempo real + endpoint `/api/logs` |
| **A.8.20** | Seguridad en redes | Mitigación vía `iptables` registrada en DB con `iso_control="A.8.20"` |

---

## 🚀 Comandos de Inicio Rápido

```bash
# 1. Entrenar el modelo ML (una sola vez)
cd ml_pipeline
pip install -r requirements.txt
python train_model.py

# 2. Iniciar el backend
cd ../backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# 3. Iniciar el simulador de tráfico (terminal separada)
cd backend
python simulation.py

# 4. Iniciar el frontend
cd ../frontend
npm install
npm run dev
```

---

## 👥 Credenciales por Defecto

| Campo | Valor |
|-------|-------|
| Usuario | `admin` |
| Contraseña | `admin123` |
| Token expira en | 24 horas |

---

*Documentación generada para el proyecto SMAR-IA — Universidad Continental*  
*Fecha de referencia: Mayo 2026*
