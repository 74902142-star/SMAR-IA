"""SMAR-IA — Router de bloqueo progresivo."""

from fastapi import APIRouter, Depends
from auth import get_current_user, require_role
from progressive_block import get_offenders_summary, reset_offender
from config import PROGRESSIVE_BLOCK_ENABLED

router = APIRouter(prefix="/api/progressive-block", tags=["progressive-block"])


@router.get("/status")
def progressive_block_status():
    return {
        "enabled": PROGRESSIVE_BLOCK_ENABLED,
        "offenders": get_offenders_summary(),
    }


@router.post("/reset/{ip}")
def reset_ip(ip: str, current_user=Depends(require_role("admin"))):
    reset_offender(ip)
    return {"status": "reset", "ip": ip}
