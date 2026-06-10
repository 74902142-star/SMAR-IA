"""SMAR-IA — Conexión PostgreSQL con pool y failback a SQLite."""

import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import SECURITY_DB_URL, TRAFFIC_DB_URL, DATABASE_POOL_SIZE, DATABASE_MAX_OVERFLOW

logger = logging.getLogger("smar-ia-db-pg")

_USE_POSTGRES = "postgresql" in SECURITY_DB_URL

def _create_pg_engine(db_url: str, pool_size: int = DATABASE_POOL_SIZE, max_overflow: int = DATABASE_MAX_OVERFLOW):
    if "postgresql" not in db_url:
        return None
    try:
        import psycopg2
        engine = create_engine(
            db_url,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_pre_ping=True,
            pool_recycle=3600,
        )
        logger.info("Conexión PostgreSQL establecida: %s", db_url.replace(db_url.split("@")[-1] if "@" in db_url else "", "***"))
        return engine
    except ImportError:
        logger.warning("psycopg2 no instalado. Usando SQLite.")
        return None
    except Exception as exc:
        logger.error("Error conectando a PostgreSQL: %s. Usando SQLite.", exc)
        return None


def get_engines():
    """Retorna motores de BD. Si PostgreSQL falla, usa SQLite."""
    from sqlalchemy import create_engine as sqlite_engine
    from database import SECURITY_DB_URL as FALLBACK_SECURITY, TRAFFIC_DB_URL as FALLBACK_TRAFFIC

    security_engine = _create_pg_engine(SECURITY_DB_URL) or sqlite_engine(FALLBACK_SECURITY, connect_args={"check_same_thread": False})
    traffic_engine = _create_pg_engine(TRAFFIC_DB_URL) or sqlite_engine(FALLBACK_TRAFFIC, connect_args={"check_same_thread": False})
    return security_engine, traffic_engine
