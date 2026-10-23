"""Bridge to the deterministic payroll engine and generated files."""
import json
import sys
from decimal import Decimal
from typing import Any, Dict, List, Optional

from .config import DATA_DIR, ENGINE_DIR, GENERATED_DIR, MOCK_DIR, ROOT_DIR

# Ensure engine is on sys.path
if str(ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(ENGINE_DIR))

from payroll.core import parse_date
from payroll.scenarios import calculate


def decimal_serializer(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Type {type(obj)} not serializable")


class EngineBridge:
    def __init__(self):
        self._bundle = None

    def get_bundle(self):
        if self._bundle is None:
            self._bundle = calculate(ROOT_DIR, parse_date("2026-10-13"))
        return self._bundle

    def get_scenario(self, scenario_num: int) -> dict:
        filename = f"scenario-{scenario_num:02d}.json"
        path = GENERATED_DIR / "scenarios" / filename
        if not path.exists():
            raise FileNotFoundError(f"Scenario file {filename} not found")
        content = json.loads(path.read_text(encoding="utf-8-sig"))
        return content

    def get_scenario_summary(self) -> List[dict]:
        path = GENERATED_DIR / "scenario-summary.json"
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8-sig"))
        return []

    def calculate_bonus_scope(self, bonus_type: str, period: str, employee_ids: List[str]) -> dict:
        bundle = self.get_bundle()
        flows = bundle["flows"]
        res = flows.bonus_selected_scope(bonus_type, period, employee_ids)
        # Convert Decimals for JSON serialization
        raw = json.dumps(res, default=decimal_serializer)
        return json.loads(raw)

    def recalculate_hike(self, employee_id: str, new_hike_percent: float, reason: str) -> dict:
        bundle = self.get_bundle()
        flows = bundle["flows"]
        store = bundle["store"]
        revision = store.one("salary-revisions", employee_id)
        if not revision:
            raise ValueError(f"No salary revision for {employee_id}")
        revised_revision = dict(revision)
        revised_revision["hike_percent"] = new_hike_percent
        revised_revision["edit_reason"] = reason

        result = flows.hike(employee_id, revision_override=revised_revision)
        raw = json.dumps(result, default=decimal_serializer)
        return json.loads(raw)


bridge = EngineBridge()
