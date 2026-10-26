"""Masked audit logging for AI layer executions.
Writes structured JSONL records to data/runtime/ai_runs.jsonl.
Strict privacy: Never logs API keys, raw PAN, bank accounts, or unmasked sensitive PII.
"""
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Dict, Optional

from ..config import RUNTIME_DIR

import os

_OVERRIDE_LOG_FILE: Optional[Path] = None


def get_log_file() -> Path:
    if _OVERRIDE_LOG_FILE is not None:
        return _OVERRIDE_LOG_FILE
    env_path = os.environ.get("AI_RUNS_LOG_PATH")
    if env_path:
        return Path(env_path)
    return RUNTIME_DIR / "ai_runs.jsonl"


def set_ai_runs_log_path(path: Optional[Path]) -> None:
    global _OVERRIDE_LOG_FILE
    _OVERRIDE_LOG_FILE = path


LOG_FILE = get_log_file()


def mask_user_id(user_id: Optional[str]) -> str:
    """Masks user identifiers for audit log privacy."""
    if not user_id:
        return "ANON"
    if user_id.startswith("USER-"):
        return "USER-***"
    if len(user_id) > 2:
        return user_id[:2] + "**"
    return user_id + "**"


def log_ai_run(
    user_id: str,
    role: str,
    surface: str,
    intent: str,
    scenario_num: Optional[int],
    guards_result: Dict[str, Any],
    fallback_triggered: bool,
    fallback_reason: Optional[str],
    latency_ms: float,
    metrics: Optional[Dict[str, Any]] = None
) -> None:
    """Appends a masked execution record to data/runtime/ai_runs.jsonl."""
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_id_masked": mask_user_id(user_id),
        "role": role,
        "surface": surface,
        "intent": intent,
        "scenario_num": scenario_num,
        "guards": guards_result,
        "fallback_triggered": fallback_triggered,
        "fallback_reason": fallback_reason,
        "latency_ms": round(latency_ms, 2),
        "metrics": metrics or {}
    }

    try:
        target_file = get_log_file()
        target_file.parent.mkdir(parents=True, exist_ok=True)
        with open(target_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
    except Exception:
        # Non-blocking logging failure
        pass
