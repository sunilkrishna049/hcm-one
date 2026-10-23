"""Windows-friendly command-line entry point; no network or AI dependencies."""
import argparse
import sys
from pathlib import Path

from payroll.core import parse_date
from payroll.scenarios import generate


def main():
    if sys.version_info[:2] != (3, 12):
        raise SystemExit("Run with Python 3.12")
    parser = argparse.ArgumentParser(description="Generate read-only payroll demo proposals")
    parser.add_argument("--as-of", required=True, type=parse_date,
                        help="Explicit calculation date (YYYY-MM-DD), used only for notice eligibility")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    bundle = generate(root, args.as_of)
    print(f"Generated {len(bundle['scenarios'])} scenarios and {len(bundle['payroll'].payslips)} complete payslips.")
    print(f"Payslips not generated: {len(bundle['payroll'].failures)}; non-employed months: {len(bundle['payroll'].skipped)}.")
    print(f"Ambiguities: {', '.join(bundle['store'].ambiguities) or 'none'}.")


if __name__ == "__main__":
    main()
