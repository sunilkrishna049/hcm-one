"""Live-path smoke test executing the exact 8-step live sequence through /api/chat
with AI MOCKED ON in order in one single session.
Verifies all 8 user interactions succeed deterministically without generic calculation fallbacks.
"""
import json
import pytest
from fastapi.testclient import TestClient

from app.backend.main import app
from app.backend.lifecycle import lifecycle
from app.backend.ai.crew import ai_crew, ClassifierOutput
from app.backend.ai_messages import AI_MESSAGES

CANT_APPROVE_PREFIX = AI_MESSAGES["C56"].split(":")[0] + ":"
import app.backend.config as backend_config

client = TestClient(app)

GENERIC_ERROR = "The payroll calculation did not produce a usable result for this operation. I cannot give a complete amount for it."


class MockSmokeLLM:
    """Mock LLM classifier simulating the live classifier agent without external API calls."""
    def classify(self, message: str, role: str, context: dict) -> dict:
        lower = message.lower()
        if "approval" in lower:
            return {
                "intent": "approvals_list",
                "scenario_num": None,
                "entities": {},
                "confidence": 0.98,
                "is_prompt_injection": False,
                "clarification_needed": False
            }
        if "bonus for engineering" in lower:
            return {
                "intent": "bonus_proposal",
                "scenario_num": 4,
                "entities": {},
                "confidence": 0.98,
                "is_prompt_injection": False,
                "clarification_needed": True
            }
        if "show neha's query" in lower or "neha" in lower and "query" in lower:
            return {
                "intent": "hr_query_review",
                "scenario_num": None,
                "entities": {"employee_name": "Neha Gupta", "employee_id": "E05"},
                "confidence": 0.98,
                "is_prompt_injection": False,
                "clarification_needed": False
            }
        if "reply on my query" in lower or "reply to my query" in lower or "status" in lower and "query" in lower:
            return {
                "intent": "query_status",
                "scenario_num": None,
                "entities": {},
                "confidence": 0.98,
                "is_prompt_injection": False,
                "clarification_needed": False
            }
        if "why is my salary less" in lower or "salary less" in lower:
            return {
                "intent": "explain_salary",
                "scenario_num": 9,
                "entities": {"month": "September 2026"},
                "confidence": 0.98,
                "is_prompt_injection": False,
                "clarification_needed": False
            }
        if "priya" in lower and "salary" in lower:
            return {
                "intent": "other_employee_data",
                "scenario_num": 12,
                "entities": {"employee_name": "Priya Sharma", "access_denied": "true"},
                "confidence": 0.99,
                "is_prompt_injection": False,
                "clarification_needed": False
            }
        if "which regime should i choose" in lower or "choose" in lower and "regime" in lower:
            return {
                "intent": "out_of_scope",
                "scenario_num": None,
                "entities": {},
                "confidence": 0.98,
                "is_prompt_injection": False,
                "clarification_needed": False
            }
        if "imran" in lower and "settlement" in lower:
            return {
                "intent": "settlement_proposal",
                "scenario_num": 8,
                "entities": {"employee_name": "Imran Khan", "employee_id": "E12"},
                "confidence": 0.98,
                "is_prompt_injection": False,
                "clarification_needed": False
            }
        if "prepare a bonus proposal" in lower or lower.strip() == "bonus":
            return {
                "intent": "clarifying_question",
                "scenario_num": None,
                "entities": {},
                "confidence": 0.98,
                "is_prompt_injection": False,
                "clarification_needed": True
            }
        if "why was there lop" in lower or "lop days" in lower or "loss of pay" in lower:
            return {
                "intent": "lop_days",
                "scenario_num": None,
                "entities": {"month": "2026-09"},
                "confidence": 0.98,
                "is_prompt_injection": False,
                "clarification_needed": False
            }
        if any(phr in lower for phr in ["who took this action", "who closed", "who resolved", "who replied", "who actioned", "who handled"]):
            return {
                "intent": "query_status",
                "scenario_num": None,
                "entities": {},
                "confidence": 0.98,
                "is_prompt_injection": False,
                "clarification_needed": False
            }
        return {
            "intent": "unknown",
            "scenario_num": None,
            "entities": {},
            "confidence": 0.5,
            "is_prompt_injection": False,
            "clarification_needed": False
        }

    def draft(self, message: str, facts_list: dict, scenario_num: int, role: str) -> str:
        return ""


