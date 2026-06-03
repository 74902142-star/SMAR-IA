"""SMAR-IA — Punto de entrada FastAPI con pipeline de detección y mitigación."""

import asyncio
import logging
from datetime import datetime, timezone

from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from sqlalchemy.orm import Session

from database import get_security_db, get_traffic_db, SecurityLog, NetworkTraffic, init_db, BlockedIP, Rule
from auth import oauth2_scheme
from ml_service import ml_service
from routers import auth, mitigation, system, audit, whitelist, settings
from routers.whitelist import is_whitelisted
from routers.mitigation import add_suspicious_activity, record_block, is_ip_blocked
from routers.audit import record_audit
from event_manager import manager
from config import print_config_summary, AUTO_BLOCK_THRESHOLD, DRY_RUN, CORS_ORIGINS
from firewall import remove_iptables_block, apply_iptables_block, restore_iptables_rules
from alerting import notify_threat
from audit_logger import write_audit_log
import rules

logger = logging.getLogger("smar-ia-main")

app = FastAPI(title="IDS Security Dashboard API", debug=False)

limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

cors_origins = [o.strip() for o in CORS_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
)

app.include_router(auth.router)
app.include_router(mitigation.router)
app.include_router(system.router)
app.include_router(rules.router)
app.include_router(audit.router)
app.include_router(whitelist.router)
app.include_router(settings.router)


# ── Startup ──────────────────────────────────────────────────────────────


@app.on_event("startup")
async def startup_event():
    """Inicializa BD, sincroniza firewall, carga modelos y lanza workers."""
    print_config_summary()
    init_db()
    db = next(get_security_db())
    try:
        blocked = db.query(BlockedIP).filter(BlockedIP.is_active == 1).all()
        restore_iptables_rules([b.ip for b in blocked])
        ml_service.load_models()
        app._bg_tasks = [
            asyncio.create_task(process_traffic_loop()),
            asyncio.create_task(check_block_expiry_loop()),
        ]
    finally:
        db.close()


# ── Worker de expiración de bloqueos ────────────────────────────────────


async def check_block_expiry_loop():
    """Worker periódico que desactiva bloqueos expirados (cada 60s)."""
    logger.info("Iniciando worker de expiración de bloqueos...")
    while True:
        db = next(get_security_db())
        try:
            _process_expired_blocks(db)
        except Exception as exc:
            logger.error("Error en worker de expiración: %s", exc)
        finally:
            try:
                db.close()
            except Exception as exc:
                logger.warning("Error cerrando DB en expiry loop: %s", exc)
        await asyncio.sleep(60)


def _process_expired_blocks(db: Session):
    """Marca como inactivos los bloqueos vencidos y notifica."""
    now = datetime.now(timezone.utc)
    now_naive = now.replace(tzinfo=None)
    expired = (
        db.query(BlockedIP)
        .filter(BlockedIP.is_active == 1, BlockedIP.expires_at != None, BlockedIP.expires_at <= now_naive)
        .all()
    )
    for entry in expired:
        entry.is_active = 0
        remove_iptables_block(entry.ip)
        _log_auto_unblock(db, entry)
    if expired:
        db.commit()


def _log_auto_unblock(db: Session, entry):
    """Registra un desbloqueo automático en BD y audit log."""
    log = SecurityLog(
        source_ip=entry.ip,
        destination_ip="Any",
        attack_type="Auto-Unblock",
        confidence=1.0,
        action_taken="AUTO-UNBLOCKED: expiry",
    )
    db.add(log)
    write_audit_log({
        "event_type": "BLOCK_REMOVED",
        "network": {"source_ip": entry.ip, "destination_ip": "Any"},
        "detection": {"attack_type": "Auto-Unblock"},
        "response": {"action_taken": "AUTO-UNBLOCKED: expiry"},
        "iso_compliance": {"controls_activated": ["A.8.15", "A.8.20"]},
    })


# ── Evaluación de reglas dinámicas (segura, sin eval) ─────────────────────

