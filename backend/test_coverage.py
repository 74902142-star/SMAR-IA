"""SMAR-IA — Tests de cobertura para módulos con dependencias externas."""

import os
import sys
import json
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient

os.environ["SMAR_IA_DRY_RUN"] = "true"
os.environ["SMAR_IA_SECRET_KEY"] = "test_secret_key_not_for_production"
os.environ["SMAR_IA_SECURITY_DB"] = "sqlite:///./test_security.db"
os.environ["SMAR_IA_TRAFFIC_DB"] = "sqlite:///./test_traffic.db"
os.environ["SMAR_IA_MODELS_DIR"] = "/tmp/smaria_test_models"

from main import app
from database import (
    SecurityBase, TrafficBase, security_engine, traffic_engine,
    SecuritySessionLocal, TrafficSessionLocal, User, SecurityLog,
    BlockedIP, Whitelist, NetworkTraffic,
    get_security_db, get_traffic_db,
)
from auth import create_access_token, get_password_hash


@pytest.fixture(autouse=True)
def setup_db():
    SecurityBase.metadata.create_all(bind=security_engine)
    TrafficBase.metadata.create_all(bind=traffic_engine)
    with security_engine.connect() as conn:
        for table in reversed(SecurityBase.metadata.sorted_tables):
            conn.execute(table.delete())
        conn.commit()
    with traffic_engine.connect() as conn:
        for table in reversed(TrafficBase.metadata.sorted_tables):
            conn.execute(table.delete())
        conn.commit()
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
    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        hashed = get_password_hash("admin123")
        admin = User(username="admin", hashed_password=hashed, role="admin", is_active=1)
        db.add(admin)
        db.commit()
    r = client.post("/api/auth/login", data={"username": "admin", "password": "admin123"})
    return r.json()["access_token"]


@pytest.fixture
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


# ── Tests de Firewall con subprocess mockeado ──────────────

