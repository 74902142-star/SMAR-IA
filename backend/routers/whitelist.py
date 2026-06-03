"""SMAR-IA — Router de whitelist: gestión de IPs exentas de bloqueo."""

import ipaddress
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import get_security_db, Whitelist
from auth import require_role, get_current_user

router = APIRouter(prefix="/api/whitelist", tags=["whitelist"])


class WhitelistAddRequest(BaseModel):
    """Solicitud para añadir IP a whitelist."""
    ip: str = Field(..., description="Dirección IPv4 a eximir de bloqueo")
    reason: Optional[str] = ""


def _validate_ip(ip: str) -> str:
    """Valida formato IPv4."""
    try:
        return str(ipaddress.ip_address(ip.strip()))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"IP inválida: {ip}") from exc


@router.get("/")
def get_whitelist(
    db: Session = Depends(get_security_db),
    current_user=Depends(get_current_user),
):
    """Retorna todas las IPs en whitelist."""
    entries = db.query(Whitelist).order_by(Whitelist.created_at.desc()).all()
    return [
        {
            "id": e.id,
            "ip": e.ip,
            "reason": e.reason,
            "created_at": e.created_at.isoformat() if e.created_at else None,
            "created_by": e.created_by,
        }
        for e in entries
    ]


@router.post("/", dependencies=[Depends(require_role("admin"))])
def add_to_whitelist(
    request: WhitelistAddRequest,
    db: Session = Depends(get_security_db),
    current_user=Depends(get_current_user),
):
    """Añade una IP a la whitelist (solo admin)."""
    ip = _validate_ip(request.ip)
    existing = db.query(Whitelist).filter(Whitelist.ip == ip).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"IP {ip} ya está en la whitelist")
    entry = Whitelist(ip=ip, reason=request.reason, created_by=current_user.username)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return {
        "id": entry.id,
        "ip": entry.ip,
        "reason": entry.reason,
        "created_at": entry.created_at.isoformat() if entry.created_at else None,
        "created_by": entry.created_by,
    }


@router.delete("/{entry_id}", dependencies=[Depends(require_role("admin"))])
def remove_from_whitelist(
    entry_id: int,
    db: Session = Depends(get_security_db),
    current_user=Depends(get_current_user),
):
    """Elimina una IP de la whitelist (solo admin)."""
    entry = db.query(Whitelist).filter(Whitelist.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entrada no encontrada")
    db.delete(entry)
    db.commit()
    return {"status": "success", "message": f"IP {entry.ip} eliminada de whitelist"}


def is_whitelisted(db: Session, ip: str) -> bool:
    """Verifica si una IP está en whitelist."""
    return db.query(Whitelist).filter(Whitelist.ip == ip).first() is not None
