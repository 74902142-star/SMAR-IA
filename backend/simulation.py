import time
import random
import numpy as np
from database import TrafficSessionLocal, NetworkTraffic
from datetime import datetime, timezone

def generate_ip():
    return f"192.168.1.{random.randint(2, 254)}"

def simulate_traffic():
    print("Iniciando simulador de tráfico AVANZADO...")
    db = TrafficSessionLocal()
    
    # Mantener una IP atacante persistente por un tiempo para forzar que aparezca en la Zona de Mitigación
    current_attacker_ip = None
    attack_burst_remaining = 0

    try:
        while True:
            # Lógica para ráfagas de ataques desde una misma IP
            if attack_burst_remaining > 0:
                source_ip = current_attacker_ip
                # Forzar características anómalas severas
                features = np.random.randn(80) * 10 + 20
                attack_burst_remaining -= 1
                sleep_time = random.uniform(0.1, 0.3) # Muy rápido (ráfaga)
                print(f"[{datetime.now(timezone.utc)}] [ALERTA] Ráfaga de ataque desde {source_ip} (Restantes: {attack_burst_remaining})")
            else:
                source_ip = generate_ip()
                features = np.random.randn(80)
                sleep_time = random.uniform(0.5, 2.0)
                
                # Ocasionalmente iniciar un nuevo ataque
                if random.random() < 0.05: # 5% de probabilidad de iniciar ráfaga
                    current_attacker_ip = source_ip
                    attack_burst_remaining = random.randint(4, 8) # 4 a 8 peticiones seguidas
                    print(f"\n--- NUEVA RÁFAGA DE ATAQUE DETECTADA DESDE {current_attacker_ip} ---\n")
                
            features_csv = ",".join(map(str, features))
            
            traffic_entry = NetworkTraffic(
                source_ip=source_ip,
                destination_ip="192.168.1.1",
                features_csv=features_csv
            )
            
            db.add(traffic_entry)
            db.commit()
            
            if attack_burst_remaining == 0:
                print(f"[{datetime.now(timezone.utc)}] Tráfico normal desde {traffic_entry.source_ip}")
            
            time.sleep(sleep_time)
    except KeyboardInterrupt:
        print("Simulador detenido.")
    finally:
        db.close()

if __name__ == "__main__":
    simulate_traffic()
