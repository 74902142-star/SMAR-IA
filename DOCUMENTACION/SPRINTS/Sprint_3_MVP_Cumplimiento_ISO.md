# 📋 Sprint 3: MVP y Cumplimiento de Controles ISO/IEC 27001:2022

## 1. Objetivos del Sprint
* Asegurar que el sistema **SMAR-IA** cumple con las especificaciones de seguridad y auditoría requeridas para entornos corporativos.
* Implementar registro estructurado de eventos en formato JSON y base de datos con control criptográfico (SHA-256).
* Mapear y validar los controles del estándar internacional de seguridad de la información **ISO/IEC 27001:2022**.

---

## 2. Alineación con el Estado del Arte
La auditoría y validación de decisiones tomadas de forma autónoma por la IA es un pilar fundamental en la documentación de seguridad de redes SDN moderna.
* **Integridad Criptográfica:** Cada registro de log de seguridad guardado en `security_logs.db` contiene un hash SHA-256 calculated a partir del timestamp, IP, tipo de ataque y la firma del registro anterior, evitando ataques de manipulación o inyección de logs falsos.

---

## 3. Mapeo de Controles ISO/IEC 27001:2022

| Control ISO | Definición | Implementación en SMAR-IA |
|---|---|---|
| **A.8.15** | Registro de actividades | Base de datos `security_logs.db` almacena cada intento de intrusión, anomalía y acción tomada con firma criptográfica. |
| **A.8.16** | Actividades de monitoreo | Telemetría WebSocket continua y almacenamiento histórico de logs con metadatos extendidos. |
| **A.8.20** | Seguridad en redes | Reglas automáticas en el firewall iptables aplicadas a nivel de flujo de red L3 con registro de control explícito. |

---

## 4. Estructura de Registro de Auditoría (A.8.15)
Los eventos se almacenan con la siguiente estructura de datos en SQLAlchemy:
```python
class SecurityLog(Base):
    __tablename__ = 'security_logs'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    source_ip = Column(String(50))
    destination_ip = Column(String(50))
    attack_type = Column(String(50))
    confidence = Column(Float)
    action_taken = Column(String(100))
    hash_checksum = Column(String(64))  # Hash SHA-256 de integridad
```

---

## 5. Criterios de Aceptación
* Cada llamada al motor de mitigación registra un log con control ISO específico.
* Intentos de alteración de logs son detectados inmediatamente mediante la invalidación de la firma hash de la cadena de auditoría.
