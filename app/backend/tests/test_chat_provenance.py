import json
from pathlib import Path
import re
from typing import Optional
import pytest
from fastapi.testclient import TestClient

from app.backend.main import app
from app.backend.chat_router import chat_router

client = TestClient(app)

# Allowed exceptions mapping: {scenario_num: {number: "explicit reason"}}
# Currently strictly NONE. All numeric figures must trace to data/generated/scenarios/ or data/rules/
ALLOWED_EXCEPTIONS = {}

SCENARIO_PROMPTS = {
    1: ("HR01", "Prepare Priya Sharma pending back-dated hike"),
    2: ("HR01", "Review back-dated hike for Arjun Rao"),
    3: ("HR01", "Prepare hike proposal for Kavya Iyer"),
    4: ("HR01", "Calculate Annual and Sales bonus runs"),
    5: ("HR01", "Check bonus eligibility for Meera Nair (E09)"),
    6: ("HR01", "Prepare full and final settlement for Rahul Verma (E10)"),
    7: ("HR01", "Review settlement for Lakshmi Reddy (E11)"),
    8: ("HR01", "Review exit recovery for Imran Khan (E12)"),
    9: ("USER-E05", "Why is my take-home pay lower in September?"),
    10: ("USER-E06", "Why did my TDS deduction increase in September?"),
    11: ("USER-E16", "Did my basic pay or allowance change in September?"),
    12: ("HR02", "What is Priya Sharma monthly salary?"),
    13: ("HR01", "Review settlement breakdown for Imran Khan (E12)"),
}

RULES_DIR = Path(__file__).resolve().parents[3] / "data" / "rules"
_RULES_NUMBERS = set()
_RULES_DATES = set()


def _extract_from_obj(obj, num_set, date_set):
    """Recursively collects numeric values and date representations from an arbitrary JSON object."""
    if isinstance(obj, (int, float)) and not isinstance(obj, bool):
        if isinstance(obj, float) and obj.is_integer():
            num_set.add(int(obj))
        num_set.add(obj)
    elif isinstance(obj, str):
        for m in re.finditer(r"\b\d{4}-\d{2}(?:-\d{2})?\b", obj):
            date_set.add(m.group(0))
        for m in re.finditer(r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{4})\b", obj, re.IGNORECASE):
            date_set.add(m.group(0))
    elif isinstance(obj, dict):
        for v in obj.values():
            _extract_from_obj(v, num_set, date_set)
    elif isinstance(obj, list):
        for item in obj:
            _extract_from_obj(item, num_set, date_set)


def _init_rules():
    global _RULES_NUMBERS, _RULES_DATES
    if not _RULES_NUMBERS:
        for p in RULES_DIR.glob("*.json"):
            with open(p, "r", encoding="utf-8") as f:
                _extract_from_obj(json.load(f), _RULES_NUMBERS, _RULES_DATES)


def _extract_engine_numbers(obj, collected=None):
    """Recursively collects all int and float values from the generated scenario JSON."""
    if collected is None:
        collected = set()
    if isinstance(obj, (int, float)) and not isinstance(obj, bool):
        if isinstance(obj, float) and obj.is_integer():
            collected.add(int(obj))
        collected.add(obj)
    elif isinstance(obj, dict):
        for v in obj.values():
            _extract_engine_numbers(v, collected)
    elif isinstance(obj, list):
        for item in obj:
            _extract_engine_numbers(item, collected)
    return collected


def _extract_card_numbers(cards):
    """Extracts all numeric fields and values from all cards in the /api/chat response."""
    collected = []
    for card in cards:
        card_id = card.get("id", "unknown_card")
        data = card.get("data", {})

        def walk(val, path):
            if isinstance(val, (int, float)) and not isinstance(val, bool):
                v = int(val) if isinstance(val, float) and val.is_integer() else val
                collected.append((f"{card_id}:{path}", v))
            elif isinstance(val, dict):
                for k, sub_v in val.items():
                    walk(sub_v, f"{path}.{k}")
            elif isinstance(val, list):
                for i, sub_v in enumerate(val):
                    walk(sub_v, f"{path}[{i}]")

        walk(data, "data")
    return collected


