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
from app.backend.engine_bridge import bridge
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
    from app.backend.lifecycle import lifecycle
    orig_mode = backend_config.AI_MODE
    orig_llm = ai_crew._custom_llm
    backend_config.AI_MODE = False
    ai_crew._custom_llm = None
    lifecycle.reset_demo()
    yield
    backend_config.AI_MODE = orig_mode
    ai_crew._custom_llm = orig_llm
    lifecycle.reset_demo()


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
        (4, "HR01", "Prepare bonus proposal for Engineering and Sales.", "Incomplete"),
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
    ]
    for query, expected_certainty in topic_cases:
        res = chat_router.handle_chat("USER-E05", message=query)
        assert res.get("state", {}).get("certainty") == expected_certainty, (
            f"Topic '{query}' state.certainty was '{res.get('state', {}).get('certainty')}', expected '{expected_certainty}'"
        )

    # 3. Replies with NO payroll numbers / record facts show no badge (state.certainty is None)
    no_number_cases = [
        ("USER-E05", "What is basic pay?"),                # FAQ
        ("USER-E05", "What is HRA?"),                     # FAQ
        ("USER-E05", "hello"),                            # Greeting / clarification C33
        ("USER-E05", "Will I get a bonus this year?"),    # C34 unrecorded topic
        ("USER-E05", "What is my October salary?"),       # C35 unrecorded month
        ("USER-E05", "Which tax regime am I in?"),        # Record fact (no calculation)
        ("HR02", "Show me Priya Sharma's salary breakdown."), # Scenario 12 refusal
    ]
    for user, query in no_number_cases:
        res = chat_router.handle_chat(user, message=query)
        assert res.get("state", {}).get("certainty") is None, (
            f"Query '{query}' state.certainty was '{res.get('state', {}).get('certainty')}', expected None"
        )


def test_state_certainty_equals_engine_overall_certainty_for_all_scenarios():
    """PART A — Item 4:
    Test: state.certainty equals the engine overall certainty for every scenario (1–13).
    """
    scenario_inputs = [
        (1, "HR01", "Prepare Priya Sharma's pending back-dated hike."),
        (2, "HR01", "Prepare Arjun Rao's pending back-dated hike."),
        (3, "HR01", "Prepare Kavya Iyer's pending back-dated hike."),
        (4, "HR01", "Annual performance bonus, FY 2025-26, Engineering"),
        (5, "HR01", "Prepare bonus proposal for Meera Nair."),
        (6, "HR01", "Prepare settlement proposal for Rahul Verma."),
        (7, "HR01", "Prepare settlement proposal for Lakshmi Reddy."),
        (8, "HR01", "Prepare settlement proposal for Imran Khan."),
        (9, "USER-E05", "Why is my September salary lower than August?"),
        (10, "USER-E06", "Why did my TDS increase in September?"),
        (11, "USER-E16", "Why did my take-home pay decrease in September when my gross did not change?"),
        (12, "HR02", "Show me Priya Sharma's salary breakdown."),
        (13, "HR01", "Review settlement calculation for Imran Khan."),
    ]
    for s_num, user, msg in scenario_inputs:
        sc_engine = bridge.get_scenario(s_num)
        engine_certainty = sc_engine.get("result", {}).get("certainty")
        res = chat_router.handle_chat(user, message=msg, context={"scenario_num": s_num})
        shown_certainty = res.get("state", {}).get("certainty")
        assert shown_certainty == engine_certainty, (
            f"Scenario {s_num}: shown state.certainty ('{shown_certainty}') != engine overall certainty ('{engine_certainty}')"
        )


def test_static_guard_no_get_certainty_defaults_in_chat_router():
    """Guard test: chat_router.py has no .get('certainty', <label>) or invented certainty defaults."""
    import re
    with open("app/backend/chat_router.py", encoding="utf-8") as f:
        content = f.read()

    # Check for .get("certainty", <default>)
    matches = re.findall(r'\.get\(\s*["\']certainty["\']\s*,\s*["\'][^"\']+["\']\s*\)', content)
    assert not matches, f"Found .get('certainty', default) in chat_router.py: {matches}"

    # Check for .get("<field>_certainty", <default>)
    matches_field = re.findall(r'\.get\(\s*["\'][a-z_]*certainty["\']\s*,\s*["\'][^"\']+["\']\s*\)', content)
    assert not matches_field, f"Found .get('*_certainty', default) in chat_router.py: {matches_field}"

    # Check for hardcoded certainty string literals in dicts
    matches_literal = re.findall(r'["\']certainty["\']\s*:\s*["\'](Complete for this scope|Incomplete|Needs HR decision|Permission denied)["\']', content)
    assert not matches_literal, f"Found hardcoded certainty literal in chat_router.py: {matches_literal}"


