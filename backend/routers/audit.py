from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from database import get_security_db, AuditLog
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
