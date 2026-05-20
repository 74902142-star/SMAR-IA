# Sprint 3 (MVP) — Cumplimiento Normativo ISO/IEC 27001:2022

> **Duración estimada:** 1 semana  
> **Estado actual:** ✅ COMPLETADO (controles base implementados)  
> **Hito:** Este sprint constituye el **MVP funcional**: el sistema detecta, mitiga y registra bajo cumplimiento normativo.

---

## 1. Objetivo General

Garantizar que el sistema SMAR-IA cumpla con los controles de seguridad de la información de **ISO/IEC 27001:2022**, específicamente los controles del Anexo A relacionados con registro de actividades, monitoreo y seguridad de redes. El objetivo es que cada evento del sistema quede documentado de forma auditable, íntegra y trazable.

Al finalizar este sprint debe ser posible:
- Demostrar evidencia de registro estructurado (Control A.8.15).
- Demostrar capacidad de monitoreo continuo (Control A.8.16).
- Demostrar registro de acciones de seguridad de red (Control A.8.20).
- Presentar un checklist documentado de controles implementados.

---

## 2. Controles ISO/IEC 27001:2022 Implementados

### 2.1 Resumen de Controles

| Control | Nombre | Implementación en SMAR-IA | Estado |
|---------|--------|--------------------------|--------|
| **A.8.15** | Registro de actividades | `SecurityLog` en `security_logs.db` | ✅ |
| **A.8.16** | Actividades de monitoreo | WebSocket + endpoint `/api/logs` | ✅ |
| **A.8.20** | Seguridad en redes | Registro de comandos iptables en BD | ✅ |
| **A.8.21** | Seguridad de servicios de red | Autenticación JWT en todos los endpoints | ✅ Parcial |
| **A.8.22** | Segregación de redes | Arquitectura dual DB (seguridad vs. tráfico) | ✅ Parcial |
| **A.8.29** | Pruebas de seguridad en desarrollo | (Sprint 5) | ⏳ Pendiente |
| **A.8.32** | Gestión de cambios | Documentación de sprints iterativos | ✅ Parcial |

---

## 3. Control A.8.15 — Registro de Actividades

### 3.1 Definición del Control

> *"Se deben crear, almacenar, proteger y analizar registros que contengan actividades de usuarios, excepciones, fallas y eventos de seguridad de la información."*

### 3.2 Implementación: Modelo `SecurityLog`

```python
# database.py
class SecurityLog(SecurityBase):
    __tablename__ = "security_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)  # UTC siempre
    source_ip = Column(String, index=True)
    destination_ip = Column(String)
    attack_type = Column(String, index=True)
    confidence = Column(Float)
    action_taken = Column(String)
    iso_control = Column(String, default="A.8.15")
```

### 3.3 Campos del Registro y su Propósito Normativo

| Campo | Tipo | Propósito ISO A.8.15 |
|-------|------|---------------------|
| `id` | Integer | Identificación única e irrepetible del evento |
| `timestamp` | DateTime UTC | Trazabilidad temporal exacta (no modificable por zona horaria) |
| `source_ip` | String | Identificación del actor/origen del evento |
| `destination_ip` | String | Identificación del recurso afectado |
| `attack_type` | String | Clasificación del tipo de evento/incidente |
| `confidence` | Float | Evidencia cuantitativa de la detección |
| `action_taken` | String | Registro de la respuesta aplicada |
| `iso_control` | String | Trazabilidad del control normativo aplicado |

### 3.4 Ejemplo de Registro Generado

```
ID:           142
Timestamp:    2026-05-18 23:12:47.234156 (UTC)
Source IP:    192.168.1.47
Dest IP:      192.168.1.1
Attack Type:  DDoS SYN Flood
Confidence:   0.9823 (98.23%)
Action:       AUTO-BLOCKED: iptables -A INPUT -s 192.168.1.47 -j DROP
ISO Control:  A.8.15
```

### 3.5 Tipos de Registros por Origen

| Origen | `action_taken` | `iso_control` |
|--------|---------------|---------------|
| Auto-bloqueo por IA (conf≥95%) | `AUTO-BLOCKED: iptables...` | `A.8.15` |
| Alerta pendiente (conf<95%) | `ALERTED (Pending Manual Review)` | `A.8.15` |
| Bloqueo manual por operador | `MANUAL: iptables...` | `A.8.20` |

---

## 4. Control A.8.16 — Actividades de Monitoreo

### 4.1 Definición del Control

> *"Las redes, sistemas y aplicaciones deben monitorearse continuamente para detectar comportamientos anómalos y desencadenar respuestas apropiadas."*

### 4.2 Implementación: WebSocket para Monitoreo Continuo

