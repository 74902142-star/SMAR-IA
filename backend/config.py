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

# ── Sistema ──
APP_VERSION = "1.0.0"
APP_NAME = "SMAR-IA IDS"

# ── Rate limiting ──
LOGIN_RATE_LIMIT = os.getenv("SMAR_IA_LOGIN_RATE_LIMIT", "5/minute")


def print_config_summary():
    logger.info("APP: %s v%s", APP_NAME, APP_VERSION)
    logger.info("Algoritmo JWT: %s", ALGORITHM)
    logger.info("Token expira en: %d min", ACCESS_TOKEN_EXPIRE_MINUTES)
    logger.info("CORS origins: %s", CORS_ORIGINS)
    logger.info("Directorios modelos: %s", MODELS_DIR)
    logger.info("Umbral auto-bloqueo: %s", AUTO_BLOCK_THRESHOLD)
    logger.info("Modo dry-run: %s", DRY_RUN)
    logger.info("SECRET_KEY configurada: %s", "[OK] desde .env" if os.getenv("SMAR_IA_SECRET_KEY") else "[!!] valor por defecto (DEV)")
