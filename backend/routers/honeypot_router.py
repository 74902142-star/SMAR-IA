"""SMAR-IA — Router de Honeypot."""

from fastapi import APIRouter, Depends
from auth import get_current_user, require_role
from honeypot import get_honeypot_hits, get_honeypot_hits_since, clear_honeypot_hits
from config import HONEYPOT_ENABLED

router = APIRouter(prefix="/api/honeypot", tags=["honeypot"])


@router.get("/status")
def honeypot_status():
    return {
        "enabled": HONEYPOT_ENABLED,
        "hits_count": len(get_honeypot_hits()),
    }


@router.get("/hits")
def list_honeypot_hits(current_user=Depends(get_current_user)):
    return {"hits": get_honeypot_hits()}


@router.post("/clear")
def clear_hits(current_user=Depends(require_role("admin"))):
    clear_honeypot_hits()
    return {"status": "cleared"}
