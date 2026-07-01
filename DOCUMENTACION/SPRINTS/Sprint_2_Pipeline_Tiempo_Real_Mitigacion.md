# 📋 Sprint 2: Pipeline en Tiempo Real y Mitigación Dinámica

## 1. Objetivos del Sprint
* Diseñar e implementar el canal de comunicación en tiempo real para transmitir flujos de red clasificados mediante **WebSockets**.
* Implementar el motor de mitigación activa mediante llamadas al subsistema **iptables** del kernel Linux.
* Desarrollar un simulador de tráfico de red para pruebas continuas sin necesidad de un entorno SDN físico.

---

## 2. Alineación con el Estado del Arte
Inspirándonos en el módulo de detección y mitigación preventiva de *DDoSBlocker* (2025):
* **Triggering-based Activation:** El motor de inferencia de IA se activa automáticamente cuando se detecta un volumen anómalo de flujos de red entrantes, evitando el consumo continuo e innecesario de ciclos de CPU.
* **Bloqueo en el Origen (Host/VLAN):** Al confirmarse la firma del ataque mediante la predicción de alta confianza de ML (>90%), el backend de FastAPI ejecuta una regla de descarte en el firewall local (iptables) para mitigar el ataque antes de congestionar las capas superiores de servicio.

---

## 3. Lógica de Mitigación en FastAPI
En `backend/routers/mitigation.py` se exponen los endpoints para el control y ejecución del bloqueo:

```python
import subprocess
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter()

def block_ip_system(ip_address: str):
    # Comando de inserción en la parte superior del firewall de Linux
    cmd = ["sudo", "iptables", "-I", "INPUT", "-s", ip_address, "-j", "DROP"]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        raise OSError(f"iptables error: {result.stderr.decode()}")
```

### Modo Simulación (Dry-Run)
Para desarrollo en entornos macOS/Windows sin iptables, el archivo `.env` permite activar `SMAR_IA_DRY_RUN=true`, simulando los bloqueos en memoria sin lanzar comandos del kernel.

---

## 4. Iniciar Simulador de Tráfico
Para realizar pruebas operativas, se ejecuta el simulador integrado en una terminal independiente:
```bash
cd backend
source .venv/bin/activate
python simulation.py
```
El simulador genera flujos benignos e inyecta ataques (UDP Floods, Port Scans, etc.) a intervalos aleatorios, transmitiendo la telemetría en tiempo real por WebSocket.

---

## 5. Criterios de Aceptación
* El canal de WebSockets envía la telemetría de flujos de paquetes clasificados al frontend en menos de 100 ms tras su lectura.
* Al presionar "Bloquear" o dispararse el bloqueo autónomo, se inserta la regla en iptables y se confirma en la base de datos local.
