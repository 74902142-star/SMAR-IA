from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_security_db, SecurityLog
from auth import get_current_user
from datetime import datetime, timedelta
import collections

router = APIRouter(prefix="/api/mitigation", tags=["mitigation"])

# En memoria para demo: registro de IPs y conteo de alertas recientes
# Formato: { "ip": [timestamp1, timestamp2, ...] }
suspicious_ips_tracker = collections.defaultdict(list)
blocked_ips = set()

class MitigateRequest(BaseModel):
    ip: str
    action: str # "BLOCK_IP", "CLOSE_TCP", "CLOSE_UDP"
    port: int = None
    attack_type: str = "Manual"

def add_suspicious_activity(ip: str):
    now = datetime.utcnow()
    suspicious_ips_tracker[ip].append(now)
    # Limpiar eventos mayores a 5 minutos
    suspicious_ips_tracker[ip] = [t for t in suspicious_ips_tracker[ip] if now - t < timedelta(minutes=5)]

@router.get("/suspicious")
def get_suspicious_ips(current_user = Depends(get_current_user)):
    # Retornar IPs con más de 3 alertas en los últimos 5 minutos
    suspicious = []
    now = datetime.utcnow()
    for ip, timestamps in list(suspicious_ips_tracker.items()):
        # Limpiar
        valid_times = [t for t in timestamps if now - t < timedelta(minutes=5)]
        suspicious_ips_tracker[ip] = valid_times
        
        if len(valid_times) >= 3 and ip not in blocked_ips:
            suspicious.append({
                "ip": ip,
                "alert_count": len(valid_times),
                "last_seen": valid_times[-1] if valid_times else None
            })
    return suspicious

@router.post("/block")
def block_ip(request: MitigateRequest, db: Session = Depends(get_security_db), current_user = Depends(get_current_user)):
    if request.action == "BLOCK_IP":
        command = f"iptables -A INPUT -s {request.ip} -j DROP"
    elif request.action == "CLOSE_TCP":
        command = f"iptables -A INPUT -p tcp --dport {request.port} -s {request.ip} -j DROP"
    elif request.action == "CLOSE_UDP":
        command = f"iptables -A INPUT -p udp --dport {request.port} -s {request.ip} -j DROP"
    else:
        raise HTTPException(status_code=400, detail="Invalid action")

    # Registrar en DB (ISO A.8.15 y A.8.20)
    new_log = SecurityLog(
        source_ip=request.ip,
        destination_ip="Any",
        attack_type=request.attack_type,
        confidence=1.0,
        action_taken=f"MANUAL: {command}",
        iso_control="A.8.20"
    )
    db.add(new_log)
    db.commit()

    # Marcar como bloqueada
    blocked_ips.add(request.ip)
    # Limpiar de sospechosas
    if request.ip in suspicious_ips_tracker:
        del suspicious_ips_tracker[request.ip]

    return {"status": "success", "message": f"Command logged: {command}"}
