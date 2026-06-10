"""SMAR-IA — Rate limiter para el firewall.

Monitorea eventos por IP en ventanas de tiempo y dispara alertas
si se supera el umbral configurado.
"""

import time
import logging
from collections import defaultdict
from typing import Dict, List, Optional, Callable
from config import FIREWALL_RATE_LIMIT_ALERTS, FIREWALL_RATE_LIMIT_WINDOW

logger = logging.getLogger("smar-ia-rate-limiter")

_event_counts: Dict[str, List[float]] = defaultdict(list)
_alert_threshold = FIREWALL_RATE_LIMIT_ALERTS
_window_seconds = FIREWALL_RATE_LIMIT_WINDOW
_on_threshold_exceeded: Optional[Callable] = None


def set_threshold_callback(callback: Callable):
    global _on_threshold_exceeded
    _on_threshold_exceeded = callback


def record_event(ip: str):
    """Registra un evento para una IP y verifica si excede el umbral."""
    now = time.time()
    _event_counts[ip].append(now)
    _prune()

    window_events = [t for t in _event_counts[ip] if now - t <= _window_seconds]
    _event_counts[ip] = window_events

    if len(window_events) >= _alert_threshold:
        logger.warning(
            "[RATE-LIMIT] IP %s excedió %d eventos en %ds (%d eventos)",
            ip, _alert_threshold, _window_seconds, len(window_events),
        )
        if _on_threshold_exceeded:
            _on_threshold_exceeded(ip, len(window_events))
        return True
    return False


def _prune():
    now = time.time()
    stale = [ip for ip, events in _event_counts.items() if not events or now - max(events) > _window_seconds * 2]
    for ip in stale:
        del _event_counts[ip]


def get_rate_limit_status() -> Dict[str, int]:
    _prune()
    return {ip: len(events) for ip, events in sorted(_event_counts.items(), key=lambda x: -len(x[1]))}


def get_ip_event_count(ip: str) -> int:
    now = time.time()
    return len([t for t in _event_counts.get(ip, []) if now - t <= _window_seconds])
