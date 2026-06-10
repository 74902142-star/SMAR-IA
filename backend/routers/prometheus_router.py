"""SMAR-IA — Endpoint Prometheus /metrics para monitoreo externo."""

import time
from fastapi import APIRouter, Depends, Response
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import get_security_db, SecurityLog, BlockedIP
from config import PROMETHEUS_ENABLED, APP_NAME, APP_VERSION
from auth import oauth2_scheme

router = APIRouter(tags=["metrics"])


def _format_metric(name: str, value, labels: dict = None) -> str:
    """Helper para formatear métricas Prometheus."""
    label_str = ""
    if labels:
        parts = [f'{k}="{v}"' for k, v in labels.items()]
        label_str = "{" + ",".join(parts) + "}"
    return f"# HELP {name}\n# TYPE {name} gauge\n{name}{label_str} {value}\n"


@router.get("/metrics")
def prometheus_metrics():
    if not PROMETHEUS_ENABLED:
        return Response("Prometheus disabled", media_type="text/plain")

    db = next(get_security_db())
    try:
        total_logs = db.query(func.count(SecurityLog.id)).scalar() or 0
        total_blocked = db.query(func.count(BlockedIP.id)).filter(BlockedIP.is_active == 1).scalar() or 0
        critical_count = db.query(func.count(SecurityLog.id)).filter(
            SecurityLog.confidence >= 0.90, SecurityLog.attack_type != "Normal"
        ).scalar() or 0
        pending_alerts = db.query(func.count(SecurityLog.id)).filter(
            SecurityLog.action_taken == "ALERTED (Pending Manual Review)"
        ).scalar() or 0
    finally:
        db.close()

    lines = [
        _format_metric("smar_ia_info", 1, {"version": APP_VERSION, "app": APP_NAME}),
        _format_metric("smar_ia_logs_total", total_logs),
        _format_metric("smar_ia_blocked_ips", total_blocked),
        _format_metric("smar_ia_critical_alerts", critical_count),
        _format_metric("smar_ia_pending_alerts", pending_alerts),
    ]

    return Response("".join(lines), media_type="text/plain; version=0.0.4; charset=utf-8")
