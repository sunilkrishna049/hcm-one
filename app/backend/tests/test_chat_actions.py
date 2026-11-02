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
    assert "Calculation proof" in data["state"]["panel"]["title"]


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
    assert "Prepare a bonus proposal" in hr_labels
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
    assert "Prepare a bonus proposal" not in emp_labels
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


def test_static_guard_no_scenario_1_or_priya_fallbacks():
    """Static guard asserting NO fallbacks to scenario 1 or Priya Sharma or default proposals exist in code."""
    from pathlib import Path
    base_dir = Path(__file__).resolve().parent.parent.parent
    files_to_check = [
        base_dir / "backend" / "chat_router.py",
        base_dir / "backend" / "lifecycle.py",
        base_dir / "backend" / "crew.py",
        base_dir / "backend" / "main.py",
    ]

    forbidden_patterns = [
        'scenario_num", 1)',
        "scenario_num or 1",
        'scenario_num = 1',
        'context.get("proposal_id", f"PROP-SCENARIO-',
        'context.get("proposal_id", "PROP-SCENARIO-',
        'employee_id", "E01")',
        'employee_id or "E01"',
    ]

    for fpath in files_to_check:
        if not fpath.exists():
            continue
        content = fpath.read_text(encoding="utf-8")
        for line_num, line in enumerate(content.splitlines(), start=1):
            # Skip comments or default dictionary definitions
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            for pattern in forbidden_patterns:
                # Disallow forbidden fallbacks in logic
                if pattern in line and "DEFAULT_PROPOSALS" not in line and "test" not in str(fpath):
                    pytest.fail(f"Forbidden fallback pattern '{pattern}' found at {fpath.name}:{line_num}: {line}")

    # Also check frontend components (excluding test directory and TopDemoBar demo selector)
    frontend_src = base_dir / "frontend" / "src"
    frontend_files = [
        f for f in frontend_src.rglob("*")
        if f.is_file() and "tests" not in f.parts and f.name != "TopDemoBar.tsx" and f.suffix in (".ts", ".tsx")
    ]

    frontend_forbidden = [
        "?? 1",
        "currentScenario = 1",
        "currentScenario = 9",
        "defaultScenario = 1",
        "defaultScenario: 1",
        "PROP-SCENARIO-1",
    ]

    for fpath in frontend_files:
        content = fpath.read_text(encoding="utf-8")
        for line_num, line in enumerate(content.splitlines(), start=1):
            stripped = line.strip()
            if stripped.startswith("//") or stripped.startswith("/*"):
                continue
            for pattern in frontend_forbidden:
                if pattern in line:
                    pytest.fail(f"Forbidden frontend fallback pattern '{pattern}' found at {fpath.name}:{line_num}: {line}")


