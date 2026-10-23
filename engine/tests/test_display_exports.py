"""Display-copy integrity, aggregation, ranking and unchanged legacy values."""
import hashlib
import json

from conftest import ROOT
from payroll.core import CERTAINTIES, COMPLETE, INCOMPLETE
from test_invariants import calculations

ADDITIONS = {
    "display_inputs", "aggregates", "recoveries_total", "known_recoveries_subtotal",
    "reasons", "northwind_tds_already_deducted", "previous_employer_tds",
    "remaining_yearly_tax",
}


def legacy_values(value, path=""):
    result = []
    if isinstance(value, dict):
        if "value" in value:
            result.append([path + "/value", value["value"]])
        for key, child in value.items():
            if key not in ADDITIONS:
                result.extend(legacy_values(child, path + "/" + key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            result.extend(legacy_values(child, path + "/" + str(index)))
    return result


def test_existing_generated_values_are_unchanged():
    baseline = json.loads((ROOT / "engine/tests/fixtures/original-calculated-values.json").read_text())
    for file, expected in baseline.items():
        data = json.loads((ROOT / file).read_text(encoding="utf-8"))
        values = sorted(legacy_values(data))
        raw = json.dumps(values, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()
        assert len(values) == expected["count"], file
        assert hashlib.sha256(raw).hexdigest() == expected["sha256"], (
            f"An existing calculated amount, date or supplied rule value changed in {file}"
        )


def display_items(value):
    if isinstance(value, dict):
        if {"value", "source_file", "record_id", "certainty"} <= value.keys():
            yield value
        else:
            for child in value.values():
                yield from display_items(child)
    elif isinstance(value, list):
        for child in value:
            yield from display_items(child)


def resolve(value, path):
    for part in path.split("/"):
        value = value[int(part)] if isinstance(value, list) else value[part]
    return value


def test_display_items_copy_the_source_or_carry_a_calculation(bundle):
    for case in bundle["scenarios"]:
        assert "display_inputs" in case
        for item in display_items(case["display_inputs"]):
            assert item["certainty"] in CERTAINTIES
            assert item["source_file"] and item["record_id"]
            if "calculation" in item:
                assert item["value"] == item["calculation"]["value"]
                assert item["certainty"] == item["calculation"]["certainty"]
                assert item["calculation"]["inputs"] and item["calculation"]["rule_ids"]
                assert resolve(case, item["source_field"])["value"] == item["value"]
            elif item["value"] is not None:
                source = json.loads((ROOT / item["source_file"]).read_text(encoding="utf-8-sig"))
                if isinstance(source, list):
                    source = next(r for r in source if item["record_id"] in
                                  [v for k, v in r.items() if k.endswith("_id")])
                else:
                    source = source[item["record_id"]]
                assert resolve(source, item["source_field"]) == item["value"]


def test_bonus_aggregates_preserve_unknown_eligible_tax_and_net(scenarios):
    annual, sales = scenarios[4]["bonus_requests"]
    a, b = annual["aggregates"], sales["aggregates"]
    assert [a[k]["value"] for k in ("eligible_count", "not_eligible_count", "needs_input_count")] == [4, 1, 1]
    assert a["group_total_gross"]["value"] == 213929
    assert a["group_total_tds"]["value"] is None
    assert a["group_total_net"]["value"] is None
    assert a["group_total_tds"]["certainty"] == INCOMPLETE
    assert a["group_total_net"]["certainty"] == INCOMPLETE
    assert [b[k]["value"] for k in ("eligible_count", "not_eligible_count", "needs_input_count")] == [3, 0, 0]
    assert [b[k]["value"] for k in ("group_total_gross", "group_total_tds", "group_total_net")] == [120000, 0, 120000]


def test_display_limits_missing_attendance_ineligible_bonus_and_authorization(bundle):
    display = [case["display_inputs"] for case in bundle["scenarios"]]
    missing = display[2]["months"]["2026-07"]
    assert all(item["value"] is None and item["certainty"] == INCOMPLETE for item in missing.values())
    notice = display[3]["bonus_requests"][0]["employees"]["E08"]
    assert notice["rating"]["value"] == 4
    assert notice["policy_rating_rate_percent"]["value"] == 10
    assert notice["applied_rating_rate_percent"]["value"] is None
    assert notice["applied_rating_rate_percent"]["application_status"] == "Not applied: Not eligible"
    assert display[11] == {}
    assert bundle["scenarios"][11]["result"] == {"status": "Permission denied"}


def test_reasons_rank_net_effects_and_reconcile_in_both_directions(bundle, scenarios):
    for number in (9, 10, 11):
        result = scenarios[number]
        amounts = [reason["effect_amount"]["value"] for reason in result["reasons"]]
        assert amounts == sorted(amounts, key=abs, reverse=True)
        assert sum(amounts) == result["net_change"]["value"]
        assert all(reason["source_references"] for reason in result["reasons"])
    reverse = bundle["flows"].compare("E05", "2026-09", "2026-08")
    assert [r["effect_amount"]["value"] for r in reverse["reasons"]] == [5000, 420]
    assert sum(r["effect_amount"]["value"] for r in reverse["reasons"]) == reverse["net_change"]["value"]
    assert scenarios[6]["recoveries_total"]["value"] == 0
    assert scenarios[7]["recoveries_total"]["value"] == 0
    assert scenarios[8]["recoveries_total"]["value"] is None
    assert scenarios[13]["known_recoveries_subtotal"]["value"] == 56667


def test_rule_references_have_version_without_invented_effective_dates(bundle):
    records = bundle["scenarios"] + list(bundle["payroll"].ledger.values()) + bundle["bonuses"]
    for item in calculations(records):
        for ref in item["rule_ids"]:
            assert ref["rules_version"] == "Northwind demo rules v1"
            assert ref["verified_on"] == "2026-10-13"
            file, key = ref["rule_id"].split("#")
            original = bundle["store"].rule_files[file.removesuffix(".json")][key]
            assert ref["effective_from"] == original["effective_from"]
            assert ref["effective_to"] == original["effective_to"]
            if original["effective_from"] is None and original["effective_to"] is None:
                assert ref["date_note"] == "Applies to all demo periods"
            else:
                assert "date_note" not in ref
