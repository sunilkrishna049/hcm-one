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
    ("hw much pf ?", "pf_amount", "Your PF deduction for September 2026 is ₹2,220."),
    ("How much PF was cut?", "pf_amount", "Your PF deduction for September 2026 is ₹2,220."),
    ("Why is my TDS zero?", "tds_amount", "Your tax deducted (TDS) for September 2026 is ₹0. It's worked out as your remaining yearly tax divided by the months left in the tax year."),
    ("How many LOP days do I have?", "lop_days", "3 days of loss of pay were recorded in your September 2026 attendance. If that's not right, you can raise a query."),
    ("Why was there LOP?", "lop_days", "3 days of loss of pay were recorded in your September 2026 attendance. If that's not right, you can raise a query."),
    ("Explain my September pay.", "payslip_breakdown", "Here is your September 2026 payslip:"),
    ("Compare my August and September pay.", "compare_months", "Your September 2026 take-home is ₹5,420 lower than August 2026. The main recorded reasons are below."),
    ("What's happening with my query?", "query_status", "Your September 2026 query is In review. No reply has been recorded yet."),
    ("Which tax regime am I in?", "tax_regime", "You are on the new tax regime for 2026-27."),
    ("Will I get a bonus this year?", "unrecorded_topic", "I don't have a record of that in your payroll data. You can raise a query with HR."),
    ("What is my October salary?", "unrecorded_month", "I can show your pay for April to September 2026 only."),
    ("Explain my June pay.", "payslip_breakdown", "Here is your June 2026 payslip:"),
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
    assert res_a["messages"][0]["code"] == "C39"
    assert res_a["messages"][0]["text"] == "Here is your September 2026 payslip:"

    # Topic b: PF amount
    res_b = crew.handle_chat(user_id, message="How much PF was cut?")
    assert res_b["state"]["intent"] == "pf_amount"
    assert res_b["cards"][0]["data"]["hero_amount"] == 2220
    assert res_b["messages"][0]["code"] == "C37"
    assert res_b["messages"][0]["text"] == "Your PF deduction for September 2026 is ₹2,220."

    # Topic c: TDS amount & why TDS is zero (no number_hero card when amount is 0)
    res_c = crew.handle_chat(user_id, message="Why is my TDS zero?")
    assert res_c["state"]["intent"] == "tds_amount"
    assert len(res_c.get("cards", [])) == 0, "No number_hero card sent when TDS amount is 0"
    assert res_c["messages"][0]["code"] == "C38"
    assert res_c["messages"][0]["text"] == "Your tax deducted (TDS) for September 2026 is ₹0. It's worked out as your remaining yearly tax divided by the months left in the tax year."
    # C11 must not appear on factual question
    assert not any(m["code"] == "C11" for m in res_c["messages"])
    # Show calculation chip present
    assert any(c.get("action") == "show-calculation" for c in res_c.get("chips", []))

    # Topic d: LOP days by month
    res_d = crew.handle_chat(user_id, message="How many LOP days do I have?")
    assert res_d["state"]["intent"] == "lop_days"
    assert res_d["cards"][0]["data"]["hero_amount"] == 3
    assert res_d["messages"][0]["code"] == "C36"
    assert "3 days of loss of pay were recorded in your September 2026 attendance" in res_d["messages"][0]["text"]

    # Topic e: Compare any two months the engine has
    res_e = crew.handle_chat(user_id, message="Compare my August and September pay.")
    assert res_e["state"]["intent"] == "compare_months"
    assert res_e["cards"][0]["data"]["hero_amount"] == -5420
    assert res_e["cards"][0]["data"]["previous_month_amount"] == 48200
    assert res_e["cards"][0]["data"]["current_month_amount"] == 42780
    assert res_e["messages"][0]["code"] == "C30"

    # Topic f: Query status
    res_f = crew.handle_chat(user_id, message="What's happening with my query?")
    assert res_f["state"]["intent"] == "query_status"
    assert res_f["messages"][0]["code"] == "C40"
    assert res_f["messages"][0]["text"] == "Your September 2026 query is In review. No reply has been recorded yet."

    # Topic g: Tax regime from her record
    res_g = crew.handle_chat(user_id, message="Which tax regime am I in?")
    assert res_g["state"]["intent"] == "tax_regime"
    assert res_g["cards"][0]["data"]["tax_regime"] == "new"
    assert res_g["messages"][0]["code"] == "C41"
    assert res_g["messages"][0]["text"] == "You are on the new tax regime for 2026-27."
    assert not any(m["code"] == "C11" for m in res_g["messages"])

    # C34: unrecorded topics (bonus)
    res_bonus = crew.handle_chat(user_id, message="Will I get a bonus this year?")
    assert res_bonus["state"]["intent"] == "unrecorded_topic"
    assert res_bonus["messages"][0]["code"] == "C34"
    assert res_bonus["messages"][0]["text"] == "I don't have a record of that in your payroll data. You can raise a query with HR."

    # C35: unrecorded months (October)
    res_oct = crew.handle_chat(user_id, message="What is my October salary?")
    assert res_oct["state"]["intent"] == "unrecorded_month"
    assert res_oct["messages"][0]["code"] == "C35"
    assert res_oct["messages"][0]["text"] == "I can show your pay for April to September 2026 only."

    # June pay for E05 (June is in E05's ledger)
    res_june = crew.handle_chat(user_id, message="Explain my June pay.")
    assert res_june["state"]["intent"] == "payslip_breakdown"
    assert res_june["messages"][0]["code"] == "C39"
    assert res_june["messages"][0]["text"] == "Here is your June 2026 payslip:"

    # June pay for E06 (E06 joined July 2026; June is before joining)
    res_june_e06 = crew.handle_chat("USER-E06", message="Explain my June pay.")
    assert res_june_e06["state"]["intent"] == "unrecorded_month"
    assert res_june_e06["messages"][0]["code"] == "C35"
    assert res_june_e06["messages"][0]["text"] == "I can show your pay for July to September 2026 only."