@pytest.fixture(autouse=True)
def setup_smoke_session():
    lifecycle.reset_demo()
    orig_custom_llm = ai_crew._custom_llm
    orig_ai_mode = backend_config.AI_MODE
    backend_config.AI_MODE = True
    ai_crew._custom_llm = MockSmokeLLM()
    yield
    ai_crew._custom_llm = orig_custom_llm
    backend_config.AI_MODE = orig_ai_mode


def test_live_path_smoke_sequence_in_order():
    """Runs the 8 exact user messages through /api/chat with AI MOCKED ON in order in one session."""

    # -------------------------------------------------------------
    # Step 1: HR01: "What needs my approval?" -> C48+C49 with rows
    # -------------------------------------------------------------
    r1 = client.post(
        "/api/chat",
        json={"user_id": "HR01", "message": "What needs my approval?"},
        headers={"X-User-Id": "HR01"}
    )
    assert r1.status_code == 200
    data1 = r1.json()
    dump1 = json.dumps(data1)
    assert GENERIC_ERROR not in dump1

    codes1 = [m.get("code") for m in data1.get("messages", [])]
    assert "C48" in codes1, f"Expected C48 in messages, got {codes1}"
    assert "C49" in codes1, f"Expected C49 in messages, got {codes1}"

    cards1 = {c.get("id"): c for c in data1.get("cards", [])}
    assert "card-ready-approvals" in cards1
    assert "card-needs-input-approvals" in cards1

    ready_comps = cards1["card-ready-approvals"]["data"].get("components", [])
    needs_input_comps = cards1["card-needs-input-approvals"]["data"].get("components", [])
    assert len(ready_comps) >= 5, f"Expected at least 5 ready proposals, got {len(ready_comps)}"
    assert len(needs_input_comps) >= 4, f"Expected at least 4 needs-input proposals, got {len(needs_input_comps)}"

    # Ready rows show title only (no blocked note)
    for rc in ready_comps:
        assert rc.get("name")
        assert not rc.get("note")

    # Needs input rows show title + waiting reason
    for nc in needs_input_comps:
        assert nc.get("name")
        assert CANT_APPROVE_PREFIX in (nc.get("note") or "")

    # -------------------------------------------------------------
    # Step 2: HR01: "Bonus for Engineering" -> picker; then choose Annual -> C54, one badge "Incomplete", approval disabled with C56 reason
    # -------------------------------------------------------------
    r2_picker = client.post(
        "/api/chat",
        json={"user_id": "HR01", "message": "Bonus for Engineering"},
        headers={"X-User-Id": "HR01"}
    )
    assert r2_picker.status_code == 200
    data2_picker = r2_picker.json()
    assert GENERIC_ERROR not in json.dumps(data2_picker)
    assert data2_picker.get("state", {}).get("intent") in ("clarifying_question", "bonus_proposal")

    # Choose Annual
    r2_annual = client.post(
        "/api/chat",
        json={
            "user_id": "HR01",
            "action": "apply-selection",
            "context": {"choice": "Annual performance bonus · Engineering · FY 2025-26"}
        },
        headers={"X-User-Id": "HR01"}
    )
    assert r2_annual.status_code == 200
    data2_annual = r2_annual.json()
    dump2 = json.dumps(data2_annual)
    assert GENERIC_ERROR not in dump2

    codes2 = [m.get("code") for m in data2_annual.get("messages", [])]
    assert "C54" in codes2, f"Expected C54 in {codes2}"

    # Verify one badge "Incomplete" (Meera Nair / E09)
    bonus_card = next((c for c in data2_annual.get("cards", []) if c.get("type") == "proposal_summary"), None)
    assert bonus_card is not None
    assert bonus_card.get("certainty") == "Incomplete" or bonus_card["data"].get("needs_input_count") == 1

    # Verify approval card is disabled with C56 reason
    approval_card = next((c for c in data2_annual.get("cards", []) if c.get("type") == "approval_card"), None)
    assert approval_card is not None
    assert approval_card["data"].get("disabled") is True
    reason_s4 = approval_card["data"].get("blocking_reason") or approval_card["data"].get("disabled_label") or ""
    assert CANT_APPROVE_PREFIX in reason_s4
    assert "performance record is missing" in reason_s4

    # -------------------------------------------------------------
    # Step 3: HR01: "Show Neha's query" -> HR query card plus way to reply; then send a reply -> HR_QUERY_REPLY
    # -------------------------------------------------------------
    r3_show = client.post(
        "/api/chat",
        json={"user_id": "HR01", "message": "Show Neha's query"},
        headers={"X-User-Id": "HR01"}
    )
    assert r3_show.status_code == 200
    data3_show = r3_show.json()
    dump3_show = json.dumps(data3_show)
    assert GENERIC_ERROR not in dump3_show

    # Query card plus way to reply (query_draft card and/or Reply chip)
    card_types3 = [c.get("type") for c in data3_show.get("cards", [])]
    chip_labels3 = [ch.get("label") for ch in data3_show.get("chips", [])]
    assert "query_status" in card_types3
    assert "query_draft" in card_types3 or any("Reply to Neha" in lbl for lbl in chip_labels3)

    # Now HR sends a reply
    reply_text = "Attendance verified against access gate logs. 3 LOP days stand as recorded."
    r3_reply = client.post(
        "/api/chat",
        json={
            "user_id": "HR01",
            "action": "confirm-reply-query",
            "context": {"query_id": "QUERY-E05-SEPTEMBER", "reply_text": reply_text}
        },
        headers={"X-User-Id": "HR01"}
    )
    assert r3_reply.status_code == 200
    data3_reply = r3_reply.json()
    assert GENERIC_ERROR not in json.dumps(data3_reply)
    codes3 = [m.get("code") for m in data3_reply.get("messages", [])]
    assert "HR_QUERY_REPLY" in codes3

    # -------------------------------------------------------------
    # Step 4: USER-E05: "Do I have a reply on my query?" -> C44 with reply text
    # -------------------------------------------------------------
    r4 = client.post(
        "/api/chat",
        json={"user_id": "USER-E05", "message": "Do I have a reply on my query?"},
        headers={"X-User-Id": "USER-E05"}
    )
    assert r4.status_code == 200
    data4 = r4.json()
    dump4 = json.dumps(data4)
    assert GENERIC_ERROR not in dump4

    codes4 = [m.get("code") for m in data4.get("messages", [])]
    assert "C44" in codes4, f"Expected C44 in {codes4}"
    assert reply_text in dump4 or "verified against access gate logs" in dump4

    # -------------------------------------------------------------
    # Step 5: USER-E05: "Why is my salary less this month?" -> C58, "3 LOP days recorded", "Show breakdown" chip
    # -------------------------------------------------------------
    r5 = client.post(
        "/api/chat",
        json={"user_id": "USER-E05", "message": "Why is my salary less this month?"},
        headers={"X-User-Id": "USER-E05"}
    )
    assert r5.status_code == 200
    data5 = r5.json()
    dump5 = json.dumps(data5)
    assert GENERIC_ERROR not in dump5

    codes5 = [m.get("code") for m in data5.get("messages", [])]
    assert "C58" in codes5, f"Expected C58 in {codes5}"
    assert "3 LOP days recorded" in dump5
    chip_labels5 = [ch.get("label") for ch in data5.get("chips", [])]
    assert "Show breakdown" in chip_labels5

    # -------------------------------------------------------------
    # Step 6: USER-E05: "Show me Priya's salary" -> C10 once
    # -------------------------------------------------------------
    r6 = client.post(
        "/api/chat",
        json={"user_id": "USER-E05", "message": "Show me Priya's salary"},
        headers={"X-User-Id": "USER-E05"}
    )
    assert r6.status_code == 200
    data6 = r6.json()
    dump6 = json.dumps(data6)
    assert GENERIC_ERROR not in dump6

    codes6 = [m.get("code") for m in data6.get("messages", [])]
    assert codes6.count("C10") == 1, f"Expected C10 exactly once, got {codes6}"

    # -------------------------------------------------------------
    # Step 7: USER-E05: "Which regime should I choose?" -> C11
    # -------------------------------------------------------------
    r7 = client.post(
        "/api/chat",
        json={"user_id": "USER-E05", "message": "Which regime should I choose?"},
        headers={"X-User-Id": "USER-E05"}
    )
    assert r7.status_code == 200
    data7 = r7.json()
    dump7 = json.dumps(data7)
    assert GENERIC_ERROR not in dump7

    codes7 = [m.get("code") for m in data7.get("messages", [])]
    assert "C11" in codes7, f"Expected C11 in {codes7}"

    # -------------------------------------------------------------
    # Step 8: HR01: "Show Imran Khan's settlement" -> settlement cards with no empty values, disabled approval with C59 reason
    # -------------------------------------------------------------
    r8 = client.post(
        "/api/chat",
        json={"user_id": "HR01", "message": "Show Imran Khan's settlement"},
        headers={"X-User-Id": "HR01"}
    )
    assert r8.status_code == 200
    data8 = r8.json()
    dump8 = json.dumps(data8)
    assert GENERIC_ERROR not in dump8

    # Assert no empty interpolations
    assert "from  to" not in dump8
    assert "from to" not in dump8

    # Verify approval card is disabled with C59 reason
    s8_approval = next((c for c in data8.get("cards", []) if c.get("type") == "approval_card"), None)
    assert s8_approval is not None
    assert s8_approval["data"].get("disabled") is True
    reason_s8 = s8_approval["data"].get("blocking_reason") or s8_approval["data"].get("disabled_label") or ""
    assert CANT_APPROVE_PREFIX in reason_s8
    assert "laptop clearance is pending" in reason_s8