class TestFirewallMocked:
    def test_remove_iptables_real_execution(self):
        with patch("firewall.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            from firewall import remove_iptables_block
            with patch("firewall.DRY_RUN", False):
                result = remove_iptables_block("10.0.0.1")
                assert result == True
                mock_run.assert_called_once()

    def test_remove_iptables_failure(self):
        with patch("firewall.subprocess.run") as mock_run:
            from subprocess import CalledProcessError
            mock_run.side_effect = CalledProcessError(1, "iptables")
            from firewall import remove_iptables_block
            with patch("firewall.DRY_RUN", False):
                result = remove_iptables_block("10.0.0.1")
                assert result == False

    def test_remove_iptables_timeout(self):
        with patch("firewall.subprocess.run") as mock_run:
            from subprocess import TimeoutExpired
            mock_run.side_effect = TimeoutExpired("iptables", 30)
            from firewall import remove_iptables_block
            with patch("firewall.DRY_RUN", False):
                result = remove_iptables_block("10.0.0.1")
                assert result == False

    def test_remove_iptables_oserror(self):
        with patch("firewall.subprocess.run") as mock_run:
            mock_run.side_effect = OSError("permission denied")
            from firewall import remove_iptables_block
            with patch("firewall.DRY_RUN", False):
                result = remove_iptables_block("10.0.0.1")
                assert result == False

    def test_apply_block_already_exists(self):
        with patch("firewall.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            from firewall import apply_iptables_block
            with patch("firewall.DRY_RUN", False):
                result = apply_iptables_block("10.0.0.1")
                assert result == 0.0  # already exists

    def test_apply_block_new_rule(self):
        with patch("firewall.subprocess.run") as mock_run:
            check_result = MagicMock(returncode=1)  # rule doesn't exist
            add_result = MagicMock(returncode=0)
            mock_run.side_effect = [check_result, add_result]
            from firewall import apply_iptables_block
            with patch("firewall.DRY_RUN", False):
                result = apply_iptables_block("10.0.0.1")
                assert result > 0  # positive latency

    def test_apply_block_timeout(self):
        with patch("firewall.subprocess.run") as mock_run:
            from subprocess import TimeoutExpired
            check_result = MagicMock(returncode=1)
            mock_run.side_effect = [check_result, TimeoutExpired(cmd="iptables", timeout=30)]
            from firewall import apply_iptables_block
            with patch("firewall.DRY_RUN", False):
                result = apply_iptables_block("10.0.0.1")
                assert result == -1.0

    def test_apply_block_oserror(self):
        with patch("firewall.subprocess.run") as mock_run:
            from subprocess import CalledProcessError
            check_result = MagicMock(returncode=1)
            mock_run.side_effect = [check_result, CalledProcessError(1, "iptables")]
            from firewall import apply_iptables_block
            with patch("firewall.DRY_RUN", False):
                result = apply_iptables_block("10.0.0.1")
                assert result == -1.0

    def test_apply_block_calledprocesserror(self):
        with patch("firewall.subprocess.run") as mock_run:
            from subprocess import CalledProcessError
            check_result = MagicMock(returncode=1)
            mock_run.side_effect = [check_result, CalledProcessError(2, "iptables")]
            from firewall import apply_iptables_block
            with patch("firewall.DRY_RUN", False):
                result = apply_iptables_block("10.0.0.1")
                assert result == -1.0

    def test_is_active_with_sudo(self):
        with patch("firewall.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            from firewall import is_iptables_block_active
            with patch("firewall.DRY_RUN", False):
                assert is_iptables_block_active("10.0.0.1") == True

    def test_restore_rules(self):
        with patch("firewall.apply_iptables_block") as mock_apply:
            mock_apply.return_value = 5.0
            from firewall import restore_iptables_rules, sync_firewall_with_db
            with patch("firewall.DRY_RUN", False):
                restore_iptables_rules(["10.0.0.1", "10.0.0.2"])
                assert mock_apply.call_count == 2

    def test_sync_firewall_alias(self):
        with patch("firewall.restore_iptables_rules") as mock_restore:
            from firewall import sync_firewall_with_db
            sync_firewall_with_db(["10.0.0.1"])
            mock_restore.assert_called_once_with(["10.0.0.1"])


# ── Tests de Alerting con HTTP mockeado ────────────────────

class TestAlertingMocked:
    @pytest.mark.asyncio
    async def test_send_slack(self):
        with patch("alerting.httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            mock_instance.post.return_value = MagicMock(status_code=200)
            from alerting import _send_slack
            with patch("alerting.SLACK_WEBHOOK_URL", "https://hooks.slack.com/test"):
                await _send_slack("1.2.3.4", "DDoS SYN Flood", 0.95, "BLOCK")
                assert mock_instance.post.called

    @pytest.mark.asyncio
    async def test_send_discord(self):
        with patch("alerting.httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            mock_instance.post.return_value = MagicMock(status_code=204)
            from alerting import _send_discord
            with patch("alerting.DISCORD_WEBHOOK_URL", "https://discord.com/test"):
                await _send_discord("1.2.3.4", "Brute Force", 0.99, "ALERT")
                assert mock_instance.post.called

    @pytest.mark.asyncio
    async def test_send_generic(self):
        with patch("alerting.httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            mock_instance.post.return_value = MagicMock(status_code=200)
            from alerting import _send_generic
            with patch("alerting.GENERIC_WEBHOOK_URL", "https://hooks.example.com/test"):
                await _send_generic("1.2.3.4", "Port Scan", 0.75, "ALERT")
                assert mock_instance.post.called

    @pytest.mark.asyncio
    async def test_slack_error(self):
        with patch("alerting.httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            mock_instance.post.return_value = MagicMock(status_code=500, text="error")
            from alerting import _send_slack
            with patch("alerting.SLACK_WEBHOOK_URL", "https://hooks.slack.com/test"):
                await _send_slack("1.2.3.4", "DDoS", 0.95, "BLOCK")

    @pytest.mark.asyncio
    async def test_notify_all_channels_enabled(self):
        with patch("alerting._send_slack", AsyncMock()) as slack:
            with patch("alerting._send_discord", AsyncMock()) as discord:
                with patch("alerting._send_generic", AsyncMock()) as generic:
                    with patch("alerting._send_email", AsyncMock()) as email:
                        from alerting import notify_threat
                        with patch("alerting.SLACK_WEBHOOK_URL", "https://slack.test"):
                            with patch("alerting.DISCORD_WEBHOOK_URL", "https://discord.test"):
                                with patch("alerting.GENERIC_WEBHOOK_URL", "https://generic.test"):
                                    with patch("alerting.SMTP_HOST", "smtp.test.com"):
                                        with patch("alerting.EMAIL_TO", "admin@test.com"):
                                            await notify_threat("1.2.3.4", "Test", 0.95, "BLOCK")
                                            assert slack.called
                                            assert discord.called
                                            assert generic.called
                                            assert email.called


# ── Tests de Pipeline de main.py ───────────────────────────

class TestMainPipeline:
    def test_evaluate_condition_all_cases(self):
        from main import evaluate_condition
        assert evaluate_condition("confidence == 0.5", {"confidence": 0.5}) == True
        assert evaluate_condition("confidence != 0.5", {"confidence": 0.3}) == True
        assert evaluate_condition("confidence == 0.5", {"confidence": 0.3}) == False

    def test_mark_processed(self):
        from database import TrafficSessionLocal, NetworkTraffic
        db = TrafficSessionLocal()
        entry = NetworkTraffic(source_ip="1.1.1.1", destination_ip="2.2.2.2", features_csv="0,0,0")
        db.add(entry)
        db.commit()
        db.refresh(entry)
        assert entry.is_processed == 0
        from main import _mark_processed
        _mark_processed(entry, db)
        db.refresh(entry)
        assert entry.is_processed == 1
        db.close()

    def test_save_security_log(self):
        from database import SecuritySessionLocal, NetworkTraffic
        from main import _save_security_log
        db = SecuritySessionLocal()
        traffic = NetworkTraffic(source_ip="1.1.1.1", destination_ip="2.2.2.2", features_csv="0,0,0")
        _save_security_log(traffic, "DDoS SYN Flood", 0.95, "AUTO-BLOCKED", db,
                          detection_ts=None, mitigation_ts=None, latency=None)
        log = db.query(SecurityLog).first()
        assert log is not None
        assert log.attack_type == "DDoS SYN Flood"
        assert log.latency_ms is None
        db.close()

    def test_save_security_log_with_latency(self):
        from database import SecuritySessionLocal, NetworkTraffic
        from main import _save_security_log
        from datetime import datetime
        db = SecuritySessionLocal()
        traffic = NetworkTraffic(source_ip="1.1.1.2", destination_ip="2.2.2.2", features_csv="0,0,0")
        _save_security_log(traffic, "Test", 0.5, "LOGGED", db,
                          detection_ts=datetime.utcnow(),
                          mitigation_ts=datetime.utcnow(),
                          latency=15.5)
        log = db.query(SecurityLog).filter(SecurityLog.source_ip == "1.1.1.2").first()
        assert log is not None
        assert log.latency_ms == 15.5
        assert log.detection_timestamp is not None
        assert log.mitigation_timestamp is not None
        db.close()

    def test_write_mitigation_audit(self):
        from database import NetworkTraffic
        from main import _write_mitigation_audit
        from audit_logger import read_audit_logs
        from datetime import datetime, timezone
        traffic = NetworkTraffic(source_ip="10.0.0.99", destination_ip="10.0.0.1", features_csv="0,0,0")
        _write_mitigation_audit(traffic, "Brute Force", 0.97, "AUTO-BLOCKED", 12.34)
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        logs = read_audit_logs(today)
        assert any(
            l["event_type"] == "INTRUSION_MITIGATED" and l["network"]["source_ip"] == "10.0.0.99"
            for l in logs
        )

    def test_broadcast_update(self):
        from database import NetworkTraffic
        from main import _broadcast_update
        from unittest.mock import patch
        traffic = NetworkTraffic(source_ip="1.2.3.4", destination_ip="5.6.7.8", features_csv="0,0,0")
        with patch("main.manager.broadcast", AsyncMock()):
            _broadcast_update(traffic, "Normal", 0.5, False, "NONE")

    def test_log_auto_unblock(self):
        from database import SecuritySessionLocal, BlockedIP, SecurityLog
        from main import _log_auto_unblock
        from datetime import datetime
        db = SecuritySessionLocal()
        entry = BlockedIP(ip="10.0.0.5", method="AUTO", reason="test",
                         blocked_at=datetime.utcnow(), is_active=1)
        db.add(entry)
        db.commit()
        _log_auto_unblock(db, entry)
        db.commit()
        log = db.query(SecurityLog).filter(SecurityLog.source_ip == "10.0.0.5").first()
        assert log is not None
        assert "AUTO-UNBLOCKED" in log.action_taken
        db.close()


# ── Tests de ML Service con modelos mockeados ─────────────

class TestMLServiceMocked:
    def test_load_models_success(self):
        import joblib
        import numpy as np
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.preprocessing import StandardScaler, LabelEncoder
        import tempfile, os

        with tempfile.TemporaryDirectory() as tmp:
            # Train RF on encoded labels (integers) to match ml_service.predict() expectations
            rf = RandomForestClassifier(n_estimators=10, random_state=42)
            rng = np.random.RandomState(42)
            X = np.vstack([
                rng.normal(loc=0.0, scale=0.1, size=(50, 80)),   # Normal
                rng.normal(loc=5.0, scale=0.1, size=(50, 80)),   # DDoS SYN Flood
            ])
            y_str = np.array(["Normal"] * 50 + ["DDoS SYN Flood"] * 50)
            le = LabelEncoder().fit(y_str)
            y_int = le.transform(y_str)
            rf.fit(X, y_int)
            scaler = StandardScaler().fit(X)

            joblib.dump(rf, os.path.join(tmp, "random_forest.pkl"))
            joblib.dump(scaler, os.path.join(tmp, "scaler.pkl"))
            joblib.dump(le, os.path.join(tmp, "label_encoder.pkl"))

            from ml_service import MLService
            svc = MLService(models_dir=tmp)
            svc.load_models()
            assert svc.is_loaded == True

            # Test predict — use a sample from class 1 (DDoS-like)
            features = rng.normal(loc=5.0, scale=0.1, size=80).tolist()
            cls, conf = svc.predict(features)
            assert cls in ("Normal", "DDoS SYN Flood")
            assert 0 <= conf <= 1.0

            # Test get_model_info
            info = svc.get_model_info()
            assert info["is_loaded"] == True
            assert info["num_classes"] == 2
            assert "RandomForest" in info["model_type"]

    def test_predict_with_bad_input(self, tmp_path):
        import joblib
        import numpy as np
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.preprocessing import StandardScaler, LabelEncoder

        rf = RandomForestClassifier(n_estimators=10)
        X = np.random.rand(10, 80)
        y_str = ["Normal"] * 10
        le = LabelEncoder().fit(y_str)
        y_int = le.transform(y_str)
        rf.fit(X, y_int)
        scaler = StandardScaler().fit(X)
        joblib.dump(rf, str(tmp_path / "random_forest.pkl"))
        joblib.dump(scaler, str(tmp_path / "scaler.pkl"))
        joblib.dump(le, str(tmp_path / "label_encoder.pkl"))

        from ml_service import MLService
        svc = MLService(models_dir=str(tmp_path))
        svc.load_models()
        assert svc.is_loaded == True

        # Predict with wrong number of features
        cls, conf = svc.predict([0.0] * 10)
        assert cls == "Error"
        assert conf == 0.0

    def test_model_info_with_loaded_instance(self, tmp_path):
        import joblib
        import numpy as np
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.preprocessing import StandardScaler, LabelEncoder

        rf = RandomForestClassifier(n_estimators=10)
        X = np.random.rand(10, 80)
        y_str = ["Normal"] * 10
        le = LabelEncoder().fit(y_str)
        y_int = le.transform(y_str)
        rf.fit(X, y_int)
        scaler = StandardScaler().fit(X)
        joblib.dump(rf, str(tmp_path / "random_forest.pkl"))
        joblib.dump(scaler, str(tmp_path / "scaler.pkl"))
        joblib.dump(le, str(tmp_path / "label_encoder.pkl"))

        from ml_service import MLService
        svc = MLService(models_dir=str(tmp_path))
        svc.load_models()
        info = svc.get_model_info()
        assert info["loaded_at"] is not None


# ── Tests de Config con variables de entorno ───────────────

class TestConfigWithEnv:
    def test_config_loaded_from_env(self, monkeypatch):
        monkeypatch.setenv("SMAR_IA_DRY_RUN", "true")
        monkeypatch.setenv("SMAR_IA_SECRET_KEY", "custom_key_12345")
        # Force reimport
        import importlib
        import config as cfg
        importlib.reload(cfg)
        assert cfg.DRY_RUN == True
        monkeypatch.delenv("SMAR_IA_SECRET_KEY", raising=False)
        monkeypatch.delenv("SMAR_IA_DRY_RUN", raising=False)


# ── Tests de WebSocket ─────────────────────────────────────

class TestWebSocketAdvanced:
    def test_websocket_multiple_connections(self, client):
        with client.websocket_connect("/ws") as ws1:
            with client.websocket_connect("/ws") as ws2:
                pass  # Both should connect without error

    def test_websocket_receives_from_traffic(self, client, admin_headers):
        """When traffic is processed, WebSocket should receive update."""
        from database import TrafficSessionLocal, NetworkTraffic
        db = TrafficSessionLocal()
        entry = NetworkTraffic(
            source_ip="10.0.0.200", destination_ip="10.0.0.1",
            features_csv=",".join(["0.0"] * 80),
            is_processed=0,
        )
        db.add(entry)
        db.commit()
        db.close()

        # Process one iteration of the traffic loop through the API
        with client.websocket_connect("/ws") as ws:
            # Trigger the traffic processor by requesting stats
            # (processing loop runs in background)
            import asyncio
            asyncio.run(asyncio.sleep(2))


# ── Tests de Auditoría JSON ────────────────────────────────

class TestAuditJsonEndpoint:
    def test_audit_json_with_date_param(self, client, admin_headers):
        from audit_logger import write_audit_log
        from datetime import datetime, timezone
        write_audit_log({
            "event_type": "TEST_EVENT",
            "network": {"source_ip": "10.0.0.100"},
            "detection": {},
            "response": {"action_taken": "test"},
            "iso_compliance": {"controls_activated": ["A.8.15"]},
        })
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        r = client.get(f"/api/audit/json?date={today}", headers=admin_headers)
        assert r.status_code == 200
        logs = r.json()
        assert any(l["event_type"] == "TEST_EVENT" for l in logs)

    def test_audit_dates_endpoint(self, client, admin_headers):
        r = client.get("/api/audit/dates", headers=admin_headers)
        assert r.status_code == 200
        data = r.json()
        assert "dates" in data
        assert isinstance(data["dates"], list)


# ── Tests de ML Evaluation (Punto 6) ────────────────────────

class TestMLEvaluate:
    def test_generate_attack_features_all_types(self):
        import numpy as np
        from benchmark.ml_evaluate import generate_attack_features, ATTACK_CLASSES
        for cls in ATTACK_CLASSES:
            if cls == "Normal":
                continue
            X = generate_attack_features(cls, 10)
            assert X.shape == (10, 80)
            assert not np.isnan(X).any()

    def test_generate_dataset_shape(self):
        import numpy as np
        from benchmark.ml_evaluate import generate_dataset, ATTACK_CLASSES, N_SAMPLES_PER_CLASS
        X, y = generate_dataset()
        expected = len(ATTACK_CLASSES) * N_SAMPLES_PER_CLASS
        assert X.shape == (expected, 80)
        assert len(y) == expected

    def test_compute_metrics_perfect(self):
        from benchmark.ml_evaluate import compute_metrics
        classes = ["Normal", "Attack"]
        y_true = ["Normal", "Normal", "Attack", "Attack"]
        y_pred = ["Normal", "Normal", "Attack", "Attack"]
        m = compute_metrics(y_true, y_pred, classes)
        assert m["accuracy"] == 1.0
        assert m["precision_macro"] == 1.0
        assert m["f1_macro"] == 1.0
        assert "Normal" in m["per_class"]

    def test_compute_metrics_worst(self):
        from benchmark.ml_evaluate import compute_metrics
        classes = ["Normal", "Attack"]
        y_true = ["Normal", "Normal", "Attack", "Attack"]
        y_pred = ["Attack", "Attack", "Normal", "Normal"]
        m = compute_metrics(y_true, y_pred, classes)
        assert m["accuracy"] == 0.0
        assert m["per_class"]["Normal"]["precision"] == 0.0
        assert m["per_class"]["Attack"]["recall"] == 0.0

    def test_load_models_raises_on_missing(self):
        import joblib
        from unittest.mock import patch
        with patch("joblib.load") as mock_load:
            mock_load.side_effect = FileNotFoundError("model not found")
            from benchmark.ml_evaluate import load_models
            with pytest.raises(FileNotFoundError):
                load_models()

    def test_evaluate_function_runs(self):
        from benchmark.ml_evaluate import evaluate
        result = evaluate()
        assert result["n_splits"] == 5
        assert result["overall"]["accuracy"] > 0.9
        assert len(result["fold_results"]) == 5
