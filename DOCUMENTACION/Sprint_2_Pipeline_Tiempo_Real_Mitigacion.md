# Sprint 2 — Pipeline en Tiempo Real y Mitigación

> **Duración estimada:** 1.5 semanas  
> **Estado actual:** ✅ COMPLETADO  
> **Objetivo:** Procesar tráfico en tiempo real mediante WebSocket, ejecutar inferencia ML de forma continua y aplicar mitigación automática/manual mediante bloqueo de IPs.

---

## 1. Objetivo General

Convertir el clasificador offline en un sistema reactivo en tiempo real. El sistema debe:
- Procesar continuamente nuevos registros de tráfico (cada 1 segundo).
- Transmitir resultados al frontend mediante WebSocket sin latencia perceptible.
- Ejecutar bloqueos automáticos de IPs cuando la confianza del modelo supere el 95%.
- Permitir al operador de seguridad ejecutar mitigaciones manuales desde la interfaz.
- Mantener un registro de IPs sospechosas con conteo de alertas recientes.

---

## 2. Arquitectura del Pipeline en Tiempo Real

```
┌─────────────────────────────────────────────────────────────┐
│                   PIPELINE EN TIEMPO REAL                    │
│                                                             │
│  simulation.py          backend/main.py                     │
│  ─────────────          ────────────────                    │
│  [Genera tráfico]  →   [process_traffic_loop()]             │
│  Cada 0.1–2.0s         ├─ Lee NetworkTraffic no procesados  │
│                         ├─ ml_service.predict()             │
│                         ├─ Registra en SecurityLog          │
│                         ├─ Actualiza blocked_ips            │
│                         └─ Broadcast WebSocket              │
│                                    │                        │
│                                    ▼                        │
│                           ConnectionManager                 │
│                           .broadcast(message)               │
│                                    │                        │
│                         ┌──────────┼──────────┐            │
│                         ▼          ▼          ▼            │
│                    Dashboard  TrafficMonitor  Logs          │
│                    (React)    (React)         (React)       │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Bucle de Procesamiento Asíncrono

### Archivo: `backend/main.py` — `process_traffic_loop()`

Este bucle es el corazón del pipeline en tiempo real. Se ejecuta como una tarea asyncio independiente en segundo plano.

```python
async def process_traffic_loop():
    print("Iniciando bucle de procesamiento de tráfico...")
    while True:
        db_traffic = next(get_traffic_db())
        db_security = next(get_security_db())
        
        try:
            # Obtener todos los registros sin procesar
            unprocessed_traffic = db_traffic.query(NetworkTraffic)\
                .filter(NetworkTraffic.is_processed == 0)\
                .all()
            
            for traffic in unprocessed_traffic:
                # ── PASO 1: Parsear features ─────────────────────
                features = [float(x) for x in traffic.features_csv.split(",")]
                
                # ── PASO 2: Inferencia ML ─────────────────────────
                attack_type, confidence = ml_service.predict(features)
                
                # ── PASO 3: Verificar lista de bloqueadas ──────────
                if traffic.source_ip in blocked_ips:
                    traffic.is_processed = 1
                    db_traffic.commit()
                    continue  # Saltar IPs ya bloqueadas
                
                # ── PASO 4: Lógica de mitigación ──────────────────
                action_taken = "NONE"
                is_alert = False
                
                if attack_type != "Normal" and attack_type != "Unknown":
                    is_alert = True
                    add_suspicious_activity(traffic.source_ip)
                    
                    if confidence >= 0.95:
                        # AUTO-BLOQUEO
                        action_taken = f"AUTO-BLOCKED: iptables -A INPUT -s {traffic.source_ip} -j DROP"
                        blocked_ips.add(traffic.source_ip)
                    else:
                        # Alerta para revisión manual
                        action_taken = "ALERTED (Pending Manual Review)"
                    
                    # ── PASO 5: Persistir en security_logs.db ────
                    new_log = SecurityLog(
                        source_ip=traffic.source_ip,
                        destination_ip=traffic.destination_ip,
                        attack_type=attack_type,
                        confidence=confidence,
                        action_taken=action_taken
                    )
                    db_security.add(new_log)
                    db_security.commit()
                
                # ── PASO 6: Marcar como procesado ─────────────────
                traffic.is_processed = 1
                db_traffic.commit()
                
                # ── PASO 7: Broadcast WebSocket ───────────────────
                ws_message = {
                    "type": "traffic_update",
                    "timestamp": traffic.timestamp.isoformat(),
                    "source_ip": traffic.source_ip,
                    "destination_ip": traffic.destination_ip,
                    "predicted_class": attack_type,
                    "confidence": confidence,
                    "is_alert": is_alert,
                    "action_taken": action_taken
                }
                await manager.broadcast(ws_message)
                
        except Exception as e:
            print(f"Error procesando tráfico: {e}")
        finally:
            db_traffic.close()
            db_security.close()
        
        await asyncio.sleep(1)  # Ciclo cada 1 segundo
