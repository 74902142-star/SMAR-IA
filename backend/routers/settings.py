"""SMAR-IA — Endpoints para persistir configuración del frontend."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_security_db, AppSetting
from auth import get_current_user, require_role

router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("/")
def get_all_settings(db: Session = Depends(get_security_db)):
    """Retorna todas las configuraciones como dict clave→valor."""
    settings = db.query(AppSetting).all()
    return {s.key: s.value for s in settings}


@router.get("/{key}")
def get_setting(key: str, db: Session = Depends(get_security_db)):
    """Retorna el valor de una configuración específica."""
    setting = db.query(AppSetting).filter(AppSetting.key == key).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    return {"key": setting.key, "value": setting.value}


@router.put("/{key}")
def update_setting(key: str, value: str, db: Session = Depends(get_security_db),
                   current_user=Depends(require_role("admin"))):
    """Crea o actualiza una configuración. Solo admin."""
    setting = db.query(AppSetting).filter(AppSetting.key == key).first()
    if setting:
        setting.value = value
    else:
        setting = AppSetting(key=key, value=value)
        db.add(setting)
    db.commit()
    return {"key": key, "value": value}


@router.post("/bulk")
def update_bulk(payload: dict, db: Session = Depends(get_security_db),
                current_user=Depends(require_role("admin"))):
    """Actualiza múltiples configuraciones a la vez. Solo admin."""
    for key, value in payload.items():
        setting = db.query(AppSetting).filter(AppSetting.key == key).first()
        if setting:
            setting.value = value
        else:
            setting = AppSetting(key=key, value=str(value))
            db.add(setting)
    db.commit()
    return {"message": f"{len(payload)} settings saved"}
