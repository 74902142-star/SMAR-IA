import time
import random
import numpy as np
from database import TrafficSessionLocal, NetworkTraffic
from datetime import datetime, timezone

ATTACK_CLASSES = ['DDoS SYN Flood', 'DDoS UDP Flood', 'Sniffing Pasivo',
                  'DHCP Starvation', 'DHCP Spoofing', 'Port Scanning', 'Brute Force']

def generate_ip():
    return f"192.168.1.{random.randint(2, 254)}"

def _gen_attack_features(attack_type: str) -> list:
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

def simulate_traffic():
    print("Iniciando simulador de tráfico...")
    db = TrafficSessionLocal()
    current_attacker_ip = None
    attack_burst_remaining = 0
    current_attack_type = None

    try:
        while True:
            if attack_burst_remaining > 0:
                source_ip = current_attacker_ip
                features = _gen_attack_features(current_attack_type)
                attack_burst_remaining -= 1
                sleep_time = random.uniform(0.1, 0.3)
                print(f"[{datetime.now(timezone.utc)}] [ATAQUE] {current_attack_type} desde {source_ip} ({attack_burst_remaining} restantes)")
            else:
                source_ip = generate_ip()
                if random.random() < 0.05:
                    current_attacker_ip = source_ip
                    current_attack_type = random.choice(ATTACK_CLASSES)
                    attack_burst_remaining = random.randint(4, 8)
                    features = _gen_attack_features(current_attack_type)
                    attack_burst_remaining -= 1
                    sleep_time = random.uniform(0.1, 0.3)
                    print(f"\n--- NUEVO ATAQUE: {current_attack_type} desde {current_attacker_ip} ---\n")
                else:
                    features = [random.gauss(0.0, 0.8) for _ in range(80)]
                    sleep_time = random.uniform(0.5, 2.0)
                    print(f"[{datetime.now(timezone.utc)}] Tráfico normal desde {source_ip}")

            traffic_entry = NetworkTraffic(
                source_ip=source_ip,
                destination_ip="192.168.1.1",
                features_csv=",".join(map(str, features))
            )
            db.add(traffic_entry)
            db.commit()
            time.sleep(sleep_time)
    except KeyboardInterrupt:
        print("Simulador detenido.")
    finally:
        db.close()

if __name__ == "__main__":
    simulate_traffic()