def test_guard_all_suggestion_chips_click_without_failure():
    """GUARD: Every suggestion chip the app shows (HR default chips, Employee default chips,
    chips returned in replies for main scenarios) is clicked/sent once with AI mocked ON.
    Asserts none returns generic 'did not produce a usable result' or C33.
    """
    # Autouse fixture sets MockSmokeLLM and AI_MODE=True

    from app.backend.chat_router import _get_user_fallback_chips
    from app.backend.auth import USERS

    hr_user = USERS["HR01"]
    emp_user = USERS["USER-E05"]

    chips_to_test = []

    # HR default chips
    for chip in _get_user_fallback_chips(hr_user):
        chips_to_test.append(("HR01", chip))

    # Employee default chips
    for chip in _get_user_fallback_chips(emp_user):
        chips_to_test.append(("USER-E05", chip))

    # Fetch chips from main scenarios
    scenario_requests = [
        ("HR01", "Show pending proposals for approval"),
        ("HR01", "Show Imran Khan's settlement"),
        ("USER-E05", "Why is my salary less this month?"),
    ]
    for uid, msg in scenario_requests:
        resp = client.post(
            "/api/chat",
            json={"user_id": uid, "message": msg},
            headers={"X-User-Id": uid}
        )
        if resp.status_code == 200:
            for ch in resp.json().get("chips", []):
                chips_to_test.append((uid, ch))

    assert len(chips_to_test) >= 8, f"Expected at least 8 chips, found {len(chips_to_test)}"

    for uid, chip in chips_to_test:
        label = chip.get("label", "")
        action = chip.get("action")
        payload = chip.get("payload", {})

        req_body = {
            "user_id": uid,
            "message": label,
        }
        if action:
            req_body["action"] = action
            req_body["context"] = payload

        res = client.post(
            "/api/chat",
            json=req_body,
            headers={"X-User-Id": uid}
        )
        assert res.status_code == 200, f"Chip '{label}' returned status {res.status_code}"
        data = res.json()
        dump = json.dumps(data)

        assert GENERIC_ERROR not in dump, f"Chip '{label}' triggered GENERIC_ERROR: {dump}"
        codes = [m.get("code") for m in data.get("messages", [])]
        assert "C33" not in codes, f"Chip '{label}' triggered C33 fallback: {codes}"


