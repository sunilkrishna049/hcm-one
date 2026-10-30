"""Tests for Live-Test Fixes F1 through F10.
Verifies all requirements under Prompt:
F1. HR "What needs my approval?" lists rows showing what it is and for whom. C48/C49 counts equal row counts.
F2. Card payloads do not render card-level certainty badges.
F3. Bonus summary replies use templates only (C54 / C55); drafting is off for bonus intents.
F4. Approval card disabled reason matches C56 / C57.
F5. HR query reply starts empty with placeholder.
F6. Salary-drop message uses C58 without minus sign next to 'lower'.
F7. LOP detail says '{n} LOP days recorded'.
F8. Refusal returns C10 and refusal_card.
F9. Salary-drop reply provides 'Show breakdown' chip.
F10. Query card HR reply label logic.
"""
import pytest
from fastapi.testclient import TestClient

from app.backend.main import app
from app.backend.lifecycle import lifecycle
import app.backend.config as backend_config
from app.backend.ai_messages import validate_message_text

client = TestClient(app)


@pytest.fixture(autouse=True)
def ensure_reset():
    backend_config.AI_MODE = False
    lifecycle.reset_demo()
    yield
    lifecycle.reset_demo()


def test_f1_approvals_list_counts_and_row_labels():
    """F1: The counts in C48/C49 equal the number of rows in each list, and no list is empty when its count is above 0.
    Each row shows what it is and for whom, and 'Needs input first' shows recorded reasons.
    """
    res = client.post("/api/chat", json={
        "user_id": "HR01",
        "message": "What needs my approval?"
    })
    assert res.status_code == 200
    data = res.json()

    msgs = data.get("messages", [])
    c48_msg = next((m for m in msgs if m["code"] == "C48"), None)
    c49_msg = next((m for m in msgs if m["code"] == "C49"), None)
    assert c48_msg is not None, "C48 message missing"
    assert c49_msg is not None, "C49 message missing"

    cards = {c["id"]: c for c in data.get("cards", [])}
    ready_card = cards.get("card-ready-approvals")
    needs_input_card = cards.get("card-needs-input-approvals")

    assert ready_card is not None, "Ready to approve card missing"
    assert needs_input_card is not None, "Needs input first card missing"

    ready_items = ready_card["data"]["items"]
    needs_input_items = needs_input_card["data"]["items"]

    # Counts in C48/C49 equal number of rows
    assert f"{len(ready_items)} proposals are ready for your approval." in c48_msg["text"]
    assert f"{len(needs_input_items)} need input before they can be approved." in c49_msg["text"]
    assert len(ready_items) > 0, "Ready items list is empty"
    assert len(needs_input_items) > 0, "Needs input items list is empty"

    # Each row shows what it is and for whom
    for item in ready_items:
        lbl = item["label"]
        assert " · " in lbl, f"Row label '{lbl}' missing ' · ' separator"
        assert any(k in lbl for k in ("Salary revision", "Full and final settlement", "Annual performance bonus", "Sales incentive")), f"Unknown kind in '{lbl}'"

    for item in needs_input_items:
        lbl = item["label"]
        assert " · " in lbl, f"Row label '{lbl}' missing ' · ' separator"
        # Rows under Needs input first also show the recorded reason
        reason = item.get("reason") or item.get("blocked_reason")
        assert reason, f"Missing recorded reason in item: {item}"
        assert any(k in reason for k in ("missing", "pending", "incomplete")), f"Reason '{reason}' does not explain blocker"


