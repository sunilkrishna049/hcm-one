"""Pytest suite for HCM One backend."""
import pytest
from fastapi.testclient import TestClient

from app.backend.main import app
from app.backend.auth import set_active_demo_user
from app.backend.lifecycle import lifecycle

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_teardown():
    # Reset demo before each test
    lifecycle.reset_demo()
    set_active_demo_user("HR01")
    yield
    lifecycle.reset_demo()
    set_active_demo_user("HR01")


def test_login_and_me():
    res = client.post("/api/auth/login", json={"user_id": "USER-E05"})
    assert res.status_code == 200
    assert res.json()["user_id"] == "USER-E05"

    me = client.get("/api/me")
    assert me.status_code == 200
    assert me.json()["user_id"] == "USER-E05"
    assert me.json()["role"] == "Employee"


def test_permission_guard_scenario_12():
    # Login as Employee USER-E05 (Neha)
    client.post("/api/auth/login", json={"user_id": "USER-E05"})
    res = client.get("/api/scenarios/scenario-12")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "Permission denied"
    assert "I cannot provide that information" in data["message"]
    # Check no target name or ID leaked
    assert "Priya" not in str(data["display_inputs"])


def test_permission_guard_employee_cannot_access_other():
    # Login as Employee USER-E05 (Neha)
    client.post("/api/auth/login", json={"user_id": "USER-E05"})
    # Try accessing scenario-01 (Priya E01)
    res = client.get("/api/scenarios/scenario-01")
    assert res.status_code == 403
    assert "I cannot provide that information" in res.json()["detail"]["message"]


def test_permission_guard_hr02_sales_only():
    # Login as HR02 (Karan Bose, Sales only: E13, E14, E15)
    client.post("/api/auth/login", json={"user_id": "HR02"})

    # Non-sales employee E01 (Scenario 1) should be blocked
    res_e01 = client.get("/api/scenarios/scenario-01")
    assert res_e01.status_code == 403

    # Sales employee E13 should succeed
    res_e13 = client.post("/api/proposals/bonus/calculate-scope", json={
        "bonus_type": "quarterly_sales_incentive",
        "period": "Q2 2026-27",
        "selected_employee_ids": ["E13"]
    })
    assert res_e13.status_code == 200
    assert res_e13.json()["aggregates"]["eligible_count"]["value"] == 1


def test_approval_guard_complete_scope_succeeds():
    # Scenario 1 is complete
    client.post("/api/auth/login", json={"user_id": "HR01"})
    # First get scenario to initialize proposal
    init_res = client.get("/api/scenarios/scenario-01")
    assert init_res.status_code == 200
    prop_id = "PROP-HIKE-E01"

    # Approve version 1
    appr_res = client.post(f"/api/proposals/{prop_id}/approve", json={"version": 1})
    assert appr_res.status_code == 200
    assert appr_res.json()["status"] == "Approved and ready for payroll"
    assert "Approving records this version" in appr_res.json()["message"]


def test_approval_guard_stale_version_rejected():
    client.post("/api/auth/login", json={"user_id": "HR01"})
    client.get("/api/scenarios/scenario-01")
    prop_id = "PROP-HIKE-E01"

    # Edit proposal to bump to version 2
    edit_res = client.post(f"/api/proposals/{prop_id}/edit", json={
        "line": "requested_hike_percentage",
        "proposed_value": 15,
        "reason": "Performance revision"
    })
    assert edit_res.status_code == 200
    assert edit_res.json()["version"] == 2

    # Now attempt to approve version 1 (stale!)
    stale_appr = client.post(f"/api/proposals/{prop_id}/approve", json={"version": 1})
    assert stale_appr.status_code == 400
    assert stale_appr.json()["detail"]["code"] == "C25"
    assert "This proposal changed after you reviewed it" in stale_appr.json()["detail"]["message"]

    # Approving current version 2 succeeds
    fresh_appr = client.post(f"/api/proposals/{prop_id}/approve", json={"version": 2})
    assert fresh_appr.status_code == 200


def test_approval_guard_incomplete_scope_blocked():
    client.post("/api/auth/login", json={"user_id": "HR01"})
    # Scenario 3 is incomplete (July attendance missing)
    sc3 = client.get("/api/scenarios/scenario-03")
    assert sc3.status_code == 200
    prop_id = "PROP-HIKE-E03"

    # Attempt to approve incomplete proposal
    appr_res = client.post(f"/api/proposals/{prop_id}/approve", json={"version": 1})
    assert appr_res.status_code == 400
    assert "Incomplete or unverified scope cannot be approved" in appr_res.json()["detail"]["error"]


