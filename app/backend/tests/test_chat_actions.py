"""Tests for all chat actions and lifecycle flows through /api/chat.
Validates:
1. Proposal governance: approve, edit with reason, reject, and version staleness guards.
2. Approved state: "Approved and ready for payroll", version, approver, time (never looks like payment).
3. Employee & HR query lifecycle: draft, confirm send, append, take into review, reply, resolve, dispute, close.
4. Show calculation: opens calculation proof panel.
5. Role-scoped suggestion chips: HR role vs. Employee role.
6. Guard test: asserts NO valid action returns an error or unknown-intent fallback.
"""
from fastapi.testclient import TestClient
import pytest

from app.backend.main import app
from app.backend.lifecycle import lifecycle
import app.backend.config as backend_config

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_store_and_deterministic_mode():
    orig_ai_mode = backend_config.AI_MODE
    backend_config.AI_MODE = False
    lifecycle.reset_demo()
    yield
    backend_config.AI_MODE = orig_ai_mode



def test_approve_proposal_flow():
    """Clicking approve returns approved state: 'Approved and ready for payroll', version, approver, time."""
    # 1. Initialize proposal by loading scenario 1
    resp = client.post(
        "/api/chat",
        json={"user_id": "HR01", "action": "scenario-1", "context": {"scenario_num": 1}},
    )
    assert resp.status_code == 200

    # 2. Approve proposal with version 1
    approve_resp = client.post(
        "/api/chat",
        json={
            "user_id": "HR01",
            "action": "approve-proposal",
            "context": {"scenario_num": 1, "proposal_id": "PROP-SCENARIO-1", "version": 1},
        },
    )
    assert approve_resp.status_code == 200
    data = approve_resp.json()

    assert data["state"]["intent"] == "approve_proposal"
    assert data["state"]["status"] == "Approved and ready for payroll"

    # Card assertions
    assert len(data["cards"]) > 0
    appr_card = data["cards"][0]
    assert appr_card["type"] == "approval_card"
    assert appr_card["data"]["status"] == "approved"
    assert appr_card["data"]["status_text"] == "Approved and ready for payroll"
    assert appr_card["data"]["version"] == 1
    assert appr_card["data"]["approver"] == "Anita Desai"
    assert "Approved and ready for payroll" in appr_card["data"]["status_badge"]
    assert "Version 1" in appr_card["data"]["status_badge"]
    assert "Anita Desai" in appr_card["data"]["status_badge"]

    # Verify C04 message is not repeated in assistant messages
    assert len(data["messages"]) == 0
    # Verify no certainty label on approval card
    assert appr_card.get("certainty") is None
    # Verify past tense scope label
    assert "Approved:" in appr_card["data"]["scope_label"]
    # Verify no payment resemblance
    badge = appr_card["data"]["status_badge"].lower()
    assert "paid" not in badge
    assert "payment" not in badge


def test_approve_proposal_version_staleness_guard():
    """Attempting to approve a stale version returns C25 error notice."""
    client.post(
        "/api/chat",
        json={"user_id": "HR01", "action": "scenario-1", "context": {"scenario_num": 1}},
    )

    # Edit proposal to bump current version to 2
    edit_resp = client.post(
        "/api/chat",
        json={
            "user_id": "HR01",
            "action": "edit-proposal",
            "context": {
                "scenario_num": 1,
                "proposal_id": "PROP-SCENARIO-1",
                "line": "gross_arrears",
                "proposed_value": 72000,
                "reason": "Attendance adjustment",
            },
        },
    )
    assert edit_resp.status_code == 200
    assert edit_resp.json()["state"]["version"] == 2

    # Now attempt to approve version 1 (which is now stale!)
    stale_resp = client.post(
        "/api/chat",
        json={
            "user_id": "HR01",
            "action": "approve-proposal",
            "context": {"scenario_num": 1, "proposal_id": "PROP-SCENARIO-1", "version": 1},
        },
    )
    assert stale_resp.status_code == 200
    data = stale_resp.json()
    assert any(m["code"] == "C25" for m in data["messages"])