def test_guard_certainty_integrity_all_replies():
    """Guard test: for every scenario, employee topic, FAQ and canned reply, every
    certainty label anywhere in the reply (state and cards) must exist in the
    engine source for that reply; otherwise fail.
    """
    # 1. Scenarios 1 to 13
    for s_num in range(1, 14):
        sc_engine = bridge.get_scenario(s_num)
        engine_cert = sc_engine.get("result", {}).get("certainty")
        user = "HR01"
        if s_num == 9:
            user = "USER-E05"
        elif s_num == 10:
            user = "USER-E06"
        elif s_num == 11:
            user = "USER-E16"
        elif s_num == 12:
            user = "HR02"

        res = chat_router.handle_chat(user, action=f"scenario-{s_num}", context={"scenario_num": s_num})

        # State certainty
        state_cert = res.get("state", {}).get("certainty")
        if s_num == 12:
            assert state_cert is None, f"Scenario 12 state.certainty should be None, got {state_cert}"
        else:
            assert state_cert == engine_cert, f"Scenario {s_num} state.certainty {state_cert} != engine {engine_cert}"

        # Card certainties
        for card in res.get("cards", []):
            c_cert = card.get("certainty")
            if c_cert is not None:
                assert c_cert == engine_cert or c_cert in str(sc_engine.get("result", {})), (
                    f"Card {card.get('id')} has certainty '{c_cert}' not found in engine result for scenario {s_num}"
                )

    # 2. Employee Topics with calculations
    topics = [
        ("Explain my September pay.", "payslip_breakdown", "certainty"),
        ("How much PF was cut?", "pf_amount", "pf_certainty"),
        ("Why is my TDS zero?", "tds_amount", "tds_certainty"),
        ("How many LOP days do I have?", "lop_days", "lop_certainty"),
        ("Compare my August and September pay.", "compare_months", "net_pay_certainty"),
    ]
    data_e05 = get_employee_payroll_data("E05", "2026-09")
    for query, expected_intent, engine_field in topics:
        res = chat_router.handle_chat("USER-E05", message=query)
        expected_cert = data_e05.get(engine_field)
        state_cert = res.get("state", {}).get("certainty")
        assert state_cert == expected_cert, f"Topic '{query}' state.certainty '{state_cert}' != expected '{expected_cert}'"
        for card in res.get("cards", []):
            if "certainty" in card:
                assert card["certainty"] == expected_cert, (
                    f"Topic '{query}' card '{card.get('id')}' certainty '{card['certainty']}' != expected '{expected_cert}'"
                )

    # 3. Non-calculating replies and record facts (FAQ, canned, greetings, C33, C34, C35, choices, pickers, tax regime)
    no_cert_cases = [
        ("USER-E05", "What is basic pay?", {}),
        ("USER-E05", "What is HRA?", {}),
        ("USER-E05", "hello", {}),
        ("USER-E05", "Will I get a bonus this year?", {}),
        ("USER-E05", "What is my October salary?", {}),
        ("USER-E05", "Which tax regime am I in?", {}),
        ("HR02", "Show me Priya Sharma's salary breakdown.", {}),
        ("HR01", "", {"action": "arrears-picker"}),
        ("HR01", "prepare a bonus proposal", {}),
    ]
    for user, query, kwargs in no_cert_cases:
        res = chat_router.handle_chat(user, message=query, **kwargs)
        assert res.get("state", {}).get("certainty") is None, (
            f"Query '{query}' {kwargs} state.certainty must be None, got '{res.get('state', {}).get('certainty')}'"
        )
        for card in res.get("cards", []):
            assert card.get("certainty") is None, (
                f"Query '{query}' {kwargs} card '{card.get('id')}' has certainty '{card.get('certainty')}', must be None"
            )


