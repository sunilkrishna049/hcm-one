"""Copied display operands and explicitly calculated display-only quantities."""
from __future__ import annotations

from copy import deepcopy
from decimal import Decimal

from .core import COMPLETE, HR, INCOMPLETE, dec
from .flows import bonus_rating_rate


def native(value):
    """JSON conversion only; do not round a copied source value."""
    if isinstance(value, Decimal):
        return float(value)
    return deepcopy(value)


class DisplayInputs:
    def __init__(self, payroll):
        self.p = payroll
        self.s = payroll.s

    def copied(self, file, row, field, *, record_id=None, certainty=None):
        ref = self.s.ref(file, row, record_id=record_id)
        value = row.get(field) if row is not None else None
        return {"value": native(value), **ref, "source_field": field,
                "certainty": certainty or (COMPLETE if value is not None else INCOMPLETE)}

    def calculated(self, calculation, scenario, field):
        # The wrapper identifies the exported record. Its nested calculation keeps
        # the unchanged six-field calculation contract and all input provenance.
        return {"value": calculation["value"],
                "source_file": f"data/generated/scenarios/{scenario}.json",
                "record_id": scenario, "source_field": f"display_inputs/{field}",
                "certainty": calculation["certainty"], "calculation": deepcopy(calculation)}

    def attendance(self, employee, months):
        result = {}
        for month in months:
            row = self.s.one("attendance", employee, month=month)
            record_id = (row or {}).get("attendance_id", f"missing:{employee}:{month}")
            result[month] = {
                "lop_days": self.copied("attendance", row, "lop_days", record_id=record_id),
                "calendar_days": self.copied("attendance", row, "days_in_month", record_id=record_id),
            }
        return result

    def hike(self, result, scenario):
        s = self.s
        employee = result["employee_id"]
        revision = s.one("salary-revisions", employee)
        structure = s.structures[employee]
        raw = structure["monthly_components"]
        refs = s.base_refs(employee) + [s.ref("salary-revisions", revision)]
        rules = s.rule_refs(("company-settings", "hike_allocation"))
        revised = self.p.components(employee, revision)
        old_lines = {key: s.calc(value, f"Recorded contractual monthly {key}",
                                 s.base_refs(employee), rules)
                     for key, value in self.p.components(employee).items()}
        new_lines = {key: s.calc(value,
                                 f"Recorded monthly {key} increased by the requested hike percentage",
                                 refs, rules) for key, value in revised.items()}
        old = {key: self.copied("salary-structures", raw, key,
                                record_id=structure["salary_structure_id"]) for key in old_lines}
        for key in old:
            old[key]["source_field"] = f"monthly_components/{key}"
        proposed = {key: self.calculated(value, scenario,
                     f"proposed_monthly_salary/components/{key}") for key, value in new_lines.items()}
        return {
            "requested_hike_percentage": self.copied("salary-revisions", revision, "hike_percent"),
            "effective_date": self.copied("salary-revisions", revision, "effective_date"),
            "old_monthly_salary": {
                "components": old,
                "total": self.calculated(s.total(old_lines.values(),
                         "Sum of rounded original contractual monthly components, without LOP"),
                         scenario, "old_monthly_salary/total")},
            "proposed_monthly_salary": {
                "components": proposed,
                "total": self.calculated(s.total(new_lines.values(),
                         "Sum of rounded proposed contractual monthly components, without LOP"),
                         scenario, "proposed_monthly_salary/total")},
            "months": self.attendance(employee, [row["month"] for row in result["months"]]),
        }

    def settlement(self, result, scenario):
        s = self.s
        employee = result["employee_id"]
        exit_row = s.one("exits", employee)
        leave = s.one("leave-balances", employee)
        policy = s.rule("company-settings", "leave_encashment")
        record = s.structures[employee]
        raw = record["monthly_components"]
        displayed = {key: self.copied("exits", exit_row, key,
                        certainty=HR if key == "notice_waived" and exit_row[key] is None else None)
                     for key in ("resignation_date", "last_working_day",
                                 "notice_period_required", "notice_period_served", "notice_waived")}
        # Select the exact source operand the engine uses; do not re-estimate leave.
        if leave is None or leave["encashable_days"] is None:
            used = self.copied("leave-balances", leave, "encashable_days",
                              record_id=(leave or {}).get("leave_balance_id", f"missing:{employee}"))
        elif leave["encashable_days"] <= policy["maximum_days"]:
            used = self.copied("leave-balances", leave, "encashable_days")
        else:
            used = {"value": native(policy["maximum_days"]),
                    "source_file": "data/rules/company-settings.json",
                    "record_id": "leave_encashment", "source_field": "value/maximum_days",
                    "certainty": COMPLETE}
        displayed["encashable_leave_days_used"] = used
        for key in ("basic", "da"):
            displayed[f"last_drawn_{key}"] = self.copied("salary-structures", raw, key,
                                                       record_id=record["salary_structure_id"])
            displayed[f"last_drawn_{key}"]["source_field"] = f"monthly_components/{key}"
        rules = s.rule_refs(("gratuity-rules", "wage_base_scope"))
        components = self.p.components(employee)
        base = s.calc(components["basic"] + components["da"],
                      "Last drawn contractual monthly Basic plus DA used for the gratuity wage base",
                      s.base_refs(employee) + [s.ref("exits", exit_row)], rules)
        displayed["last_drawn_basic_plus_da"] = self.calculated(base, scenario, "last_drawn_basic_plus_da")
        return displayed

    def bonus_employee(self, request, item):
        s = self.s
        employee = item["employee_id"]
        row = s.one("performance", employee, period=request["period"])
        record_id = (row or {}).get("performance_id", f"missing:{employee}:{request['period']}")
        if request["bonus_type"] == "quarterly_sales_incentive":
            return {key: self.copied("performance", row, key, record_id=record_id)
                    for key in ("target", "achievement")}
        rating = self.copied("performance", row, "rating", record_id=record_id)
        rates = s.rule("bonus-rules", request["bonus_type"])["rating_rates_percent"]
        rate = None if rating["value"] is None else bonus_rating_rate(rates, rating["value"])
        rate_key = str(rating["value"])
        if rate is not None and rate_key not in rates:
            rate_key = next(k for k in rates if "_to_" in k
                            and int(k.split("_to_")[0]) <= rating["value"] <= int(k.split("_to_")[1]))
        policy_rate = {"value": native(rate), "source_file": "data/rules/bonus-rules.json",
                       "record_id": request["bonus_type"],
                       "source_field": f"value/rating_rates_percent/{rate_key}" if rate is not None else None,
                       "certainty": COMPLETE if rate is not None else INCOMPLETE}
        applied = deepcopy(policy_rate)
        if item["eligibility"] != "Eligible":
            applied["value"] = None
            applied["certainty"] = COMPLETE if item["eligibility"] == "Not eligible" else INCOMPLETE
            applied["application_status"] = f"Not applied: {item['eligibility']}"
        else:
            applied["application_status"] = "Applied"
        return {"rating": rating, "policy_rating_rate_percent": policy_rate,
                "applied_rating_rate_percent": applied}

    def tax(self, result, scenario):
        s = self.s
        employee, month = result["employee_id"], result["after_month"]
        policy = s.rule("tax-rules", "previous_employer_income")
        rows = [r for r in s.records("declarations", employee)
                if r["financial_year"] == s.company["financial_year"]
                and r["proof_status"] == policy["declaration_status"]
                and r["applied_from_payroll_month"] <= month]
        detail = result["after"]["tds"]
        if len(rows) == 1:
            gross = self.copied("declarations", rows[0], "declared_amount")
            prior_tds = self.copied("declarations", rows[0], "previous_employer_tds_already_deducted")
        else:
            rules = s.rule_refs(("tax-rules", "previous_employer_income"))
            lines = [s.calc(r["declared_amount"], "Accepted declared previous-employer gross",
                            [s.ref("declarations", r)], rules) for r in rows]
            gross = self.calculated(s.total(lines, "Sum of accepted previous-employer declared gross",
                                           s.base_refs(employee), rules),
                                    scenario, "previous_employer_declared_gross")
            prior_tds = self.calculated(detail["previous_employer_tds"], scenario, "previous_employer_tds")
        row = rows[0] if rows else None
        if row and row.get("income_period_start") and row.get("income_period_end"):
            start_month = row["income_period_start"][:7]
            end_month = row["income_period_end"][:7]
            month_range = f"{start_month} to {end_month}"
            rules = s.rule_refs(("tax-rules", "previous_employer_income"))
            calc = s.calc(month_range, "Accepted declared previous-employer month range",
                          [s.ref("declarations", row)], rules, money=False)
            declared_month_range = {
                "value": month_range,
                "source_file": "data/mock/declarations.json",
                "record_id": row["declaration_id"],
                "source_field": "display_inputs/declared_month_range",
                "certainty": COMPLETE,
                "calculation": deepcopy(calc),
            }
        else:
            declared_month_range = {
                "value": None,
                "source_file": "data/mock/declarations.json",
                "record_id": f"missing:{employee}",
                "source_field": "display_inputs/declared_month_range",
                "certainty": INCOMPLETE,
            }
        return {
            "declared_month_range": declared_month_range,
            "previous_employer_declared_gross": gross,
            "previous_employer_tds": prior_tds,
            "northwind_tds_already_deducted": self.calculated(
                detail["northwind_tds_already_deducted"], scenario, "northwind_tds_already_deducted"),
            "remaining_yearly_tax": self.calculated(
                detail["remaining_yearly_tax"], scenario, "remaining_yearly_tax"),
        }

    def export(self, number, result, scenario):
        # Authorization failure is checked before reading any display source.
        if number == 12 or result.get("status") == "Permission denied":
            return {}
        if result.get("certainty") == "Rule not verified" and "reason" in result:
            return {}
        if number in (1, 2, 3):
            return self.hike(result, scenario)
        if number in (6, 7, 8, 13):
            return self.settlement(result, scenario)
        if number in (4, 5):
            requests = self.s.company["bonus_request_inputs"]
            if number == 4:
                return {"bonus_requests": [
                    {"bonus_type": request["bonus_type"], "period": request["period"],
                     "employees": {item["employee_id"]: self.bonus_employee(request, item)
                                   for item in calculated["employees"]}}
                    for request, calculated in zip(requests, result["bonus_requests"], strict=True)]}
            item = result["employee"]
            request = next(r for r in requests if r["bonus_type"] == item["bonus_type"]
                           and r["period"] == item["period"])
            return {"employees": {item["employee_id"]: self.bonus_employee(request, item)}}
        if number in (9, 10, 11):
            displayed = {"months": self.attendance(result["employee_id"],
                                      [result["before_month"], result["after_month"]])}
            if number == 10:
                displayed.update(self.tax(result, scenario))
            return displayed
        return {}
