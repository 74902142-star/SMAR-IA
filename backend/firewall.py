import subprocess
import logging
import time
from config import DRY_RUN

logger = logging.getLogger("smar-ia-firewall")


def apply_iptables_block(ip: str, duration_seconds: int = 3600) -> float:
    """
    Añade regla iptables para bloquear una IP.
    Retorna latencia en milisegundos (0.0 si dry-run o ya existía).
    Requiere sudo.
    """
    detection_time = time.perf_counter()

    if DRY_RUN:
        logger.info(f"[DRY-RUN] iptables -A INPUT -s {ip} -j DROP (duration={duration_seconds}s)")
        return 0.0

    try:
        check_cmd = ["sudo", "iptables", "-C", "INPUT", "-s", ip, "-j", "DROP"]
        exists = subprocess.run(check_cmd, capture_output=True).returncode == 0

        if not exists:
            add_cmd = ["sudo", "iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"]
            subprocess.run(add_cmd, check=True)

            mitigation_time = time.perf_counter()
            latency_ms = round((mitigation_time - detection_time) * 1000, 2)

            logger.info(f"IP {ip} bloqueada en firewall. Latencia: {latency_ms}ms")
            return latency_ms

        return 0.0
    except Exception as e:
        logger.error(f"Error aplicando bloqueo iptables para {ip}: {e}")
        return -1.0


def remove_iptables_block(ip: str) -> bool:
    """Elimina regla de bloqueo de iptables."""
    if DRY_RUN:
        logger.info(f"[DRY-RUN] iptables -D INPUT -s {ip} -j DROP")
        return True

    try:
        del_cmd = ["sudo", "iptables", "-D", "INPUT", "-s", ip, "-j", "DROP"]
        subprocess.run(del_cmd, check=True)
        logger.info(f"IP {ip} desbloqueada en firewall.")
        return True
    except Exception as e:
        logger.error(f"Error eliminando bloqueo iptables para {ip}: {e}")
        return False


def restore_iptables_rules(active_ips: list):
    """
    Restaura reglas iptables desde la BD al iniciar el backend.
    Se llama una vez en startup.
    """
    if DRY_RUN:
        logger.info(f"[DRY-RUN] Restaurando {len(active_ips)} reglas de firewall...")
        return

    logger.info(f"Restaurando {len(active_ips)} reglas de firewall desde BD...")
    restored = 0
    for ip in active_ips:
        latency = apply_iptables_block(ip)
        if latency >= 0:
            restored += 1
    logger.info(f"Restauración completada: {restored}/{len(active_ips)} reglas aplicadas")


def sync_firewall_with_db(active_ips: list):
    """Alias para restore_iptables_rules (compatibilidad)."""
    restore_iptables_rules(active_ips)


def is_iptables_block_active(ip: str) -> bool:
    """Verifica si una IP tiene regla activa en iptables."""
    try:
        check_cmd = ["sudo", "iptables", "-C", "INPUT", "-s", ip, "-j", "DROP"]
        return subprocess.run(check_cmd, capture_output=True).returncode == 0
    except Exception:
        return False