def test_item_2_bonus_type_own_engine_certainty():
    """Item 2: After HR picks a bonus type, use that bonus request's own engine certainty:
    - Annual performance bonus -> 'Incomplete' (its own label from scenario 4 engine result)
    - Sales incentive -> 'Complete for this scope' (its own label, NOT Scenario 4's overall 'Incomplete')
    """
    # 1. Direct prompt with Annual performance bonus
    res_annual = chat_router.handle_chat("HR01", message="Annual performance bonus, FY 2025-26, Engineering")
    assert res_annual["state"]["certainty"] == "Incomplete"
    for card in res_annual.get("cards", []):
        if card.get("id") in ("card-bonus-s4", "card-approval-s4"):
            assert card.get("certainty") == "Incomplete"

    # 2. Direct prompt with Sales incentive
    res_sales = chat_router.handle_chat("HR01", message="Q2 Sales incentive, Hyderabad Sales")
    assert res_sales["state"]["certainty"] == "Complete for this scope", (
        f"Sales incentive state.certainty should be its own engine certainty 'Complete for this scope', got '{res_sales['state']['certainty']}'"
    )
    for card in res_sales.get("cards", []):
        if card.get("id") in ("card-bonus-s4", "card-approval-s4"):
            assert card.get("certainty") == "Complete for this scope"

    # 3. Via action apply-selection
    res_sel_sales = chat_router.handle_chat("HR01", action="apply-selection", context={"choice": "Q2 Sales incentive, Hyderabad Sales"})
    assert res_sel_sales["state"]["certainty"] == "Complete for this scope"
    for card in res_sel_sales.get("cards", []):
        if card.get("id") in ("card-bonus-s4", "card-approval-s4"):
            assert card.get("certainty") == "Complete for this scope"

    res_sel_annual = chat_router.handle_chat("HR01", action="apply-selection", context={"choice": "Annual performance bonus, FY 2025-26, Engineering"})
    assert res_sel_annual["state"]["certainty"] == "Incomplete"
    for card in res_sel_annual.get("cards", []):
        if card.get("id") in ("card-bonus-s4", "card-approval-s4"):
            assert card.get("certainty") == "Incomplete"


def test_item_3_least_certain_label_order_and_combined_numbers():
    """Item 3: When a reply combines several numbers (e.g. comparing two months), the badge
    shows the least certain label among them:
    - Any label other than 'Complete for this scope' wins.
    - Order: Needs HR decision > Rule not verified > Incomplete > Cannot explain from available payroll data.
    """
    from app.backend.chat_router import get_least_certain_label

    # Precedence tests
    assert get_least_certain_label("Complete for this scope", "Complete for this scope") == "Complete for this scope"
    assert get_least_certain_label("Complete for this scope", "Incomplete") == "Incomplete"
    assert get_least_certain_label("Complete for this scope", "Needs HR decision") == "Needs HR decision"
    assert get_least_certain_label("Complete for this scope", "Rule not verified") == "Rule not verified"
    assert get_least_certain_label("Complete for this scope", "Cannot explain from available payroll data") == "Cannot explain from available payroll data"

    # Hierarchy among non-complete labels
    # Needs HR decision beats all
    assert get_least_certain_label("Needs HR decision", "Rule not verified") == "Needs HR decision"
    assert get_least_certain_label("Needs HR decision", "Incomplete") == "Needs HR decision"
    assert get_least_certain_label("Needs HR decision", "Cannot explain from available payroll data") == "Needs HR decision"

    # Rule not verified beats Incomplete and Cannot explain
    assert get_least_certain_label("Rule not verified", "Incomplete") == "Rule not verified"
    assert get_least_certain_label("Rule not verified", "Cannot explain from available payroll data") == "Rule not verified"

    # Incomplete beats Cannot explain
    assert get_least_certain_label("Incomplete", "Cannot explain from available payroll data") == "Incomplete"

    # Multi-label combinations
    assert get_least_certain_label("Complete for this scope", "Incomplete", "Needs HR decision", "Rule not verified") == "Needs HR decision"
    assert get_least_certain_label("Complete for this scope", "Rule not verified", "Incomplete") == "Rule not verified"
    assert get_least_certain_label("Complete for this scope", "Cannot explain from available payroll data", "Incomplete") == "Incomplete"

    # None and empty handling
    assert get_least_certain_label(None, "Complete for this scope") == "Complete for this scope"
    assert get_least_certain_label(None, "Incomplete") == "Incomplete"
    assert get_least_certain_label(None, None) is None

    # Test month comparison query combining August and September
    res = chat_router.handle_chat("USER-E05", message="Compare my August and September pay.")
    assert res["state"]["intent"] == "compare_months"
    assert res["state"]["certainty"] == "Complete for this scope"
    assert res["cards"][0]["certainty"] == "Complete for this scope"


