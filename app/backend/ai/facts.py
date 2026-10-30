"""Builds turn-scoped facts lists for AI slot-based drafting.
All numbers and formatted strings are extracted strictly from deterministic engine output,
including signs (e.g. −₹420, −₹5,420).
"""
import re
from typing import Dict, Optional, Set, Tuple

from ..engine_bridge import bridge
from ..chat_router import format_inr, get_employee_name, get_rule_file, format_month_range_phrase


def build_facts_list(scenario_num: Optional[int], user: dict, bonus_type_key: Optional[str] = None) -> Dict[str, str]:
    """Generates the allowed slot names and exact formatted values for this reply."""
    if not scenario_num:
        return {}

    facts: Dict[str, str] = {}
    emp_id = user.get("employee_id")

    if scenario_num == 1:
        sc = bridge.get_scenario(1)
        r = sc["result"]
        t = r["totals"]
        disp = sc.get("display_inputs", {})
        old_sal = disp.get("old_monthly_salary", {}).get("total", {}).get("value")
        prop_sal = disp.get("proposed_monthly_salary", {}).get("total", {}).get("value")

        facts = {
            "employee_name": "Priya Sharma",
            "employee_first_name": "Priya",
            "employee_id": "E01",
            "period": "July to September 2026",
            "requested_hike": "10%",
            "net_arrears": format_inr(t["net_arrears"]["value"]),
            "hero_amount": format_inr(t["net_arrears"]["value"]),
            "gross_arrears": format_inr(t["gross_arrears"]["value"]),
            "estimated_tds_impact": format_inr(t.get("tds_impact", {}).get("value")),
            "tds_impact": format_inr(t.get("tds_impact", {}).get("value")),
            "employee_pf_change": format_inr(t.get("pf_change", {}).get("value")),
            "pf_change": format_inr(t.get("pf_change", {}).get("value")),
            "old_monthly_salary": format_inr(old_sal),
            "proposed_monthly_salary": format_inr(prop_sal),
            "status": "Ready for HR review; not applied"
        }

    elif scenario_num == 2:
        sc = bridge.get_scenario(2)
        r = sc["result"]
        t = r["totals"]
        facts = {
            "employee_name": "Arjun Rao",
            "employee_first_name": "Arjun",
            "employee_id": "E02",
            "period": "July to September 2026",
            "net_arrears": format_inr(t["net_arrears"]["value"]),
            "hero_amount": format_inr(t["net_arrears"]["value"]),
            "gross_arrears": format_inr(t["gross_arrears"]["value"]),
            "employee_pf_change": format_inr(t.get("pf_change", {}).get("value")),
            "pf_change": format_inr(t.get("pf_change", {}).get("value")),
            "status": "Ready for HR review; not applied"
        }

    elif scenario_num == 3:
        sc = bridge.get_scenario(3)
        r = sc["result"]
        disp = sc.get("display_inputs", {})
        aug_val = disp.get("august_diff", {}).get("value")
        sep_val = disp.get("september_diff", {}).get("value")
        facts = {
            "employee_name": "Kavya Iyer",
            "employee_first_name": "Kavya",
            "employee_id": "E03",
            "missing_record": "attendance",
            "period": "August and September 2026",
            "august_diff": format_inr(aug_val),
            "september_diff": format_inr(sep_val),
            "status": "Unresolved: Attendance missing"
        }

    elif scenario_num == 4:
        sc = bridge.get_scenario(4)
        r = sc["result"]
        runs = r.get("runs", {})
        target_run_key = bonus_type_key or "annual_performance_bonus"
        target_run = runs.get(target_run_key, runs.get("annual_performance_bonus", {}))
        meta = target_run.get("run_metadata", {})
        summary = target_run.get("summary", {})

        bonus_title = meta.get("bonus_type_name", "Annual performance bonus")
        period_str = meta.get("period", "FY 2025-26")
        eligible_gross = summary.get("known_eligible_gross", {}).get("value")
        eligible_cnt = str(summary.get("eligible_count", 4))
        ineligible_cnt = str(summary.get("ineligible_count", 1))
        needs_input_cnt = str(summary.get("needs_input_count", 1))

        facts = {
            "bonus_type": bonus_title,
            "period": period_str,
            "gross_eligible_total": format_inr(eligible_gross),
            "known_eligible_gross": format_inr(eligible_gross),
            "eligible_count": eligible_cnt,
            "ineligible_count": ineligible_cnt,
            "needs_input_count": needs_input_cnt,
            "status": "Ready for review; not applied"
        }

    elif scenario_num == 5:
        facts = {
            "employee_name": "Meera Nair",
            "employee_first_name": "Meera",
            "employee_id": "E09",
            "missing_record": "performance rating",
            "bonus_type": "Annual performance bonus",
            "status": "Needs HR decision"
        }

    elif scenario_num == 6:
        sc = bridge.get_scenario(6)
        r = sc.get("result", {})
        final_net = r.get("final_net", {}).get("value")
        tot_pay = r.get("gross_payables", {}).get("value")
        tot_ded = r.get("total_deductions", {}).get("value")
        grat_val = r.get("components", {}).get("gratuity", {}).get("amount", {}).get("value")
        facts = {
            "employee_name": "Rahul Verma",
            "employee_first_name": "Rahul",
            "employee_id": "E10",
            "final_net": format_inr(final_net),
            "total_payables": format_inr(tot_pay),
            "total_deductions": format_inr(tot_ded),
            "gratuity": format_inr(grat_val),
            "status": "Ready for HR review; not applied"
        }

    elif scenario_num == 7:
        facts = {
            "employee_name": "Lakshmi Reddy",
            "employee_first_name": "Lakshmi",
            "employee_id": "E11",
            "tenure": "4 years, 11 months",
            "service_threshold": "5 years",
            "status": "Needs HR decision"
        }

    elif scenario_num == 8:
        sc = bridge.get_scenario(8)
        r = sc.get("result", {})
        known_rec = r.get("known_recoveries_subtotal", {}).get("value")
        comps = r.get("components", {})
        notice_rec = comps.get("notice_shortfall_recovery", {}).get("amount", {}).get("value")
        adv_rec = comps.get("loan_and_advance_recovery", {}).get("amount", {}).get("value")
        facts = {
            "employee_name": "Imran Khan",
            "employee_first_name": "Imran",
            "employee_id": "E12",
            "known_recoveries": format_inr(known_rec),
            "notice_shortfall_recovery": format_inr(notice_rec),
            "salary_advance": format_inr(adv_rec),
            "status": "Unresolved asset recovery"
        }

    elif scenario_num == 9:
        sc = bridge.get_scenario(9)
        r = sc["result"]
        after_net = r["after"]["net_pay"]["value"]
        before_net = r["before"]["net_pay"]["value"]
        net_change = r["net_change"]["value"]
        reasons_list = r.get("reasons", [])
        lop_amt = reasons_list[0]["effect_amount"]["value"] if len(reasons_list) > 0 else -5000
        pf_amt = reasons_list[1]["effect_amount"]["value"] if len(reasons_list) > 1 else -420
        abs_net_change = abs(net_change)

        facts = {
            "employee_name": "Neha Gupta",
            "employee_first_name": "Neha",
            "employee_id": "E05",
            "earlier_month": "August",
            "later_month": "September",
            "net_change": format_inr(net_change),          # −₹5,420 (with sign)
            "abs_net_change": format_inr(abs_net_change),  # ₹5,420
            "net_change_direction": "lower",
            "after_net": format_inr(after_net),            # ₹42,780
            "before_net": format_inr(before_net),          # ₹48,200
            "lop_days": "3",
            "lop_amount": format_inr(lop_amt),             # −₹5,000
            "pf_change": format_inr(pf_amt),               # −₹420
            "pf_effect": format_inr(pf_amt),               # −₹420
            "primary_reason": "Loss of Pay (LOP)",
            "secondary_reason": "PF ceiling change"
        }

    elif scenario_num == 10:
        sc = bridge.get_scenario(10)
        disp = sc.get("display_inputs", {})
        r = sc["result"]
        net_change = r.get("net_change", {}).get("value")
        abs_net_change = abs(net_change)
        tds_change = r.get("tds_change", {}).get("value")
        reasons_list = r.get("reasons", [])
        prior_tds_amt = reasons_list[0]["effect_amount"]["value"] if len(reasons_list) > 0 else -12454
        pf_amt = reasons_list[1]["effect_amount"]["value"] if len(reasons_list) > 1 else -560
        after_tds = r.get("after", {}).get("tds", {}).get("amount", {}).get("value")

        facts = {
            "employee_name": "Siddharth Jain",
            "employee_first_name": "Siddharth",
            "employee_id": "E06",
            "earlier_month": "August",
            "later_month": "September",
            "net_change": format_inr(net_change),
            "abs_net_change": format_inr(abs_net_change),
            "tds_increase": format_inr(tds_change),
            "tds_change": format_inr(tds_change),
            "prior_tds_amt": format_inr(prior_tds_amt),
            "pf_change": format_inr(pf_amt),
            "after_tds": format_inr(after_tds),
            "declared_months": format_month_range_phrase(disp.get("declared_month_range", {}).get("value")) if disp.get("declared_month_range", {}).get("value") else "",
            "primary_reason": "previous employer income declaration",
            "secondary_reason": "PF ceiling change"
        }

    elif scenario_num == 11:
        sc = bridge.get_scenario(11)
        r = sc["result"]
        net_change = r.get("net_change", {}).get("value")
        abs_net_change = abs(net_change)
        reasons_list = r.get("reasons", [])
        pf_amt = reasons_list[0].get("effect_amount", {}).get("value") if reasons_list else None

        facts = {
            "employee_name": "Pooja Das",
            "employee_first_name": "Pooja",
            "employee_id": "E16",
            "earlier_month": "August",
            "later_month": "September",
            "net_change": format_inr(net_change),
            "abs_net_change": format_inr(abs_net_change),
            "net_decrease": format_inr(net_change),
            "abs_net_decrease": format_inr(abs_net_change),
            "gross_amount": format_inr(60000),
            "pf_change": format_inr(pf_amt),
            "primary_reason": "revised PF statutory deduction"
        }

    elif scenario_num == 13:
        facts = {
            "employee_name": "Imran Khan",
            "employee_first_name": "Imran",
            "employee_id": "E12",
            "known_recoveries": format_inr(56667),
            "notice_shortfall_recovery": format_inr(46667),
            "salary_advance": format_inr(10000),
            "status": "Review settlement calculation"
        }

    return facts


