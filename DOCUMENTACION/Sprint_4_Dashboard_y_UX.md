# Sprint 4 — Dashboard y UX (Interfaz Gráfica)

> **Duración estimada:** 1.5 semanas  
> **Estado actual:** ✅ COMPLETADO  
> **Objetivo:** Desarrollar la interfaz web de monitoreo en vivo e histórico con estética "cyber-terminal" premium.

---

## 1. Objetivo General

Proporcionar al equipo DTI (Dirección de Tecnologías de la Información) de la Universidad Continental una interfaz visual profesional, intuitiva y en tiempo real para monitorear el estado de la red, gestionar incidentes y revisar el historial de eventos de seguridad.

Al finalizar este sprint debe ser posible:
- Autenticarse y acceder a un dashboard protegido.
- Ver el tráfico de red en tiempo real con animaciones de paquetes.
- Recibir notificaciones toast al detectar ataques.
- Gestionar incidentes desde la Zona de Mitigación.
- Consultar el historial completo de logs en una terminal interactiva.
- Navegar entre 5 secciones mediante un sidebar lateral.

---

## 2. Stack Frontend

| Tecnología | Versión | Propósito |
|-----------|---------|-----------|
| React | ^19.2.5 | Framework SPA principal |
| Vite | ^8.0.10 | Bundler y servidor de desarrollo |
| React Router DOM | ^7.14.2 | Enrutamiento SPA |
| React Bootstrap | ^2.10.10 | Componentes de layout (Row, Col, Badge) |
| Bootstrap | ^5.3.8 | Sistema de grilla base |
| Recharts | ^3.8.1 | Gráficos de barras (tendencias) |
| Lucide React | ^1.14.0 | Iconografía consistente |
| React Toastify | ^11.1.0 | Notificaciones de alertas |

---

## 3. Sistema de Diseño — Identidad Visual Cyber

### 3.1 Paleta de Colores

```css
/* Definida en frontend/src/index.css */

/* Fondo principal */
--bg-primary: #0a0d14         /* Negro azulado profundo */
--bg-secondary: #0d1117       /* Negro carbón */
--bg-card: rgba(13,17,23,0.8) /* Cards semi-transparentes */

/* Colores de acento */
--color-cyan: #00f0ff          /* Cyan neón — estado normal/info */
--color-pink: #ff0055          /* Rosa/rojo — alertas críticas */
--color-yellow: #f59e0b        /* Amarillo — advertencias */
--color-green: #00ff88         /* Verde — estado OK/nominal */

/* Tipografía */
font-family: 'Space Mono', monospace  /* Terminal aesthetic */
```

### 3.2 Componentes Visuales del Design System

| Componente CSS | Uso | Descripción |
|---------------|-----|-------------|
| `.cyber-widget` | Cards de información | Panel con borde cyan sutil, fondo oscuro |
| `.cyber-panel` | Paneles grandes | Similar a widget pero con más padding |
| `.cyber-progress` | Barras de progreso | Progreso estilizado con color neón |
| `.terminal-body` | Área de logs | Fuente monospace, scroll automático |
| `.btn-matrix-cyan` | Botones acción primaria | Botón con borde y glow cyan |
| `.btn-matrix-pink` | Botones acción crítica | Botón con borde y glow rosa |
| `.btn-matrix-yellow` | Botones acción media | Botón con borde y glow amarillo |
| `.packet` | Animación de paquetes | Partícula animada en el mapa de red |
| `.glow-ring` | Efecto de pulso | Anillo pulsante en el nodo central |
| `.scan-line` | Línea de escaneo | Animación de radar/scan |
| `.live-fade-in` | Entrada de logs | Animación fade + slide en nuevos logs |

### 3.3 Clases de Estado de Paquetes

```css
/* Paquetes animados en el mapa de red del Dashboard */
.packet.type-normal    /* Cyan — tráfico legítimo */
.packet.type-suspicious /* Amarillo — confianza media */
.packet.type-critical  /* Rosa — alta confianza de ataque */
.packet.type-burst     /* Rojo parpadeante — ráfaga detectada */
```

---

## 4. Arquitectura de Navegación

### 4.1 Enrutamiento — `App.jsx`

