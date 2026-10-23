"""Decimal arithmetic, input loading, rule validity and calculation provenance."""
from __future__ import annotations

import calendar
import hashlib
import json
import re
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

COMPLETE = "Complete for this scope"
INCOMPLETE = "Incomplete"
UNVERIFIED = "Rule not verified"
HR = "Needs HR decision"
UNEXPLAINED = "Cannot explain from available payroll data"
CERTAINTIES = {COMPLETE, INCOMPLETE, UNVERIFIED, HR, UNEXPLAINED}


def dec(value):
    return Decimal(str(value))


def parse_date(value):
    return date.fromisoformat(value)


def month_bounds(month):
    year, number = map(int, month.split("-"))
    return date(year, number, 1), date(year, number, calendar.monthrange(year, number)[1])


def month_range(start, end):
    current = start.replace(day=1)
    while current <= end:
        yield current.strftime("%Y-%m")
        current = (current.replace(day=calendar.monthrange(current.year, current.month)[1])
                   + timedelta(days=1))


def add_months(start, count):
    index = start.year * len(calendar.month_name[1:]) + start.month - 1 + count
    year, month = divmod(index, len(calendar.month_name[1:]))
    month += 1
    return date(year, month, min(start.day, calendar.monthrange(year, month)[1]))


def numbers(text):
    """Read numeric operands from the supplied human-readable rule; never eval it."""
    return [dec(item) for item in re.findall(r"\d+(?:\.\d+)?", text)]


def unique(records):
    return list({json.dumps(record, sort_keys=True): record for record in records}.values())


class RuleError(ValueError):
    pass


