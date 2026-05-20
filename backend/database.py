from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

# Base de datos para registros de seguridad (ISO A.8.15)
SECURITY_DB_URL = "sqlite:///./security_logs.db"
security_engine = create_engine(SECURITY_DB_URL, connect_args={"check_same_thread": False})
SecuritySessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=security_engine)
SecurityBase = declarative_base()

# Base de datos simulada de tráfico de red
TRAFFIC_DB_URL = "sqlite:///./traffic.db"
traffic_engine = create_engine(TRAFFIC_DB_URL, connect_args={"check_same_thread": False})
TrafficSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=traffic_engine)
TrafficBase = declarative_base()

# Modelos
class User(SecurityBase):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
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

class NetworkTraffic(TrafficBase):
    __tablename__ = "network_traffic"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    source_ip = Column(String)
    destination_ip = Column(String)
    # Almacenamos el vector de características como un string separado por comas para simular
    features_csv = Column(String)
    is_processed = Column(Integer, default=0) # 0: No procesado, 1: Procesado

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

def init_db():
    db = SecuritySessionLocal()
    try:
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        # Verificar si existe el admin
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            hashed_pw = pwd_context.hash("admin123")
            new_admin = User(username="admin", hashed_password=hashed_pw)
            db.add(new_admin)
            db.commit()
            print("Usuario administrador creado por defecto (admin/admin123).")
    except Exception as e:
        print(f"Error inicializando DB: {e}")
    finally:
        db.close()

init_db()
