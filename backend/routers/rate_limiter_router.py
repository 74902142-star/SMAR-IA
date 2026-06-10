"""SMAR-IA — Router de rate limiter de firewall."""

from fastapi import APIRouter, Depends
from auth import get_current_user
from rate_limiter_firewall import get_rate_limit_status, get_ip_event_count

router = APIRouter(prefix="/api/rate-limiter", tags=["rate-limiter"])


@router.get("/status")
def rate_limiter_status(current_user=Depends(get_current_user)):
    return {
        "top_offenders": dict(list(get_rate_limit_status().items())[:20]),
        "total_tracked_ips": len(get_rate_limit_status()),
    }


@router.get("/check/{ip}")
def check_ip_rate(ip: str, current_user=Depends(get_current_user)):
    return {"ip": ip, "events_in_window": get_ip_event_count(ip)}
