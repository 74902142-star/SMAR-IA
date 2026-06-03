"""
SMAR-IA — Logger de auditoría con integridad criptográfica (ISO 27001 A.8.15)
=======================================================================
Genera archivos JSON rotados diariamente con hash SHA-256 de integridad.

Formato por evento (Anexo E de la tesis):
{
    "event_id": "uuid",
    "timestamp": "ISO-8601",
    "event_type": "INTRUSION_MITIGATED | BLOCK_ADDED | BLOCK_REMOVED | WHITELIST_HIT",
    "network": {
        "source_ip": "...",
        "destination_ip": "..."
    },
    "detection": {
        "model_confidence": 0.98,
        "attack_type": "...",
        "latency_ms": 12.34
    },
    "response": {
        "mitigation_latency_ms": 12.34,
        "action_taken": "..."
    },
    "iso_compliance": {
        "controls_activated": ["A.8.15", "A.8.20"]
    },
    "log_integrity_hash": "sha256=..."
}
"""
import json
import hashlib
import logging
import os
import uuid
from datetime import datetime, timezone

logger = logging.getLogger("smar-ia-audit")

LOGS_DIR = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(LOGS_DIR, mode=0o750, exist_ok=True)


def _get_log_path(date_str: str = None) -> str:
    if not date_str:
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return os.path.join(LOGS_DIR, f"audit_{date_str}.json")


def _serialize_safe(obj):
    """Serializa objetos no estándar de forma segura para el hash de integridad."""
    if isinstance(obj, (bytes, bytearray)):
        return obj.hex()
    raise TypeError(f"Tipo no serializable: {type(obj).__name__}")


def _compute_hash(event: dict) -> str:
    serialized = json.dumps(event, sort_keys=True, default=_serialize_safe)
    return "sha256=" + hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def write_audit_log(event_data: dict):
    """
    Escribe un evento de auditoría en el archivo JSON diario.
    Añade event_id, timestamp ISO y hash de integridad SHA-256.
    """
    event = {
        "event_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
        **event_data,
    }
    event["log_integrity_hash"] = _compute_hash(event)

    log_path = _get_log_path()
    try:
        with open(log_path, "a") as f:
            f.write(json.dumps(event, default=_serialize_safe) + "\n")
    except IOError as e:
        logger.error("Error escribiendo log de auditoría: %s", e)

    return event


def read_audit_logs(date_str: str = None) -> list:
    """Lee todos los eventos de auditoría para una fecha."""
    log_path = _get_log_path(date_str)
    if not os.path.exists(log_path):
        return []
    events = []
    try:
        with open(log_path, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    events.append(json.loads(line))
    except (IOError, json.JSONDecodeError) as e:
        logger.error("Error leyendo log de auditoría: %s", e)
    return events


def get_available_dates() -> list:
    """Lista las fechas para las que existen archivos de auditoría."""
    dates = []
    if not os.path.isdir(LOGS_DIR):
        return dates
    for fname in os.listdir(LOGS_DIR):
        if fname.startswith("audit_") and fname.endswith(".json"):
            date_str = fname.replace("audit_", "").replace(".json", "")
            dates.append(date_str)
    return sorted(dates, reverse=True)