def test_edit_proposal_with_reason():
    """Editing a proposal requires reason, increments version, and returns C05."""
    edit_resp = client.post(
        "/api/chat",
        json={
            "user_id": "HR01",
            "action": "edit-proposal",
            "context": {
                "scenario_num": 1,
                "proposal_id": "PROP-SCENARIO-1",
                "line": "gross_arrears",
                "proposed_value": 70000,
                "reason": "Reviewed June punch log records",
            },
        },
    )
    assert edit_resp.status_code == 200
    data = edit_resp.json()
    assert data["state"]["intent"] == "edit_proposal"
    assert data["state"]["version"] == 2
    assert any(m["code"] == "C05" for m in data["messages"])


def test_reject_proposal():
    """Rejecting a proposal records rejection."""
    reject_resp = client.post(
        "/api/chat",
        json={
            "user_id": "HR01",
            "action": "reject-proposal",
            "context": {
                "scenario_num": 1,
                "proposal_id": "PROP-SCENARIO-1",
                "reason": "Documentation incomplete",
            },
        },
    )
    assert reject_resp.status_code == 200
    data = reject_resp.json()
    assert data["state"]["intent"] == "reject_proposal"
    assert any(m["code"] == "REJECTED" for m in data["messages"])
    assert data["cards"][0]["data"]["status"] == "rejected"


def test_full_query_lifecycle():
    """Full lifecycle: draft -> confirm_send -> append -> take_into_review -> reply -> resolve -> dispute -> close."""
    emp_user = "USER-E05"

    # 1. Draft Query
    draft_resp = client.post(
        "/api/chat",
        json={
            "user_id": emp_user,
            "action": "draft-query",
            "context": {
                "employee_id": "E05",
                "period": "2026-09",
                "description": "Please review September LOP deduction of 3 days.",
            },
        },
    )
    assert draft_resp.status_code == 200
    draft_data = draft_resp.json()
    assert draft_data["state"]["intent"] == "draft_query"
    assert any(m["code"] == "C12" for m in draft_data["messages"])
    draft = draft_data["state"]["draft"]
    assert draft["status"] == "Draft"

    # 2. Confirm and Send Query
    send_resp = client.post(
        "/api/chat",
        json={
            "user_id": emp_user,
            "action": "confirm-send-query",
            "context": {"draft": draft},
        },
    )
    assert send_resp.status_code == 200
    send_data = send_resp.json()
    assert any(m["code"] == "C15" for m in send_data["messages"])
    query_id = send_data["cards"][0]["data"]["query_id"]
    assert query_id.startswith("QUERY-E05-")

    # 3. Add to existing query (append)
    append_resp = client.post(
        "/api/chat",
        json={
            "user_id": emp_user,
            "action": "append-query",
            "context": {
                "draft": {"description": "Adding manager email approval."},
                "target_query_id": query_id,
            },
        },
    )
    assert append_resp.status_code == 200
    assert any(m["code"] in ("C15", "C16") for m in append_resp.json()["messages"])

    # 4. HR takes into review
    review_resp = client.post(
        "/api/chat",
        json={
            "user_id": "HR01",
            "action": "take-into-review",
            "context": {"query_id": query_id},
        },
    )
    assert review_resp.status_code == 200
    assert any(m["code"] == "C16" for m in review_resp.json()["messages"])
    assert review_resp.json()["cards"][0]["data"]["status"] == "In review"

    # 5. HR replies to query
    reply_resp = client.post(
        "/api/chat",
        json={
            "user_id": "HR01",
            "action": "reply-query",
            "context": {"query_id": query_id, "reply_text": "HR verified punch log."},
        },
    )
    assert reply_resp.status_code == 200
    assert any(m["code"] == "C16" for m in reply_resp.json()["messages"])

    # 6. HR resolves query
    resolve_resp = client.post(
        "/api/chat",
        json={
            "user_id": "HR01",
            "action": "resolve-query",
            "context": {"query_id": query_id, "reply_text": "Corrected in October cycle."},
        },
    )
    assert resolve_resp.status_code == 200
    assert any(m["code"] == "C23" for m in resolve_resp.json()["messages"])
    assert resolve_resp.json()["cards"][0]["data"]["status"] == "Resolved"

    # 7. Employee disputes resolution
    dispute_resp = client.post(
        "/api/chat",
        json={
            "user_id": emp_user,
            "action": "dispute-query",
            "context": {"query_id": query_id, "reason": "October cycle is too late."},
        },
    )
    assert dispute_resp.status_code == 200
    assert any(m["code"] == "C16" for m in dispute_resp.json()["messages"])
    assert dispute_resp.json()["cards"][0]["data"]["status"] == "In review"

    # Re-resolve so it can be closed
    client.post(
        "/api/chat",
        json={
            "user_id": "HR01",
            "action": "resolve-query",
            "context": {"query_id": query_id, "reply_text": "Off-cycle adjustment approved."},
        },
    )

    # 8. Employee closes query
    close_resp = client.post(
        "/api/chat",
        json={
            "user_id": emp_user,
            "action": "close-query",
            "context": {"query_id": query_id},
        },
    )
    assert close_resp.status_code == 200
    assert any(m["code"] == "C24" for m in close_resp.json()["messages"])
    assert close_resp.json()["cards"][0]["data"]["status"] == "Closed"