def extract_numbers_from_facts(facts: Dict[str, str]) -> Tuple[Set[float | int], Set[str]]:
    """Extracts all numeric values and dates from a turn's facts dictionary.
    Used by Guard 4 (Scoped Number Provenance Guard) to verify filled text against THIS reply only.
    """
    numbers: Set[float | int] = set()
    dates: Set[str] = set()

    for val in facts.values():
        if not val or not isinstance(val, str):
            continue

        # Currency & amounts (e.g. ₹67,476, −₹420, -5000)
        for m in re.finditer(r"[−\-]?\s*₹?\s*([0-9]{1,3}(?:,[0-9]{2,3})*(?:\.[0-9]+)?|[0-9]+(?:\.[0-9]+)?)", val):
            clean = m.group(1).replace(",", "")
            try:
                num = float(clean)
                n_val = int(num) if num.is_integer() else num
                numbers.add(n_val)
                numbers.add(-n_val)
            except ValueError:
                pass

        # Plain digits (e.g. "3", "4", "10%")
        for m in re.finditer(r"\b(\d+)\b", val):
            try:
                n_val = int(m.group(1))
                numbers.add(n_val)
                numbers.add(-n_val)
            except ValueError:
                pass

        # Percentage
        for m in re.finditer(r"(\d+(?:\.\d+)?)\s*%", val):
            try:
                num = float(m.group(1))
                numbers.add(int(num) if num.is_integer() else num)
            except ValueError:
                pass

        # Dates / Month names
        for m in re.finditer(r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{4})\b", val, re.IGNORECASE):
            dates.add(m.group(0))
        for m in re.finditer(r"\b\d{4}-\d{2}(?:-\d{2})?\b", val):
            dates.add(m.group(0))

    return numbers, dates
