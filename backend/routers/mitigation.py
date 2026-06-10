"""SMAR-IA — Router de mitigación: bloqueo/desbloqueo de IPs con iptables."""

import collections
import ipaddress
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

logger = logging.getLogger("smar-ia-mitigation")

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import get_security_db, SecurityLog, BlockedIP
from auth import get_current_user, require_role
from config import SUSPICIOUS_ALERT_COUNT, SUSPICIOUS_WINDOW_MINUTES, FIREWALL_BACKEND, DRY_RUN
from event_manager import manager
from routers.audit import record_audit
from firewall import apply_iptables_block, remove_iptables_block
from audit_logger import write_audit_log
from progressive_block import get_block_duration, register_block
from siem_integration import send_event as send_siem_event

router = APIRouter(prefix="/api/mitigation", tags=["mitigation"])

suspicious_ips_tracker = collections.defaultdict(list)


class MitigateRequest(BaseModel):
    """Solicitud de bloqueo con validación de IP."""
    ip: str = Field(..., description="Dirección IPv4 a bloquear")
    action: str = Field(..., pattern="^(BLOCK_IP|CLOSE_TCP|CLOSE_UDP)$")
    port: Optional[int] = Field(None, ge=1, le=65535)
    attack_type: str = "Manual"
    expires_minutes: Optional[int] = Field(None, ge=1, le=43200)

    class Config:
        json_schema_extra = {
            "example": {"ip": "192.168.1.100", "action": "BLOCK_IP", "attack_type": "DDoS SYN Flood"}
        }


class UnblockRequest(BaseModel):
    """Solicitud de desbloqueo."""
    ip: str = Field(..., description="Dirección IPv4 a desbloquear")
    attack_type: Optional[str] = "Unblock"


def _validate_ip(ip: str) -> str:
    """Valida formato IPv4 y retorna IP normalizada."""
    try:
        return str(ipaddress.ip_address(ip.strip()))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"IP inválida: {ip}") from exc


def add_suspicious_activity(ip: str):
    """Registra actividad sospechosa de una IP en la ventana de tiempo."""
    now = datetime.now(timezone.utc)
    suspicious_ips_tracker[ip].append(now)
    suspicious_ips_tracker[ip] = [
        t for t in suspicious_ips_tracker[ip]
        if now - t < timedelta(minutes=SUSPICIOUS_WINDOW_MINUTES)
    ]


def is_ip_blocked(db: Session, ip: str) -> bool:
    """Verifica si una IP está activamente bloqueada en BD."""
    return db.query(BlockedIP).filter(BlockedIP.ip == ip, BlockedIP.is_active == 1).first() is not None


def get_active_blocked_ips(db: Session):
    """Retorna todas las IPs bloqueadas activas."""
    return db.query(BlockedIP).filter(BlockedIP.is_active == 1).order_by(BlockedIP.blocked_at.desc()).all()


def _get_recent_suspicious_from_logs(db: Session):
    """Obtiene IPs sospechosas desde los logs de seguridad."""
    since = datetime.now(timezone.utc) - timedelta(minutes=SUSPICIOUS_WINDOW_MINUTES)
    rows = (
        db.query(
            SecurityLog.source_ip,
            func.count(SecurityLog.id).label("count"),
            func.max(SecurityLog.timestamp).label("last_seen"),
        )
        .filter(
            SecurityLog.timestamp >= since,
            SecurityLog.attack_type.notin_(["Normal", "Unknown"]),
            SecurityLog.action_taken == "ALERTED (Pending Manual Review)",
        )
        .group_by(SecurityLog.source_ip)
        .all()
    )
    return [
        {
            "ip": row.source_ip,
            "alerts": row.count,
            "last_seen": row.last_seen.isoformat() if row.last_seen else None,
        }
        for row in rows
        if row.count >= SUSPICIOUS_ALERT_COUNT and not is_ip_blocked(db, row.source_ip)
    ]


def record_block(db: Session, ip: str, method: str, reason: str, action_taken: str, expires_at=None):
    """Persiste un bloqueo en la tabla blocked_ips."""
    blocked = db.query(BlockedIP).filter(BlockedIP.ip == ip).first()
    if blocked:
        blocked.blocked_at = datetime.now(timezone.utc)
        blocked.expires_at = expires_at
        blocked.method = method
        blocked.reason = reason
        blocked.is_active = 1
    else:
        blocked = BlockedIP(
            ip=ip,
            blocked_at=datetime.now(timezone.utc),
            expires_at=expires_at,
            method=method,
            reason=reason,
            is_active=1,
        )
        db.add(blocked)
    db.commit()
    return blocked


# ── Endpoints ───────────────────────────────────────────────────────────


@router.get("/suspicious")
def get_suspicious_ips(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_security_db),
):
    """Retorna IPs con actividad sospechosa pendiente de revisión."""
    return _get_recent_suspicious_from_logs(db)


@router.get("/blocked")
def get_blocked_list(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_security_db),
):
    """Retorna lista de IPs bloqueadas activamente."""
    blocked = get_active_blocked_ips(db)
    return [
        {
            "ip": entry.ip,
            "blocked_at": entry.blocked_at.isoformat() if entry.blocked_at else None,
            "expires_at": entry.expires_at.isoformat() if entry.expires_at else None,
            "method": entry.method,
            "reason": entry.reason,
            "remaining_seconds": (
                int((entry.expires_at - datetime.now(timezone.utc)).total_seconds())
                if entry.expires_at and entry.expires_at > datetime.now(timezone.utc)
                else None
            ),
        }
        for entry in blocked
    ]


