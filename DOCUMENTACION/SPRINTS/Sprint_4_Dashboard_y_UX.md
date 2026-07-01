# 📋 Sprint 4: Dashboard Principal y Experiencia de Usuario (UX)

## 1. Objetivos del Sprint
* Diseñar e implementar la interfaz gráfica de usuario en tiempo real utilizando **React 19** y **Vite 8**.
* Integrar gráficos y mapas interactivos que faciliten la rápida visualización de eventos de red y telemetría de IA.
* Asegurar un diseño responsivo y premium que maximice la eficiencia operativa de los analistas de seguridad.

---

## 2. Alineación con el Estado del Arte
La interfaz visual de **SMAR-IA** traduce la complejidad de las métricas de clasificación heurística en paneles de control intuitivos:
* **Visualización Dinámica:** En lugar de desplegar texto plano, los datos de precisión de la IA se muestran mediante diales radiales y matrices de confusión de 2x2.
* **Mapa de Topología del Campus:** Representación espacial en origen de los hosts comprometidos (Ala Admin, Laboratorio Biblioteca, Ala I+D) con flujos coloreados por nivel de carga (Carga Alta, Media, Nominal).

---

## 3. Arquitectura del Frontend
La estructura del cliente React consta de los siguientes módulos clave:
* **[Layout.jsx](file:///Users/johnsmith/Downloads/UNIVERSIDAD%20CONTINENTAL/Sistema%20IDS/SmarIA/frontend/src/pages/Layout.jsx):** Barra de navegación lateral persistente con la información y credenciales de sesión del operador de turno.
* **[Dashboard.jsx](file:///Users/johnsmith/Downloads/UNIVERSIDAD%20CONTINENTAL/Sistema%20IDS/SmarIA/frontend/src/pages/Dashboard.jsx):** Vista unificada del campus que integra las KPI Cards de flujo de red, gráficos de barra del throughput, lista de alertas críticas y el mapa topológico del campus.
* **[TrafficMonitor.jsx](file:///Users/johnsmith/Downloads/UNIVERSIDAD%20CONTINENTAL/Sistema%20IDS/SmarIA/frontend/src/pages/TrafficMonitor.jsx):** Muestra el gráfico en tiempo real de los principales emisores de ancho de banda y la tabla detallada de flujos activos.
* **[MitigationZone.jsx](file:///Users/johnsmith/Downloads/UNIVERSIDAD%20CONTINENTAL/Sistema%20IDS/SmarIA/frontend/src/pages/MitigationZone.jsx):** Panel de control interactivo para ejecutar bloqueos manuales y visualizar el estado del nodo comprometido.

---

## 4. Tecnologías de Visualización Empleadas
* **Recharts:** Usado para renderizar gráficos de barras del flujo interno del campus y mapas de calor históricos.
* **Lucide React:** Colección de iconos vectoriales interactivos para representar de forma semántica dispositivos, umbrales y tipos de alerta.

---

## 5. Criterios de Aceptación
* El frontend responde de forma fluida a las actualizaciones del WebSocket del backend.
* El diseño se adapta perfectamente a resoluciones móviles y pantallas de monitoreo de centros de operaciones de seguridad (SOC).