El sistema implementa monitoreo continuo mediante WebSocket, transmitiendo cada evento de tráfico analizado al frontend en tiempo real.

```python
# main.py — Endpoint WebSocket
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
```

**Evidencia de monitoreo continuo:**
- El bucle `process_traffic_loop()` procesa nuevos eventos cada **1 segundo**.
- Cada evento procesado se transmite inmediatamente a todos los clientes conectados.
- El frontend mantiene la conexión WebSocket activa durante toda la sesión.

### 4.3 Implementación: Endpoint de Métricas `/api/logs`

```python
# main.py
@app.get("/api/logs")
def get_logs(db: Session = Depends(get_security_db), limit: int = 50):
    logs = db.query(SecurityLog)\
        .order_by(SecurityLog.timestamp.desc())\
        .limit(limit)\
        .all()
    return logs
```

**Este endpoint cumple A.8.16 al permitir:**
- Consulta histórica de eventos de seguridad.
- Filtrado por cantidad de eventos recientes.
- Acceso desde el Dashboard y la vista de Logs del frontend.

### 4.4 Monitoreo en el Frontend — Dashboard

```javascript
// Dashboard.jsx — Conexión WebSocket permanente
useEffect(() => {
  ws.current = new WebSocket('ws://localhost:8000/ws');
  
  ws.current.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'traffic_update') {
      // Actualizar logs en tiempo real
      setLogs(prev => [newLog, ...prev.slice(0, 14)]);
      
      // Notificación visual inmediata
      if (data.is_alert) {
        toast.error(`INGRESO SOSPECHOSO: ${data.predicted_class} desde ${data.source_ip}`);
      }
    }
  };
  
  return () => ws.current?.close();
}, []);
```

### 4.5 Monitoreo en el Frontend — Logs Page

La página `Logs.jsx` implementa una **terminal en tiempo real** que combina:
- Carga inicial de los últimos 50 eventos vía `GET /api/logs`.
- Actualización continua mediante WebSocket.
- Categorización visual: `CRITICAL_ERR` (rosa) vs `NW_TRAFFIC` (cyan).

---

## 5. Control A.8.20 — Seguridad en Redes

### 5.1 Definición del Control

> *"Las redes y los servicios de red deben ser gestionados y controlados para proteger la información en los sistemas y aplicaciones."*

### 5.2 Implementación: Registro de Acciones de Red

Cada acción de mitigación (manual o automática) que afecta la red se registra con `iso_control="A.8.20"`:

```python
# routers/mitigation.py
new_log = SecurityLog(
    source_ip=request.ip,
    destination_ip="Any",
    attack_type=request.attack_type,
    confidence=1.0,
    action_taken=f"MANUAL: {command}",
    iso_control="A.8.20"      # ← Etiqueta el control aplicado
)
```

### 5.3 Comandos de Red Registrados

| Acción | Comando Registrado | Descripción |
|--------|-------------------|-------------|
| Bloqueo IP completo | `iptables -A INPUT -s {ip} -j DROP` | Elimina todo tráfico entrante |
| Cierre TCP por IP+Puerto | `iptables -A INPUT -p tcp --dport {port} -s {ip} -j DROP` | Cierra puerto TCP específico |
| Cierre UDP por IP+Puerto | `iptables -A INPUT -p udp --dport {port} -s {ip} -j DROP` | Cierra puerto UDP específico |

---

## 6. Control A.8.21 — Seguridad de Servicios de Red

### 6.1 Implementación: Autenticación JWT

Todos los endpoints de seguridad están protegidos mediante JWT con algoritmo HS256.

```python
# auth.py
SECRET_KEY = "smar_ia_secret_key_super_secure"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # Tokens válidos por 24 horas
```

**Endpoints protegidos por JWT:**

| Endpoint | Método | Protección |
|----------|--------|-----------|
| `/api/mitigation/suspicious` | GET | `Depends(get_current_user)` |
| `/api/mitigation/block` | POST | `Depends(get_current_user)` |
| `/api/auth/me` | GET | `Depends(get_current_user)` |
| `/api/logs` | GET | Sin autenticación (v1.0 — pendiente de asegurar) |

> **Tarea Pendiente:** Agregar `Depends(get_current_user)` al endpoint `/api/logs` para cumplimiento completo de A.8.21.

---

## 7. Control A.8.22 — Segregación de Redes (Datos)

### 7.1 Implementación: Arquitectura de Doble Base de Datos

El sistema separa lógicamente los datos en dos bases de datos independientes para cumplir el principio de segregación:

```python
# database.py — Dos engines SQLAlchemy separados

# Base de datos de SEGURIDAD (datos sensibles de auditoría)
SECURITY_DB_URL = "sqlite:///./security_logs.db"
security_engine = create_engine(SECURITY_DB_URL, ...)
SecuritySessionLocal = sessionmaker(bind=security_engine)

# Base de datos de TRÁFICO (datos operacionales brutos)
TRAFFIC_DB_URL = "sqlite:///./traffic.db"
traffic_engine = create_engine(TRAFFIC_DB_URL, ...)
TrafficSessionLocal = sessionmaker(bind=traffic_engine)
```

**Beneficios de esta segregación:**

| BD | Propósito | Acceso | Retención |
|----|-----------|--------|-----------|
| `security_logs.db` | Auditoría, eventos de seguridad | Solo backend con autenticación | Largo plazo (ISO A.8.15) |
| `traffic.db` | Datos de tráfico de red brutos | Backend interno únicamente | Corto plazo (se limpia periódicamente) |

---

## 8. Estructura de Evidencia para Auditoría

### 8.1 Consulta de Evidencia

Para obtener evidencia auditable del sistema, se puede consultar directamente la base de datos:

```sql
-- Todos los eventos en las últimas 24 horas
SELECT 
    id,
    datetime(timestamp, 'localtime') as hora_local,
    source_ip,
    destination_ip,
    attack_type,
    round(confidence * 100, 2) as confianza_pct,
    action_taken,
    iso_control
FROM security_logs
WHERE timestamp > datetime('now', '-24 hours')
ORDER BY timestamp DESC;
```

### 8.2 Reporte de Eventos por Tipo

```sql
-- Distribución de ataques detectados
SELECT 
    attack_type,
    COUNT(*) as total_eventos,
    AVG(confidence) as confianza_promedio,
    MIN(timestamp) as primer_evento,
    MAX(timestamp) as ultimo_evento
FROM security_logs
GROUP BY attack_type
ORDER BY total_eventos DESC;
```

### 8.3 Acciones de Mitigación Ejecutadas

```sql
-- Registro de mitigaciones bajo A.8.20
SELECT 
    datetime(timestamp, 'localtime') as hora,
    source_ip,
    action_taken,
    iso_control
FROM security_logs
WHERE iso_control = 'A.8.20'
ORDER BY timestamp DESC;
```

---

## 9. Endpoint `/api/logs` — Evidencia de Auditoría

```python
# main.py
@app.get("/api/logs")
def get_logs(db: Session = Depends(get_security_db), limit: int = 50):
    logs = db.query(SecurityLog)\
        .order_by(SecurityLog.timestamp.desc())\
        .limit(limit)\
        .all()
    return logs
```

**Respuesta completa para auditoría:**
```json
[
  {
    "id": 142,
    "timestamp": "2026-05-18T23:12:47.234156",
    "source_ip": "192.168.1.47",
    "destination_ip": "192.168.1.1",
    "attack_type": "DDoS SYN Flood",
    "confidence": 0.9823,
    "action_taken": "AUTO-BLOCKED: iptables -A INPUT -s 192.168.1.47 -j DROP",
    "iso_control": "A.8.15"
  }
]
```

---

## 10. Funcionalidades Pendientes para Cumplimiento Completo

### 10.1 Hash SHA-256 de Integridad de Logs (Pendiente)

> **Estado:** ⚠️ PLANIFICADO — No implementado en v1.0

Para garantizar integridad de logs (prevenir modificaciones post-registro), se debe agregar un campo `log_hash`:

```python
# Implementación futura en database.py
import hashlib
import json

def generate_log_hash(log_data: dict) -> str:
    """Genera hash SHA-256 del contenido del log para verificación de integridad."""
    log_string = json.dumps(log_data, sort_keys=True, default=str)
    return hashlib.sha256(log_string.encode()).hexdigest()

# Uso al crear SecurityLog:
log_content = {
    "timestamp": str(timestamp),
    "source_ip": source_ip,
    "destination_ip": destination_ip,
    "attack_type": attack_type,
    "confidence": confidence,
    "action_taken": action_taken
}
new_log = SecurityLog(
    ...
    log_hash=generate_log_hash(log_content)  # Campo a agregar
)
```

### 10.2 Política de Retención de Logs (Pendiente)

> **Estado:** ⚠️ PLANIFICADO

Según el plan de desarrollo:
- **30 días en caliente:** `security_logs.db` con acceso inmediato
- **1 año en frío:** Archivos JSON comprimidos con gzip

