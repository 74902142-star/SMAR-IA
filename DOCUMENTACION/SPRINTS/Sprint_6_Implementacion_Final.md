# 🚀 Sprint 6: Implementación Final y Despliegue en Producción (IDS/IPS)

Este documento describe la fase final de integración, empaquetado, despliegue en producción y pruebas operativas del sistema **SMAR-IA** (Sistema de Detección y Mitigación de Intrusiones). Basado en los estados del arte revisados (en particular, la arquitectura de mitigación preventiva en origen propuesta por *DDoSBlocker*, 2025), implementamos un esquema de despliegue en producción que desacopla la detección heurística y la mitigación activa por iptables, garantizando el cumplimiento de la norma **ISO/IEC 27001:2022**.

---

## 🏗️ 1. Arquitectura de Despliegue de Producción

Para evitar la sobrecarga y saturación del plano de control del sistema (desafío identificado en los estados del arte sobre seguridad SDN), la arquitectura de despliegue de **SMAR-IA** separa el flujo de telemetría del motor de toma de decisiones en tres capas operativas:

```
                  ┌──────────────────────────────────────────────┐
                  │                 RED EXTREMA                  │
                  └──────────────────────┬───────────────────────┘
                                         │
                                         ▼ (Inspección en Origen)
                  ┌──────────────────────────────────────────────┐
                  │        Plano de Datos (Switches / Host)       │
                  │   - Reglas de filtrado iptables (Bloqueo L3)  │
                  └──────────────────────┬───────────────────────┘
                                         │
                   (Packet-In / Telemetría)▲ (Instalación de Reglas)
                                         │
                  ┌──────────────────────▼───────────────────────┐
                  │          Plano de Control (Backend FastAPI)   │
                  │   - Validador de firma temporal de tramas     │
                  │   - Clasificación por XGBoost + Random Forest │
                  └──────────────────────┬───────────────────────┘
                                         │
                                         ▼ (Visualización)
                  ┌──────────────────────────────────────────────┐
                  │        Plano de Gestión (React Frontend)     │
                  │   - Monitorización y control de políticas     │
                  └──────────────────────────────────────────────┘
```

### 🧠 Lecciones del Estado del Arte (DDoSBlocker, 2025)
* **Bloqueo en el Origen:** Las reglas de bloqueo por IP se aplican directamente en las cadenas del firewall del host que recibe el tráfico (`INPUT`/`FORWARD` de iptables) para prevenir que la inundación de paquetes anómalos congestione la cola del socket del servidor de aplicación de la API o del controlador.
* **Filtro Temporal de Tramas:** Se integra un umbral de rate-limiting rápido en la capa de red del backend para descartar ráfagas de peticiones idénticas de la misma IP origen que no varíen su firma temporal, bloqueando de forma inmediata ráfagas de spoofing L2/L3.

---

## 🔧 2. Pasos de Instalación y Configuración del Servidor

### Requisitos Previos (Ubuntu Server 22.04 LTS / Debian 12)
Instalar paquetes base para la captura, encriptación y firewall de red:
```bash
sudo apt update && sudo apt install -y python3-pip python3-venv nginx iptables-persistent git nodejs npm
```

### Paso A: Configuración y Clonación del Repositorio
1. Clonar el repositorio y acceder a la carpeta del proyecto:
   ```bash
   git clone https://github.com/74902142-star/SMAR-IA.git
   cd SMAR-IA
   ```

2. Configurar las variables del entorno de producción creando el archivo `backend/.env`:
   ```ini
   SMAR_IA_SECRET_KEY="SU_CLAVE_JWT_SECRETA_Y_SEGURA"
   SMAR_IA_ADMIN_PASSWORD="Contraseña_Segura_Administrador_Prod"
   SMAR_IA_DRY_RUN=false
   SMAR_IA_CORS_ORIGINS="http://localhost,http://127.0.0.1"
   VITE_API_BASE_URL="http://localhost:8000"
   ```

