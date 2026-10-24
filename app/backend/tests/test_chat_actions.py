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

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_store():
    lifecycle.reset_demo()


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

    # Verify C04 message
    assert any(m["code"] == "C04" for m in data["messages"])
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
    """HR role gets HR chips only; HR never sees 'Why is my take-home pay lower in September?'."""
    # HR fallback
    hr_resp = client.post(
        "/api/chat",
        json={"user_id": "HR01", "message": "unrecognized question xyzz123"},
    )
    assert hr_resp.status_code == 200
    hr_labels = [c["label"] for c in hr_resp.json().get("chips", [])]
    assert "Why is my take-home pay lower in September?" not in hr_labels
    assert "Prepare Priya Sharma hike" in hr_labels

    # Employee fallback
    emp_resp = client.post(
        "/api/chat",
        json={"user_id": "USER-E05", "message": "unrecognized question xyzz123"},
    )
    assert emp_resp.status_code == 200
    emp_labels = [c["label"] for c in emp_resp.json().get("chips", [])]
    assert "Why is my take-home pay lower in September?" in emp_labels
    assert "Prepare Priya Sharma hike" not in emp_labels


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
