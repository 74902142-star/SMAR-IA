import argparse
import random
import datetime
from database import (
    SecurityBase,
    TrafficBase,
    security_engine,
    traffic_engine,
    TrafficSessionLocal,
    SecuritySessionLocal,
    User,
    NetworkTraffic,
    get_security_db,
    get_traffic_db,
)
from auth import get_password_hash


def migrate():
    SecurityBase.metadata.create_all(bind=security_engine)
    TrafficBase.metadata.create_all(bind=traffic_engine)
    print("[manage] Tablas de base de datos creadas o actualizadas.")


def seed_admin(password: str = "admin123"):
    db = SecuritySessionLocal()
    try:
        admin = db.query(User).filter(User.username == "admin").first()
        if admin:
            print("[manage] El usuario admin ya existe.")
            return
        hashed_pw = get_password_hash(password)
        admin = User(username="admin", hashed_password=hashed_pw, is_active=1)
        db.add(admin)
        db.commit()
        print("[manage] Usuario admin creado con contraseña por defecto.")
    finally:
        db.close()


ATTACK_CLASSES = ['DDoS SYN Flood', 'DDoS UDP Flood', 'Sniffing Pasivo',
                  'DHCP Starvation', 'DHCP Spoofing', 'Port Scanning', 'Brute Force']

def _generate_attack_features(attack_type: str) -> list:
    x = [random.gauss(0, 0.5) for _ in range(80)]
    if attack_type == 'DDoS SYN Flood':
        for i in range(10): x[i] += random.uniform(2.0, 4.0)
        for i in range(15, 20): x[i] += random.uniform(1.5, 3.0)
    elif attack_type == 'DDoS UDP Flood':
        for i in range(10, 20): x[i] += random.uniform(2.5, 4.5)
        for i in range(25, 30): x[i] += random.uniform(1.0, 2.5)
    elif attack_type == 'Port Scanning':
        for i in range(20, 35): x[i] += random.uniform(1.5, 3.5)
        for i in range(40, 45): x[i] += random.uniform(1.0, 2.0)
    elif attack_type == 'Brute Force':
        for i in range(30, 40): x[i] += random.uniform(2.0, 5.0)
        for i in range(50, 55): x[i] += random.uniform(1.0, 3.0)
    elif attack_type == 'DHCP Starvation':
        for i in range(35, 45): x[i] += random.uniform(2.0, 4.0)
        for i in range(60, 65): x[i] += random.uniform(1.5, 3.0)
    elif attack_type == 'DHCP Spoofing':
        for i in range(40, 50): x[i] += random.uniform(2.0, 4.5)
        for i in range(70, 75): x[i] += random.uniform(1.0, 2.5)
    elif attack_type == 'Sniffing Pasivo':
        for i in range(45, 55): x[i] += random.uniform(1.0, 2.0)
        for i in range(55, 60): x[i] += random.uniform(0.5, 1.5)
    return x

def seed_traffic(count: int = 200, attacker_rate: float = 0.12):
    db = TrafficSessionLocal()
    try:
        print(f"[manage] Insertando {count} entradas de tráfico simulado...")
        attacker_ip = None
        burst_remaining = 0
        burst_type = None
        for _ in range(count):
            if burst_remaining > 0:
                source_ip = attacker_ip
                burst_remaining -= 1
                features = _generate_attack_features(burst_type)
            else:
                source_ip = f"192.168.1.{random.randint(2, 254)}"
                if random.random() < attacker_rate:
                    attacker_ip = source_ip
                    burst_type = random.choice(ATTACK_CLASSES)
                    burst_remaining = random.randint(4, 9)
                    features = _generate_attack_features(burst_type)
                else:
                    features = [random.gauss(0.0, 0.8) for _ in range(80)]

            entry = NetworkTraffic(
                source_ip=source_ip,
                destination_ip="192.168.1.1",
                features_csv=",".join(str(x) for x in features),
            )
            db.add(entry)
        db.commit()
        print("[manage] Tráfico de prueba sembrado con éxito.")
    finally:
        db.close()


def show_status():
    db = SecuritySessionLocal()
    traffic_db = TrafficSessionLocal()
    try:
        users = db.query(User).count()
        traffic = traffic_db.query(NetworkTraffic).count()
        print(f"[manage] Usuarios: {users}")
        print(f"[manage] Entradas de tráfico: {traffic}")
    finally:
        db.close()
        traffic_db.close()


def main():
    parser = argparse.ArgumentParser(description="Gestión de base de datos SMAR-IA")
    parser.add_argument("command", choices=["migrate", "seed-admin", "seed-traffic", "status"], help="Comando a ejecutar")
    parser.add_argument("--password", default="admin123", help="Contraseña para el usuario admin")
    parser.add_argument("--count", type=int, default=200, help="Cantidad de entradas de tráfico a generar")
    args = parser.parse_args()

    if args.command == "migrate":
        migrate()
    elif args.command == "seed-admin":
        seed_admin(args.password)
    elif args.command == "seed-traffic":
        seed_traffic(args.count)
    elif args.command == "status":
        show_status()


if __name__ == "__main__":
    main()
