"""
SMAR-IA — Modelos y configuración de base de datos SQLAlchemy.
Seguridad: todas las consultas ORM usan parámetros vinculados (inyección SQL no posible).
"""

import logging
from datetime import datetime, timezone

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Generator

from config import SECURITY_DB_URL, TRAFFIC_DB_URL, ADMIN_PASSWORD

logger = logging.getLogger("smar-ia-database")

# Base de datos para registros de seguridad (ISO A.8.15)
security_engine = create_engine(SECURITY_DB_URL, connect_args={"check_same_thread": False})
SecuritySessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=security_engine)
SecurityBase = declarative_base()

# Base de datos simulada de tráfico de red
traffic_engine = create_engine(TRAFFIC_DB_URL, connect_args={"check_same_thread": False})
TrafficSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=traffic_engine)
TrafficBase = declarative_base()


def _utcnow():
    return datetime.now(timezone.utc)


class User(SecurityBase):
    """Modelo de usuario para autenticación."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="viewer")
    is_active = Column(Integer, default=1)


class RevokedToken(SecurityBase):
    """Token JWT revocado (logout). Persistente entre reinicios."""
    __tablename__ = "revoked_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True)
    revoked_at = Column(DateTime, default=_utcnow)
    expires_at = Column(DateTime, nullable=True)


class SecurityLog(SecurityBase):
    """Registro de eventos de seguridad detectados por el IDS."""
    __tablename__ = "security_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=_utcnow)
    source_ip = Column(String, index=True)
    destination_ip = Column(String)
    attack_type = Column(String, index=True)
    confidence = Column(Float)
    action_taken = Column(String)
    iso_control = Column(String, default="A.8.15")
    detection_timestamp = Column(DateTime, nullable=True)
    mitigation_timestamp = Column(DateTime, nullable=True)
    latency_ms = Column(Float, nullable=True)
    whitelist_hit = Column(Integer, default=0)
    severity = Column(String, default="INFO")


class NetworkTraffic(TrafficBase):
    """Tráfico de red simulado para procesamiento por el pipeline ML."""
    __tablename__ = "network_traffic"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=_utcnow)
    source_ip = Column(String)
    destination_ip = Column(String)
    features_csv = Column(String)
    is_processed = Column(Integer, default=0)


class BlockedIP(SecurityBase):
    """IP bloqueada por el sistema de mitigación."""
    __tablename__ = "blocked_ips"

    id = Column(Integer, primary_key=True, index=True)
    ip = Column(String, unique=True, index=True)
    blocked_at = Column(DateTime, default=_utcnow)
    expires_at = Column(DateTime, nullable=True)
    method = Column(String, default="AUTO")
    reason = Column(String, default="Threat mitigation")
    is_active = Column(Integer, default=1)


class Whitelist(SecurityBase):
    """IP exenta de bloqueo automático."""
    __tablename__ = "whitelist"

    id = Column(Integer, primary_key=True, index=True)
    ip = Column(String, unique=True, index=True)
    reason = Column(String, default="")
    created_at = Column(DateTime, default=_utcnow)
    created_by = Column(String, default="admin")


class Rule(SecurityBase):
    """Regla dinámica de detección y mitigación."""
    __tablename__ = "rules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    condition = Column(String)
    action = Column(String)
    duration_minutes = Column(Integer, default=60)
    enabled = Column(Boolean, default=True)


class AppSetting(SecurityBase):
    """Configuración persistente de la aplicación frontend."""
    __tablename__ = "app_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    value = Column(String)


class AuditLog(SecurityBase):
    """Registro de auditoría de acciones administrativas (ISO A.8.21)."""
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=_utcnow)
    username = Column(String, index=True)
    action = Column(String)
    target = Column(String)
    details = Column(String)
    iso_control = Column(String, default="A.8.21")


# Crear tablas (solo si no existen)
SecurityBase.metadata.create_all(bind=security_engine)
TrafficBase.metadata.create_all(bind=traffic_engine)


def get_security_db() -> Generator:
    """Proporciona sesión de base de datos de seguridad. Cierra automáticamente."""
    db = SecuritySessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_traffic_db() -> Generator:
    """Proporciona sesión de base de datos de tráfico. Cierra automáticamente."""
    db = TrafficSessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── Migraciones ──────────────────────────────────────────────────────────────

_MIGRATION_COLUMNS = {
    "security_logs": [
        ("detection_timestamp", "DATETIME"),
        ("mitigation_timestamp", "DATETIME"),
        ("latency_ms", "FLOAT"),
        ("whitelist_hit", "INTEGER DEFAULT 0"),
        ("severity", "VARCHAR DEFAULT 'INFO'"),
    ],
    "blocked_ips": [
        ("expires_at", "DATETIME"),
    ],
}


def _migrate_security_db():
    """Aplica migraciones de esquema para columnas añadidas en nuevas versiones.
    Los nombres de columna/tabla provienen de LISTA HARDCODEADA (no input de
    usuario), por lo que el interpolado directo en SQL no presenta riesgo de
    inyección. bindparams() no funciona para identificadores DDL en SQLite, por
    eso se usa f-string controlado.
    """
    from sqlalchemy import inspect, text

    engine = security_engine
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    for table_name, columns in _MIGRATION_COLUMNS.items():
        if table_name not in tables:
            continue
        existing_cols = {c["name"] for c in inspector.get_columns(table_name)}
        with engine.connect() as conn:
            for col_name, col_type in columns:
                if col_name not in existing_cols:
                    conn.execute(
                        text(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}")
                    )
            conn.commit()


def init_db():
    """Inicializa la base de datos: migraciones + usuario admin."""
    _migrate_security_db()
    db = SecuritySessionLocal()
    try:
        import bcrypt

        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            password = ADMIN_PASSWORD or "admin123"
            if not ADMIN_PASSWORD:
                logger.warning(
                    "Creando admin con contraseña por defecto 'admin123'. "
                    "Defina SMAR_IA_ADMIN_PASSWORD en .env para producción."
                )
            salt = bcrypt.gensalt()
            hashed_pw = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")
            new_admin = User(username="admin", hashed_password=hashed_pw, role="admin")
            db.add(new_admin)
            db.commit()
            logger.info("Usuario administrador creado.")
    except ImportError:
        logger.error("bcrypt no instalado. Omitiendo creación de usuario admin.")
    except Exception as exc:
        logger.error("Error inicializando DB: %s", exc)
    finally:
        db.close()


init_db()
