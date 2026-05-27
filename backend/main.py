import asyncio
import json
import time
from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from sqlalchemy.orm import Session
from database import get_security_db, get_traffic_db, SecurityLog, NetworkTraffic, init_db, BlockedIP, Rule
from ml_service import ml_service
from datetime import datetime

from routers import auth, mitigation, system, audit, whitelist
from routers.whitelist import is_whitelisted
import rules
from routers.mitigation import add_suspicious_activity, record_block, is_ip_blocked
from routers.audit import record_audit
from event_manager import manager
from config import print_config_summary, AUTO_BLOCK_THRESHOLD, DRY_RUN
from firewall import sync_firewall_with_db, remove_iptables_block, apply_iptables_block, restore_iptables_rules
from alerting import notify_threat
from audit_logger import write_audit_log

app = FastAPI(title="IDS Security Dashboard API")

limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(mitigation.router)
app.include_router(system.router)
app.include_router(rules.router)
app.include_router(audit.router)
app.include_router(whitelist.router)

@app.on_event("startup")
async def startup_event():
    print_config_summary()
    init_db()
    # Sincronizar firewall al inicio
    db = next(get_security_db())
    blocked = db.query(BlockedIP).filter(BlockedIP.is_active == 1).all()
    restore_iptables_rules([b.ip for b in blocked])
    ml_service.load_models()
    asyncio.create_task(process_traffic_loop())
    asyncio.create_task(check_block_expiry_loop())


async def check_block_expiry_loop():
    """Worker que desactiva bloqueos cuya fecha de expiración pasó."""
    print("Iniciando worker de expiración de bloqueos...")
    while True:
        db = next(get_security_db())
        try:
            now = datetime.utcnow()
            expired = db.query(BlockedIP).filter(BlockedIP.is_active == 1, BlockedIP.expires_at != None, BlockedIP.expires_at <= now).all()
            for entry in expired:
                entry.is_active = 0
                remove_iptables_block(entry.ip)
                log = SecurityLog(
                    source_ip=entry.ip,
                    destination_ip="Any",
                    attack_type="Auto-Unblock",
                    confidence=1.0,
                    action_taken=f"AUTO-UNBLOCKED: expiry",
                )
                db.add(log)
                write_audit_log({
                    "event_type": "BLOCK_REMOVED",
                    "network": {"source_ip": entry.ip, "destination_ip": "Any"},
                    "detection": {"attack_type": "Auto-Unblock"},
                    "response": {"action_taken": "AUTO-UNBLOCKED: expiry"},
                    "iso_compliance": {"controls_activated": ["A.8.15", "A.8.20"]},
                })
                await manager.broadcast({
                    "type": "mitigation_event",
                    "event": "auto_unblock",
                    "ip": entry.ip,
                    "blocked_at": entry.blocked_at.isoformat() if entry.blocked_at else None,
                    "expires_at": entry.expires_at.isoformat() if entry.expires_at else None,
                })
            if expired:
                db.commit()
        except Exception as e:
            print(f"Error en worker de expiración: {e}")
        finally:
            try:
                db.close()
            except Exception:
                pass
        await asyncio.sleep(60)


def evaluate_condition(condition: str, context: dict) -> bool:
    """
    Evaluador simple y seguro de condiciones para reglas.
    Soporta comparaciones básicas: ==, !=, >, <, and, or.
    """
    try:
        for key, value in context.items():
            condition = condition.replace(key, f"'{value}'" if isinstance(value, str) else str(value))
        return eval(condition, {"__builtins__": {}}, {})
    except Exception:
        return False

