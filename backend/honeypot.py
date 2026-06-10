"""SMAR-IA — Honeypot integrado.

Abre puertos falsos que registran cualquier intento de conexión
como potencial ataque y alimentan el pipeline de detección.
"""

import asyncio
import logging
import time
import socket
from typing import List, Optional

from config import HONEYPOT_ENABLED, HONEYPOT_PORTS

logger = logging.getLogger("smar-ia-honeypot")

_honeypot_servers: List[asyncio.Server] = []
_honeypot_hits: List[dict] = []


async def _handle_honeypot(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    """Maneja conexión entrante a un puerto señuelo."""
    peername = writer.get_extra_info("peername")
    sockname = writer.get_extra_info("sockname")
    ip = peername[0] if peername else "unknown"
    port = sockname[1] if sockname else 0

    hit = {
        "ip": ip,
        "port": port,
        "timestamp": time.time(),
        "iso_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    _honeypot_hits.append(hit)
    logger.warning("[HONEYPOT] Conexión desde %s al puerto señuelo %d", ip, port)

    try:
        # Slow down attacker: send fake banner, wait
        writer.write(b"SSH-2.0-OpenSSH_8.9p1 Ubuntu-3\r\n")
        await asyncio.sleep(3)
    except (OSError, asyncio.CancelledError):
        pass
    finally:
        try:
            writer.close()
            await writer.wait_closed()
        except (OSError, asyncio.CancelledError):
            pass


async def start_honeypots():
    """Inicia servidores señuelo en los puertos configurados."""
    if not HONEYPOT_ENABLED:
        return

    ports = [int(p.strip()) for p in HONEYPOT_PORTS.split(",") if p.strip().isdigit()]
    for port in ports:
        try:
            server = await asyncio.start_unix_server(
                _handle_honeypot, path=None
            ) if port == 0 else await asyncio.start_server(
                _handle_honeypot, host="0.0.0.0", port=port
            )
            _honeypot_servers.append(server)
            logger.info("Honeypot activo en puerto %d", port)
        except (OSError, PermissionError) as exc:
            logger.warning("No se pudo abrir honeypot en puerto %d: %s", port, exc)


async def stop_honeypots():
    """Detiene todos los honeypots."""
    for server in _honeypot_servers:
        server.close()
        await server.wait_closed()
    _honeypot_servers.clear()


def get_honeypot_hits() -> List[dict]:
    return list(_honeypot_hits)


def get_honeypot_hits_since(since: float) -> List[dict]:
    return [h for h in _honeypot_hits if h["timestamp"] >= since]


def clear_honeypot_hits():
    _honeypot_hits.clear()