```jsx
function AppRoutes() {
  return (
    <Routes>
      {/* Ruta pública */}
      <Route path="/login" element={<Login />} />
      
      {/* Rutas protegidas — requieren JWT */}
      <Route path="/" element={
        <ProtectedRoute>
          <Layout />   {/* Sidebar permanente */}
        </ProtectedRoute>
      }>
        <Route index element={<Dashboard />} />          {/* / */}
        <Route path="traffic" element={<TrafficMonitor />} />   {/* /traffic */}
        <Route path="mitigation" element={<MitigationZone />} /> {/* /mitigation */}
        <Route path="settings" element={<Settings />} />        {/* /settings */}
        <Route path="logs" element={<Logs />} />               {/* /logs */}
      </Route>
    </Routes>
  );
}
```

### 4.2 Protección de Rutas

```jsx
const ProtectedRoute = ({ children }) => {
  const { token } = useContext(AuthContext);
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return children;
};
```

Si el token JWT no existe en el contexto → redirect automático a `/login`.

---

## 5. Gestión de Estado Global — `AuthContext`

### Archivo: `frontend/src/context/AuthContext.jsx`

Provee el token JWT y el estado de autenticación a todos los componentes:

```jsx
// Consumo en cualquier componente:
const { token } = useContext(AuthContext);

// Ejemplo en MitigationZone.jsx:
const res = await fetch('http://localhost:8000/api/mitigation/suspicious', {
  headers: { 'Authorization': `Bearer ${token}` }
});
```

---

## 6. Página de Login — `Login.jsx`

### 6.1 Descripción

Formulario de autenticación con estética cyber. Envía credenciales al endpoint `/api/auth/login` usando el formato `application/x-www-form-urlencoded` (requerido por OAuth2PasswordRequestForm de FastAPI).

### 6.2 Flujo de Autenticación

```
Usuario ingresa username + password
         ↓
POST /api/auth/login (form-data)
         ↓
Backend verifica bcrypt
         ↓
Retorna { access_token, token_type: "bearer" }
         ↓
AuthContext guarda el token
         ↓
Redirect → Dashboard (/)
```

---

## 7. Layout y Sidebar — `Layout.jsx`

### 7.1 Estructura del Layout

```
┌────────────────────────────────────────────────────────────┐
│  [SIDEBAR]              [MAIN CONTENT AREA]                │
│  ─────────              ────────────────────               │
│  🛡 SMAR-IA              <Outlet />                         │
│     IDS v1.0            (Dashboard / Traffic /             │
│                          MitigationZone / Logs /           │
│  ── Navegación ──        Settings)                         │
│  📊 Dashboard                                               │
│  📡 Tráfico                                                 │
│  🛡 Mitigación                                              │
│  📋 Logs                                                    │
│  ⚙️  Ajustes                                                │
│                                                             │
│  ── Sistema ──                                              │
│  🟢 Backend: ON                                             │
│  👤 admin                                                   │
│  [Cerrar Sesión]                                            │
└────────────────────────────────────────────────────────────┘
```

---

## 8. Dashboard Principal — `Dashboard.jsx`

### 8.1 Descripción General

El Dashboard es la vista principal del sistema. Combina datos en tiempo real (WebSocket) con datos históricos (REST API) y los presenta en un layout de 4 cuadrantes.

### 8.2 Estructura del Dashboard (Grid Layout)

```
┌─────────────────────────┬────────────────────┐
│  TRÁFICO DE RED EN VIVO │  ESTADO DEL SISTEMA │
│  (Col lg=8)             │  (Col lg=4)         │
│                         │  ─────────────────  │
│  [Mapa de red animado]  │  TEMP. NÚCLEO: 42°C │
│  • Nodo central         │  CARGA NEURONAL: 78%│
│  • 3 nodos origen       │  UPTIME: 452:12:04  │
│  • Líneas de conexión   │  ─────────────────  │
│  • Paquetes animados    │  AMENAZAS ACTIVAS   │
│                         │  04 ALERTA ALTA     │
│  Rendimiento: 1.2 TB/S  │  • DDOS: 89% MIT.   │
│  Nodos: 4,092           │  • API DESCONOCIDA  │
├─────────────────────────┼────────────────────┤
│  CONFIANZA IA           │  REGISTRO ACTIVIDAD │
│  (Col lg=4)             │  (Col lg=8)         │
│                         │                     │
│  [Gauge circular: 90%]  │  [Terminal de logs] │
│  "Patrones sugieren     │  [23:12:47] CRÍTICO │
│   movimiento lateral"   │  [23:12:46] NOMINAL │
└─────────────────────────┴────────────────────┘
```