import ast
import operator as _operator


def evaluate_condition(condition: str, context: dict) -> bool:
    """Evalúa condición de regla dinámica usando ast.literal_eval restringido.
    Solo permite variables conocidas, operadores de comparación y lógicos.
    Sin eval() ni exec() — 100% resistente a inyección de código.
    """
    allowed_names = {
        'True': True, 'False': False,
        'attack_type': context.get('attack_type', ''),
        'confidence': context.get('confidence', 0.0),
        'ip': context.get('ip', ''),
    }
    ops = {
        ast.Eq: _operator.eq, ast.NotEq: _operator.ne,
        ast.Gt: _operator.gt, ast.GtE: _operator.ge,
        ast.Lt: _operator.lt, ast.LtE: _operator.le,
        ast.In: lambda a, b: a in b,
        ast.NotIn: lambda a, b: a not in b,
        ast.Is: _operator.is_,
        ast.IsNot: _operator.is_not,
    }
    bool_ops = {
        ast.And: lambda a, b: a and b,
        ast.Or: lambda a, b: a or b,
    }

    def _eval_node(node):
        if isinstance(node, ast.Expression):
            return _eval_node(node.body)
        if isinstance(node, ast.BoolOp):
            results = [_eval_node(v) for v in node.values]
            return bool_ops[type(node.op)](*results) if len(results) == 2 else all(results) if isinstance(node.op, ast.And) else any(results)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            return not _eval_node(node.operand)
        if isinstance(node, ast.Compare):
            left = _eval_node(node.left)
            for op, comparator in zip(node.ops, node.comparators):
                right = _eval_node(comparator)
                if not ops[type(op)](left, right):
                    return False
                left = right
            return True
        if isinstance(node, ast.Name):
            name = node.id
            if name in allowed_names:
                return allowed_names[name]
            raise NameError(f"Variable no permitida: {name}")
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, (ast.Tuple, ast.List)):
            return [_eval_node(e) for e in node.elts]
        if isinstance(node, ast.BinOp):
            left = _eval_node(node.left)
            right = _eval_node(node.right)
            if isinstance(node.op, ast.Add): return left + right
            if isinstance(node.op, ast.Sub): return left - right
            if isinstance(node.op, ast.Mult): return left * right
            if isinstance(node.op, ast.Div): return left / right
            raise TypeError(f"Operador no permitido: {type(node.op)}")
        raise TypeError(f"Nodo AST no permitido: {type(node)}")

    try:
        tree = ast.parse(condition, mode='eval')
        return bool(_eval_node(tree.body))
    except (SyntaxError, NameError, TypeError, ZeroDivisionError):
        return False


# ── Pipeline de procesamiento de tráfico ────────────────────────────────


async def process_traffic_loop():
    """Bucle principal que procesa tráfico no analizado en lotes (batch inference)."""
    logger.info("Iniciando bucle de procesamiento de tráfico (batch inference)...")
    while True:
        db_traffic = next(get_traffic_db())
        db_security = next(get_security_db())
        try:
            unprocessed = (
                db_traffic.query(NetworkTraffic)
                .filter(NetworkTraffic.is_processed == 0)
                .limit(50)
                .all()
            )
            if unprocessed:
                features_batch = []
                for t in unprocessed:
                    try:
                        f = [float(x) for x in t.features_csv.split(",")]
                        features_batch.append(f)
                    except (ValueError, AttributeError):
                        features_batch.append([0.0] * 80)

                predictions = ml_service.predict_batch(features_batch) if len(features_batch) > 1 else None

                for i, traffic in enumerate(unprocessed):
                    if predictions:
                        attack_type, confidence = predictions[i]
                    else:
                        attack_type, confidence = ml_service.predict(features_batch[0])
                    _process_classified_traffic(traffic, attack_type, confidence, db_traffic, db_security)
        except Exception as e:
            logger.error("Error en bucle de procesamiento de tráfico: %s", e)
        finally:
            db_traffic.close()
            db_security.close()
        await asyncio.sleep(1)