class Store:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.mock = {}
        self.rule_files = {}
        self.ambiguities = {}
        self.hashes = {}
        for folder, target in (("mock", self.mock), ("rules", self.rule_files)):
            for path in sorted((self.root / "data" / folder).glob("*.json")):
                raw = path.read_bytes()
                target[path.stem] = json.loads(raw.decode("utf-8-sig"), parse_float=Decimal)
                self.hashes[path.relative_to(self.root).as_posix()] = hashlib.sha256(raw).hexdigest()
        self.company = self.mock["company"]
        self.employees = {row["employee_id"]: row for row in self.mock["employees"]}
        self.structures = {row["employee_id"]: row for row in self.mock["salary-structures"]}
        self.processed = sorted(row["month"] for row in self.mock["payroll-runs"]
                                if row["status"] == "processed")
        self.year_start = parse_date(self.company["tax_year_start"])
        self.year_end = parse_date(self.company["tax_year_end"])

    def records(self, file, employee=None):
        rows = self.mock[file]
        return [r for r in rows if employee is None or r.get("employee_id") == employee]

    def one(self, file, employee, **filters):
        rows = [row for row in self.records(file, employee)
                if all(row.get(key) == value for key, value in filters.items())]
        if len(rows) > 1:
            raise ValueError(f"Multiple {file} records for {employee}: {filters}")
        return rows[0] if rows else None

    def ref(self, file, row=None, *, record_id=None, fields=None):
        if record_id is None:
            candidates = [key for key in (row or {}) if key.endswith("_id")]
            primary = next((k for k in candidates if k != "employee_id"), "employee_id")
            record_id = row.get(primary) if row else "missing record"
        result = {"source_file": f"data/mock/{file}.json", "record_id": record_id}
        if fields:
            result["fields"] = fields
        return result

    def base_refs(self, employee):
        return [self.ref("employees", self.employees[employee]),
                self.ref("salary-structures", self.structures[employee]),
                self.ref("company", record_id=self.company["company_id"])]

    def rule(self, file, key, on=None):
        row = self.rule_files[file][key]
        status = row["status"]
        if not (status in {"demo_rule_approved", "company_setting_demo"}
                or status.startswith("verified_by_project_owner_")):
            raise RuleError(f"Unverified rule: {file}#{key}")
        if on is not None:
            if row["effective_from"] and on < parse_date(row["effective_from"]):
                raise RuleError(f"Rule not yet effective: {file}#{key}")
            if row["effective_to"] and on > parse_date(row["effective_to"]):
                raise RuleError(f"Rule expired: {file}#{key}")
        return row["value"]

    def rule_ref(self, file, key):
        row = self.rule_files[file][key]
        value = row["value"]
        # Keep the actual rule content, not just an opaque reference.
        value = json.loads(json.dumps(value, default=lambda v: float(v)))
        result = {"rule_id": f"{file}.json#{key}", "source_file": f"data/rules/{file}.json",
                "source": row["source"], "effective_from": row["effective_from"],
                "effective_to": row["effective_to"], "status": row["status"], "value": value}
        result["rules_version"] = self.rule_files[file]["rules_version"]
        result["verified_on"] = self.rule_files[file]["verified_on"]
        if row["effective_from"] is None and row["effective_to"] is None:
            result["date_note"] = "Applies to all demo periods"
        return result

    def rule_refs(self, *keys):
        return [self.rule_ref(*key) for key in keys]

    def ambiguity(self, identifier, description, scope):
        item = self.ambiguities.setdefault(identifier, {"id": identifier,
                    "description": description, "affected": []})
        if scope not in item["affected"]:
            item["affected"].append(scope)
        return identifier

    def calc(self, value, formula, inputs, rules=(), certainty=COMPLETE, flags=(), *, money=True):
        rules = unique(list(rules))
        flags = list(flags)
        if value is not None and money:
            self.rule("company-settings", "rounding")
            rounding = self.rule_ref("company-settings", "rounding")
            rules = unique(rules + [rounding])
            raw = dec(value)
            fraction = abs(raw) % 1
            if fraction * 2 == 1:
                tie_rule = self.rule_files["company-settings"].get("rounding_ties")
                if tie_rule is None or "round half up" not in self.rule("company-settings", "rounding_ties").lower():
                    self.ambiguity("AMB-01", "The nearest-rupee rule needs a verified exact half-rupee tie convention.", formula)
                    value, certainty = None, UNVERIFIED
                    flags += ["AMB-01: Exact half-rupee rounding tie"]
                else:
                    rules = unique(rules + [self.rule_ref("company-settings", "rounding_ties")])
                    value = int(raw.to_integral_value(rounding=ROUND_HALF_UP))
            else:
                value = int(raw.to_integral_value(rounding=ROUND_HALF_UP))
        elif isinstance(value, date):
            value = value.isoformat()
        return {"value": value, "formula": formula, "inputs": unique(list(inputs)),
                "rule_ids": rules, "certainty": certainty, "flags": flags}

    def blocked(self, formula, inputs, rules=(), certainty=INCOMPLETE, flags=()):
        return self.calc(None, formula, inputs, rules, certainty, flags)

    def total(self, lines, formula, inputs=(), rules=(), signs=None):
        lines = list(lines)
        dependencies = [r for line in lines for r in line["inputs"]]
        all_rules = list(rules) + [r for line in lines for r in line["rule_ids"]]
        flags = [f for line in lines for f in line["flags"]]
        unknown = [line for line in lines if line["value"] is None]
        if unknown:
            certainty = UNVERIFIED if any(l["certainty"] == UNVERIFIED for l in unknown) else INCOMPLETE
            return self.blocked(formula, list(inputs) + dependencies, all_rules, certainty, unique(flags))
        multipliers = list(signs) if signs is not None else [1] * len(lines)
        return self.calc(sum(dec(l["value"]) * sign for l, sign in zip(lines, multipliers, strict=True)),
                         formula, list(inputs) + dependencies, all_rules, flags=unique(flags))


def completeness(value):
    """Overall certainty; known sub-calculations retain their own certainty."""
    states = []
    def visit(item):
        if isinstance(item, dict):
            if "formula" in item and "certainty" in item:
                states.append(item["certainty"])
            else:
                for child in item.values():
                    visit(child)
        elif isinstance(item, list):
            for child in item:
                visit(child)
    visit(value)
    for state in (UNVERIFIED, INCOMPLETE, HR, UNEXPLAINED):
        if state in states:
            return state
    return COMPLETE