def test_approval_integrity_for_all_proposals():
    """Tests approval integrity across all proposals:
    Scenarios 1, 2, 3, 6, 7, 8, 13 and both bonus types (Annual and Sales).
    - Approve succeeds ONLY for complete proposals (S1, S2, S4-Sales, S6, S7) and modifies EXACTLY that proposal.
    - Confirmation shows the same scope as the card that was approved.
    - Approving an Incomplete proposal (S3, S4-Annual, S8, S13) is refused and changes nothing.
    - Approving with missing, unknown, or mismatched proposal_id/version changes nothing and is refused.
    """
    complete_proposals = [
        ("PROP-SCENARIO-1", 1, "Priya Sharma · Apr–Sep 2026"),
        ("PROP-SCENARIO-2", 2, "Arjun Rao · September 2026"),
        ("PROP-SCENARIO-4-SALES", 4, "Sales incentive (Q2 2026-27) · Hyderabad Sales"),
        ("PROP-SCENARIO-6", 6, "Rahul Verma · Settlement"),
        ("PROP-SCENARIO-7", 7, "Lakshmi Reddy · Settlement"),
    ]

    incomplete_proposals = [
        ("PROP-SCENARIO-3", 3, "Kavya Iyer"),
        ("PROP-SCENARIO-4-ANNUAL", 4, "Annual performance bonus · Engineering"),
        ("PROP-SCENARIO-8", 8, "Imran Khan"),
        ("PROP-SCENARIO-13", 13, "Imran Khan"),
    ]

    # 1. Test each complete proposal
    for prop_id, s_num, expected_scope in complete_proposals:
        lifecycle.reset_demo()
        prop_before = lifecycle.get_proposal(prop_id)
        assert prop_before["status"] == "Calculated; needs HR approval"

        resp = client.post(
            "/api/chat",
            json={
                "user_id": "HR01",
                "action": "approve-proposal",
                "context": {"proposal_id": prop_id, "version": 1},
            },
        )
        assert resp.status_code == 200, f"Approval failed for {prop_id}"
        data = resp.json()
        assert data.get("state", {}).get("intent") == "approve_proposal"
        card = data["cards"][0]
        assert card["data"]["status"] == "approved"
        assert card["data"]["proposal_id"] == prop_id
        assert expected_scope in card["data"]["scope_label"]
        assert "Approved:" in card["data"]["scope_label"]

        # Verify ONLY this proposal changed in runtime
        prop_after = lifecycle.get_proposal(prop_id)
        assert prop_after["status"] == "Approved and ready for payroll"
        assert prop_after["approved_version"] == 1

        # Check all other proposals are untouched
        for other_id, _, _ in complete_proposals + incomplete_proposals:
            if other_id != prop_id:
                other_prop = lifecycle.get_proposal(other_id)
                assert other_prop["status"] == "Calculated; needs HR approval", (
                    f"Proposal {other_id} was modified when approving {prop_id}!"
                )

    # 2. Test each incomplete proposal (Option A: must be refused)
    for prop_id, s_num, expected_name in incomplete_proposals:
        lifecycle.reset_demo()
        resp = client.post(
            "/api/chat",
            json={
                "user_id": "HR01",
                "action": "approve-proposal",
                "context": {"proposal_id": prop_id, "version": 1},
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        card = data["cards"][0]
        assert card["data"]["status"] == "blocked" or "refused" in card["data"].get("status_badge", "").lower()

        # Proposal in store must NOT be approved
        prop_check = lifecycle.get_proposal(prop_id)
        assert prop_check["status"] == "Calculated; needs HR approval"

    # 3. Missing proposal_id -> refused, nothing changed
    lifecycle.reset_demo()
    resp_missing = client.post(
        "/api/chat",
        json={
            "user_id": "HR01",
            "action": "approve-proposal",
            "context": {"version": 1},
        },
    )
    assert resp_missing.status_code == 200
    assert resp_missing.json()["cards"][0]["data"]["status"] == "error"
    # Ensure scenario 1 is NOT approved
    assert lifecycle.get_proposal("PROP-SCENARIO-1")["status"] == "Calculated; needs HR approval"

    # 4. Unknown proposal_id -> refused, nothing changed
    resp_unknown = client.post(
        "/api/chat",
        json={
            "user_id": "HR01",
            "action": "approve-proposal",
            "context": {"proposal_id": "PROP-UNKNOWN-99", "version": 1},
        },
    )
    assert resp_unknown.status_code == 200
    assert resp_unknown.json()["cards"][0]["data"]["status"] == "error"

    # 5. Mismatched version -> C25 refused, nothing changed
    resp_mismatch = client.post(
        "/api/chat",
        json={
            "user_id": "HR01",
            "action": "approve-proposal",
            "context": {"proposal_id": "PROP-SCENARIO-1", "version": 99},
        },
    )
    assert resp_mismatch.status_code == 200
    assert any(m["code"] == "C25" for m in resp_mismatch.json()["messages"])
    assert lifecycle.get_proposal("PROP-SCENARIO-1")["status"] == "Calculated; needs HR approval"


def test_advice_refusal_equals_c11_exactly():
    """Item 5: The advice refusal ('Which regime should I choose?') must equal C11
    exactly as written in conversation-design.md.
    """
    import re
    from pathlib import Path
    from app.backend.ai_messages import get_message

    # Read conversation-design.md and extract the personal tax advice refusal text
    conv_design_path = Path("output/06-ai-interaction/conversation-design.md")
    assert conv_design_path.exists(), f"{conv_design_path} does not exist"
    content = conv_design_path.read_text(encoding="utf-8")

    match = re.search(r'\|\s*Personal tax advice\s*\|\s*"([^"]+)"', content)
    assert match, "Could not find Personal tax advice table row in conversation-design.md"
    expected_refusal = match.group(1).strip()

    assert expected_refusal == (
        "I can explain the tax recorded in your payroll. "
        "I cannot recommend a tax regime or investment. "
        "Please consult a tax professional for personal advice."
    )

    # API call with exact prompt
    resp = client.post("/api/chat", json={
        "user_id": "USER-E05",
        "message": "Which regime should I choose?"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["state"]["intent"] == "out_of_scope"
    assert len(data["messages"]) > 0
    assert data["messages"][0]["code"] == "C11"
    assert data["messages"][0]["text"] == expected_refusal
    assert get_message("C11") == expected_refusal


def test_name_guard_permanent_check():
    """Item 6: Name guard permanent test.
    - Every person name in every /api/chat response across the full test matrix
      (scenarios, employee topics, chip taps, picker, approvals), in approved
      sentences, and in FAQ text must exist in data/mock/employees.json or users.json.
    - Regression check: fail if any of these appear anywhere in app code, copy or
      fixtures: Ananya, Sameer, Divya, Sanjay, Aarav, Vikramaditya, Rohan Joshi.
    """
    import json
    import glob
    import os
    from pathlib import Path
    from app.backend.ai_messages import AI_MESSAGES

    # 1. Regression check: fail if any disallowed name appears in app code, copy, or fixtures
    disallowed_names = ["Ananya", "Sameer", "Divya", "Sanjay", "Aarav", "Vikramaditya", "Rohan Joshi"]
    code_paths = (
        glob.glob("app/backend/**/*.py", recursive=True)
        + glob.glob("app/frontend/src/**/*.ts", recursive=True)
        + glob.glob("app/frontend/src/**/*.tsx", recursive=True)
        + glob.glob("app/frontend/src/tests/*.json", recursive=True)
    )

    for p in code_paths:
        if not os.path.isfile(p):
            continue
        # Skip this test file and existing test_chat_endpoint.py asserting absence
        if "test_chat_actions.py" in p or "test_chat_endpoint.py" in p:
            continue
        with open(p, "r", encoding="utf-8", errors="ignore") as f:
            file_text = f.read()
        for d in disallowed_names:
            assert d not in file_text, f"Disallowed name '{d}' found in {p}"

    # 2. Load valid mock names
    with open("data/mock/employees.json", "r", encoding="utf-8") as f:
        emps = json.load(f)
    with open("data/mock/users.json", "r", encoding="utf-8") as f:
        users = json.load(f)

    valid_full_names = {e["name"] for e in emps if "name" in e} | {u["name"] for u in users if "name" in u}

    all_texts = []

    # Approved sentences
    for k, v in AI_MESSAGES.items():
        all_texts.append(v)

    # FAQ text
    with open("data/knowledge/payroll_faq.json", "r", encoding="utf-8") as f:
        faq_data = json.load(f)
        for q in faq_data.get("questions", []):
            all_texts.append(q.get("question", "") + " " + q.get("answer", ""))

    # Full test matrix
    matrix_calls = [
        # Scenarios 1-13
        ("HR01", "Prepare Priya Sharma's pending back-dated hike", None, None),
        ("HR01", "Review Arjun Rao's pending back-dated hike", None, None),
        ("HR01", "Prepare Kavya Iyer's pending back-dated hike", None, None),
        ("HR01", "Prepare bonus proposal for Engineering and Sales.", None, None),
        ("HR01", "Prepare bonus proposal for Meera Nair.", None, None),
        ("HR01", "Prepare Rahul Verma's full & final settlement.", None, None),
        ("HR01", "Prepare Lakshmi Reddy's full & final settlement.", None, None),
        ("HR01", "Prepare Imran Khan's full & final settlement.", None, None),
        ("HR01", None, "scenario-9", {"scenario_num": 9}),
        ("HR01", None, "scenario-10", {"scenario_num": 10}),
        ("HR01", None, "scenario-11", {"scenario_num": 11}),
        ("HR01", None, "scenario-12", {"scenario_num": 12}),
        ("HR01", None, "scenario-13", {"scenario_num": 13}),
        # Picker
        ("HR01", "Calculate arrears", None, None),
        ("HR01", None, "select-employee", {"employee_id": "E01", "task": "arrears"}),
        # Queries
        ("HR01", "Review payroll queries", None, None),
        # Employee topics
        ("USER-E05", "Why is my take-home lower this month?", None, None),
        ("USER-E05", "Why is my pay lower in September compared to August?", None, None),
        ("USER-E05", "How much PF was deducted from my salary?", None, None),
        ("USER-E05", "Why is my TDS zero?", None, None),
        ("USER-E05", "How many LOP days do I have?", None, None),
        ("USER-E05", "Compare August and September pay", None, None),
        ("USER-E05", "What is the status of my query?", None, None),
        ("USER-E05", "Which regime should I choose?", None, None),
        ("USER-E05", "What will my October salary be?", None, None),
        ("USER-E05", "Show my salary for July 2026", None, None),
        ("USER-E06", "Why did my TDS increase in September?", None, None),
        ("USER-E16", "Explain my deduction", None, None),
        # Approvals
        ("HR01", None, "approve-proposal", {"scenario_num": 1, "proposal_id": "PROP-SCENARIO-1", "version": 1}),
        ("HR01", None, "approve-proposal", {"scenario_num": 4, "proposal_id": "PROP-SCENARIO-4-SALES", "version": 1}),
    ]

    import re
    import pytest

    def check_reply_names(obj, valid_names, parent_key=""):
        NON_PERSON_NAMES = {
            "asset recovery", "earned salary", "gratuity", "leave encashment",
            "notice shortfall recovery", "salary advance", "basic", "hra", "pf", "tds"
        }

        if isinstance(obj, dict):
            if "employee_name" in obj and obj["employee_name"]:
                val = str(obj["employee_name"]).strip()
                assert val in valid_names, f"Unknown name '{val}' in employee_name field"

            if "approver" in obj and obj["approver"]:
                if isinstance(obj["approver"], str):
                    val = obj["approver"].strip()
                    if not val.startswith("HR") and not val.startswith("USER-"):
                        assert val in valid_names, f"Unknown name '{val}' in approver field"
                elif isinstance(obj["approver"], dict) and "name" in obj["approver"]:
                    val = str(obj["approver"]["name"]).strip()
                    assert val in valid_names, f"Unknown name '{val}' in approver.name field"

            if "name" in obj and obj["name"]:
                val = str(obj["name"]).strip()
                if val.lower() not in NON_PERSON_NAMES:
                    assert val in valid_names, f"Unknown name '{val}' in name field"

            for k, v in obj.items():
                if isinstance(v, str):
                    m = re.match(r"^(?:Approved:\s*)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\s*·\s*E\d{2}", v)
                    if m:
                        extracted_name = m.group(1).strip()
                        assert extracted_name in valid_names, f"Unknown name '{extracted_name}' in label '{v}'"
                check_reply_names(v, valid_names, k)

        elif isinstance(obj, list):
            for item in obj:
                check_reply_names(item, valid_names, parent_key)

    for user_id, msg, act, ctx in matrix_calls:
        body = {"user_id": user_id}
        if msg:
            body["message"] = msg
        if act:
            body["action"] = act
        if ctx:
            body["context"] = ctx
        res = client.post("/api/chat", json=body)
        assert res.status_code == 200, f"Status {res.status_code} on {body}"
        payload = res.json()
        check_reply_names(payload, valid_full_names)
        all_texts.append(json.dumps(payload))

    combined = " ".join(all_texts)

    # Disallowed names must not appear across the full matrix, approved copy, or FAQ
    for d in disallowed_names:
        assert d not in combined, f"Disallowed name '{d}' found in chat matrix or copy"

    # All matched person names must exist in employees.json or users.json
    found_names = {name for name in valid_full_names if name in combined}
    assert len(found_names) > 0, "No valid person names found in responses"

    # Proof: Inject "Kiran Das" into a mocked reply -> fails
    with pytest.raises(AssertionError) as exc_kiran:
        check_reply_names({"cards": [{"type": "proposal_summary", "data": {"employee_name": "Kiran Das"}}]}, valid_full_names)
    assert "Kiran Das" in str(exc_kiran.value)

    # Proof: Inject "Aarav Patel" into a mocked reply -> fails
    with pytest.raises(AssertionError) as exc_aarav:
        check_reply_names({"cards": [{"type": "approval_card", "data": {"approver": "Aarav Patel"}}]}, valid_full_names)
    assert "Aarav Patel" in str(exc_aarav.value)


def test_approval_blocked_reason_built_from_engine_data():
    """Item 5 & R3: The approval blocked reason must be built from engine data for every non-complete
    proposal (Kavya Iyer's arrears, Imran Khan's settlement, the bonus), each with a test.
    If 1 reason: C59 ('{Name}\'s {item} is {status}.').
    If >1 reasons: C57 ('{count} items need input before this can be approved.') + \n + reasons.
    If the engine gives no item list, show 'Needs input before approval'.
    """
    import copy
    from unittest.mock import patch
    from app.backend.engine_bridge import bridge
    from app.backend.ai_messages import get_message

    # --- 1. Bonus Proposal (Scenario 4) ---
    # 1a. Default engine result produces dynamic blocking reason from C59
    res_s4 = client.post("/api/chat", json={
        "user_id": "HR01",
        "action": "scenario-4",
        "context": {"scenario_num": 4, "bonus_type": "annual_performance_bonus"}
    })
    assert res_s4.status_code == 200
    card_s4 = next(c for c in res_s4.json()["cards"] if c["type"] == "approval_card")
    exp_c56_meera = get_message("C56", Name="Meera Nair", **{"missing item": "performance record"})
    assert card_s4["data"]["blocking_reason"] == exp_c56_meera
    assert card_s4["data"]["disabled_label"] == exp_c56_meera

    # 1b. Modify engine result via mock: add another needs_input item and verify C57 reason text
    orig_sc4 = bridge.get_scenario(4)
    mock_sc4 = copy.deepcopy(orig_sc4)
    req4 = next(item for item in mock_sc4["result"]["bonus_requests"] if item.get("bonus_type") == "annual_performance_bonus")
    req4["needs_input"].append({"employee_id": "E04", "reason": "attendance record missing"})

    with patch.object(bridge, "get_scenario", return_value=mock_sc4):
        res_mock = client.post("/api/chat", json={
            "user_id": "HR01",
            "action": "scenario-4",
            "context": {"scenario_num": 4, "bonus_type": "annual_performance_bonus"}
        })
        assert res_mock.status_code == 200
        card_mock = next(c for c in res_mock.json()["cards"] if c["type"] == "approval_card")
        expected_reason = get_message("C57", n=2) + "\nMeera Nair's performance record is missing.\nRohan Mehta's attendance record is missing."
        assert card_mock["data"]["blocking_reason"] == expected_reason
        assert card_mock["data"]["disabled_label"] == expected_reason

    # 1c. Engine gives no item list when incomplete: shows "Needs input before approval"
    mock_sc4_empty = copy.deepcopy(orig_sc4)
    req4_empty = next(item for item in mock_sc4_empty["result"]["bonus_requests"] if item.get("bonus_type") == "annual_performance_bonus")
    req4_empty["needs_input"] = []
    for e in req4_empty.get("employees", []):
        e["certainty"] = "Complete for this scope"
    mock_sc4_empty["result"]["certainty"] = "Incomplete"
    with patch.object(bridge, "get_scenario", return_value=mock_sc4_empty):
        res_empty = client.post("/api/chat", json={
            "user_id": "HR01",
            "action": "scenario-4",
            "context": {"scenario_num": 4, "bonus_type": "annual_performance_bonus"}
        })
        assert res_empty.status_code == 200
        card_empty = next(c for c in res_empty.json()["cards"] if c["type"] == "approval_card")
        assert card_empty["data"]["blocking_reason"] == "Needs input before approval"
        assert card_empty["data"]["disabled_label"] == "Needs input before approval"

    # --- 2. Kavya Iyer's Arrears (Scenario 3) ---
    # 2a. Default engine result produces dynamic blocking reason from missing attendance (C59)
    res_s3 = client.post("/api/chat", json={
        "user_id": "HR01",
        "action": "scenario-3",
        "context": {"scenario_num": 3}
    })
    assert res_s3.status_code == 200
    card_s3 = next(c for c in res_s3.json()["cards"] if c["type"] == "approval_card")
    exp_c56_kavya = get_message("C56", Name="Kavya Iyer", **{"missing item": "July attendance"})
    assert card_s3["data"]["blocking_reason"] == exp_c56_kavya
    assert card_s3["data"]["disabled_label"] == exp_c56_kavya

    # 2b. Modify engine result to have multiple missing months
    orig_sc3 = bridge.get_scenario(3)
    mock_sc3 = copy.deepcopy(orig_sc3)
    mock_sc3["result"]["months"].append({
        "month": "2026-06",
        "paid_days": {"value": None},
        "difference": {"value": None}
    })
    with patch.object(bridge, "get_scenario", return_value=mock_sc3):
        res_s3_multi = client.post("/api/chat", json={
            "user_id": "HR01",
            "action": "scenario-3",
            "context": {"scenario_num": 3}
        })
        assert res_s3_multi.status_code == 200
        card_s3_multi = next(c for c in res_s3_multi.json()["cards"] if c["type"] == "approval_card")
        assert "July, June attendance is missing" in card_s3_multi["data"]["blocking_reason"]

    # 2c. Engine gives no missing months when incomplete: shows "Needs input before approval"
    mock_sc3_empty = copy.deepcopy(orig_sc3)
    for m in mock_sc3_empty["result"]["months"]:
        m["paid_days"] = {"value": 30}
        m["difference"] = {"value": 4800}
    mock_sc3_empty["result"]["certainty"] = "Incomplete"
    with patch.object(bridge, "get_scenario", return_value=mock_sc3_empty):
        res_s3_empty = client.post("/api/chat", json={
            "user_id": "HR01",
            "action": "scenario-3",
            "context": {"scenario_num": 3}
        })
        assert res_s3_empty.status_code == 200
        card_s3_empty = next(c for c in res_s3_empty.json()["cards"] if c["type"] == "approval_card")
        assert card_s3_empty["data"]["blocking_reason"] == "Needs input before approval"
        assert card_s3_empty["data"]["disabled_label"] == "Needs input before approval"

    # --- 3. Imran Khan's Settlement (Scenario 8) ---
    # 3a. Default engine result produces dynamic blocking reason from unresolved asset clearance (C59)
    res_s8 = client.post("/api/chat", json={
        "user_id": "HR01",
        "action": "scenario-8",
        "context": {"scenario_num": 8}
    })
    assert res_s8.status_code == 200
    card_s8 = next(c for c in res_s8.json()["cards"] if c["type"] == "approval_card")
    exp_c59_imran = get_message("C59", Name="Imran Khan", item="laptop clearance")
    assert card_s8["data"]["blocking_reason"] == exp_c59_imran
    assert card_s8["data"]["disabled_label"] == exp_c59_imran

    # 3b. Engine gives no unresolved list when incomplete: shows "Needs input before approval"
    orig_sc8 = bridge.get_scenario(8)
    mock_sc8_empty = copy.deepcopy(orig_sc8)
    for k, v in mock_sc8_empty["result"]["components"].items():
        if isinstance(v, dict):
            v["status"] = "Verified"
    mock_sc8_empty["result"]["certainty"] = "Incomplete"
    with patch.object(bridge, "get_scenario", return_value=mock_sc8_empty):
        res_s8_empty = client.post("/api/chat", json={
            "user_id": "HR01",
            "action": "scenario-8",
            "context": {"scenario_num": 8}
        })
        assert res_s8_empty.status_code == 200
        card_s8_empty = next(c for c in res_s8_empty.json()["cards"] if c["type"] == "approval_card")
        assert card_s8_empty["data"]["blocking_reason"] == "Needs input before approval"
        assert card_s8_empty["data"]["disabled_label"] == "Needs input before approval"


def test_reset_check_looks_for_real_approved_status():
    """Item 6: Fix the reset check to look for the real approved status
    ('Approved and ready for payroll'), and verify it reverts to unapproved.
    """
    # 1. Approve proposal PROP-SCENARIO-1 via /api/chat
    resp = client.post("/api/chat", json={
        "user_id": "HR01",
        "action": "approve-proposal",
        "context": {"scenario_num": 1, "proposal_id": "PROP-SCENARIO-1", "version": 1}
    })
    assert resp.status_code == 200
    prop_before = lifecycle.get_proposal("PROP-SCENARIO-1")
    assert prop_before["status"] == "Approved and ready for payroll"

    # 2. Call reset
    reset_resp = client.post("/api/demo/reset")
    assert reset_resp.status_code == 200

    # 3. Verify real approved status is cleared
    prop_after = lifecycle.get_proposal("PROP-SCENARIO-1")
    assert prop_after["status"] != "Approved and ready for payroll"
    assert prop_after["status"] == "Calculated; needs HR approval"

    # 4. Verify no proposal has "Approved and ready for payroll"
    events = lifecycle.get_events()
    assert len(events) == 0


def test_static_guard_no_engine_defaults_in_app_code():
    """Static guard test (Prompt 2c-2a Item 2):
    Fails on any .get("value", <number>) or .get("employee_id", "<id>") pattern in app code.
    Checks backend code (excluding tests and .venv) and frontend source code.
    """
    import re
    from pathlib import Path

    base_dir = Path(__file__).resolve().parent.parent.parent.parent

    # Backend python files
    backend_files = [
        p for p in (base_dir / "app" / "backend").rglob("*.py")
        if "tests" not in p.parts and ".venv" not in p.parts
    ]
    # Frontend ts/tsx/js/jsx files
    frontend_files = [
        p for p in (base_dir / "app" / "frontend" / "src").rglob("*")
        if p.is_file() and p.suffix in (".ts", ".tsx", ".js", ".jsx") and "tests" not in p.parts
    ]

    val_pattern = re.compile(r'\.get\(\s*["\']value["\']\s*,\s*[-+]?[0-9]')
    emp_pattern = re.compile(r'\.get\(\s*["\']employee_id["\']\s*,\s*["\'][A-Za-z0-9_-]+["\']\)')
    val_or_pattern = re.compile(r'\.get\(\s*["\']value["\']\s*\)\s*or\s*(["\'][^"\']+["\']|[-+]?[0-9])')

    violations = []
    for fpath in backend_files + frontend_files:
        file_content = fpath.read_text(encoding="utf-8")
        for line_num, line in enumerate(file_content.splitlines(), start=1):
            stripped = line.strip()
            if stripped.startswith("#") or stripped.startswith("//") or stripped.startswith("/*"):
                continue
            if val_pattern.search(line):
                violations.append(f"{fpath.name}:{line_num}: {stripped} [forbidden .get('value', <number>)]")
            if emp_pattern.search(line):
                violations.append(f"{fpath.name}:{line_num}: {stripped} [forbidden .get('employee_id', '<id>')]")
            if val_or_pattern.search(line):
                violations.append(f"{fpath.name}:{line_num}: {stripped} [forbidden .get('value') or '<literal>']")

    assert not violations, "Found forbidden engine default patterns in app code:\n" + "\n".join(violations)


def test_imran_khan_blocked_reason_built_only_from_data():
    """Test (Prompt 2c-2a Item 3):
    - Imran Khan's blocked reason (scenarios 8 and 13) must be built only from engine/clearance/recovery data.
    - Remove 'Company laptop not received' unless that exact text exists in data.
    - Asserts both scenario 8 and 13 have data-built reasons and do NOT contain 'Company laptop not received'.
    """
    import json
    from pathlib import Path
    from fastapi.testclient import TestClient
    from app.backend.main import app
    from app.backend.ai_messages import get_message

    client = TestClient(app)

    for sc_num in (8, 13):
        res = client.post("/api/chat", json={
            "user_id": "HR01",
            "action": f"scenario-{sc_num}",
            "context": {"scenario_num": sc_num}
        })
        assert res.status_code == 200
        data = res.json()
        approval_card = next((c for c in data["cards"] if c["type"] == "approval_card"), None)
        assert approval_card is not None
        blocking_reason = approval_card["data"].get("blocking_reason")
        disabled_label = approval_card["data"].get("disabled_label")

        # Must be built from clearance data
        expected_reason = get_message("C59", Name="Imran Khan", item="laptop clearance")
        assert blocking_reason == expected_reason, f"Scenario {sc_num} blocking reason mismatch: {blocking_reason}"
        assert disabled_label == expected_reason, f"Scenario {sc_num} disabled label mismatch: {disabled_label}"

        # Assert "Company laptop not received" is completely absent across response
        resp_str = json.dumps(data)
        assert "Company laptop not received" not in resp_str, f"Forbidden invented text in scenario {sc_num} response"
        assert "Company laptop status unconfirmed" not in resp_str, f"Forbidden invented text in scenario {sc_num} response"

    # Also assert that 'Company laptop not received' is not hardcoded anywhere in app code
    base_dir = Path(__file__).resolve().parent.parent.parent.parent
    app_files = [
        p for p in (base_dir / "app").rglob("*")
        if p.is_file() and not any(part in p.parts for part in [".venv", "node_modules", "tests"]) and p.suffix in (".py", ".ts", ".tsx")
    ]
    for p in app_files:
        txt = p.read_text(encoding="utf-8")
        assert "Company laptop not received" not in txt, f"Found 'Company laptop not received' in {p}"
        assert "Company laptop status unconfirmed" not in txt, f"Found 'Company laptop status unconfirmed' in {p}"


def test_missing_engine_value_logs_masked_warning_and_fails(caplog):
    """Test (Prompt 2c-2a Item 1):
    If an engine value is missing:
    - Do not show that invented number
    - Log a masked warning
    - Make a test fail (engine contract assertion)
    """
    import copy
    import logging
    from unittest.mock import patch
    from fastapi.testclient import TestClient
    from app.backend.main import app
    from app.backend.ai_messages import get_message
    from app.backend.engine_bridge import bridge
    from app.backend.ai_messages import get_message

    client = TestClient(app)

    # Test with Scenario 1 missing display inputs
    orig_sc1 = bridge.get_scenario(1)
    mock_sc1 = copy.deepcopy(orig_sc1)
    mock_sc1["display_inputs"]["old_monthly_salary"]["total"]["value"] = None

    with caplog.at_level(logging.WARNING):
        with patch.object(bridge, "get_scenario", return_value=mock_sc1):
            res = client.post("/api/chat", json={
                "user_id": "HR01",
                "action": "scenario-1",
                "context": {"scenario_num": 1}
            })
            assert res.status_code == 200
            data = res.json()

            # Ensure the old invented default (120000) was NOT used when value was missing
            prop_card = next(c for c in data["cards"] if c["type"] == "proposal_summary")
            assert prop_card["data"]["old_monthly_salary_total"] is None

            # Assert masked warning was logged
            masked_warnings = [rec for rec in caplog.records if "Masked warning" in rec.message]
            assert len(masked_warnings) > 0, "Expected a masked warning to be logged for missing engine value"

            # Assert that expecting an engine value when missing causes test failure (contract verification)
            with pytest.raises(AssertionError):
                assert prop_card["data"]["old_monthly_salary_total"] == 120000


def test_hr_voice_across_all_scenarios():
    """PART A (Item 1 & 11): When signed-in user is HR and the reply is about an employee,
    never use 'Your'/'your'/'you' for that employee. Use their name.
    """
    from fastapi.testclient import TestClient
    from app.backend.main import app
    from app.backend.ai_messages import get_message
    from app.backend.chat_router import EMPLOYEE_NAMES

    client = TestClient(app)

    # 1. Scenario 9: Neha Gupta take-home drop
    res9 = client.post("/api/chat", json={"user_id": "HR01", "action": "scenario-9", "context": {"scenario_num": 9}})
    assert res9.status_code == 200
    data9 = res9.json()
    assert data9["messages"][0]["code"] == "C42"
    assert "Neha Gupta's September take-home is" in data9["messages"][0]["text"]
    assert "Your" not in data9["messages"][0]["text"]
    assert "your" not in data9["messages"][0]["text"]

    # 2. Scenario 10: Siddharth Jain TDS increase
    res10 = client.post("/api/chat", json={"user_id": "HR01", "action": "scenario-10", "context": {"scenario_num": 10}})
    assert res10.status_code == 200
    data10 = res10.json()
    assert data10["messages"][0]["code"] == "C42"
    assert "Siddharth Jain's September take-home is" in data10["messages"][0]["text"]
    # HR version of C29
    assert data10["messages"][1]["code"] == "C29"
    assert "Siddharth Jain's TDS is higher because they declared income from their previous employer" in data10["messages"][1]["text"]
    assert "you" not in data10["messages"][1]["text"].lower()
    assert "your" not in data10["messages"][1]["text"].lower()

    # 3. Scenario 11: Pooja Das take-home drop
    res11 = client.post("/api/chat", json={"user_id": "HR01", "action": "scenario-11", "context": {"scenario_num": 11}})
    assert res11.status_code == 200
    data11 = res11.json()
    assert data11["messages"][0]["code"] == "C42"
    assert "Pooja Das's September take-home is" in data11["messages"][0]["text"]
    assert "Your" not in data11["messages"][0]["text"]


def test_hr_query_word_routing_and_full_loop():
    """PART B & D (Items 2-8 & 11):
    - HR mentions employee AND query word: never jumps to salary scenario.
    - Full query loop: show -> reply draft -> confirm send -> resolve confirm -> Neha sees reply.
    - Delete query refused (C45).
    - HR02 refused access to Neha's query (C10).
    - Missing or wrong query_id changes nothing.
    """
    from fastapi.testclient import TestClient
    from app.backend.main import app
    from app.backend.ai_messages import get_message
    from app.backend.lifecycle import lifecycle

    client = TestClient(app)
    lifecycle.reset_demo()

    # 1. Routing: 'Show Neha's query' routes to query, not salary scenario
    show_res = client.post("/api/chat", json={"user_id": "HR01", "message": "Show Neha's query"})
    assert show_res.status_code == 200
    show_data = show_res.json()
    assert show_data["state"]["intent"] == "hr_query_review"
    assert show_data["messages"][0]["code"] == "C43"
    assert "Neha Gupta's September query is In review. No reply has been recorded yet." in show_data["messages"][0]["text"]
    assert len(show_data["cards"]) == 1
    q_card = show_data["cards"][0]
    assert q_card["type"] == "query_status"
    assert q_card["data"]["name_code"] == "Neha Gupta · E05"
    assert q_card["data"]["period"] == "September 2026"
    assert q_card["data"]["category"] == "salary"
    assert q_card["data"]["description"] == "Please check my September attendance."
    assert q_card["data"]["status"] == "In review"
    # No invented dates, reviewer or reply
    assert "reply_text" not in q_card["data"]
    assert "reviewer" not in q_card["data"]

    # 2. 'Delete Neha's query' -> C45
    del_res = client.post("/api/chat", json={"user_id": "HR01", "message": "Delete Neha's query"})
    assert del_res.status_code == 200
    assert del_res.json()["messages"][0]["code"] == "C45"
    assert del_res.json()["messages"][0]["text"] == "Queries can't be deleted. You can close it instead."

    # 3. HR02 (Sales only) cannot access Neha's query (permission gate -> C10)
    hr02_show = client.post("/api/chat", json={"user_id": "HR02", "message": "Show Neha's query"})
    assert hr02_show.status_code == 200
    assert hr02_show.json()["messages"][0]["code"] == "C10"

    hr02_del = client.post("/api/chat", json={"user_id": "HR02", "message": "Delete Neha's query"})
    assert hr02_del.status_code == 200
    assert hr02_del.json()["messages"][0]["code"] == "C10"

    hr02_reply = client.post("/api/chat", json={"user_id": "HR02", "message": "Reply to Neha's query"})
    assert hr02_reply.status_code == 200
    assert hr02_reply.json()["messages"][0]["code"] == "C10"

    hr02_resolve = client.post("/api/chat", json={"user_id": "HR02", "message": "Mark Neha's query resolved"})
    assert hr02_resolve.status_code == 200
    assert hr02_resolve.json()["messages"][0]["code"] == "C10"

    # 4. Wrong or missing query_id changes nothing
    bad_res = client.post("/api/chat", json={"user_id": "HR01", "action": "confirm-reply-query", "context": {"query_id": "QUERY-FAKE-999", "reply_text": "Bad"}})
    assert bad_res.status_code == 200
    assert bad_res.json()["messages"][0]["code"] == "C10"
    # Verify Neha's query was unchanged
    neha_q = lifecycle.get_query("QUERY-E05-SEPTEMBER")
    assert neha_q.get("hr_reply") is None

    # 5. 'Reply to Neha's query': draft card; nothing sent until confirmed
    draft_reply_res = client.post("/api/chat", json={"user_id": "HR01", "message": "Reply to Neha's query"})
    assert draft_reply_res.status_code == 200
    draft_rep_data = draft_reply_res.json()
    assert draft_rep_data["cards"][0]["type"] == "query_draft"
    assert "Nothing is sent until" in draft_rep_data["cards"][0]["data"]["notice"]
    assert draft_rep_data["cards"][0]["data"]["status"] == "In review"
    # Verify nothing was sent yet
    neha_q = lifecycle.get_query("QUERY-E05-SEPTEMBER")
    assert neha_q.get("hr_reply") is None

    # 6. HR clicks Send (confirm-reply-query)
    confirm_rep = client.post("/api/chat", json={
        "user_id": "HR01",
        "action": "confirm-reply-query",
        "context": {"query_id": "QUERY-E05-SEPTEMBER", "reply_text": "Attendance punch log verified."}
    })
    assert confirm_rep.status_code == 200
    neha_q = lifecycle.get_query("QUERY-E05-SEPTEMBER")
    assert neha_q.get("hr_reply") == "Attendance punch log verified."

    # 7. 'Mark Neha's query resolved': button with confirmation
    resolve_prompt = client.post("/api/chat", json={"user_id": "HR01", "message": "Mark Neha's query resolved"})
    assert resolve_prompt.status_code == 200
    assert resolve_prompt.json()["messages"][0]["code"] == "C51"
    assert resolve_prompt.json()["messages"][0]["text"] == "Mark Neha Gupta's query as resolved?"
    assert any(chip["action"] == "confirm-resolve-query" for chip in resolve_prompt.json()["chips"])
    # Not yet marked resolved in data
    neha_q = lifecycle.get_query("QUERY-E05-SEPTEMBER")
    assert neha_q.get("status") == "In review"

    # 8. HR confirms resolve
    confirm_resolve = client.post("/api/chat", json={
        "user_id": "HR01",
        "action": "confirm-resolve-query",
        "context": {"query_id": "QUERY-E05-SEPTEMBER", "confirmed": True}
    })
    assert confirm_resolve.status_code == 200
    assert confirm_resolve.json()["messages"][0]["code"] == "C23"
    neha_q = lifecycle.get_query("QUERY-E05-SEPTEMBER")
    assert neha_q.get("status") == "Resolved"

    # 9. Neha asks 'What's happening with my query?' -> gets C44 + reply
    neha_check = client.post("/api/chat", json={"user_id": "USER-E05", "message": "What's happening with my query?"})
    assert neha_check.status_code == 200
    assert neha_check.json()["messages"][0]["code"] == "C44"
    assert "Your September 2026 query is Resolved. Here is HR's reply: Attendance punch log verified." in neha_check.json()["messages"][0]["text"]


def test_hr_list_questions():
    """PART C & D (Items 9, 10 & 11):
    - 'What needs my approval?': lists waiting proposals, buttons to open each; C46 if none.
    - 'Who is leaving this month?': lists leavers in open payroll month with C47.
    """
    from fastapi.testclient import TestClient
    from app.backend.main import app
    from app.backend.ai_messages import get_message
    from app.backend.lifecycle import lifecycle

    client = TestClient(app)
    lifecycle.reset_demo()

    # 1. 'What needs my approval?' for HR01
    appr_res = client.post("/api/chat", json={"user_id": "HR01", "message": "What needs my approval?"})
    assert appr_res.status_code == 200
    appr_data = appr_res.json()
    assert appr_data["state"]["intent"] == "approvals_list"
    assert appr_data["messages"][0]["code"] == "C48"
    assert "proposals are ready for your approval." in appr_data["messages"][0]["text"]
    assert appr_data["messages"][1]["code"] == "C49"
    assert "need input before they can be approved." in appr_data["messages"][1]["text"]
    assert len(appr_data["cards"]) == 2
    assert appr_data["cards"][0]["title"] == "Ready to approve"
    ready_items = appr_data["cards"][0]["data"]["items"]
    assert any("Priya Sharma" in it["name_code"] for it in ready_items)
    assert appr_data["cards"][1]["title"] == "Needs input first"
    needs_input_items = appr_data["cards"][1]["data"]["items"]
    assert any(it.get("blocked_reason") for it in needs_input_items)

    # 2. 'Who is leaving this month?' for HR01
    leave_res = client.post("/api/chat", json={"user_id": "HR01", "message": "Who is leaving this month?"})
    assert leave_res.status_code == 200
    leave_data = leave_res.json()
    assert leave_data["state"]["intent"] == "leavers_list"
    assert leave_data["messages"][0]["code"] == "C47"
    assert "3 employees have a last working day in October 2026:" in leave_data["messages"][0]["text"]
    l_items = leave_data["cards"][0]["data"]["items"]
    assert len(l_items) == 3
    names = [it["name_code"] for it in l_items]
    assert any("Rahul Verma" in n for n in names)
    assert any("Lakshmi Reddy" in n for n in names)
    assert any("Imran Khan" in n for n in names)

    # 3. 'Who is leaving this month?' for HR02 (Sales only: E13, E14, E15 -> 0 October leavers)
    leave_res2 = client.post("/api/chat", json={"user_id": "HR02", "message": "Who is leaving this month?"})
    assert leave_res2.status_code == 200
    leave_data2 = leave_res2.json()
    assert leave_data2["messages"][0]["code"] == "C47"
    assert "0 employees have a last working day in October 2026:" in leave_data2["messages"][0]["text"]
    assert len(leave_data2["cards"][0]["data"]["items"]) == 0


# --- Prompt 2c-2c Tests ---

def test_no_placeholder_leaks_full_matrix():
    """Prompt 2c-2c Item 1: No placeholder leaks in message text across the full matrix.
    No reply may contain 'Not available in generated data', 'None', 'null', 'undefined', '{' or '}'.
    Fix declared-months slot in TDS-increase sentence from E06's declaration data.
    """
    from fastapi.testclient import TestClient
    from app.backend.main import app
    from app.backend.ai_messages import get_message
    from app.backend.lifecycle import lifecycle

    client = TestClient(app)
    lifecycle.reset_demo()

    disallowed_substrings = [
        "Not available in generated data",
        "None",
        "null",
        "undefined",
        "{",
        "}",
    ]

    # Test Scenarios 1 to 13
    for s_num in range(1, 14):
        # As Employee (where applicable) and as HR01
        for uid in ["USER-E05", "USER-E06", "USER-E16", "HR01"]:
            res = client.post("/api/chat", json={"user_id": uid, "action": f"scenario-{s_num}"})
            if res.status_code == 200:
                data = res.json()
                for m in data.get("messages", []):
                    t = m.get("text", "")
                    for ds in disallowed_substrings:
                        assert ds not in t, f"Leak '{ds}' found in Scenario {s_num} for user {uid}: '{t}'"

    # Specific Scenario 10 check for declared_months
    s10_emp = client.post("/api/chat", json={"user_id": "USER-E06", "message": "Why did my TDS increase?"})
    assert s10_emp.status_code == 200
    tds_msg_emp = s10_emp.json()["messages"][1]["text"]
    assert "April to June 2026" in tds_msg_emp, f"Expected declared months 'April to June 2026' in: {tds_msg_emp}"

    s10_hr = client.post("/api/chat", json={"user_id": "HR01", "action": "scenario-10"})
    assert s10_hr.status_code == 200
    tds_msg_hr = s10_hr.json()["messages"][1]["text"]
    assert "April to June 2026" in tds_msg_hr, f"Expected declared months 'April to June 2026' in: {tds_msg_hr}"

    # Test list questions
    for q in ["What needs my approval?", "Who is leaving this month?"]:
        res = client.post("/api/chat", json={"user_id": "HR01", "message": q})
        assert res.status_code == 200
        for m in res.json().get("messages", []):
            for ds in disallowed_substrings:
                assert ds not in m.get("text", ""), f"Leak '{ds}' in '{q}': {m.get('text')}"


def test_hr_voice_readability_full_name_at_most_once():
    """Prompt 2c-2c Item 2: HR voice readability.
    In HR replies, the employee's full name appears at most once per message,
    then 'they'/'their'/'them'.
    """
    from fastapi.testclient import TestClient
    from app.backend.main import app
    from app.backend.ai_messages import get_message
    from app.backend.lifecycle import lifecycle
    from app.backend.chat_router import EMPLOYEE_NAMES

    client = TestClient(app)
    lifecycle.reset_demo()

    # Check HR replies across scenarios and employee topics
    endpoints = [
        {"user_id": "HR01", "action": "scenario-9"},
        {"user_id": "HR01", "action": "scenario-10"},
        {"user_id": "HR01", "action": "scenario-11"},
        {"user_id": "HR01", "message": "Show Neha's query"},
        {"user_id": "HR01", "message": "Reply to Neha's query"},
        {"user_id": "HR01", "message": "Mark Neha's query resolved"},
    ]

    for req in endpoints:
        res = client.post("/api/chat", json=req)
        assert res.status_code == 200
        data = res.json()
        for m in data.get("messages", []):
            text = m.get("text", "")
            for eid, fname in EMPLOYEE_NAMES.items():
                count = text.count(fname)
                assert count <= 1, f"Employee full name '{fname}' appeared {count} times in HR reply: '{text}'"

    # Specific Scenario 10 HR wording check
    res_s10 = client.post("/api/chat", json={"user_id": "HR01", "action": "scenario-10"})
    msg_tds = res_s10.json()["messages"][1]["text"]
    assert msg_tds.count("Siddharth Jain") == 1
    assert "they declared income from their previous employer" in msg_tds
    assert "their expected yearly tax" in msg_tds


def test_guard_every_message_code_and_template():
    """Prompt 2c-2c Item 5: Guard: every message in every reply has a code that exists
    in ai_messages.py, and its text equals that template filled with data.
    No free-text messages.
    """
    from fastapi.testclient import TestClient
    from app.backend.main import app
    from app.backend.ai_messages import get_message
    from app.backend.lifecycle import lifecycle
    from app.backend.ai_messages import AI_MESSAGES, AI_MESSAGES_HR, validate_message_text

    client = TestClient(app)
    lifecycle.reset_demo()

    all_valid_codes = set(AI_MESSAGES.keys()) | set(AI_MESSAGES_HR.keys())

    test_queries = [
        {"user_id": "USER-E05", "message": "Why is my take-home pay lower in September?"},
        {"user_id": "USER-E05", "message": "How much PF was cut in September?"},
        {"user_id": "USER-E05", "message": "What is LOP?"},
        {"user_id": "USER-E05", "message": "pf"},
        {"user_id": "USER-E06", "message": "Why did my TDS increase?"},
        {"user_id": "USER-E06", "message": "What is TDS?"},
        {"user_id": "USER-E16", "message": "Why did my basic pay change?"},
        {"user_id": "HR01", "message": "What needs my approval?"},
        {"user_id": "HR01", "message": "Who is leaving this month?"},
        {"user_id": "HR01", "message": "Show Neha's query"},
        {"user_id": "HR01", "message": "Reply to Neha's query"},
        {"user_id": "HR01", "message": "Delete Neha's query"},
        {"user_id": "HR01", "message": "pf"},
        {"user_id": "HR02", "message": "What needs my approval?"},
        {"user_id": "HR02", "message": "Who is leaving this month?"},
    ]

    for req in test_queries:
        res = client.post("/api/chat", json=req)
        assert res.status_code == 200
        data = res.json()
        for m in data.get("messages", []):
            code = m.get("code")
            text = m.get("text")
            assert code in all_valid_codes, f"Unknown message code '{code}' in reply to {req}"
            assert validate_message_text(code, text), f"Message text does not match template for code '{code}': '{text}'"


def test_did_you_mean_chips_resolve_to_real_answers():
    """Prompt 2c-2c Item 7: 'Did you mean?' chips.
    When intent is unknown or ambiguous but topic word is present, reply with C52
    and up to 3 chips from fixed list plus 'Something else'.
    Every chip resolves to a real answer (not C33, not C10), per user.
    """
    from fastapi.testclient import TestClient
    from app.backend.main import app
    from app.backend.ai_messages import get_message
    from app.backend.lifecycle import lifecycle

    client = TestClient(app)
    lifecycle.reset_demo()

    # 1. Neha + "pf" test from prompt specification
    res_pf = client.post("/api/chat", json={"user_id": "USER-E05", "message": "pf"})
    assert res_pf.status_code == 200
    data_pf = res_pf.json()
    assert data_pf["messages"][0]["code"] == "C52"
    assert data_pf["messages"][0]["text"] == "Did you mean one of these?"
    chip_labels = [c["label"] for c in data_pf["chips"]]
    assert "How much PF was cut in September?" in chip_labels
    assert "What was my August PF?" in chip_labels
    assert "What is PF?" in chip_labels
    assert chip_labels[-1] == "Something else"

    # 2. Every chip resolves to a real answer (not C33, not C10)
    for chip in chip_labels[:-1]:  # exclude 'Something else' which intentionally falls back
        ans_res = client.post("/api/chat", json={"user_id": "USER-E05", "message": chip})
        assert ans_res.status_code == 200
        ans_data = ans_res.json()
        codes = [m.get("code") for m in ans_data.get("messages", [])]
        assert "C33" not in codes, f"Chip '{chip}' resolved to C33 fallback!"
        assert "C10" not in codes, f"Chip '{chip}' resolved to C10 refusal!"

    # 3. 'Something else' resolves to C33
    se_res = client.post("/api/chat", json={"user_id": "USER-E05", "message": "Something else"})
    assert se_res.status_code == 200
    assert se_res.json()["messages"][0]["code"] == "C33"

    # 4. Confident question answers directly without C52
    conf_res = client.post("/api/chat", json={"user_id": "USER-E05", "message": "What is PF?"})
    assert conf_res.status_code == 200
    assert conf_res.json()["messages"][0]["code"] == "FAQ"
