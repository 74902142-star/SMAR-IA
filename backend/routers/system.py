"""
SMAR-IA — Router de Sistema
Endpoints de salud, estadísticas y métricas (ISO A.8.16).
"""
from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from sqlalchemy import func, case, extract
from database import get_security_db, get_traffic_db, SecurityLog, NetworkTraffic, BlockedIP, Whitelist
from ml_service import ml_service
from config import APP_VERSION, APP_NAME, DRY_RUN, AUTO_BLOCK_THRESHOLD
from datetime import datetime, timedelta
import time
import csv
import io

router = APIRouter(prefix="/api", tags=["system"])

# Momento en que el backend inició (para calcular uptime)
_startup_time = time.time()


@router.get("/health")
def health_check():
    """
    Endpoint de salud del sistema (Control ISO A.8.16).
    Retorna estado de cada componente crítico.
    """
    # Verificar BD de seguridad
    db_security_ok = False
    try:
        db = next(get_security_db())
        db.query(func.count(SecurityLog.id)).scalar()
        db_security_ok = True
        db.close()
    except Exception:
        try:
            db.close()
        except Exception:
            pass

    # Verificar BD de tráfico
    db_traffic_ok = False
    try:
        db = next(get_traffic_db())
        db.query(func.count(NetworkTraffic.id)).scalar()
        db_traffic_ok = True
        db.close()
    except Exception:
        try:
            db.close()
        except Exception:
            pass

    # Uptime
    uptime_seconds = time.time() - _startup_time
    hours = int(uptime_seconds // 3600)
    minutes = int((uptime_seconds % 3600) // 60)
    seconds = int(uptime_seconds % 60)

    # Modelo
    model_info = ml_service.get_model_info()

    all_ok = db_security_ok and db_traffic_ok and model_info.get("is_loaded", False)

    return {
        "status": "online" if all_ok else "degraded",
        "app": APP_NAME,
        "version": APP_VERSION,
        "timestamp": datetime.utcnow().isoformat() + 'Z',
        "uptime": f"{hours:03d}:{minutes:02d}:{seconds:02d}",
        "uptime_seconds": round(uptime_seconds),
        "components": {
            "ml_model": {
                "status": "loaded" if model_info["is_loaded"] else "not_loaded",
                "model_type": model_info.get("model_type", "unknown"),
                "num_classes": model_info.get("num_classes", 0),
            },
            "database_security": "connected" if db_security_ok else "error",
            "database_traffic": "connected" if db_traffic_ok else "error",
        },
        "config": {
            "dry_run": DRY_RUN,
            "auto_block_threshold": AUTO_BLOCK_THRESHOLD,
        }
    }


@router.get("/stats")
def get_system_stats(db: Session = Depends(get_security_db)):
    """
    Estadísticas globales del sistema para el Dashboard y TrafficMonitor.
    Combina datos de seguridad, modelo ML y recursos del sistema.
    """
    now = datetime.utcnow()
    last_24h = now - timedelta(hours=24)

    # ── Conteos generales ────────────────────────────────────────
    total_logs = db.query(func.count(SecurityLog.id)).scalar() or 0

    total_last_24h = db.query(func.count(SecurityLog.id)).filter(
        SecurityLog.timestamp >= last_24h
    ).scalar() or 0

    # ── Conteos por severidad (basado en confianza) ──────────────
    critical_count = db.query(func.count(SecurityLog.id)).filter(
        SecurityLog.confidence >= 0.90,
        SecurityLog.attack_type != "Normal"
    ).scalar() or 0

    warning_count = db.query(func.count(SecurityLog.id)).filter(
        SecurityLog.confidence >= 0.50,
        SecurityLog.confidence < 0.90,
        SecurityLog.attack_type != "Normal"
    ).scalar() or 0

    info_count = db.query(func.count(SecurityLog.id)).filter(
        SecurityLog.confidence < 0.50,
        SecurityLog.attack_type != "Normal"
    ).scalar() or 0

    # ── Confianza promedio del modelo ─────────────────────────────
    avg_confidence_row = db.query(func.avg(SecurityLog.confidence)).filter(
        SecurityLog.attack_type != "Normal"
    ).scalar()
    avg_confidence = round(float(avg_confidence_row * 100), 1) if avg_confidence_row else 90.0

    # ── Distribución por tipo de ataque ──────────────────────────
    attack_distribution = db.query(
        SecurityLog.attack_type,
        func.count(SecurityLog.id).label("count")
    ).filter(
        SecurityLog.attack_type != "Normal"
    ).group_by(SecurityLog.attack_type).order_by(
        func.count(SecurityLog.id).desc()
    ).all()

    distribution = [{"type": row[0], "count": row[1]} for row in attack_distribution]

    # ── Top 5 IPs atacantes ──────────────────────────────────────
    top_ips = db.query(
        SecurityLog.source_ip,
        func.count(SecurityLog.id).label("count"),
        func.max(SecurityLog.timestamp).label("last_seen")
    ).filter(
        SecurityLog.attack_type != "Normal"
    ).group_by(SecurityLog.source_ip).order_by(
        func.count(SecurityLog.id).desc()
    ).limit(5).all()

    top_attackers = [
        {"ip": row[0], "count": row[1], "last_seen": row[2].isoformat() if row[2] else None}
        for row in top_ips
    ]

    # ── Distribución de tráfico por hora (últimas 24h) ───────────
    hourly_data = []
    for h in range(24):
        hour_start = (now - timedelta(hours=24 - h)).replace(minute=0, second=0, microsecond=0)
        hour_end = hour_start + timedelta(hours=1)
        count = db.query(func.count(SecurityLog.id)).filter(
            SecurityLog.timestamp >= hour_start,
            SecurityLog.timestamp < hour_end
        ).scalar() or 0
        hourly_data.append({
            "hour": hour_start.strftime("%H:00"),
            "count": count
        })

    # ── Acciones ejecutadas ──────────────────────────────────────
    auto_blocked = db.query(func.count(SecurityLog.id)).filter(
        SecurityLog.action_taken.like("AUTO-BLOCKED%")
    ).scalar() or 0

    manual_blocked = db.query(func.count(SecurityLog.id)).filter(
        SecurityLog.action_taken.like("MANUAL%")
    ).scalar() or 0

    pending_alerts = db.query(func.count(SecurityLog.id)).filter(
        SecurityLog.action_taken == "ALERTED (Pending Manual Review)"
    ).scalar() or 0

    active_blocked_ips = db.query(func.count(BlockedIP.id)).filter(
        BlockedIP.is_active == 1
    ).scalar() or 0

    whitelist_count = db.query(func.count(Whitelist.id)).scalar() or 0

    avg_latency_row = db.query(func.avg(SecurityLog.latency_ms)).filter(
        SecurityLog.latency_ms != None
    ).scalar()
    avg_latency = round(float(avg_latency_row), 2) if avg_latency_row else 0.0

    recent_blocked_ips = db.query(BlockedIP.ip).filter(
        BlockedIP.is_active == 1
    ).order_by(BlockedIP.blocked_at.desc()).limit(5).all()

    blocked_ips_list = [row[0] for row in recent_blocked_ips]

    # ── Métricas de recursos del sistema ─────────────────────────
    cpu_percent = 0.0
    ram_percent = 0.0
    ram_used_gb = 0.0
    ram_total_gb = 0.0
    try:
        import psutil
        cpu_percent = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory()
        ram_percent = mem.percent
        ram_used_gb = round(mem.used / (1024 ** 3), 1)
        ram_total_gb = round(mem.total / (1024 ** 3), 1)
    except ImportError:
        pass

    # ── Uptime ───────────────────────────────────────────────────
    uptime_seconds = time.time() - _startup_time
    hours_up = int(uptime_seconds // 3600)
    mins_up = int((uptime_seconds % 3600) // 60)
    secs_up = int(uptime_seconds % 60)

    # ── Modelo info ──────────────────────────────────────────────
    model_info = ml_service.get_model_info()

    return {
        "timestamp": now.isoformat(),
        "uptime": f"{hours_up:03d}:{mins_up:02d}:{secs_up:02d}",
        "counts": {
            "total_logs": total_logs,
            "total_last_24h": total_last_24h,
            "critical": critical_count,
            "warning": warning_count,
            "info": info_count,
            "auto_blocked": auto_blocked,
            "manual_blocked": manual_blocked,
            "pending_alerts": pending_alerts,
            "active_blocked_ips": active_blocked_ips,
            "whitelist_count": whitelist_count,
            "avg_latency_ms": avg_latency,
        },
        "model": {
            "confidence_avg": avg_confidence,
            "is_loaded": model_info["is_loaded"],
            "model_type": model_info.get("model_type", "N/A"),
            "classes": model_info.get("classes", []),
        },
        "attack_distribution": distribution,
        "top_attackers": top_attackers,
        "hourly_traffic": hourly_data,
        "blocked_ips": blocked_ips_list,
        "resources": {
            "cpu_percent": cpu_percent,
            "ram_percent": ram_percent,
            "ram_used_gb": ram_used_gb,
            "ram_total_gb": ram_total_gb,
        }
    }


@router.get("/stats/alerts-count")
def get_alerts_count(db: Session = Depends(get_security_db)):
    """
    Conteo rápido de alertas pendientes para el badge del header.
    Solo cuenta alertas con action_taken = 'ALERTED (Pending Manual Review)'.
    """
    pending = db.query(func.count(SecurityLog.id)).filter(
        SecurityLog.action_taken == "ALERTED (Pending Manual Review)"
    ).scalar() or 0

    # También las últimas 5 alertas para el tooltip
    recent_alerts = db.query(SecurityLog).filter(
        SecurityLog.attack_type != "Normal"
    ).order_by(SecurityLog.timestamp.desc()).limit(5).all()

    alerts_list = [
        {
            "id": alert.id,
            "source_ip": alert.source_ip,
            "attack_type": alert.attack_type,
            "confidence": alert.confidence,
            "timestamp": alert.timestamp.isoformat() if alert.timestamp else None,
            "action_taken": alert.action_taken,
        }
        for alert in recent_alerts
    ]

    return {
        "pending_count": pending,
        "recent_alerts": alerts_list,
    }


@router.get("/logs/export")
def export_logs(
    format: str = "csv",
    limit: int = 1000,
    db: Session = Depends(get_security_db),
):
    logs = db.query(SecurityLog).order_by(SecurityLog.timestamp.desc()).limit(limit).all()

    if format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["id", "timestamp", "source_ip", "destination_ip", "attack_type", "confidence", "action_taken", "iso_control", "latency_ms", "whitelist_hit"])
        for log in logs:
            writer.writerow([
                log.id,
                log.timestamp.isoformat() if log.timestamp else "",
                log.source_ip,
                log.destination_ip,
                log.attack_type,
                log.confidence,
                log.action_taken,
                log.iso_control,
                log.latency_ms or "",
                1 if log.whitelist_hit else 0,
            ])
        return Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=security_logs.csv"},
        )

    return {"error": "Unsupported format"}


@router.get("/stats/active-threats")
def get_active_threats(db: Session = Depends(get_security_db)):
    pending_alerts = db.query(SecurityLog).filter(
        SecurityLog.action_taken == "ALERTED (Pending Manual Review)"
    ).order_by(SecurityLog.timestamp.desc()).limit(10).all()

    active_sources = db.query(
        SecurityLog.source_ip,
        func.count(SecurityLog.id).label("count"),
        func.max(SecurityLog.timestamp).label("last_seen")
    ).filter(
        SecurityLog.action_taken == "ALERTED (Pending Manual Review)"
    ).group_by(SecurityLog.source_ip).order_by(func.count(SecurityLog.id).desc()).limit(10).all()

    blocked = db.query(BlockedIP).filter(BlockedIP.is_active == 1).order_by(BlockedIP.blocked_at.desc()).limit(20).all()

    return {
        "pending_alerts": [
            {
                "id": log.id,
                "source_ip": log.source_ip,
                "attack_type": log.attack_type,
                "confidence": log.confidence,
                "timestamp": log.timestamp.isoformat() if log.timestamp else None,
            }
            for log in pending_alerts
        ],
        "top_sources": [
            {
                "source_ip": row[0],
                "count": row[1],
                "last_seen": row[2].isoformat() if row[2] else None,
            }
            for row in active_sources
        ],
        "blocked_ips": [
            {
                "ip": entry.ip,
                "blocked_at": entry.blocked_at.isoformat() if entry.blocked_at else None,
                "method": entry.method,
                "reason": entry.reason,
            }
            for entry in blocked
        ],
        "total_pending": len(pending_alerts),
        "total_blocked": len(blocked),
    }
