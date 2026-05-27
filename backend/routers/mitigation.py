from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session
from database import get_security_db, SecurityLog, BlockedIP
from auth import get_current_user, require_role
from config import SUSPICIOUS_ALERT_COUNT, SUSPICIOUS_WINDOW_MINUTES
from datetime import datetime, timedelta
from typing import Optional
import collections
from event_manager import manager
from routers.audit import record_audit
from firewall import apply_iptables_block, remove_iptables_block
from audit_logger import write_audit_log

router = APIRouter(prefix="/api/mitigation", tags=["mitigation"])

# En memoria para demo: registro de IPs y conteo de alertas recientes
# Formato: { "ip": [timestamp1, timestamp2, ...] }
suspicious_ips_tracker = collections.defaultdict(list)

class MitigateRequest(BaseModel):
    ip: str
    action: str # "BLOCK_IP", "CLOSE_TCP", "CLOSE_UDP"
    port: Optional[int] = None
    attack_type: str = "Manual"
    expires_minutes: Optional[int] = None


def add_suspicious_activity(ip: str):
    now = datetime.utcnow()
    suspicious_ips_tracker[ip].append(now)
    suspicious_ips_tracker[ip] = [t for t in suspicious_ips_tracker[ip] if now - t < timedelta(minutes=SUSPICIOUS_WINDOW_MINUTES)]


def is_ip_blocked(db: Session, ip: str) -> bool:
    return db.query(BlockedIP).filter(BlockedIP.ip == ip, BlockedIP.is_active == 1).first() is not None


def get_active_blocked_ips(db: Session):
    return db.query(BlockedIP).filter(BlockedIP.is_active == 1).order_by(BlockedIP.blocked_at.desc()).all()


def _get_recent_suspicious_from_logs(db: Session):
    since = datetime.utcnow() - timedelta(minutes=SUSPICIOUS_WINDOW_MINUTES)
    rows = db.query(
        SecurityLog.source_ip,
        func.count(SecurityLog.id).label("count"),
        func.max(SecurityLog.timestamp).label("last_seen")
    ).filter(
        SecurityLog.timestamp >= since,
        SecurityLog.attack_type != "Normal",
        SecurityLog.attack_type != "Unknown",
        SecurityLog.action_taken == "ALERTED (Pending Manual Review)"
    ).group_by(SecurityLog.source_ip).all()

    suspicious = []
    for row in rows:
        if row.count >= SUSPICIOUS_ALERT_COUNT and not is_ip_blocked(db, row.source_ip):
            suspicious.append({
                "ip": row.source_ip,
                "alerts": row.count,
                "last_seen": row.last_seen.isoformat() if row.last_seen else None,
            })

    return suspicious


def record_block(db: Session, ip: str, method: str, reason: str, action_taken: str, expires_at=None):
    blocked = db.query(BlockedIP).filter(BlockedIP.ip == ip).first()
    if blocked:
        blocked.blocked_at = datetime.utcnow()
        blocked.expires_at = expires_at
        blocked.method = method
        blocked.reason = reason
        blocked.is_active = 1
    else:
        blocked = BlockedIP(
            ip=ip,
            blocked_at=datetime.utcnow(),
            expires_at=expires_at,
            method=method,
            reason=reason,
            is_active=1,
        )
        db.add(blocked)
    db.commit()
    return blocked


@router.get("/suspicious")
def get_suspicious_ips(current_user=Depends(get_current_user), db: Session = Depends(get_security_db)):
    return _get_recent_suspicious_from_logs(db)


@router.get("/blocked")
def get_blocked_list(current_user=Depends(get_current_user), db: Session = Depends(get_security_db)):
    blocked = get_active_blocked_ips(db)
    return [
        {
            "ip": entry.ip,
            "blocked_at": entry.blocked_at.isoformat() if entry.blocked_at else None,
            "expires_at": entry.expires_at.isoformat() if entry.expires_at else None,
            "method": entry.method,
            "reason": entry.reason,
            "remaining_seconds": (
                int((entry.expires_at - datetime.utcnow()).total_seconds())
                if entry.expires_at and entry.expires_at > datetime.utcnow()
                else None
            ),
        }
        for entry in blocked
    ]


@router.get("/active")
def get_active_threats(current_user=Depends(get_current_user), db: Session = Depends(get_security_db)):
    suspicious_data = _get_recent_suspicious_from_logs(db)
    blocked_entries = get_active_blocked_ips(db)

    return {
        "suspicious_ips": suspicious_data,
        "blocked_ips": [
            {
                "ip": entry.ip,
                "blocked_at": entry.blocked_at.isoformat() if entry.blocked_at else None,
                "expires_at": entry.expires_at.isoformat() if entry.expires_at else None,
                "method": entry.method,
                "reason": entry.reason,
                "remaining_seconds": (
                    int((entry.expires_at - datetime.utcnow()).total_seconds())
                    if entry.expires_at and entry.expires_at > datetime.utcnow()
                    else None
                ),
            }
            for entry in blocked_entries
        ],
        "total_suspicious": len(suspicious_data),
        "total_blocked": len(blocked_entries),
    }


