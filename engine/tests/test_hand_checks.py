"""The owner's supplied expectations are fixed independently of the engine."""
import pytest


def hand_values(bundle, scenarios):
    bonus = {row["employee_id"]: row for request in bundle["bonuses"] for row in request["employees"]}
    e10, e11, e12 = [scenarios[n] for n in (6, 7, 8)]
    return {
        "E05_September_gross": scenarios[9]["after"]["earnings"]["gross"]["value"],
        "E16_no_component_change": scenarios[11]["no_earning_component_change"],
        "E10_gratuity": e10["components"]["gratuity"]["amount"]["value"],
        "E10_leave_encashment": e10["components"]["leave_encashment"]["amount"]["value"],
        "E10_salary_due": e10["components"]["final_month_salary"]["applicable_due_date"]["value"],
        "E10_gratuity_due": e10["components"]["gratuity"]["applicable_due_date"]["value"],
        "E11_gratuity_status": e11["components"]["gratuity"]["status"],
        "E11_close_flag": e11["components"]["gratuity"]["flags"],
        "E12_notice_recovery": e12["components"]["notice_shortfall_recovery"]["amount"]["value"],
        "E12_no_final_net": "final_net" not in e12,
        "E12_certainty": e12["certainty"],
        "E07_bonus": bonus["E07"]["amount"]["value"],
        "E04_bonus": bonus["E04"]["amount"]["value"],
        "E08_eligibility": bonus["E08"]["eligibility"],
        "E08_reason": bonus["E08"]["reason"],
        "E09_eligibility": bonus["E09"]["eligibility"],
        "E09_reason": bonus["E09"]["reason"],
        "E13_incentive": bonus["E13"]["amount"]["value"],
        "E14_incentive": bonus["E14"]["amount"]["value"],
        "E15_incentive": bonus["E15"]["amount"]["value"],
    }


EXPECTED = {
    "E05_September_gross": 45000,
    "E16_no_component_change": True,
    "E10_gratuity": 201923,
    "E10_leave_encashment": 33333,
    "E10_salary_due": "2026-11-03",
    "E10_gratuity_due": "2026-12-01",
    "E11_gratuity_status": "Not applicable",
    "E11_close_flag": ["Close to minimum service"],
    "E12_notice_recovery": 46667,
    "E12_no_final_net": True,
    "E12_certainty": "Incomplete",
    "E07_bonus": 9929,
    "E04_bonus": 60000,
    "E08_eligibility": "Not eligible",
    "E08_reason": "On notice at the time of calculation",
    "E09_eligibility": "Needs input",
    "E09_reason": "Performance record missing",
    "E13_incentive": 20000,
    "E14_incentive": 40000,
    "E15_incentive": 60000,
}


@pytest.mark.parametrize("name,expected", EXPECTED.items(), ids=EXPECTED.keys())
def test_owner_hand_check(name, expected, bundle, scenarios):
    actual = hand_values(bundle, scenarios)[name]
    assert actual == expected, f"{name}: expected {expected!r}, actual {actual!r}; consult the result's inputs and rule_ids"


def test_owner_hand_check_e05_september_pf(bundle):
    assert bundle["payroll"].ledger["E05", "2026-09"]["pf"]["employee"]["value"] == 2220


def test_owner_hand_check_e01_june_pf(bundle):
    assert bundle["payroll"].ledger["E01", "2026-06"]["pf"]["employee"]["value"] == 1800


def test_owner_hand_check_round_half_up(bundle):
    from payroll.core import dec
    result = bundle["store"].calc(dec("1249.50"), "Round an exact half-rupee tie using the approved rule",
                                     bundle["store"].base_refs("E01"))
    assert result["value"] == 1250


def test_owner_hand_check_e01_proposal_flag(scenarios):
    assert "Estimated TDS if approved and paid in October 2026 payroll" in scenarios[1]["flags"]


DISPLAY_EXPECTED = {
    "E01_requested_hike_percentage": 10,
    "E01_effective_date": "2026-04-01",
    "E01_old_monthly_total": 120000,
    "E01_proposed_monthly_total": 132000,
    "E05_September_lop_days": 3,
    "E05_September_calendar_days": 30,
    "E06_previous_employer_gross": 450000,
    "E06_previous_employer_tds": 15000,
    "E06_remaining_yearly_tax": 87180,
    "E04_rating": 4,
    "E04_applied_rating_rate_percent": 10,
    "E12_known_recoveries_subtotal": 56667,
    "E12_recoveries_total": None,
    "E12_recoveries_certainty": "Incomplete",
    "E12_known_recoveries_flag": "Excludes unresolved asset recovery",
    "E05_first_reason_type": "LOP",
    "E05_first_reason_effect": -5000,
    "E05_second_reason_type": "PF ceiling change",
    "E05_second_reason_effect": -420,
}


def display_hand_values(bundle, scenarios):
    display = {i + 1: case["display_inputs"] for i, case in enumerate(bundle["scenarios"])}
    e04 = display[4]["bonus_requests"][0]["employees"]["E04"]
    return {
        "E01_requested_hike_percentage": display[1]["requested_hike_percentage"]["value"],
        "E01_effective_date": display[1]["effective_date"]["value"],
        "E01_old_monthly_total": display[1]["old_monthly_salary"]["total"]["value"],
        "E01_proposed_monthly_total": display[1]["proposed_monthly_salary"]["total"]["value"],
        "E05_September_lop_days": display[9]["months"]["2026-09"]["lop_days"]["value"],
        "E05_September_calendar_days": display[9]["months"]["2026-09"]["calendar_days"]["value"],
        "E06_previous_employer_gross": display[10]["previous_employer_declared_gross"]["value"],
        "E06_previous_employer_tds": display[10]["previous_employer_tds"]["value"],
        "E06_remaining_yearly_tax": display[10]["remaining_yearly_tax"]["value"],
        "E04_rating": e04["rating"]["value"],
        "E04_applied_rating_rate_percent": e04["applied_rating_rate_percent"]["value"],
        "E12_known_recoveries_subtotal": scenarios[8]["known_recoveries_subtotal"]["value"],
        "E12_recoveries_total": scenarios[8]["recoveries_total"]["value"],
        "E12_recoveries_certainty": scenarios[8]["recoveries_total"]["certainty"],
        "E12_known_recoveries_flag": scenarios[8]["known_recoveries_subtotal"]["flags"][0],
        "E05_first_reason_type": scenarios[9]["reasons"][0]["type"],
        "E05_first_reason_effect": scenarios[9]["reasons"][0]["effect_amount"]["value"],
        "E05_second_reason_type": scenarios[9]["reasons"][1]["type"],
        "E05_second_reason_effect": scenarios[9]["reasons"][1]["effect_amount"]["value"],
    }


@pytest.mark.parametrize("name,expected", DISPLAY_EXPECTED.items(), ids=DISPLAY_EXPECTED.keys())
def test_owner_display_hand_check(name, expected, bundle, scenarios):
    actual = display_hand_values(bundle, scenarios)[name]
    assert actual == expected, (
        f"{name}: expected {expected!r}, actual {actual!r}; "
        "consult the display source or calculation inputs and rule_ids"
    )


def test_owner_hand_check_e06_declared_month_range(bundle):
    display = {i + 1: case["display_inputs"] for i, case in enumerate(bundle["scenarios"])}
    actual = display[10]["declared_month_range"]["value"]
    assert actual == "2026-04 to 2026-06", (
        f"E06_declared_month_range: expected '2026-04 to 2026-06', actual {actual!r}"
    )

