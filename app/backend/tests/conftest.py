"""Pytest configuration and safety fixtures for HCM One backend tests.
Guarantees:
1. No test writes to data/runtime/ai_runs.jsonl (all logs redirected to tmp_path).
2. Safety net: Fails immediately if any test attempts to create a live LLM without a mock.
"""
import os
import pytest
from app.backend.ai.logger import set_ai_runs_log_path
from app.backend.ai.crew import PayrollAICrew
from app.backend.config import is_ai_enabled
from app.backend.rate_limiter import rate_limiter


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    """Reset chat rate limiter state between tests."""
    rate_limiter.reset()
    yield
    rate_limiter.reset()


@pytest.fixture(autouse=True)
def isolate_ai_runs_log(tmp_path, monkeypatch):
    """Ensure no test writes to production data/runtime/ai_runs.jsonl, including prompt injection."""
    temp_log = tmp_path / "test_ai_runs.jsonl"
    set_ai_runs_log_path(temp_log)
    monkeypatch.setenv("AI_RUNS_LOG_PATH", str(temp_log))
    yield temp_log
    set_ai_runs_log_path(None)


@pytest.fixture(autouse=True)
def live_ai_safety_net(monkeypatch):
    """Safety net: fails immediately if any test tries to initialize or call live AI."""
    orig_get_llm = PayrollAICrew._get_llm

    def safe_get_llm(self):
        if self._custom_llm is not None:
            return self._custom_llm
        if not is_ai_enabled():
            return None
        pytest.fail("Test tried to call live AI")

    monkeypatch.setattr(PayrollAICrew, "_get_llm", safe_get_llm)
    yield
