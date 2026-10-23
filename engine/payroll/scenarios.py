"""BRD scenario routing from the mock README's scenario coverage table."""
from __future__ import annotations

import json
import re
from pathlib import Path

from .core import RuleError, Store, UNVERIFIED, completeness
from .flows import Flows
from .display import DisplayInputs
from .history import Payroll


def scenario_plan(root):
    text = (Path(root) / "data/mock/README.md").read_text(encoding="utf-8-sig")
    result = []
    section = text.split("## Scenario coverage", 1)[1].split("## Missing rules", 1)[0]
    for line in section.splitlines():
        if not line.startswith("|"):
            continue
        fields = [part.strip() for part in line.strip("|").split("|")]
        if fields[0].isdigit():
            result.append({"number": int(fields[0]), "description": fields[1],
                           "employees": re.findall(r"E\d+", fields[2])})
    if len(result) != 13 or [r["number"] for r in result] != list(range(1, 14)):
        raise ValueError("The mock README must map all thirteen BRD scenarios in order")
    return result


def calculate(root, as_of):
    store = Store(root)
    payroll = Payroll(store)
    payroll.generate_history()
    flows = Flows(payroll, as_of)
    display = DisplayInputs(payroll)
    bonuses = flows.bonus()
    settlements = {}
    results = []
    for case in scenario_plan(root):
        number, employees = case["number"], case["employees"]
        eid = employees[0]
        try:
            if number in (1, 2, 3):
                result = flows.hike(eid)
            elif number == 4:
                result = {"bonus_requests": bonuses,
                          "certainty": completeness(bonuses)}
            elif number == 5:
                item = next(row for request in bonuses for row in request["employees"] if row["employee_id"] == eid)
                result = {"employee": item, "certainty": item["certainty"]}
            elif number in (6, 7, 8, 13):
                if eid not in settlements:
                    settlements[eid] = flows.settlement(eid)
                result = settlements[eid]
            elif number in (9, 10, 11):
                result = flows.compare(eid, store.processed[-2], store.processed[-1])
            elif number == 12:
                user = next(row for row in store.mock["users"] if row.get("employee_id") == eid)
                result = flows.authorize(user["user_id"], employees[1])
            else:
                raise ValueError("Unmapped BRD scenario")
        except RuleError as error:
            scope = f"Scenario {number}"
            store.ambiguity("AMB-RULE", str(error), scope)
            result = {"certainty": UNVERIFIED, "reason": str(error)}
        # The permission-denied payload contains no target data, IDs, sources or calculations.
        scenario_id = f"scenario-{number:02}"
        display_inputs = display.export(number, result, scenario_id)
        result = {"scenario_id": scenario_id,
                  "description": case["description"], "result": result,
                  "display_inputs": display_inputs}
        results.append(result)
    return {"store": store, "payroll": payroll, "flows": flows, "scenarios": results,
            "bonuses": bonuses, "settlements": settlements}


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def generate(root, as_of):
    root = Path(root).resolve()
    bundle = calculate(root, as_of)
    store, payroll = bundle["store"], bundle["payroll"]
    destination = root / "data/generated"
    context = {"record_id": "RUN-CONTEXT", "calculation_date": store.calc(as_of,
               "Calculation date explicitly supplied to the deterministic run; used for the notice check",
               [{"source_file": "data/generated/run-context.json", "record_id": "RUN-CONTEXT", "fields": ["command_line.as_of"]}],
               store.rule_refs(("bonus-rules", "annual_performance_bonus_notice_check")), money=False),
               "command_line": {"as_of": as_of.isoformat()},
               "source_sha256": store.hashes,
               "salary_history_scope": "The supplied original structures apply to this demo fixture; pending hikes are not applied",
               "proposal_only": True}
    write_json(destination / "run-context.json", context)
    write_json(destination / "payslips.json", payroll.payslips)
    write_json(destination / "payslip-failures.json", {"not_generated": payroll.failures,
               "not_employed": payroll.skipped})
    write_json(destination / "calculation-ledger.json", list(payroll.ledger.values()))
    write_json(destination / "bonus-proposals.json", bundle["bonuses"])
    write_json(destination / "ambiguities.json", list(store.ambiguities.values()))
    for case in bundle["scenarios"]:
        write_json(destination / "scenarios" / f"{case['scenario_id']}.json", case)
    summary = [{"scenario": row["scenario_id"], "description": row["description"],
                "certainty": row["result"].get("certainty", row["result"].get("status"))}
               for row in bundle["scenarios"]]
    write_json(destination / "scenario-summary.json", summary)
    readme = root / "engine/README.md"
    if readme.exists():
        before = readme.read_text(encoding="utf-8").split("## Ambiguities found", 1)[0]
        sections = [before.rstrip(), "", "## Ambiguities found", ""]
        for item in store.ambiguities.values():
            sections += [f"### {item['id']}", "", item["description"], "",
                         "Affected scopes: " + ", ".join(item["affected"]) + ".", ""]
        if not store.ambiguities:
            sections.append("None.")
        readme.write_text("\n".join(sections).rstrip() + "\n", encoding="utf-8")
    return bundle