def _process_classified_traffic(traffic, attack_type, confidence, db_traffic, db_security):
    """Procesa una entrada de tráfico ya clasificada: evalúa reglas y mitiga."""
    action_taken = "NONE"
    is_alert = False

    if is_ip_blocked(db_security, traffic.source_ip):
        _mark_processed(traffic, db_traffic)
        return

    if is_whitelisted(db_security, traffic.source_ip):
        _mark_processed(traffic, db_traffic)
        write_audit_log({
            "event_type": "WHITELIST_HIT",
            "network": {"source_ip": traffic.source_ip, "destination_ip": traffic.destination_ip},
            "detection": {"model_confidence": confidence, "attack_type": attack_type},
            "response": {"action_taken": "SKIPPED (whitelisted)"},
            "iso_compliance": {"controls_activated": ["A.8.15"]},
        })
        return

    if attack_type == "Normal" or attack_type == "Unknown":
        _mark_processed(traffic, db_traffic)
        _broadcast_update(traffic, attack_type, confidence, False, action_taken)
        return

    is_alert = True
    add_suspicious_activity(traffic.source_ip)
    severity = _derive_severity(confidence, attack_type)

    action_taken = _evaluate_rules_and_mitigate(traffic, attack_type, confidence, db_security)

    if action_taken == "NONE":
        if confidence >= AUTO_BLOCK_THRESHOLD:
            action_taken = _auto_block(traffic, attack_type, confidence, db_security)
        else:
            action_taken = "ALERTED (Pending Manual Review)"

    if confidence > 0.85:
        asyncio.create_task(notify_threat(traffic.source_ip, attack_type, confidence, action_taken))

    _save_security_log(traffic, attack_type, confidence, action_taken, db_security, severity=severity)
    _mark_processed(traffic, db_traffic)
    _broadcast_update(traffic, attack_type, confidence, is_alert, action_taken)


def _evaluate_rules_and_mitigate(traffic: NetworkTraffic, attack_type: str, confidence: float, db_security: Session) -> str:
    """Evalúa reglas dinámicas y ejecuta la primera que coincida."""
    rules_list = db_security.query(Rule).filter(Rule.enabled == True).all()
    rule_context = {"attack_type": attack_type, "confidence": confidence, "ip": traffic.source_ip}

    for rule in rules_list:
        if evaluate_condition(rule.condition, rule_context) and rule.action == "BLOCK":
            detection_ts = datetime.now(timezone.utc)
            latency = apply_iptables_block(traffic.source_ip)
            mitigation_ts = datetime.now(timezone.utc)
            record_block(
                db_security, traffic.source_ip,
                method=f"RULE:{rule.name}", reason=attack_type,
                action_taken=f"Rule {rule.name} triggered",
            )
            action_taken = f"RULE_BLOCKED: {rule.name}"
            _write_mitigation_audit(traffic, attack_type, confidence, action_taken, latency)
            _save_security_log(traffic, attack_type, confidence, action_taken, db_security,
                               detection_ts, mitigation_ts, latency)
            return action_taken
    return "NONE"


def _auto_block(traffic: NetworkTraffic, attack_type: str, confidence: float, db_security: Session) -> str:
    """Ejecuta bloqueo automático por umbral de confianza."""
    detection_ts = datetime.now(timezone.utc)
    latency = apply_iptables_block(traffic.source_ip)
    mitigation_ts = datetime.now(timezone.utc)

    if DRY_RUN:
        action_taken = f"DRY-RUN: iptables -A INPUT -s {traffic.source_ip} -j DROP"
    else:
        action_taken = f"AUTO-BLOCKED: iptables -A INPUT -s {traffic.source_ip} -j DROP"
        record_block(
            db_security, traffic.source_ip,
            method="AUTO", reason=attack_type,
            action_taken=action_taken,
        )

    _write_mitigation_audit(traffic, attack_type, confidence, action_taken, latency)
    _save_security_log(traffic, attack_type, confidence, action_taken, db_security,
                       detection_ts, mitigation_ts, latency)
    return action_taken


