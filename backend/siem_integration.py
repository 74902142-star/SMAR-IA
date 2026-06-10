"""SMAR-IA — Integración SIEM vía Syslog (CEF, LEEF, JSON).

Formato CEF: CEF:0|SMAR-IA|IDS|1.0|block|Blocked IP|5|src=1.2.3.4 msg=Attack blocked
"""

import logging
import socket
import json
from datetime import datetime
from typing import Dict, Optional

from config import SIEM_SYSLOG_ENABLED, SIEM_SYSLOG_HOST, SIEM_SYSLOG_PORT

logger = logging.getLogger("smar-ia-siem")

_sock: Optional[socket.socket] = None


def _get_socket():
    global _sock
    if _sock is not None:
        return _sock
    if not SIEM_SYSLOG_ENABLED:
        return None
    try:
        _sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        _sock.connect((SIEM_SYSLOG_HOST, SIEM_SYSLOG_PORT))
        logger.info("Conectado a syslog %s:%d", SIEM_SYSLOG_HOST, SIEM_SYSLOG_PORT)
        return _sock
    except OSError as exc:
        logger.warning("Syslog no disponible: %s", exc)
        return None


def _build_cef(event: str, src_ip: str, msg: str, severity: int = 5) -> str:
    # CEF:0|Vendor|Product|Version|Event|Name|Severity|extensions
    ext = f"src={src_ip} msg={msg}"
    return f"CEF:0|SMAR-IA|IDS|1.0|{event}|{msg}|{severity}|{ext}"


def _build_leef(event: str, src_ip: str, msg: str, severity: int = 5) -> str:
    return (
        f"LEEF:1.0|SMAR-IA|IDS|1.0|{event}|"
        f"devTime={datetime.now(datetime.UTC).isoformat()}Z|"
        f"src={src_ip}|"
        f"severity={severity}|"
        f"msg={msg}"
    )


def _build_json(event: str, src_ip: str, msg: str, severity: int = 5, **extra) -> str:
    payload = {
        "vendor": "SMAR-IA",
        "product": "IDS",
        "version": "1.0",
        "event": event,
        "src_ip": src_ip,
        "msg": msg,
        "severity": severity,
        "timestamp": datetime.now(datetime.UTC).isoformat() + "Z",
    }
    payload.update(extra)
    return json.dumps(payload)


def send_event(
    event: str,
    src_ip: str,
    msg: str,
    severity: int = 5,
    fmt: str = "cef",
    **extra,
):
    """Envía evento a SIEM via syslog."""
    if not SIEM_SYSLOG_ENABLED:
        return

    sock = _get_socket()
    if sock is None:
        return

    builders = {"cef": _build_cef, "leef": _build_leef, "json": _build_json}
    builder = builders.get(fmt, _build_cef)
    try:
        payload = builder(event, src_ip, msg, severity, **extra)
        sock.sendto(payload.encode("utf-8"), (SIEM_SYSLOG_HOST, SIEM_SYSLOG_PORT))
        logger.debug("SIEM event sent: %s", payload[:120])
    except OSError as exc:
        logger.warning("Error enviando a SIEM: %s", exc)


def siem_close():
    global _sock
    if _sock:
        try:
            _sock.close()
        except OSError:
            pass
        _sock = None