MONTHS_MAP = {
    "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
    "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
    "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"
}


def _parse_human_date(s: str) -> Optional[str]:
    m = re.search(r"\b(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{4})\b", s, re.IGNORECASE)
    if m:
        day, mon, year = m.group(1), m.group(2)[:3].title(), m.group(3)
        return f"{year}-{MONTHS_MAP[mon]}-{int(day):02d}"
    m2 = re.search(r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{4})\b", s, re.IGNORECASE)
    if m2:
        mon, year = m2.group(1)[:3].title(), m2.group(2)
        return f"{year}-{MONTHS_MAP[mon]}"
    return None


def _extract_text_numbers_and_dates(text: str):
    found_numbers = []
    found_dates = []

    # 1. Amounts with currency symbol: ₹ or INR (supports Indian grouping e.g. ₹1,08,000, −₹420)
    for m in re.finditer(r"[₹]\s*([0-9]{1,3}(?:,[0-9]{2,3})*(?:\.[0-9]+)?|[0-9]+(?:\.[0-9]+)?)", text):
        clean = m.group(1).replace(",", "")
        val = float(clean)
        found_numbers.append((m.group(0), int(val) if val.is_integer() else val))

    # 2. Amounts with comma grouping without ₹ (e.g., 71,200)
    for m in re.finditer(r"(?<![₹\d,.])([0-9]{1,3}(?:,[0-9]{2,3})+(?:\.[0-9]+)?)(?![\d,%])", text):
        clean = m.group(1).replace(",", "")
        val = float(clean)
        found_numbers.append((m.group(0), int(val) if val.is_integer() else val))

    # 3. Percentages (e.g. 10%, 12%, 4%)
    for m in re.finditer(r"([0-9]+(?:\.[0-9]+)?)\s*%", text):
        val = float(m.group(1))
        found_numbers.append((m.group(0), int(val) if val.is_integer() else val))

    # 4. ISO dates and fiscal years (e.g. 2026-09-17, 2026-10, 2026-27, 2025-26)
    for m in re.finditer(r"\b(\d{4}-\d{2}(?:-\d{2})?)\b", text):
        found_dates.append((m.group(0), m.group(1)))

    # 5. Human dates (e.g. 17 Sep 2026, 16 Sep 2026, September 2026)
    d = _parse_human_date(text)
    if d:
        found_dates.append((text, d))

    return found_numbers, found_dates


