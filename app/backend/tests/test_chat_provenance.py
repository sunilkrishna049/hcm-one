import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from app.backend.main import app
from app.backend.chat_router import chat_router

client = TestClient(app)

# Allowed exceptions mapping: {scenario_num: {number: "explicit reason"}}
# Currently strictly NONE. All numeric figures must trace to data/generated/scenarios/
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


def _extract_engine_numbers(obj, collected=None):
    """Recursively collects all int and float values from the generated scenario JSON."""
    if collected is None:
        collected = set()
    if isinstance(obj, (int, float)):
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


@pytest.mark.parametrize("scenario_num", range(1, 14))
def test_scenario_cards_provenance_guard(scenario_num):
    """Backend provenance guard: verifies every numeric value in every card of the /api/chat response

    originates directly from engine output in data/generated/scenarios/scenario-XX.json.
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

    cards = body.get("cards", [])
    card_numbers = _extract_card_numbers(cards)

    # Load corresponding scenario engine output
    sc_path = Path(__file__).resolve().parents[3] / "data" / "generated" / "scenarios" / f"scenario-{scenario_num:02d}.json"
    assert sc_path.exists(), f"Engine scenario file not found: {sc_path}"

    with open(sc_path, "r", encoding="utf-8") as f:
        sc_data = json.load(f)

    engine_numbers = _extract_engine_numbers(sc_data)
    scenario_exceptions = ALLOWED_EXCEPTIONS.get(scenario_num, {})

    untraced = []
    for field_path, num in card_numbers:
        # Number must exist in engine output (or allowed negative/exceptions)
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
                    # Flag strings that look like formatted money rather than labels/dates
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