async def process_traffic_loop():
    print("Iniciando bucle de procesamiento de tráfico...")
    while True:
        db_traffic = next(get_traffic_db())
        db_security = next(get_security_db())

        try:
            unprocessed_traffic = db_traffic.query(NetworkTraffic).filter(NetworkTraffic.is_processed == 0).limit(10).all()

            for traffic in unprocessed_traffic:
                features = [float(x) for x in traffic.features_csv.split(",")]
                attack_type, confidence = ml_service.predict(features)

                action_taken = "NONE"
                is_alert = False

                if is_ip_blocked(db_security, traffic.source_ip):
                    traffic.is_processed = 1
                    db_traffic.commit()
                    continue

                # ── WHITELIST CHECK ────────────────────────────────
                if is_whitelisted(db_security, traffic.source_ip):
                    traffic.is_processed = 1
                    db_traffic.commit()
                    write_audit_log({
                        "event_type": "WHITELIST_HIT",
                        "network": {"source_ip": traffic.source_ip, "destination_ip": traffic.destination_ip},
                        "detection": {"model_confidence": confidence, "attack_type": attack_type},
                        "response": {"action_taken": "SKIPPED (whitelisted)"},
                        "iso_compliance": {"controls_activated": ["A.8.15"]},
                    })
                    continue

                if attack_type != "Normal" and attack_type != "Unknown":
                    is_alert = True
                    add_suspicious_activity(traffic.source_ip)

                    # ── EVALUACIÓN DE REGLAS DINÁMICAS ─────────────
                    rules_list = db_security.query(Rule).filter(Rule.enabled == True).all()
                    rule_context = {
                        "attack_type": attack_type,
                        "confidence": confidence,
                        "ip": traffic.source_ip
                    }

                    rule_triggered = False
                    for rule in rules_list:
                        if evaluate_condition(rule.condition, rule_context):
                            if rule.action == "BLOCK":
                                detection_ts = datetime.utcnow()
                                latency = apply_iptables_block(traffic.source_ip)
                                mitigation_ts = datetime.utcnow()

                                record_block(
                                    db_security,
                                    traffic.source_ip,
                                    method=f"RULE:{rule.name}",
                                    reason=attack_type,
                                    action_taken=f"Rule {rule.name} triggered",
                                )
                                action_taken = f"RULE_BLOCKED: {rule.name}"
                                rule_triggered = True

                                isoc = ["A.8.15", "A.8.20"]
                                write_audit_log({
                                    "event_type": "INTRUSION_MITIGATED",
                                    "network": {"source_ip": traffic.source_ip, "destination_ip": traffic.destination_ip},
                                    "detection": {"model_confidence": confidence, "attack_type": attack_type},
                                    "response": {"mitigation_latency_ms": latency, "action_taken": action_taken},
                                    "iso_compliance": {"controls_activated": isoc},
                                })

                                new_log = SecurityLog(
                                    source_ip=traffic.source_ip,
                                    destination_ip=traffic.destination_ip,
                                    attack_type=attack_type,
                                    confidence=confidence,
                                    action_taken=action_taken,
                                    detection_timestamp=detection_ts,
                                    mitigation_timestamp=mitigation_ts,
                                    latency_ms=latency if latency >= 0 else None,
                                )
                                db_security.add(new_log)
                                db_security.commit()
                                break
                    # ───────────────────────────────────────────────

                    if not rule_triggered:
                        if confidence >= AUTO_BLOCK_THRESHOLD:
                            detection_ts = datetime.utcnow()
                            latency = apply_iptables_block(traffic.source_ip)
                            mitigation_ts = datetime.utcnow()

                            if DRY_RUN:
                                action_taken = f"DRY-RUN: iptables -A INPUT -s {traffic.source_ip} -j DROP"
                            else:
                                action_taken = f"AUTO-BLOCKED: iptables -A INPUT -s {traffic.source_ip} -j DROP"
                                record_block(
                                    db_security,
                                    traffic.source_ip,
                                    method="AUTO",
                                    reason=attack_type,
                                    action_taken=action_taken,
                                )

                            isoc = ["A.8.15", "A.8.20"]
                            write_audit_log({
                                "event_type": "INTRUSION_MITIGATED",
                                "network": {"source_ip": traffic.source_ip, "destination_ip": traffic.destination_ip},
                                "detection": {"model_confidence": confidence, "attack_type": attack_type},
                                "response": {"mitigation_latency_ms": latency, "action_taken": action_taken},
                                "iso_compliance": {"controls_activated": isoc},
                            })

                            new_log = SecurityLog(
                                source_ip=traffic.source_ip,
                                destination_ip=traffic.destination_ip,
                                attack_type=attack_type,
                                confidence=confidence,
                                action_taken=action_taken,
                                detection_timestamp=detection_ts,
                                mitigation_timestamp=mitigation_ts,
                                latency_ms=latency if latency >= 0 else None,
                            )
                            db_security.add(new_log)
                            db_security.commit()
                        else:
                            action_taken = "ALERTED (Pending Manual Review)"

                    if confidence > 0.85:
                        await notify_threat(traffic.source_ip, attack_type, confidence, action_taken)

                    if not rule_triggered and confidence < AUTO_BLOCK_THRESHOLD:
                        new_log = SecurityLog(
                            source_ip=traffic.source_ip,
                            destination_ip=traffic.destination_ip,
                            attack_type=attack_type,
                            confidence=confidence,
                            action_taken=action_taken
                        )
                        db_security.add(new_log)
                        db_security.commit()

                traffic.is_processed = 1
                db_traffic.commit()

                ws_message = {
                    "type": "traffic_update",
                    "timestamp": traffic.timestamp.isoformat(),
                    "source_ip": traffic.source_ip,
                    "destination_ip": traffic.destination_ip,
                    "predicted_class": attack_type,
                    "confidence": confidence,
                    "is_alert": is_alert,
                    "action_taken": action_taken
                }
                await manager.broadcast(ws_message)

        except Exception as e:
            print(f"Error procesando tráfico: {e}")
        finally:
            db_traffic.close()
            db_security.close()

        await asyncio.sleep(1)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/api/logs")
def get_logs(db: Session = Depends(get_security_db), limit: int = 50):
    logs = db.query(SecurityLog).order_by(SecurityLog.timestamp.desc()).limit(limit).all()
    return [
        {
            "id": log.id,
            "timestamp": log.timestamp.isoformat() if log.timestamp else None,
            "source_ip": log.source_ip,
            "destination_ip": log.destination_ip,
            "attack_type": log.attack_type,
            "confidence": log.confidence,
            "action_taken": log.action_taken,
            "iso_control": log.iso_control,
            "latency_ms": log.latency_ms,
            "whitelist_hit": bool(log.whitelist_hit),
        }
        for log in logs
    ]