def test_guard_tester_sequences_u1_to_u5():
    """GUARD: Exact verification of user tester bug scenarios U1 through U5."""
    # Autouse fixture sets MockSmokeLLM and AI_MODE=True

    # -------------------------------------------------------------
    # U1: Employee "Why was there LOP in my last month salary?"
    # Must show Recorded LOP days: 3 without "₹"
    # -------------------------------------------------------------
    r_u1 = client.post(
        "/api/chat",
        json={"user_id": "USER-E05", "message": "Why was there LOP in my last month salary?"},
        headers={"X-User-Id": "USER-E05"}
    )
    assert r_u1.status_code == 200
    d_u1 = r_u1.json()
    assert GENERIC_ERROR not in json.dumps(d_u1)
    
    lop_card = next((c for c in d_u1.get("cards", []) if c.get("type") == "number_hero"), None)
    assert lop_card is not None
    assert lop_card["data"].get("hero_label") == "Recorded LOP days"
    assert lop_card["data"].get("hero_amount") == 3
    # Check that day count is never a string with rupee
    assert "₹3" not in json.dumps(lop_card["data"])

    # -------------------------------------------------------------
    # U2: HR "prepare a bonus proposal" (and clicking "Prepare a bonus proposal")
    # Must return bonus type picker ("Which bonus type do you mean?")
    # -------------------------------------------------------------
    r_u2 = client.post(
        "/api/chat",
        json={"user_id": "HR01", "message": "prepare a bonus proposal"},
        headers={"X-User-Id": "HR01"}
    )
    assert r_u2.status_code == 200
    d_u2 = r_u2.json()
    assert GENERIC_ERROR not in json.dumps(d_u2)
    clarify_card = next((c for c in d_u2.get("cards", []) if c.get("type") == "clarifying_question"), None)
    assert clarify_card is not None
    assert "Which bonus type do you mean?" in clarify_card["data"].get("question")
    assert len(clarify_card["data"].get("choices", [])) >= 2

    # Click chip "Prepare a bonus proposal"
    r_u2_chip = client.post(
        "/api/chat",
        json={"user_id": "HR01", "message": "Prepare a bonus proposal", "action": "bonus-picker", "context": {}},
        headers={"X-User-Id": "HR01"}
    )
    assert r_u2_chip.status_code == 200
    d_u2_chip = r_u2_chip.json()
    assert GENERIC_ERROR not in json.dumps(d_u2_chip)
    assert any(c.get("type") == "clarifying_question" for c in d_u2_chip.get("cards", []))

    # -------------------------------------------------------------
    # U3: HR clicks "Edit with reason" on Sales incentive proposal
    # Must show revised version, edit reason, what changed, recalculated summary, and approval card for new version
    # -------------------------------------------------------------
    r_u3 = client.post(
        "/api/chat",
        json={
            "user_id": "HR01",
            "message": "Edit with reason",
            "action": "edit-proposal",
            "context": {
                "proposal_id": "PROP-SCENARIO-4-SALES",
                "version": 1,
                "reason": "Target adjusted by HR for Q2",
                "line": "target_achievement",
                "proposed_value": 120000
            }
        },
        headers={"X-User-Id": "HR01"}
    )
    assert r_u3.status_code == 200
    d_u3 = r_u3.json()
    assert GENERIC_ERROR not in json.dumps(d_u3)
    codes_u3 = [m.get("code") for m in d_u3.get("messages", [])]
    assert "C68" in codes_u3

    cards_u3 = d_u3.get("cards", [])
    assert len(cards_u3) >= 2, f"Expected at least 2 cards (revised summary + approval card), got {len(cards_u3)}"

    revised_card = cards_u3[0]
    assert revised_card.get("type") == "proposal_summary"
    assert revised_card["data"].get("version") == 2
    assert revised_card["data"].get("edit_reason") == "Target adjusted by HR for Q2"
    assert revised_card["data"].get("eligible_count") == 3
    assert revised_card["data"].get("gross_eligible_total") == 120000

    new_approval_card = cards_u3[1]
    assert new_approval_card.get("type") == "approval_card"
    assert new_approval_card["data"].get("version") == 2
    assert new_approval_card["data"].get("proposal_id") == "PROP-SCENARIO-4-SALES"
    assert new_approval_card["data"].get("disabled") is False

    # -------------------------------------------------------------
    # U4: Query closed without HR reply shows C67 and 'Closed by {Name} on {date}'
    # Never shows "Auto-resolved prior to closure."
    # -------------------------------------------------------------
    # First submit a query as USER-E05
    client.post(
        "/api/chat",
        json={
            "user_id": "USER-E05",
            "message": "Send query",
            "action": "send-query",
            "context": {"description": "Testing closure without reply"}
        },
        headers={"X-User-Id": "USER-E05"}
    )
    # Now close it without resolving or replying
    emp_queries = lifecycle.get_queries(employee_id="E05")
    latest_q = emp_queries[-1]
    q_id = latest_q["query_id"]

    r_u4_close = client.post(
        "/api/chat",
        json={
            "user_id": "USER-E05",
            "message": "Close query",
            "action": "close-query",
            "context": {"query_id": q_id}
        },
        headers={"X-User-Id": "USER-E05"}
    )
    assert r_u4_close.status_code == 200
    d_u4_close = r_u4_close.json()
    dump_u4 = json.dumps(d_u4_close)
    assert "Auto-resolved" not in dump_u4

    # Query status check
    r_u4_status = client.post(
        "/api/chat",
        json={"user_id": "USER-E05", "message": "Do I have a reply on my query?"},
        headers={"X-User-Id": "USER-E05"}
    )
    assert r_u4_status.status_code == 200
    d_u4_status = r_u4_status.json()
    dump_status = json.dumps(d_u4_status)
    assert "Auto-resolved" not in dump_status
    codes_u4 = [m.get("code") for m in d_u4_status.get("messages", [])]
    assert "C67" in codes_u4
    status_card = next((c for c in d_u4_status.get("cards", []) if c.get("type") == "query_status"), None)
    assert status_card is not None
    assert status_card["data"].get("closed_by") is not None

    # -------------------------------------------------------------
    # U5: Employee asks "who took this action and closed?"
    # Must route to query status, not C33
    # -------------------------------------------------------------
    for phrasing in [
        "who took this action and closed?",
        "who closed my query?",
        "who resolved this?",
        "who replied to my ticket?"
    ]:
        r_u5 = client.post(
            "/api/chat",
            json={"user_id": "USER-E05", "message": phrasing},
            headers={"X-User-Id": "USER-E05"}
        )
        assert r_u5.status_code == 200
        d_u5 = r_u5.json()
        assert GENERIC_ERROR not in json.dumps(d_u5)
        codes_u5 = [m.get("code") for m in d_u5.get("messages", [])]
        assert "C33" not in codes_u5, f"Phrasing '{phrasing}' returned C33: {codes_u5}"
        assert any(c.get("type") == "query_status" for c in d_u5.get("cards", [])), f"Phrasing '{phrasing}' did not return query_status card"


