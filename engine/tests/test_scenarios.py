"""One behavioral test for each BRD v1.2 scenario, including blocked results."""
from payroll.core import COMPLETE, INCOMPLETE, UNVERIFIED


def test_scenario_01_hike_with_lop(scenarios):
    result = scenarios[1]
    june = next(row for row in result["months"] if row["month"] == "2026-06")
    assert june["paid_days"]["value"] == 28
    assert june["old"]["gross"]["value"] == 112000
    assert june["revised"]["gross"]["value"] == 123200
    assert june["difference"]["value"] == 11200
    assert result["totals"]["gross_arrears"]["value"] == 71200
    assert june["pf_change"]["employee"]["certainty"] == COMPLETE
    assert june["pf_change"]["employee"]["value"] == 0
    assert result["totals"]["net_arrears"]["value"] == 67476
    assert result["totals"]["tds_impact"]["value"] == 3724
    assert result["certainty"] == COMPLETE


def test_scenario_02_hike_crossing_pf_change(scenarios):
    result = scenarios[2]
    september = next(row for row in result["months"] if row["month"] == "2026-09")
    old, new = september["old_pf"], september["revised_pf"]
    assert [segment["days"]["value"] for segment in old["segments"]] == [16, 14]
    assert [segment["start"]["value"] for segment in old["segments"]] == ["2026-09-01", "2026-09-17"]
    assert old["employee"]["value"] == 1968
    assert new["employee"]["value"] == 2069
    assert september["pf_change"]["employee"]["value"] == 101
    assert result["totals"]["gross_arrears"]["value"] == 7200
    assert result["totals"]["tds_impact"]["certainty"] == COMPLETE
    assert result["totals"]["tds_impact"]["value"] == 0


def test_scenario_03_hike_missing_attendance(scenarios):
    result = scenarios[3]
    july = result["months"][0]
    assert july["month"] == "2026-07"
    assert july["difference"]["value"] is None
    assert july["difference"]["certainty"] == INCOMPLETE
    assert result["totals"]["gross_arrears"]["value"] is None
    # Known August earnings are retained rather than hiding the entire proposal.
    assert result["months"][1]["difference"]["value"] == 4800


def test_scenario_04_team_bonus(scenarios):
    requests = scenarios[4]["bonus_requests"]
    annual, sales = requests
    assert annual["eligible"] == ["E01", "E03", "E04", "E07"]
    assert annual["not_eligible"] == [{"employee_id": "E08", "reason": "On notice at the time of calculation"}]
    assert annual["needs_input"] == [{"employee_id": "E09", "reason": "Performance record missing"}]
    assert annual["known_eligible_gross"]["value"] == 213929
    assert sales["eligible"] == ["E13", "E14", "E15"]
    assert sales["known_eligible_gross"]["value"] == 120000
    e07 = next(row for row in annual["employees"] if row["employee_id"] == "E07")
    assert e07["eligible_days"]["value"] == 151
    assert e07["period_days"]["value"] == 365
    assert e07["tds_impact"]["certainty"] == COMPLETE
    assert e07["tds_impact"]["value"] == 0
    assert scenarios[4]["certainty"] == INCOMPLETE  # E03 payroll and E09 performance are still missing.


def test_scenario_05_missing_performance(scenarios):
    employee = scenarios[5]["employee"]
    assert employee["employee_id"] == "E09"
    assert employee["eligibility"] == "Needs input"
    assert employee["reason"] == "Performance record missing"
    assert employee["amount"]["value"] is None
    assert employee["amount"]["certainty"] == INCOMPLETE


def test_scenario_06_eligible_settlement(scenarios):
    result = scenarios[6]
    assert result["components"]["gratuity"]["amount"]["value"] == 201923
    assert result["components"]["final_month_salary"]["classification"] == "separation wages"
    assert result["components"]["leave_encashment"]["classification"] == "paid with separation wages"
    assert result["certainty"] == COMPLETE
    assert result["final_net"]["value"] == 332256
    assert result["proposal_status"] == "Needs HR approval; no payment generated"


def test_scenario_07_below_service_minimum(scenarios):
    gratuity = scenarios[7]["components"]["gratuity"]
    assert gratuity["status"] == "Not applicable"
    assert gratuity["amount"]["value"] == 0
    assert gratuity["flags"] == ["Close to minimum service"]
    assert gratuity["service"]["years"]["value"] == 4
    assert gratuity["service"]["months"]["value"] == 11
    assert gratuity["applicable_due_date"]["value"] is None
    assert scenarios[7]["final_net"]["value"] == 93000


def test_scenario_08_pending_asset_and_notice(scenarios):
    result = scenarios[8]
    assert result["components"]["notice_shortfall_recovery"]["amount"]["value"] == 46667
    assert result["components"]["asset_recovery"]["amount"]["value"] is None
    assert result["components"]["asset_recovery"]["status"] == "Unresolved"
    assert "final_net" not in result
    assert result["certainty"] == INCOMPLETE


def test_scenario_09_lop_explanation(scenarios):
    result = scenarios[9]
    assert result["before"]["earnings"]["gross"]["value"] == 50000
    assert result["after"]["earnings"]["gross"]["value"] == 45000
    assert result["gross_change"]["value"] == -5000
    assert result["net_change"]["value"] == -5420
    assert result["employee_pf_change"]["certainty"] == COMPLETE
    assert result["employee_pf_change"]["value"] == 420
    assert result["existing_query"]["status"] == "In review"
    assert result["existing_query"]["sent_by_engine"] is False


def test_scenario_10_previous_employer_tds(scenarios):
    result = scenarios[10]
    assert result["before"]["tds"]["amount"]["value"] == 0
    assert result["after"]["tds"]["projected_gross"]["value"] == 1530000
    assert result["after"]["tds"]["taxable_income"]["value"] == 1455000
    assert result["after"]["tds"]["yearly_tax"]["value"] == 102180
    assert result["after"]["tds"]["tax_already_deducted"]["value"] == 15000
    assert result["after"]["tds"]["remaining_months"]["value"] == 7
    assert result["after"]["tds"]["amount"]["value"] == 12454
    assert result["tds_change"]["value"] == 12454


def test_scenario_11_no_earning_change(scenarios):
    result = scenarios[11]
    assert result["no_earning_component_change"] is True
    assert all(line["value"] == 0 for line in result["earning_component_changes"].values())
    assert result["gross_change"]["value"] == 0
    # Salary earnings do not change, but the dated PF ceiling must still be applied.
    assert result["employee_pf_change"]["value"] == 420
    assert result["net_change"]["value"] == -420


def test_scenario_12_authorization(scenarios, bundle):
    assert scenarios[12] == {"status": "Permission denied"}
    assert bundle["flows"].authorize("HR02", "E01") == {"status": "Permission denied"}
    assert bundle["flows"].authorize("USER-E05", "E05") == {"status": "Authorized"}
    assert bundle["flows"].authorize("missing user", "E01") == {"status": "Permission denied"}


def test_scenario_13_confirmed_and_unresolved_components(scenarios):
    result = scenarios[13]
    advance = result["components"]["loan_and_advance_recovery"]
    salary = result["components"]["final_month_salary"]
    asset = result["components"]["asset_recovery"]
    assert advance["amount"]["value"] == 10000
    assert advance["certainty"] == COMPLETE
    assert salary["amount"]["value"] == 70000
    assert salary["held"] is False
    assert salary["applicable_due_date"]["value"] == "2026-11-03"
    assert asset["certainty"] == INCOMPLETE
    assert "final_net" not in result