### 8.3 Mapa de Red Animado

```jsx
{/* Nodo Central con anillo pulsante */}
<div className="node central">
  <Processor size={24} />
  <div className="glow-ring"></div>   {/* CSS pulse animation */}
</div>

{/* Nodos de origen fijos */}
<div className="node cyan pos-1"><Server size={12} /></div>   {/* Nodo 1: tráfico normal */}
<div className="node red pos-2"><Server size={12} /></div>    {/* Nodo 2: tráfico sospechoso */}
<div className="node yellow pos-3"><Server size={12} /></div> {/* Nodo 3: advertencias */}

{/* Líneas de conexión estáticas */}
<div className="connection-line line-1"></div>
<div className="connection-line line-2"></div>
<div className="connection-line line-3"></div>

{/* Paquetes dinámicos — generados por WebSocket */}
{packets.map(packet => (
  <div 
    key={packet.id} 
    className={`packet origin-${packet.origin} type-${packet.type}`}
  >
    <div className="packet-glow"></div>
  </div>
))}
```

### 8.4 Lógica de Clasificación Visual de Paquetes

```javascript
// Determinar tipo visual del paquete basado en datos del WebSocket
let type = 'normal';
if (ipCount > 3) type = 'burst';           // Ráfaga desde la misma IP
else if (data.is_alert) {
  type = data.confidence > 0.9 
    ? 'critical'    // Confianza alta → Rosa crítico
    : 'suspicious'; // Confianza media → Amarillo sospechoso
}
```

### 8.5 Sistema de Toasts para Alertas

```javascript
// Toastify configurado según nivel de amenaza
if (data.is_alert) {
  const toastType = data.confidence > 0.9 ? 'error' : 'warning';
  toast[toastType](
    `INGRESO SOSPECHOSO: ${data.predicted_class} desde ${data.source_ip}`,
    {
      position: "top-right",
      autoClose: 5000,
      theme: "dark",
      style: {
        border: data.confidence > 0.9 ? '1px solid #ff0055' : '1px solid #f59e0b',
        background: '#0d1117',
        fontFamily: "'Space Mono', monospace"
      }
    }
  );
}
```

---

## 9. Monitor de Tráfico — `TrafficMonitor.jsx`

### 9.1 Descripción

Página dedicada a la visualización detallada del tráfico de red en tiempo real. Complementa el Dashboard con tablas y gráficos más detallados del flujo de paquetes.

---

## 10. Zona de Mitigación — `MitigationZone.jsx`

### 10.1 Descripción General

Interfaz para que el operador de seguridad gestione incidentes activos. Muestra el perfil detallado del ataque más reciente y ofrece acciones de respuesta recomendadas por la IA.

### 10.2 Componentes Principales

#### Perfil de Incursión (Panel izquierdo — 7/12 columnas)
```jsx
<div className="cyber-panel incursion-profile">
  {/* Ícono de amenaza con animación de escaneo */}
  <Bug size={80} className="text-pink-glow" />
  <div className="scanning-line"></div>
  
  {/* Datos del incidente activo (desde API) */}
  <div className="detail-item">
    <span>NODO_ORIGEN</span>
    <span>{activeIncident?.ip || "192.168.1.104"}</span>
  </div>
  
  {/* Log de actividad del incidente */}
  <div className="terminal-log-area">
    <div className="log-line info">INICIALIZANDO INSPECCIÓN PROFUNDA...</div>
    <div className="log-line alert">ADVERTENCIA: INTENTO DE EJECUCIÓN</div>
    <div className="log-line blink">ESPERANDO DESPLIEGUE DE MITIGACIÓN...</div>
  </div>
</div>
```

#### Recomendaciones de la IA (Panel derecho — 5/12 columnas)

