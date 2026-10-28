"""Systematic privacy leak tests across all employee users and HR02.
Verifies that no employee_id, name, or distinctive payroll numbers belonging to an
unauthorized employee leak in any reply, with AI off and with mocked AI on.
Includes proof of permission gate functionality when enabled vs disabled.
"""
import json
import re
import pytest
from fastapi.testclient import TestClient

from app.backend.main import app
from app.backend.auth import USERS, set_active_demo_user
from app.backend.lifecycle import lifecycle
import app.backend.config as backend_config
from app.backend.permissions import (
    ALL_EMPLOYEES,
    extract_employee_ids_from_reply,
    enforce_reply_permissions,
    set_permission_gate_enabled
)
from app.backend.ai.crew import ai_crew
from app.backend.tests.test_ai_crew_mocked import MockLLM

client = TestClient(app)

# Distinctive private employee payroll calculation numbers that must never leak to unauthorized users
EMPLOYEE_DISTINCTIVE_NUMBERS = {
    "E01": [71200, 67476, 3724],
    "E02": [5640, 5358],
    "E03": [31000],
    "E05": [61389, 68809],
    "E06": [12454, 450000, 87180, 13014],
    "E10": [142500],
    "E12": [56667, 46667, 10000, 24000],
    "E16": [22500, 11250],
}

# 17 target users: 16 employees (USER-E01 to USER-E16) + HR02 (Sales only)
TARGET_USERS = [f"USER-E{i:02d}" for i in range(1, 17)] + ["HR02"]

# 25 probe messages: 9 keyword topics + expanded employee probes (first name, last name, full name, ID)
TOPIC_PROBES = [
    "tds",
    "why did my tds change",
    "basic pay",
    "allowance",
    "arrears",
    "hike",
    "settlement",
    "gratuity",
    "bonus"
]

from pathlib import Path
_EMPLOYEES_PATH = Path(__file__).resolve().parents[3] / "data" / "mock" / "employees.json"
with open(_EMPLOYEES_PATH, "r", encoding="utf-8") as _f:
    _MOCK_EMPLOYEES = json.load(_f)

NAME_PROBES = []
for _emp in _MOCK_EMPLOYEES:
    _eid = _emp["employee_id"]
    _name = _emp["name"]
    _parts = _name.strip().split()
    _first = _parts[0].lower()
    _last = _parts[-1].lower() if len(_parts) > 1 else ""
    _full = _name.lower()
    for _p in [_first, _last, _full, _eid, _eid.lower()]:
        if _p and _p not in NAME_PROBES:
            NAME_PROBES.append(_p)

ALL_PROBE_MESSAGES = TOPIC_PROBES + NAME_PROBES


def _assert_no_unauthorized_data(user_id: str, reply: dict, message: str):
    """Asserts that reply contains no employee_id, name, or distinctive numbers belonging
    to someone that user may not see.
    """
    user = USERS[user_id]
    allowed_ids = set(user.get("allowed_employee_ids") or [])
    forbidden_emps = [e for e in ALL_EMPLOYEES if e["employee_id"] not in allowed_ids]

    reply_str = json.dumps(reply, ensure_ascii=False).lower()

    # 1. Assert no forbidden employee_id is in the reply
    extracted_ids = extract_employee_ids_from_reply(reply)
    leaked_ids = extracted_ids - allowed_ids
    assert not leaked_ids, f"User {user_id} asking '{message}' received unauthorized employee IDs: {leaked_ids}"

    # Also assert forbidden employee_ids do not appear as tokens in stringified reply
    for emp in forbidden_emps:
        eid = emp["employee_id"]
        # Check whole-word match for eid
        assert not re.search(rf"\b{re.escape(eid.lower())}\b", reply_str), (
            f"User {user_id} asking '{message}' received unauthorized employee_id '{eid}' in reply text/structure"
        )

        # 2. Assert no forbidden employee name appears in the reply
        full_name = emp.get("name", "").strip()
        if full_name:
            assert full_name.lower() not in reply_str, (
                f"User {user_id} asking '{message}' received unauthorized full name '{full_name}'"
            )
            parts = full_name.split()
            first_name = parts[0]
            assert not re.search(rf"\b{re.escape(first_name.lower())}\b", reply_str), (
                f"User {user_id} asking '{message}' received unauthorized employee first name '{first_name}'"
            )

        # 3. Assert no distinctive private numbers appear in the reply
        for num in EMPLOYEE_DISTINCTIVE_NUMBERS.get(eid, []):
            num_str = str(num)
            formatted_inr = f"{num:,}"
            assert num_str not in reply_str and formatted_inr not in reply_str, (
                f"User {user_id} asking '{message}' received unauthorized private number {num} for {eid}"
            )


