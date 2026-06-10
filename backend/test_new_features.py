"""Tests para las nuevas features: PostgreSQL, nftables, progressive block, SIEM, threat intel, honeypot, rate limiter, prometheus."""

import os
import time
import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock

os.environ["SMAR_IA_DRY_RUN"] = "true"
os.environ["SMAR_IA_SECRET_KEY"] = "test_secret_key_for_tests_only_123456789012345678901234567890"
os.environ["SMAR_IA_ADMIN_PASSWORD"] = "admin123"
os.environ["SMAR_IA_FIREWALL_BACKEND"] = "auto"
os.environ["SMAR_IA_SIEM_SYSLOG"] = "false"

from fastapi.testclient import TestClient
from config import (
    FIREWALL_BACKEND, PROGRESSIVE_BLOCK_ENABLED, 
    SIEM_SYSLOG_ENABLED, THREAT_INTEL_ENABLED, HONEYPOT_ENABLED,
    PROMETHEUS_ENABLED, FIREWALL_RATE_LIMIT_ALERTS, FIREWALL_RATE_LIMIT_WINDOW,
    PROGRESSIVE_BLOCK_INTERVALS, HONEYPOT_PORTS,
)


class TestConfigNew:
    def test_firewall_backend_default(self):
        assert FIREWALL_BACKEND == "auto"

    def test_progressive_block_enabled(self):
        assert PROGRESSIVE_BLOCK_ENABLED is True

    def test_siem_syslog_disabled(self):
        assert SIEM_SYSLOG_ENABLED is False

    def test_threat_intel_enabled(self):
        assert THREAT_INTEL_ENABLED is True

    def test_honeypot_enabled(self):
        assert HONEYPOT_ENABLED is False

    def test_prometheus_enabled(self):
        assert PROMETHEUS_ENABLED is True

    def test_rate_limiter_config(self):
        assert FIREWALL_RATE_LIMIT_ALERTS == 10
        assert FIREWALL_RATE_LIMIT_WINDOW == 60

    def test_progressive_intervals(self):
        intervals = [int(x) * 60 for x in PROGRESSIVE_BLOCK_INTERVALS.split(",")]
        assert intervals == [300, 1800, 86400]


class TestProgressiveBlock:
    def test_get_block_duration_first(self):
        from progressive_block import get_block_duration, _offenders
        _offenders.clear()
        duration = get_block_duration("192.168.1.1")
        assert duration == 300

    def test_get_block_duration_second(self):
        import progressive_block
        progressive_block._offenders.clear()
        with patch.object(progressive_block, "_load_offenders", lambda: None):
            with patch.object(progressive_block, "_save_offenders", lambda: None):
                progressive_block.register_block("192.168.1.2")
                duration = progressive_block.get_block_duration("192.168.1.2")
                assert duration == 1800

    def test_get_block_duration_third(self):
        import progressive_block
        progressive_block._offenders.clear()
        with patch.object(progressive_block, "_load_offenders", lambda: None):
            with patch.object(progressive_block, "_save_offenders", lambda: None):
                progressive_block.register_block("192.168.1.3")
                progressive_block.register_block("192.168.1.3")
                duration = progressive_block.get_block_duration("192.168.1.3")
                assert duration == 86400

    def test_get_block_duration_max(self):
        import progressive_block
        progressive_block._offenders.clear()
        with patch.object(progressive_block, "_load_offenders", lambda: None):
            with patch.object(progressive_block, "_save_offenders", lambda: None):
                for _ in range(5):
                    progressive_block.register_block("192.168.1.4")
                duration = progressive_block.get_block_duration("192.168.1.4")
                assert duration == 86400

    def test_reset_offender(self):
        import progressive_block
        progressive_block._offenders.clear()
        with patch.object(progressive_block, "_load_offenders", lambda: None):
            with patch.object(progressive_block, "_save_offenders", lambda: None):
                progressive_block.register_block("192.168.1.5")
                progressive_block.reset_offender("192.168.1.5")
                duration = progressive_block.get_block_duration("192.168.1.5")
                assert duration == 300

    def test_register_and_summary(self):
        import progressive_block
        progressive_block._offenders.clear()
        with patch.object(progressive_block, "_load_offenders", lambda: None):
            with patch.object(progressive_block, "_save_offenders", lambda: None):
                progressive_block.register_block("10.0.0.1")
                summary = progressive_block.get_offenders_summary()
                assert len(summary) >= 1
                ips = [s["ip"] for s in summary]
                assert "10.0.0.1" in ips


