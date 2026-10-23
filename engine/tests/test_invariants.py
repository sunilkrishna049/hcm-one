"""Cross-cutting controls: provenance, incomplete history and reproducibility."""
import json

from conftest import ROOT
from payroll.core import CERTAINTIES, COMPLETE, RuleError, Store, UNVERIFIED, dec, parse_date
from payroll.history import Payroll
from payroll.flows import Flows
from payroll.scenarios import calculate


def calculations(value):
    if isinstance(value, dict):
        if "formula" in value:
            yield value
        else:
            for item in value.values():
                yield from calculations(item)
    elif isinstance(value, list):
        for item in value:
            yield from calculations(item)


def test_all_results_have_provenance(bundle):
    records = bundle["scenarios"] + list(bundle["payroll"].ledger.values())
    for result in calculations(records):
        assert set(result) == {"value", "formula", "inputs", "rule_ids", "certainty", "flags"}
        assert result["certainty"] in CERTAINTIES
        assert result["inputs"] and result["rule_ids"]
        assert all(ref["source_file"] and ref["record_id"] for ref in result["inputs"])
        for rule in result["rule_ids"]:
            assert {"rule_id", "source_file", "source", "effective_from", "effective_to"} <= rule.keys()
            file, key = rule["rule_id"].split("#")
            assert rule == bundle["store"].rule_ref(file.removesuffix(".json"), key)


def test_missing_attendance_never_creates_a_payslip(bundle):
    payroll = bundle["payroll"]
    assert not any(row["employee_id"] == "E03" and row["month"] == "2026-07" for row in payroll.payslips)
    assert any(row["employee_id"] == "E03" and row["month"] == "2026-07" for row in payroll.failures)
    assert all(row["certainty"] == COMPLETE for row in payroll.payslips)
    assert len(payroll.payslips) + len(payroll.failures) + len(payroll.skipped) == 16 * 6


def test_rounding_tie_stops_without_a_convention(bundle):
    s = Store(ROOT)
    del s.rule_files["company-settings"]["rounding_ties"]
    refs = s.base_refs("E01")
    assert s.calc(dec("1249.5"), "Test exact nearest-rupee tie", refs)["certainty"] == UNVERIFIED
    assert s.calc(dec("1249.49"), "Test below half rupee", refs)["value"] == 1249
    assert s.calc(dec("1249.51"), "Test above half rupee", refs)["value"] == 1250


def test_proposal_tax_estimate_reconciles_without_changing_history(bundle):
    hike = bundle["scenarios"][0]["result"]
    totals = hike["totals"]
    assert hike["estimated_payment_month"] == "2026-10"
    assert totals["tds_impact"]["value"] == (totals["recurring_salary_tds_impact"]["value"]
                                             + totals["arrears_only_tds_impact"]["value"])
    assert sum(row["tds_impact"]["value"] for row in hike["months"]) == totals["arrears_only_tds_impact"]["value"]
    assert hike["tds_estimate"]["baseline"]["amount"]["value"] == 7220
    assert hike["tds_estimate"]["proposed"]["amount"]["value"] == 10944
    assert bundle["payroll"].ledger["E01", "2026-04"]["earnings"]["gross"]["value"] == 120000
    assert "Estimated TDS if approved and paid in October 2026 payroll" in totals["tds_impact"]["flags"]


def test_lop_pf_ceiling_is_applied_per_dated_segment(bundle):
    pf = bundle["payroll"].ledger["E05", "2026-09"]["pf"]
    assert pf["monthly_earned_pf_wage"]["value"] == 22500
    assert [row["earned_pf_wage"]["value"] for row in pf["segments"]] == [12000, 10500]
    assert [row["pf_wage"]["value"] for row in pf["segments"]] == [8000, 10500]
    assert [row["employee"]["value"] for row in pf["segments"]] == [960, 1260]


def test_proposal_tax_recalculates_when_receipt_month_changes():
    s = Store(ROOT)
    first_payroll = Payroll(s)
    first_payroll.generate_history()
    first_flows = Flows(first_payroll, parse_date("2026-10-13"))
    first = first_flows.hike("E01")
    revision = s.one("salary-revisions", "E01")
    refs = s.base_refs("E01") + [s.ref("salary-revisions", revision)]
    # Simulate a later receipt month in memory only; protected JSON fixtures stay unchanged.
    s.mock["payroll-runs"].append({"payroll_run_id": "TEST-RUN-2026-11", "month": "2026-11",
                                  "status": "open", "processed_date": None})
    missing_history = first_flows.proposal_tax("E01", first["totals"]["gross_arrears"], refs, revision,
                                               payment_month="2026-11")
    assert missing_history["amount"]["value"] is None
    assert "Prior processed payroll unavailable for 2026-10" in missing_history["amount"]["flags"]
    for run in s.mock["payroll-runs"]:
        if run["month"] == "2026-10":
            run["status"] = "processed"
    s.processed.append("2026-10")
    later_payroll = Payroll(s)
    later_payroll.generate_history()
    later = Flows(later_payroll, parse_date("2026-11-13")).proposal_tax(
        "E01", first["totals"]["gross_arrears"], refs, revision)
    assert later["estimated_payment_month"] == "2026-11"
    assert later["proposed"]["remaining_months"]["value"] == 5
    assert later["amount"]["value"] != first["totals"]["tds_impact"]["value"]
    assert "Estimated TDS if approved and paid in November 2026 payroll" in later["amount"]["flags"]


def test_rule_changes_are_loaded_not_hardcoded():
    s = Store(ROOT)
    s.rule_files["pf-rules"]["employee_contribution_rate_percent"]["value"] = 10
    assert Payroll(s).pf("E04", "2026-09")["employee"]["value"] == 1967
    s.rule_files["pf-rules"]["employee_contribution_rate_percent"]["status"] = "verify_before_build"
    try:
        Payroll(s).pf("E04", "2026-09")
    except RuleError as error:
        assert "Unverified rule" in str(error)
    else:
        raise AssertionError("An unverified contribution rate must stop the calculation")


def test_persisted_results_match_repeat_run(bundle):
    for case in bundle["scenarios"]:
        path = ROOT / "data/generated/scenarios" / f"{case['scenario_id']}.json"
        assert json.loads(path.read_text(encoding="utf-8")) == case
    again = calculate(ROOT, parse_date("2026-10-13"))
    assert again["scenarios"] == bundle["scenarios"]
    assert again["payroll"].payslips == bundle["payroll"].payslips


def test_net_is_sum_of_rounded_lines(bundle):
    for slip in bundle["payroll"].payslips:
        gross = sum(line["value"] for line in slip["earnings"]["lines"].values())
        deductions = slip["pf"]["employee"]["value"] + slip["tds"]["amount"]["value"]
        assert slip["earnings"]["gross"]["value"] == gross
        assert slip["net_pay"]["value"] == gross - deductions
        assert slip["pf"]["employer"]["value"] == slip["pf"]["eps"]["value"] + slip["pf"]["epf"]["value"]