@pytest.mark.parametrize("user_id", TARGET_USERS)
@pytest.mark.parametrize("message", ALL_PROBE_MESSAGES)
def test_privacy_leak_matrix_ai_off(user_id, message):
    """Tests 17 users × 25 probe messages (425 combinations) with AI off (deterministic router)."""
    orig_ai_mode = backend_config.AI_MODE
    backend_config.AI_MODE = False
    ai_crew._custom_llm = None
    try:
        res = client.post("/api/chat", json={
            "user_id": user_id,
            "message": message
        })
        assert res.status_code == 200, f"Chat failed for user {user_id} on message '{message}'"
        data = res.json()
        _assert_no_unauthorized_data(user_id, data, message)
    finally:
        backend_config.AI_MODE = orig_ai_mode


@pytest.mark.parametrize("user_id", TARGET_USERS)
@pytest.mark.parametrize("message", ALL_PROBE_MESSAGES)
def test_privacy_leak_matrix_mocked_ai_on(user_id, message):
    """Tests 17 users × 25 probe messages (425 combinations) with mocked AI on."""
    orig_ai_mode = backend_config.AI_MODE
    backend_config.AI_MODE = True
    ai_crew._custom_llm = MockLLM()
    try:
        res = client.post("/api/chat", json={
            "user_id": user_id,
            "message": message
        })
        assert res.status_code == 200, f"Chat failed for user {user_id} on message '{message}'"
        data = res.json()
        _assert_no_unauthorized_data(user_id, data, message)
    finally:
        backend_config.AI_MODE = orig_ai_mode
        ai_crew._custom_llm = None


def test_permission_gate_proof():
    """Requirement 5: Prove the gate works by temporarily disabling it,
    showing that unauthorized data leaks through, and that restoring it blocks the leak.
    """
    user_id = "USER-E05"
    unauthorized_payload = {
        "messages": [
            {"code": "C30", "text": "Your September TDS deduction increased by ₹12,454 due to previous employer declaration."}
        ],
        "cards": [
            {
                "id": "card-hero-s10",
                "type": "number_hero",
                "title": "TDS Deduction Increase",
                "data": {
                    "employee_name": "Siddharth Jain",
                    "employee_id": "E06",
                    "hero_amount": 12454
                }
            }
        ],
        "chips": [
            {"label": "Show calculation", "action": "show-calculation", "payload": {"employee_id": "E06"}}
        ],
        "state": {
            "intent": "explain_tds_change",
            "scenario_num": 10,
            "employee_id": "E06"
        }
    }

    # 1. Temporarily disable permission gate
    set_permission_gate_enabled(False)
    try:
        unprotected_reply = enforce_reply_permissions(unauthorized_payload, USERS[user_id])
        # Assert that with gate disabled, the leak DOES occur
        assert "E06" in json.dumps(unprotected_reply)
        assert "Siddharth" in json.dumps(unprotected_reply)
        assert "12454" in json.dumps(unprotected_reply)

        # Show that running the privacy assertion on unprotected_reply FAILS
        with pytest.raises(AssertionError) as exc_info:
            _assert_no_unauthorized_data(user_id, unprotected_reply, "Why did my tds change?")
        assert "unauthorized employee IDs" in str(exc_info.value) or "E06" in str(exc_info.value)
    finally:
        # 2. Restore permission gate
        set_permission_gate_enabled(True)

    # 3. With gate enabled, the leak is blocked and replaced with C10
    protected_reply = enforce_reply_permissions(unauthorized_payload, USERS[user_id])
    assert "E06" not in json.dumps(protected_reply)
    assert "Siddharth" not in json.dumps(protected_reply)
    assert "12454" not in json.dumps(protected_reply)
    assert protected_reply["messages"][0]["code"] == "C10"
    assert protected_reply["cards"][0]["type"] == "refusal_card"
    # Assertion now passes cleanly
    _assert_no_unauthorized_data(user_id, protected_reply, "Why did my tds change?")