class TestSiemIntegration:
    def test_siem_disabled_no_socket(self):
        from siem_integration import _get_socket
        sock = _get_socket()
        assert sock is None

    def test_siem_close_no_error(self):
        from siem_integration import siem_close
        siem_close()

    @patch("siem_integration.SIEM_SYSLOG_ENABLED", False)
    def test_send_event_disabled(self):
        from siem_integration import send_event
        send_event("test", "1.2.3.4", "test event")  # should not raise

    def test_build_cef(self):
        from siem_integration import _build_cef
        msg = _build_cef("block", "1.2.3.4", "Test block", severity=5)
        assert msg.startswith("CEF:0|SMAR-IA|IDS")
        assert "1.2.3.4" in msg
        assert "Test block" in msg

    def test_build_leef(self):
        from siem_integration import _build_leef
        msg = _build_leef("block", "1.2.3.4", "Test block")
        assert msg.startswith("LEEF:1.0|SMAR-IA|IDS")
        assert "1.2.3.4" in msg

    def test_build_json(self):
        from siem_integration import _build_json
        msg = _build_json("block", "1.2.3.4", "Test block")
        parsed = json.loads(msg)
        assert parsed["event"] == "block"
        assert parsed["src_ip"] == "1.2.3.4"

    def test_send_event_mocked(self):
        import siem_integration
        with patch.object(siem_integration, "SIEM_SYSLOG_ENABLED", True):
            with patch("siem_integration._get_socket") as mock_gs:
                mock_sock = MagicMock()
                mock_gs.return_value = mock_sock
                siem_integration.send_event("test", "1.2.3.4", "test event")
                mock_sock.sendto.assert_called_once()


class TestThreatIntel:
    def test_is_known_threat_empty(self):
        from threat_intel import is_known_threat, _known_bad_ips
        _known_bad_ips.clear()
        assert is_known_threat("1.2.3.4") is False

    def test_get_stats_empty(self):
        from threat_intel import get_threat_intel_stats, _known_bad_ips
        _known_bad_ips.clear()
        stats = get_threat_intel_stats()
        assert stats["enabled"] is True
        assert stats["cached_ips"] == 0

    def test_is_known_threat_match(self):
        from threat_intel import is_known_threat, _known_bad_ips
        _known_bad_ips.clear()
        _known_bad_ips.add("5.6.7.8")
        assert is_known_threat("5.6.7.8") is True
        assert is_known_threat("1.1.1.1") is False

    def test_is_known_threat_prefix(self):
        from threat_intel import is_known_threat, _known_bad_ips
        _known_bad_ips.clear()
        _known_bad_ips.add("10.0.0.0/8")
        assert is_known_threat("10.1.2.3") is True

    @patch("threat_intel.THREAT_INTEL_ENABLED", False)
    @pytest.mark.asyncio
    async def test_update_disabled(self):
        from threat_intel import update_threat_intel
        await update_threat_intel()


class TestHoneypot:
    def test_honeypot_disabled(self):
        assert HONEYPOT_ENABLED is False

    def test_honeypot_hits_empty(self):
        from honeypot import get_honeypot_hits, _honeypot_hits
        _honeypot_hits.clear()
        assert get_honeypot_hits() == []

    def test_honeypot_hits_since(self):
        from honeypot import get_honeypot_hits_since, _honeypot_hits
        _honeypot_hits.clear()
        _honeypot_hits.append({"ip": "1.2.3.4", "port": 22, "timestamp": 100})
        hits = get_honeypot_hits_since(50)
        assert len(hits) == 1
        hits = get_honeypot_hits_since(200)
        assert len(hits) == 0

    def test_clear_honeypot_hits(self):
        from honeypot import clear_honeypot_hits, _honeypot_hits
        _honeypot_hits.clear()
        _honeypot_hits.append({"ip": "1.2.3.4", "port": 22, "timestamp": 100})
        clear_honeypot_hits()
        assert _honeypot_hits == []

    @pytest.mark.asyncio
    async def test_start_stop_honeypots(self):
        from honeypot import start_honeypots, stop_honeypots
        await stop_honeypots()
        await start_honeypots()
        await stop_honeypots()


class TestFirewallRateLimiter:
    def test_record_event_under_threshold(self):
        from rate_limiter_firewall import record_event, _event_counts
        _event_counts.clear()
        result = record_event("1.2.3.4")
        assert result is False

    def test_get_rate_limit_status(self):
        from rate_limiter_firewall import get_rate_limit_status, _event_counts
        _event_counts.clear()
        _event_counts["10.0.0.1"] = [time.time()]
        status = get_rate_limit_status()
        assert "10.0.0.1" in status

    def test_get_ip_event_count(self):
        from rate_limiter_firewall import get_ip_event_count, _event_counts
        _event_counts.clear()
        _event_counts["10.0.0.2"] = [time.time()]
        count = get_ip_event_count("10.0.0.2")
        assert count == 1

    def test_set_threshold_callback(self):
        import rate_limiter_firewall
        def dummy(ip, count):
            pass
        rate_limiter_firewall.set_threshold_callback(dummy)
        assert rate_limiter_firewall._on_threshold_exceeded is dummy