@pytest.mark.parametrize("scenario_num", range(1, 14))
def test_scenario_cards_provenance_guard(scenario_num):
    """Backend provenance guard: verifies every numeric value in every card of the /api/chat response
    and every number, percentage, and date inside card/message/chip text originates directly from
    engine output in data/generated/scenarios/scenario-XX.json or data/rules/*.json.
    """
    user_id, message = SCENARIO_PROMPTS[scenario_num]

    # Test through the real HTTP API endpoint
    response = client.post(
        "/api/chat",
        json={
            "user_id": user_id,
            "message": message,
            "context": {"scenario_num": scenario_num},
        },
    )
    assert response.status_code == 200, f"Chat endpoint failed for scenario {scenario_num}"
    body = response.json()

    # Part A: Check raw numeric fields in card data
    cards = body.get("cards", [])
    card_numbers = _extract_card_numbers(cards)

    sc_path = Path(__file__).resolve().parents[3] / "data" / "generated" / "scenarios" / f"scenario-{scenario_num:02d}.json"
    assert sc_path.exists(), f"Engine scenario file not found: {sc_path}"

    with open(sc_path, "r", encoding="utf-8") as f:
        sc_data = json.load(f)

    engine_numbers = _extract_engine_numbers(sc_data)
    scenario_exceptions = ALLOWED_EXCEPTIONS.get(scenario_num, {})

    untraced = []
    for field_path, num in card_numbers:
        is_in_engine = (num in engine_numbers) or (-num in engine_numbers)
        is_exception = num in scenario_exceptions

        if not (is_in_engine or is_exception):
            untraced.append((field_path, num))

    assert not untraced, (
        f"BACKEND PROVENANCE GUARD FAILED for Scenario {scenario_num}!\n"
        f"The following {len(untraced)} number(s) in /api/chat response cards do NOT exist "
        f"in {sc_path.name}:\n"
        + "\n".join(f"  - {path}: {val}" for path, val in untraced)
    )

    # Part B: EXTENDED PROVENANCE GUARD: check numbers, percentages, and dates written inside text
    _init_rules()
    sc_numbers = set()
    sc_dates = set()
    _extract_from_obj(sc_data, sc_numbers, sc_dates)

    all_strings = []
    for m in body.get("messages", []):
        all_strings.append(("message", m.get("text", "")))
    for chip in body.get("chips", []):
        all_strings.append(("chip", chip.get("label", "")))
    for card in body.get("cards", []):
        all_strings.append((f"card-{card.get('id')}-title", card.get("title", "")))
        all_strings.append((f"card-{card.get('id')}-certainty", card.get("certainty", "")))

        def collect_strings(val, path):
            if isinstance(val, str):
                all_strings.append((path, val))
            elif isinstance(val, dict):
                for k, sub_v in val.items():
                    collect_strings(sub_v, f"{path}.{k}")
            elif isinstance(val, list):
                for i, sub_v in enumerate(val):
                    collect_strings(sub_v, f"{path}[{i}]")

        collect_strings(card.get("data", {}), f"card-{card.get('id')}")

    panel = body.get("state", {}).get("panel") or {}
    for f_text in panel.get("formulas", []):
        all_strings.append(("panel-formula", f_text))
    for r_text in panel.get("rule_citations", []):
        all_strings.append(("panel-citation", r_text))

    untraced_text_items = []
    for origin, text in all_strings:
        nums, dates = _extract_text_numbers_and_dates(text)
        for raw_match, n in nums:
            in_sc = (n in sc_numbers) or (-n in sc_numbers)
            in_rules = (n in _RULES_NUMBERS) or (-n in _RULES_NUMBERS)
            if not (in_sc or in_rules):
                untraced_text_items.append((origin, raw_match, n, text))

        for raw_match, d in dates:
            in_sc = (d in sc_dates) or any(d in str(sd) for sd in sc_dates)
            in_rules = (d in _RULES_DATES) or any(d in str(rd) for rd in _RULES_DATES)
            if not (in_sc or in_rules):
                untraced_text_items.append((origin, raw_match, d, text))

    assert not untraced_text_items, (
        f"EXTENDED PROVENANCE GUARD FAILED for Scenario {scenario_num}!\n"
        f"The following {len(untraced_text_items)} number(s)/date(s) inside text do NOT exist in {sc_path.name} or data/rules/:\n"
        + "\n".join(f"  - [{orig}] token '{raw}' ({val}) in text: '{txt}'" for orig, raw, val, txt in untraced_text_items)
    )


def test_no_preformatted_currency_in_backend_card_numbers():
    """Confirms display formatting happens strictly in the frontend:
    all numeric card data fields must be raw numbers (int/float), never pre-formatted strings
    with currency symbols ('₹', 'INR', or minus signs '−').
    """
    for scenario_num in range(1, 14):
        user_id, message = SCENARIO_PROMPTS[scenario_num]
        resp = chat_router.handle_chat(
            user_id=user_id,
            message=message,
            context={"scenario_num": scenario_num},
        )
        for card in resp.get("cards", []):
            card_id = card.get("id")
            data = card.get("data", {})

            def check_strings(obj, path):
                if isinstance(obj, str):
                    assert not (
                        obj.startswith("₹")
                        or obj.startswith("−₹")
                        or obj.startswith("-₹")
                        or ("₹" in obj and not path.endswith("notice") and not path.endswith("rule"))
                    ), f"Card {card_id} data field '{path}' contains formatted currency '{obj}'. Display formatting must happen only in the frontend!"
                elif isinstance(obj, dict):
                    for k, v in obj.items():
                        check_strings(v, f"{path}.{k}")
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        check_strings(item, f"{path}[{i}]")

            check_strings(data, "data")