```bash
# Script de rotación diaria (a implementar en Sprint 5)
# cron: 0 0 * * * /usr/local/bin/smar-ia-log-rotate.sh

#!/bin/bash
DATE=$(date +%Y-%m-%d)
sqlite3 security_logs.db \
    "SELECT json_object(...) FROM security_logs WHERE date(timestamp) = '$DATE'" \
    | gzip > /var/log/uc_ids/events_$DATE.json.gz
```

### 10.3 Clasificación de Severidad (Pendiente)

> **Estado:** ⚠️ PLANIFICADO

Agregar campo `severity` basado en la confianza del modelo:

| Confianza | Severidad | Acción Recomendada |
|-----------|-----------|-------------------|
| ≥ 0.95 | `HIGH` | Bloqueo automático inmediato |
| 0.70 – 0.94 | `MEDIUM` | Alerta + revisión manual urgente |
| 0.50 – 0.69 | `LOW` | Monitoreo reforzado |
| < 0.50 | `INFO` | Registro informativo |

---

## 11. Checklist de Controles ISO — Estado del MVP

```
✅ A.8.15 — Registro de actividades
    ✅ Cada evento tiene timestamp UTC
    ✅ IP origen e IP destino registradas
    ✅ Tipo de ataque clasificado
    ✅ Nivel de confianza del modelo
    ✅ Acción tomada documentada
    ✅ Control ISO etiquetado por evento
    ⚠️  Hash SHA-256 de integridad (pendiente)
    ⚠️  Política de retención por niveles (pendiente)

✅ A.8.16 — Actividades de monitoreo
    ✅ WebSocket para actualización en tiempo real
    ✅ Dashboard con visualización de amenazas
    ✅ Endpoint GET /api/logs para consulta histórica
    ✅ Página de Logs con terminal en tiempo real
    ⚠️  Endpoint /health dedicado (pendiente)
    ⚠️  Métricas /metrics con formato estándar (pendiente)

✅ A.8.20 — Seguridad en redes
    ✅ Comandos iptables registrados en BD
    ✅ Diferenciación entre acciones manuales y automáticas
    ✅ Etiqueta iso_control="A.8.20" en acciones de red
    ⚠️  Whitelist de IPs críticas (pendiente)
    ⚠️  Modo dry-run para entornos de prueba (pendiente)

✅ A.8.21 — Seguridad de servicios de red
    ✅ JWT en endpoints de mitigación
    ✅ Contraseñas almacenadas en bcrypt
    ✅ Tokens con expiración de 24 horas
    ⚠️  JWT en endpoint /api/logs (pendiente)
    ⚠️  Rotación de SECRET_KEY (pendiente)

✅ A.8.22 — Segregación de redes (datos)
    ✅ BD de seguridad separada de BD de tráfico
    ✅ Sesiones de BD independientes por módulo
    ⚠️  Cifrado de BD en reposo (pendiente)
```

---

## 12. Criterios de Aceptación del Sprint 3 (MVP)

| Criterio | Método de Verificación | Estado |
|----------|----------------------|--------|
| Cada ataque genera registro en security_logs.db | Consultar BD tras ataque detectado | ✅ |
| Registro incluye timestamp UTC | `timestamp` en formato ISO 8601 UTC | ✅ |
| Control ISO documentado por evento | Campo `iso_control` tiene valor "A.8.15" o "A.8.20" | ✅ |
| Acciones manuales etiquetadas diferente | `MANUAL: iptables...` vs `AUTO-BLOCKED: iptables...` | ✅ |
| Logs accesibles via API REST | `GET /api/logs` retorna JSON válido | ✅ |
| Monitoreo en tiempo real operativo | WebSocket transmite eventos sin recargar página | ✅ |
| Sistema detecta, mitiga Y registra (MVP) | Ejecutar simulación y verificar los 3 comportamientos | ✅ |

---

## 13. Evidencia del MVP Funcional

Para demostrar el MVP funcional ante el equipo DTI o auditores, ejecutar la siguiente secuencia:

```bash
# Terminal 1: Backend
cd backend && uvicorn main:app --reload

# Terminal 2: Simulador
cd backend && python simulation.py

# Terminal 3: Frontend
cd frontend && npm run dev

# Acceder a http://localhost:5173
# Login: admin / admin123
# Observar:
#   1. Dashboard: paquetes de red animados en tiempo real
#   2. Toast notifications cuando se detectan ataques
#   3. Logs: terminal actualizada automáticamente
#   4. MitigationZone: IPs sospechosas listadas
#   5. Hacer clic en "EJECUTAR AISLAMIENTO" para bloqueo manual
#   6. Verificar en security_logs.db que el evento fue registrado
```

---

*Sprint 3 — SMAR-IA — Universidad Continental*  
*Hito MVP: Sistema funcional con detección, mitigación y registro auditables bajo ISO/IEC 27001:2022*
