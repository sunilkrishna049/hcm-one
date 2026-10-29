"""Permission gate and cross-employee privacy enforcement.
Enforces that every chat reply (router path and AI path) contains only data
belonging to the signed-in user's allowed employee scope.
"""
import json
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Set

from .ai_messages import get_message
from .ai.logger import log_ai_run
from .config import MOCK_DIR

EMPLOYEES_PATH = MOCK_DIR / "employees.json"


def _load_mock_employees() -> List[dict]:
    if EMPLOYEES_PATH.exists():
        try:
            return json.loads(EMPLOYEES_PATH.read_text(encoding="utf-8-sig"))
        except Exception:
            return []
    return []


ALL_EMPLOYEES = _load_mock_employees()
ALL_EMPLOYEE_IDS = {e["employee_id"] for e in ALL_EMPLOYEES if e.get("employee_id")}

_PERMISSION_GATE_ENABLED = True


def set_permission_gate_enabled(enabled: bool) -> None:
    """Toggles permission gate for testing and verification."""
    global _PERMISSION_GATE_ENABLED
    _PERMISSION_GATE_ENABLED = enabled


def is_permission_gate_enabled() -> bool:
    return _PERMISSION_GATE_ENABLED


def get_mentioned_employee_ids(lower_msg: str) -> List[str]:
    """Detects mentions of employees from data/mock/employees.json using whole-word matching only.
    Ensures 'rao' does not match inside other words and 'khan' does not match 'khana'.
    Shared across router and AI crew.
    """
    mentioned = []
    for emp in ALL_EMPLOYEES:
        emp_id = emp.get("employee_id")
        full_name = emp.get("name", "")
        if not emp_id or not full_name:
            continue
        parts = full_name.strip().split()
        tokens = [emp_id, full_name]
        if parts:
            tokens.append(parts[0])  # first name
        if len(parts) > 1:
            tokens.append(parts[-1])  # last name
        for tok in tokens:
            pattern = rf"\b{re.escape(tok.lower())}\b"
            if re.search(pattern, lower_msg):
                if emp_id not in mentioned:
                    mentioned.append(emp_id)
                break
    return mentioned


def extract_employee_ids_from_reply(reply: Any) -> Set[str]:
    """Collects every employee_id in the reply: state, cards, panel, chip payloads."""
    collected = set()

    def _scan(obj: Any):
        if isinstance(obj, dict):
            for k, v in obj.items():
                k_lower = k.lower()
                if k_lower in ("employee_id", "employeeid", "target_employee_id", "eid") and isinstance(v, str):
                    cand = v.strip().upper()
                    if cand in ALL_EMPLOYEE_IDS:
                        collected.add(cand)
                elif isinstance(v, str):
                    matches = re.findall(r"\bE(0[1-9]|1[0-6])\b", v, flags=re.IGNORECASE)
                    for m in matches:
                        collected.add(f"E{m.upper()}")
                _scan(v)
        elif isinstance(obj, list):
            for item in obj:
                _scan(item)

    _scan(reply)
    return collected


def build_c10_permission_reply(user: dict, reason: str = "Access boundary enforced.") -> dict:
    """Standard C10 permission refusal response."""
    role = user.get("role", "Employee")
    surface = "CHAT-HR" if role == "HR Admin" else "CHAT-EMP"
    emp_id = user.get("employee_id")
    return {
        "messages": [
            {"code": "C10", "text": get_message("C10")}
        ],
        "cards": [
            {
                "id": "card-refusal",
                "type": "refusal_card",
                "title": "Permission Denied",
                "certainty": "Permission denied",
                "data": {
                    "message": get_message("C10"),
                    "reason": reason
                }
            }
        ],
        "chips": [
            {"label": "Ask about my payroll", "action": "explain-salary", "payload": {}},
            {"label": "What is LOP?", "action": "faq-lop", "payload": {}},
            {"label": "What is PF?", "action": "faq-pf", "payload": {}}
        ],
        "state": {
            "intent": "other_employee_data",
            "role": role,
            "surface": surface,
            "scenario_num": None,
            "employee_id": emp_id,
            "certainty": None,
            "panel": None
        }
    }


def enforce_reply_permissions(reply: dict, user: dict) -> dict:
    """Permission gate run last on the server:
    Collects every employee_id in the reply (state, cards, panel, chip payloads).
    If any is not in the signed-in user's allowed list, do not send it.
    Sends C10 permission reply instead, and logs masked event to AI run log.
    Does not depend on keywords or names.
    """
    if not is_permission_gate_enabled():
        return reply

    if not isinstance(reply, dict):
        return reply

    allowed_ids = set(user.get("allowed_employee_ids") or [])
    contained_ids = extract_employee_ids_from_reply(reply)

    unauthorized_ids = contained_ids - allowed_ids
    if unauthorized_ids:
        role = user.get("role", "Employee")
        surface = "CHAT-HR" if role == "HR Admin" else "CHAT-EMP"
        user_id = user.get("user_id", "UNKNOWN")

        # Masked audit log entry
        log_ai_run(
            user_id=user_id,
            role=role,
            surface=surface,
            intent="other_employee_data",
            scenario_num=None,
            guards_result={"permission_gate": "FAIL"},
            fallback_triggered=True,
            fallback_reason="Permission boundary enforced: reply contained unauthorized employee data",
            latency_ms=0.0
        )
        return build_c10_permission_reply(user)

    return reply