```jsx
{/* Recomendación 1: Aislamiento por Firewall */}
<div className="rec-card">
  <ShieldAlert size={24} />
  <h6>AISLAMIENTO POR FIREWALL</h6>
  <span>PROBABILIDAD ÉXITO: 94%</span>
  <button onClick={() => handleMitigate(activeIncident?.ip, "BLOCK_IP")}>
    EJECUTAR AISLAMIENTO
  </button>
</div>

{/* Recomendación 2: Terminar Conexión TCP:443 */}
<div className="rec-card">
  <Zap size={24} />
  <h6>TERMINAR CONEXIÓN</h6>
  <span>PROBABILIDAD ÉXITO: 100%</span>
  <button onClick={() => handleMitigate(activeIncident?.ip, "CLOSE_TCP", 443)}>
    TERMINAR AHORA
  </button>
</div>

{/* Recomendación 3: Encriptar Segmento (UI placeholder) */}
<div className="rec-card">
  <Lock size={24} />
  <h6>ENCRIPTAR SEGMENTO</h6>
  <span>PROBABILIDAD ÉXITO: 88%</span>
  <button className="btn-matrix-yellow">ACTIVAR ENCRIPTACIÓN</button>
</div>
```

### 10.3 Flujo de Mitigación Manual

```
Operador abre MitigationZone
         ↓
GET /api/mitigation/suspicious (cada 3s)
         ↓
Lista de IPs con ≥3 alertas en últimos 5min
         ↓
Primer incidente auto-seleccionado como activeIncident
         ↓
Operador hace clic en "EJECUTAR AISLAMIENTO"
         ↓
POST /api/mitigation/block 
  { ip, action: "BLOCK_IP", attack_type: "IA Recommended" }
         ↓
Backend: registra en security_logs.db (iso_control="A.8.20")
         ↓
blocked_ips.add(ip) → IP eliminada de lista sospechosos
         ↓
Toast: "Protocolo BLOCK_IP ejecutado con éxito"
         ↓
fetchSuspicious() → lista actualizada
```

---

## 11. Terminal de Logs — `Logs.jsx`

### 11.1 Descripción General

Página de auditoría que muestra un stream en tiempo real de todos los eventos del sistema en formato de terminal Unix.

### 11.2 Estructura de la Interfaz

```
┌─────────────────────────────────────────────────────────────┐
│  SYSTEM_LOG_STREAM                                          │
│  REAL-TIME NETWORK AUDIT & AI DECISION TELEMETRY           │
│  ● UPTIME: 142:12:05          FILTER: [ALL_EVENTS ▼]       │
├──────────────┬──────────────────────────────────────────────┤
│  STATS       │  ROOT@SMAR-IA: ~/_LOGS/LIVE_STREAM          │
│  ─────────   │  ● ● ●                          ⬇ ⤢         │
│  TOTAL/24H   │  ─────────────────────────────────────────  │
│  482,901     │  [23:12:47] [CRITICAL_ERR] UNAUTHORIZED...  │
│              │  [23:12:46] [NW_TRAFFIC] Inbound request... │
│  CRITICAL    │  [23:12:44] [SEC_AUDIT] Routine check...    │
│  12 (+4)     │  ...                                        │
│              │  _  WAITING FOR DATA PACKETS...             │
│  TOPOLOGY    │                                             │
│  Sub-7B      │  ● LIVE FEED  ○ VERBOSE MODE  LINES: 47    │
│              │                                             │
│  LOG CATS    │                                             │
│  ■ Network   │                                             │
│  ■ Security  │                                             │
│  ■ AI Logs   │                                             │
└──────────────┴──────────────────────────────────────────────┘
│ 🧠 4.2GB/32GB  🔥 64% CPU  ✅ Synced  🌐 1,024 Nodes       │
└─────────────────────────────────────────────────────────────┘
```

### 11.3 Formato de Entradas en el Log

```javascript
// Evento de ataque
{
  timestamp: "23:12:47",
  category: "CRITICAL_ERR",
  message: "DDoS SYN Flood detected from 192.168.1.47. Action: AUTO-BLOCKED",
  isCritical: true
}

// Evento normal
{
  timestamp: "23:12:46",
  category: "NW_TRAFFIC",
  message: "Inbound request from 192.168.1.133 handled by gateway.",
  isCritical: false
}
```

### 11.4 Filtros Disponibles

| Opción del Select | Descripción |
|------------------|-------------|
| `ALL_EVENTS` | Muestra todos los eventos (UI implementada, lógica pendiente) |
| `CRITICAL_ONLY` | Solo eventos de ataque (lógica pendiente) |
| `AI_LOGIC` | Solo decisiones del modelo ML (lógica pendiente) |

> **Nota:** La lógica de filtrado en el frontend está planificada para Sprint 5. La selección del select no filtra aún los resultados.

