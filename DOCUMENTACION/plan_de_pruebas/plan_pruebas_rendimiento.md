# 📈 Plan de Pruebas de Rendimiento y Estrés — SmarIA

Este documento describe la metodología y los casos de prueba aplicados para certificar la velocidad, estabilidad y consumo de recursos de la plataforma bajo cargas extremas.

---

## 1. Métricas Clave de Rendimiento (KPIs)

* **Tiempo de Inferencia Neural (ML Latency):** Tiempo de cómputo empleado por el modelo Random Forest para evaluar un flujo preprocesado de red.
  - *Límite Máximo Aceptable:* 5 ms.
  - *Objetivo de Diseño:* < 3 ms.
* **Tiempo de Mitigación del Firewall:** Tiempo que transcurre desde la detección de una anomalía hasta que la regla de iptables es activada de forma efectiva.
  - *Límite Máximo Aceptable:* 3.5 segundos.
  - *Objetivo de Diseño:* < 1.5 segundos.

---

## 2. Pruebas de Estrés y Carga

### Caso de Prueba PR-01: Inundación Masiva de Paquetes
* **Objetivo:** Asegurar que el backend no colapse o sufra fugas de memoria ante ataques DDoS masivos de inundación.
* **Entrada:** Ataque simulado a través del host generador de tráfico:
  ```bash
  hping3 --flood --udp -p 80 [IP_SERVIDOR]
  ```
* **Régimen Evaluado:** 50,000 paquetes por segundo (PPS) concurrentes durante 15 minutos continuos.
* **Resultados Esperados:**
  - El uso de la CPU del servidor del backend de FastAPI no supera el 85%.
  - La memoria RAM se mantiene estable por debajo de 220 MB (sin fugas acumulativas).
  - Los eventos del WebSocket siguen transmitiéndose en tiempo real.