def test_certainty_label_equals_engine_certainty():
    """Item 8: Certainty test: for every employee topic reply, each label shown
    equals the engine's certainty for that number.
    """
    for topic_query, expected_intent, expected_certainty in [
        ("Explain my September pay.", "payslip_breakdown", "Complete for this scope"),
        ("How much PF was cut?", "pf_amount", "Complete for this scope"),
        ("Why is my TDS zero?", "tds_amount", "Complete for this scope"),
        ("How many LOP days do I have?", "lop_days", "Complete for this scope"),
        ("Compare my August and September pay.", "compare_months", "Complete for this scope"),
        ("Which tax regime am I in?", "tax_regime", "Complete for this scope"),
    ]:
        res = chat_router.handle_chat("USER-E05", message=topic_query)
        assert res.get("state", {}).get("certainty") == expected_certainty
        if topic_query == "Why is my TDS zero?":
            assert len(res.get("cards", [])) == 0, "No card sent for TDS 0"
            res_nonzero = chat_router.handle_chat("USER-E06", message="Why did my TDS increase in September?")
            assert res_nonzero.get("cards")
            for card in res_nonzero["cards"]:
                assert card.get("certainty") == expected_certainty
            continue

        assert res.get("cards"), f"No card returned for '{topic_query}'"
        for card in res["cards"]:
            assert card.get("certainty") == expected_certainty, (
                f"Topic '{expected_intent}' card '{card.get('id')}' has certainty '{card.get('certainty')}', "
                f"expected engine certainty '{expected_certainty}'"
            )


def test_reply_level_state_certainty_for_topics_and_scenarios():
    """PART A — Items 1-3:
    For every employee topic and scenario reply:
    - If any payroll number appears in messages or cards, state.certainty equals the engine label.
    - Replies with no payroll number (FAQ, C33, C34, greetings) show no badge (state.certainty is None).
    """
    # 1. Scenarios with payroll numbers
    scenario_cases = [
        (1, "HR01", "Prepare Priya Sharma's pending back-dated hike.", "Complete for this scope"),
        (2, "HR01", "Prepare Arjun Rao's pending back-dated hike.", "Complete for this scope"),
        (3, "HR01", "Prepare Kavya Iyer's pending back-dated hike.", "Incomplete"),
        (4, "HR01", "Prepare bonus proposal for Engineering and Sales.", "Complete for this scope"),
        (5, "HR01", "Prepare bonus proposal for Meera Nair.", "Incomplete"),
        (6, "HR01", "Prepare settlement proposal for Rahul Verma.", "Complete for this scope"),
        (7, "HR01", "Prepare settlement proposal for Lakshmi Reddy.", "Complete for this scope"),
        (8, "HR01", "Prepare settlement proposal for Imran Khan.", "Incomplete"),
        (9, "USER-E05", "Why is my September salary lower than August?", "Complete for this scope"),
        (10, "USER-E06", "Why did my TDS increase in September?", "Complete for this scope"),
        (11, "USER-E16", "Why did my take-home pay decrease in September when my gross did not change?", "Complete for this scope"),
        (13, "HR01", "Review settlement calculation for Imran Khan.", "Incomplete"),
    ]
    for s_num, user, msg, expected_certainty in scenario_cases:
        res = chat_router.handle_chat(user, message=msg, context={"scenario_num": s_num})
        assert res.get("state", {}).get("certainty") == expected_certainty, (
            f"Scenario {s_num} state.certainty was '{res.get('state', {}).get('certainty')}', expected '{expected_certainty}'"
        )

    # 2. Employee topics with payroll numbers (including TDS zero where cards is empty)
    topic_cases = [
        ("Explain my September pay.", "Complete for this scope"),
        ("How much PF was cut?", "Complete for this scope"),
        ("Why is my TDS zero?", "Complete for this scope"),
        ("How many LOP days do I have?", "Complete for this scope"),
        ("Compare my August and September pay.", "Complete for this scope"),
        ("Which tax regime am I in?", "Complete for this scope"),
    ]
    for query, expected_certainty in topic_cases:
        res = chat_router.handle_chat("USER-E05", message=query)
        assert res.get("state", {}).get("certainty") == expected_certainty, (
            f"Topic '{query}' state.certainty was '{res.get('state', {}).get('certainty')}', expected '{expected_certainty}'"
        )

    # 3. Replies with NO payroll numbers show no badge (state.certainty is None)
    no_number_cases = [
        ("USER-E05", "What is basic pay?"),                # FAQ
        ("USER-E05", "What is HRA?"),                     # FAQ
        ("USER-E05", "hello"),                            # Greeting / clarification C33
        ("USER-E05", "Will I get a bonus this year?"),    # C34 unrecorded topic
        ("USER-E05", "What is my October salary?"),       # C35 unrecorded month
        ("HR02", "Show me Priya Sharma's salary breakdown."), # Scenario 12 refusal
    ]
    for user, query in no_number_cases:
        res = chat_router.handle_chat(user, message=query)
        assert res.get("state", {}).get("certainty") is None, (
            f"Query '{query}' state.certainty was '{res.get('state', {}).get('certainty')}', expected None"
        )


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