def _write_mitigation_audit(traffic: NetworkTraffic, attack_type: str, confidence: float,
                            action_taken: str, latency: float):
    """Registra evento de mitigación en el logger de auditoría JSON."""
    write_audit_log({
        "event_type": "INTRUSION_MITIGATED",
        "network": {"source_ip": traffic.source_ip, "destination_ip": traffic.destination_ip},
        "detection": {"model_confidence": confidence, "attack_type": attack_type},
        "response": {"mitigation_latency_ms": latency, "action_taken": action_taken},
        "iso_compliance": {"controls_activated": ["A.8.15", "A.8.20"]},
    })


def _derive_severity(confidence: float, attack_type: str) -> str:
    """Deriva severidad basada en confianza y tipo de ataque."""
    if attack_type in ("Normal", "Unknown", "Auto-Unblock"):
        return "INFO"
    if confidence >= 0.95:
        return "CRITICAL"
    if confidence >= 0.85:
        return "HIGH"
    if confidence >= 0.70:
        return "MEDIUM"
    if confidence >= 0.50:
        return "LOW"
    return "INFO"


def _save_security_log(traffic: NetworkTraffic, attack_type: str, confidence: float,
                       action_taken: str, db_security: Session,
                       detection_ts=None, mitigation_ts=None, latency=None,
                       severity=None):
    """Persiste un registro de seguridad en la BD."""
    if severity is None:
        severity = _derive_severity(confidence, attack_type)
    log = SecurityLog(
        source_ip=traffic.source_ip,
        destination_ip=traffic.destination_ip,
        attack_type=attack_type,
        confidence=confidence,
        action_taken=action_taken,
        severity=severity,
        detection_timestamp=detection_ts,
        mitigation_timestamp=mitigation_ts,
        latency_ms=latency if latency and latency >= 0 else None,
    )
    db_security.add(log)
    db_security.commit()


def _mark_processed(traffic: NetworkTraffic, db_traffic: Session):
    """Marca una entrada de tráfico como procesada."""
    traffic.is_processed = 1
    db_traffic.commit()


def _broadcast_update(traffic: NetworkTraffic, attack_type: str, confidence: float,
                      is_alert: bool, action_taken: str):
    """Envía actualización de tráfico por WebSocket."""
    try:
        ws_message = {
            "type": "traffic_update",
            "timestamp": traffic.timestamp.isoformat(),
            "source_ip": traffic.source_ip,
            "destination_ip": traffic.destination_ip,
            "predicted_class": attack_type,
            "confidence": confidence,
            "is_alert": is_alert,
            "action_taken": action_taken,
        }
        asyncio.create_task(manager.broadcast(ws_message))
    except Exception as exc:
        logger.warning("Error en broadcast: %s", exc)


# ── WebSocket ───────────────────────────────────────────────────────────


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Endpoint WebSocket para actualizaciones en tiempo real.
    Autenticación vía primer mensaje: {"token": "..."}
    """
    from auth import get_current_user_ws
    await websocket.accept()
    try:
        data = await websocket.receive_text()
        import json as _json
        try:
            msg = _json.loads(data)
            token = msg.get("token")
        except (_json.JSONDecodeError, AttributeError):
            token = None
        user = await get_current_user_ws(websocket, token)
        if not user:
            return
        await manager.connect(websocket)
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    except Exception as exc:
        logger.warning("Error en WebSocket: %s", exc)
        try:
            await manager.disconnect(websocket)
        except Exception:
            logger.debug("WebSocket ya cerrado al desconectar")


# ── Logs ────────────────────────────────────────────────────────────────


@app.get("/api/logs")
def get_logs(token: str = Depends(oauth2_scheme), db: Session = Depends(get_security_db), limit: int = 50):
    """Retorna los registros de seguridad más recientes."""
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
            "severity": log.severity or "INFO",
        }
        for log in logs
    ]
