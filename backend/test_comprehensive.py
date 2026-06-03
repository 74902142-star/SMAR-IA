"""
SMAR-IA — Suite de pruebas integrales.
Ejecutar con: python -m pytest test_comprehensive.py -v
Requiere: pytest, pytest-asyncio, httpx, bcrypt, python-jose
"""
import pytest
import os
import sys
import json
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# ── Configurar modo test ──────────────────────────────────
os.environ["SMAR_IA_DRY_RUN"] = "true"
os.environ["SMAR_IA_SECRET_KEY"] = "test_secret_key_not_for_production"
os.environ["SMAR_IA_SECURITY_DB"] = "sqlite:///./test_security.db"
os.environ["SMAR_IA_TRAFFIC_DB"] = "sqlite:///./test_traffic.db"

from main import app
from database import (
    SecurityBase, TrafficBase, security_engine, traffic_engine,
    SecuritySessionLocal, TrafficSessionLocal, User, SecurityLog, NetworkTraffic,
    BlockedIP, Whitelist, Rule, AuditLog,
    get_security_db, get_traffic_db, init_db,
)
from auth import create_access_token, get_password_hash


# ── Fixtures ───────────────────────────────────────────────

@pytest.fixture(autouse=True)
def setup_db():
    """Crea tablas antes de cada test y las limpia después."""
    SecurityBase.metadata.create_all(bind=security_engine)
    TrafficBase.metadata.create_all(bind=traffic_engine)
    yield
    SecurityBase.metadata.drop_all(bind=security_engine)
    TrafficBase.metadata.drop_all(bind=traffic_engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def db():
    db = SecuritySessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def admin_token(client, db):
    """Crea admin si no existe y devuelve token."""
    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        hashed = get_password_hash("admin123")
        admin = User(username="admin", hashed_password=hashed, role="admin", is_active=1)
        db.add(admin)
        db.commit()
    response = client.post("/api/auth/login", data={"username": "admin", "password": "admin123"})
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


# ── Tests de Autenticación ─────────────────────────────────

class TestAuth:
    def test_login_success(self, client, db):
        hashed = get_password_hash("test123")
        user = User(username="testuser", hashed_password=hashed, role="viewer", is_active=1)
        db.add(user)
        db.commit()
        r = client.post("/api/auth/login", data={"username": "testuser", "password": "test123"})
        assert r.status_code == 200
        data = r.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["username"] == "testuser"

    def test_login_fail_wrong_password(self, client, db):
        hashed = get_password_hash("test123")
        user = User(username="testuser", hashed_password=hashed, role="viewer", is_active=1)
        db.add(user)
        db.commit()
        r = client.post("/api/auth/login", data={"username": "testuser", "password": "wrong"})
        assert r.status_code == 401

    def test_login_fail_inactive(self, client, db):
        hashed = get_password_hash("test123")
        user = User(username="testuser", hashed_password=hashed, role="viewer", is_active=0)
        db.add(user)
        db.commit()
        r = client.post("/api/auth/login", data={"username": "testuser", "password": "test123"})
        assert r.status_code == 401

    def test_me_endpoint(self, client, admin_headers):
        r = client.get("/api/auth/me", headers=admin_headers)
        assert r.status_code == 200
        assert r.json()["username"] == "admin"

    def test_me_unauthorized(self, client):
        r = client.get("/api/auth/me")
        assert r.status_code == 401

    def test_logout(self, client, admin_token, admin_headers):
        r = client.post("/api/auth/logout", headers=admin_headers)
        assert r.status_code == 200
        r2 = client.get("/api/auth/me", headers=admin_headers)
        assert r2.status_code == 401

    def test_refresh_token(self, client, admin_token, admin_headers):
        login_r = client.post("/api/auth/login", data={"username": "admin", "password": "admin123"})
        refresh_token = login_r.json().get("refresh_token")
        if refresh_token:
            r = client.post("/api/auth/refresh", json={"refresh_token": refresh_token})
            assert r.status_code == 200
            data = r.json()
            assert "access_token" in data
            assert "refresh_token" in data

    def test_list_users_requires_admin(self, client, db):
        hashed = get_password_hash("view123")
        user = User(username="viewer_list", hashed_password=hashed, role="viewer", is_active=1)
        db.add(user)
        db.commit()
        r = client.post("/api/auth/login", data={"username": "viewer_list", "password": "view123"})
        token = r.json()["access_token"]
        r2 = client.post("/api/auth/users", headers={"Authorization": f"Bearer {token}"})
        assert r2.status_code == 403

    def test_list_users_admin_ok(self, client, admin_headers):
        r = client.post("/api/auth/users", headers=admin_headers)
        assert r.status_code == 200
        users = r.json()
        assert isinstance(users, list)


# ── Tests de Mitigación ────────────────────────────────────

class TestMitigation:
    def test_block_ip(self, client, admin_headers, db):
        r = client.post("/api/mitigation/block",
            json={"ip": "10.0.0.1", "action": "BLOCK_IP", "attack_type": "Test"},
            headers=admin_headers)
        assert r.status_code == 200
        blocked = db.query(BlockedIP).filter(BlockedIP.ip == "10.0.0.1").first()
        assert blocked is not None
        assert blocked.is_active == 1

    def test_block_requires_admin(self, client, db):
        hashed = get_password_hash("view123")
        user = User(username="viewer", hashed_password=hashed, role="viewer", is_active=1)
        db.add(user)
        db.commit()
        r = client.post("/api/auth/login", data={"username": "viewer", "password": "view123"})
        token = r.json()["access_token"]
        r2 = client.post("/api/mitigation/block",
            json={"ip": "10.0.0.2", "action": "BLOCK_IP"},
            headers={"Authorization": f"Bearer {token}"})
        assert r2.status_code == 403

    def test_block_duplicate(self, client, admin_headers, db):
        r = client.post("/api/mitigation/block",
            json={"ip": "10.0.0.5", "action": "BLOCK_IP", "attack_type": "Test"},
            headers=admin_headers)
        assert r.status_code == 200
        r2 = client.post("/api/mitigation/block",
            json={"ip": "10.0.0.5", "action": "BLOCK_IP", "attack_type": "Test"},
            headers=admin_headers)
        assert r2.status_code == 200
        assert "already blocked" in r2.json()["message"]

    def test_unblock_ip(self, client, admin_headers, db):
        from routers.mitigation import record_block
        record_block(db, "10.0.0.3", method="TEST", reason="test", action_taken="test")
        r = client.post("/api/mitigation/unblock",
            json={"ip": "10.0.0.3"},
            headers=admin_headers)
        assert r.status_code == 200
        entry = db.query(BlockedIP).filter(BlockedIP.ip == "10.0.0.3").first()
        assert entry.is_active == 0

    def test_unblock_not_found(self, client, admin_headers):
        r = client.post("/api/mitigation/unblock",
            json={"ip": "1.2.3.4"},
            headers=admin_headers)
        assert r.status_code == 404

    def test_unblock_requires_admin(self, client, db):
        hashed = get_password_hash("view123")
        user = User(username="viewer_unblock", hashed_password=hashed, role="viewer", is_active=1)
        db.add(user)
        db.commit()
        r = client.post("/api/auth/login", data={"username": "viewer_unblock", "password": "view123"})
        token = r.json()["access_token"]
        r2 = client.post("/api/mitigation/unblock",
            json={"ip": "10.0.0.1"},
            headers={"Authorization": f"Bearer {token}"})
        assert r2.status_code == 403

    def test_get_suspicious(self, client, admin_headers):
        r = client.get("/api/mitigation/suspicious", headers=admin_headers)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_get_blocked(self, client, admin_headers, db):
        from routers.mitigation import record_block
        record_block(db, "10.0.0.4", method="TEST", reason="test", action_taken="test")
        r = client.get("/api/mitigation/blocked", headers=admin_headers)
        assert r.status_code == 200
        ips = r.json()
        assert any(b["ip"] == "10.0.0.4" for b in ips)

    def test_get_active(self, client, admin_headers, db):
        from routers.mitigation import record_block
        record_block(db, "10.0.0.6", method="TEST", reason="test", action_taken="test")
        r = client.get("/api/mitigation/active", headers=admin_headers)
        assert r.status_code == 200
        data = r.json()
        assert "suspicious_ips" in data
        assert "blocked_ips" in data
        assert any(b["ip"] == "10.0.0.6" for b in data["blocked_ips"])

    def test_block_close_tcp(self, client, admin_headers, db):
        r = client.post("/api/mitigation/block",
            json={"ip": "10.0.0.7", "action": "CLOSE_TCP", "port": 22, "attack_type": "SSH"},
            headers=admin_headers)
        assert r.status_code == 200
        blocked = db.query(BlockedIP).filter(BlockedIP.ip == "10.0.0.7").first()
        assert blocked is not None

    def test_block_invalid_action(self, client, admin_headers):
        r = client.post("/api/mitigation/block",
            json={"ip": "10.0.0.8", "action": "INVALID_ACTION"},
            headers=admin_headers)
        # Pydantic validation returns 422 for invalid action values
        assert r.status_code in (400, 422)

    def test_block_missing_port(self, client, admin_headers):
        r = client.post("/api/mitigation/block",
            json={"ip": "10.0.0.9", "action": "CLOSE_TCP"},
            headers=admin_headers)
        assert r.status_code == 400


# ── Tests de Reglas ────────────────────────────────────────

class TestRules:
    def test_create_rule(self, client, admin_headers, db):
        r = client.post("/api/rules/",
            json={"name": "Test Block", "condition": "attack_type == 'Brute Force'", "action": "BLOCK"},
            headers=admin_headers)
        assert r.status_code == 200
        data = r.json()
        assert data["name"] == "Test Block"
        assert data["action"] == "BLOCK"
        assert data["enabled"] == True

    def test_create_rule_requires_admin(self, client, db):
        hashed = get_password_hash("view123")
        user = User(username="viewer2", hashed_password=hashed, role="viewer", is_active=1)
        db.add(user)
        db.commit()
        r = client.post("/api/auth/login", data={"username": "viewer2", "password": "view123"})
        token = r.json()["access_token"]
        r2 = client.post("/api/rules/",
            json={"name": "Test", "condition": "true", "action": "BLOCK"},
            headers={"Authorization": f"Bearer {token}"})
        assert r2.status_code == 403

    def test_get_rules(self, client, admin_headers, db):
        db.add(Rule(name="Rule1", condition="true", action="BLOCK"))
        db.commit()
        r = client.get("/api/rules/", headers=admin_headers)
        assert r.status_code == 200
        data = r.json()
        assert len(data) >= 1
        assert any(rule["name"] == "Rule1" for rule in data)

    def test_update_rule(self, client, admin_headers, db):
        rule = Rule(name="Old", condition="true", action="BLOCK")
        db.add(rule)
        db.commit()
        db.refresh(rule)
        r = client.put(f"/api/rules/{rule.id}",
            json={"name": "Updated", "enabled": False},
            headers=admin_headers)
        assert r.status_code == 200
        assert r.json()["name"] == "Updated"
        assert r.json()["enabled"] == False

    def test_update_rule_not_found(self, client, admin_headers):
        r = client.put("/api/rules/9999",
            json={"name": "Ghost"},
            headers=admin_headers)
        assert r.status_code == 404

    def test_delete_rule(self, client, admin_headers, db):
        rule = Rule(name="DeleteMe", condition="true", action="ALERT")
        db.add(rule)
        db.commit()
        db.refresh(rule)
        r = client.delete(f"/api/rules/{rule.id}", headers=admin_headers)
        assert r.status_code == 200
        assert db.query(Rule).filter(Rule.id == rule.id).first() is None

    def test_delete_rule_not_found(self, client, admin_headers):
        r = client.delete("/api/rules/9999", headers=admin_headers)
        assert r.status_code == 404

    def test_get_rules_no_auth(self, client):
        r = client.get("/api/rules/")
        assert r.status_code == 401


# ── Tests de Sistema / Health ──────────────────────────────

class TestSystem:
    def test_health_endpoint(self, client):
        r = client.get("/api/health")
        assert r.status_code == 200
        data = r.json()
        assert "status" in data
        assert "app" in data
        assert data["app"] == "SMAR-IA IDS"

    def test_health_has_components(self, client):
        r = client.get("/api/health")
        data = r.json()
        assert "components" in data
        assert "ml_model" in data["components"]
        assert "database_security" in data["components"]
        assert "database_traffic" in data["components"]

    def test_stats_endpoint(self, client):
        r = client.get("/api/stats")
        assert r.status_code == 200
        data = r.json()
        assert "counts" in data
        assert "resources" in data

    def test_stats_counts_keys(self, client):
        r = client.get("/api/stats")
        data = r.json()
        expected_keys = {"total_logs", "total_last_24h", "critical", "warning", "info",
                         "auto_blocked", "manual_blocked", "pending_alerts", "active_blocked_ips",
                         "whitelist_count", "avg_latency_ms"}
        assert expected_keys.issubset(data["counts"].keys())

    def test_alerts_count(self, client):
        r = client.get("/api/stats/alerts-count")
        assert r.status_code == 200
        data = r.json()
        assert "pending_count" in data
        assert "recent_alerts" in data

    def test_active_threats(self, client):
        r = client.get("/api/stats/active-threats")
        assert r.status_code == 200
        data = r.json()
        assert "pending_alerts" in data
        assert "top_sources" in data
        assert "blocked_ips" in data


# ── Tests de Auditoría ─────────────────────────────────────

class TestAudit:
    def test_audit_log_exists(self, client, admin_headers, db):
        r = client.post("/api/mitigation/block",
            json={"ip": "10.10.10.10", "action": "BLOCK_IP", "attack_type": "Test Audit"},
            headers=admin_headers)
        assert r.status_code == 200
        r2 = client.get("/api/audit/", headers=admin_headers)
        assert r2.status_code == 200
        logs = r2.json()
        assert len(logs) >= 1
        assert any(log["action"] == "BLOCK" for log in logs)

    def test_audit_log_unblock(self, client, admin_headers, db):
        from routers.mitigation import record_block
        record_block(db, "10.10.10.11", method="TEST", reason="test", action_taken="test")
        r = client.post("/api/mitigation/unblock",
            json={"ip": "10.10.10.11"},
            headers=admin_headers)
        r2 = client.get("/api/audit/", headers=admin_headers)
        assert any(log["action"] == "UNBLOCK" for log in r2.json())

    def test_audit_requires_auth(self, client):
        r = client.get("/api/audit/")
        assert r.status_code == 401

    def test_audit_log_rule_create(self, client, admin_headers, db):
        r = client.post("/api/rules/",
            json={"name": "AuditRule", "condition": "true", "action": "ALERT"},
            headers=admin_headers)
        assert r.status_code == 200
        r2 = client.get("/api/audit/", headers=admin_headers)
        assert any(log["action"] == "RULE_CREATE" for log in r2.json())


# ── Tests de Logs / Export ─────────────────────────────────

class TestLogs:
    def test_logs_endpoint(self, client):
        r = client.get("/api/logs?limit=5")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_logs_export_csv(self, client):
        r = client.get("/api/logs/export?format=csv")
        assert r.status_code == 200
        assert "text/csv" in r.headers["content-type"]
        assert "id,timestamp,source_ip" in r.text

    def test_logs_export_unsupported_format(self, client):
        r = client.get("/api/logs/export?format=xml")
        assert r.status_code == 200
        data = r.json()
        assert "error" in data


# ── Tests de WebSocket ─────────────────────────────────────

class TestWebSocket:
    def test_websocket_connect(self, client):
        with client.websocket_connect("/ws"):
            pass

    def test_websocket_receives_broadcast(self, client, admin_headers):
        with client.websocket_connect("/ws") as ws:
            r = client.post("/api/mitigation/block",
                json={"ip": "10.20.30.40", "action": "BLOCK_IP"},
                headers=admin_headers)
            assert r.status_code == 200
            data = ws.receive_json()
            assert data["type"] == "mitigation_event"
            assert data["event"] == "block"
            assert data["ip"] == "10.20.30.40"

    def test_websocket_receives_unblock(self, client, admin_headers, db):
        from routers.mitigation import record_block
        record_block(db, "10.20.30.41", method="TEST", reason="test", action_taken="test")
        with client.websocket_connect("/ws") as ws:
            r = client.post("/api/mitigation/unblock",
                json={"ip": "10.20.30.41"},
                headers=admin_headers)
            assert r.status_code == 200
            data = ws.receive_json()
            assert data["type"] == "mitigation_event"
            assert data["event"] == "unblock"


# ── Tests de Whitelist ─────────────────────────────────────

class TestWhitelist:
    def test_get_whitelist_empty(self, client, admin_headers):
        r = client.get("/api/whitelist/", headers=admin_headers)
        assert r.status_code == 200
        assert r.json() == []

    def test_add_to_whitelist(self, client, admin_headers, db):
        r = client.post("/api/whitelist/",
            json={"ip": "192.168.1.1", "reason": "Servidor DNS"},
            headers=admin_headers)
        assert r.status_code == 200
        data = r.json()
        assert data["ip"] == "192.168.1.1"
        assert data["reason"] == "Servidor DNS"

    def test_add_duplicate_whitelist(self, client, admin_headers, db):
        client.post("/api/whitelist/",
            json={"ip": "192.168.1.2", "reason": "test"},
            headers=admin_headers)
        r = client.post("/api/whitelist/",
            json={"ip": "192.168.1.2", "reason": "otra vez"},
            headers=admin_headers)
        assert r.status_code == 400

    def test_whitelist_requires_admin(self, client, db):
        hashed = get_password_hash("view123")
        user = User(username="whitelist_viewer", hashed_password=hashed, role="viewer", is_active=1)
        db.add(user)
        db.commit()
        r = client.post("/api/auth/login", data={"username": "whitelist_viewer", "password": "view123"})
        token = r.json()["access_token"]
        r2 = client.post("/api/whitelist/",
            json={"ip": "10.0.0.1", "reason": "test"},
            headers={"Authorization": f"Bearer {token}"})
        assert r2.status_code == 403

    def test_delete_whitelist(self, client, admin_headers, db):
        r = client.post("/api/whitelist/",
            json={"ip": "192.168.1.99", "reason": "delete me"},
            headers=admin_headers)
        eid = r.json()["id"]
        r2 = client.delete(f"/api/whitelist/{eid}", headers=admin_headers)
        assert r2.status_code == 200
        r3 = client.get("/api/whitelist/", headers=admin_headers)
        assert all(e["ip"] != "192.168.1.99" for e in r3.json())

    def test_is_whitelisted(self, db):
        from routers.whitelist import is_whitelisted
        from database import Whitelist
        db.add(Whitelist(ip="10.0.0.1", reason="test"))
        db.commit()
        assert is_whitelisted(db, "10.0.0.1") == True
        assert is_whitelisted(db, "1.2.3.4") == False


# ── Tests de Audit Logger (JSON con hash) ───────────────────

class TestAuditLogger:
    def test_write_audit_log(self):
        from audit_logger import write_audit_log, read_audit_logs
        event = write_audit_log({
            "event_type": "INTRUSION_MITIGATED",
            "network": {"source_ip": "10.0.0.5"},
            "detection": {"model_confidence": 0.97, "attack_type": "DDoS SYN Flood"},
            "response": {"mitigation_latency_ms": 12.34, "action_taken": "AUTO-BLOCKED"},
            "iso_compliance": {"controls_activated": ["A.8.15"]},
        })
        assert "event_id" in event
        assert "timestamp" in event
        assert "log_integrity_hash" in event
        assert event["log_integrity_hash"].startswith("sha256=")
        assert event["event_type"] == "INTRUSION_MITIGATED"

    def test_read_audit_logs(self):
        from audit_logger import write_audit_log, read_audit_logs, get_available_dates
        from datetime import datetime, timezone
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        write_audit_log({
            "event_type": "BLOCK_ADDED",
            "network": {"source_ip": "10.0.0.6"},
            "detection": {},
            "response": {"action_taken": "BLOCKED"},
            "iso_compliance": {"controls_activated": ["A.8.20"]},
        })
        events = read_audit_logs(today)
        assert len(events) >= 1
        assert any(e["event_type"] == "BLOCK_ADDED" for e in events)
        dates = get_available_dates()
        assert today in dates

    def test_json_audit_log_endpoint(self, client, admin_headers, db):
        from audit_logger import write_audit_log
        write_audit_log({
            "event_type": "INTRUSION_MITIGATED",
            "network": {"source_ip": "10.0.0.7"},
            "detection": {"model_confidence": 0.95},
            "response": {"action_taken": "BLOCK"},
            "iso_compliance": {"controls_activated": ["A.8.15"]},
        })
        r = client.get("/api/audit/json", headers=admin_headers)
        assert r.status_code == 200
        logs = r.json()
        assert isinstance(logs, list)
        assert any(l["event_type"] == "INTRUSION_MITIGATED" for l in logs)

    def test_json_audit_requires_admin(self, client, db):
        hashed = get_password_hash("view123")
        user = User(username="audit_viewer", hashed_password=hashed, role="viewer", is_active=1)
        db.add(user)
        db.commit()
        r = client.post("/api/auth/login", data={"username": "audit_viewer", "password": "view123"})
        token = r.json()["access_token"]
        r2 = client.get("/api/audit/json", headers={"Authorization": f"Bearer {token}"})
        assert r2.status_code == 403


# ── Tests de Firewall (DRY_RUN) ────────────────────────────

class TestFirewall:
    def test_firewall_dry_run_block_returns_float(self):
        from firewall import apply_iptables_block
        result = apply_iptables_block("8.8.8.8")
        assert isinstance(result, float)
        assert result == 0.0

    def test_firewall_dry_run_unblock(self):
        from firewall import remove_iptables_block
        assert remove_iptables_block("8.8.8.8") == True

    def test_firewall_sync(self):
        from firewall import restore_iptables_rules
        restore_iptables_rules(["1.1.1.1", "2.2.2.2"])

    def test_firewall_sync_alias(self):
        from firewall import sync_firewall_with_db
        sync_firewall_with_db(["1.1.1.1", "2.2.2.2"])

    def test_firewall_apply_dry_run_logs(self, caplog):
        import logging
        caplog.set_level(logging.INFO)
        from firewall import apply_iptables_block
        result = apply_iptables_block("8.8.4.4")
        assert result == 0.0
        assert "DRY-RUN" in caplog.text
        assert "8.8.4.4" in caplog.text

    def test_firewall_is_active_dry_run(self):
        from firewall import is_iptables_block_active
        # En DRY_RUN no hay iptables real, debe retornar False sin excepción
        assert is_iptables_block_active("1.2.3.4") == False


# ── Tests de Alerting ──────────────────────────────────────

class TestAlerting:
    @pytest.mark.asyncio
    async def test_notify_no_webhook(self):
        from alerting import notify_threat
        await notify_threat("1.2.3.4", "Test", 0.95, "ALERT")

    @pytest.mark.asyncio
    async def test_notify_empty_webhooks_returns_early(self):
        from alerting import notify_threat
        result = await notify_threat("1.2.3.5", "Brute Force", 0.99, "BLOCK")
        assert result is None

    def test_format_slack(self):
        from alerting import _format_slack
        payload = _format_slack("1.2.3.4", "Brute Force", 0.95, "BLOCK")
        assert payload["blocks"][0]["text"]["text"] == "🚨 SMAR-IA: Amenaza detectada"

    def test_format_discord(self):
        from alerting import _format_discord
        payload = _format_discord("1.2.3.4", "Brute Force", 0.95, "ALERT")
        assert "SMAR-IA" in payload["embeds"][0]["title"]

    def test_format_generic(self):
        from alerting import _format_generic
        payload = _format_generic("1.2.3.4", "Brute Force", 0.95, "ALERT")
        assert "AMENAZA" in payload["text"]


# ── Tests de RBAC ──────────────────────────────────────────

class TestRBAC:
    def test_viewer_cannot_block(self, client, db):
        hashed = get_password_hash("view123")
        user = User(username="viewer3", hashed_password=hashed, role="viewer", is_active=1)
        db.add(user)
        db.commit()
        r = client.post("/api/auth/login", data={"username": "viewer3", "password": "view123"})
        token = r.json()["access_token"]
        h = {"Authorization": f"Bearer {token}"}
        r = client.post("/api/mitigation/block", json={"ip": "1.1.1.1", "action": "BLOCK_IP"}, headers=h)
        assert r.status_code == 403
        r = client.post("/api/mitigation/unblock", json={"ip": "1.1.1.1"}, headers=h)
        assert r.status_code == 403
        r = client.get("/api/mitigation/suspicious", headers=h)
        assert r.status_code == 200

    def test_viewer_can_view_logs(self, client, db):
        hashed = get_password_hash("view123")
        user = User(username="viewer4", hashed_password=hashed, role="viewer", is_active=1)
        db.add(user)
        db.commit()
        r = client.post("/api/auth/login", data={"username": "viewer4", "password": "view123"})
        token = r.json()["access_token"]
        h = {"Authorization": f"Bearer {token}"}
        r = client.get("/api/logs", headers=h)
        assert r.status_code == 200

    def test_viewer_can_view_audit(self, client, db):
        hashed = get_password_hash("view123")
        user = User(username="viewer5", hashed_password=hashed, role="viewer", is_active=1)
        db.add(user)
        db.commit()
        r = client.post("/api/auth/login", data={"username": "viewer5", "password": "view123"})
        token = r.json()["access_token"]
        r2 = client.get("/api/audit/", headers={"Authorization": f"Bearer {token}"})
        assert r2.status_code == 200

    def test_viewer_cannot_create_rules(self, client, db):
        hashed = get_password_hash("view123")
        user = User(username="viewer6", hashed_password=hashed, role="viewer", is_active=1)
        db.add(user)
        db.commit()
        r = client.post("/api/auth/login", data={"username": "viewer6", "password": "view123"})
        token = r.json()["access_token"]
        r2 = client.post("/api/rules/",
            json={"name": "X", "condition": "true", "action": "BLOCK"},
            headers={"Authorization": f"Bearer {token}"})
        assert r2.status_code == 403


# ── Tests de ML Service ────────────────────────────────────

class TestMLService:
    def test_ml_service_not_loaded(self):
        from ml_service import ml_service
        from ml_service import MLService
        svc = MLService()
        assert svc.is_loaded == False

    def test_ml_predict_returns_unknown_when_not_loaded(self):
        from ml_service import MLService
        svc = MLService()
        cls, conf = svc.predict([0.0] * 80)
        assert cls == "Unknown"
        assert conf == 0.0

    def test_ml_get_model_info_not_loaded(self):
        from ml_service import MLService
        svc = MLService()
        info = svc.get_model_info()
        assert info["is_loaded"] == False
        assert info["model_type"] == "N/A"

    def test_global_ml_service_instance(self):
        from ml_service import ml_service
        assert hasattr(ml_service, "is_loaded")
        assert hasattr(ml_service, "predict")
        assert hasattr(ml_service, "get_model_info")


# ── Tests de Auth module ───────────────────────────────────

class TestAuthModule:
    def test_password_hash_and_verify(self):
        from auth import get_password_hash, verify_password
        pw = "SuperSecret123!"
        hashed = get_password_hash(pw)
        assert hashed != pw
        assert verify_password(pw, hashed) == True
        assert verify_password("wrong", hashed) == False

    def test_create_access_token(self):
        token = create_access_token(data={"sub": "testuser", "role": "admin"})
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 20

    def test_create_refresh_token(self):
        from auth import create_refresh_token
        token = create_refresh_token(data={"sub": "testuser", "role": "viewer"})
        assert token is not None
        assert isinstance(token, str)

    def test_token_blacklist(self):
        from auth import token_blacklist, logout_token, is_token_blacklisted
        token_blacklist.clear()
        assert is_token_blacklisted("dummy_token") == False
        logout_token("dummy_token")
        assert is_token_blacklisted("dummy_token") == True


# ── Tests de Config ────────────────────────────────────────

class TestConfig:
    def test_dry_run_enabled(self):
        from config import DRY_RUN
        assert DRY_RUN == True

    def test_app_name(self):
        from config import APP_NAME
        assert APP_NAME == "SMAR-IA IDS"

    def test_app_version(self):
        from config import APP_VERSION
        assert APP_VERSION == "1.0.0"


# ── Tests de main.py helpers ───────────────────────────────

class TestMainHelpers:
    def test_evaluate_condition_true(self):
        from main import evaluate_condition
        assert evaluate_condition("attack_type == 'Brute Force'", {"attack_type": "Brute Force"}) == True

    def test_evaluate_condition_false(self):
        from main import evaluate_condition
        assert evaluate_condition("attack_type == 'Brute Force'", {"attack_type": "Normal"}) == False

    def test_evaluate_condition_numeric(self):
        from main import evaluate_condition
        assert evaluate_condition("confidence > 0.8", {"confidence": 0.95}) == True
        assert evaluate_condition("confidence > 0.8", {"confidence": 0.5}) == False

    def test_evaluate_condition_malformed(self):
        from main import evaluate_condition
        assert evaluate_condition("not valid python !!!", {"attack_type": "test"}) == False


# ── Tests de eventos / ConnectionManager ───────────────────

class TestEventManager:
    def test_manager_broadcast_no_connections(self):
        from event_manager import manager
        import asyncio
        asyncio.run(manager.broadcast({"type": "test", "data": "hello"}))
        # No connections, should not raise

    def test_connection_manager_init(self):
        from event_manager import ConnectionManager
        cm = ConnectionManager()
        assert cm.active_connections == []


# ── Tests de ISO compliance ───────────────────────────────

class TestISOCompliance:
    def test_security_log_has_iso_field(self, client, admin_headers, db):
        r = client.post("/api/mitigation/block",
            json={"ip": "10.0.0.99", "action": "BLOCK_IP", "attack_type": "ISO Test"},
            headers=admin_headers)
        assert r.status_code == 200
        log = db.query(SecurityLog).filter(SecurityLog.source_ip == "10.0.0.99").first()
        assert log is not None
        assert log.iso_control == "A.8.20"

    def test_audit_log_has_iso_field(self, client, admin_headers, db):
        r = client.post("/api/mitigation/block",
            json={"ip": "10.0.0.100", "action": "BLOCK_IP", "attack_type": "ISO Audit"},
            headers=admin_headers)
        assert r.status_code == 200
        audit = db.query(AuditLog).first()
        assert audit is not None
        assert audit.iso_control == "A.8.21"


# ── Tests avanzados de Firewall ────────────────────────────

class TestFirewallAdvanced:
    def test_validate_ip_valid(self):
        from firewall import _validate_ip
        assert _validate_ip("192.168.1.1") == "192.168.1.1"
        assert _validate_ip("10.0.0.1") == "10.0.0.1"

    def test_validate_ip_invalid(self):
        from firewall import _validate_ip
        import pytest
        with pytest.raises(ValueError):
            _validate_ip("not-an-ip")
        with pytest.raises(ValueError):
            _validate_ip("999.999.999.999")
        with pytest.raises(ValueError):
            _validate_ip("")

    def test_remove_iptables_block_dry_run(self):
        from firewall import remove_iptables_block
        assert remove_iptables_block("8.8.8.8") == True

    def test_remove_iptables_block_invalid_ip(self):
        from firewall import remove_iptables_block
        assert remove_iptables_block("bad-ip") == False

    def test_restore_rules_empty(self):
        from firewall import restore_iptables_rules
        restore_iptables_rules([])

    def test_restore_rules_dry_run(self):
        from firewall import restore_iptables_rules
        restore_iptables_rules(["10.0.0.1", "10.0.0.2"])

    def test_apply_block_invalid_ip(self):
        from firewall import apply_iptables_block
        import pytest
        with pytest.raises(ValueError):
            apply_iptables_block("bad-ip")

    def test_is_active_invalid_ip(self):
        from firewall import is_iptables_block_active
        assert is_iptables_block_active("bad-ip") == False


# ── Tests avanzados de ML Service ──────────────────────────

class TestMLServiceAdvanced:
    def test_predict_bad_features_length(self):
        from ml_service import MLService
        svc = MLService()
        # Even without loaded model, should handle gracefully
        cls, conf = svc.predict([0.0] * 10)
        assert cls == "Unknown"

    def test_get_model_info_loaded_no_models(self):
        from ml_service import MLService
        svc = MLService()
        svc.is_loaded = True
        info = svc.get_model_info()
        assert info["is_loaded"] == True
        assert info["num_classes"] == 0

    def test_load_models_failure(self, tmp_path):
        from ml_service import MLService
        svc = MLService(models_dir=str(tmp_path))
        svc.load_models()
        assert svc.is_loaded == False


# ── Tests avanzados de Event Manager ───────────────────────

class TestEventManagerAdvanced:
    @pytest.mark.asyncio
    async def test_connect_and_disconnect(self):
        from event_manager import ConnectionManager
        from unittest.mock import AsyncMock, MagicMock
        cm = ConnectionManager()
        ws = AsyncMock()
        ws.accept = AsyncMock()
        ws.send_text = AsyncMock()
        await cm.connect(ws)
        assert len(cm.active_connections) == 1
        await cm.disconnect(ws)
        assert len(cm.active_connections) == 0

    @pytest.mark.asyncio
    async def test_broadcast_to_multiple(self):
        from event_manager import ConnectionManager
        from unittest.mock import AsyncMock
        cm = ConnectionManager()
        ws1, ws2 = AsyncMock(), AsyncMock()
        ws1.accept = AsyncMock()
        ws2.accept = AsyncMock()
        ws1.send_text = AsyncMock()
        ws2.send_text = AsyncMock()
        await cm.connect(ws1)
        await cm.connect(ws2)
        await cm.broadcast({"msg": "test"})
        assert ws1.send_text.called
        assert ws2.send_text.called

    @pytest.mark.asyncio
    async def test_broadcast_failure_disconnects(self):
        from event_manager import ConnectionManager
        from unittest.mock import AsyncMock
        cm = ConnectionManager()
        ws = AsyncMock()
        ws.accept = AsyncMock()
        ws.send_text = AsyncMock(side_effect=Exception("fail"))
        await cm.connect(ws)
        await cm.broadcast({"msg": "fail"})
        assert len(cm.active_connections) == 0

    @pytest.mark.asyncio
    async def test_disconnect_not_connected(self):
        from event_manager import ConnectionManager
        from unittest.mock import AsyncMock
        cm = ConnectionManager()
        ws = AsyncMock()
        await cm.disconnect(ws)
        assert len(cm.active_connections) == 0


# ── Tests avanzados de Auth ────────────────────────────────

class TestAuthAdvanced:
    def test_verify_password_bad_hash(self):
        from auth import verify_password
        assert verify_password("test", "not-a-valid-hash") == False
        assert verify_password("test", "") == False

    def test_create_access_token_with_expiry(self):
        from auth import create_access_token
        from datetime import timedelta
        token = create_access_token({"sub": "user"}, expires_delta=timedelta(minutes=5))
        assert token is not None
        assert len(token) > 20


# ── Tests avanzados de Config ──────────────────────────────

class TestConfigAdvanced:
    def test_threshold_values(self):
        from config import AUTO_BLOCK_THRESHOLD, SUSPICIOUS_ALERT_COUNT, SUSPICIOUS_WINDOW_MINUTES
        assert 0 < AUTO_BLOCK_THRESHOLD <= 1.0
        assert SUSPICIOUS_ALERT_COUNT > 0
        assert SUSPICIOUS_WINDOW_MINUTES > 0


# ── Tests avanzados de main.py helpers ─────────────────────

class TestMainHelpersAdvanced:
    def test_evaluate_condition_with_ip(self):
        from main import evaluate_condition
        assert evaluate_condition("ip == '10.0.0.1'", {"ip": "10.0.0.1"}) == True
        assert evaluate_condition("ip == '10.0.0.1'", {"ip": "10.0.0.2"}) == False

    def test_evaluate_condition_complex(self):
        from main import evaluate_condition
        ctx = {"attack_type": "DDoS SYN Flood", "confidence": 0.95}
        assert evaluate_condition("attack_type == 'DDoS SYN Flood' and confidence > 0.9", ctx) == True
        assert evaluate_condition("attack_type == 'Normal' or confidence < 0.5", ctx) == False


# ── Tests de Audit Logger (adicionales) ────────────────────

class TestAuditLoggerAdvanced:
    def test_read_nonexistent_date(self):
        from audit_logger import read_audit_logs
        events = read_audit_logs("2000-01-01")
        assert events == []

    def test_get_available_dates_empty(self):
        from audit_logger import get_available_dates, LOGS_DIR
        import os, shutil
        if os.path.exists(LOGS_DIR):
            backup = LOGS_DIR + "_bak"
            os.rename(LOGS_DIR, backup)
        try:
            dates = get_available_dates()
            assert dates == []
        finally:
            if os.path.exists(backup):
                shutil.rmtree(LOGS_DIR, ignore_errors=True)
                os.rename(backup, LOGS_DIR)


# ── Tests de Alerting (adicionales) ────────────────────────

class TestAlertingAdvanced:
    def test_build_emoji_block(self):
        from alerting import _build_emoji
        assert _build_emoji("BLOCK") == "🛑"
        assert _build_emoji("ALERT") == "⚠️"
        assert _build_emoji("test") == "🚨"

    def test_format_slack_alert(self):
        from alerting import _format_slack
        payload = _format_slack("1.2.3.4", "DDoS SYN Flood", 0.85, "ALERT")
        fields = payload["blocks"][1]["fields"]
        field_texts = [f["text"] for f in fields]
        assert any("1.2.3.4" in t for t in field_texts)
        assert any("DDoS" in t for t in field_texts)

    def test_format_discord_alert(self):
        from alerting import _format_discord
        payload = _format_discord("5.6.7.8", "Brute Force", 0.99, "ALERT")
        embed = payload["embeds"][0]
        assert embed["color"] == 16776960  # yellow for alert

    def test_format_generic_alert(self):
        from alerting import _format_generic
        result = _format_generic("5.6.7.8", "Port Scan", 0.75, "BLOCK")
        assert "*IP:*" in result["text"]
        assert "5.6.7.8" in result["text"]


# ── Tests de Database avanzados ────────────────────────────

class TestDatabaseAdvanced:
    def test_get_security_db(self):
        from database import get_security_db
        gen = get_security_db()
        db = next(gen)
        assert db is not None
        try:
            next(gen)
        except StopIteration:
            pass

    def test_get_traffic_db(self):
        from database import get_traffic_db
        gen = get_traffic_db()
        db = next(gen)
        assert db is not None
        try:
            next(gen)
        except StopIteration:
            pass


# ── Limpieza final ─────────────────────────────────────────

def teardown_module():
    """Remove test databases after all tests."""
    import os
    for f in ["test_security.db", "test_traffic.db"]:
        if os.path.exists(f):
            os.remove(f)