def test_smoke_show_query_mark_resolved_confirm_no_note():
    """Smoke test: show query -> mark resolved -> confirm (no note) -> C73, stored reply null."""
    lifecycle.reset_demo()

    # 1. Show query
    r_show = client.post(
        "/api/chat",
        json={"user_id": "HR01", "message": "Show Neha's query"},
        headers={"X-User-Id": "HR01"}
    )
    assert r_show.status_code == 200
    d_show = r_show.json()
    assert any(m.get("code") == "C43" for m in d_show.get("messages", []))
    resolve_chip = next((ch for ch in d_show.get("chips", []) if ch.get("label") == "Mark query resolved"), None)
    assert resolve_chip is not None

    # 2. Mark resolved
    r_mark = client.post(
        "/api/chat",
        json={
            "user_id": "HR01",
            "action": resolve_chip.get("action", "resolve-query"),
            "context": resolve_chip.get("payload", {"query_id": "QUERY-E05-SEPTEMBER", "employee_id": "E05"})
        },
        headers={"X-User-Id": "HR01"}
    )
    assert r_mark.status_code == 200
    d_mark = r_mark.json()
    assert any(m.get("code") == "C51" for m in d_mark.get("messages", []))
    confirm_card = next((c for c in d_mark.get("cards", []) if c.get("title") == "Resolve query confirmation"), None)
    assert confirm_card is not None
    assert confirm_card["data"].get("is_resolve_confirmation") is True

    # 3. Confirm (no note)
    r_confirm = client.post(
        "/api/chat",
        json={
            "user_id": "HR01",
            "action": "confirm-resolve-query",
            "context": {"query_id": "QUERY-E05-SEPTEMBER", "confirmed": True}
        },
        headers={"X-User-Id": "HR01"}
    )
    assert r_confirm.status_code == 200
    d_confirm = r_confirm.json()
    assert any(m.get("code") == "C73" for m in d_confirm.get("messages", []))
    assert d_confirm["cards"][0]["data"].get("status") == "Resolved"

    # Stored reply must be null (no invented reply)
    q = lifecycle.get_query("QUERY-E05-SEPTEMBER")
    assert q.get("status") == "Resolved"
    assert q.get("hr_reply") is None
