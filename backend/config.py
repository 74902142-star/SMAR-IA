"""
SMAR-IA — Configuración Centralizada
Carga valores desde variables de entorno (.env) con fallbacks por defecto.
"""
import os
from pathlib import Path

# Intentar cargar .env si existe
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print(f"[CONFIG] Variables de entorno cargadas desde {env_path}")
    else:
        print("[CONFIG] Archivo .env no encontrado, usando valores por defecto.")
except ImportError:
    print("[CONFIG] python-dotenv no instalado, usando valores por defecto.")

# ── Seguridad / JWT ──────────────────────────────────────────────────────────
SECRET_KEY = os.getenv("SMAR_IA_SECRET_KEY", "smar_ia_secret_key_super_secure")
ALGORITHM = os.getenv("SMAR_IA_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("SMAR_IA_TOKEN_EXPIRE_MINUTES", "1440"))  # 24h

# ── Modelo ML ────────────────────────────────────────────────────────────────
MODELS_DIR = os.getenv("SMAR_IA_MODELS_DIR", os.path.join(os.path.dirname(__file__), "..", "ml_pipeline", "models"))
NUM_FEATURES = int(os.getenv("SMAR_IA_NUM_FEATURES", "80"))

# ── Umbrales de Decisión ─────────────────────────────────────────────────────
AUTO_BLOCK_THRESHOLD = float(os.getenv("SMAR_IA_AUTO_BLOCK_THRESHOLD", "0.95"))
SUSPICIOUS_ALERT_COUNT = int(os.getenv("SMAR_IA_SUSPICIOUS_ALERT_COUNT", "3"))
SUSPICIOUS_WINDOW_MINUTES = int(os.getenv("SMAR_IA_SUSPICIOUS_WINDOW_MINUTES", "5"))

# ── Modo de operación ────────────────────────────────────────────────────────
DRY_RUN = os.getenv("SMAR_IA_DRY_RUN", "false").lower() == "true"

# ── Base de Datos ────────────────────────────────────────────────────────────
SECURITY_DB_URL = os.getenv("SMAR_IA_SECURITY_DB", "sqlite:///./security_logs.db")
TRAFFIC_DB_URL = os.getenv("SMAR_IA_TRAFFIC_DB", "sqlite:///./traffic.db")

# ── Sistema ──────────────────────────────────────────────────────────────────
APP_VERSION = "1.0.0"
APP_NAME = "SMAR-IA IDS"

# ── Logging de configuración cargada (sin exponer secrets) ───────────────────
def print_config_summary():
    print(f"[CONFIG] APP: {APP_NAME} v{APP_VERSION}")
    print(f"[CONFIG] Algoritmo JWT: {ALGORITHM}")
    print(f"[CONFIG] Token expira en: {ACCESS_TOKEN_EXPIRE_MINUTES} min")
    print(f"[CONFIG] Directorio modelos: {MODELS_DIR}")
    print(f"[CONFIG] Umbral auto-bloqueo: {AUTO_BLOCK_THRESHOLD}")
    print(f"[CONFIG] Modo dry-run: {DRY_RUN}")
    print(f"[CONFIG] SECRET_KEY configurada: {'[OK] desde .env' if os.getenv('SMAR_IA_SECRET_KEY') else '[!!] valor por defecto'}")
