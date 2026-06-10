"""
SMAR-IA — Configuración Centralizada
Carga valores desde variables de entorno (.env) con validación al inicio.
"""

import os
import logging
import secrets
from pathlib import Path

logger = logging.getLogger("smar-ia-config")

try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        logger.info("Variables de entorno cargadas desde %s", env_path)
    else:
        logger.info("Archivo .env no encontrado, usando variables del sistema.")
except ImportError:
    logger.info("python-dotenv no instalado, usando variables del sistema.")


def _require_env(key: str, default: str = None) -> str:
    """Valida que una variable de entorno exista. En desarrollo usa default con advertencia."""
    value = os.getenv(key)
    if value is not None:
        return value
    if default is not None:
        logger.warning("[DEV] %s no definido, usando valor por defecto. ¡NO USAR EN PRODUCCIÓN!", key)
        return default
    raise RuntimeError(
        f"Variable de entorno {key} es obligatoria. "
        f"Crear archivo .env en {Path(__file__).parent / '.env'}"
    )


# ── Seguridad / JWT ──
SECRET_KEY = _require_env(
    "SMAR_IA_SECRET_KEY",
    default="dev_" + secrets.token_hex(32)
)
ALGORITHM = os.getenv("SMAR_IA_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("SMAR_IA_TOKEN_EXPIRE_MINUTES", "1440"))

# ── Admin inicial ──
ADMIN_PASSWORD = os.getenv("SMAR_IA_ADMIN_PASSWORD")
if not ADMIN_PASSWORD:
    logger.warning(
        "[DEV] SMAR_IA_ADMIN_PASSWORD no definido. Se usará 'admin123' "
        "como contraseña por defecto. ¡CAMBIAR EN PRODUCCIÓN!"
    )

# ── CORS ──
CORS_ORIGINS = os.getenv("SMAR_IA_CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")

# ── Modelo ML ──
MODELS_DIR = os.getenv("SMAR_IA_MODELS_DIR", os.path.join(os.path.dirname(__file__), "..", "ml_pipeline", "models"))
NUM_FEATURES = int(os.getenv("SMAR_IA_NUM_FEATURES", "80"))

# ── Umbrales de Decisión ──
AUTO_BLOCK_THRESHOLD = float(os.getenv("SMAR_IA_AUTO_BLOCK_THRESHOLD", "0.85"))
SUSPICIOUS_ALERT_COUNT = int(os.getenv("SMAR_IA_SUSPICIOUS_ALERT_COUNT", "3"))
SUSPICIOUS_WINDOW_MINUTES = int(os.getenv("SMAR_IA_SUSPICIOUS_WINDOW_MINUTES", "5"))

# ── Modo de operación ──
DRY_RUN = os.getenv("SMAR_IA_DRY_RUN", "false").lower() == "true"

# ── Base de Datos ──
SECURITY_DB_URL = os.getenv("SMAR_IA_SECURITY_DB", "sqlite:///./security_logs.db")
TRAFFIC_DB_URL = os.getenv("SMAR_IA_TRAFFIC_DB", "sqlite:///./traffic.db")
DATABASE_POOL_SIZE = int(os.getenv("SMAR_IA_DB_POOL_SIZE", "5"))
DATABASE_MAX_OVERFLOW = int(os.getenv("SMAR_IA_DB_MAX_OVERFLOW", "10"))

# ── Firewall backend ──
FIREWALL_BACKEND = os.getenv("SMAR_IA_FIREWALL_BACKEND", "auto")  # auto, iptables, nftables

# ── Bloqueo progresivo (fail2ban-style) ──
PROGRESSIVE_BLOCK_ENABLED = os.getenv("SMAR_IA_PROGRESSIVE_BLOCK", "true").lower() == "true"
PROGRESSIVE_BLOCK_INTERVALS = os.getenv(
    "SMAR_IA_PROGRESSIVE_INTERVALS", "5,30,1440"
)  # minutos: 1er, 2do, 3er+ bloqueo

# ── SIEM ──
SIEM_SYSLOG_ENABLED = os.getenv("SMAR_IA_SIEM_SYSLOG", "false").lower() == "true"
SIEM_SYSLOG_HOST = os.getenv("SMAR_IA_SIEM_SYSLOG_HOST", "127.0.0.1")
SIEM_SYSLOG_PORT = int(os.getenv("SMAR_IA_SIEM_SYSLOG_PORT", "514"))

# ── Threat Intelligence ──
THREAT_INTEL_ENABLED = os.getenv("SMAR_IA_THREAT_INTEL", "true").lower() == "true"
THREAT_INTEL_UPDATE_MINUTES = int(os.getenv("SMAR_IA_THREAT_INTEL_UPDATE", "60"))
THREAT_INTEL_FEEDS = os.getenv(
    "SMAR_IA_THREAT_INTEL_FEEDS",
    "https://feeds.dshield.org/block.txt,https://rules.emergingthreats.net/blockrules/compromised-ips.txt",
)

# ── Honeypot ──
HONEYPOT_ENABLED = os.getenv("SMAR_IA_HONEYPOT", "false").lower() == "true"
HONEYPOT_PORTS = os.getenv("SMAR_IA_HONEYPOT_PORTS", "22,3306,8080,8443")

# ── Prometheus ──
PROMETHEUS_ENABLED = os.getenv("SMAR_IA_PROMETHEUS", "true").lower() == "true"

# ── Sistema ──
APP_VERSION = "1.1.0"
APP_NAME = "SMAR-IA IDS"

# ── Rate limiting ──
LOGIN_RATE_LIMIT = os.getenv("SMAR_IA_LOGIN_RATE_LIMIT", "5/minute")
FIREWALL_RATE_LIMIT_ALERTS = int(os.getenv("SMAR_IA_RATE_LIMIT_ALERTS", "10"))
FIREWALL_RATE_LIMIT_WINDOW = int(os.getenv("SMAR_IA_RATE_LIMIT_WINDOW", "60"))


def print_config_summary():
    logger.info("APP: %s v%s", APP_NAME, APP_VERSION)
    logger.info("Algoritmo JWT: %s", ALGORITHM)
    logger.info("Token expira en: %d min", ACCESS_TOKEN_EXPIRE_MINUTES)
    logger.info("CORS origins: %s", CORS_ORIGINS)
    logger.info("Directorios modelos: %s", MODELS_DIR)
    logger.info("Umbral auto-bloqueo: %s", AUTO_BLOCK_THRESHOLD)
    logger.info("Modo dry-run: %s", DRY_RUN)
    logger.info("Firewall backend: %s", FIREWALL_BACKEND)
    logger.info("Bloqueo progresivo: %s", PROGRESSIVE_BLOCK_ENABLED)
    logger.info("SIEM Syslog: %s", SIEM_SYSLOG_ENABLED)
    logger.info("Threat Intelligence: %s", THREAT_INTEL_ENABLED)
    logger.info("Honeypot: %s", HONEYPOT_ENABLED)
    logger.info("Prometheus: %s", PROMETHEUS_ENABLED)
    logger.info("SECRET_KEY configurada: %s", "[OK] desde .env" if os.getenv("SMAR_IA_SECRET_KEY") else "[!!] valor por defecto (DEV)")
