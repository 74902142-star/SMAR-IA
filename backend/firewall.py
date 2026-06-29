"""SMAR-IA — Gestión de reglas iptables con validación y auditoría."""

import subprocess
import logging
import time
import ipaddress
from typing import List

from config import DRY_RUN, FIREWALL_BACKEND

logger = logging.getLogger("smar-ia-firewall")

# IPs que nunca deben ser bloqueadas (infraestructura crítica)
_NEVER_BLOCK_IPS = {
    "127.0.0.1", "0.0.0.0", "::1",
    # DNS, gateway, etc — agregar según red
}
# Redes privadas que no deben ser bloqueadas automáticamente
_NEVER_BLOCK_NETWORKS = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
]


def validate_ip(ip: str) -> bool:
    """Valida que la IP sea IPv4 o IPv6 válida."""
    try:
        ipaddress.ip_address(ip.strip())
        return True
    except (ValueError, AttributeError):
        return False


def _validate_ip(ip: str) -> str:
    """Valida que una IP tenga formato IPv4/IPv6 válido y no esté en never-block."""
    try:
        addr = ipaddress.ip_address(ip.strip())
    except ValueError as exc:
        raise ValueError(f"IP inválida: {ip}") from exc

    ip_str = str(addr)

    if ip_str in _NEVER_BLOCK_IPS:
        raise ValueError(f"IP {ip_str} está en la lista de nunca bloquear")

    for net in _NEVER_BLOCK_NETWORKS:
        if addr in net:
            logger.debug("Bloqueando IP privada %s (red %s)", ip_str, net)
            break

    return ip_str


def apply_iptables_block(ip: str, duration_seconds: int = 3600) -> float:
    """
    Añade regla iptables para bloquear una IP.

    Args:
        ip: Dirección IPv4 a bloquear.
        duration_seconds: Duración del bloqueo en segundos.

    Returns:
        Latencia en milisegundos, 0.0 si dry-run o ya existía, -1.0 si error.

    Raises:
        ValueError: Si la IP no es válida o está en never-block.
    """
    ip = _validate_ip(ip)
    detection_time = time.perf_counter()
    if DRY_RUN:
        logger.info("[DRY-RUN] iptables -A INPUT -s %s -j DROP (duration=%ss)", ip, duration_seconds)
        return 0.0

    try:
        check_cmd = ["sudo", "iptables", "-C", "INPUT", "-s", ip, "-j", "DROP"]
        exists = subprocess.run(check_cmd, capture_output=True).returncode == 0

        if not exists:
            add_cmd = ["sudo", "iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"]
            subprocess.run(add_cmd, check=True, timeout=30)

            mitigation_time = time.perf_counter()
            latency_ms = round((mitigation_time - detection_time) * 1000, 2)

            logger.info("IP %s bloqueada en firewall. Latencia: %sms", ip, latency_ms)
            return latency_ms

        return 0.0
    except subprocess.TimeoutExpired:
        logger.error("Timeout aplicando bloqueo iptables para %s", ip)
        return -1.0
    except subprocess.CalledProcessError as exc:
        logger.error("Error en iptables para %s: %s", ip, exc)
        return -1.0
    except OSError as exc:
        logger.error("Error del sistema para %s: %s", ip, exc)
        return -1.0


def remove_iptables_block(ip: str) -> bool:
    """Elimina regla de bloqueo de iptables."""
    try:
        ip = _validate_ip(ip)
    except ValueError:
        return False

    if DRY_RUN:
        logger.info("[DRY-RUN] iptables -D INPUT -s %s -j DROP", ip)
        return True

    try:
        del_cmd = ["sudo", "iptables", "-D", "INPUT", "-s", ip, "-j", "DROP"]
        subprocess.run(del_cmd, check=True, timeout=30)
        logger.info("IP %s desbloqueada en firewall.", ip)
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError) as exc:
        logger.error("Error eliminando bloqueo iptables para %s: %s", ip, exc)
        return False


def _get_block_func():
    """Retorna la función de bloqueo según el backend configurado."""
    if FIREWALL_BACKEND == "nftables":
        try:
            from firewall_nftables import nft_block_ip
            return nft_block_ip
        except ImportError:
            logger.warning("nftables backend no disponible, usando iptables")
    return apply_iptables_block


def restore_iptables_rules(active_ips: List[str]):
    """Restaura reglas firewall desde la BD al iniciar el backend."""
    if DRY_RUN:
        logger.info("[DRY-RUN] Restaurando %d reglas de firewall...", len(active_ips))
        return

    block_func = _get_block_func()
    logger.info("Restaurando %d reglas de firewall desde BD...", len(active_ips))
    restored = 0
    for ip in active_ips:
        try:
            latency = block_func(ip)
            if latency >= 0:
                restored += 1
        except ValueError:
            logger.warning("IP inválida omitida durante restauración: %s", ip)
    logger.info("Restauración completada: %d/%d reglas aplicadas", restored, len(active_ips))


def sync_firewall_with_db(active_ips: List[str]):
    """Alias para restore_iptables_rules (compatibilidad)."""
    restore_iptables_rules(active_ips)


def is_iptables_block_active(ip: str) -> bool:
    """Verifica si una IP tiene regla activa en iptables."""
    try:
        ip = _validate_ip(ip)
        check_cmd = ["sudo", "iptables", "-C", "INPUT", "-s", ip, "-j", "DROP"]
        return subprocess.run(check_cmd, capture_output=True, timeout=10).returncode == 0
    except (ValueError, subprocess.TimeoutExpired, OSError):
        return False