### 11.5 Categorías Visuales

```jsx
<span className={`log-cat ${
  log.category === 'CRITICAL_ERR' ? 'text-pink' : 'text-cyan'
}`}>
  [{log.category}]
</span>
```

| Categoría | Color | Origen |
|-----------|-------|--------|
| `CRITICAL_ERR` | Rosa (`#ff0055`) | Eventos de ataque |
| `NW_TRAFFIC` | Cyan (`#00f0ff`) | Tráfico normal |
| `SEC_AUDIT` | Cyan | Auditorías de seguridad |

---

## 12. Settings — `Settings.jsx`

### 12.1 Descripción

Panel de configuración del sistema que incluye:
- Configuración de umbrales de confianza para auto-bloqueo.
- Gestión de notificaciones.
- Configuración de retención de logs.
- Información del sistema.

---

## 13. Sistema de Notificaciones (React Toastify)

### Configuración Global en `App.jsx`

```jsx
<ToastContainer theme="dark" />
```

### Tipos de Notificación por Evento

| Evento | Tipo Toast | Estilo |
|--------|-----------|--------|
| Ataque con confianza > 90% | `toast.error()` | Borde rosa, fondo oscuro |
| Ataque con confianza 50-90% | `toast.warning()` | Borde amarillo, fondo oscuro |
| Mitigación exitosa | `toast.success()` | Verde, tema dark |
| Error de conexión | `toast.error()` | Rojo estándar |

---

## 14. Comunicación Frontend ↔ Backend

### 14.1 REST API Calls

| Componente | Endpoint | Método | Propósito |
|-----------|----------|--------|-----------|
| `Dashboard.jsx` | `/api/logs?limit=10` | GET | Logs iniciales |
| `Logs.jsx` | `/api/logs?limit=50` | GET | Historial completo |
| `MitigationZone.jsx` | `/api/mitigation/suspicious` | GET | IPs sospechosas |
| `MitigationZone.jsx` | `/api/mitigation/block` | POST | Ejecutar mitigación |
| `Login.jsx` | `/api/auth/login` | POST | Autenticación |

### 14.2 WebSocket

| Componente | Endpoint WS | Propósito |
|-----------|-------------|-----------|
| `Dashboard.jsx` | `ws://localhost:8000/ws` | Tráfico en vivo + animación |
| `Logs.jsx` | `ws://localhost:8000/ws` | Log stream en tiempo real |

### 14.3 Manejo de Ciclo de Vida WebSocket

```javascript
useEffect(() => {
  // Crear conexión al montar el componente
  ws.current = new WebSocket('ws://localhost:8000/ws');
  ws.current.onmessage = (event) => { /* procesar mensaje */ };
  
  // Limpiar (cerrar) conexión al desmontar
  return () => ws.current?.close();
}, []);  // Dependencia vacía = solo al montar/desmontar
```

---

## 15. Criterios de Aceptación del Sprint 4

| Criterio | Método de Verificación | Estado |
|----------|----------------------|--------|
| Login funcional con admin/admin123 | Ingresar credenciales → llegar al Dashboard | ✅ |
| Ruta protegida redirige al login | Acceder a `/` sin token → redirect a `/login` | ✅ |
| Dashboard muestra tráfico en vivo | Paquetes animados aparecen con cada evento WS | ✅ |
| Toast de alerta al detectar ataque | Ataque → notificación visible en esquina superior | ✅ |
| MitigationZone lista IPs sospechosas | IPs con ≥3 alertas/5min aparecen en la lista | ✅ |
| Botón "EJECUTAR AISLAMIENTO" funciona | Click → POST enviado → toast de éxito | ✅ |
| Logs page muestra historial + live | Logs históricos + nuevos eventos en tiempo real | ✅ |
| Sidebar navega entre 5 páginas | Cada enlace carga la página correspondiente | ✅ |
| Diseño cyber-theme consistente | Todas las páginas usan la paleta y tipografía definida | ✅ |

---

## 16. Comandos de Desarrollo Frontend

```bash
# Instalar dependencias
cd frontend
npm install

# Servidor de desarrollo (con hot reload)
npm run dev
# → Acceso: http://localhost:5173

# Verificar lint
npm run lint

# Build de producción
npm run build
# → Genera: frontend/dist/
```

---

*Sprint 4 — SMAR-IA — Universidad Continental*