@router.get("/active")
def get_active_threats(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_security_db),
):
    """Retorna amenazas activas: IPs sospechosas + bloqueadas."""
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
                    int((entry.expires_at - datetime.now(timezone.utc)).total_seconds())
                    if entry.expires_at and entry.expires_at > datetime.now(timezone.utc)
                    else None
                ),
            }
            for entry in blocked_entries
        ],
        "total_suspicious": len(suspicious_data),
        "total_blocked": len(blocked_entries),
    }


@router.post("/block", dependencies=[Depends(require_role("admin"))])
async def block_ip(
    request: MitigateRequest,
    db: Session = Depends(get_security_db),
    current_user=Depends(get_current_user),
):
    """Bloquea una IP manualmente ejecutando iptables."""
    ip = _validate_ip(request.ip)
    method = request.action

    if method in ("CLOSE_TCP", "CLOSE_UDP") and not request.port:
        raise HTTPException(status_code=400, detail=f"Puerto requerido para {method}")

    if is_ip_blocked(db, ip):
        return {"status": "success", "message": f"IP {ip} is already blocked."}

    duration = get_block_duration(ip) if not request.expires_minutes else request.expires_minutes * 60
    if FIREWALL_BACKEND == "nftables":
        from firewall_nftables import nft_block_ip
        latency = nft_block_ip(ip, duration) if not DRY_RUN else 0.0
    else:
        latency = apply_iptables_block(ip)
    expires_at = (
        datetime.now(timezone.utc) + timedelta(minutes=request.expires_minutes or duration // 60)
        if (request.expires_minutes or duration) > 0
        else None
    )

    record_block(db, ip, method, request.attack_type or "Manual", f"MANUAL: {method}", expires_at=expires_at)
    register_block(ip)
    send_siem_event("manual_block", ip, f"{method}: {request.attack_type}", severity=5)

    log = SecurityLog(
        source_ip=ip,
        destination_ip="Any",
        attack_type=request.attack_type,
        confidence=1.0,
        action_taken=f"MANUAL: {method}",
        iso_control="A.8.20",
        detection_timestamp=datetime.now(timezone.utc),
        mitigation_timestamp=datetime.now(timezone.utc),
        latency_ms=latency if latency >= 0 else None,
    )
    db.add(log)
    db.commit()

    record_audit(db, current_user.username, "BLOCK", ip, f"method={method}, latency={latency}ms")

    write_audit_log({
        "event_type": "BLOCK_ADDED",
        "network": {"source_ip": ip, "destination_ip": "Any"},
        "detection": {"model_confidence": 1.0, "attack_type": request.attack_type or "Manual"},
        "response": {"mitigation_latency_ms": latency, "action_taken": f"MANUAL: {method}"},
        "iso_compliance": {"controls_activated": ["A.8.15", "A.8.20"]},
        "username": current_user.username,
    })

    suspicious_ips_tracker.pop(ip, None)

    await manager.broadcast({
        "type": "mitigation_event",
        "event": "block",
        "ip": ip,
        "method": method,
        "reason": request.attack_type or "Manual",
        "blocked_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": expires_at.isoformat() if expires_at else None,
    })

    return {"status": "success", "message": f"Command logged: {method}", "latency_ms": latency}


@router.post("/unblock", dependencies=[Depends(require_role("admin"))])
async def unblock_ip(
    payload: UnblockRequest,
    db: Session = Depends(get_security_db),
    current_user=Depends(get_current_user),
):
    """Desbloquea una IP eliminando la regla iptables."""
    ip = _validate_ip(payload.ip)
    entry = db.query(BlockedIP).filter(BlockedIP.ip == ip, BlockedIP.is_active == 1).first()
    if not entry:
        raise HTTPException(status_code=404, detail="IP not found or not active")

    entry.is_active = 0
    db.commit()

    if FIREWALL_BACKEND == "nftables":
        from firewall_nftables import nft_unblock_ip
        nft_unblock_ip(ip)
    else:
        remove_iptables_block(ip)

    from progressive_block import reset_offender
    reset_offender(ip)

    record_audit(db, current_user.username, "UNBLOCK", ip, f"attack_type={payload.attack_type}")

    write_audit_log({
        "event_type": "BLOCK_REMOVED",
        "network": {"source_ip": ip, "destination_ip": "Any"},
        "detection": {"attack_type": payload.attack_type or "Unblock"},
        "response": {"action_taken": f"MANUAL: UNBLOCK {ip}"},
        "iso_compliance": {"controls_activated": ["A.8.15", "A.8.20"]},
        "username": current_user.username,
    })

    log = SecurityLog(
        source_ip=ip,
        destination_ip="Any",
        attack_type=payload.attack_type or "Unblock",
        confidence=1.0,
        action_taken=f"MANUAL: UNBLOCK {ip}",
        iso_control="A.8.20",
    )
    db.add(log)
    db.commit()

    await manager.broadcast({
        "type": "mitigation_event",
        "event": "unblock",
        "ip": ip,
        "reason": payload.attack_type or "Unblock",
        "unblocked_at": datetime.now(timezone.utc).isoformat(),
    })

    return {"status": "success", "message": f"IP {ip} unblocked"}
