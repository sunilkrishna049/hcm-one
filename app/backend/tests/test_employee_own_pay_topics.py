"""Tests for Part B (Per-User Suggestion Chips) and Part C & E (Employee Own-Pay Topics a-g, C34-C36).
Verifies:
1. Every employee user (USER-E01 to USER-E16) and HR01/HR02: tapping any shown chip never returns C33 or C10.
2. Neha (USER-E05) never receives "Why did my TDS increase?".
3. Part C topics a-g return exact engine figures with AI off and mocked AI on.
4. All 13 Neha intent phrasings reach the exact right topic, never another employee, never FAQ for a personal query.
"""
import pytest
from fastapi.testclient import TestClient

from app.backend.main import app
from app.backend.auth import USERS, set_active_demo_user
from app.backend.chat_router import chat_router, get_employee_payroll_data
from app.backend.ai.crew import PayrollAICrew, ai_crew
from app.backend.tests.test_ai_crew_mocked import MockLLM
import app.backend.config as backend_config

client = TestClient(app)

ALL_TEST_USERS = [f"USER-E{i:02d}" for i in range(1, 17)] + ["HR01", "HR02"]

NEHA_PHRASINGS = [
    ("hw much pf ?", "pf_amount", "Your recorded employee PF contribution for September 2026 is ₹2,220."),
    ("How much PF was cut?", "pf_amount", "Your recorded employee PF contribution for September 2026 is ₹2,220."),
    ("Why is my TDS zero?", "tds_amount", "Your recorded TDS for September 2026 is ₹0."),
    ("How many LOP days do I have?", "lop_days", "3 days of loss of pay were recorded in your September 2026 attendance. If that's not right, you can raise a query."),
    ("Why was there LOP?", "lop_days", "3 days of loss of pay were recorded in your September 2026 attendance. If that's not right, you can raise a query."),
    ("Explain my September pay.", "payslip_breakdown", "Here is your recorded payslip breakdown for September 2026:"),
    ("Compare my August and September pay.", "compare_months", "Your September 2026 take-home is ₹5,420 lower than August 2026. The main recorded reasons are below."),
    ("What's happening with my query?", "query_status", "Your query is"),
    ("Which tax regime am I in?", "tax_regime", "Your employee record indicates you are under the New tax regime for Tax Year 2026-27."),
    ("Will I get a bonus this year?", "unrecorded_topic", "I don't have a record of that in your payroll data. You can raise a query with HR."),
    ("What is my October salary?", "unrecorded_topic", "I don't have a record of that in your payroll data. You can raise a query with HR."),
    ("Explain my June pay.", "unrecorded_month", "I can show your pay for August 2026 and September 2026 only."),
    ("What is basic pay?", "faq_question", "Here is the recorded meaning from the payroll glossary:")
]


@pytest.fixture(autouse=True)
def setup_test_mode(tmp_path):
    orig_mode = backend_config.AI_MODE
    orig_llm = ai_crew._custom_llm
    backend_config.AI_MODE = False
    ai_crew._custom_llm = None
    yield
    backend_config.AI_MODE = orig_mode
    ai_crew._custom_llm = orig_llm


def test_part_b_chips_per_user_no_c33_no_c10():
    """PART B — Chips must work for the person who sees them.
    For every employee user and HR01/HR02:
    - Tap every chip they are shown from fallback; none may return C33 or C10.
    - Neha must never get 'Why did my TDS increase?' (that is E06's scenario).
    """
    for user_id in ALL_TEST_USERS:
        # 1. Trigger fallback chips
        resp = client.post("/api/chat", json={
            "user_id": user_id,
            "message": "unrecognized intent prompt for fallback chip testing"
        })
        assert resp.status_code == 200, f"User {user_id} failed fallback call"
        data = resp.json()
        chips = data.get("chips", [])
        assert chips, f"User {user_id} was not shown any fallback chips"

        # Check Neha constraint: Neha must NEVER get TDS increase chip
        if user_id == "USER-E05":
            chip_labels = [c["label"].lower() for c in chips]
            assert not any("tds increase" in lbl for lbl in chip_labels), (
                f"Neha (USER-E05) was illegally shown TDS increase chip: {chip_labels}"
            )

        # 2. Tap every chip shown to this user
        for chip in chips:
            act = chip.get("action")
            ctx = chip.get("payload") or {}
            chip_lbl = chip.get("label")

            tap_resp = client.post("/api/chat", json={
                "user_id": user_id,
                "message": "",
                "action": act,
                "context": ctx
            })
            assert tap_resp.status_code == 200, (
                f"User {user_id} tapped chip '{chip_lbl}' ({act}) but got status {tap_resp.status_code}"
            )
            tap_data = tap_resp.json()
            msg_codes = [m.get("code") for m in tap_data.get("messages", [])]

            assert "C33" not in msg_codes, (
                f"User {user_id} tapping chip '{chip_lbl}' ({act}) returned fallback C33"
            )
            assert "C10" not in msg_codes, (
                f"User {user_id} tapping chip '{chip_lbl}' ({act}) was refused with C10"
            )