def test_item_4_record_facts_no_badge():
    """Item 4: Facts from records that are not calculations (e.g. tax regime): no badge."""
    res = chat_router.handle_chat("USER-E05", message="Which tax regime am I in?")
    assert res["state"]["intent"] == "tax_regime"
    assert res["state"]["certainty"] is None, (
        f"Record fact query must have state.certainty = None, got '{res['state']['certainty']}'"
    )
    for card in res.get("cards", []):
        assert card.get("certainty") is None, (
            f"Record fact card '{card.get('id')}' must not have certainty badge, got '{card.get('certainty')}'"
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


def test_q1_neha_own_query_status_phrasings_never_c10():
    """Q1: In Employee view (Neha Gupta, USER-E05), her own query must never be refused with C10.
    Phrasings:
    - 'Do I have a reply on my query?'
    - 'Has HR replied to my query?'
    - 'Any update on my query?'
    - 'What is the status of my query?'
    Each returns Neha's own query status (C40 when no reply yet), never C10.
    """
    from app.backend.ai.crew import PayrollAICrew
    from app.backend.lifecycle import lifecycle
    import app.backend.config as backend_config

    backend_config.AI_MODE = False
    lifecycle.reset_demo()

    crew = PayrollAICrew()
    phrasings = [
        "Do I have a reply on my query?",
        "Has HR replied to my query?",
        "Any update on my query?",
        "What is the status of my query?",
    ]

    for p in phrasings:
        res = crew.handle_chat("USER-E05", message=p)
        codes = [m["code"] for m in res.get("messages", [])]
        first_text = res.get("messages", [{}])[0].get("text", "")

        assert "C10" not in codes, f"Phrasing '{p}' unexpectedly returned C10 refusal: {res}"
        assert "C40" in codes, f"Phrasing '{p}' expected C40 query status, got {codes}"
        assert "Your September 2026 query is" in first_text, f"Phrasing '{p}' text unexpected: {first_text}"
        assert "No reply has been recorded yet." in first_text, f"Phrasing '{p}' text unexpected: {first_text}"
        assert res.get("state", {}).get("intent") == "query_status"
        assert res.get("state", {}).get("employee_id") == "E05"

        cards = [c["type"] for c in res.get("cards", [])]
        assert "query_status" in cards, f"Phrasing '{p}' missing query_status card"
        assert "refusal_card" not in cards, f"Phrasing '{p}' unexpectedly returned refusal_card"


def test_q1_neha_query_with_hr_reply():
    """Q1: When HR has replied first, Neha sees the C44 query reply message plus reply text, never C10."""
    from app.backend.ai.crew import PayrollAICrew
    from app.backend.lifecycle import lifecycle
    import app.backend.config as backend_config

    backend_config.AI_MODE = False
    lifecycle.reset_demo()

    reply_str = "Biometric punch logs rechecked; half-day attendance adjusted."
    lifecycle.resolve_query(
        "QUERY-E05-SEPTEMBER",
        actor={"user_id": "HR01", "role": "HR Admin"},
        reply_text=reply_str
    )

    crew = PayrollAICrew()
    res = crew.handle_chat("USER-E05", message="Do I have a reply on my query?")
    codes = [m["code"] for m in res.get("messages", [])]
    first_text = res.get("messages", [{}])[0].get("text", "")

    assert "C10" not in codes, f"Unexpected C10 refusal: {res}"
    assert "C44" in codes, f"Expected C44 query reply code, got {codes}"
    assert reply_str in first_text, f"Expected reply text '{reply_str}' in message, got '{first_text}'"
    assert "Your September 2026 query is Resolved. Here is HR's reply:" in first_text

    cards = [c["type"] for c in res.get("cards", [])]
    assert "query_status" in cards
    assert "refusal_card" not in cards

    lifecycle.reset_demo()


def test_q1_cross_employee_query_inquiry_strictly_returns_c10():
    """Q1: An employee asking about ANOTHER employee's query still gets C10 refusal."""
    from app.backend.ai.crew import PayrollAICrew
    from app.backend.lifecycle import lifecycle
    import app.backend.config as backend_config

    backend_config.AI_MODE = False
    lifecycle.reset_demo()

    crew = PayrollAICrew()
    cross_queries = [
        "What is Neha's query status?",
        "Did HR reply to Neha's query?",
        "Show Neha's query",
        "Has HR replied to Priya Sharma's query?",
    ]

    for cq in cross_queries:
        res = crew.handle_chat("USER-E06", message=cq)
        codes = [m["code"] for m in res.get("messages", [])]
        assert "C10" in codes, f"Cross-employee query '{cq}' expected C10, got {codes}"
        cards = [c["type"] for c in res.get("cards", [])]
        assert "refusal_card" in cards
