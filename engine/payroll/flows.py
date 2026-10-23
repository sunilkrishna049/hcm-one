"""Read-only hike, bonus, settlement, comparison and authorization proposals."""
from __future__ import annotations

import calendar
import re
from datetime import timedelta

from .core import (COMPLETE, HR, INCOMPLETE, UNVERIFIED, RuleError, add_months,
                   completeness, dec, month_bounds, numbers, parse_date, unique)


def bonus_rating_rate(rates, rating):
    """Select the supplied policy rate without changing or deriving a rate."""
    rate = rates.get(str(rating))
    if rate is not None:
        return rate
    matches = [v for k, v in rates.items() if "_to_" in k
               and int(k.split("_to_")[0]) <= rating <= int(k.split("_to_")[1])]
    if len(matches) != 1:
        raise RuleError("Rating has no unique bonus rate")
    return matches[0]


class Flows:
    def __init__(self, payroll, as_of):
        self.p = payroll
        self.s = payroll.s
        self.as_of = as_of

    def proposal_tax(self, employee, amount, refs, hike=None, payment_month=None):
        """Recalculate a hypothetical receipt-month withholding difference from original history."""
        s = self.s
        policy = s.rule("tax-rules", "proposal_tds_estimate")
        rules = s.rule_refs(("tax-rules", "proposal_tds_estimate"),
                            ("tax-rules", "past_year_arrears"), ("tax-rules", "monthly_tds_formula"))
        runs = [row for row in s.mock["payroll-runs"] if row["month"] > s.processed[-1]
                and (row["month"] == payment_month if payment_month else row["status"] == "open")]
        if not runs:
            return {"estimated_payment_month": payment_month, "flags": ["Payment payroll input missing"],
                    "amount": s.blocked("Proposal TDS estimate needs a receipt payroll record", refs, rules)}
        run = min(runs, key=lambda row: row["month"])
        month = run["month"]
        first, _ = month_bounds(month)
        if not s.year_start <= first <= s.year_end:
            s.ambiguity("AMB-03", "Proposal receipt payroll is outside the configured tax year; its rules and history are unavailable.", employee)
            return {"estimated_payment_month": month, "flags": [],
                    "amount": s.blocked("Proposal TDS requires the receipt tax year's rules and payroll history", refs, rules, UNVERIFIED)}
        template = re.search(r'flag "([^"]+)"', policy)
        if not template:
            raise RuleError("The proposal TDS estimate rule must supply its assumption flag")
        label = f"{calendar.month_name[first.month]} {first.year}"
        flag = template.group(1).replace("[month]", label)
        estimate_refs = refs + [s.ref("payroll-runs", run)]
        baseline = self.p.tds(employee, month, self.p.earnings(employee, month))
        proposed = self.p.tds(employee, month, self.p.earnings(employee, month, hike), hike, amount)
        def annotate(item):
            if isinstance(item, dict):
                if "formula" in item:
                    item["inputs"] = unique(item["inputs"] + estimate_refs)
                    item["rule_ids"] = unique(item["rule_ids"] + rules)
                    item["flags"] = unique(item["flags"] + [flag])
                else:
                    for child in item.values():
                        annotate(child)
            elif isinstance(item, list):
                for child in item:
                    annotate(child)
        annotate(baseline)
        annotate(proposed)
        impact = s.total([proposed["amount"], baseline["amount"]],
                         "Estimated receipt-month TDS with this proposal less TDS without this proposal; recalculate if the payment month changes",
                         estimate_refs, rules, signs=[1, -1])
        return {"estimated_payment_month": month, "flags": [flag], "baseline": baseline,
                "proposed": proposed, "amount": impact,
                "recalculate_when_payment_month_changes": True}

    def hike(self, employee, revision_override=None):
        s = self.s
        revision = revision_override or s.one("salary-revisions", employee)
        if revision is None:
            raise ValueError(f"No revision request for {employee}")
        refs = s.base_refs(employee) + [s.ref("salary-revisions", revision)]
        affected = [month for month in s.processed if month >= revision["effective_date"][:7]]
        rows = []
        for month in affected:
            old = self.p.ledger[employee, month]["earnings"]
            revised = self.p.earnings(employee, month, revision)
            differences = {key: s.total([revised["lines"][key], old["lines"][key]],
                              f"Revised rounded {key} less original rounded {key}", signs=[1, -1])
                           for key in old["lines"]}
            old_pf = self.p.ledger[employee, month]["pf"]
            revised_pf = self.p.pf(employee, month, revision)
            pf_changes = {key: s.total([revised_pf[key], old_pf[key]],
                                       f"Revised rounded {key} PF less original rounded {key} PF", signs=[1, -1])
                          for key in ("employee", "employer", "eps", "epf")}
            rows.append({"month": month, "paid_days": old["paid_days"], "old": old,
                         "revised": revised, "component_differences": differences,
                         "difference": s.total(differences.values(), "Sum of rounded component arrears for this month"),
                         "old_pf": old_pf, "revised_pf": revised_pf, "pf_change": pf_changes})
        gross = s.total([row["difference"] for row in rows], "Sum of all known monthly rounded arrears; stop if a month is unknown")
        pf = {key: s.total([row["pf_change"][key] for row in rows], f"Sum of monthly {key} PF changes")
              for key in ("employee", "employer", "eps", "epf")}
        estimate = self.proposal_tax(employee, gross, refs, revision)
        tax = estimate["amount"]
        zero = s.calc(0, "No arrears in the recurring-salary-only comparison", refs,
                      s.rule_refs(("tax-rules", "proposal_tds_estimate")))
        recurring = self.proposal_tax(employee, zero, refs, revision)
        previous_tds = recurring.get("proposed", {}).get("amount", recurring["amount"])
        accumulated = []
        for row in rows:
            accumulated.append(row["difference"])
            cumulative = s.total(accumulated, "Sum of rounded arrears through this affected month")
            step = self.proposal_tax(employee, cumulative, refs, revision)
            next_tds = step.get("proposed", {}).get("amount", step["amount"])
            row["tds_impact"] = s.total([next_tds, previous_tds],
                                        "Incremental estimated receipt-month TDS from adding this month's arrears after earlier months' arrears", signs=[1, -1])
            row["estimated_payment_month"] = estimate["estimated_payment_month"]
            previous_tds = next_tds
        net = s.total([gross, pf["employee"], tax], "Gross arrears less employee PF change and receipt-month TDS impact", signs=[1, -1, -1])
        result = {"employee_id": employee, "revision_id": revision["revision_id"],
                  "proposal_status": "Needs HR approval; not applied", "months": rows,
                  "estimated_payment_month": estimate["estimated_payment_month"], "flags": estimate["flags"],
                  "tds_estimate": estimate,
                  "totals": {"gross_arrears": gross, "pf_change": pf, "tds_impact": tax,
                             "recurring_salary_tds_impact": recurring["amount"],
                             "arrears_only_tds_impact": s.total([row["tds_impact"] for row in rows], "Sum of incremental monthly arrears TDS effects in receipt payroll"),
                             "net_arrears": net}}
        result["certainty"] = completeness(result)
        return result

    def notice_at(self, employee):
        row = self.s.one("exits", employee)
        if row:
            return parse_date(row["resignation_date"]) <= self.as_of <= parse_date(row["last_working_day"])
        return False

    def bonus_employee(self, request, employee):
        s = self.s
        kind = request["bonus_type"]
        policy = s.rule("bonus-rules", kind)
        record = s.employees[employee]
        performance = s.one("performance", employee, period=request["period"])
        refs = s.base_refs(employee) + [s.ref("company", record_id=s.company["company_id"],
                                             fields=["bonus_request_inputs"])]
        refs.append(s.ref("performance", performance, record_id=(performance or {}).get(
                         "performance_id", f"missing:{employee}:{request['period']}")))
        exit_row = s.one("exits", employee)
        if exit_row:
            refs.append(s.ref("exits", exit_row))
        refs.append({"source_file": "data/generated/run-context.json", "record_id": "RUN-CONTEXT"})
        rules = s.rule_refs(("bonus-rules", kind))
        start, end = parse_date(request["period_start"]), parse_date(request["period_end"])
        joining = parse_date(record["joining_date"])
        item = {"employee_id": employee, "period": request["period"], "bonus_type": kind,
                "proposal_status": "Needs HR approval; not applied"}
        reason = None
        if kind == "annual_performance_bonus":
            notice_rule = s.rule("bonus-rules", "annual_performance_bonus_notice_check")
            rules += s.rule_refs(("bonus-rules", "annual_performance_bonus_notice_check"),
                                 ("bonus-rules", "annual_performance_bonus_calculation"))
            if self.notice_at(employee) and not policy["eligibility"]["on_notice_allowed"]:
                reason = notice_rule["recorded_reason"]
            elif (end - joining).days < policy["eligibility"]["joined_at_least_days_before_period_end"]:
                reason = "Joined too close to the bonus period end"
        elif record["team"] != policy["eligibility"]["team"]:
            reason = "Employee is outside the eligible team"
        elif self.notice_at(employee) and not policy["eligibility"]["on_notice_allowed"]:
            reason = "On notice at the time of calculation"
        if reason:
            item.update(eligibility="Not eligible", reason=reason,
                        amount=s.calc(0, "No bonus payable because the eligibility check failed", refs, rules))
        elif performance is None:
            item.update(eligibility="Needs input", reason="Performance record missing",
                        amount=s.blocked("Bonus needs the performance record for the requested period", refs, rules,
                                         flags=["Performance record missing"]))
        elif kind == "annual_performance_bonus":
            calculation = s.rule("bonus-rules", "annual_performance_bonus_calculation")
            if calculation["lop_reduces_eligible_days"] or calculation["proration_applications"] != 1:
                raise RuleError("Unsupported annual bonus proration policy")
            operands = numbers(calculation["annual_basic_formula"])
            if len(operands) != 1:
                raise RuleError("Annual Basic multiplier is missing or ambiguous")
            annual_basic = s.calc(self.p.components(employee)["basic"] * operands[0],
                                 "Monthly Basic at the bonus period end times the configured annual multiplier", refs, rules)
            days = max(0, (end - max(joining, start)).days + 1)
            period_days = (end - start).days + 1
            rating = performance["rating"]
            rates = policy["rating_rates_percent"]
            if rating is None:
                item.update(eligibility="Needs input", reason="Performance rating missing",
                            amount=s.blocked("Bonus needs a performance rating", refs, rules))
            else:
                rate = bonus_rating_rate(rates, rating)
                amount = s.calc(dec(rate) / 100 * dec(annual_basic["value"]) * days / period_days,
                                "Rating rate times annual Basic times eligible employment days divided by bonus period calendar days; prorate once", refs, rules)
                item.update(eligibility="Eligible", reason="Team, joining date, notice and performance checks passed",
                            annual_basic=annual_basic,
                            eligible_days=s.calc(days, "Inclusive days employed within the requested period; LOP does not reduce these days", refs, rules, money=False),
                            period_days=s.calc(period_days, "Inclusive calendar days in the requested bonus period", refs, rules, money=False),
                            amount=amount)
        else:
            target, achievement = performance["target"], performance["achievement"]
            if target is None or achievement is None or target <= 0:
                item.update(eligibility="Needs input", reason="Valid target and achievement are required",
                            amount=s.blocked("Sales incentive needs a positive target and recorded achievement", refs, rules))
            else:
                percent = dec(achievement) / dec(target) * 100
                matches = []
                for slab in policy["slabs"]:
                    text = slab["achievement_range"]
                    limits = numbers(text)
                    if "below" in text and percent < limits[0]:
                        matches.append(slab)
                    elif "above" in text and percent >= limits[0]:
                        matches.append(slab)
                    elif " to " in text and limits[0] <= percent <= limits[1]:
                        matches.append(slab)
                if len(matches) != 1:
                    s.ambiguity("AMB-04", "Sales incentive ranges do not define fractional achievement between their written integer ranges.", employee)
                    item.update(eligibility="Needs input", reason="Rule not verified: achievement has no unique slab",
                                amount=s.blocked("Sales incentive requires a unique achievement slab", refs, rules, UNVERIFIED, ["AMB-04"]))
                else:
                    item.update(eligibility="Eligible", reason=f"Achievement falls in the {matches[0]['achievement_range']} slab",
                                achievement_percent=s.calc(str(percent), "Recorded achievement divided by target, expressed as a percentage", refs, rules, money=False),
                                amount=s.calc(matches[0]["amount_inr"], "Configured incentive amount for the matched achievement slab", refs, rules))
        if item["eligibility"] == "Eligible":
            if policy["part_of_pf_wage"]:
                s.ambiguity("AMB-05", "A PF-bearing bonus requires a verified receipt-month PF interaction rule.", employee)
                item["pf_change"] = s.blocked("Bonus PF requires its receipt-month wage calculation", refs, rules, UNVERIFIED, ["AMB-05"])
            else:
                item["pf_change"] = s.calc(0, "This bonus type is excluded from PF wage by company policy", refs, rules)
            estimate = self.proposal_tax(employee, item["amount"], refs)
            item["tds_estimate"] = estimate
            item["estimated_payment_month"] = estimate["estimated_payment_month"]
            item["flags"] = estimate["flags"]
            item["tds_impact"] = estimate["amount"]
            item["net_amount"] = s.total([item["amount"], item["pf_change"], item["tds_impact"]],
                                        "Rounded gross bonus less employee PF and receipt-month TDS impact", signs=[1, -1, -1])
        item["certainty"] = completeness(item)
        return item

    def bonus(self):
        result = []
        for request in self.s.company["bonus_request_inputs"]:
            items = [self.bonus_employee(request, eid) for eid in request["employee_ids"]]
            eligible = [r for r in items if r["eligibility"] == "Eligible"]
            result.append({"bonus_type": request["bonus_type"], "period": request["period"], "employees": items,
                           "eligible": [r["employee_id"] for r in eligible],
                           "not_eligible": [{"employee_id": r["employee_id"], "reason": r["reason"]} for r in items if r["eligibility"] == "Not eligible"],
                           "needs_input": [{"employee_id": r["employee_id"], "reason": r["reason"]} for r in items if r["eligibility"] == "Needs input"],
                           "known_eligible_gross": self.s.total([r["amount"] for r in eligible], "Sum of rounded gross bonus lines for employees with known eligibility; missing employee is excluded explicitly"),
                           "certainty": completeness(items)})
            result[-1]["aggregates"] = self.bonus_aggregates(request, items)
        return result

    def bonus_aggregates(self, request, items):
        s = self.s
        rules = s.rule_refs(("bonus-rules", request["bonus_type"]))
        refs = [s.ref("company", record_id=s.company["company_id"],
                      fields=["bonus_request_inputs"])]
        refs += [ref for item in items for ref in item["amount"]["inputs"]]
        result = {}
        for key, label in (("eligible_count", "Eligible"),
                           ("not_eligible_count", "Not eligible"),
                           ("needs_input_count", "Needs input")):
            result[key] = s.calc(sum(item["eligibility"] == label for item in items),
                                 f"Count request employees whose recorded eligibility is {label}",
                                 refs, rules, money=False)
        eligible = [item for item in items if item["eligibility"] == "Eligible"]
        for key, field in (("group_total_gross", "amount"),
                           ("group_total_tds", "tds_impact"),
                           ("group_total_net", "net_amount")):
            result[key] = s.total([item[field] for item in eligible],
                                   f"Sum of rounded {field} lines for employees with known eligible status; exclude needs-input and not-eligible employees",
                                   refs, rules)
            if result[key]["value"] is None:
                result[key]["certainty"] = INCOMPLETE
        return result

    def bonus_selected_scope(self, bonus_type, period, selected_employee_ids):
        request = next((r for r in self.s.company["bonus_request_inputs"]
                        if r["bonus_type"] == bonus_type and r["period"] == period), None)
        if not request:
            raise ValueError(f"No bonus request for {bonus_type} {period}")
        items = [self.bonus_employee(request, eid) for eid in selected_employee_ids]
        aggregates = self.bonus_aggregates(request, items)
        return {
            "bonus_type": bonus_type,
            "period": period,
            "selected_employee_ids": selected_employee_ids,
            "employees": items,
            "aggregates": aggregates,
        }

    def gratuity(self, employee, exit_row):
        s = self.s
        refs = s.base_refs(employee) + [s.ref("exits", exit_row)]
        keys = [("gratuity-rules", k) for k in ("formula", "part_year_counting", "eligibility_order",
                "maximum_gratuity_inr", "wage_base_scope")]
        kind = s.employees[employee]["employment_type"].replace("-", "_").replace(" ", "_")
        minimum_key = f"minimum_service_{kind}_years"
        minimum = s.rule("gratuity-rules", minimum_key)
        keys.append(("gratuity-rules", minimum_key))
        rules = s.rule_refs(*keys)
        joining, last = parse_date(s.employees[employee]["joining_date"]), parse_date(exit_row["last_working_day"])
        year_months = len(calendar.month_name[1:])
        actual_months = (last.year - joining.year) * year_months + last.month - joining.month
        if add_months(joining, actual_months) > last:
            actual_months -= 1
        years, months = divmod(actual_months, year_months)
        days = (last - add_months(joining, actual_months)).days
        boundary = add_months(joining, minimum * year_months)
        ordering = s.rule("gratuity-rules", "eligibility_order")
        proximity = int(numbers(ordering["informational_flag_condition"])[0])
        flags = []
        eligible = last >= boundary
        if not eligible and last >= add_months(boundary, -proximity):
            flags.append(ordering["informational_flag"])
        threshold = int(numbers(s.rule("gratuity-rules", "part_year_counting"))[0])
        rounded_years = years + int(last > add_months(joining, years * year_months + threshold))
        service = {"years": s.calc(years, "Actual completed service years before rounding", refs, rules, money=False),
                   "months": s.calc(months, "Actual remaining completed service months", refs, rules, money=False),
                   "days": s.calc(days, "Actual remaining service days", refs, rules, money=False)}
        if not eligible:
            return {"status": "Not applicable", "service": service, "flags": flags,
                    "amount": s.calc(0, "No gratuity because actual service is below the minimum before part-year rounding", refs, rules, flags=flags)}
        operands = numbers(s.rule("gratuity-rules", "formula"))
        if len(operands) != 2:
            raise RuleError("Gratuity formula operands are not uniquely defined")
        base = self.p.components(employee)["basic"] + self.p.components(employee)["da"]
        raw = operands[0] / operands[1] * base * rounded_years
        amount = min(raw, dec(s.rule("gratuity-rules", "maximum_gratuity_inr")))
        return {"status": "Calculated; needs HR approval", "service": service, "flags": flags,
                "calculation_years": s.calc(rounded_years, "Completed years plus an eligible part-year longer than the configured rounding boundary", refs, rules, money=False),
                "amount": s.calc(amount, "Configured gratuity numerator divided by denominator times last drawn Basic plus DA times calculation service years, limited to the configured cap", refs, rules)}

    def due(self, employee, exit_row, component, applicable=True):
        s = self.s
        refs = s.base_refs(employee) + [s.ref("exits", exit_row)]
        rules = s.rule_refs(("settlement-rules", component), ("settlement-rules", "due_date_wording"))
        policy = s.rule("settlement-rules", component)
        due = policy.get("due")
        if not applicable or due is None:
            return s.calc(None, "No separate applicable due date for this non-payable or deduction component", refs, rules,
                          COMPLETE, money=False)
        last = parse_date(exit_row["last_working_day"])
        if component == "gratuity":
            rules += s.rule_refs(("settlement-rules", "gratuity_payable_trigger"), ("gratuity-rules", "payment_due"))
            s.rule("settlement-rules", "gratuity_payable_trigger")
            if s.rule("gratuity-rules", "payment_due")["within_days"] != due["within_days"]:
                raise RuleError("The two gratuity deadline rules disagree")
            result = last + timedelta(days=1 + due["within_days"])
            formula = "Day after the last working day, plus the configured days from becoming payable; applicable due date, not payment date"
        else:
            cal = s.rule("settlement-rules", "working_day_calendar")
            rules += s.rule_refs(("settlement-rules", "working_day_calendar"))
            result, counted = last, 0
            while counted < due["within_days"]:
                result += timedelta(days=1)
                if calendar.day_name[result.weekday()] in cal["working_days"] and result.isoformat() not in cal["holidays"]:
                    counted += 1
            formula = "Count the configured working days from the next working day after the last working day; applicable due date, not payment date"
        return s.calc(result, formula, refs, rules, money=False)

    def settlement(self, employee):
        s = self.s
        exit_row = s.one("exits", employee)
        if exit_row is None:
            raise ValueError("Settlement requires an exit record")
        last = parse_date(exit_row["last_working_day"])
        refs = s.base_refs(employee) + [s.ref("exits", exit_row)]
        month = last.strftime("%Y-%m")
        payroll = self.p.month(employee, month, final_day=last)
        gratuity = self.gratuity(employee, exit_row)
        leave = s.one("leave-balances", employee)
        leave_policy = s.rule("company-settings", "leave_encashment")
        leave_refs = refs + [s.ref("leave-balances", leave)]
        leave_rules = s.rule_refs(("company-settings", "leave_encashment"), ("settlement-rules", "leave_encashment"))
        if leave is None or leave["encashable_days"] is None:
            encashment = s.blocked("Leave encashment needs the recorded encashable balance", leave_refs, leave_rules)
        else:
            leave_days = min(leave["encashable_days"], leave_policy["maximum_days"])
            base_key = leave_policy["base"].lower()
            encashment = s.calc(dec(leave_days) * self.p.components(employee)[base_key] / leave_policy["divisor"],
                                "Lower of recorded encashable leave and policy maximum, times salary base divided by the policy divisor", leave_refs, leave_rules)
        notice_policy = s.rule("company-settings", "notice_recovery")
        notice_rules = s.rule_refs(("company-settings", "notice_recovery"), ("company-settings", "notice_period_days"),
                                   ("settlement-rules", "notice_shortfall_recovery"))
        if exit_row["notice_period_required"] != s.rule("company-settings", "notice_period_days"):
            raise RuleError("Notice record disagrees with the company notice rule")
        if exit_row["notice_waived"] is None:
            notice = s.blocked("Notice recovery needs HR's recorded waiver decision", refs, notice_rules, HR)
        elif exit_row["notice_waived"]:
            if not notice_policy["hr_can_waive"]:
                raise RuleError("Recorded notice waiver is not permitted by company policy")
            notice = s.calc(0, "Recorded HR waiver removes the notice shortfall recovery", refs, notice_rules)
        elif exit_row["notice_period_served"] is None:
            notice = s.blocked("Notice recovery needs recorded served notice days", refs, notice_rules)
        else:
            shortfall = max(0, exit_row["notice_period_required"] - exit_row["notice_period_served"])
            if notice_policy["base"] != "monthly gross":
                raise RuleError("Unsupported notice recovery base")
            notice = s.calc(dec(shortfall) * sum(self.p.components(employee).values()) / notice_policy["divisor"],
                            "Required notice days less served days, not below zero, times monthly gross divided by the policy divisor", refs, notice_rules)
        recoveries = s.records("recoveries", employee)
        collection_ref = s.ref("recoveries", record_id="$", fields=[f"employee_id={employee}"])
        advances = [row for row in recoveries if row["type"] in {"advance", "loan"}]
        advance_rules = s.rule_refs(("settlement-rules", "loan_and_advance_recovery"),
                                    ("settlement-rules", "salary_advance_recovery_treatment"))
        s.rule("settlement-rules", "salary_advance_recovery_treatment")
        advance = s.total([s.calc(row["amount"], "Recorded salary advance recovery deducted from settlement payables",
                                  refs + [s.ref("recoveries", row)], advance_rules) for row in advances],
                          "Sum of recorded advance and loan recovery lines; no records means no recorded recovery",
                          refs + [collection_ref], advance_rules)
        asset_rows = [row for row in recoveries if row["type"] == "asset"]
        permission = s.rule("settlement-rules", "asset_recovery_permission")
        asset_rules = s.rule_refs(("settlement-rules", "asset_recovery"), ("settlement-rules", "asset_recovery_permission"),
                                  ("settlement-rules", "pending_clearance_holds"))
        asset_lines, reasons = [], []
        for row in asset_rows:
            clearance = s.one("clearances", employee, clearance_id=row["clearance_id"])
            asset_refs = refs + [s.ref("recoveries", row), s.ref("clearances", clearance)]
            if clearance is None:
                amount = s.blocked("Asset recovery needs the referenced clearance", asset_refs, asset_rules)
                reasons.append("Asset clearance record missing")
            elif clearance["status"] == permission["pending_clearance_status"]:
                amount = s.blocked("Asset recovery is unresolved while the asset clearance is pending; recorded exposure is not a permitted deduction", asset_refs,
                                   asset_rules, INCOMPLETE, ["Asset recovery unresolved"])
                reasons.append("Asset clearance pending; final net incomplete")
            elif clearance["status"] == permission["allowed_clearance_status"]:
                amount = s.calc(row["amount"], "Recorded recovery allowed because the asset is marked not returned", asset_refs, asset_rules)
            elif clearance["status"] == "complete":
                amount = s.calc(0, "Asset clearance is complete; recovery is not permitted by the not-returned rule", asset_refs, asset_rules)
            else:
                amount = s.blocked("Asset clearance status has no verified recovery treatment", asset_refs, asset_rules, UNVERIFIED)
                reasons.append("Asset clearance status not covered by the rule")
            asset_lines.append(amount)
        asset = s.total(asset_lines, "Sum of allowed recorded asset recovery lines; pending recovery prevents this total", refs + [collection_ref], asset_rules)
        components = {}
        def component(key, amount, applicable=True, status="Calculated; needs HR approval", reason=None):
            policy = s.rule("settlement-rules", key)
            components[key] = {"classification": policy["classification"], "amount": amount,
                               "applicable_due_date": self.due(employee, exit_row, key, applicable),
                               "status": status, "hold_or_unresolved_reason": reason,
                               "held": False, "certainty": amount["certainty"]}
        component("final_month_salary", payroll["earnings"]["gross"])
        components["final_month_salary"]["clearance_rule"] = s.rule_ref("settlement-rules", "separation_wages_clearance_hold")
        component("leave_encashment", encashment)
        component("gratuity", gratuity["amount"], gratuity["status"] != "Not applicable", gratuity["status"])
        components["gratuity"]["service"] = gratuity["service"]
        components["gratuity"]["flags"] = gratuity["flags"]
        if "calculation_years" in gratuity:
            components["gratuity"]["calculation_years"] = gratuity["calculation_years"]
        component("notice_shortfall_recovery", notice)
        component("loan_and_advance_recovery", advance)
        component("asset_recovery", asset, status="Unresolved" if asset["value"] is None else "Calculated; needs HR approval",
                  reason="; ".join(reasons) or None)
        exemption_lines, taxable_lines = [], []
        for key, amount in (("gratuity_tax_exemption", gratuity["amount"]), ("leave_encashment_tax_exemption", encashment)):
            rule = s.rule("tax-rules", key)
            rule_refs = s.rule_refs(("tax-rules", key))
            if not rule["available_under_new_tax_regime"]:
                raise RuleError("Exemption is not available in the configured regime")
            # This fixture records a resignation date, which supplies the exit type.
            exit_type = "resignation" if exit_row.get("resignation_date") else None
            applicable = "exit_types" not in rule or exit_type in rule["exit_types"]
            if amount["value"] is None:
                exempt = s.blocked("Tax exemption requires a known component amount", refs, rule_refs, amount["certainty"], amount["flags"])
            else:
                exempt = s.calc(min(amount["value"], rule["exemption_limit_inr"]) if applicable else 0,
                                "Lower of actual component and exemption limit when the configured exit type qualifies", refs + amount["inputs"], rule_refs + amount["rule_ids"])
            exemption_lines.append(exempt)
            taxable_lines.append(s.total([amount, exempt], "Rounded component less its permitted exemption", signs=[1, -1]))
        taxable_extra = s.total(taxable_lines, "Sum of taxable settlement components beyond final salary")
        if taxable_extra["value"] == 0:
            tds = payroll["tds"]["amount"]
        else:
            # No fixture currently needs this, but never silently ignore taxable excess.
            s.ambiguity("AMB-06", "Taxable settlement excess needs a verified receipt-month withholding allocation, "
                        "including tax-year remaining months versus the employee's last payroll.", employee)
            tds = s.blocked("Settlement excess TDS needs a verified final-payroll allocation rule", refs, taxable_extra["rule_ids"], UNVERIFIED, ["AMB-06"])
        total = s.total([components[k]["amount"] for k in ("final_month_salary", "leave_encashment", "gratuity")],
                        "Sum of rounded settlement earning components")
        deductions = s.total([notice, advance, asset, payroll["pf"]["employee"], tds],
                             "Sum of rounded notice, recorded recoveries, employee PF and TDS; stop if any component is unresolved")
        result = {"employee_id": employee, "proposal_status": "Needs HR approval; no payment generated",
                  "components": components, "employee_pf": payroll["pf"]["employee"], "tds": tds,
                  "tax_exemptions": exemption_lines, "taxable_additional_components": taxable_extra,
                  "gross_payables": total, "total_deductions": deductions}
        result["recoveries_total"] = s.total([notice, advance, asset],
            "Sum of rounded notice, loan or advance, and asset recoveries only; exclude employee PF and TDS")
        known = [line for line in (notice, advance, asset) if line["value"] is not None]
        result["known_recoveries_subtotal"] = s.total(known,
            "Sum of known rounded recovery lines only; exclude unresolved recoveries", refs,
            notice_rules + advance_rules + asset_rules)
        if asset["value"] is None:
            result["recoveries_total"]["certainty"] = INCOMPLETE
            result["known_recoveries_subtotal"]["flags"] = unique(
                result["known_recoveries_subtotal"]["flags"] + ["Excludes unresolved asset recovery"])
        if deductions["value"] is not None and total["value"] is not None:
            result["final_net"] = s.total([total, deductions], "Rounded settlement payables less rounded settlement deductions", signs=[1, -1])
            result["net_direction"] = "Recoverable from employee" if result["final_net"]["value"] < 0 else "Payable after HR approval"
            result["certainty"] = completeness(result)
        else:
            result["certainty"] = INCOMPLETE if asset["value"] is None else completeness(result)
            result["final_net_not_generated_reason"] = "One or more settlement components are unknown; unknowns are not treated as zero"
        return result

    def compare(self, employee, before, after):
        s = self.s
        a, b = self.p.ledger[employee, before], self.p.ledger[employee, after]
        lines = {key: s.total([b["earnings"]["lines"][key], a["earnings"]["lines"][key]],
                              f"Later rounded {key} earnings less earlier rounded {key} earnings", signs=[1, -1])
                 for key in a["earnings"]["lines"]}
        employee_pf_change = s.total([b["pf"]["employee"], a["pf"]["employee"]],
                                    "Later employee PF less earlier employee PF", signs=[1, -1])
        tds_change = s.total([b["tds"]["amount"], a["tds"]["amount"]], "Later TDS less earlier TDS", signs=[1, -1])
        result = {"employee_id": employee, "before_month": before, "after_month": after,
                  "before": a, "after": b, "earning_component_changes": lines,
                  "gross_change": s.total(lines.values(), "Sum of rounded earning component differences"),
                  "employee_pf_change": employee_pf_change, "tds_change": tds_change,
                  "net_change": s.total([b["net_pay"], a["net_pay"]], "Later net pay less earlier net pay", signs=[1, -1]),
                  "no_earning_component_change": all(line["value"] == 0 for line in lines.values())}
        query = s.one("queries", employee)
        if query:
            result["existing_query"] = {"query_id": query["query_id"], "status": query["status"], "sent_by_engine": False}
        result["certainty"] = completeness(result)
        result["reasons"] = self.comparison_reasons(result)
        return result

    def comparison_reasons(self, result):
        """Rank known net effects, not deduction increases, by absolute magnitude."""
        s = self.s
        employee = result["employee_id"]
        a, b = result["before"], result["after"]
        earlier = s.one("attendance", employee, month=result["before_month"])
        later = s.one("attendance", employee, month=result["after_month"])
        joining = parse_date(s.employees[employee]["joining_date"])
        exit_row = s.one("exits", employee)
        full_employment = joining <= month_bounds(result["before_month"])[0] and (
            exit_row is None or parse_date(exit_row["last_working_day"]) >= month_bounds(result["after_month"])[1])
        lop_changed = earlier and later and full_employment and (
            dec(earlier["lop_days"]) / earlier["days_in_month"] != dec(later["lop_days"]) / later["days_in_month"])
        ceiling_ids = lambda slip: {r["rule_id"] for band in slip["pf"]["segments"]
                                   for r in band["pf_wage"]["rule_ids"] if "#wage_ceiling_" in r["rule_id"]}
        pf_type = "PF ceiling change" if ceiling_ids(a) != ceiling_ids(b) else "Employee PF change"
        reasons = []
        for kind, field, sign in (("LOP" if lop_changed else "Salary earnings change", "gross_change", 1),
                                  (pf_type, "employee_pf_change", -1), ("TDS change", "tds_change", -1)):
            line = result[field]
            if line["value"] == 0:
                continue
            effect = (s.blocked(f"Take-home effect of {kind}; required comparison value is unknown",
                                line["inputs"], line["rule_ids"], line["certainty"], line["flags"])
                      if line["value"] is None else
                      s.calc(dec(line["value"]) * sign,
                             f"Take-home effect of {kind}: earning change increases net; deduction change has the opposite sign",
                             line["inputs"], line["rule_ids"], flags=line["flags"]))
            if kind == "PF ceiling change":
                effect["flags"] = unique(effect["flags"] + [
                    "PF effect includes earned wage after LOP and dated ceiling segments"])
            reasons.append({"type": kind, "effect_amount": effect,
                            "source_references": effect["inputs"]})
        # Equal magnitudes retain the deterministic input order; unknown effects are not ranked.
        return sorted(reasons, key=lambda r: (r["effect_amount"]["value"] is None,
                      -abs(r["effect_amount"]["value"] or 0)))

    def authorize(self, user_id, employee):
        # Authorize before any lookup of the target employee's records or calculations.
        users = [row for row in self.s.mock["users"] if row["user_id"] == user_id]
        if len(users) != 1:
            return {"status": "Permission denied"}
        user = users[0]
        allowed = employee in user["allowed_employee_ids"]
        if user["role"] == "Employee":
            allowed = allowed and employee == user.get("employee_id")
        elif user["role"] != "HR Admin":
            allowed = False
        return {"status": "Authorized"} if allowed else {"status": "Permission denied"}
