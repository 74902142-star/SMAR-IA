# 🧩 Plan de Pruebas de Integración — SmarIA

Este documento detalla el plan de pruebas para evaluar la interacción e integración de los componentes del backend, frontend, base de datos y modelo de Machine Learning.

---

## 1. Topología del Flujo de Datos

```
[Red / Simulación] ──▶ [Captura de Flujos] ──▶ [FastAPI / Inferencia ML]
                                                    │
                   ┌────────────────────────────────┴────────────────┐
                   ▼ (WebSocket)                                     ▼ (SQLAlchemy)
           [React Frontend]                                  [security_logs.db]
```

---

## 2. Casos de Prueba de Integración

### Caso de Prueba PI-01: Ciclo Completo de Detección y Notificación
* **Componentes Involucrados:** `simulation.py` -> Backend FastAPI -> WebSocket -> Frontend React (`Dashboard.jsx` / `Logs.jsx`).
* **Procedimiento:**
  1. Iniciar la base de datos y arrancar el backend FastAPI en el puerto 8000.
  2. Abrir la consola de control React en el navegador.
  3. Ejecutar el simulador de tráfico: `python simulation.py --attack scan`.
* **Resultados Esperados:**
  - El backend captura las anomalías, las procesa a través del servicio de ML y las etiqueta como "Port Scan" con su correspondiente puntuación de confianza.
  - El backend inserta un registro en la base de datos de auditoría.
  - La alerta se transmite de forma instantánea mediante el canal de WebSockets al frontend, actualizando el gráfico de throughput y la terminal en vivo de logs sin recargar la página.

### Caso de Prueba PI-02: Transacción de Reglas Dinámicas a Firewall
* **Componentes Involucrados:** `RuleManager.jsx` -> API Endpoint (`rules.py`) -> SQLAlchemy (Rule) -> main.py (`process_traffic_loop`) -> `firewall.py`.
* **Resultados Esperados:**
  - La creación de una regla dinámica en la interfaz se guarda correctamente en la base de datos.
  - El ciclo de procesamiento del backend detecta la nueva regla y la aplica sobre el tráfico entrante inyectando comandos de red eficaces en el firewall del servidor.
