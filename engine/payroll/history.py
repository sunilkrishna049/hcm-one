"""Salary lines, dated PF segments, annual tax projection and payslip history."""
from __future__ import annotations

from datetime import timedelta

from .core import (COMPLETE, INCOMPLETE, UNVERIFIED, RuleError, completeness,
                   dec, month_bounds, month_range, parse_date)


class Payroll:
    def __init__(self, store):
        self.s = store
        self.ledger = {}
        self.payslips = []
        self.failures = []
        self.skipped = []

    def components(self, employee, hike=None):
        record = self.s.structures[employee]
        raw = record["monthly_components"]
        if raw["others"]:
            raise RuleError("Additional salary component schema is not defined in this fixture")
        result = {key: dec(value) for key, value in raw.items() if key != "others"}
        if hike:
            self.s.rule("company-settings", "hike_allocation")
            result = {key: value * (1 + dec(hike["hike_percent"]) / 100)
                      for key, value in result.items()}
        return result

    def earnings(self, employee, month, hike=None, final_day=None):
        s = self.s
        attendance = s.one("attendance", employee, month=month)
        refs = s.base_refs(employee)
        refs += [s.ref("attendance", attendance, record_id=(attendance or {}).get(
                    "attendance_id", f"missing:{employee}:{month}"))]
        rules = s.rule_refs(("settlement-rules", "final_month_days"))
        if hike:
            refs += [s.ref("salary-revisions", hike)]
            rules += s.rule_refs(("company-settings", "hike_allocation"),
                                 ("company-settings", "mid_month_hike"))
        raw = self.components(employee)
        if attendance is None:
            blocked = s.blocked("Monthly component times paid calendar days divided by days in the month; "
                                "attendance is missing", refs, rules, flags=["Attendance missing"])
            return {"lines": {key: dict(blocked) for key in raw}, "gross": dict(blocked),
                    "paid_days": s.blocked("Calendar days less recorded LOP; attendance missing", refs,
                                           rules), "month": month}
        first, last = month_bounds(month)
        s.rule("settlement-rules", "final_month_days")
        if attendance["days_in_month"] != last.day or attendance["lop_days"] is None:
            raise RuleError("Attendance calendar or LOP is invalid")
        start = max(first, parse_date(s.employees[employee]["joining_date"]))
        end = min(last, final_day) if final_day else last
        eligible = max(0, (end - start).days + 1)
        lop = attendance["lop_days"]
        if not 0 <= lop <= eligible:
            raise RuleError("Recorded LOP is outside eligible employment days")
        paid = eligible - lop
        paid_object = s.calc(paid, "Eligible calendar days through the period end less recorded LOP days",
                             refs, rules, money=False)
        values = raw
        if hike:
            revised = self.components(employee, hike)
            effective = parse_date(hike["effective_date"])
            if effective > start and effective <= end and lop:
                s.rule("pf-rules", "lop_across_dated_segments")
                rules += s.rule_refs(("pf-rules", "lop_across_dated_segments"))
            if effective <= start:
                values = revised
            elif effective <= end:
                before = (effective - start).days
                after = (end - effective).days + 1
                values = {k: (raw[k] * before + revised[k] * after) / eligible for k in raw}
        lines = {key: s.calc(value * paid / last.day,
                             f"Monthly {key.replace('_', ' ')} times paid calendar days divided by calendar days in the month",
                             refs, rules) for key, value in values.items()}
        return {"lines": lines, "gross": s.total(lines.values(), "Sum of rounded earning lines"),
                "paid_days": paid_object, "month": month}

    def pf(self, employee, month, hike=None, final_day=None):
        s = self.s
        refs = s.base_refs(employee)
        attendance = s.one("attendance", employee, month=month)
        refs += [s.ref("attendance", attendance, record_id=(attendance or {}).get(
                       "attendance_id", f"missing:{employee}:{month}"))]
        keys = [("pf-rules", k) for k in ("pf_wage_formula", "employee_contribution_rate_percent",
                "employer_contribution_rate_percent", "eps_allocation", "company_pf_basis",
                "mid_month_ceiling_change", "pf_wage_with_lop", "lop_across_dated_segments")]
        rules = s.rule_refs(*keys)
        if hike:
            refs += [s.ref("salary-revisions", hike)]
            rules += s.rule_refs(("company-settings", "hike_allocation"),
                                 ("company-settings", "mid_month_hike"))
        if attendance is None:
            certainty = INCOMPLETE
            flag = "Attendance missing"
            blocked = s.blocked("PF needs a verified wage basis and eligible days", refs, rules,
                                certainty, [flag])
            return {"employee": dict(blocked), "employer": dict(blocked), "eps": dict(blocked),
                    "epf": dict(blocked), "segments": [], "certainty": certainty}
        s.rule("pf-rules", "pf_wage_formula")
        if s.structures[employee]["pf_wage_components"] != ["basic", "da"]:
            raise RuleError("Salary PF components disagree with the Basic plus DA rule")
        if "capped" not in s.rule("pf-rules", "company_pf_basis").lower():
            raise RuleError("Unsupported company PF basis")
        s.rule("pf-rules", "mid_month_ceiling_change")
        s.rule("pf-rules", "pf_wage_with_lop")
        s.rule("pf-rules", "lop_across_dated_segments")
        first, last = month_bounds(month)
        start = max(first, parse_date(s.employees[employee]["joining_date"]))
        end = min(last, final_day) if final_day else last
        ceilings = [(key, row) for key, row in s.rule_files["pf-rules"].items()
                    if key.startswith("wage_ceiling_")]
        raw = self.components(employee)
        revised = self.components(employee, hike) if hike else raw
        eligible = max(0, (end - start).days + 1)
        lop = attendance["lop_days"]
        if attendance["days_in_month"] != last.day or lop is None or not 0 <= lop <= eligible:
            raise RuleError("PF attendance calendar or LOP is invalid")
        monthly_values = raw
        if hike:
            effective = parse_date(hike["effective_date"])
            if effective <= start:
                monthly_values = revised
            elif effective <= end:
                before, after = (effective - start).days, (end - effective).days + 1
                monthly_values = {k: (raw[k] * before + revised[k] * after) / eligible for k in raw}
        monthly_earned_wage = sum(monthly_values[k] for k in s.structures[employee]["pf_wage_components"]) * (eligible - lop) / last.day
        earned_wage_object = s.calc(monthly_earned_wage,
                                    "Monthly Basic plus DA, weighted for any dated hike, times paid days divided by month calendar days", refs, rules)
        bands = []
        for key, row in ceilings:
            a = max(start, parse_date(row["effective_from"])) if row["effective_from"] else start
            b = min(end, parse_date(row["effective_to"])) if row["effective_to"] else end
            if a > b:
                continue
            cuts = [a, b + timedelta(days=1)]
            if hike and a < parse_date(hike["effective_date"]) <= b:
                cuts.insert(1, parse_date(hike["effective_date"]))
            for segment_start, next_start in zip(cuts, cuts[1:]):
                segment_end = next_start - timedelta(days=1)
                days = (segment_end - segment_start).days + 1
                ceiling = s.rule("pf-rules", key, segment_start)
                earned_segment = monthly_earned_wage * days / last.day
                prorated_ceiling = dec(ceiling) * days / last.day
                wage = min(earned_segment, prorated_ceiling)
                band_rules = rules + s.rule_refs(("pf-rules", key))
                emp = s.calc(wage * dec(s.rule("pf-rules", "employee_contribution_rate_percent")) / 100,
                             "Lower of evenly allocated earned segment PF wage and pro-rated ceiling, times employee contribution rate",
                             refs, band_rules)
                employer = s.calc(wage * dec(s.rule("pf-rules", "employer_contribution_rate_percent")) / 100,
                                  "Lower of evenly allocated earned segment PF wage and pro-rated ceiling, times employer contribution rate",
                                  refs, band_rules)
                eps = s.calc(wage * dec(s.rule("pf-rules", "eps_allocation")["rate_percent"]) / 100,
                             "Lower of evenly allocated earned segment PF wage and pro-rated ceiling, times EPS rate",
                             refs, band_rules)
                epf = s.total([employer, eps], "Rounded employer contribution less rounded EPS allocation", signs=[1, -1])
                bands.append({"start": s.calc(segment_start, "First eligible day in this PF rule segment", refs,
                                               band_rules, money=False),
                              "end": s.calc(segment_end, "Last eligible day in this PF rule segment", refs,
                                             band_rules, money=False),
                              "days": s.calc(days, "Inclusive calendar days in the PF segment", refs,
                                              band_rules, money=False),
                              "earned_pf_wage": s.calc(earned_segment, "Month earned PF wage times segment calendar days divided by month calendar days", refs, band_rules),
                              "prorated_ceiling": s.calc(prorated_ceiling, "Applicable monthly ceiling times segment calendar days divided by month calendar days", refs, band_rules),
                              "pf_wage": s.calc(wage, "Lower of evenly allocated earned segment PF wage and the pro-rated segment ceiling", refs, band_rules),
                              "employee": emp, "employer": employer, "eps": eps, "epf": epf})
        if sum(band["days"]["value"] for band in bands) != max(0, (end - start).days + 1):
            raise RuleError("Dated PF ceilings overlap or leave a gap")
        result = {key: s.total([band[key] for band in bands], f"Sum of rounded {key} PF segment lines")
                  for key in ("employee", "employer", "eps", "epf")}
        result["segments"] = bands
        result["monthly_earned_pf_wage"] = earned_wage_object
        result["certainty"] = completeness(result)
        return result

    def yearly_tax(self, projected, refs):
        s = self.s
        rules = s.rule_refs(*[("tax-rules", key) for key in ("regime_scope", "tax_year", "slabs",
                 "standard_deduction_inr", "rebate", "health_and_education_cess", "marginal_relief_scope")])
        if s.rule("tax-rules", "tax_year")["year"] != s.company["financial_year"]:
            raise RuleError("Tax-year rules do not match the mock company's financial year")
        standard = s.calc(s.rule("tax-rules", "standard_deduction_inr"),
                          "Apply the standard deduction once for this person and tax year", refs, rules)
        taxable = s.total([projected, standard], "Projected yearly gross income less one standard deduction", signs=[1, -1])
        if taxable["value"] is None:
            blocked = s.blocked("Yearly tax requires complete projected income", refs + projected["inputs"],
                                rules, taxable["certainty"], taxable["flags"])
            return {"projected_gross": projected, "standard_deduction": standard,
                    "taxable_income": taxable, "slab_tax": blocked, "cess": dict(blocked), "yearly_tax": dict(blocked)}
        taxable["value"] = max(0, taxable["value"])
        bands = []
        lower = dec(0)
        for slab in s.rule("tax-rules", "slabs"):
            upper = slab["income_to_inr"]
            # The recorded integer bands are continuous bracket boundaries, not flat rates.
            amount = max(dec(0), dec(taxable["value"]) - lower)
            if upper is not None:
                amount = min(amount, dec(upper) - lower)
            bands.append(s.calc(amount * dec(slab["rate_percent"]) / 100,
                                "Income within this tax bracket times the bracket rate", refs,
                                rules))
            if upper is not None:
                lower = dec(upper)
        base = s.total(bands, "Sum of rounded tax bracket lines")
        rebate = s.rule("tax-rules", "rebate")
        if taxable["value"] <= rebate["taxable_income_limit_inr"]:
            base = s.calc(rebate["tax_up_to_limit_inr"], "Yearly tax after the configured rebate within the income limit", refs, rules)
        cess_rule = s.rule("tax-rules", "health_and_education_cess")
        cess = (s.calc(dec(base["value"]) * dec(cess_rule["rate_percent"]) / 100,
                       "Rounded tax after rebate times the cess rate", refs, rules) if base["value"] is not None else
                s.blocked("Cess requires known tax after rebate", refs, rules, base["certainty"], base["flags"]))
        return {"projected_gross": projected, "standard_deduction": standard, "taxable_income": taxable,
                "tax_brackets": bands, "slab_tax": base, "cess": cess,
                "yearly_tax": s.total([base, cess], "Rounded tax after rebate plus rounded cess")}

    def tds(self, employee, month, current_earnings, hike=None, one_time=None):
        s = self.s
        refs = s.base_refs(employee)
        if hike:
            refs += [s.ref("salary-revisions", hike)]
        rules = s.rule_refs(*[("tax-rules", key) for key in ("monthly_tds_formula", "previous_employer_income",
                              "negative_remaining_tax", "last_month_tds", "regime_scope")])
        regime = s.rule("tax-rules", "regime_scope")["regime"]
        if s.employees[employee]["tax_regime_selected"] != regime:
            raise RuleError("Selected tax regime is outside the configured scope")
        start, _ = month_bounds(month)
        prior = [entry for (eid, previous), entry in self.ledger.items() if eid == employee and previous < month]
        past_lines = [entry["earnings"]["gross"] for entry in prior]
        prior_tds_lines = [entry["tds"]["amount"] for entry in prior]
        expected = []
        exit_row = s.one("exits", employee)
        exit_date = parse_date(exit_row["last_working_day"]) if exit_row else s.year_end
        if exit_row:
            refs += [s.ref("exits", exit_row)]
        joining = parse_date(s.employees[employee]["joining_date"])
        for earlier in month_range(s.year_start, start - timedelta(days=1)):
            a, b = month_bounds(earlier)
            if b < joining or a > exit_date or (employee, earlier) in self.ledger:
                continue
            run = next((r for r in s.mock["payroll-runs"] if r["month"] == earlier), None)
            prior_refs = refs + [s.ref("payroll-runs", run, record_id=(run or {}).get("payroll_run_id", f"missing:{earlier}"))]
            unknown = s.blocked("Prior actual payroll is unavailable; projected income must not omit the month",
                                prior_refs, rules, flags=[f"Prior processed payroll unavailable for {earlier}"])
            past_lines.append(unknown)
            prior_tds_lines.append(dict(unknown))
        gross_lines = past_lines + [current_earnings["gross"]]
        for future in month_range(start, s.year_end):
            if future <= month or month_bounds(future)[0] > exit_date:
                continue
            a, b = month_bounds(future)
            eligible_end = min(b, exit_date)
            # BR-4.1 projection uses the unmodified recurring salary. Future LOP is not invented.
            projection_rules = s.rule_refs(("settlement-rules", "final_month_days"))
            values = self.components(employee)
            if hike and parse_date(hike["effective_date"]) <= a:
                values = self.components(employee, hike)
                projection_rules += s.rule_refs(("company-settings", "hike_allocation"))
            elif hike and parse_date(hike["effective_date"]) <= eligible_end:
                effective = parse_date(hike["effective_date"])
                before, after = (effective - a).days, (eligible_end - effective).days + 1
                revised = self.components(employee, hike)
                values = {key: (values[key] * before + revised[key] * after) / (before + after) for key in values}
                projection_rules += s.rule_refs(("company-settings", "hike_allocation"), ("company-settings", "mid_month_hike"))
            expected.append(s.calc(sum(values.values()) * ((eligible_end - a).days + 1) / b.day,
                                   "Expected recurring gross salary for the remaining employment month", refs, projection_rules))
        gross_lines += expected
        if one_time is not None:
            gross_lines.append(one_time)
        declaration_rule = s.rule("tax-rules", "previous_employer_income")
        declarations = [row for row in s.records("declarations", employee)
                        if row["financial_year"] == s.company["financial_year"]
                        and row["proof_status"] == declaration_rule["declaration_status"]
                        and row["applied_from_payroll_month"] <= month]
        previous_tds = []
        for row in declarations:
            row_refs = [s.ref("declarations", row)]
            refs += row_refs
            gross_lines.append(s.calc(row["declared_amount"], "Accepted previous-employer gross income included once", row_refs, rules))
            previous_tds.append(s.calc(row["previous_employer_tds_already_deducted"],
                                       "Accepted declared tax already deducted by the previous employer", row_refs, rules))
        projection = s.total(gross_lines, "Rounded actual gross so far plus expected remaining salary and accepted prior-employer gross", refs, rules)
        details = self.yearly_tax(projection, refs)
        northwind_tds = s.total(prior_tds_lines,
                                "Sum of previously calculated Northwind monthly TDS, excluding previous-employer TDS",
                                refs, rules)
        declared_tds = s.total(previous_tds,
                               "Sum of accepted previous-employer TDS declarations applied by this payroll month",
                               refs, rules)
        tax_so_far = s.total(prior_tds_lines + previous_tds,
                             "Sum of previously calculated monthly TDS and accepted previous-employer TDS", refs, rules)
        remaining_months = len(list(month_range(start, s.year_end)))
        remaining = s.total([details["yearly_tax"], tax_so_far], "Projected yearly tax less TDS already deducted", signs=[1, -1])
        if remaining["value"] is None:
            amount = s.blocked("Remaining yearly tax divided by remaining tax-year months including this month", refs + remaining["inputs"],
                               remaining["rule_ids"] + rules, remaining["certainty"], remaining["flags"])
        elif remaining["value"] < 0:
            rule = s.rule("tax-rules", "negative_remaining_tax")
            amount = s.calc(rule["monthly_tds_inr"], "Configured zero TDS when tax already deducted exceeds projected tax", refs + remaining["inputs"],
                            rules + remaining["rule_ids"], flags=[rule["flag"]])
        else:
            s.rule("tax-rules", "monthly_tds_formula")
            if remaining_months == 1:
                s.rule("tax-rules", "last_month_tds")
            amount = s.calc(dec(remaining["value"]) / remaining_months,
                            "Remaining yearly tax divided by remaining tax-year months including the current month", refs + remaining["inputs"],
                            remaining["rule_ids"] + rules)
        return {**details, "tax_already_deducted": tax_so_far,
                "northwind_tds_already_deducted": northwind_tds,
                "previous_employer_tds": declared_tds,
                "remaining_yearly_tax": remaining,
                "remaining_months": s.calc(remaining_months, "Calendar payroll months from the current month to tax-year end", refs,
                                           rules, money=False), "amount": amount}

    def month(self, employee, month, final_day=None):
        earnings = self.earnings(employee, month, final_day=final_day)
        pf = self.pf(employee, month, final_day=final_day)
        tds = self.tds(employee, month, earnings)
        deductions = self.s.total([pf["employee"], tds["amount"]], "Rounded employee PF plus rounded monthly TDS")
        net = self.s.total([earnings["gross"], deductions], "Rounded gross pay less total employee deductions", signs=[1, -1])
        row = {"record_id": f"PAY-{employee}-{month}", "employee_id": employee, "month": month,
               "salary_basis": "Original mock salary structure; pending revisions not applied",
               "earnings": earnings, "pf": pf, "tds": tds, "total_deductions": deductions,
               "net_pay": net}
        row["certainty"] = completeness(row)
        return row

    def generate_history(self):
        for employee, record in self.s.employees.items():
            for month in self.s.processed:
                _, end = month_bounds(month)
                if end < parse_date(record["joining_date"]):
                    self.skipped.append({"employee_id": employee, "month": month,
                                         "reason": "Not employed in this month"})
                    continue
                row = self.month(employee, month)
                self.ledger[employee, month] = row
                if row["certainty"] == COMPLETE:
                    self.payslips.append(row)
                else:
                    flags = []
                    def collect(item):
                        if isinstance(item, dict):
                            if "formula" in item:
                                if item["value"] is None:
                                    flags.append({"reason": item["formula"], "certainty": item["certainty"],
                                                  "flags": item["flags"]})
                            else:
                                for child in item.values():
                                    collect(child)
                        elif isinstance(item, list):
                            for child in item:
                                collect(child)
                    collect(row)
                    self.failures.append({"employee_id": employee, "month": month,
                                          "certainty": row["certainty"], "reasons": flags,
                                          "partial_calculation_id": row["record_id"]})
        return self.payslips
