from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_security_db, AuditLog, SecurityLog, BlockedIP
from auth import get_current_user, require_role
from audit_logger import write_audit_log, read_audit_logs, get_available_dates

router = APIRouter(prefix="/api/audit", tags=["audit"])


@router.get("/")
def get_audit_logs(
    limit: int = 50,
    db: Session = Depends(get_security_db),
    current_user = Depends(get_current_user),
):
    logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit).all()
    return [
        {
            "id": log.id,
            "timestamp": log.timestamp.isoformat() if log.timestamp else None,
            "username": log.username,
            "action": log.action,
            "target": log.target,
            "details": log.details,
            "iso_control": log.iso_control,
        }
        for log in logs
    ]


@router.get("/json")
def get_json_audit_logs(
    date: str = Query(None, description="Fecha en formato YYYY-MM-DD"),
    current_user = Depends(require_role("admin")),
):
    """
    Endpoint protegido para descargar logs de auditoría en formato JSON
    con hash de integridad (ISO A.8.15).
    """
    events = read_audit_logs(date)
    return JSONResponse(content=events)


@router.get("/dates")
def get_audit_dates(
    current_user = Depends(require_role("admin")),
):
    """Lista las fechas disponibles de logs de auditoría."""
    return {"dates": get_available_dates()}


@router.get("/report")
def get_audit_report(
    days: int = Query(7, description="Ventana de tiempo en días"),
    current_user = Depends(require_role("admin")),
    db: Session = Depends(get_security_db),
):
    """Genera un reporte de auditoría resumido: eventos, alertas, bloqueos."""
    since = datetime.now(timezone.utc) - timedelta(days=days)

    total_events = db.query(func.count(AuditLog.id)).filter(AuditLog.timestamp >= since).scalar() or 0
    total_alerts = db.query(func.count(SecurityLog.id)).filter(
        SecurityLog.timestamp >= since,
        SecurityLog.attack_type.notin_(["Normal", "Unknown", "Auto-Unblock"]),
    ).scalar() or 0
    total_blocks = db.query(func.count(BlockedIP.id)).filter(BlockedIP.blocked_at >= since).scalar() or 0
    unique_ips = db.query(func.count(func.distinct(SecurityLog.source_ip))).filter(
        SecurityLog.timestamp >= since,
        SecurityLog.attack_type.notin_(["Normal", "Unknown"]),
    ).scalar() or 0

    top_attacks = db.query(
        SecurityLog.attack_type, func.count(SecurityLog.id).label("count")
    ).filter(
        SecurityLog.timestamp >= since,
        SecurityLog.attack_type.notin_(["Normal", "Unknown"]),
    ).group_by(SecurityLog.attack_type).order_by(func.count(SecurityLog.id).desc()).limit(5).all()

    return {
        "period_days": days,
        "since": since.isoformat(),
        "total_events": total_events,
        "total_alerts": total_alerts,
        "total_blocks": total_blocks,
        "unique_attack_ips": unique_ips,
        "top_attacks": [{"attack_type": a, "count": c} for a, c in top_attacks],
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def record_audit(db: Session, username: str, action: str, target: str, details: str = ""):
    log = AuditLog(
        username=username,
        action=action,
        target=target,
        details=details,
    )
    db.add(log)
    db.commit()
    write_audit_log({
        "event_type": f"AUDIT_{action}",
        "network": {"source_ip": target},
        "detection": {},
        "response": {"action_taken": details},
        "iso_compliance": {"controls_activated": ["A.8.21"]},
        "username": username,
    })