@router.post("/block", dependencies=[Depends(require_role("admin"))])
async def block_ip(request: MitigateRequest, db: Session = Depends(get_security_db), current_user=Depends(get_current_user)):
    if not request.ip:
        raise HTTPException(status_code=400, detail="IP requerido para bloqueo")

    if request.action == "BLOCK_IP":
        method = "BLOCK_IP"
    elif request.action == "CLOSE_TCP":
        if not request.port:
            raise HTTPException(status_code=400, detail="Puerto requerido para CLOSE_TCP")
        method = "CLOSE_TCP"
    elif request.action == "CLOSE_UDP":
        if not request.port:
            raise HTTPException(status_code=400, detail="Puerto requerido para CLOSE_UDP")
        method = "CLOSE_UDP"
    else:
        raise HTTPException(status_code=400, detail="Invalid action")

    if is_ip_blocked(db, request.ip):
        return {"status": "success", "message": f"IP {request.ip} is already blocked."}

    # Ejecutar bloqueo iptables y medir latencia
    latency = apply_iptables_block(request.ip)

    expires_at = None
    if request.expires_minutes and request.expires_minutes > 0:
        expires_at = datetime.utcnow() + timedelta(minutes=request.expires_minutes)

    record_block(db, request.ip, method, request.attack_type or "Manual", f"MANUAL: {method}", expires_at=expires_at)

    new_log = SecurityLog(
        source_ip=request.ip,
        destination_ip="Any",
        attack_type=request.attack_type,
        confidence=1.0,
        action_taken=f"MANUAL: {method}",
        iso_control="A.8.20",
        detection_timestamp=datetime.utcnow(),
        mitigation_timestamp=datetime.utcnow(),
        latency_ms=latency if latency >= 0 else None,
    )
    db.add(new_log)
    db.commit()

    record_audit(db, current_user.username, "BLOCK", request.ip, f"method={method}, attack_type={request.attack_type}, latency={latency}ms")

    write_audit_log({
        "event_type": "BLOCK_ADDED",
        "network": {"source_ip": request.ip, "destination_ip": "Any"},
        "detection": {"model_confidence": 1.0, "attack_type": request.attack_type or "Manual"},
        "response": {"mitigation_latency_ms": latency, "action_taken": f"MANUAL: {method}"},
        "iso_compliance": {"controls_activated": ["A.8.15", "A.8.20"]},
        "username": current_user.username,
    })

    if request.ip in suspicious_ips_tracker:
        del suspicious_ips_tracker[request.ip]

    await manager.broadcast({
        "type": "mitigation_event",
        "event": "block",
        "ip": request.ip,
        "method": method,
        "reason": request.attack_type or "Manual",
        "blocked_at": datetime.utcnow().isoformat(),
        "expires_at": expires_at.isoformat() if expires_at else None,
    })

    return {"status": "success", "message": f"Command logged: {method}", "latency_ms": latency}


class UnblockRequest(BaseModel):
    ip: str
    attack_type: Optional[str] = "Unblock"


@router.post("/unblock", dependencies=[Depends(require_role("admin"))])
async def unblock_ip(payload: UnblockRequest, db: Session = Depends(get_security_db), current_user=Depends(get_current_user)):
    ip = payload.ip
    entry = db.query(BlockedIP).filter(BlockedIP.ip == ip, BlockedIP.is_active == 1).first()
    if not entry:
        raise HTTPException(status_code=404, detail="IP not found or not active")

    entry.is_active = 0
    db.commit()

    remove_iptables_block(ip)

    record_audit(db, current_user.username, "UNBLOCK", ip, f"attack_type={payload.attack_type}")

    write_audit_log({
        "event_type": "BLOCK_REMOVED",
        "network": {"source_ip": ip, "destination_ip": "Any"},
        "detection": {"attack_type": payload.attack_type or "Unblock"},
        "response": {"action_taken": f"MANUAL: UNBLOCK {ip}"},
        "iso_compliance": {"controls_activated": ["A.8.15", "A.8.20"]},
        "username": current_user.username,
    })

    new_log = SecurityLog(
        source_ip=ip,
        destination_ip="Any",
        attack_type=payload.attack_type or "Unblock",
        confidence=1.0,
        action_taken=f"MANUAL: UNBLOCK {ip}",
        iso_control="A.8.20"
    )
    db.add(new_log)
    db.commit()

    await manager.broadcast({
        "type": "mitigation_event",
        "event": "unblock",
        "ip": ip,
        "reason": payload.attack_type or "Unblock",
        "unblocked_at": datetime.utcnow().isoformat(),
    })

    return {"status": "success", "message": f"IP {ip} unblocked"}
