"""Test bonus selected scope calculation function."""
import pytest
from payroll.core import COMPLETE, INCOMPLETE


def test_bonus_selected_scope_sales(bundle):
    flows = bundle["flows"]
    # Select Sales employees E13 and E14
    result = flows.bonus_selected_scope("quarterly_sales_incentive", "Q2 2026-27", ["E13", "E14"])
    aggs = result["aggregates"]
    assert aggs["eligible_count"]["value"] == 2
    assert aggs["not_eligible_count"]["value"] == 0
    assert aggs["needs_input_count"]["value"] == 0
    # E13 award is 20000, E14 award is 40000 -> gross 60000
    assert aggs["group_total_gross"]["value"] == 60000
    assert aggs["group_total_tds"]["value"] == 0
    assert aggs["group_total_net"]["value"] == 60000
    assert aggs["group_total_gross"]["certainty"] == COMPLETE
    assert aggs["group_total_net"]["certainty"] == COMPLETE


def test_bonus_selected_scope_with_incomplete_employee(bundle):
    flows = bundle["flows"]
    # E03 is in annual bonus but has incomplete attendance and tax
    result = flows.bonus_selected_scope("annual_performance_bonus", "FY 2025-26", ["E03", "E04"])
    aggs = result["aggregates"]
    assert aggs["eligible_count"]["value"] == 2
    assert aggs["group_total_gross"]["value"] == 96000
    assert aggs["group_total_tds"]["value"] is None
    assert aggs["group_total_net"]["value"] is None
    assert aggs["group_total_tds"]["certainty"] == INCOMPLETE
    assert aggs["group_total_net"]["certainty"] == INCOMPLETE
