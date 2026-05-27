from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
from config import SECURITY_DB_URL, TRAFFIC_DB_URL

# Base de datos para registros de seguridad (ISO A.8.15)
security_engine = create_engine(SECURITY_DB_URL, connect_args={"check_same_thread": False})
SecuritySessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=security_engine)
SecurityBase = declarative_base()

# Base de datos simulada de tráfico de red
traffic_engine = create_engine(TRAFFIC_DB_URL, connect_args={"check_same_thread": False})
TrafficSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=traffic_engine)
TrafficBase = declarative_base()

# Modelos
class User(SecurityBase):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="viewer") # "admin" o "viewer"
    is_active = Column(Integer, default=1) # 1: Activo, 0: Inactivo

class SecurityLog(SecurityBase):
    __tablename__ = "security_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    source_ip = Column(String, index=True)
    destination_ip = Column(String)
    attack_type = Column(String, index=True)
    confidence = Column(Float)
    action_taken = Column(String) # ej. "LOGGED", "BLOCKED_IPTABLES"
    iso_control = Column(String, default="A.8.15")
    detection_timestamp = Column(DateTime, nullable=True)
    mitigation_timestamp = Column(DateTime, nullable=True)
    latency_ms = Column(Float, nullable=True)
    whitelist_hit = Column(Integer, default=0)

class NetworkTraffic(TrafficBase):
    __tablename__ = "network_traffic"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    source_ip = Column(String)
    destination_ip = Column(String)
    # Almacenamos el vector de características como un string separado por comas para simular
    features_csv = Column(String)
    is_processed = Column(Integer, default=0) # 0: No procesado, 1: Procesado

class BlockedIP(SecurityBase):
    __tablename__ = "blocked_ips"

    id = Column(Integer, primary_key=True, index=True)
    ip = Column(String, unique=True, index=True)
    blocked_at = Column(DateTime, default=datetime.datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    method = Column(String, default="AUTO")
    reason = Column(String, default="Threat mitigation")
    is_active = Column(Integer, default=1)

class Whitelist(SecurityBase):
    __tablename__ = "whitelist"

    id = Column(Integer, primary_key=True, index=True)
    ip = Column(String, unique=True, index=True)
    reason = Column(String, default="")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    created_by = Column(String, default="admin")


class Rule(SecurityBase):
    __tablename__ = "rules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    condition = Column(String) # Ej: "attack_type == 'Brute Force' and confidence > 0.8"
    action = Column(String)    # "BLOCK" o "ALERT"
    duration_minutes = Column(Integer, default=60)
    enabled = Column(Boolean, default=True)

class AuditLog(SecurityBase):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    username = Column(String, index=True)
    action = Column(String)      # "BLOCK", "UNBLOCK", "RULE_CREATE", "RULE_DELETE", etc.
    target = Column(String)      # IP o Rule ID
    details = Column(String)     # Descripción adicional
    iso_control = Column(String, default="A.8.21")

# Crear tablas
SecurityBase.metadata.create_all(bind=security_engine)
TrafficBase.metadata.create_all(bind=traffic_engine)

def get_security_db():
    db = SecuritySessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_traffic_db():
    db = TrafficSessionLocal()
    try:
        yield db
    finally:
        db.close()

def _migrate_security_db():
    """Migraciones manuales para columnas añadidas en nuevas versiones."""
    from sqlalchemy import inspect, text
    engine = security_engine
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    if "security_logs" in tables:
        cols = [c["name"] for c in inspector.get_columns("security_logs")]
        with engine.connect() as conn:
            if "detection_timestamp" not in cols:
                conn.execute(text("ALTER TABLE security_logs ADD COLUMN detection_timestamp DATETIME"))
            if "mitigation_timestamp" not in cols:
                conn.execute(text("ALTER TABLE security_logs ADD COLUMN mitigation_timestamp DATETIME"))
            if "latency_ms" not in cols:
                conn.execute(text("ALTER TABLE security_logs ADD COLUMN latency_ms FLOAT"))
            if "whitelist_hit" not in cols:
                conn.execute(text("ALTER TABLE security_logs ADD COLUMN whitelist_hit INTEGER DEFAULT 0"))
            conn.commit()

    if "blocked_ips" in tables:
        cols = [c["name"] for c in inspector.get_columns("blocked_ips")]
        with engine.connect() as conn:
            if "expires_at" not in cols:
                conn.execute(text("ALTER TABLE blocked_ips ADD COLUMN expires_at DATETIME"))
            conn.commit()


def init_db():
    _migrate_security_db()
    db = SecuritySessionLocal()
    try:
        import bcrypt
        # Verificar si existe el admin
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            salt = bcrypt.gensalt()
            hashed_pw = bcrypt.hashpw("admin123".encode('utf-8'), salt).decode('utf-8')
            new_admin = User(username="admin", hashed_password=hashed_pw, role="admin")
            db.add(new_admin)
            db.commit()
            print("Usuario administrador creado por defecto (admin/admin123).")
    except Exception as e:
        print(f"Error inicializando DB: {e}")
    finally:
        db.close()

init_db()
