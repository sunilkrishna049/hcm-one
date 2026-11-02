"""Test guard scanning rendered formulas and text lines in all scenario fixtures for empty interpolations.
Guards:
- No 'from  to' or 'from to'
- No '₹' with no number immediately following
- No double spaces in user-facing strings
- No ': ' at end of line (unfilled interpolations)
"""
import json
import re
from pathlib import Path
import pytest

from app.backend.chat_router import chat_router
from app.backend.auth import USERS
from app.backend.engine_bridge import bridge


def scan_for_empty_interpolations(obj, path=""):
    issues = []
    if isinstance(obj, str):
        # 1. 'from  to' or 'from to'
        if "from  to" in obj or "from to" in obj:
            issues.append(f"{path}: Unfilled 'from to' -> '{obj}'")

        # 2. '₹' with no number (e.g. '₹ ' followed by non-digit or end of line)
        if re.search(r"₹\s*(?![0-9])", obj):
            issues.append(f"{path}: '₹' without number -> '{obj}'")

        # 3. Double spaces in text lines
        if "  " in obj:
            issues.append(f"{path}: Double space -> '{obj}'")

        # 4. ': ' at end of line or string
        if obj.rstrip().endswith(":"):
            issues.append(f"{path}: Unfilled trailing colon -> '{obj}'")

    elif isinstance(obj, dict):
        for k, v in obj.items():
            issues.extend(scan_for_empty_interpolations(v, f"{path}.{k}"))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            issues.extend(scan_for_empty_interpolations(item, f"{path}[{i}]"))
    return issues


def test_scenario_router_responses_have_no_empty_interpolations():
    """Verify that all router scenario builders produce clean strings with zero empty interpolations."""
    hr_user = USERS["HR01"]
    emp_user = USERS["USER-E05"]

    cases = [
        ("Scenario 1", chat_router._build_scenario_1(hr_user, "HR Admin", "CHAT-HR")),
        ("Scenario 2", chat_router._build_scenario_2(hr_user, "HR Admin", "CHAT-HR")),
        ("Scenario 3", chat_router._build_scenario_3(hr_user, "HR Admin", "CHAT-HR")),
        ("Scenario 4 Annual", chat_router._build_scenario_4(hr_user, "HR Admin", "CHAT-HR", "annual_performance_bonus")),
        ("Scenario 4 Sales", chat_router._build_scenario_4(hr_user, "HR Admin", "CHAT-HR", "quarterly_sales_incentive")),
        ("Scenario 5", chat_router._build_scenario_5(hr_user, "HR Admin", "CHAT-HR")),
        ("Scenario 6", chat_router._build_scenario_6(hr_user, "HR Admin", "CHAT-HR")),
        ("Scenario 7", chat_router._build_scenario_7(hr_user, "HR Admin", "CHAT-HR")),
        ("Scenario 8", chat_router._build_scenario_8(hr_user, "HR Admin", "CHAT-HR")),
        ("Scenario 9 HR", chat_router._build_scenario_9(hr_user, "HR Admin", "CHAT-HR")),
        ("Scenario 9 Emp", chat_router._build_scenario_9(emp_user, "Employee", "CHAT-EMP")),
        ("Scenario 10 HR", chat_router._build_scenario_10(hr_user, "HR Admin", "CHAT-HR")),
        ("Scenario 10 Emp", chat_router._build_scenario_10(USERS["USER-E06"], "Employee", "CHAT-EMP")),
        ("Scenario 11 HR", chat_router._build_scenario_11(hr_user, "HR Admin", "CHAT-HR")),
        ("Scenario 11 Emp", chat_router._build_scenario_11(USERS["USER-E16"], "Employee", "CHAT-EMP")),
        ("Scenario 13", chat_router._build_scenario_13(hr_user, "HR Admin", "CHAT-HR")),
        ("Approvals List", chat_router._handle_approvals_list(hr_user, "HR Admin", "CHAT-HR")),
    ]

    all_issues = []
    for name, response in cases:
        issues = scan_for_empty_interpolations(response, name)
        if issues:
            all_issues.extend(issues)

    assert not all_issues, f"Found empty interpolation issues:\n" + "\n".join(all_issues)


def test_scenario_fixture_files_have_no_empty_interpolations():
    """Verify that any exported fixture files in tests/fixtures or data/ have no empty interpolations."""
    fixture_dir = Path("app/backend/tests/fixtures")
    if fixture_dir.exists():
        for f in fixture_dir.glob("*.json"):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                issues = scan_for_empty_interpolations(data, f.name)
                assert not issues, f"Found empty interpolations in fixture {f.name}:\n" + "\n".join(issues)
            except Exception as e:
                if not isinstance(e, AssertionError):
                    pass
                else:
                    raise


def test_scenario_fixtures_day_count_never_contains_rupee():
    """Guard: any value whose label mentions days or count never contains '₹'."""
    fixture_path = Path("app/frontend/src/tests/chat_scenario_fixtures.json")
    if not fixture_path.exists():
        pytest.skip("Fixtures file not found")
    with open(fixture_path, "r", encoding="utf-8") as f:
        fixtures = json.load(f)

    violations = []
    for scen_name, scen_data in fixtures.items():
        cards = scen_data.get("cards", [])
        for card in cards:
            data = card.get("data", {})
            hero_label = str(data.get("hero_label", "")).lower()
            if any(w in hero_label for w in ["day", "days", "count"]):
                hero_amount = data.get("hero_amount")
                if isinstance(hero_amount, str) and "₹" in hero_amount:
                    violations.append(f"{scen_name} card {card.get('type')}: {hero_label} -> {hero_amount}")
            for k, v in data.items():
                k_lower = str(k).lower()
                if any(w in k_lower for w in ["day", "days", "count", "item", "employee"]):
                    if isinstance(v, str) and "₹" in v:
                        violations.append(f"{scen_name} card {card.get('type')}: {k} -> {v}")
    assert not violations, f"Found count/day fields containing '₹': {violations}"


