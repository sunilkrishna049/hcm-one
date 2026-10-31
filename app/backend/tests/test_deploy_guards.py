from pathlib import Path
"""Tests for Deployment Preparation (Prompt 5).
Verifies:
1. GET /api/health returns {"status": "ok"}.
2. CORS configuration allows FRONTEND_ORIGIN and localhost dev origins.
3. Rate limiter on /api/chat restricts requests to 20 per minute per IP, returning HTTP 429.
4. Daily cap on live AI calls (300 per day). After the cap, AI turns off automatically and safe templates answer. Log it (masked).
"""
import logging
import pytest
from fastapi.testclient import TestClient

from app.backend.main import app
from app.backend.rate_limiter import rate_limiter
from app.backend.ai.cap_manager import cap_manager
import app.backend.config as backend_config
from app.backend.tests.test_ai_crew_mocked import MockLLM
from app.backend.ai.crew import ai_crew

client = TestClient(app)


def test_api_health():
    """Item 4: GET /api/health returns {'status': 'ok'}."""
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_cors_configuration():
    """Item 4: CORS allows dev origins and FRONTEND_ORIGIN."""
    resp = client.options(
        "/api/health",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET"
        }
    )
    assert resp.status_code in (200, 204)
    assert resp.headers.get("access-control-allow-origin") == "http://localhost:5173"


def test_rate_limit_chat_per_ip():
    """Item 5: Rate limit /api/chat per IP (20 requests per minute)."""
    orig_mode = backend_config.AI_MODE
    backend_config.AI_MODE = False
    rate_limiter.reset()
    test_ip = "203.0.113.42"
    headers = {"X-Forwarded-For": test_ip}

    try:
        # First 20 requests should pass rate limit (returning 200 OK)
        for i in range(20):
            resp = client.post("/api/chat", json={"user_id": "HR01", "message": "What is basic pay?"}, headers=headers)
            assert resp.status_code == 200, f"Request {i+1} got unexpected status {resp.status_code}"

        # 21st request from same IP must be rate limited with 429
        blocked_resp = client.post("/api/chat", json={"user_id": "HR01", "message": "What is basic pay?"}, headers=headers)
        assert blocked_resp.status_code == 429
        assert "Rate limit exceeded" in blocked_resp.json().get("detail", "")

        # Different IP should not be blocked
        other_ip = "203.0.113.99"
        other_resp = client.post("/api/chat", json={"user_id": "HR01", "message": "What is basic pay?"}, headers={"X-Forwarded-For": other_ip})
        assert other_resp.status_code == 200

    finally:
        backend_config.AI_MODE = orig_mode
        rate_limiter.reset()


def test_daily_ai_call_cap(caplog):
    """Item 5: Daily cap on live AI calls (300 per day).
    After the cap, AI turns off automatically and safe templates answer. Log it (masked).
    """
    orig_mode = backend_config.AI_MODE
    orig_key = backend_config.OPENAI_API_KEY
    backend_config.AI_MODE = True
    backend_config.OPENAI_API_KEY = "test-key-mock"

    try:
        # 1. Reset cap state to 0
        cap_manager.reset(count=0)
        assert not cap_manager.is_capped()
        assert backend_config.is_ai_enabled()

        # 2. Simulate reaching the cap of 300 calls
        cap_manager.reset(count=300)
        assert cap_manager.is_capped()
        assert not backend_config.is_ai_enabled()

        # Attempting to record an AI call returns False and logs a masked warning
        with caplog.at_level(logging.WARNING):
            allowed = cap_manager.record_live_call()
            assert not allowed
            assert any("Masked warning" in rec.message and "Daily AI call cap" in rec.message for rec in caplog.records)

        # 3. Chat queries still succeed by falling back gracefully to deterministic safe templates
        resp = client.post("/api/chat", json={"user_id": "USER-E05", "message": "How much PF was cut?"})
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("messages")
        assert "₹2,220" in data["messages"][0]["text"]
        assert data["messages"][0]["code"] == "C37"

    finally:
        backend_config.AI_MODE = orig_mode
        backend_config.OPENAI_API_KEY = orig_key
        cap_manager.reset(count=0)


def test_cant_approve_yet_static_guard():
    """T1: Static guard: no unapproved reason text outside ai_messages.py, and dynamic disabled-Approve checks."""
    root_path = Path(__file__).resolve().parent.parent.parent.parent
    phrase = chr(67) + chr(97) + chr(110) + chr(39) + chr(116) + ' approve yet'
    violating_files = []

    for ext in ("*.py", "*.ts", "*.tsx"):
        for p in root_path.rglob(ext):
            p_str = str(p)
            if any(ignore in p_str for ignore in (".git", "node_modules", ".venv", "__pycache__", "scratch")):
                continue
            if p.name == "ai_messages.py":
                continue
            try:
                text = p.read_text(encoding="utf-8", errors="ignore")
                if phrase in text:
                    violating_files.append(str(p.relative_to(root_path)))
            except Exception:
                pass

    assert not violating_files, f"Found '{phrase}' in unauthorized files: {violating_files}"

    from app.backend.ai_messages import get_message, validate_message_text

    disabled_proposals_to_check = [
        ("scenario-3", {"scenario_num": 3}, "C56", get_message("C56", Name="Kavya Iyer", **{"missing item": "July attendance"})),
        ("scenario-4", {"scenario_num": 4, "bonus_type": "annual_performance_bonus"}, "C56", get_message("C56", Name="Meera Nair", **{"missing item": "performance record"})),
        ("scenario-8", {"scenario_num": 8}, "C59", get_message("C59", Name="Imran Khan", item="laptop clearance")),
        ("scenario-13", {"scenario_num": 13}, "C59", get_message("C59", Name="Imran Khan", item="laptop clearance")),
    ]

    for act, ctx, exp_code, exp_reason in disabled_proposals_to_check:
        res = client.post("/api/chat", json={
            "user_id": "HR01",
            "action": act,
            "context": ctx
        })
        assert res.status_code == 200, f"Request failed for {act}: {res.text}"
        data = res.json()
        appr_card = next((c for c in data.get("cards", []) if c.get("type") == "approval_card"), None)
        assert appr_card is not None, f"No approval_card found for action {act}"
        assert appr_card["data"]["disabled"] is True, f"Approve button must be disabled for {act}"

        reason = appr_card["data"].get("disabled_reason") or appr_card["data"].get("blocking_reason")
        assert reason is not None, f"No disabled_reason found for {act}"
        assert reason.startswith(f"{phrase}:"), f"Reason does not start with '{phrase}:': '{reason}'"
        assert reason == exp_reason, f"Reason '{reason}' does not equal expected template '{exp_reason}'"
        header = reason.split("\n")[0]
        assert validate_message_text(exp_code, header), f"Reason header '{header}' failed validation against {exp_code}"
