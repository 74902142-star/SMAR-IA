"""SMAR-IA — Threat Intelligence Feeds.

Descarga listas de IPs maliciosas desde fuentes externas
y las mantiene en caché para bloquear automáticamente.
"""

import asyncio
import ipaddress
import logging
import time
import json
from pathlib import Path
from typing import List, Set, Optional
from urllib.request import urlopen, Request
from urllib.error import URLError

from config import THREAT_INTEL_ENABLED, THREAT_INTEL_UPDATE_MINUTES, THREAT_INTEL_FEEDS

logger = logging.getLogger("smar-ia-threat-intel")

_CACHE_FILE = Path(__file__).parent / "logs" / "threat_intel_cache.json"
_known_bad_ips: Set[str] = set()
_last_update: float = 0


def _ip_in_prefix(ip: str, prefixes: List[str]) -> bool:
    try:
        addr = ipaddress.ip_address(ip)
        for prefix in prefixes:
            try:
                net = ipaddress.ip_network(prefix, strict=False)
                if addr in net:
                    return True
            except ValueError:
                continue
    except ValueError:
        pass
    return False


def _parse_dshield(data: str) -> List[str]:
    ips = []
    for line in data.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith(";"):
            continue
        parts = line.split()
        if len(parts) >= 2:
            try:
                ipaddress.ip_address(parts[0])
                ips.append(parts[0])
            except ValueError:
                try:
                    net = ipaddress.ip_network(parts[0], strict=False)
                    ips.append(str(net))
                except ValueError:
                    continue
    return ips


def _parse_emergingthreats(data: str) -> List[str]:
    ips = []
    for line in data.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith(";"):
            continue
        try:
            ipaddress.ip_address(line)
            ips.append(line)
        except ValueError:
            try:
                net = ipaddress.ip_network(line, strict=False)
                ips.append(str(net))
            except ValueError:
                continue
    return ips


def _fetch_feed(url: str, timeout: int = 30) -> Optional[str]:
    try:
        req = Request(url, headers={"User-Agent": "SMAR-IA-IDS/1.0"})
        with urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except (URLError, OSError) as exc:
        logger.warning("Error fetching threat feed %s: %s", url, exc)
        return None


async def update_threat_intel():
    """Actualiza la caché de IPs maliciosas desde los feeds configurados."""
    global _known_bad_ips, _last_update

    if not THREAT_INTEL_ENABLED:
        return

    feeds = [f.strip() for f in THREAT_INTEL_FEEDS.split(",") if f.strip()]
    if not feeds:
        return

    all_ips: Set[str] = set()
    parsers = {
        "dshield": _parse_dshield,
        "emergingthreats": _parse_emergingthreats,
        "blocklist": _parse_emergingthreats,
    }

    for url in feeds:
        try:
            data = await asyncio.to_thread(_fetch_feed, url)
            if data is None:
                continue
            for name, parser in parsers.items():
                if name in url:
                    parsed = parser(data)
                    all_ips.update(parsed)
                    logger.info("Feed %s: %d IPs/prefixes", url, len(parsed))
                    break
            else:
                parsed = _parse_emergingthreats(data)
                all_ips.update(parsed)
                logger.info("Feed %s: %d IPs/prefixes (generic)", url, len(parsed))
        except Exception as exc:
            logger.warning("Error procesando feed %s: %s", url, exc)

    if all_ips:
        _known_bad_ips = all_ips
        _last_update = time.time()
        _CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        _CACHE_FILE.write_text(json.dumps({"updated": _last_update, "ips": list(_known_bad_ips)}, indent=2))
        logger.info("Threat intel actualizado: %d IPs en caché", len(_known_bad_ips))


def is_known_threat(ip: str) -> bool:
    """Verifica si una IP está en la lista de amenazas conocidas."""
    if not _known_bad_ips:
        _load_cache()
    if ip in _known_bad_ips:
        return True
    return _ip_in_prefix(ip, [p for p in _known_bad_ips if "/" in p])


def _load_cache():
    global _known_bad_ips, _last_update
    if _CACHE_FILE.exists():
        try:
            data = json.loads(_CACHE_FILE.read_text())
            _known_bad_ips = set(data.get("ips", []))
            _last_update = data.get("updated", 0)
        except (json.JSONDecodeError, OSError):
            pass


def get_threat_intel_stats() -> dict:
    return {
        "enabled": THREAT_INTEL_ENABLED,
        "cached_ips": len(_known_bad_ips),
        "last_update": _last_update,
        "age_minutes": round((time.time() - _last_update) / 60, 1) if _last_update else 0,
    }
