# 🔒 Plan de Pruebas de Seguridad y Cumplimiento — SmarIA

Este documento define la metodología de pruebas para validar los mecanismos de endurecimiento (hardening) del sistema y verificar el cumplimiento de la norma internacional **ISO/IEC 27001:2022**.

---

## 1. Controles ISO/IEC 27001:2022 Evaluados

* **A.8.15 (Registro de Actividades):** Verificación de que cada alteración, alerta o mitigación se almacene con firma de hash SHA-256 no repudiable.
* **A.8.16 (Actividades de Monitoreo):** Confirmación de que el flujo de eventos se transmita de forma íntegra por sockets autenticados.
* **A.8.20 (Seguridad en Redes):** Inspección de la inyección y liberación correcta de reglas en el firewall del sistema operativo.

---

## 2. Casos de Prueba de Seguridad

### Caso de Prueba PS-01: Intentos de Inyección de Código (Caja Blanca)
* **Objetivo:** Asegurar que la inserción de reglas dinámicas por parte de administradores no permita la ejecución de comandos no autorizados en el servidor.
* **Entradas de Ataque:** Inserción de la regla con condición:
  `"__import__('os').system('rm -rf /')"`
* **Procedimiento:**
  - Enviar petición POST a `/api/rules/` con la condición anterior.
* **Resultados Esperados:**
  - El sistema detecta y sanitiza la entrada mediante el parser AST.
  - La petición es rechazada de manera segura y no se ejecuta ninguna operación en el sistema de archivos del servidor.

### Caso de Prueba PS-02: Evitación de Falsos Positivos de Infraestructura
* **Objetivo:** Verificar que las IPs de la lista blanca (whitelist) no sean bloqueadas bajo ninguna circunstancia de tráfico anómalo.
* **Entrada:** IP `192.168.1.1` (servidor DNS del campus) en la lista de Whitelist.
* **Resultado Esperado:** Al recibir tráfico de simulación de ataque DDoS desde esta IP, el sistema escribe una auditoría especial "WHITELIST_HIT" y elude por completo la instalación de la regla de bloqueo.
