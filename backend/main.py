import asyncio
import json
from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import get_security_db, get_traffic_db, SecurityLog, NetworkTraffic, init_db
from ml_service import ml_service
from datetime import datetime

from routers import auth, mitigation, system
from config import print_config_summary, AUTO_BLOCK_THRESHOLD, DRY_RUN

app = FastAPI(title="IDS Security Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(mitigation.router)
app.include_router(system.router)

@app.on_event("startup")
async def startup_event():
    print_config_summary()
    init_db()
    ml_service.load_models()
    asyncio.create_task(process_traffic_loop())

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception:
                pass

manager = ConnectionManager()

async def process_traffic_loop():
    print("Iniciando bucle de procesamiento de tráfico...")
    while True:
        db_traffic = next(get_traffic_db())
        db_security = next(get_security_db())
        
        try:
            unprocessed_traffic = db_traffic.query(NetworkTraffic).filter(NetworkTraffic.is_processed == 0).all()
            
            for traffic in unprocessed_traffic:
                features = [float(x) for x in traffic.features_csv.split(",")]
                attack_type, confidence = ml_service.predict(features)
                
                action_taken = "NONE"
                is_alert = False
                
                # Ignorar tráfico si la IP ya está bloqueada (manual o automáticamente)
                from routers.mitigation import blocked_ips, add_suspicious_activity
                if traffic.source_ip in blocked_ips:
                    traffic.is_processed = 1
                    db_traffic.commit()
                    continue

                if attack_type != "Normal" and attack_type != "Unknown":
                    is_alert = True
                    add_suspicious_activity(traffic.source_ip)
                    
                    # Lógica Híbrida: Si la IA está extremadamente segura (>umbral), mitiga sola. 
                    # Si no, lo deja como alerta para mitigación manual.
                    if confidence >= AUTO_BLOCK_THRESHOLD:
                        if DRY_RUN:
                            action_taken = f"DRY-RUN: iptables -A INPUT -s {traffic.source_ip} -j DROP"
                        else:
                            action_taken = f"AUTO-BLOCKED: iptables -A INPUT -s {traffic.source_ip} -j DROP"
                            blocked_ips.add(traffic.source_ip)
                    else:
                        action_taken = "ALERTED (Pending Manual Review)"
                    
                    # Registrar log
                    new_log = SecurityLog(
                        source_ip=traffic.source_ip,
                        destination_ip=traffic.destination_ip,
                        attack_type=attack_type,
                        confidence=confidence,
                        action_taken=action_taken
                    )
                    db_security.add(new_log)
                    db_security.commit()
                
                traffic.is_processed = 1
                db_traffic.commit()
                
                ws_message = {
                    "type": "traffic_update",
                    "timestamp": traffic.timestamp.isoformat(),
                    "source_ip": traffic.source_ip,
                    "destination_ip": traffic.destination_ip,
                    "predicted_class": attack_type,
                    "confidence": confidence,
                    "is_alert": is_alert,
                    "action_taken": action_taken
                }
                await manager.broadcast(ws_message)
                
        except Exception as e:
            print(f"Error procesando tráfico: {e}")
        finally:
            db_traffic.close()
            db_security.close()
            
        await asyncio.sleep(1)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/api/logs")
def get_logs(db: Session = Depends(get_security_db), limit: int = 50):
    logs = db.query(SecurityLog).order_by(SecurityLog.timestamp.desc()).limit(limit).all()
    return logs