class TestPrometheusRouter:
    def test_prometheus_metrics_format(self):
        from routers.prometheus_router import _format_metric
        output = _format_metric("test_metric", 42, {"label1": "val1"})
        assert "test_metric" in output
        assert "42" in output
        assert "label1" in output

    def test_prometheus_metrics_route(self):
        from main import app
        client = TestClient(app)
        response = client.get("/metrics")
        assert response.status_code == 200
        assert "text/plain" in response.headers["content-type"]
        assert "smar_ia_info" in response.text


class TestDatabasePostgres:
    def test_get_engines_sqlite_fallback(self):
        import database
        from database_postgres import get_engines
        security_engine, traffic_engine = get_engines()
        assert security_engine is not None
        assert traffic_engine is not None

    def test_pg_not_used_with_sqlite_url(self):
        from database_postgres import _create_pg_engine
        engine = _create_pg_engine("sqlite:///./test.db")
        assert engine is None

    @patch("database_postgres.SECURITY_DB_URL", "postgresql://user:pass@localhost:5432/test")
    def test_pg_connection_error_fallback(self):
        from database_postgres import _create_pg_engine
        engine = _create_pg_engine("postgresql://user:pass@localhost:5432/test")
        assert engine is None


class TestNftables:
    def test_nft_block_ip_invalid(self):
        from firewall_nftables import nft_block_ip
        result = nft_block_ip("invalid_ip")
        assert result == -1.0

    def test_nft_block_ip_dry_run(self):
        from firewall_nftables import nft_block_ip
        result = nft_block_ip("192.168.1.100")
        assert result == 0.0

    def test_nft_unblock_ip_dry_run(self):
        from firewall_nftables import nft_unblock_ip
        result = nft_unblock_ip("192.168.1.100")
        assert result is True

    def test_nft_unblock_ip_invalid(self):
        from firewall_nftables import nft_unblock_ip
        result = nft_unblock_ip("bad_ip")
        assert result is False

    def test_nft_is_blocked_dry_run(self):
        from firewall_nftables import nft_is_blocked
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.stdout = "192.168.1.200"
            mock_run.return_value.returncode = 0
            result = nft_is_blocked("192.168.1.200")
            assert result is True


class TestNewAPIEndpoints:
    def test_prometheus_metrics(self):
        from main import app
        client = TestClient(app)
        response = client.get("/metrics")
        assert response.status_code == 200
        assert "smar_ia_info" in response.text

    def test_honeypot_status(self):
        from main import app
        client = TestClient(app)
        response = client.get("/api/honeypot/status")
        assert response.status_code == 200
        data = response.json()
        assert "enabled" in data
        assert "hits_count" in data

    def test_threat_intel_status(self):
        from main import app
        client = TestClient(app)
        response = client.get("/api/threat-intel/status")
        assert response.status_code == 200
        data = response.json()
        assert data["enabled"] is True

    def test_threat_intel_check_requires_auth(self):
        from main import app
        client = TestClient(app)
        response = client.get("/api/threat-intel/check/1.2.3.4")
        assert response.status_code in (401, 403)

    def test_progressive_block_status(self):
        from main import app
        client = TestClient(app)
        response = client.get("/api/progressive-block/status")
        assert response.status_code == 200
        data = response.json()
        assert data["enabled"] is True

    def test_rate_limiter_status_requires_auth(self):
        from main import app
        client = TestClient(app)
        response = client.get("/api/rate-limiter/status")
        assert response.status_code in (401, 403)

    def test_health_still_works(self):
        from main import app
        client = TestClient(app)
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] in ("online", "degraded")

    def test_login_and_check_threat_intel(self):
        from main import app
        client = TestClient(app)
        login_resp = client.post("/api/auth/login", data={"username": "admin", "password": "admin123"})
        if login_resp.status_code != 200:
            pytest.skip("Login failed (DB may have different password)")
        token = login_resp.json().get("access_token")
        assert token

        headers = {"Authorization": f"Bearer {token}"}
        resp = client.get("/api/threat-intel/check/1.2.3.4", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["ip"] == "1.2.3.4"

    def test_login_and_check_rate_limiter(self):
        from main import app
        client = TestClient(app)
        login_resp = client.post("/api/auth/login", data={"username": "admin", "password": "admin123"})
        if login_resp.status_code != 200:
            pytest.skip("Login failed (DB may have different password)")
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        resp = client.get("/api/rate-limiter/check/1.2.3.4", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["ip"] == "1.2.3.4"
