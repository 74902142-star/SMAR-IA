# 📋 Plan Integral de Pruebas — SmarIA

Este directorio contiene la estructura del Plan de Pruebas del sistema de detección y mitigación de intrusiones **SmarIA** (NIDS/NIPS). Cada componente y tipo de prueba se encuentra documentado de manera independiente para facilitar su auditoría y mantenimiento continuo.

---

## 🗂️ Estructura del Plan de Pruebas

* **[README_PLAN_PRUEBAS.md](./README_PLAN_PRUEBAS.md)**: Guía maestra, alcance, entorno y requisitos de hardware.
* **[plan_pruebas_unitarias.md](./plan_pruebas_unitarias.md)**: Estrategia de pruebas unitarias sobre los algoritmos del backend y componentes individuales.
* **[plan_pruebas_funcionales.md](./plan_pruebas_funcionales.md)**: Pruebas de caja negra sobre la interfaz de usuario de React y flujos de API.
* **[plan_pruebas_integracion.md](./plan_pruebas_integracion.md)**: Pruebas de flujo de datos extremo a extremo (Full-Stack Data Flow).
* **[plan_pruebas_rendimiento.md](./plan_pruebas_rendimiento.md)**: Pruebas de velocidad de inferencia de IA, latencia de bloqueo y pruebas de estrés.
* **[plan_pruebas_seguridad.md](./plan_pruebas_seguridad.md)**: Validación de controles ISO/IEC 27001:2022 y resistencia a inyección de código.
* **[matriz_plan_pruebas.csv](./matriz_plan_pruebas.csv)**: Matriz general de trazabilidad de los casos de prueba.

---

## 💻 Requisitos de Hardware y Software de Pruebas

### 1. Entorno del Servidor
* **Procesador:** Intel Core i7 o equivalente (mínimo 4 núcleos).
* **Memoria RAM:** 16 GB DDR4.
* **Almacenamiento:** SSD NVMe M.2 con al menos 10 GB libres.
* **Sistema Operativo:** Ubuntu Server 22.04 LTS (o kernel de Linux compatible con iptables/nftables).

### 2. Entorno del Cliente y Generación de Tráfico
* **Generación de Tráfico:** `hping3` y Scapy (Python 3).
* **Cliente de Visualización:** Navegadores modernos Chrome/Firefox con DevTools.