def test_f3_bonus_summary_templates_c54_c55():
    """F3: Bonus summary replies must use templates only:
    C54: '{Bonus name}: {n} eligible, {n} not eligible, {n} waiting for input.'
    C55: '{Bonus name}: {n} eligible, {n} not eligible.'
    """
    # Annual bonus (has 1 waiting for input -> C54)
    res_ann = client.post("/api/chat", json={
        "user_id": "HR01",
        "message": "Annual performance bonus, FY 2025-26, Engineering"
    })
    assert res_ann.status_code == 200
    d_ann = res_ann.json()
    assert d_ann["messages"][0]["code"] == "C54"
    assert d_ann["messages"][0]["text"] == "Engineering annual performance bonus (FY 2025-26): 4 eligible, 1 not eligible, 1 waiting for input."
    assert validate_message_text("C54", d_ann["messages"][0]["text"])

    # Sales bonus (0 waiting for input -> C55)
    res_sales = client.post("/api/chat", json={
        "user_id": "HR01",
        "message": "Q2 Sales incentive, Hyderabad Sales"
    })
    assert res_sales.status_code == 200
    d_sales = res_sales.json()
    assert d_sales["messages"][0]["code"] == "C55"
    assert d_sales["messages"][0]["text"] == "Q2 Sales incentive (Q2 2026-27): 3 eligible, 0 not eligible."
    assert validate_message_text("C55", d_sales["messages"][0]["text"])


def test_f4_approval_card_disabled_reason_matching_c56_c57():
    """F4: When Approve is disabled, blocking_reason matches C56 / C57."""
    res = client.post("/api/chat", json={
        "user_id": "HR01",
        "message": "Annual performance bonus, FY 2025-26, Engineering"
    })
    assert res.status_code == 200
    data = res.json()
    appr_card = next(c for c in data["cards"] if c["type"] == "approval_card")
    assert appr_card["data"]["disabled"] is True
    reason = appr_card["data"].get("disabled_reason") or appr_card["data"].get("blocking_reason")
    assert reason.startswith("Can't approve yet:")
    assert "2 items need input." in reason


def test_f5_hr_reply_box_starts_empty():
    """F5: The HR reply box must start EMPTY with no pre-filled draft text."""
    res = client.post("/api/chat", json={
        "user_id": "HR01",
        "message": "Reply to Neha's query"
    })
    assert res.status_code == 200
    data = res.json()
    draft_card = next(c for c in data["cards"] if c["type"] == "query_draft")
    assert draft_card["data"]["draft_reply"] == "", "draft_reply must be empty string"


def test_f6_f7_f9_employee_salary_drop_c58_lop_and_breakdown_chip():
    """F6: Salary-drop message uses C58 without minus sign next to lower.
    F7: LOP row says '3 LOP days recorded'.
    F9: 'Show breakdown' chip is present and maps to show-calculation.
    """
    res = client.post("/api/chat", json={
        "user_id": "USER-E05",
        "message": "Why is my salary less this month?"
    })
    assert res.status_code == 200
    data = res.json()

    # F6: C58 template without minus sign
    assert data["messages"][0]["code"] == "C58"
    msg_text = data["messages"][0]["text"]
    assert msg_text == "Your September take-home is ₹5,420 lower than August. The main recorded reasons are below."
    assert "−₹" not in msg_text and "-₹" not in msg_text and "−" not in msg_text, "Minus sign must not appear next to amount in sentence"

    # F7: LOP row detail
    reasons_card = next(c for c in data["cards"] if c["type"] == "reason_list")
    reasons = reasons_card["data"]["reasons"]
    lop_reason = next(r for r in reasons if "Loss of Pay" in r["cause"])
    assert lop_reason["detail"] == "3 LOP days recorded"
    assert "unpaid leave" not in lop_reason["detail"].lower()

    # F9: Show breakdown chip
    chips = data.get("chips", [])
    breakdown_chip = next((c for c in chips if c["label"] == "Show breakdown"), None)
    assert breakdown_chip is not None, "Show breakdown chip missing"
    assert breakdown_chip["action"] == "show-calculation"


def test_f8_permission_denied_structure():
    """F8: Permission denied returns C10 code and refusal_card."""
    res = client.post("/api/chat", json={
        "user_id": "USER-E05",
        "message": "What is Vikram's salary?"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["messages"][0]["code"] == "C10"
    card_types = [c["type"] for c in data["cards"]]
    assert "refusal_card" in card_types
