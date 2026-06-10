"""SMAR-IA — Gestión de reglas nftables como alternativa moderna a iptables."""

import subprocess
import logging
import time
import ipaddress
from typing import List
from config import DRY_RUN

logger = logging.getLogger("smar-ia-nftables")

NFT_TABLE = "smar-ia"
NFT_SET = "blocked_ips"


def _ensure_table():
    """Crea la tabla y set de nftables si no existen."""
    if DRY_RUN:
        return True
    try:
        subprocess.run(
            ["sudo", "nft", "add", "table", "inet", NFT_TABLE],
            capture_output=True, timeout=10,
        )
        subprocess.run(
            ["sudo", "nft", "add", "set", "inet", NFT_TABLE, NFT_SET, "{ type ipv4_addr; flags timeout; }"],
            capture_output=True, timeout=10,
        )
        subprocess.run(
            ["sudo", "nft", "add", "chain", "inet", NFT_TABLE, "input", "{ type filter hook input priority 0; }"],
            capture_output=True, timeout=10,
        )
        subprocess.run(
            ["sudo", "nft", "add", "rule", "inet", NFT_TABLE, "input", f"ip saddr @{NFT_SET} drop"],
            capture_output=True, timeout=10,
        )
        return True
    except Exception as exc:
        logger.error("Error creando tabla nftables: %s", exc)
        return False


def nft_block_ip(ip: str, duration_seconds: int = 3600) -> float:
    """Bloquea IP via nftables con timeout automático."""
    from firewall import _validate_ip
    try:
        ip = _validate_ip(ip)
    except ValueError as exc:
        logger.error("IP inválida para nftables: %s", exc)
        return -1.0

    detection_time = time.perf_counter()

    if DRY_RUN:
        logger.info("[DRY-RUN] nft add element inet %s %s '{ %s timeout %ds }'", NFT_TABLE, NFT_SET, ip, duration_seconds)
        return 0.0

    try:
        _ensure_table()
        cmd = [
            "sudo", "nft", "add", "element", "inet", NFT_TABLE, NFT_SET,
            f"{{ {ip} timeout {duration_seconds}s }}",
        ]
        subprocess.run(cmd, check=True, timeout=30)
        mitigation_time = time.perf_counter()
        latency_ms = round((mitigation_time - detection_time) * 1000, 2)
        logger.info("IP %s bloqueada via nftables (%ds). Latencia: %sms", ip, duration_seconds, latency_ms)
        return latency_ms
    except subprocess.TimeoutExpired:
        logger.error("Timeout aplicando nftables para %s", ip)
        return -1.0
    except subprocess.CalledProcessError as exc:
        logger.error("Error nftables para %s: %s", ip, exc)
        return -1.0


def nft_unblock_ip(ip: str) -> bool:
    """Elimina IP del set de bloqueo nftables."""
    from firewall import _validate_ip
    try:
        ip = _validate_ip(ip)
    except ValueError:
        return False

    if DRY_RUN:
        logger.info("[DRY-RUN] nft delete element inet %s %s '{ %s }'", NFT_TABLE, NFT_SET, ip)
        return True

    try:
        cmd = ["sudo", "nft", "delete", "element", "inet", NFT_TABLE, NFT_SET, f"{{ {ip} }}"]
        subprocess.run(cmd, check=True, timeout=30)
        logger.info("IP %s desbloqueada via nftables.", ip)
        return True
    except subprocess.CalledProcessError:
        logger.warning("IP %s no estaba en nftables.", ip)
        return False


def nft_is_blocked(ip: str) -> bool:
    """Verifica si una IP está en el set de nftables."""
    try:
        cmd = ["sudo", "nft", "list", "set", "inet", NFT_TABLE, NFT_SET]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return ip in result.stdout
    except Exception:
        return False
