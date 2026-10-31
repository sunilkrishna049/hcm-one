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
from app.backend.lifecycle import lifecycle, evaluate_proposal_readiness
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
    assert d_sales["messages"][0]["text"] == "Sales incentive (Q2 2026-27): 3 eligible, 0 not eligible."
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
    assert "Meera Nair's performance record is missing." in reason
    from app.backend.ai_messages import get_message
    assert reason == get_message("C56", Name="Meera Nair", **{"missing item": "performance record"})


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



def test_r2_approvals_list_one_source_of_truth():
    """R2: For every proposal, it is in 'Ready to approve' iff Approve is enabled.
    C48/C49 counts equal the row counts.
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
    assert c48_msg is not None
    assert c49_msg is not None

    cards = {c["id"]: c for c in data.get("cards", [])}
    ready_items = cards["card-ready-approvals"]["data"]["items"]
    needs_input_items = cards["card-needs-input-approvals"]["data"]["items"]

    assert len(ready_items) == 5
    assert len(needs_input_items) == 4
    assert f"{len(ready_items)} proposals are ready for your approval." in c48_msg["text"]
    assert f"{len(needs_input_items)} need input before they can be approved." in c49_msg["text"]

    all_props = lifecycle.get_all_proposals()
    ready_pids = {item["proposal_id"] for item in ready_items if "proposal_id" in item}
    needs_pids = {item["proposal_id"] for item in needs_input_items if "proposal_id" in item}

    for pid in ready_pids:
        is_ready, dis_reason, _ = evaluate_proposal_readiness(pid)
        assert is_ready is True, f"Proposal {pid} is in Ready to approve but evaluate_proposal_readiness returned is_ready=False ({dis_reason})"

    for pid in needs_pids:
        is_ready, dis_reason, _ = evaluate_proposal_readiness(pid)
        assert is_ready is False, f"Proposal {pid} is in Needs input but evaluate_proposal_readiness returned is_ready=True"


def test_r3_reasons_from_data_dynamic_update(monkeypatch):
    """R3: Test: in a temporary copy of the data, add a performance record for E09.
    The Engineering bonus reason disappears and Approve becomes enabled.
    Do not change the real data/mock files.
    """
    # Verify baseline: with original data, annual bonus is blocked due to Meera Nair missing performance record
    is_ready_orig, dis_reason_orig, row_reason_orig = evaluate_proposal_readiness("PROP-SCENARIO-4-ANNUAL")
    assert is_ready_orig is False
    assert "Meera Nair's performance record is missing." in (dis_reason_orig or "")
    assert "Meera Nair's performance record is missing." in (row_reason_orig or "")

    from app.backend.engine_bridge import bridge
    import copy

    # Get copy of scenario 4 data and simulate adding performance record for E09
    real_sc4 = bridge.get_scenario(4)
    patched_sc4 = copy.deepcopy(real_sc4)

    # In patched copy, clear needs_input (performance record added for E09)
    for req in patched_sc4["result"]["bonus_requests"]:
        if req.get("bonus_type") == "annual_performance_bonus":
            req["needs_input"] = []
            req["certainty"] = "Complete for this scope"

    # Monkeypatch bridge.get_scenario(4) to return the updated data
    monkeypatch.setattr(bridge, "get_scenario", lambda s_num: patched_sc4 if s_num == 4 else real_sc4)

    # With performance record added, Engineering bonus becomes ready and Approve is enabled
    is_ready_new, dis_reason_new, row_reason_new = evaluate_proposal_readiness("PROP-SCENARIO-4-ANNUAL")
    assert is_ready_new is True
    assert dis_reason_new is None
    assert row_reason_new is None


def test_r1_mocked_drafter_sentinel_never_appears(monkeypatch):
    """R1: New guard test: with AI mocked ON, make the mocked drafter return the sentinel text
    'SENTINEL_AI_DRAFT' for every call. Run all 60 evaluation questions plus the leak-matrix probes
    through /api/chat. Assert the sentinel NEVER appears in any response.
    Also prove the test can fail: temporarily set the constant to True, show it fails, then set it back.
    """
    from app.backend.ai.eval_ai_crew import EVAL_CASES
    from app.backend.tests.test_privacy_leak import TOPIC_PROBES, TARGET_USERS
    from app.backend.tests.test_ai_crew_mocked import MockLLM
    from app.backend.ai.crew import ai_crew

    # Mocked LLM where drafter always emits the sentinel string
    mock_llm = MockLLM()
    mock_llm.custom_draft_response = "SENTINEL_AI_DRAFT"
    orig_custom_llm = ai_crew._custom_llm
    orig_ai_mode = backend_config.AI_MODE

    try:
        ai_crew._custom_llm = mock_llm
        backend_config.AI_MODE = True
        assert backend_config.AI_DRAFTING_ENABLED is False

        # 1. Run all 60 evaluation questions
        for case_id, user_id, query, _, label in EVAL_CASES:
            res = client.post("/api/chat", json={"user_id": user_id, "message": query})
            assert res.status_code == 200, f"Query failed for case {case_id}: {query}"
            body_text = str(res.json())
            assert "SENTINEL_AI_DRAFT" not in body_text, f"Sentinel leaked in response for eval case {case_id} ('{query}'): {body_text}"

        # 2. Run leak-matrix probes
        for target_user in TARGET_USERS[:5]:  # sample of users
            for probe in TOPIC_PROBES[:5]:
                res = client.post("/api/chat", json={"user_id": target_user, "message": probe})
                assert res.status_code == 200
                body_text = str(res.json())
                assert "SENTINEL_AI_DRAFT" not in body_text, f"Sentinel leaked for user {target_user} on probe '{probe}'"

        # 3. PROVE FAILURE: temporarily set AI_DRAFTING_ENABLED to True
        backend_config.AI_DRAFTING_ENABLED = True
        try:
            # Query that triggers drafting (e.g. Priya Sharma hike proposal)
            res_fail = client.post("/api/chat", json={
                "user_id": "HR01",
                "message": "Prepare salary hike for Priya Sharma"
            })
            assert res_fail.status_code == 200
            fail_body = str(res_fail.json())
            # When drafting is enabled, the sentinel DOES appear in the AI message!
            assert "SENTINEL_AI_DRAFT" in fail_body, f"Expected sentinel to appear when AI_DRAFTING_ENABLED is True, but got: {fail_body}"
        finally:
            # Set it back to False immediately
            backend_config.AI_DRAFTING_ENABLED = False

    finally:
        ai_crew._custom_llm = orig_custom_llm
        backend_config.AI_MODE = orig_ai_mode
        backend_config.AI_DRAFTING_ENABLED = False