def test_bonus_selected_scope_totals():
    client.post("/api/auth/login", json={"user_id": "HR01"})
    res = client.post("/api/proposals/bonus/calculate-scope", json={
        "bonus_type": "quarterly_sales_incentive",
        "period": "Q2 2026-27",
        "selected_employee_ids": ["E13", "E14"]
    })
    assert res.status_code == 200
    aggs = res.json()["aggregates"]
    # Calculated by engine, not frontend
    assert aggs["eligible_count"]["value"] == 2
    assert aggs["group_total_gross"]["value"] == 60000


def test_query_confirmation_and_append():
    client.post("/api/auth/login", json={"user_id": "USER-E05"})
    draft_data = {
        "employee_id": "E05",
        "category": "salary",
        "months": ["2026-09"],
        "description": "Disputing my LOP deduction",
        "evidence": [{"type": "payslip", "record_id": "PAY-E05-2026-09"}]
    }

    # Cannot send without confirmation
    unconfirmed = client.post("/api/queries/confirm-send", json={
        "draft": draft_data,
        "add_or_new": "new",
        "confirmed": False
    })
    assert unconfirmed.status_code == 400

    # Confirmed send as new query
    confirmed = client.post("/api/queries/confirm-send", json={
        "draft": draft_data,
        "add_or_new": "new",
        "confirmed": True
    })
    assert confirmed.status_code == 200
    assert confirmed.json()["status"] == "Sent"
    new_qid = confirmed.json()["query"]["query_id"]

    # Append to existing query
    append_res = client.post("/api/queries/confirm-send", json={
        "draft": {
            "employee_id": "E05",
            "description": "Additional note on attendance"
        },
        "add_or_new": "add",
        "target_query_id": "QUERY-E05-SEPTEMBER",
        "confirmed": True
    })
    assert append_res.status_code == 200
    assert append_res.json()["query"]["query_id"] == "QUERY-E05-SEPTEMBER"
    assert "Additional note" in append_res.json()["query"]["description"]


def test_reset_demo():
    # Make some runtime changes: approve a proposal and check real approved status
    client.post("/api/auth/login", json={"user_id": "HR01"})
    client.post(
        "/api/chat",
        json={"user_id": "HR01", "action": "approve-proposal", "context": {"scenario_num": 1, "proposal_id": "PROP-SCENARIO-1", "version": 1}}
    )
    prop_before = lifecycle.get_proposal("PROP-SCENARIO-1")
    assert prop_before["status"] == "Approved and ready for payroll"

    # Call reset
    reset_res = client.post("/api/demo/reset")
    assert reset_res.status_code == 200

    # Check that events are cleared
    events = lifecycle.get_events()
    assert len(events) == 0

    # Check that real approved status is cleared
    prop_after = lifecycle.get_proposal("PROP-SCENARIO-1")
    assert prop_after["status"] != "Approved and ready for payroll"
    assert prop_after["status"] == "Calculated; needs HR approval"


def test_scenarios_exact_numbers_and_c29():
    client.post("/api/auth/login", json={"user_id": "HR01"})

    # Scenario 1 (Priya E01): Net arrears in totals
    sc1 = client.get("/api/scenarios/scenario-01").json()
    assert sc1["scenario"]["result"]["totals"]["gross_arrears"]["value"] == 71200
    assert sc1["scenario"]["result"]["totals"]["net_arrears"]["value"] == 67476
    assert sc1["scenario"]["display_inputs"]["proposed_monthly_salary"]["total"]["value"] == 132000

    # Scenario 6 (Rahul E10 Gratuity)
    sc6 = client.get("/api/scenarios/scenario-06").json()
    assert sc6["scenario"]["result"]["components"]["gratuity"]["amount"]["value"] == 201923
    assert sc6["scenario"]["result"]["certainty"] == "Complete for this scope"

    # Scenario 9 (Neha E05 LOP)
    client.post("/api/auth/login", json={"user_id": "USER-E05"})
    sc9 = client.get("/api/scenarios/scenario-09").json()
    assert sc9["scenario"]["result"]["after"]["net_pay"]["value"] == 42780
    assert sc9["scenario"]["result"]["reasons"][0]["type"] == "LOP"

    # Scenario 10 (Siddharth E06 Prior Employer TDS & C29)
    client.post("/api/auth/login", json={"user_id": "USER-E06"})
    sc10 = client.get("/api/scenarios/scenario-10").json()
    declared_range = sc10["scenario"]["display_inputs"]["declared_month_range"]["value"]
    assert declared_range == "2026-04 to 2026-06"
    assert sc10["scenario"]["result"]["reasons"][0]["type"] == "TDS change"
    assert any("DECL-E06-PREVIOUS-EMPLOYER" in str(ref) for ref in sc10["scenario"]["result"]["reasons"][0]["source_references"])

    # Verbatim C29 test with slot interpolation
    from app.backend.ai_messages import get_message
    c29 = get_message("C29", declared_months=declared_range)
    assert "Your TDS is higher because you declared income from your previous employer for 2026-04 to 2026-06" in c29