### Paso B: Despliegue del Backend (FastAPI + Uvicorn)
1. Configurar el entorno virtual e instalar dependencias del core y del pipeline ML:
   ```bash
   cd backend
   python3 -m venv .venv
   source .venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

2. Configurar la base de datos local de control ISO A.8.15 y aplicar el script inicial:
   ```bash
   python -c "from database import Base, engine; Base.metadata.create_all(bind=engine)"
   ```

3. Crear el servicio de Systemd para mantener el backend en ejecución constante en segundo plano (`/etc/systemd/system/smaria-backend.service`):
   ```ini
   [Unit]
   Description=SMAR-IA FastAPI Backend Service
   After=network.target

   [Service]
   User=root
   WorkingDirectory=/Users/johnsmith/Downloads/UNIVERSIDAD CONTINENTAL/Sistema IDS/SmarIA/backend
   ExecStart=/Users/johnsmith/Downloads/UNIVERSIDAD CONTINENTAL/Sistema IDS/SmarIA/backend/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
   Restart=always
   Environment=PYTHONUNBUFFERED=1

   [Install]
   WantedBy=multi-user.target
   ```

4. Habilitar e iniciar el backend:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable smaria-backend
   sudo systemctl start smaria-backend
   ```

### Paso C: Construcción y Servido del Frontend (React + Nginx)
1. Acceder a la carpeta del frontend, instalar módulos e inicializar la build estática optimizada para producción:
   ```bash
   cd ../frontend
   npm install
   npm run build
   ```

2. Configurar el archivo de distribución de Nginx `/etc/nginx/sites-available/smaria` para servir los activos estáticos del frontend y redirigir las conexiones REST y WebSocket al backend de FastAPI:
   ```nginx
   server {
       listen 80;
       server_name localhost;

       # Frontend estático de React
       location / {
           root /Users/johnsmith/Downloads/UNIVERSIDAD CONTINENTAL/Sistema IDS/SmarIA/frontend/dist;
           try_files $uri $uri/ /index.html;
       }

       # Proxificación a la API del Backend
       location /api/ {
           proxy_pass http://127.0.0.1:8000/api/;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       }

       # Proxificación a WebSockets (Telemetría en Vivo)
       location /ws {
           proxy_pass http://127.0.0.1:8000/ws;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "Upgrade";
           proxy_set_header Host $host;
       }
   }
   ```

3. Activar el sitio y reiniciar Nginx:
   ```bash
   sudo ln -s /etc/nginx/sites-available/smaria /etc/nginx/sites-enabled/
   sudo systemctl restart nginx
   ```

---

## 🔒 3. Políticas de Mitigación y Reglas de iptables

En consonancia con el control **ISO/IEC 27001:2022 A.8.20** (Seguridad en redes) y los patrones automatizados de mitigación del estado del arte, el sistema ejecuta las siguientes acciones al detectar flujos anómalos:

1. **Aislamiento por Firewall (Descarte inmediato):**
   Añade una regla de descarte en la parte superior de la cadena INPUT del sistema:
   ```bash
   iptables -I INPUT -s [IP_ATACANTE] -j DROP
   ```
2. **Registro de la Acción (Control A.8.15):**
   La base de datos registra la firma y los metadatos del bloqueo en `security_logs.db` con control de hash SHA-256 en las cabeceras para evitar alteración o borrado malicioso de la auditoría.
3. **Expiración de la Regla (Mitigación Efímera):**
   El backend mantiene un hilo temporizado encargado de purgar y remover las reglas obsoletas para evitar la saturación de la tabla de flujos de iptables:
   ```bash
   iptables -D INPUT -s [IP_ATACANTE] -j DROP
   ```

---

## 🧪 4. Plan de Verificación en Producción

### Escenario A: Ataque DDoS Simulado (UDP/SYN Flood)
1. Ejecutar un ataque simulado desde el plano de pruebas del simulador integrado:
   ```bash
   cd backend
   python simulation.py --attack ddos_udp
   ```
2. **Criterio de Aceptación:**
   * La interfaz de *Detección de Amenazas* (`MitigationZone.jsx`) debe cambiar a estado de alerta crítica en menos de 3 segundos (umbral de DDoSBlocker).
   * La regla de iptables correspondiente al flujo malicioso se debe autogenerar.
   * El tráfico legítimo proveniente de otras IPs no debe verse afectado.

### Escenario B: Prueba de Carga del Firewall (Estrés de Reglas)
* Validar que el servicio de purga automática remueve con éxito las mitigaciones vencidas una vez transcurrido el tiempo configurado de expiración de las reglas dinámicas, manteniendo limpia la tabla de flujos del host.

---

*SMAR-IA — Universidad Continental | Documentación de Iteración de Producción*