```

---

## 4. Gestión de Conexiones WebSocket

### Clase `ConnectionManager`

```python
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception:
                pass  # Ignorar conexiones rotas
```

### Endpoint WebSocket

```python
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()  # Mantiene la conexión abierta
    except WebSocketDisconnect:
        manager.disconnect(websocket)
```

### Formato del Mensaje WebSocket

```json
{
  "type": "traffic_update",
  "timestamp": "2026-05-18T23:12:47.234156",
  "source_ip": "192.168.1.47",
  "destination_ip": "192.168.1.1",
  "predicted_class": "DDoS SYN Flood",
  "confidence": 0.9823,
  "is_alert": true,
  "action_taken": "AUTO-BLOCKED: iptables -A INPUT -s 192.168.1.47 -j DROP"
}
```

---

## 5. Sistema de Mitigación

### Archivo: `backend/routers/mitigation.py`

#### 5.1 Estructuras de Datos en Memoria

```python
# Registro de actividad sospechosa: IP → lista de timestamps
# Se limpia automáticamente cada 5 minutos
suspicious_ips_tracker = collections.defaultdict(list)

# IPs actualmente bloqueadas (RAM)
# En producción: persistir en Redis o BD
blocked_ips = set()
```

> **Nota de Producción:** `blocked_ips` y `suspicious_ips_tracker` viven en memoria RAM. Si el servidor reinicia, se pierden. En producción, estos datos deben persistirse en Redis o en la base de datos.

#### 5.2 Función `add_suspicious_activity(ip)`

```python
def add_suspicious_activity(ip: str):
    now = datetime.utcnow()
    suspicious_ips_tracker[ip].append(now)
    
    # Ventana deslizante de 5 minutos
    suspicious_ips_tracker[ip] = [
        t for t in suspicious_ips_tracker[ip] 
        if now - t < timedelta(minutes=5)
    ]
