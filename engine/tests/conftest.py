import sys
from pathlib import Path

import pytest

ENGINE = Path(__file__).resolve().parents[1]
ROOT = ENGINE.parent
sys.path.insert(0, str(ENGINE))

from payroll.core import parse_date
from payroll.scenarios import calculate


@pytest.fixture(scope="session")
def bundle():
    return calculate(ROOT, parse_date("2026-10-13"))


@pytest.fixture(scope="session")
def scenarios(bundle):
    return {i + 1: case["result"] for i, case in enumerate(bundle["scenarios"])}