def test_show_calculation_action():
    """Action 'show-calculation' opens calculation proof panel."""
    resp = client.post(
        "/api/chat",
        json={
            "user_id": "HR01",
            "action": "show-calculation",
            "context": {"scenario_num": 1},
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["state"]["open_panel"] is True
    assert data["state"]["panel"] is not None
    assert "Calculation Proof" in data["state"]["panel"]["title"]


def test_suggestion_chips_role_scoping():
    """HR role gets HR chips only; HR never sees 'Why is my take-home pay lower in September?'.
    Employee role gets employee chips only; Employee never sees settlements or bonus.
    All chips under C33 lead to real answers."""
    # HR fallback
    hr_resp = client.post(
        "/api/chat",
        json={"user_id": "HR01", "message": "unrecognized question xyzz123"},
    )
    assert hr_resp.status_code == 200
    hr_data = hr_resp.json()
    assert hr_data["messages"][0]["code"] == "C33"
    assert "demo" not in hr_data["messages"][0]["text"].lower()
    hr_labels = [c["label"] for c in hr_data.get("chips", [])]
    assert "Why is my take-home pay lower in September?" not in hr_labels
    assert "Calculate arrears" in hr_labels
    assert "Prepare team bonus proposal" in hr_labels
    assert "Prepare full and final settlement" in hr_labels
    assert "Review payroll queries" in hr_labels

    # Verify each HR chip leads to a real answer
    for chip in hr_data.get("chips", []):
        chip_res = client.post(
            "/api/chat",
            json={"user_id": "HR01", "action": chip["action"], "context": chip.get("payload", {})},
        )
        assert chip_res.status_code == 200
        assert chip_res.json()["state"]["intent"] != "unknown"
        assert not any(m["code"] == "C33" for m in chip_res.json().get("messages", []))

    # Employee fallback
    emp_resp = client.post(
        "/api/chat",
        json={"user_id": "USER-E05", "message": "unrecognized question xyzz123"},
    )
    assert emp_resp.status_code == 200
    emp_data = emp_resp.json()
    assert emp_data["messages"][0]["code"] == "C33"
    assert "demo" not in emp_data["messages"][0]["text"].lower()
    emp_labels = [c["label"] for c in emp_data.get("chips", [])]
    assert "Why is my take-home pay lower in September?" in emp_labels
    assert "Calculate arrears" not in emp_labels
    assert "Prepare team bonus proposal" not in emp_labels
    assert "Prepare full and final settlement" not in emp_labels

    # Verify each Employee chip leads to a real answer
    for chip in emp_data.get("chips", []):
        chip_res = client.post(
            "/api/chat",
            json={"user_id": "USER-E05", "action": chip["action"], "context": chip.get("payload", {})},
        )
        assert chip_res.status_code == 200
        assert chip_res.json()["state"]["intent"] != "unknown"
        assert not any(m["code"] == "C33" for m in chip_res.json().get("messages", []))


def test_employee_picker_for_hr_tasks():
    """HR asking for arrears, settlement, or salary without naming an employee receives employee_picker card."""
    # 1. Arrears picker
    res_arr = client.post("/api/chat", json={"user_id": "HR01", "message": "Calculate arrears"})
    assert res_arr.status_code == 200
    data_arr = res_arr.json()
    cards_arr = {c["type"]: c for c in data_arr["cards"]}
    assert "employee_picker" in cards_arr
    picker_arr = cards_arr["employee_picker"]
    assert picker_arr["data"]["task"] == "arrears"
    arr_ids = [e["employee_id"] for e in picker_arr["data"]["employees"]]
    # Should contain pending revisions: E01, E02, E03
    assert "E01" in arr_ids
    assert "E02" in arr_ids

    # Tapping employee continues task (E01 -> Scenario 1)
    res_sel = client.post(
        "/api/chat",
        json={"user_id": "HR01", "action": "select-employee", "context": {"employee_id": "E01", "task": "arrears"}},
    )
    assert res_sel.status_code == 200
    assert res_sel.json()["state"]["scenario_num"] == 1

    # 2. Settlement picker
    res_set = client.post("/api/chat", json={"user_id": "HR01", "message": "Prepare full and final settlement"})
    assert res_set.status_code == 200
    data_set = res_set.json()
    cards_set = {c["type"]: c for c in data_set["cards"]}
    assert "employee_picker" in cards_set
    assert cards_set["employee_picker"]["data"]["task"] == "settlement"
    set_ids = [e["employee_id"] for e in cards_set["employee_picker"]["data"]["employees"]]
    assert "E10" in set_ids  # Rahul Verma
    assert "E11" in set_ids  # Lakshmi Reddy

    # 3. Salary picker
    res_sal = client.post("/api/chat", json={"user_id": "HR01", "message": "Show an employee's salary"})
    assert res_sal.status_code == 200
    data_sal = res_sal.json()
    cards_sal = {c["type"]: c for c in data_sal["cards"]}
    assert "employee_picker" in cards_sal
    assert cards_sal["employee_picker"]["data"]["task"] == "salary"

    # 4. Ambiguous name match (two matches for "Jain": Siddharth Jain E06 and Ankit Jain E13)
    res_amb = client.post("/api/chat", json={"user_id": "HR01", "message": "Show salary for Jain"})
    assert res_amb.status_code == 200
    data_amb = res_amb.json()
    assert "employee_picker" in [c["type"] for c in data_amb["cards"]]
    assert "Which Jain do you mean?" in data_amb["messages"][0]["text"]
    amb_ids = [e["employee_id"] for e in data_amb["cards"][0]["data"]["employees"]]
    assert "E06" in amb_ids
    assert "E13" in amb_ids

    # 5. No match ("Smith")
    res_nomatch = client.post("/api/chat", json={"user_id": "HR01", "message": "Show salary for Smith"})
    assert res_nomatch.status_code == 200
    data_nomatch = res_nomatch.json()
    assert "employee_picker" in [c["type"] for c in data_nomatch["cards"]]
    assert "I couldn't find an employee named Smith." in data_nomatch["messages"][0]["text"]


def test_faq_link_chip_role_scoping():
    """FAQ card action chip ('Show my latest payslip change') must only appear for employees, never in HR chat."""
    # Employee asks about LOP
    res_emp = client.post("/api/chat", json={"user_id": "USER-E05", "message": "What is LOP?"})
    assert res_emp.status_code == 200
    card_emp = res_emp.json()["cards"][0]
    assert card_emp["type"] == "faq_answer"
    assert card_emp["data"]["link_text"] == "Show my latest payslip change"

    # HR asks about LOP
    res_hr = client.post("/api/chat", json={"user_id": "HR01", "message": "What is LOP?"})
    assert res_hr.status_code == 200
    card_hr = res_hr.json()["cards"][0]
    assert card_hr["type"] == "faq_answer"
    assert card_hr["data"]["link_text"] == ""


def test_neha_salary_reply_fixes():
    """Neha's salary reply uses approved employee reason labels, first chip answers C27, and open query handles C14."""
    res = client.post("/api/chat", json={"user_id": "USER-E05", "message": "Why is my take-home pay lower in September?"})
    assert res.status_code == 200
    data = res.json()

    # Employee reason label verification
    reasons_card = next(c for c in data["cards"] if c["type"] == "reason_list")
    pf_reason = next(r for r in reasons_card["data"]["reasons"] if "PF" in r["cause"])
    assert pf_reason["cause"] == "PF deduction went up"
    assert pf_reason["detail"] == "PF wage limit raised from 17 Sep"

    # First chip answers question C27 ('Would you like the earnings and deductions breakdown?')
    assert data["chips"][0]["label"] == "Show breakdown"

    # Open query handling: Neha has September query in review -> C14 asked when drafting
    draft_res = client.post("/api/chat", json={"user_id": "USER-E05", "message": "Draft a query for HR"})
    assert draft_res.status_code == 200
    draft_data = draft_res.json()
    assert draft_data["messages"][0]["code"] == "C14"
    assert "Is this the same issue as your open query" in draft_data["messages"][0]["text"]
    chip_labels = [c["label"] for c in draft_data["chips"]]
    assert "Add to my September query" in chip_labels
    assert "Draft a new query" in chip_labels


def test_no_action_returns_error_or_unknown():
    """All wired action buttons and chips must resolve successfully without returning FALLBACK or unknown intent."""
    tested_actions = [
        ("HR01", "approve-proposal", {"scenario_num": 1, "proposal_id": "PROP-SCENARIO-1", "version": 1}),
        ("HR01", "edit-proposal", {"scenario_num": 1, "proposal_id": "PROP-SCENARIO-1", "reason": "Attendance edit"}),
        ("HR01", "reject-proposal", {"scenario_num": 1, "proposal_id": "PROP-SCENARIO-1", "reason": "Incomplete"}),
        ("USER-E05", "draft-query", {"employee_id": "E05", "period": "2026-09"}),
        ("USER-E05", "confirm-send-query", {}),
        ("HR01", "take-into-review", {}),
        ("HR01", "reply-query", {"reply_text": "Reviewed."}),
        ("HR01", "resolve-query", {"reply_text": "Resolved."}),
        ("USER-E05", "dispute-query", {"reason": "Disagree."}),
        ("USER-E05", "close-query", {}),
        ("HR01", "show-calculation", {"scenario_num": 1}),
        ("USER-E05", "query-status", {}),
        ("USER-E05", "faq-lop", {}),
        ("USER-E05", "faq-pf", {}),
        ("USER-E05", "faq-tds", {}),
    ]

    for user_id, action, ctx in tested_actions:
        resp = client.post(
            "/api/chat",
            json={"user_id": user_id, "action": action, "context": ctx},
        )
        assert resp.status_code == 200, f"Action {action} returned HTTP {resp.status_code}"
        data = resp.json()
        assert data.get("state", {}).get("intent") != "unknown", f"Action {action} resulted in unknown intent"
        messages = data.get("messages", [])
        assert not any(m.get("code") == "FALLBACK" for m in messages), f"Action {action} returned FALLBACK message"