```

Esta función se llama automáticamente desde `process_traffic_loop()` cada vez que se detecta un ataque.

---

## 6. Endpoints de Mitigación

### `GET /api/mitigation/suspicious`

Retorna todas las IPs con **3 o más alertas** en los últimos 5 minutos y que **no están bloqueadas aún**.

**Requiere:** JWT Bearer Token

**Respuesta:**
```json
[
  {
    "ip": "192.168.1.47",
    "alert_count": 7,
    "last_seen": "2026-05-18T23:12:50.123456"
  },
  {
    "ip": "192.168.1.93",
    "alert_count": 4,
    "last_seen": "2026-05-18T23:12:48.789012"
  }
]
```

**Uso en frontend (`MitigationZone.jsx`):**
```javascript
const fetchSuspicious = async () => {
  const res = await fetch('http://localhost:8000/api/mitigation/suspicious', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  const data = await res.json();
  setSuspiciousIps(data);
  if (data.length > 0 && !activeIncident) {
    setActiveIncident(data[0]);  // Auto-selecciona el primer incidente
  }
};

// Refresca cada 3 segundos
const interval = setInterval(fetchSuspicious, 3000);
```

---

### `POST /api/mitigation/block`

Ejecuta una acción de mitigación y la registra en `security_logs.db` bajo el control **ISO A.8.20**.

**Requiere:** JWT Bearer Token

**Body:**
```json
{
  "ip": "192.168.1.47",
  "action": "BLOCK_IP",
  "port": null,
  "attack_type": "IA Recommended Mitigation"
}
```

**Acciones disponibles:**

| `action` | Comando iptables generado | Descripción |
|----------|--------------------------|-------------|
| `BLOCK_IP` | `iptables -A INPUT -s {ip} -j DROP` | Bloquea toda comunicación desde la IP |
| `CLOSE_TCP` | `iptables -A INPUT -p tcp --dport {port} -s {ip} -j DROP` | Cierra un puerto TCP específico |
| `CLOSE_UDP` | `iptables -A INPUT -p udp --dport {port} -s {ip} -j DROP` | Cierra un puerto UDP específico |

**Lógica interna:**
```python
@router.post("/block")
def block_ip(request: MitigateRequest, db: Session = Depends(get_security_db), 
             current_user = Depends(get_current_user)):
    
    # Construir comando iptables según acción solicitada
    if request.action == "BLOCK_IP":
        command = f"iptables -A INPUT -s {request.ip} -j DROP"
    elif request.action == "CLOSE_TCP":
        command = f"iptables -A INPUT -p tcp --dport {request.port} -s {request.ip} -j DROP"
    
    # Registrar en BD bajo control ISO A.8.20
    new_log = SecurityLog(
        source_ip=request.ip,
        destination_ip="Any",
        attack_type=request.attack_type,
        confidence=1.0,            # Acción manual = confianza total
        action_taken=f"MANUAL: {command}",
        iso_control="A.8.20"       # Control de seguridad de red
    )
    db.add(new_log)
    db.commit()
    
    # Actualizar estado en memoria
    blocked_ips.add(request.ip)
    if request.ip in suspicious_ips_tracker:
        del suspicious_ips_tracker[request.ip]
    
    return {"status": "success", "message": f"Command logged: {command}"}
```

**Respuesta:**
```json
{
  "status": "success",
  "message": "Command logged: iptables -A INPUT -s 192.168.1.47 -j DROP"
}
```

---

## 7. Interfaz de Mitigación — Frontend

### Archivo: `frontend/src/pages/MitigationZone.jsx`

#### 7.1 Componentes de la Interfaz

```
┌────────────────────────────────────────────────────────────┐
│  Matriz_de_Amenazas_Activa          UPTIME: 99.98%         │
│  Incidente: #TK-8829 | Prioridad: CRÍTICA  LATENCIA: 12ms  │
├─────────────────────────┬──────────────────────────────────┤
│  PERFIL_DE_INCURSIÓN    │  RECOMENDACIONES IA              │
│  ┌─────────────────┐    │  ┌──────────────────────────┐   │
│  │    [Bug Icon]   │    │  │ 🛡 AISLAMIENTO FIREWALL   │   │
│  │   Scanning...   │    │  │   Prob. Éxito: 94%        │   │
│  │                 │    │  │   [EJECUTAR AISLAMIENTO]  │   │
│  │ NODO_ORIGEN:    │    │  ├──────────────────────────┤   │
│  │ 192.168.1.47    │    │  │ ⚡ TERMINAR CONEXIÓN      │   │
│  │ FIRMA: WORM_V3  │    │  │   Prob. Éxito: 100%       │   │
│  │ VECTOR: L7_EXP  │    │  │   [TERMINAR AHORA]        │   │
│  │ RIESGO: 9.8/10  │    │  ├──────────────────────────┤   │
│  └─────────────────┘    │  │ 🔒 ENCRIPTAR SEGMENTO     │   │
│  [Terminal Log Area]    │  │   Prob. Éxito: 88%        │   │
│                         │  │   [ACTIVAR ENCRIPTACIÓN]  │   │
│                         │  └──────────────────────────┘   │
├─────────────────────────┴──────────────────────────────────┤
│  [Tendencia] [CONFIANZA SMAR-IA: 99.4%] [Nodos Seguros]   │
└────────────────────────────────────────────────────────────┘
```

#### 7.2 Función `handleMitigate()`

```javascript
const handleMitigate = async (ip, action, port = null) => {
  const payload = {
    ip: ip,
    action: action,           // "BLOCK_IP", "CLOSE_TCP", "CLOSE_UDP"
    port: port,               // null para BLOCK_IP, número para CLOSE_*
    attack_type: "IA Recommended Mitigation"
  };

  const res = await fetch('http://localhost:8000/api/mitigation/block', {
    method: 'POST',
    headers: { 
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(payload)
  });

  if (res.ok) {
    toast.success(`Protocolo ${action} ejecutado con éxito`, { theme: "dark" });
    fetchSuspicious();  // Refresca la lista de sospechosos
  }
};
```

#### 7.3 Botones de Acción y Sus Efectos

| Botón | Acción | Parámetros enviados |
|-------|--------|---------------------|
| **EJECUTAR AISLAMIENTO** | `BLOCK_IP` | `{ip: activeIncident.ip, action: "BLOCK_IP"}` |
| **TERMINAR AHORA** | `CLOSE_TCP` | `{ip: activeIncident.ip, action: "CLOSE_TCP", port: 443}` |
| **ACTIVAR ENCRIPTACIÓN** | (UI pendiente) | No conectado en v1.0 |

---

## 8. Flujo Completo — Escenario de Ataque

```
T+0s   simulation.py: Inicia ráfaga desde 192.168.1.47
       → Inserta 7 registros en traffic.db (is_processed=0)

T+1s   process_traffic_loop() despierta
       → Lee 7 registros no procesados
       → Para cada uno: ml_service.predict(features)
       → Resultado: "DDoS SYN Flood" con confianza=0.987
       
T+1s   ¿Confianza >= 0.95? SÍ
       → blocked_ips.add("192.168.1.47")
       → SecurityLog insertado en security_logs.db
       → Broadcast WebSocket: {is_alert: true, predicted_class: "DDoS SYN Flood"}

T+1s   Frontend Dashboard recibe mensaje WebSocket
       → Toast Error: "INGRESO SOSPECHOSO: DDoS SYN Flood desde 192.168.1.47"
       → Log aparece en terminal del Dashboard
       → Packet animado tipo "critical" en mapa de red

T+4s   MitigationZone llama GET /api/mitigation/suspicious
       → "192.168.1.47" ya fue auto-bloqueada → NO aparece en lista

T+5s   process_traffic_loop() vuelve a procesar
       → "192.168.1.47" está en blocked_ips
       → Skip (continuar sin procesar)
```

---

## 9. Seguridad en los Endpoints de Mitigación

Todos los endpoints de mitigación requieren autenticación JWT:

```python
@router.get("/suspicious")
def get_suspicious_ips(current_user = Depends(get_current_user)):
    # current_user es inyectado automáticamente por FastAPI
    # Si el token es inválido → HTTP 401 Unauthorized
    ...

@router.post("/block")
def block_ip(request, db, current_user = Depends(get_current_user)):
    # Solo usuarios autenticados pueden ejecutar mitigaciones
    ...
```

**Headers requeridos:**
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json
```

---

## 10. Whitelist de IPs Críticas (Pendiente — Sprint 2 Ext.)

> **Estado:** ⚠️ PENDIENTE DE IMPLEMENTACIÓN  

El plan de desarrollo contempla una whitelist estática para evitar bloquear IPs de infraestructura crítica (servidores DNS, gateways, IPs de administración).

```python
# Implementación pendiente en routers/mitigation.py
WHITELIST_IPS = {
    "192.168.1.1",    # Gateway principal
    "8.8.8.8",        # DNS Google
    "192.168.1.100",  # Servidor de administración
}

def should_block(ip: str) -> bool:
    return ip not in WHITELIST_IPS and ip not in blocked_ips
```

---

## 11. Modo Dry-Run (Pendiente — Sprint 2 Ext.)

> **Estado:** ⚠️ PENDIENTE DE IMPLEMENTACIÓN  

Para entornos donde se desea monitorear sin ejecutar bloqueos reales:

```python
# Variable de entorno a agregar
DRY_RUN = os.getenv("SMAR_IA_DRY_RUN", "false").lower() == "true"

# Modificar en process_traffic_loop()
if confidence >= 0.95:
    if DRY_RUN:
        action_taken = f"DRY-RUN: iptables -A INPUT -s {ip} -j DROP"
    else:
        # Ejecutar bloqueo real
        blocked_ips.add(ip)
        action_taken = f"AUTO-BLOCKED: iptables -A INPUT -s {ip} -j DROP"
```

---

## 12. Criterios de Aceptación del Sprint 2

| Criterio | Método de Verificación | Estado |
|----------|----------------------|--------|
| WebSocket transmite en tiempo real | Dashboard muestra nuevos logs sin recargar | ✅ |
| Múltiples clientes reciben el mismo mensaje | Abrir 2 tabs → ambos reciben broadcast | ✅ |
| Confianza ≥ 95% → auto-bloqueo | IP con conf>95% aparece en `blocked_ips` | ✅ |
| IP bloqueada no se vuelve a procesar | Loop hace `continue` para IPs en `blocked_ips` | ✅ |
| `POST /block` requiere JWT | Sin token → 401 Unauthorized | ✅ |
| Acción de bloqueo manual genera log | `security_logs.db` tiene registro con `iso_control="A.8.20"` | ✅ |
| IP bloqueada sale de lista sospechosos | `GET /suspicious` no retorna IPs en `blocked_ips` | ✅ |
| Toast de alerta en frontend | Ataque detectado → notificación visible en UI | ✅ |

---

*Sprint 2 — SMAR-IA — Universidad Continental*
