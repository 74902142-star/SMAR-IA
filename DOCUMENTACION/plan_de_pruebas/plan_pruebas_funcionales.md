# ⚙️ Plan de Pruebas Funcionales (Caja Negra) — SmarIA

Este documento describe los casos de prueba funcionales destinados a validar la interfaz gráfica y los flujos expuestos del API del sistema SmarIA desde la perspectiva de un analista de seguridad.

---

## 1. Casos de Prueba Funcionales

### Caso de Prueba PF-01: Autenticación y Control de Accesos
* **Componente:** `Login.jsx` / `/api/auth/login`
* **Entradas:**
  - Caso Correcto: `admin` / `admin123`
  - Caso Incorrecto: `admin` / `clave_invalida`
* **Procedimiento:**
  1. Ingresar credenciales en la UI.
  2. Presionar el botón "Acceder".
* **Resultados Esperados:**
  - Caso Correcto: Redirección instantánea al Dashboard principal.
  - Caso Incorrecto: Ventana emergente (Toast) que indica "Credenciales incorrectas" con código `401 Unauthorized` de la API.

### Caso de Prueba PF-02: Bloqueo Manual de IP
* **Componente:** `MitigationZone.jsx` -> Inspector de Anomalías
* **Entradas:** Clic en botón "Iniciar Bloqueo Total" para el flujo de la IP `192.168.1.100`.
* **Procedimiento:**
  1. Navegar a la pestaña "Detección de Amenazas".
  2. Seleccionar la IP sospechosa en la lista.
  3. Hacer clic en "Iniciar Bloqueo Total".
* **Resultados Esperados:**
  - Mensaje Toast confirmando la mitigación.
  - La IP se añade dinámicamente a la tabla de bloqueos y se inyecta la regla de descarte en el firewall del sistema operativo.