@pytest.mark.parametrize("ai_mode", ["router", "mocked_ai"])
def test_part_c_employee_own_pay_topics_match_engine(ai_mode):
    """PART C — Employee's own pay topics (Topics a-g, C34-C36).
    Every number comes from engine output; tested with AI off and mocked AI on.
    """
    if ai_mode == "router":
        backend_config.AI_MODE = False
        crew = PayrollAICrew(llm=None)
    else:
        backend_config.AI_MODE = True
        crew = PayrollAICrew(llm=MockLLM())

    user_id = "USER-E05"

    # Topic a: Payslip breakdown for September
    res_a = crew.handle_chat(user_id, message="Explain my September pay.")
    assert res_a["state"]["intent"] == "payslip_breakdown"
    card_a = res_a["cards"][0]
    assert card_a["data"]["gross_pay"] == 45000
    assert card_a["data"]["basic"] == 22500
    assert card_a["data"]["hra"] == 11250
    assert card_a["data"]["special_allowance"] == 11250
    assert card_a["data"]["da"] == 0
    assert card_a["data"]["total_deductions"] == 2220
    assert card_a["data"]["pf"] == 2220
    assert card_a["data"]["tds"] == 0
    assert card_a["data"]["net_pay"] == 42780

    # Topic b: PF amount
    res_b = crew.handle_chat(user_id, message="How much PF was cut?")
    assert res_b["state"]["intent"] == "pf_amount"
    assert res_b["cards"][0]["data"]["hero_amount"] == 2220
    assert "₹2,220" in res_b["messages"][0]["text"]

    # Topic c: TDS amount & why TDS is zero
    res_c = crew.handle_chat(user_id, message="Why is my TDS zero?")
    assert res_c["state"]["intent"] == "tds_amount"
    assert res_c["cards"][0]["data"]["hero_amount"] == 0
    assert res_c["cards"][0]["certainty"] == "Cannot explain from available payroll data"
    assert any(m["code"] == "C11" for m in res_c["messages"])

    # Topic d: LOP days by month
    res_d = crew.handle_chat(user_id, message="How many LOP days do I have?")
    assert res_d["state"]["intent"] == "lop_days"
    assert res_d["cards"][0]["data"]["hero_amount"] == 3
    assert "3 days of loss of pay were recorded in your September 2026 attendance" in res_d["messages"][0]["text"]

    # Topic e: Compare any two months the engine has
    res_e = crew.handle_chat(user_id, message="Compare my August and September pay.")
    assert res_e["state"]["intent"] == "compare_months"
    assert res_e["cards"][0]["data"]["hero_amount"] == -5420
    assert res_e["cards"][0]["data"]["previous_month_amount"] == 48200
    assert res_e["cards"][0]["data"]["current_month_amount"] == 42780

    # Topic f: Query status (status only; no invented dates, reviewer or reply)
    res_f = crew.handle_chat(user_id, message="What's happening with my query?")
    assert res_f["state"]["intent"] == "query_status"
    card_f = res_f["cards"][0]
    assert "status" in card_f["data"]
    assert "reviewer" not in card_f["data"]

    # Topic g: Tax regime from her record
    res_g = crew.handle_chat(user_id, message="Which tax regime am I in?")
    assert res_g["state"]["intent"] == "tax_regime"
    assert res_g["cards"][0]["data"]["tax_regime"] == "New tax regime"
    assert any(m["code"] == "C11" for m in res_g["messages"])

    # C34: unrecorded topics
    res_bonus = crew.handle_chat(user_id, message="Will I get a bonus this year?")
    assert res_bonus["state"]["intent"] == "unrecorded_topic"
    assert res_bonus["messages"][0]["code"] == "C34"
    assert res_bonus["messages"][0]["text"] == "I don't have a record of that in your payroll data. You can raise a query with HR."

    res_oct = crew.handle_chat(user_id, message="What is my October salary?")
    assert res_oct["state"]["intent"] == "unrecorded_topic"
    assert res_oct["messages"][0]["code"] == "C34"

    # C35: unrecorded months
    res_june = crew.handle_chat(user_id, message="Explain my June pay.")
    assert res_june["state"]["intent"] == "unrecorded_month"
    assert res_june["messages"][0]["code"] == "C35"
    assert res_june["messages"][0]["text"] == "I can show your pay for August 2026 and September 2026 only."


@pytest.mark.parametrize("phrasing,expected_topic,expected_reply_start", NEHA_PHRASINGS)
def test_part_e_neha_phrasings_intent_and_reply(phrasing, expected_topic, expected_reply_start):
    """PART E — Item 10 Intent test with the 13 Neha phrasings:
    Each must reach the right topic, never another employee, never FAQ for a personal question.
    """
    res = chat_router.handle_chat("USER-E05", message=phrasing)
    actual_intent = res.get("state", {}).get("intent")
    first_reply = res.get("messages", [{}])[0].get("text", "")

    assert actual_intent == expected_topic, (
        f"Phrasing '{phrasing}' reached intent '{actual_intent}', expected '{expected_topic}'"
    )
    assert expected_reply_start in first_reply, (
        f"Phrasing '{phrasing}' first reply was '{first_reply}', expected to contain '{expected_reply_start}'"
    )

    # Assert no cross-employee leak
    reply_str = str(res).lower()
    for eid in [f"e{i:02d}" for i in range(1, 17) if i != 5]:
        assert f"'{eid}'" not in reply_str and f'"{eid}"' not in reply_str
