"""SMAR-IA — Router de Threat Intelligence."""

from fastapi import APIRouter, Depends
from auth import get_current_user, require_role
from threat_intel import get_threat_intel_stats, is_known_threat

router = APIRouter(prefix="/api/threat-intel", tags=["threat-intel"])


@router.get("/status")
def threat_intel_status():
    return get_threat_intel_stats()


@router.get("/check/{ip}")
def check_ip(ip: str, current_user=Depends(get_current_user)):
    return {"ip": ip, "is_known_threat": is_known_threat(ip)}
