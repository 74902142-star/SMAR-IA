"""SMAR-IA — Bloqueo progresivo estilo fail2ban.

Intervalos crecientes:
  1er bloqueo → 5 min
  2do bloqueo → 30 min
  3er+ bloqueo → 24 h
"""

import os
import json
import logging
import time
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from config import PROGRESSIVE_BLOCK_ENABLED, PROGRESSIVE_BLOCK_INTERVALS

logger = logging.getLogger("smar-ia-progressive")

_INTERVALS = [
    int(x) * 60 for x in PROGRESSIVE_BLOCK_INTERVALS.split(",")
]
_OFFENDERS_FILE = Path(__file__).parent / "logs" / "progressive_offenders.json"
_offenders: Dict[str, List[float]] = {}


def _load_offenders():
    global _offenders
    if _OFFENDERS_FILE.exists():
        try:
            raw = json.loads(_OFFENDERS_FILE.read_text())
            now = time.time()
            _offenders = {
                ip: [t for t in stamps if now - t < _INTERVALS[-1]]
                for ip, stamps in raw.items()
            }
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Error cargando offenders: %s", exc)
            _offenders = {}


def _save_offenders():
    _OFFENDERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    try:
        _OFFENDERS_FILE.write_text(json.dumps(_offenders, indent=2))
    except OSError as exc:
        logger.error("Error guardando offenders: %s", exc)


def _prune_offenders():
    now = time.time()
    max_age = _INTERVALS[-1]
    to_delete = [ip for ip, stamps in _offenders.items() if not stamps or now - max(stamps) > max_age]
    for ip in to_delete:
        del _offenders[ip]
    for ip in list(_offenders.keys()):
        _offenders[ip] = [t for t in _offenders[ip] if now - t <= max_age]
        if not _offenders[ip]:
            del _offenders[ip]


def get_block_duration(ip: str) -> int:
    """Retorna duración en segundos según historial de la IP."""
    if not PROGRESSIVE_BLOCK_ENABLED:
        return _INTERVALS[-1]

    _load_offenders()
    history = _offenders.get(ip, [])
    _prune_offenders()

    strike = len(history)
    if strike >= len(_INTERVALS):
        duration = _INTERVALS[-1]
        logger.info("[PROGRESSIVE] IP %s strike %d → %d s (máximo)", ip, strike + 1, duration)
    else:
        duration = _INTERVALS[strike]
        logger.info("[PROGRESSIVE] IP %s strike %d → %d s", ip, strike + 1, duration)
    return duration


def register_block(ip: str):
    """Registra un bloqueo para escalar la próxima vez."""
    if not PROGRESSIVE_BLOCK_ENABLED:
        return
    _load_offenders()
    if ip not in _offenders:
        _offenders[ip] = []
    _offenders[ip].append(time.time())
    _prune_offenders()
    _save_offenders()


def reset_offender(ip: str):
    """Borra historial de una IP desbloqueada manualmente."""
    _load_offenders()
    _offenders.pop(ip, None)
    _save_offenders()


def get_offenders_summary() -> List[Dict]:
    _load_offenders()
    now = time.time()
    return [
        {"ip": ip, "strikes": len(stamps), "last_block_minutes_ago": round((now - max(stamps)) / 60, 1)}
        for ip, stamps in sorted(_offenders.items(), key=lambda x: -len(x[1]))
    ]
