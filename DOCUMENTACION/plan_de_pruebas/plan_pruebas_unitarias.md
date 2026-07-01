# 🧪 Plan de Pruebas Unitarias — SmarIA

Este documento define las directrices y casos de prueba para evaluar los componentes y funciones del sistema de forma aislada, garantizando su correcto comportamiento lógico e inmunidad a entradas corruptas.

---

## 1. Estrategia y Cobertura de Pruebas
Las pruebas unitarias se ejecutan utilizando el framework **pytest** en el backend. El objetivo es asegurar una cobertura mínima del 80% en los módulos de lógica de negocios:
* **Evaluador de Reglas Dinámicas (`main.py` -> `evaluate_condition`)**
* **Módulo de Tokenización y Cifrado (`auth.py`)**
* **Preprocesamiento del ML Service (`ml_service.py`)**

---

## 2. Casos de Prueba Detallados

### Caso de Prueba PU-01: Validación de Reglas AST Seguras
* **Componente:** `main.py` -> `evaluate_condition`
* **Método de Prueba:** Caja Blanca (inspección de ramificaciones).
* **Entradas de Prueba:**
  1. `"confidence > 0.90"` (Válido)
  2. `"ip == '192.168.1.1' and attack_type == 'DDoS'"` (Válido)
  3. `"__import__('os').system('rm -rf /')"` (Intento de inyección)
* **Resultados Esperados:**
  - El parser AST procesa exitosamente las entradas 1 y 2 retornando un booleano coherente con el contexto.
  - La entrada 3 levanta una excepción controlada internamente y retorna `False` sin ejecutar código del sistema operativo.

### Caso de Prueba PU-02: Generación de JWT y RBAC
* **Componente:** `auth.py` -> `create_access_token`
* **Entradas de Prueba:** Diccionario de sesión conteniendo `sub` (username) y `role` (admin/viewer).
* **Resultados Esperados:**
  - Emisión de un string firmado criptográficamente en formato HS256.
  - El token decodificado coincide exactamente con el payload original de roles de usuario.
