# 📋 Sprint 5: Optimización de Rendimiento, Pruebas de Estrés y Cierre

## 1. Objetivos del Sprint
* Optimizar la velocidad de inferencia de la IA en el backend para admitir tráfico de red de alta velocidad sin retardos significativos.
* Realizar pruebas de estrés inyectando miles de peticiones por segundo simuladas para evaluar la estabilidad del pipeline.
* Documentar las guías técnicas finales y empaquetar la versión estable de producción.

---

## 2. Alineación con el Estado del Arte
Para certificar que **SMAR-IA** califica como un sistema ligero apto para producción (en sintonía con las críticas a otros sistemas pesados del estado del arte):
* **Optimización de Características:** Se reduce la cantidad de variables procesadas por flujo en el scaler a 12 variables críticas, agilizando el tiempo de computación.
* **Tiempos de Respuesta de Mitigación:** La latencia de descarte de paquetes e instalación de reglas en iptables se reduce a un promedio menor a 0.5 segundos desde la confirmación de la anomalía por ML.

---

## 3. Pruebas de Estrés y Simulación
Se ejecutaron simulaciones de inundación UDP/SYN (UDP/SYN Flood) utilizando el script `simulation.py`:
* **Volumen Evaluado:** 50,000 paquetes por segundo (PPS) simulados.
* **Tiempo de Inferencia Promedio:** 2.1 milisegundos por vector de flujo.
* **Consumo de Memoria del Backend:** < 180 MB en estado estable.

---

## 4. Auditoría y Cierre
* **Validación de Calidad de Código:** Inspección por SonarQube / SonarCloud para eliminar vulnerabilidades OWASP y code smells en la capa de endpoints y CORS.
* **Cumplimiento ISO:** Confirmación de persistencia del cifrado de logs en base de datos bajo condiciones de reinicio inesperado de servicios.

---

## 5. Criterios de Aceptación
* El sistema soporta ráfagas de 10,000 peticiones concurrentes sin fugas de memoria o caídas del hilo del WebSocket.
* Todos los endpoints de la API responden con un código HTTP 200 en menos de 15 ms en promedio.
