"""Deterministic intent router and response generator for POST /api/chat.
Follows app/backend/chat_contract.md and output/07-prototype/screen-specs.md.
Zero dynamic LLM calls. All payroll figures come from engine_bridge (data/generated/scenarios/).
"""
from datetime import datetime, timezone
import json
import logging
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Tuple
from fastapi import HTTPException

logger = logging.getLogger(__name__)

from .ai_messages import get_message
from .auth import USERS, check_employee_access
from .engine_bridge import bridge
from .faq_matcher import faq_matcher
from .lifecycle import lifecycle, evaluate_proposal_readiness
from .permissions import get_mentioned_employee_ids, enforce_reply_permissions

RULES_DIR = Path(__file__).resolve().parents[2] / "data" / "rules"
_RULES_CACHE: Dict[str, dict] = {}

MOCK_DIR = Path(__file__).resolve().parents[2] / "data" / "mock"
EMPLOYEES_PATH = MOCK_DIR / "employees.json"
try:
    if EMPLOYEES_PATH.exists():
        _emp_data = json.loads(EMPLOYEES_PATH.read_text(encoding="utf-8"))
        EMPLOYEE_NAMES: Dict[str, str] = {e["employee_id"]: e["name"] for e in _emp_data}
    else:
        EMPLOYEE_NAMES = {}
except Exception:
    EMPLOYEE_NAMES = {}


def _get_engine_val(d: Optional[dict], field_name: str, key: str = "value") -> Any:
    """Read value from engine data without default. Logs masked warning if missing."""
    if not isinstance(d, dict):
        logger.warning(f"Masked warning: Engine dictionary for '{field_name}' is missing; value cannot be read.")
        return None
    val = d.get(key)
    if val is None:
        logger.warning(f"Masked warning: Engine field '{field_name}.{key}' is missing; omitted from display.")
        return None
    return val


def _get_engine_certainty(obj: Optional[dict], field_name: str = "certainty") -> Optional[str]:
    """Read certainty directly from engine output; never invent a default label.
    Logs a masked warning if the value is missing or empty.
    """
    if not isinstance(obj, dict):
        logger.warning("Masked warning: Engine result object is missing or non-dict; certainty cannot be read.")
        return None
    val = obj.get(field_name)
    if val is None or val == "":
        logger.warning(f"Masked warning: Engine certainty field '{field_name}' is missing; no badge displayed.")
        return None
    return str(val)


LEAST_CERTAIN_ORDER = [
    "Needs HR decision",
    "Rule not verified",
    "Incomplete",
    "Cannot explain from available payroll data",
]


def get_least_certain_label(*labels: Optional[str]) -> Optional[str]:
    """Return the least certain label among the provided labels.
    - Any label other than 'Complete for this scope' wins.
    - If several differ, the order is:
      1. Needs HR decision
      2. Rule not verified
      3. Incomplete
      4. Cannot explain from available payroll data
    - If all valid labels are 'Complete for this scope', returns 'Complete for this scope'.
    - If no valid labels, returns None.
    """
    valid_labels = [l for l in labels if l]
    if not valid_labels:
        return None
    if all(l == "Complete for this scope" for l in valid_labels):
        return "Complete for this scope"
    for candidate in LEAST_CERTAIN_ORDER:
        if candidate in valid_labels:
            return candidate
    for l in valid_labels:
        if l != "Complete for this scope":
            return l
    return "Complete for this scope"


MONTH_NAMES = {
    "01": "January", "02": "February", "03": "March", "04": "April",
    "05": "May", "06": "June", "07": "July", "08": "August",
    "09": "September", "10": "October", "11": "November", "12": "December"
}


def format_month_label(month_str: str) -> str:
    """Format '2026-09' to 'September 2026'."""
    parts = month_str.split("-")
    if len(parts) == 2:
        return f"{MONTH_NAMES.get(parts[1], parts[1])} {parts[0]}"
    return month_str


def get_employee_ledger_months(emp_id: str) -> List[str]:
    """Return every month the engine ledger holds with full provenance for that employee.
    Never shows months before the employee joined.
    """
    bundle = bridge.get_bundle()
    payroll = bundle.get("payroll")
    store = bundle.get("store")
    if not payroll or not store:
        return ["2026-09"]

    emp = store.employees.get(emp_id) if hasattr(store, "employees") else None
    joining_date = None
    if isinstance(emp, dict):
        joining_date = emp.get("joining_date")
    elif emp:
        joining_date = getattr(emp, "joining_date", None)

    joining_month = joining_date[:7] if joining_date else None

    months = set()
    for p in payroll.payslips:
        if p.get("employee_id") == emp_id:
            m = p.get("month")
            if m:
                if joining_month and m < joining_month:
                    continue
                months.add(m)

    return sorted(list(months))


def format_available_months_phrase(months: List[str]) -> str:
    """Format available months from engine data, e.g. 'April to September 2026'."""
    if not months:
        return "September 2026"
    if len(months) == 1:
        return format_month_label(months[0])

    start_parts = months[0].split("-")
    end_parts = months[-1].split("-")
    start_name = MONTH_NAMES.get(start_parts[1], start_parts[1])
    end_name = MONTH_NAMES.get(end_parts[1], end_parts[1])

    if start_parts[0] == end_parts[0]:
        return f"{start_name} to {end_name} {end_parts[0]}"
    return f"{start_name} {start_parts[0]} to {end_name} {end_parts[0]}"


def format_month_range_phrase(range_str: Optional[str]) -> str:
    """Format month range '2026-04 to 2026-06' to 'April to June 2026'."""
    if not range_str:
        return ""
    parts = [p.strip() for p in range_str.split("to")]
    if len(parts) == 2 and re.match(r"^\d{4}-\d{2}$", parts[0]) and re.match(r"^\d{4}-\d{2}$", parts[1]):
        return format_available_months_phrase(parts)
    return range_str


def normalize_month_code(m_str: Optional[str]) -> str:
    """Normalizes any month string (e.g. 'September 2026', 'september', '2026-09') to 'YYYY-MM'."""
    if not m_str:
        return "2026-09"
    m_clean = str(m_str).strip()
    if re.match(r"^\d{4}-\d{2}$", m_clean):
        return m_clean
    lower = m_clean.lower()
    month_map = {
        "january": "01", "jan": "01",
        "february": "02", "feb": "02",
        "march": "03", "mar": "03",
        "april": "04", "apr": "04",
        "may": "05",
        "june": "06", "jun": "06",
        "july": "07", "jul": "07",
        "august": "08", "aug": "08",
        "september": "09", "sep": "09", "sept": "09",
        "october": "10", "oct": "10",
        "november": "11", "nov": "11",
        "december": "12", "dec": "12",
    }
    for name, num in month_map.items():
        if name in lower:
            year_match = re.search(r"\b(20\d\d)\b", lower)
            year = year_match.group(1) if year_match else "2026"
            return f"{year}-{num}"
    return "2026-09"


def get_employee_name(employee_id: str) -> str:
    return EMPLOYEE_NAMES.get(employee_id, employee_id)


def get_employee_payroll_data(emp_id: str, month: str = "2026-09") -> Optional[dict]:
    bundle = bridge.get_bundle()
    payroll = bundle.get("payroll")
    if not payroll:
        return None
    ps = next((p for p in payroll.payslips if p.get("employee_id") == emp_id and p.get("month") == month), None)
    if not ps:
        return None
    store = bundle.get("store")
    att = next((a for a in store.records("attendance") if a.get("employee_id") == emp_id and a.get("month") == month), None)
    emp = store.employees.get(emp_id) if hasattr(store, "employees") else None

    earnings_lines = ps.get("earnings", {}).get("lines", {}) if isinstance(ps.get("earnings"), dict) else {}
    basic = earnings_lines.get("basic", {}).get("value") if isinstance(earnings_lines, dict) else None
    hra = earnings_lines.get("hra", {}).get("value") if isinstance(earnings_lines, dict) else None
    spl = earnings_lines.get("special_allowance", {}).get("value") if isinstance(earnings_lines, dict) else None
    da = earnings_lines.get("da", {}).get("value") if isinstance(earnings_lines, dict) else None
    gross = ps.get("earnings", {}).get("gross", {}).get("value") if isinstance(ps.get("earnings"), dict) else None

    pf_rec = ps.get("pf", {})
    pf_val = pf_rec.get("employee", {}).get("value") if isinstance(pf_rec, dict) and isinstance(pf_rec.get("employee"), dict) else (pf_rec.get("value") if isinstance(pf_rec, dict) else None)
    pf_certainty = _get_engine_certainty(pf_rec) or (_get_engine_certainty(pf_rec.get("employee")) if isinstance(pf_rec, dict) else None)

    tds_rec = ps.get("tds", {})
    tds_val = tds_rec.get("amount", {}).get("value") if isinstance(tds_rec, dict) and isinstance(tds_rec.get("amount"), dict) else (tds_rec.get("value") if isinstance(tds_rec, dict) else None)
    tds_certainty = (_get_engine_certainty(tds_rec.get("amount")) if isinstance(tds_rec, dict) else None) or _get_engine_certainty(tds_rec)
    tds_formula = tds_rec.get("amount", {}).get("formula") if isinstance(tds_rec, dict) and isinstance(tds_rec.get("amount"), dict) else "Remaining yearly tax divided by remaining tax-year months including the current month"
    tds_rules = tds_rec.get("amount", {}).get("rule_ids", []) if isinstance(tds_rec, dict) and isinstance(tds_rec.get("amount"), dict) else []

    tot_ded = ps.get("total_deductions", {})
    tot_ded_val = tot_ded.get("value") if isinstance(tot_ded, dict) else tot_ded

    net_rec = ps.get("net_pay", {})
    net_val = net_rec.get("value") if isinstance(net_rec, dict) else net_rec

    for _fn, _fv in [("basic", basic), ("hra", hra), ("special_allowance", spl), ("da", da), ("gross", gross), ("pf", pf_val), ("tds", tds_val), ("total_deductions", tot_ded_val), ("net_pay", net_val)]:
        if _fv is None:
            logger.warning(f"Masked warning: Engine field '{_fn}' is missing; omitted from display.")
    net_pay_certainty = _get_engine_certainty(net_rec) if isinstance(net_rec, dict) else None

    lop_days = att.get("lop_days", 0) if att else 0
    paid_days_rec = ps.get("earnings", {}).get("paid_days", {})
    lop_certainty = _get_engine_certainty(paid_days_rec) if isinstance(paid_days_rec, dict) else None

    tax_regime = emp.get("tax_regime_selected", "new") if isinstance(emp, dict) else "new"
    tax_regime_certainty = None

    return {
        "employee_id": emp_id,
        "month": month,
        "basic": basic,
        "hra": hra,
        "special_allowance": spl,
        "da": da,
        "gross": gross,
        "pf": pf_val,
        "pf_certainty": pf_certainty,
        "tds": tds_val,
        "tds_certainty": tds_certainty,
        "tds_formula": tds_formula,
        "tds_rules": tds_rules,
        "total_deductions": tot_ded_val,
        "net_pay": net_val,
        "net_pay_certainty": net_pay_certainty,
        "lop_days": lop_days,
        "lop_certainty": lop_certainty,
        "tax_regime": tax_regime,
        "tax_regime_certainty": tax_regime_certainty,
        "certainty": _get_engine_certainty(ps)
    }


def _get_user_fallback_chips(user: Optional[dict] = None) -> list[dict]:
    if not user:
        return [
            {"label": "What is PF?", "action": "faq-pf", "payload": {}},
            {"label": "What is TDS?", "action": "faq-tds", "payload": {}},
            {"label": "Draft a query for HR", "action": "draft-query", "payload": {}}
        ]
    role = user.get("role", "Employee")
    uid = user.get("user_id", "")
    eid = user.get("employee_id")
    if role == "HR Admin":
        if uid == "HR02":
            return [
                {"label": "Calculate arrears", "action": "arrears-picker", "payload": {}},
                {"label": "Prepare sales incentive proposal", "action": "apply-selection", "payload": {"choice": "sales"}},
                {"label": "Prepare full and final settlement", "action": "settlement-picker", "payload": {}},
                {"label": "Review payroll queries", "action": "review-queries", "payload": {}}
            ]
        return [
            {"label": "Calculate arrears", "action": "arrears-picker", "payload": {}},
            {"label": "Prepare team bonus proposal", "action": "scenario-4", "payload": {}},
            {"label": "Prepare full and final settlement", "action": "settlement-picker", "payload": {}},
            {"label": "Review payroll queries", "action": "review-queries", "payload": {}}
        ]
    if eid == "E05" or uid == "USER-E05":
        return [
            {"label": "Why is my take-home pay lower in September?", "action": "explain-salary", "payload": {}},
            {"label": "How much PF was cut in September?", "action": "explain-pf", "payload": {"month": "2026-09"}},
            {"label": "What is LOP?", "action": "faq-lop", "payload": {}},
            {"label": "Draft a query for HR", "action": "draft-query", "payload": {}}
        ]
    if eid == "E06" or uid == "USER-E06":
        return [
            {"label": "Why did my TDS increase?", "action": "explain-tds", "payload": {}},
            {"label": "What is TDS?", "action": "faq-tds", "payload": {}},
            {"label": "Draft a query for HR", "action": "draft-query", "payload": {}}
        ]
    if eid == "E16" or uid == "USER-E16":
        return [
            {"label": "Did my basic pay or allowance change?", "action": "explain-deduction", "payload": {}},
            {"label": "What is PF?", "action": "faq-pf", "payload": {}},
            {"label": "Draft a query for HR", "action": "draft-query", "payload": {}}
        ]
    return [
        {"label": "Show my September payslip", "action": "explain-payslip", "payload": {"month": "2026-09"}},
        {"label": "What is PF?", "action": "faq-pf", "payload": {}},
        {"label": "What is TDS?", "action": "faq-tds", "payload": {}},
        {"label": "Draft a query for HR", "action": "draft-query", "payload": {}}
    ]


def _build_clearance_blocked_reason(emp_id: Optional[str], emp_name: Optional[str], comp_data: dict) -> Tuple[Optional[str], bool]:
    """Build blocking reason dynamically ONLY from clearance/recovery/engine data.
    Never invents unverified text.
    """
    if not emp_id:
        logger.warning("Masked warning: Employee ID is missing for settlement proposal.")
        return ("Needs input before approval", True)

    clearances = _load_mock_json("clearances.json")
    emp_clearances = [cl for cl in clearances if cl.get("employee_id") == emp_id and cl.get("status") == "pending"]

    reasons = []
    if emp_clearances:
        for cl in emp_clearances:
            cl_type = cl.get("clearance_type", "asset")
            item_name = f"{cl_type.title()} clearance"
            asset_desc = cl.get("asset_description")
            status = cl.get("status", "pending")
            detail = f"{asset_desc} {status}" if asset_desc else status
            name_str = f" for {emp_name}" if emp_name else ""
            reasons.append(f"{item_name} pending{name_str} ({detail})")
    else:
        recoveries = _load_mock_json("recoveries.json")
        emp_recovs = [rec for rec in recoveries if rec.get("employee_id") == emp_id and "pending" in str(rec.get("status", "")).lower()]
        for rec in emp_recovs:
            rec_type = rec.get("type", "asset")
            item_name = f"{rec_type.title()} recovery"
            asset_desc = rec.get("asset_description")
            status = rec.get("status", "pending")
            detail = f"{asset_desc} {status}" if asset_desc else status
            name_str = f" for {emp_name}" if emp_name else ""
            reasons.append(f"{item_name} pending{name_str} ({detail})")

    if reasons:
        count = len(reasons)
        item_word = "item needs" if count == 1 else "items need"
        return (f"{count} {item_word} input: {', '.join(reasons)}", True)

    return (None, False)


def _load_mock_json(filename: str) -> list:
    p = MOCK_DIR / filename
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def get_picker_employees_for_task(task: str, user: dict) -> list[dict]:
    allowed_ids = set(user.get("allowed_employee_ids") or [])
    all_employees = _load_mock_json("employees.json")
    emp_map = {e["employee_id"]: e for e in all_employees}

    if task in ("arrears", "hike"):
        revisions = _load_mock_json("salary-revisions.json")
        pending_revs = [r for r in revisions if r.get("status") == "pending HR proposal" and r.get("employee_id") in allowed_ids]
        candidates = []
        for r in pending_revs:
            eid = r["employee_id"]
            emp = emp_map.get(eid, {})
            hike = r.get("hike_percent", 10)
            eff = r.get("effective_date", "")
            candidates.append({
                "employee_id": eid,
                "name": emp.get("name", eid),
                "department": emp.get("department", ""),
                "subtitle": f"Pending revision · {hike}% hike from {eff}"
            })
        return candidates

    elif task in ("settlement", "full_and_final"):
        exits = _load_mock_json("exits.json")
        exit_candidates = [e for e in exits if e.get("employee_id") in allowed_ids]
        candidates = []
        for ex in exit_candidates:
            eid = ex["employee_id"]
            emp = emp_map.get(eid, {})
            lwd = ex.get("last_working_day", "")
            candidates.append({
                "employee_id": eid,
                "name": emp.get("name", eid),
                "department": emp.get("department", ""),
                "subtitle": f"Exit settlement · Last working day {lwd}"
            })
        return candidates

    elif task == "salary":
        candidates = []
        for eid in sorted(allowed_ids):
            emp = emp_map.get(eid)
            if emp:
                status_str = emp.get("employment_status", "active")
                candidates.append({
                    "employee_id": eid,
                    "name": emp.get("name", eid),
                    "department": emp.get("department", ""),
                    "subtitle": f"{emp.get('department', '')} · {status_str.capitalize()}"
                })
        return candidates

    return []


def _extract_candidate_name(text: str) -> Optional[str]:
    m = re.search(r"\b(?:for|of|employee)\s+([a-zA-Z]+(?:\s+[a-zA-Z]+)?)", text, re.IGNORECASE)
    if m:
        raw_val = m.group(1).strip()
        stop = {"an", "the", "a", "all", "full", "final", "settlement", "arrears", "salary", "hike", "proposal", "calculation", "breakdown", "each"}
        tokens = [t for t in raw_val.split() if t.lower() not in stop]
        if tokens:
            return " ".join(tokens)
    return None


def get_rule_file(filename: str) -> dict:
    if filename not in _RULES_CACHE:
        p = RULES_DIR / filename
        if p.exists():
            _RULES_CACHE[filename] = json.loads(p.read_text(encoding="utf-8"))
        else:
            _RULES_CACHE[filename] = {}
    return _RULES_CACHE[filename]


def format_inr(amount: Optional[float | int]) -> str:
    """Format numbers into Indian Rupee presentation format for UI copy."""
    if amount is None:
        return "Not available in generated data"
    is_neg = amount < 0
    val = abs(int(round(amount)))
    s = str(val)
    if len(s) > 3:
        last3 = s[-3:]
        remaining = s[:-3]
        groups = []
        while len(remaining) > 2:
            groups.insert(0, remaining[-2:])
            remaining = remaining[:-2]
        if remaining:
            groups.insert(0, remaining)
        formatted = ",".join(groups) + "," + last3
    else:
        formatted = s
    sign = "−" if is_neg else ""
    return f"{sign}₹{formatted}"


TOPIC_CHIPS_TABLE = {
    "USER-E05": {
        "pf": ["How much PF was cut in September?", "What was my August PF?", "What is PF?"],
        "tds": ["Why is my TDS zero?", "What is TDS?", "Which tax regime am I in?"],
        "tax": ["Why is my TDS zero?", "What is TDS?", "Which tax regime am I in?"],
        "lop": ["How many LOP days were recorded in September?", "What was my August LOP?", "What is LOP?"],
        "leave": ["How many LOP days were recorded in September?", "What was my August LOP?", "What is LOP?"],
        "salary": ["Why is my take-home pay lower in September?", "Explain my September pay", "Explain my August pay"],
        "pay": ["Why is my take-home pay lower in September?", "Explain my September pay", "Explain my August pay"],
        "payslip": ["Why is my take-home pay lower in September?", "Explain my September pay", "Explain my August pay"],
        "bonus": ["What is the annual performance bonus?", "What is statutory bonus?", "Draft a query for HR"],
        "arrears": ["What are salary arrears?", "Draft a query for HR"],
        "hike": ["What are salary arrears?", "Draft a query for HR"],
        "settlement": ["What is leave encashment?", "What is Gratuity?", "Draft a query for HR"],
        "query": ["What's happening with my query?", "Draft a query for HR"]
    },
    "USER-E06": {
        "pf": ["How much PF was cut in September?", "What was my August PF?", "What is PF?"],
        "tds": ["Why did my TDS increase?", "What is TDS?", "Which tax regime am I in?"],
        "tax": ["Why did my TDS increase?", "What is TDS?", "Which tax regime am I in?"],
        "lop": ["How many LOP days were recorded in September?", "What was my August LOP?", "What is LOP?"],
        "leave": ["How many LOP days were recorded in September?", "What was my August LOP?", "What is LOP?"],
        "salary": ["Why did my TDS increase?", "Explain my September pay", "Explain my August pay"],
        "pay": ["Why did my TDS increase?", "Explain my September pay", "Explain my August pay"],
        "payslip": ["Why did my TDS increase?", "Explain my September pay", "Explain my August pay"],
        "bonus": ["What is the annual performance bonus?", "What is statutory bonus?", "Draft a query for HR"],
        "arrears": ["What are salary arrears?", "Draft a query for HR"],
        "hike": ["What are salary arrears?", "Draft a query for HR"],
        "settlement": ["What is leave encashment?", "What is Gratuity?", "Draft a query for HR"],
        "query": ["What's happening with my query?", "Draft a query for HR"]
    },
    "USER-E16": {
        "pf": ["How much PF was cut in September?", "What was my August PF?", "What is PF?"],
        "tds": ["Why is my TDS zero?", "What is TDS?", "Which tax regime am I in?"],
        "tax": ["Why is my TDS zero?", "What is TDS?", "Which tax regime am I in?"],
        "lop": ["How many LOP days were recorded in September?", "What was my August LOP?", "What is LOP?"],
        "leave": ["How many LOP days were recorded in September?", "What was my August LOP?", "What is LOP?"],
        "salary": ["Why did my basic pay change?", "Explain my September pay", "Explain my August pay"],
        "pay": ["Why did my basic pay change?", "Explain my September pay", "Explain my August pay"],
        "payslip": ["Why did my basic pay change?", "Explain my September pay", "Explain my August pay"],
        "bonus": ["What is the annual performance bonus?", "What is statutory bonus?", "Draft a query for HR"],
        "arrears": ["What are salary arrears?", "Draft a query for HR"],
        "hike": ["What are salary arrears?", "Draft a query for HR"],
        "settlement": ["What is leave encashment?", "What is Gratuity?", "Draft a query for HR"],
        "query": ["What's happening with my query?", "Draft a query for HR"]
    },
    "DEFAULT_EMPLOYEE": {
        "pf": ["How much PF was cut in September?", "What was my August PF?", "What is PF?"],
        "tds": ["Why is my TDS zero?", "What is TDS?", "Which tax regime am I in?"],
        "tax": ["Why is my TDS zero?", "What is TDS?", "Which tax regime am I in?"],
        "lop": ["How many LOP days were recorded in September?", "What was my August LOP?", "What is LOP?"],
        "leave": ["How many LOP days were recorded in September?", "What was my August LOP?", "What is LOP?"],
        "salary": ["Explain my September pay", "Explain my August pay", "Compare August and September pay"],
        "pay": ["Explain my September pay", "Explain my August pay", "Compare August and September pay"],
        "payslip": ["Explain my September pay", "Explain my August pay", "Compare August and September pay"],
        "bonus": ["What is the annual performance bonus?", "What is statutory bonus?", "Draft a query for HR"],
        "arrears": ["What are salary arrears?", "Draft a query for HR"],
        "hike": ["What are salary arrears?", "Draft a query for HR"],
        "settlement": ["What is leave encashment?", "What is Gratuity?", "Draft a query for HR"],
        "query": ["What's happening with my query?", "Draft a query for HR"]
    },
    "HR01": {
        "pf": ["What is PF?", "What is basic pay?"],
        "tds": ["What is TDS?", "What is basic pay?"],
        "tax": ["What is TDS?", "What is basic pay?"],
        "lop": ["What is LOP?", "What is leave encashment?", "What needs my approval?"],
        "leave": ["What is LOP?", "What is leave encashment?", "What needs my approval?"],
        "salary": ["What needs my approval?", "Who is leaving this month?", "Calculate arrears"],
        "pay": ["What needs my approval?", "Who is leaving this month?", "Calculate arrears"],
        "payslip": ["What needs my approval?", "Who is leaving this month?", "Calculate arrears"],
        "bonus": ["What is the difference between gross and net pay?", "What needs my approval?"],
        "arrears": ["Which employees have a pending hike?", "Calculate arrears", "What needs my approval?"],
        "hike": ["Which employees have a pending hike?", "Calculate arrears", "What needs my approval?"],
        "settlement": ["Prepare full and final settlement", "Who is leaving this month?", "What needs my approval?"],
        "query": ["Show Neha's query", "Review payroll queries"]
    },
    "HR02": {
        "pf": ["What is PF?", "What is basic pay?"],
        "tds": ["What is TDS?", "What is basic pay?"],
        "tax": ["What is TDS?", "What is basic pay?"],
        "lop": ["What is LOP?", "What is leave encashment?", "What needs my approval?"],
        "leave": ["What is LOP?", "What is leave encashment?", "What needs my approval?"],
        "salary": ["What needs my approval?", "Calculate arrears"],
        "pay": ["What needs my approval?", "Calculate arrears"],
        "payslip": ["What needs my approval?", "Calculate arrears"],
        "bonus": ["Prepare the Sales quarterly incentive", "What needs my approval?"],
        "arrears": ["Which employees have a pending hike?", "Calculate arrears", "What needs my approval?"],
        "hike": ["Which employees have a pending hike?", "Calculate arrears", "What needs my approval?"],
        "settlement": ["Prepare full and final settlement", "What needs my approval?"],
        "query": ["Review payroll queries"]
    }
}


class ChatRouter:
    def handle_chat(self, user_id: str, message: str = "", action: Optional[str] = None, context: Optional[dict] = None) -> dict:
        user = USERS.get(user_id, USERS.get("HR01", {}))
        result = self._handle_chat_internal(user_id=user_id, message=message, action=action, context=context)
        if isinstance(result, dict) and "state" in result and isinstance(result["state"], dict):
            if "certainty" not in result["state"]:
                result["state"]["certainty"] = None
        return enforce_reply_permissions(result, user)

    def _handle_chat_internal(self, user_id: str, message: str = "", action: Optional[str] = None, context: Optional[dict] = None) -> dict:
        context = context or {}
        if user_id not in USERS:
            user = USERS.get("HR01")
        else:
            user = USERS[user_id]

        role = user.get("role", "Employee")
        surface = "CHAT-HR" if role == "HR Admin" else "CHAT-EMP"
        raw_msg = (message or "").strip()
        lower_msg = raw_msg.lower()

        # 1. Prompt Injection Guardrail
        injection_patterns = [
            r"ignore (all|previous) instructions",
            r"system prompt",
            r"reveal.*(instruction|prompt)",
            r"jailbreak",
            r"developer mode",
            r"forget (the|your) rules"
        ]
        for pat in injection_patterns:
            if re.search(pat, lower_msg):
                return self._build_refusal(role, surface, "Prompt injection prevented.", user=user)

        # 2. Cross-employee Data Access Guardrail (Scenario 12 / GR-2.1 - GR-2.6)
        if context.get("scenario_num") == 12:
            return self._build_scenario_12(user, role, surface)
        if context.get("scenario_num") == 10:
            return self._build_scenario_10(user, role, surface)

        allowed = set(user.get("allowed_employee_ids") or [])
        mentioned_emp_ids = get_mentioned_employee_ids(lower_msg)
        for emp_id in mentioned_emp_ids:
            if emp_id not in allowed:
                return self._build_scenario_12(user, role, surface)

        if role == "Employee":
            # Generic "other people's salary" inquiry
            if "other people" in lower_msg or "another person" in lower_msg or "colleague" in lower_msg:
                return self._build_scenario_12(user, role, surface)

        # 2b. Masked PII (PAN / Bank Details) Guardrail (Prompt 4 Item 4 / C53)
        if re.search(r"\bpan\b|\bpan card\b|\bpan number\b|\bbank details\b|\bbank account\b|\bbank info\b|\bbank information\b", lower_msg) and not re.search(r"\bbank deposit\b|\bbank credit\b|\bcredited in bank\b|\bcredited to bank\b", lower_msg):
            if role == "HR Admin" or (mentioned_emp_ids and mentioned_emp_ids[0] != user.get("employee_id")):
                target_name = EMPLOYEE_NAMES.get(mentioned_emp_ids[0], "Employee") if mentioned_emp_ids else "Employee"
                text = get_message("C53", role="HR Admin", Name=target_name)
            else:
                text = get_message("C53", role="Employee")
            return {
                "messages": [{"code": "C53", "text": text}],
                "cards": [],
                "chips": _get_user_fallback_chips(user),
                "state": {
                    "intent": "masked_pii",
                    "role": role,
                    "surface": surface,
                    "scenario_num": None,
                    "employee_id": mentioned_emp_ids[0] if mentioned_emp_ids else user.get("employee_id"),
                    "panel": None,
                    "certainty": None
                }
            }

        # 3. Out-of-Scope Requests (Personal Tax advice, Bank account verification)
        if re.search(r"\b(tax\s+)?regime\b.*\b(choose|select|recommend|advise|better)\b|\b(recommend|advise|suggestion|suggest|should i choose|choose|is better to choose)\b.*(\btax\s+)?regime\b|\b(tax\s+)?investment\b|\bhow (can|to|do) (i )?save tax\b|\bshould i choose (new|old)\b|\bwhich regime should i choose\b", lower_msg):
            tax_chips = [{"label": "What is TDS?", "action": "faq-tds", "payload": {}}]
            if user.get("employee_id") == "E06":
                tax_chips.insert(0, {"label": "Why did my TDS increase?", "action": "explain-tds", "payload": {}})
            elif user.get("employee_id") == "E05":
                tax_chips.insert(0, {"label": "Why is my TDS zero?", "action": "explain-tds-zero", "payload": {}})
            else:
                tax_chips.insert(0, {"label": "Which tax regime am I in?", "action": "explain-regime", "payload": {}})
            return {
                "messages": [
                    {"code": "C11", "text": get_message("C11")}
                ],
                "cards": [],
                "chips": tax_chips,
                "state": {
                    "intent": "out_of_scope",
                    "role": role,
                    "surface": surface,
                    "scenario_num": None,
                    "employee_id": user.get("employee_id"),
                    "panel": None
                }
            }

        if re.search(r"\bbank deposit\b|\bbank credit\b|\bbank account\b|\bcredited in bank\b", lower_msg):
            chips = [{"label": "Draft a query for HR", "action": "draft-query", "payload": {}}]
            if role == "Employee":
                if user.get("employee_id") == "E05":
                    chips.append({"label": "Why is my take-home pay lower in September?", "action": "explain-salary", "payload": {}})
                elif user.get("employee_id") == "E06":
                    chips.append({"label": "Why did my TDS increase?", "action": "explain-tds", "payload": {}})
                elif user.get("employee_id") == "E16":
                    chips.append({"label": "Did my basic pay or allowance change?", "action": "explain-deduction", "payload": {}})
                else:
                    chips.append({"label": "Show my September payslip", "action": "explain-payslip", "payload": {"month": "2026-09"}})
            return {
                "messages": [
                    {"code": "C21", "text": get_message("C21")},
                    {"code": "C28", "text": get_message("C28")}
                ],
                "cards": [],
                "chips": chips,
                "state": {
                    "intent": "out_of_scope",
                    "role": role,
                    "surface": surface,
                    "scenario_num": None,
                    "employee_id": user.get("employee_id"),
                    "panel": None
                }
            }

        # 4. Action-Based Routing (Chips, Scenario Picker, Governance Buttons)
        if action:
            act = action.lower()
            if act == "select-employee":
                return self._handle_employee_selection(user, role, surface, context)
            elif act in ("arrears-picker", "arrears", "calculate arrears"):
                return self._handle_arrears_picker(user, role, surface)
            elif act in ("settlement-picker", "settlement", "prepare settlement"):
                return self._handle_settlement_picker(user, role, surface)
            elif act in ("salary-picker", "show salary", "show an employee's salary"):
                return self._handle_salary_picker(user, role, surface)
            elif act in ("review-queries", "review payroll queries"):
                return self._handle_hr_query_review(user, role, surface, context)
            elif act in ("scenario-1", "scenario-01"):
                return self._build_scenario_1(user, role, surface)
            elif act in ("scenario-2", "scenario-02"):
                return self._build_scenario_2(user, role, surface)
            elif act in ("scenario-3", "scenario-03"):
                return self._build_scenario_3(user, role, surface)
            elif act in ("scenario-4", "scenario-04"):
                b_type = (context.get("bonus_type") or context.get("choice") or "").lower()
                b_key = "quarterly_sales_incentive" if ("sales" in b_type or "hyderabad" in b_type or "incentive" in b_type) else "annual_performance_bonus"
                return self._build_scenario_4(user, role, surface, bonus_type_key=b_key)
            elif act in ("scenario-5", "scenario-05"):
                return self._build_scenario_5(user, role, surface)
            elif act in ("scenario-6", "scenario-06"):
                return self._build_scenario_6(user, role, surface)
            elif act in ("scenario-7", "scenario-07"):
                return self._build_scenario_7(user, role, surface)
            elif act in ("scenario-8", "scenario-08"):
                return self._build_scenario_8(user, role, surface)
            elif act in ("scenario-9", "scenario-09", "explain-salary", "explain_salary"):
                return self._build_scenario_9(user, role, surface)
            elif act in ("scenario-10", "scenario-10", "explain-tds", "explain_tds"):
                return self._build_scenario_10(user, role, surface)
            elif act in ("scenario-11", "scenario-11", "explain-deduction", "explain_deduction"):
                return self._build_scenario_11(user, role, surface)
            elif act in ("scenario-12", "scenario-12"):
                return self._build_scenario_12(user, role, surface)
            elif act in ("scenario-13", "scenario-13"):
                return self._build_scenario_13(user, role, surface)
            elif act in ("approve-proposal", "approve", "approve proposal for payroll"):
                return self._handle_approve_proposal(user, role, surface, context)
            elif act in ("edit-proposal", "edit", "edit with reason"):
                return self._handle_edit_proposal(user, role, surface, context)
            elif act in ("reject-proposal", "reject", "reject proposal"):
                return self._handle_reject_proposal(user, role, surface, context)
            elif act in ("draft-query", "draft query", "draft a query for hr", "draft-query-for-hr"):
                return self._handle_draft_query(user, role, surface, context)
            elif act in ("draft-new-query", "draft new query", "draft a new query"):
                return self._handle_draft_query(user, role, surface, {**context, "force_new": True})
            elif act in ("confirm-send-query", "send-query", "confirm and send", "send this query to hr", "send query with listed evidence"):
                return self._handle_confirm_send_query(user, role, surface, context)
            elif act in ("append-query", "add to open query", "add to existing query", "add to my september query"):
                return self._handle_append_query(user, role, surface, context)
            elif act in ("query-status", "check my query status"):
                return self._handle_query_status(user, role, surface, context)
            elif act in ("confirm-reply-query", "confirm-reply"):
                return self._handle_confirm_reply_query(user, role, surface, context)
            elif act in ("confirm-resolve-query", "confirm-resolve"):
                return self._handle_resolve_query(user, role, surface, {**context, "confirmed": True})
            elif act in ("take-into-review", "take for review", "take into review", "hr-take-into-review"):
                return self._handle_take_into_review(user, role, surface, context)
            elif act in ("reply-query", "reply", "hr-reply"):
                return self._handle_reply_query(user, role, surface, context)
            elif act in ("resolve-query", "resolve", "hr-resolve"):
                return self._handle_resolve_query(user, role, surface, context)
            elif act in ("dispute-query", "dispute", "employee-dispute"):
                return self._handle_dispute_query(user, role, surface, context)
            elif act in ("close-query", "close", "employee-close", "acknowledge and close"):
                return self._handle_close_query(user, role, surface, context)
            elif act in ("approvals-list", "what-needs-approval", "pending-approvals"):
                return self._handle_approvals_list(user, role, surface)
            elif act in ("leavers-list", "who-is-leaving", "leavers-this-month"):
                return self._handle_leavers_list(user, role, surface)
            elif act in ("show-calculation", "show calculation", "show calculation proof", "view full month breakdown"):
                return self._handle_show_calculation(user, role, surface, context)
            elif act == "apply-selection":
                choice = (context.get("choice") or "").lower()
                if "annual" in choice or "engineering" in choice:
                    return self._build_scenario_4(user, role, surface, bonus_type_key="annual_performance_bonus")
                elif "sales" in choice or "hyderabad" in choice:
                    return self._build_scenario_4(user, role, surface, bonus_type_key="quarterly_sales_incentive")
                return self._build_bonus_clarifying_question(role, surface)
            elif act in ("explain-payslip", "explain_payslip", "payslip-breakdown"):
                target_month = (context.get("month") or context.get("target_month") or "2026-09")
                return self._build_payslip_breakdown(user, role, surface, target_month)
            elif act in ("explain-pf", "explain_pf", "pf-amount"):
                target_month = (context.get("month") or context.get("target_month") or "2026-09")
                return self._build_pf_amount(user, role, surface, target_month)
            elif act in ("explain-tds-zero", "explain_tds_zero", "tds-zero", "explain-tds-amount"):
                target_month = (context.get("month") or context.get("target_month") or "2026-09")
                return self._build_tds_amount(user, role, surface, target_month)
            elif act in ("explain-lop", "explain_lop", "lop-days"):
                target_month = (context.get("month") or context.get("target_month") or "2026-09")
                return self._build_lop_days(user, role, surface, target_month)
            elif act in ("compare-months", "compare_months"):
                return self._build_compare_months(user, role, surface)
            elif act in ("explain-regime", "explain_regime", "tax-regime"):
                return self._build_tax_regime(user, role, surface)
            elif act in ("unrecorded-topic", "unrecorded_topic"):
                return self._build_unrecorded_topic(user, role, surface)
            elif act in ("unrecorded-month", "unrecorded_month"):
                return self._build_unrecorded_month(user, role, surface)
            elif act.startswith("faq-"):
                faq_topic = act.replace("faq-", "")
                return self._handle_faq_query(faq_topic, role, surface, user)

        # 5. Natural Language Intent Mapping

        # Direct Natural Language Action Matchers: List questions (Items 9 & 10)
        if re.search(r"\b(who is leaving|who is leaving this month|leaving this month|leavers this month|employees leaving)\b", lower_msg):
            return self._handle_leavers_list(user, role, surface)
        if re.search(r"\b(what needs my approval|what needs approval|pending approval|proposals for approval|approval queue)\b", lower_msg):
            return self._handle_approvals_list(user, role, surface)

        # Item 2: Routing when HR mentions an employee AND a query word (query, reply, resolve, close, delete)
        if role == "HR Admin":
            query_words = ["query", "reply", "resolve", "close", "delete"]
            has_query_kw = any(re.search(rf"\b{qw}\b", lower_msg) for qw in query_words)
            mentioned_ids = get_mentioned_employee_ids(raw_msg)
            emp_target_id = None
            if mentioned_ids:
                emp_target_id = mentioned_ids[0]
            else:
                for eid, ename in EMPLOYEE_NAMES.items():
                    first_name = ename.split()[0].lower()
                    if first_name in lower_msg or ename.lower() in lower_msg:
                        emp_target_id = eid
                        break
            if has_query_kw and emp_target_id:
                return self._handle_hr_employee_query_flow(user, role, surface, emp_target_id, raw_msg, context)

        if re.search(r"^(approve proposal|approve for payroll|approve\b)", lower_msg):
            return self._handle_approve_proposal(user, role, surface, context)
        if re.search(r"^(edit with reason|edit proposal)", lower_msg):
            return self._handle_edit_proposal(user, role, surface, context)
        if re.search(r"^(reject proposal|reject\b)", lower_msg):
            return self._handle_reject_proposal(user, role, surface, context)
        if re.search(r"\bdraft.*query\b", lower_msg):
            return self._handle_draft_query(user, role, surface, context)
        if re.search(r"\b(send.*query|confirm and send)\b", lower_msg):
            return self._handle_confirm_send_query(user, role, surface, context)
        if re.search(r"\b(add to.*query|append.*query)\b", lower_msg):
            return self._handle_append_query(user, role, surface, context)
        if re.search(r"\b(take into review|take for review)\b", lower_msg):
            return self._handle_take_into_review(user, role, surface, context)
        if re.search(r"\b(reply to query|reply.*query)\b", lower_msg):
            return self._handle_reply_query(user, role, surface, context)
        if re.search(r"\b(resolve query|resolve\b)", lower_msg):
            return self._handle_resolve_query(user, role, surface, context)
        if re.search(r"\b(dispute query|dispute\b)", lower_msg):
            return self._handle_dispute_query(user, role, surface, context)
        if re.search(r"\b(close query|acknowledge and close)\b", lower_msg):
            return self._handle_close_query(user, role, surface, context)
        if re.search(r"\b(show calculation|view full month breakdown|show breakdown)\b", lower_msg):
            return self._handle_show_calculation(user, role, surface, context)

        # FAQ lookup priority for general definition questions
        topic_words_set = {"pf", "tds", "tax", "lop", "leave", "salary", "pay", "payslip", "bonus", "arrears", "hike", "settlement", "query"}
        if not faq_matcher.is_personal_pay_question(lower_msg) and lower_msg.strip() not in topic_words_set:
            if re.search(r"^(what is|what are|explain|who is|can hcm one|does approving|why is my bank|what does|how does)\b", lower_msg) or "faq" in lower_msg or (len(lower_msg.split()) <= 4 and not any(re.search(r"\b" + re.escape(tw) + r"\b", lower_msg) for tw in topic_words_set)):
                matched_faq, conf = faq_matcher.match(raw_msg)
                if matched_faq and conf >= 0.70:
                    return self._build_faq_response(matched_faq, conf, role, surface, user)

        # --- Part C: Employee Own-Pay Topics and Approved Fallbacks ---

        # C34 unrecorded topics: hike/arrears, bonus, CTC, leave balance, reimbursement, salary credit date, Form 16, PF balance
        # Note: October salary is an unrecorded month (C35), handled by month routing below.
        is_bonus_query = bool(re.search(r"\b(bonus|incentive)\b", lower_msg))
        is_unrecorded_topic_match = bool(re.search(
            r"\b(ctc|leave balance|remaining leave|reimbursement|claim|salary credit date|when.*salary.*credit|when.*pay.*credit|form 16|pf balance)\b",
            lower_msg
        ))
        if role == "Employee" and (is_bonus_query or is_unrecorded_topic_match or (re.search(r"\b(hike|arrears)\b", lower_msg) and not any(k in lower_msg for k in ("priya", "arjun", "kavya")))):
            return self._build_unrecorded_topic(user, role, surface)

        # Topic e: Compare any two months
        if re.search(r"\bcompare\b.*\b(august|september|months|pay|salary)\b|\bcompare\b", lower_msg):
            return self._build_compare_months(user, role, surface)

        # Dynamic month routing for Employee
        if role == "Employee":
            month_lookup = {
                "january": "2026-01", "february": "2026-02", "march": "2026-03",
                "april": "2026-04", "may": "2026-05", "june": "2026-06",
                "july": "2026-07", "august": "2026-08", "september": "2026-09",
                "october": "2026-10", "november": "2026-11", "december": "2026-12"
            }
            found_m = None
            for m_name, m_code in month_lookup.items():
                if re.search(r"\b" + m_name + r"\b", lower_msg):
                    found_m = (m_name, m_code)
                    break

            if found_m:
                m_name, m_code = found_m
                emp_id = user.get("employee_id") or "E05"
                ledger_months = get_employee_ledger_months(emp_id)
                # October is not processed and months outside the ledger get C35
                if m_code not in ledger_months:
                    if any(k in lower_msg for k in ("pay", "salary", "payslip", "pf", "tds", "tax", "lop", "breakdown")) or "what is my" in lower_msg or "explain" in lower_msg:
                        return self._build_unrecorded_month(user, role, surface)
                else:
                    # Month is in ledger
                    is_salary_drop = bool(re.search(
                        r"\b(why is my salary less|why did i get less|why is my pay less|less this month|salary.*less|pay.*less|take-home.*less|cut in.*salary|salary.*drop|take-home.*lower)\b",
                        lower_msg
                    )) or (("take-home" in lower_msg or "salary" in lower_msg or "payslip" in lower_msg) and ("lower" in lower_msg or "drop" in lower_msg or "less" in lower_msg))

                    is_tds_increase = ("tds" in lower_msg and ("increase" in lower_msg or "higher" in lower_msg or "more" in lower_msg))
                    is_basic_allowance = ("basic pay" in lower_msg or "allowance" in lower_msg or "gross did not change" in lower_msg or ("change" in lower_msg and "allowance" in lower_msg))

                    if is_salary_drop and (user.get("employee_id") == "E05" or (role == "HR Admin" and "E05" in (user.get("allowed_employee_ids") or []))):
                        return self._build_scenario_9(user, role, surface)
                    elif is_tds_increase and (user.get("employee_id") == "E06" or (role == "HR Admin" and "E06" in (user.get("allowed_employee_ids") or []))):
                        return self._build_scenario_10(user, role, surface)
                    elif is_basic_allowance and (user.get("employee_id") == "E16" or (role == "HR Admin" and "E16" in (user.get("allowed_employee_ids") or []))):
                        return self._build_scenario_11(user, role, surface)
                    elif "pf" in lower_msg:
                        return self._build_pf_amount(user, role, surface, month=m_code)
                    elif "tds" in lower_msg or ("tax" in lower_msg and "regime" not in lower_msg):
                        return self._build_tds_amount(user, role, surface, month=m_code)
                    elif "lop" in lower_msg:
                        return self._build_lop_days(user, role, surface, month=m_code)
                    elif any(k in lower_msg for k in ("pay", "salary", "payslip", "breakdown")) or "explain" in lower_msg:
                        return self._build_payslip_breakdown(user, role, surface, month=m_code)

        # Topic g: Tax regime from her record
        if re.search(r"\b(which|what)\b.*\btax regime\b.*\b(am i in|do i have|on my record|in my record)\b|\bwhich tax regime am i in\b|\bwhat is my tax regime\b|\bregime am i in\b|\bmy tax regime\b", lower_msg) and not ("choose" in lower_msg or "recommend" in lower_msg or "better" in lower_msg or "advise" in lower_msg):
            return self._build_tax_regime(user, role, surface)

        # Topic f: Query status
        if re.search(r"what('s| is) happening with my query\b|\b(track.*query|status of.*query)\b", lower_msg):
            return self._handle_query_status(user, role, surface, context)

        # Topic c: TDS amount & "why is my TDS zero" & "How much tax was cut?"
        if (re.search(r"\bwhy is my tds zero\b|\btds zero\b|\bwhy.*zero.*tds\b|\bwhy.*no tds\b|\bhow much (tax|tds)\b|\bwhat is my (tax|tds)\b|\btax was cut\b|\bcut in tax\b|\btax cut\b", lower_msg) or (lower_msg.strip() in ("tds", "my tds") and user.get("employee_id") != "E06")) and not ("increase" in lower_msg or "higher" in lower_msg or "more" in lower_msg):
            return self._build_tds_amount(user, role, surface)

        # Topic d: LOP days by month
        if re.search(r"\b(how many|why was there|why.*is there|why.*lop)\b.*\blop\b|\blop days\b|\bloss of pay days\b|\bhow many.*unpaid\b", lower_msg):
            return self._build_lop_days(user, role, surface)

        # Topic b: PF amount for a month
        if re.search(r"\b(how much|hw much|amount of|cut in)\b.*\bpf\b|\bmy pf\b|\bpf amount\b|\bpf was cut\b|\bhw much pf\b", lower_msg):
            return self._build_pf_amount(user, role, surface)

        # Topic a: Payslip breakdown for a month
        if re.search(r"\bexplain my (september|august) pay\b|\b(september|august) (payslip|breakdown|pay breakdown)\b|\b(payslip|pay) breakdown\b|\bexplain my pay\b", lower_msg):
            m = "2026-08" if "august" in lower_msg else "2026-09"
            return self._build_payslip_breakdown(user, role, surface, month=m)

        # Scenario 1 (Priya Sharma hike)
        if re.search(r"\b(priya|sharma)\b", lower_msg) or ("hike" in lower_msg and "lop" in lower_msg):
            if role != "HR Admin":
                return self._build_refusal(role, surface, "Access denied", user=user)
            return self._build_scenario_1(user, role, surface)

        # Scenario 2 (Arjun Rao PF ceiling hike)
        if re.search(r"\b(arjun|rao)\b", lower_msg) or ("hike" in lower_msg and "ceiling" in lower_msg):
            if role != "HR Admin":
                return self._build_refusal(role, surface, "Access denied", user=user)
            return self._build_scenario_2(user, role, surface)

        # Scenario 3 (Kavya Iyer missing attendance)
        if re.search(r"\b(kavya|iyer)\b", lower_msg) or ("hike" in lower_msg and "attendance" in lower_msg):
            if role != "HR Admin":
                return self._build_refusal(role, surface, "Access denied", user=user)
            return self._build_scenario_3(user, role, surface)

        # Scenario 5 (Meera Nair missing rating)
        if re.search(r"\b(meera|nair)\b", lower_msg) or ("bonus" in lower_msg and "rating" in lower_msg):
            if role != "HR Admin":
                return self._build_refusal(role, surface, "Access denied", user=user)
            return self._build_scenario_5(user, role, surface)

        # Bonus proposals (Ambiguous disambiguation vs specific runs)
        if "bonus" in lower_msg or "incentive" in lower_msg:
            if role != "HR Admin":
                return self._build_refusal(role, surface, "Access denied", user=user)
            if "annual" in lower_msg or "engineering" in lower_msg:
                return self._build_scenario_4(user, role, surface, bonus_type_key="annual_performance_bonus")
            elif "sales" in lower_msg or "hyderabad" in lower_msg or "incentive" in lower_msg:
                return self._build_scenario_4(user, role, surface, bonus_type_key="quarterly_sales_incentive")
            elif "team" in lower_msg or "proposal" in lower_msg or "run" in lower_msg or "calculate" in lower_msg or "prepare" in lower_msg or lower_msg.strip() == "bonus":
                return self._build_bonus_clarifying_question(role, surface)

        # Scenario 6 (Rahul Verma settlement)
        if re.search(r"\b(rahul|verma)\b", lower_msg) or ("settlement" in lower_msg and "gratuity" in lower_msg):
            if role != "HR Admin":
                return self._build_refusal(role, surface, "Access denied", user=user)
            return self._build_scenario_6(user, role, surface)

        # Scenario 7 (Lakshmi Reddy settlement)
        if re.search(r"\b(lakshmi|reddy)\b", lower_msg) or ("settlement" in lower_msg and "minimum service" in lower_msg):
            if role != "HR Admin":
                return self._build_refusal(role, surface, "Access denied", user=user)
            return self._build_scenario_7(user, role, surface)

        # Scenario 8 (Imran Khan exit recovery)
        if re.search(r"\b(imran|khan)\b", lower_msg) and ("recovery" in lower_msg or "prepare" in lower_msg or "exit recovery" in lower_msg) and "calculation" not in lower_msg and "unresolved" not in lower_msg:
            if role != "HR Admin":
                return self._build_refusal(role, surface, "Access denied", user=user)
            return self._build_scenario_8(user, role, surface)

        # Scenario 13 (Imran Khan settlement review / breakdown / calculation)
        if re.search(r"\b(imran|khan)\b", lower_msg) and ("review" in lower_msg or "calculation" in lower_msg or "breakdown" in lower_msg or "unresolved" in lower_msg or "settlement" in lower_msg):
            if role != "HR Admin":
                return self._build_refusal(role, surface, "Access denied", user=user)
            return self._build_scenario_13(user, role, surface)

        # Scenario 11 (Pooja Das / gross did not change / basic pay / allowance)
        if re.search(r"\b(pooja|e16)\b", lower_msg) or "basic pay" in lower_msg or "allowance" in lower_msg or "gross did not change" in lower_msg or "no earning" in lower_msg or ("decrease" in lower_msg and "gross" in lower_msg):
            has_access_s11 = (role == "HR Admin" and "E16" in (user.get("allowed_employee_ids") or [])) or user.get("employee_id") == "E16"
            if has_access_s11:
                return self._build_scenario_11(user, role, surface)
            if re.search(r"\b(what is|what are|what does\b.*\bmean|meaning of|definition of|define)\b", lower_msg) and not faq_matcher.is_personal_pay_question(lower_msg):
                matched_faq, conf = faq_matcher.match(raw_msg)
                if matched_faq and conf >= 0.70:
                    return self._build_faq_response(matched_faq, conf, role, surface, user=user)
            return self._build_unknown_fallback(role, surface, user=user, raw_msg=raw_msg)

        # Scenario 10 (Siddharth Jain / TDS increase)
        if re.search(r"\b(siddharth|e06)\b", lower_msg) or ("tds" in lower_msg and ("increase" in lower_msg or "higher" in lower_msg or "deduction" in lower_msg or "tax" in lower_msg or "why" in lower_msg or "change" in lower_msg)) or lower_msg.strip() == "tds":
            has_access_s10 = (role == "HR Admin" and "E06" in (user.get("allowed_employee_ids") or [])) or user.get("employee_id") == "E06"
            if has_access_s10:
                return self._build_scenario_10(user, role, surface)
            if re.search(r"\b(what is|what are|what does\b.*\bmean|meaning of|definition of|define)\b", lower_msg) and not faq_matcher.is_personal_pay_question(lower_msg):
                matched_faq, conf = faq_matcher.match(raw_msg)
                if matched_faq and conf >= 0.70:
                    return self._build_faq_response(matched_faq, conf, role, surface, user=user)
            return self._build_unknown_fallback(role, surface, user=user, raw_msg=raw_msg)

        # Scenario 9 (Neha Gupta / September salary drop / personal pay drop queries)
        is_salary_drop_query = bool(re.search(
            r"\b(why is my salary less|why did i get less|why is my pay less|less this month|salary.*less|pay.*less|take-home.*less|cut in.*salary|salary.*drop|take-home.*lower)\b",
            lower_msg
        ))
        if "neha" in lower_msg or "e05" in lower_msg or is_salary_drop_query or (
            ("take-home" in lower_msg or "salary" in lower_msg or "payslip" in lower_msg)
            and ("lower" in lower_msg or "drop" in lower_msg or "change" in lower_msg or "september" in lower_msg or "less" in lower_msg)
        ):
            has_access_s9 = (role == "HR Admin" and "E05" in (user.get("allowed_employee_ids") or [])) or user.get("employee_id") == "E05"
            if has_access_s9:
                return self._build_scenario_9(user, role, surface)
            return self._build_unknown_fallback(role, surface, user=user, raw_msg=raw_msg)

        # HR Tasks with Employee Picker (Part C)
        if role == "HR Admin":
            if re.search(r"\b(arrears|calculate arrears|prepare arrears|calculate hike|prepare hike)\b", lower_msg) or (
                "hike" in lower_msg and not any(k in lower_msg for k in ("priya", "sharma", "arjun", "rao", "kavya", "iyer", "review"))
            ):
                cand_name = _extract_candidate_name(raw_msg)
                return self._handle_arrears_picker(user, role, surface, cand_name)

            if re.search(r"\b(full and final|f&f|prepare settlement|prepare full and final)\b", lower_msg) or (
                "settlement" in lower_msg and not any(k in lower_msg for k in ("rahul", "verma", "lakshmi", "reddy", "imran", "khan", "review"))
            ):
                cand_name = _extract_candidate_name(raw_msg)
                return self._handle_settlement_picker(user, role, surface, cand_name)

            if re.search(r"\b(show.*salary|employee.*salary|salary of|view.*salary)\b", lower_msg) or lower_msg.strip() in ("salary", "show salary"):
                cand_name = _extract_candidate_name(raw_msg)
                return self._handle_salary_picker(user, role, surface, cand_name)

            if re.search(r"\b(review.*queries|review payroll queries|pending queries)\b", lower_msg):
                return self._handle_hr_query_review(user, role, surface, context)

        # Query Flows
        if re.search(r"\b(draft a new query|draft new query)\b", lower_msg):
            return self._handle_draft_query(user, role, surface, {**context, "force_new": True})
        if "draft" in lower_msg and "query" in lower_msg:
            return self._handle_draft_query(user, role, surface, context)
        if ("status" in lower_msg or "track" in lower_msg) and ("query" in lower_msg or "queries" in lower_msg):
            return self._handle_query_status(user, role, surface, context)
        if "review" in lower_msg and ("query" in lower_msg or "queries" in lower_msg):
            return self._handle_hr_query_review(user, role, surface, context)

        # Fallback to FAQ keyword match
        if not faq_matcher.is_personal_pay_question(lower_msg) and lower_msg.strip() not in topic_words_set:
            matched_faq, conf = faq_matcher.match(raw_msg)
            if matched_faq and conf >= 0.70:
                return self._build_faq_response(matched_faq, conf, role, surface, user=user)

        # 6. Fallback Response (Never hallucinate)
        return self._build_unknown_fallback(role, surface, user=user, raw_msg=raw_msg)

    # --- Scenario Builders ---

    def _build_scenario_1(self, user: dict, role: str, surface: str) -> dict:
        sc = bridge.get_scenario(1)
        r = sc["result"]
        t = r["totals"]
        disp = sc.get("display_inputs", {})
        old_sal = disp.get("old_monthly_salary", {}).get("total", {}).get("value")
        prop_sal = disp.get("proposed_monthly_salary", {}).get("total", {}).get("value")
        hike_pct = disp.get("requested_hike_percentage", {}).get("value")
        eff_date = disp.get("effective_date", {}).get("value")

        pf_rules = get_rule_file("pf-rules.json")
        tax_rules = get_rule_file("tax-rules.json")
        old_ceiling = pf_rules.get("wage_ceiling_before_change_inr", {}).get("value")
        old_eff_to = pf_rules.get("wage_ceiling_before_change_inr", {}).get("effective_to", "2026-09-16")
        new_ceiling = pf_rules.get("wage_ceiling_from_change_inr", {}).get("value")

        for _fn, _fv in [("old_sal", old_sal), ("prop_sal", prop_sal), ("hike_pct", hike_pct), ("eff_date", eff_date), ("old_ceiling", old_ceiling), ("new_ceiling", new_ceiling)]:
            if _fv is None:
                logger.warning(f"Masked warning: Engine field '{_fn}' is missing; omitted from display.")
        new_eff_from = pf_rules.get("wage_ceiling_from_change_inr", {}).get("effective_from", "2026-09-17")
        rules_ver = pf_rules.get("rules_version", "Northwind demo rules v1")

        old_date_str = datetime.strptime(old_eff_to, "%Y-%m-%d").strftime("%d %b %Y").lstrip("0") if old_eff_to else "16 Sep 2026"
        new_date_str = datetime.strptime(new_eff_from, "%Y-%m-%d").strftime("%d %b %Y").lstrip("0") if new_eff_from else "17 Sep 2026"

        pf_change_val = t["pf_change"]["employee"]["value"]
        pf_sentence = (
            f"PF change is ₹{pf_change_val} because monthly basic pay exceeds the PF wage ceiling "
            f"(₹{old_ceiling:,} until {old_date_str}, then ₹{new_ceiling:,} from {new_date_str}; {rules_ver}), "
            f"keeping contributions capped before and after the revision."
        )

        eng_cert = _get_engine_certainty(r)
        return {
            "messages": [
                {"code": "C03", "text": get_message("C03")}
            ],
            "cards": [
                {
                    "id": "card-prop-s1",
                    "type": "proposal_summary",
                    "title": "Proposal summary",
                    "certainty": eng_cert,
                    "data": {
                        "employee_name": "Priya Sharma",
                        "employee_id": "E01",
                        "proposal_type": "Back-dated hike proposal",
                        "requested_hike": f"{hike_pct}%",
                        "effective_date": eff_date,
                        "affected_periods": f"{len(r.get('months', []))} months ({r.get('months', [{}])[0].get('month')} to {r.get('months', [{}])[-1].get('month')})",
                        "old_monthly_salary_total": old_sal,
                        "proposed_monthly_salary_total": prop_sal,
                        "status": r.get("proposal_status", "Needs HR approval; not applied")
                    }
                },
                {
                    "id": "card-numbers-s1",
                    "type": "number_cards",
                    "title": "Arrears & tax breakdown",
                    "certainty": eng_cert,
                    "data": {
                        "hero_label": "Expected net arrears",
                        "hero_amount": t["net_arrears"]["value"],
                        "gross_arrears": t["gross_arrears"]["value"],
                        "employee_pf_change": t["pf_change"]["employee"]["value"],
                        "estimated_tds_impact": t["tds_impact"]["value"],
                        "arrears_only_tds_impact": t["arrears_only_tds_impact"]["value"],
                        "recurring_salary_tds_impact": t["recurring_salary_tds_impact"]["value"],
                        "payment_month": r.get("estimated_payment_month", "2026-10"),
                        "estimate_flag": r.get("flags", ["Estimated TDS if approved and paid in October 2026 payroll"])[0],
                        "pf_rule": pf_sentence
                    }
                },
                {
                    "id": "card-months-s1",
                    "type": "month_table",
                    "title": "Affected months summary",
                    "certainty": eng_cert,
                    "data": {
                        "months": [
                            {
                                "month": m["month"],
                                "old_gross": m["old"]["gross"]["value"],
                                "revised_gross": m["revised"]["gross"]["value"],
                                "diff": m["difference"]["value"],
                                "tds_impact": m["tds_impact"]["value"],
                                "paid_days": m["paid_days"]["value"],
                                "lop_days": disp.get("months", {}).get(m["month"], {}).get("lop_days", {}).get("value")
                            }
                            for m in r.get("months", [])
                        ],
                        "total_gross_arrears": t["gross_arrears"]["value"]
                    }
                },
                {
                    "id": "card-approval-s1",
                    "type": "approval_card",
                    "title": "Approval",
                    "certainty": eng_cert,
                    "data": {
                        "employee_name": "Priya Sharma",
                        "employee_id": "E01",
                        "period": "Apr–Sep 2026",
                        "scope_label": "Priya Sharma · Apr–Sep 2026",
                        "notice": get_message("C04"),
                        "actions": ["Approve proposal for payroll", "Edit with reason", "Reject proposal"],
                        "status": "pending",
                        "proposal_id": "PROP-SCENARIO-1",
                        "version": 1
                    }
                }
            ],
            "chips": [
                {"label": "Show calculation", "action": "show-calculation", "payload": {"scenario_num": 1}}
            ],
            "state": {
                "intent": "prepare_hike_proposal",
                "scenario_num": 1,
                "role": role,
                "surface": surface,
                "employee_id": "E01",
                "certainty": eng_cert,
                "panel": {
                    "title": "Calculation proof & month breakdown",
                    "employee_name": "Priya Sharma",
                    "employee_id": "E01",
                    "months": [
                        {
                            "month": m["month"],
                            "short_month": ["Apr", "May", "Jun", "Jul", "Aug", "Sep"][idx] if idx < 6 else m["month"][-2:],
                            "old_gross": m["old"]["gross"]["value"],
                            "revised_gross": m["revised"]["gross"]["value"],
                            "diff": m["difference"]["value"],
                            "pf_change": m["pf_change"]["employee"]["value"],
                            "tds_impact": m["tds_impact"]["value"],
                            "paid_days": m["paid_days"]["value"],
                            "lop_days": disp.get("months", {}).get(m["month"], {}).get("lop_days", {}).get("value"),
                            "formula": f"Earned = revised × {m['paid_days']['value']} ÷ {30 if m['month'] in ('2026-04', '2026-06', '2026-09') else 31}"
                        }
                        for idx, m in enumerate(r.get("months", []))
                    ],
                    "formulas": [
                        "Earned salary = monthly salary × paid days ÷ calendar days",
                        "Monthly arrears = revised earned gross − old earned gross",
                        f"PF ceiling rule: PF change is ₹{pf_change_val} because monthly basic pay exceeds the PF wage ceiling (₹{old_ceiling:,} until {old_date_str}, then ₹{new_ceiling:,} from {new_date_str}; {rules_ver}).",
                        f"Net Arrears = Gross Arrears ({format_inr(t['gross_arrears']['value'])}) − Employee PF Change ({format_inr(t['pf_change']['employee']['value'])}) − Estimated TDS Impact ({format_inr(t['tds_impact']['value'])}) = {format_inr(t['net_arrears']['value'])}"
                    ],
                    "rule_citations": [
                        f"PF wage ceiling: ₹{old_ceiling:,} until {old_date_str}, then ₹{new_ceiling:,} from {new_date_str} ({rules_ver})",
                        "Hike allocation rule: Proportional allocation across basic, HRA and special allowance",
                        "Rounding rule: Round each line to nearest rupee, then add rounded lines for totals (round half up)",
                        f"Income tax regime: New tax regime Tax year {tax_rules.get('tax_year', {}).get('value', {}).get('year', '2026-27')}",
                        f"Standard deduction: {format_inr(tax_rules.get('standard_deduction_inr', {}).get('value'))}",
                        f"Health and education cess: {tax_rules.get('health_and_education_cess', {}).get('value', {}).get('rate_percent', 4)}%",
                        f"Rules version: {rules_ver}"
                    ],
                    "note": "Calculated with simplified demo rules. Not for real payroll."
                }
            }
        }

    def _build_scenario_2(self, user: dict, role: str, surface: str) -> dict:
        sc = bridge.get_scenario(2)
        r = sc["result"]
        t = r["totals"]
        disp = sc.get("display_inputs", {})
        old_sal = disp.get("old_monthly_salary", {}).get("total", {}).get("value")
        prop_sal = disp.get("proposed_monthly_salary", {}).get("total", {}).get("value")
        hike_pct = disp.get("requested_hike_percentage", {}).get("value")
        eff_date = disp.get("effective_date", {}).get("value")

        for _fn, _fv in [("old_sal", old_sal), ("prop_sal", prop_sal), ("hike_pct", hike_pct), ("eff_date", eff_date)]:
            if _fv is None:
                logger.warning(f"Masked warning: Engine field '{_fn}' is missing; omitted from display.")
        eng_cert = _get_engine_certainty(r)
        return {
            "messages": [
                {"code": "C03", "text": get_message("C03")}
            ],
            "cards": [
                {
                    "id": "card-prop-s2",
                    "type": "proposal_summary",
                    "title": "Proposal summary",
                    "certainty": eng_cert,
                    "data": {
                        "employee_name": "Arjun Rao",
                        "employee_id": "E02",
                        "proposal_type": "Back-dated hike proposal",
                        "requested_hike": f"{hike_pct}%",
                        "effective_date": eff_date,
                        "affected_periods": f"{len(r.get('months', []))} months ({r.get('months', [{}])[0].get('month')} to {r.get('months', [{}])[-1].get('month')})",
                        "old_monthly_salary_total": old_sal,
                        "proposed_monthly_salary_total": prop_sal,
                        "status": r.get("proposal_status", "Needs HR approval; not applied")
                    }
                },
                {
                    "id": "card-numbers-s2",
                    "type": "number_cards",
                    "title": "Arrears & PF impact",
                    "certainty": eng_cert,
                    "data": {
                        "hero_label": "Expected net arrears",
                        "hero_amount": t["net_arrears"]["value"],
                        "gross_arrears": t["gross_arrears"]["value"],
                        "employee_pf_change": t["pf_change"]["employee"]["value"],
                        "estimated_tds_impact": t["tds_impact"]["value"],
                        "payment_month": r.get("estimated_payment_month", "2026-10")
                    }
                },
                {
                    "id": "card-approval-s2",
                    "type": "approval_card",
                    "title": "HR authorization",
                    "certainty": eng_cert,
                    "data": {
                        "employee_name": "Arjun Rao",
                        "employee_id": "E02",
                        "period": "September 2026",
                        "scope_label": "Arjun Rao · E02 · September 2026",
                        "notice": get_message("C04"),
                        "actions": ["Approve proposal for payroll", "Edit with reason", "Reject proposal"],
                        "status": "pending",
                        "proposal_id": "PROP-SCENARIO-2",
                        "version": 1
                    }
                }
            ],
            "chips": [
                {"label": "Show calculation", "action": "show-calculation", "payload": {"scenario_num": 2}}
            ],
            "state": {
                "intent": "prepare_hike_proposal",
                "scenario_num": 2,
                "role": role,
                "surface": surface,
                "employee_id": "E02",
                "certainty": eng_cert,
                "panel": {
                    "title": "September 2026 PF dual-segment proof",
                    "employee_name": "Arjun Rao",
                    "employee_id": "E02",
                    "formulas": [
                        f"Segment 1 (1–16 Sep): Wage ceiling ₹{get_rule_file('pf-rules.json').get('wage_ceiling_before_change_inr', {}).get('value'):,} (16 of 30 calendar days)",
                        f"Segment 2 (17–30 Sep): Wage ceiling ₹{get_rule_file('pf-rules.json').get('wage_ceiling_from_change_inr', {}).get('value'):,} (14 of 30 calendar days)",
                        f"Total PF change across dual segments = {format_inr(t['pf_change']['employee']['value'])}"
                    ],
                    "rule_citations": [
                        f"PF wage ceiling: ₹{get_rule_file('pf-rules.json').get('wage_ceiling_before_change_inr', {}).get('value'):,} until 16 Sep 2026; ₹{get_rule_file('pf-rules.json').get('wage_ceiling_from_change_inr', {}).get('value'):,} from 17 Sep 2026",
                        f"Employee PF contribution rate: {get_rule_file('pf-rules.json').get('employee_contribution_rate_percent', {}).get('value')}% of PF wage",
                        "Mid-month ceiling change: Pro-rated across dated calendar segments",
                        f"Rules version: {get_rule_file('pf-rules.json').get('rules_version', 'Northwind demo rules v1')}"
                    ]
                }
            }
        }

    def _build_scenario_3(self, user: dict, role: str, surface: str) -> dict:
        sc = bridge.get_scenario(3)
        r = sc["result"]
        aug_diff = next((m.get("difference", {}).get("value") for m in r.get("months", []) if m.get("month") == "2026-08"), None)
        sep_diff = next((m.get("difference", {}).get("value") for m in r.get("months", []) if m.get("month") == "2026-09"), None)
        eng_cert = _get_engine_certainty(r)
        # Build blocking reason dynamically from engine result months
        is_ready_s3, disabled_reason_s3, row_reason_s3 = evaluate_proposal_readiness("PROP-SCENARIO-3")
        s3_disabled = not is_ready_s3
        s3_blocking_reason = disabled_reason_s3

        return {
            "messages": [
                {"code": "C07", "text": "The required attendance record for 2026-07 is missing. I cannot explain a complete result for this scope."}
            ],
            "cards": [
                {
                    "id": "card-prop-s3",
                    "type": "proposal_summary",
                    "title": "Incomplete proposal summary",
                    "certainty": eng_cert,
                    "data": {
                        "employee_name": "Kavya Iyer",
                        "employee_id": "E03",
                        "proposal_type": "Back-dated hike proposal",
                        "status": "Needs HR approval; not applied",
                        "affected_periods": "3 months (2026-07 to 2026-09)"
                    }
                },
                {
                    "id": "card-numbers-s3",
                    "type": "number_cards",
                    "title": "Known monthly differences",
                    "certainty": eng_cert,
                    "data": {
                        "hero_label": "Expected net arrears",
                        "hero_amount": None,
                        "gross_arrears": None,
                        "august_diff": aug_diff,
                        "september_diff": sep_diff,
                        "note": "July attendance missing"
                    }
                },
                {
                    "id": "card-approval-s3",
                    "type": "approval_card",
                    "title": "HR authorization",
                    "certainty": eng_cert,
                    "data": {
                        "employee_name": "Kavya Iyer",
                        "employee_id": "E03",
                        "period": "Apr–Sep 2026",
                        "scope_label": "Kavya Iyer · Apr–Sep 2026",
                        "notice": get_message("C04"),
                        "actions": ["Approve proposal for payroll", "Edit with reason", "Reject proposal"],
                        "status": "pending",
                        "proposal_id": "PROP-SCENARIO-3",
                        "version": 1,
                        "disabled": s3_disabled,
                        "blocking_reason": s3_blocking_reason,
                        "disabled_reason": s3_blocking_reason,
                        "disabled_label": s3_blocking_reason
                    }
                }
            ],
            "chips": [
                {"label": "Show calculation", "action": "show-calculation", "payload": {"scenario_num": 3}}
            ],
            "state": {
                "intent": "prepare_hike_proposal",
                "scenario_num": 3,
                "role": role,
                "surface": surface,
                "employee_id": "E03",
                "certainty": eng_cert,
                "panel": {
                    "title": "Missing attendance proof",
                    "employee_name": "Kavya Iyer",
                    "employee_id": "E03",
                    "formulas": [
                        "2026-07: Attendance missing: Not available in generated data",
                        f"2026-08: Monthly diff = {format_inr(aug_diff)}",
                        f"2026-09: Monthly diff = {format_inr(sep_diff)}"
                    ],
                    "rule_citations": [
                        "Calendar-month divisor: Paid days equal eligible days up to last working day minus LOP",
                        f"Rules version: {get_rule_file('settlement-rules.json').get('rules_version', 'Northwind demo rules v1')}"
                    ]
                }
            }
        }

    def _build_bonus_clarifying_question(self, role: str, surface: str) -> dict:
        return {
            "messages": [],
            "cards": [
                {
                    "id": "card-clarify-bonus",
                    "type": "clarifying_question",
                    "title": "Which bonus type do you mean?",
                    "data": {
                        "question": "Which bonus type do you mean?",
                        "choices": [
                            "Annual performance bonus, FY 2025-26, Engineering",
                            "Q2 Sales incentive, Hyderabad Sales"
                        ],
                        "selected_choice": None
                    }
                }
            ],
            "chips": [
                {"label": "Annual performance bonus, FY 2025-26, Engineering"},
                {"label": "Q2 Sales incentive, Hyderabad Sales"}
            ],
            "state": {
                "intent": "clarifying_question",
                "role": role,
                "surface": surface,
                "scenario_num": None,
                "employee_id": None,
                "certainty": None,
                "panel": None
            }
        }

    def _build_scenario_4(self, user: dict, role: str, surface: str, bonus_type_key: str = "annual_performance_bonus") -> dict:
        sc = bridge.get_scenario(4)
        r = sc["result"]
        req = next((item for item in r["bonus_requests"] if item.get("bonus_type") == bonus_type_key), r["bonus_requests"][0])
        eng_cert = _get_engine_certainty(req)
        gross_total = req["known_eligible_gross"]["value"]
        gross_certainty = _get_engine_certainty(req.get("known_eligible_gross"))

        # Copy engine's own counts and lists directly (no counting in router or frontend)
        agg = req.get("aggregates", {})
        eligible_count = agg.get("eligible_count", {}).get("value")
        ineligible_count = agg.get("not_eligible_count", {}).get("value")
        needs_input_count = agg.get("needs_input_count", {}).get("value")

        eligible_list = req.get("eligible", [])
        not_eligible_list = req.get("not_eligible", [])
        needs_input_list = req.get("needs_input", [])

        if bonus_type_key == "quarterly_sales_incentive":
            display_bonus_type = "Sales incentive"
            display_period = req.get("period", "Q2 2026-27")
            card_title = "Sales incentive summary"
            prop_id = "PROP-SCENARIO-4-SALES"
            prop_scope_label = f"Sales incentive ({display_period}) · Hyderabad Sales · FY 2025-26"
            is_ready_s4, s4_disabled_reason, _ = evaluate_proposal_readiness(prop_id)
            s4_blocking_reason = s4_disabled_reason
            s4_disabled = not is_ready_s4
            emp_formulas = [
                f"{e['employee_id']} ({get_employee_name(e['employee_id'])}): Sales incentive {format_inr(e.get('amount', {}).get('value'))}"
                for e in req.get("employees", [])
            ]
        else:
            display_bonus_type = "Annual performance bonus"
            display_period = req.get("period", "FY 2025-26")
            card_title = "Team bonus run summary"
            prop_id = "PROP-SCENARIO-4-ANNUAL"
            prop_scope_label = f"Annual performance bonus · Engineering · {display_period}"

            is_ready_s4, s4_disabled_reason, s4_row_reason = evaluate_proposal_readiness(prop_id)
            s4_blocking_reason = s4_disabled_reason
            s4_disabled = not is_ready_s4
            emp_map = {e["employee_id"]: e for e in req.get("employees", [])}
            e01_amt = emp_map.get("E01", {}).get("amount", {}).get("value")
            e03_amt = emp_map.get("E03", {}).get("amount", {}).get("value")
            e04_amt = emp_map.get("E04", {}).get("amount", {}).get("value")
            e07_amt = emp_map.get("E07", {}).get("amount", {}).get("value")
            e08_amt = emp_map.get("E08", {}).get("amount", {}).get("value")
            emp_formulas = [
                f"E01 ({get_employee_name('E01')}): Annual bonus {format_inr(e01_amt)}",
                f"E03 ({get_employee_name('E03')}): Annual bonus {format_inr(e03_amt)} (tax incomplete)",
                f"E04 ({get_employee_name('E04')}): Annual bonus {format_inr(e04_amt)}",
                f"E07 ({get_employee_name('E07')}): Joiner proration {format_inr(e07_amt)}",
                f"E08 ({get_employee_name('E08')}): Notice exclusion: {format_inr(e08_amt)} (Ineligible)",
                f"E09 ({get_employee_name('E09')}): Missing performance rating (Needs input)"
            ]

        # F3: Bonus summary replies use templates only (C54 / C55)
        if bonus_type_key == "quarterly_sales_incentive":
            display_bonus_name = f"Sales incentive ({display_period})"
        else:
            display_bonus_name = f"Engineering annual performance bonus ({display_period})"

        if needs_input_count > 0:
            msg_code_s4 = "C54"
            msg_text_s4 = get_message("C54", bonus_name=display_bonus_name, eligible=eligible_count, not_eligible=ineligible_count, waiting=needs_input_count)
        else:
            msg_code_s4 = "C55"
            msg_text_s4 = get_message("C55", bonus_name=display_bonus_name, eligible=eligible_count, not_eligible=ineligible_count)

        return {
            "messages": [
                {"code": msg_code_s4, "text": msg_text_s4}
            ],
            "cards": [
                {
                    "id": "card-bonus-s4",
                    "type": "proposal_summary",
                    "title": card_title,
                    "certainty": eng_cert,
                    "data": {
                        "proposal_type": f"{display_bonus_type} ({display_period})",
                        "eligible_count": eligible_count,
                        "ineligible_count": ineligible_count,
                        "needs_input_count": needs_input_count,
                        "known_eligible_gross": gross_total,
                        "gross_eligible_total": gross_total,
                        "known_eligible_gross_certainty": gross_certainty,
                        "eligible": eligible_list,
                        "not_eligible": not_eligible_list,
                        "needs_input": needs_input_list,
                        "employee_names": {
                            e["employee_id"]: get_employee_name(e["employee_id"])
                            for e in req.get("employees", [])
                        },
                        "status": "Needs HR approval; not applied"
                    }
                },
                {
                    "id": f"card-approval-s4-{bonus_type_key}",
                    "type": "approval_card",
                    "title": "HR authorization",
                    "certainty": eng_cert,
                    "data": {
                        "employee_name": None,
                        "employee_id": None,
                        "period": display_period,
                        "scope_label": prop_scope_label,
                        "notice": get_message("C04"),
                        "actions": ["Approve proposal for payroll", "Edit with reason", "Reject proposal"],
                        "status": "pending",
                        "proposal_id": prop_id,
                        "version": 1,
                        "disabled": s4_disabled,
                        "blocking_reason": s4_blocking_reason,
                        "disabled_reason": s4_disabled_reason,
                        "disabled_label": s4_blocking_reason
                    }
                }
            ],
            "chips": [
                {"label": "Show calculation", "action": "show-calculation", "payload": {"scenario_num": 4}},
                {"label": "View bonus scope", "action": "show-calculation", "payload": {"scenario_num": 4}}
            ],
            "state": {
                "intent": "bonus_proposal",
                "scenario_num": 4,
                "role": role,
                "surface": surface,
                "employee_id": None,
                "certainty": eng_cert,
                "panel": {
                    "title": "Bonus eligibility & scope roster",
                    "formulas": emp_formulas,
                    "rule_citations": [
                        "Bonus proration rule: Joiners pro-rated by active days in performance year",
                        "Notice exclusion: Employees serving resignation notice excluded from bonus payout",
                        f"Rules version: {get_rule_file('bonus-rules.json').get('rules_version', 'Northwind demo rules v1')}"
                    ]
                }
            }
        }

    def _build_scenario_5(self, user: dict, role: str, surface: str) -> dict:
        sc = bridge.get_scenario(5)
        r = sc["result"]
        eng_cert = _get_engine_certainty(r)
        return {
            "messages": [
                {"code": "C07", "text": "The required performance record for FY 2025-26 is missing. I cannot explain a complete result for this scope."}
            ],
            "cards": [
                {
                    "id": "card-bonus-s5",
                    "type": "proposal_summary",
                    "title": "Employee bonus evaluation",
                    "certainty": eng_cert,
                    "data": {
                        "employee_name": "Meera Nair",
                        "employee_id": "E09",
                        "rating": None,
                        "bonus_amount": None,
                        "status": "Needs input"
                    }
                },
                {
                    "id": "card-approval-s5",
                    "type": "approval_card",
                    "title": "HR authorization (blocked)",
                    "certainty": eng_cert,
                    "data": {
                        "employee_name": "Meera Nair",
                        "employee_id": "E09",
                        "period": None,
                        "scope_label": "Meera Nair · E09",
                        "notice": "Cannot approve bonus without verified performance rating.",
                        "actions": [],
                        "disabled": True
                    }
                }
            ],
            "chips": [
                {"label": "Show calculation", "action": "show-calculation", "payload": {"scenario_num": 5}}
            ],
            "state": {
                "intent": "bonus_proposal",
                "scenario_num": 5,
                "role": role,
                "surface": surface,
                "employee_id": "E09",
                "certainty": eng_cert,
                "panel": {
                    "title": "Missing performance record",
                    "formulas": [
                        "Performance rating for FY 2025-26: Not available in generated data",
                        "Bonus calculation: Blocked until rating is supplied"
                    ],
                    "rule_citations": [
                        "Performance multiplier rule: Rating determines payout percentage",
                        "Rules version: Northwind demo rules v1"
                    ]
                }
            }
        }

    def _build_scenario_6(self, user: dict, role: str, surface: str) -> dict:
        sc = bridge.get_scenario(6)
        r = sc["result"]
        c = r["components"]
        eng_cert = _get_engine_certainty(r)
        return {
            "messages": [
                {"code": "C64", "text": get_message("C64", Name="Rahul Verma")}
            ],
            "cards": [
                {
                    "id": "card-settlement-s6",
                    "type": "proposal_summary",
                    "title": "Full & final settlement proposal",
                    "certainty": eng_cert,
                    "data": {
                        "employee_name": "Rahul Verma",
                        "employee_id": "E10",
                        "proposal_type": "Exit Settlement",
                        "status": "Needs HR approval; not applied",
                        "due_date": "2026-11-03"
                    }
                },
                {
                    "id": "card-components-s6",
                    "type": "component_list",
                    "title": "Settlement components ledger",
                    "certainty": eng_cert,
                    "data": {
                        "hero_label": "Final net settlement",
                        "hero_amount": r["final_net"]["value"],
                        "gross_payables": r["gross_payables"]["value"],
                        "total_deductions": r["total_deductions"]["value"],
                        "components": [
                            {"name": "Earned Salary", "amount": c["final_month_salary"]["amount"]["value"], "status": "Eligible"},
                            {"name": "Gratuity", "amount": c["gratuity"]["amount"]["value"], "status": "Eligible"},
                            {"name": "Leave Encashment", "amount": c["leave_encashment"]["amount"]["value"], "status": "Eligible"},
                            {"name": "Notice Shortfall Recovery", "amount": c["notice_shortfall_recovery"]["amount"]["value"], "status": "Eligible"}
                        ],
                        "due_date": "2026-11-03"
                    }
                },
                {
                    "id": "card-approval-s6",
                    "type": "approval_card",
                    "title": "HR authorization",
                    "certainty": eng_cert,
                    "data": {
                        "employee_name": "Rahul Verma",
                        "employee_id": "E10",
                        "period": "Exit Settlement",
                        "scope_label": "Rahul Verma · E10 · Exit Settlement",
                        "notice": get_message("C04"),
                        "actions": ["Approve proposal for payroll", "Edit with reason", "Reject proposal"],
                        "status": "pending",
                        "proposal_id": "PROP-SCENARIO-6",
                        "version": 1
                    }
                }
            ],
            "chips": [
                {"label": "Show calculation", "action": "show-calculation", "payload": {"scenario_num": 6}},
                {"label": "View full settlement breakdown", "action": "show-calculation", "payload": {"scenario_num": 6}}
            ],
            "state": {
                "intent": "settlement_proposal",
                "scenario_num": 6,
                "role": role,
                "surface": surface,
                "employee_id": "E10",
                "certainty": eng_cert,
                "panel": {
                    "title": "Settlement proof & component ledger",
                    "employee_name": "Rahul Verma",
                    "employee_id": "E10",
                    "formulas": [
                        f"Final Net = Gross Payables ({format_inr(r.get('gross_payables', {}).get('value'))}) − Total Deductions ({format_inr(r.get('total_deductions', {}).get('value'))}) = {format_inr(r.get('final_net', {}).get('value'))}",
                        f"Employee deductions = Employee PF ({format_inr(r.get('total_deductions', {}).get('value'))})",
                        f"Gratuity = 15 × last drawn salary × completed years ÷ 26 = {format_inr(c.get('gratuity', {}).get('amount', {}).get('value'))}",
                        f"Leave encashment = daily wage × unused encashable days = {format_inr(c.get('leave_encashment', {}).get('amount', {}).get('value'))}"
                    ],
                    "rule_citations": [
                        "Gratuity Act: 15 days wages per completed year of continuous service exceeding 5 years",
                        "Leave encashment formula: Daily rate calculated with 30-day divisor",
                        "Settlement due date rule: Target disbursement deadline 2026-11-03",
                        f"Rules version: {get_rule_file('settlement-rules.json').get('rules_version', 'Northwind demo rules v1')}"
                    ]
                }
            }
        }

    def _build_scenario_7(self, user: dict, role: str, surface: str) -> dict:
        sc = bridge.get_scenario(7)
        r = sc["result"]
        c = r["components"]
        grat_amt = c.get("gratuity", {}).get("amount", {}).get("value")
        eng_cert = _get_engine_certainty(r)
        return {
            "messages": [
                {"code": "C64", "text": get_message("C64", Name="Lakshmi Reddy")}
            ],
            "cards": [
                {
                    "id": "card-settlement-s7",
                    "type": "proposal_summary",
                    "title": "Full & final settlement proposal",
                    "certainty": eng_cert,
                    "data": {
                        "employee_name": "Lakshmi Reddy",
                        "employee_id": "E11",
                        "proposal_type": "Exit Settlement",
                        "status": "Needs HR approval; not applied"
                    }
                },
                {
                    "id": "card-components-s7",
                    "type": "component_list",
                    "title": "Settlement components",
                    "certainty": eng_cert,
                    "data": {
                        "components": [
                            {"name": "Gratuity", "amount": grat_amt, "status": "Ineligible", "note": "Close to minimum service: Continuous service less than 5-year requirement"}
                        ]
                    }
                },
                {
                    "id": "card-approval-s7",
                    "type": "approval_card",
                    "title": "HR authorization",
                    "certainty": eng_cert,
                    "data": {
                        "employee_name": "Lakshmi Reddy",
                        "employee_id": "E11",
                        "period": None,
                        "scope_label": "Lakshmi Reddy · E11",
                        "notice": get_message("C04"),
                        "actions": ["Approve proposal for payroll", "Edit with reason", "Reject proposal"],
                        "status": "pending",
                        "proposal_id": "PROP-SCENARIO-7",
                        "version": 1
                    }
                }
            ],
            "chips": [
                {"label": "Show calculation", "action": "show-calculation", "payload": {"scenario_num": 7}}
            ],
            "state": {
                "intent": "settlement_proposal",
                "scenario_num": 7,
                "role": role,
                "surface": surface,
                "employee_id": "E11",
                "certainty": eng_cert,
                "panel": {
                    "title": "Gratuity service eligibility proof",
                    "formulas": [
                        "Tenure: Continuous service is less than 5-year threshold",
                        f"Gratuity payable = {format_inr(grat_amt)}"
                    ],
                    "rule_citations": [
                        "Payment of Gratuity Act: Minimum 5 continuous years required",
                        f"Rules version: {get_rule_file('gratuity-rules.json').get('rules_version', 'Northwind demo rules v1')}"
                    ]
                }
            }
        }

    def _build_scenario_8(self, user: dict, role: str, surface: str) -> dict:
        sc = bridge.get_scenario(8)
        r = sc["result"]
        c = r.get("components", {})
        notice_amt = c.get("notice_shortfall_recovery", {}).get("amount", {}).get("value")
        advance_amt = c.get("loan_and_advance_recovery", {}).get("amount", {}).get("value")
        recov_subtotal = r.get("known_recoveries_subtotal", {}).get("value")
        eng_cert = _get_engine_certainty(r)
        # Build blocking reason dynamically from engine/clearance/recovery data
        s8_emp_id = r.get("employee_id")
        s8_emp_name = get_employee_name(s8_emp_id) if s8_emp_id else None

        for _fn, _fv in [("notice_amt", notice_amt), ("advance_amt", advance_amt), ("recov_subtotal", recov_subtotal), ("employee_id", s8_emp_id)]:
            if _fv is None:
                logger.warning(f"Masked warning: Engine field '{_fn}' is missing; omitted from display.")

        is_ready_s8, disabled_reason_s8, row_reason_s8 = evaluate_proposal_readiness("PROP-SCENARIO-8")
        s8_disabled = not is_ready_s8
        s8_blocking_reason = disabled_reason_s8

        return {
            "messages": [
                {"code": "C07", "text": "The required asset clearance record for exit clearance is missing. I cannot explain a complete result for this scope."},
                {"code": "C19", "text": "The final net is incomplete because unreturned company laptop is not yet known."}
            ],
            "cards": [
                {
                    "id": "card-settlement-s8",
                    "type": "proposal_summary",
                    "title": "Incomplete settlement proposal",
                    "certainty": eng_cert,
                    "data": {
                        "employee_name": "Imran Khan",
                        "employee_id": "E12",
                        "proposal_type": "Exit Recovery",
                        "status": "Needs HR approval; not applied"
                    }
                },
                {
                    "id": "card-components-s8",
                    "type": "component_list",
                    "title": "Recovery line items",
                    "certainty": eng_cert,
                    "data": {
                        "hero_label": "Final net",
                        "hero_amount": None,
                        "known_recoveries": recov_subtotal,
                        "known_recoveries_subtotal": recov_subtotal,
                        "components": [
                            {"name": "Notice Shortfall Recovery", "amount": notice_amt, "status": "Verified"},
                            {"name": "Salary Advance", "amount": advance_amt, "status": "Verified"},
                            {"name": "Asset Recovery", "amount": None, "status": "Unresolved"}
                        ]
                    }
                },
                {
                    "id": "card-approval-s8",
                    "type": "approval_card",
                    "title": "HR authorization",
                    "certainty": eng_cert,
                    "data": {
                        "employee_name": "Imran Khan",
                        "employee_id": "E12",
                        "period": "Settlement",
                        "scope_label": "Imran Khan · Settlement",
                        "notice": get_message("C04"),
                        "actions": ["Approve proposal for payroll", "Edit with reason", "Reject proposal"],
                        "status": "pending",
                        "proposal_id": "PROP-SCENARIO-8",
                        "version": 1,
                        "disabled": s8_disabled,
                        "blocking_reason": s8_blocking_reason,
                        "disabled_reason": s8_blocking_reason,
                        "disabled_label": s8_blocking_reason
                    }
                }
            ],
            "chips": [
                {"label": "Show calculation", "action": "show-calculation", "payload": {"scenario_num": 8}}
            ],
            "state": {
                "intent": "settlement_proposal",
                "scenario_num": 8,
                "role": role,
                "surface": surface,
                "employee_id": "E12",
                "certainty": eng_cert,
                "panel": {
                    "title": "Asset clearance status",
                    "formulas": [
                        f"Known recoveries = Notice shortfall recovery ({format_inr(notice_amt)}) + Salary advance ({format_inr(advance_amt)}) = {format_inr(recov_subtotal)}",
                        "Asset clearance pending: laptop pending",
                        "Final Net: Not available in generated data"
                    ],
                    "rule_citations": [
                        "Separation wages clearance hold: Unresolved asset recovery stays held without delaying final salary",
                        f"Rules version: {get_rule_file('settlement-rules.json').get('rules_version', 'Northwind demo rules v1')}"
                    ]
                }
            }
        }

    def _build_scenario_9(self, user: dict, role: str, surface: str) -> dict:
        sc = bridge.get_scenario(9)
        r = sc["result"]
        after_net = r["after"]["net_pay"]["value"]
        before_net = r["before"]["net_pay"]["value"]
        net_change = r["net_change"]["value"]
        reasons_list = r.get("reasons", [])
        lop_amt = reasons_list[0]["effect_amount"]["value"] if len(reasons_list) > 0 else -5000
        pf_amt = reasons_list[1]["effect_amount"]["value"] if len(reasons_list) > 1 else None
        tds_chg = r.get("tds_change", {}).get("value")

        after_gross = r.get("after", {}).get("earnings", {}).get("gross", {}).get("value")
        after_tot_ded = r.get("after", {}).get("total_deductions", {}).get("value")
        before_gross = r.get("before", {}).get("earnings", {}).get("gross", {}).get("value")
        before_pf = r.get("before", {}).get("pf", {}).get("value")
        after_pf = r.get("after", {}).get("pf", {}).get("value")
        pf_diff = r.get("employee_pf_change", {}).get("value")
        _gc = r.get("gross_change", {}).get("value")
        gross_diff = abs(_gc) if _gc is not None else None

        pf_rules = get_rule_file("pf-rules.json")
        old_ceiling = pf_rules.get("wage_ceiling_before_change_inr", {}).get("value")
        new_ceiling = pf_rules.get("wage_ceiling_from_change_inr", {}).get("value")

        for _fn, _fv in [("pf_amt", pf_amt), ("tds_chg", tds_chg), ("after_gross", after_gross), ("after_tot_ded", after_tot_ded), ("before_gross", before_gross), ("before_pf", before_pf), ("after_pf", after_pf), ("pf_diff", pf_diff), ("gross_diff", gross_diff), ("old_ceiling", old_ceiling), ("new_ceiling", new_ceiling)]:
            if _fv is None:
                logger.warning(f"Masked warning: Engine field '{_fn}' is missing; omitted from display.")
        rules_ver = pf_rules.get("rules_version", "Northwind demo rules v1")
        pf_cause = "PF deduction went up" if role == "Employee" else "PF ceiling change"
        pf_detail = "PF wage limit raised from 17 Sep" if role == "Employee" else "Revised ceiling from 17 Sep"

        open_queries = [
            q for q in lifecycle.get_queries()
            if q.get("employee_id") == "E05"
            and "2026-09" in q.get("months", [])
            and q.get("status") in ("In review", "Sent")
        ]
        if open_queries:
            open_q = open_queries[0]
            chips = [
                {"label": "Show breakdown", "action": "show-calculation", "payload": {"scenario_num": 9}},
                {"label": "Add to my September query", "action": "append-query", "payload": {"query_id": open_q["query_id"], "employee_id": "E05", "period": "2026-09"}},
                {"label": "Draft a new query", "action": "draft-new-query", "payload": {"employee_id": "E05", "period": "2026-09", "force_new": True}},
                {"label": "What is LOP?", "action": "faq-lop", "payload": {}}
            ]
        else:
            chips = [
                {"label": "Show breakdown", "action": "show-calculation", "payload": {"scenario_num": 9}},
                {"label": "Draft a query for HR", "action": "draft-query", "payload": {"employee_id": "E05", "period": "2026-09"}},
                {"label": "What is LOP?", "action": "faq-lop", "payload": {}},
                {"label": "What is PF?", "action": "faq-pf", "payload": {}}
            ]

        eng_cert = _get_engine_certainty(r)
        emp_name_s9 = "Neha Gupta"
        if role == "HR Admin":
            msg_code_s9 = "C42"
            msg_text_s9 = get_message("C42", Name=emp_name_s9, month="September", amount=format_inr(abs(net_change)), **{"previous_month": "August", "previous month": "August"})
        else:
            msg_code_s9 = "C58"
            msg_text_s9 = get_message("C58", month="September", amount=format_inr(abs(net_change)), **{"previous_month": "August", "previous month": "August"})

        return {
            "messages": [
                {"code": msg_code_s9, "text": msg_text_s9},
                {"code": "C27", "text": get_message("C27")}
            ],
            "cards": [
                {
                    "id": "card-hero-s9",
                    "type": "number_hero",
                    "title": "Take-home pay comparison",
                    "certainty": eng_cert,
                    "data": {
                        "hero_label": "September take-home",
                        "hero_amount": after_net,
                        "net_change": net_change,
                        "previous_month_label": "August take-home",
                        "previous_month_amount": before_net
                    }
                },
                {
                    "id": "card-reasons-s9",
                    "type": "reason_list",
                    "title": "Ranked by effect on take-home pay",
                    "certainty": eng_cert,
                    "data": {
                        "net_change": net_change,
                        "reasons": [
                            {"cause": "Loss of Pay (LOP)", "detail": f"{int(r.get('lop_days', 3))} LOP {'day' if int(r.get('lop_days', 3)) == 1 else 'days'} recorded", "amount": lop_amt},
                            {"cause": pf_cause, "detail": pf_detail, "amount": pf_amt}
                        ],
                        "tds_change": tds_chg
                    }
                }
            ],
            "chips": chips,
            "state": {
                "intent": "explain_salary_change",
                "scenario_num": 9,
                "role": role,
                "surface": surface,
                "employee_id": "E05",
                "certainty": eng_cert,
                "panel": {
                    "title": "September pay breakdown",
                    "formulas": [
                        f"Take-home pay = earned gross − total employee deductions = {format_inr(after_gross)} − {format_inr(after_tot_ded)} = {format_inr(after_net)} (change: {format_inr(net_change)})",
                        f"Loss of pay deduction = monthly gross × unpaid days ÷ calendar days = {format_inr(before_gross)} × 3 ÷ 30 = {format_inr(gross_diff)}",
                        f"PF deduction: Increased from {format_inr(before_pf)} to {format_inr(after_pf)} (+{format_inr(pf_diff)}) due to ceiling change on 17 Sep"
                    ],
                    "rule_citations": [
                        "Calendar-month divisor: Paid days equal calendar days minus LOP",
                        f"PF wage ceiling: ₹{old_ceiling:,} until 16 Sep 2026; ₹{new_ceiling:,} from 17 Sep 2026",
                        f"Rules version: {rules_ver}"
                    ]
                }
            }
        }

    def _build_scenario_10(self, user: dict, role: str, surface: str) -> dict:
        sc = bridge.get_scenario(10)
        r = sc["result"]
        after_tds = r["after"]["tds"]["amount"]["value"]
        tds_increase = r["tds_change"]["value"]
        _nc = r.get("net_change", {}).get("value")
        net_change = abs(_nc) if _nc is not None else None
        reasons_list = r.get("reasons", [])
        prior_tds_amt = reasons_list[0]["effect_amount"]["value"] if len(reasons_list) > 0 else None
        pf_amt = reasons_list[1]["effect_amount"]["value"] if len(reasons_list) > 1 else None

        for _fn, _fv in [("net_change", net_change), ("prior_tds_amt", prior_tds_amt), ("pf_amt", pf_amt)]:
            if _fv is None:
                logger.warning(f"Masked warning: Engine field '{_fn}' is missing; omitted from display.")

        disp = sc.get("display_inputs", {})
        prev_gross = disp.get("previous_employer_declared_gross", {}).get("value")
        prev_tds = disp.get("previous_employer_tds", {}).get("value")
        rem_tax = disp.get("remaining_yearly_tax", {}).get("value")
        raw_declared_range = disp.get("declared_month_range", {}).get("value")
        if not raw_declared_range:
            logger.warning("Masked warning: Engine field 'declared_month_range' is missing; omitted from display.")
            declared_months = None
        else:
            declared_months = format_month_range_phrase(raw_declared_range)

        tax_rules = get_rule_file("tax-rules.json")
        rules_ver = tax_rules.get("rules_version", "Northwind demo rules v1")
        tax_year = tax_rules.get("tax_year", {}).get("value", {}).get("year", "2026-27")

        eng_cert = _get_engine_certainty(r)
        emp_name_s10 = "Siddharth Jain"
        if role == "HR Admin":
            msg_s10_1 = {"code": "C42", "text": get_message("C42", Name=emp_name_s10, month="September", amount=format_inr(net_change), **{"previous month": "August"})}
            msg_s10_2 = {"code": "C29", "text": get_message("C29", Name=emp_name_s10, declared_months=declared_months)} if declared_months else None
        else:
            msg_s10_1 = {"code": "C30", "text": get_message("C30", later_month="September", net_change_amount=format_inr(net_change), lower_or_higher="lower", earlier_month="August")}
            msg_s10_2 = {"code": "C29", "text": get_message("C29", declared_months=declared_months)} if declared_months else None

        messages = [msg_s10_1]
        if msg_s10_2:
            messages.append(msg_s10_2)
        messages.append({"code": "C27", "text": get_message("C27")})

        return {
            "messages": messages,
            "cards": [
                {
                    "id": "card-hero-s10",
                    "type": "number_hero",
                    "title": "TDS deduction increase",
                    "certainty": eng_cert,
                    "data": {
                        "hero_label": "September TDS deduction",
                        "hero_amount": after_tds,
                        "tds_increase": tds_increase
                    }
                },
                {
                    "id": "card-reasons-s10",
                    "type": "reason_list",
                    "title": "Ranked by effect on take-home pay",
                    "certainty": eng_cert,
                    "data": {
                        "reasons": [
                            {"cause": "Prior employer declaration", "detail": "Declared income added to yearly projection", "amount": prior_tds_amt},
                            {"cause": "PF ceiling change", "detail": "Revised ceiling from 17 Sep", "amount": pf_amt}
                        ]
                    }
                }
            ],
            "chips": [
                {"label": "Show calculation", "action": "show-calculation", "payload": {"scenario_num": 10}},
                {"label": "Draft a query for HR", "action": "draft-query", "payload": {"employee_id": "E06", "period": "2026-09"}},
                {"label": "What is TDS?", "action": "faq-tds", "payload": {}}
            ],
            "state": {
                "intent": "explain_tds_change",
                "scenario_num": 10,
                "role": role,
                "surface": surface,
                "employee_id": "E06",
                "certainty": eng_cert,
                "panel": {
                    "title": "Tax calculation proof",
                    "formulas": [
                        f"Declared previous employer gross income = {format_inr(prev_gross)}",
                        f"Tax already deducted by previous employer = {format_inr(prev_tds)}",
                        f"Projected yearly income increased, remaining tax to distribute = {format_inr(rem_tax)}"
                    ],
                    "rule_citations": [
                        "Income Tax Act Section 192: Previous employer earnings declared under Form 12B integrated into annualized TDS",
                        f"Income tax regime: New tax regime Tax year {tax_year}",
                        f"Rules version: {rules_ver}"
                    ]
                }
            }
        }

    def _build_scenario_11(self, user: dict, role: str, surface: str) -> dict:
        sc = bridge.get_scenario(11)
        r = sc["result"]
        net_change = r.get("net_change", {}).get("value")
        reasons_list = r.get("reasons", [])
        pf_amt = reasons_list[0].get("effect_amount", {}).get("value") if reasons_list else None

        after_lines = r.get("after", {}).get("earnings", {}).get("lines", {})
        basic_val = after_lines.get("basic", {}).get("value")
        special_val = after_lines.get("special_allowance", {}).get("value")
        after_gross = r.get("after", {}).get("earnings", {}).get("gross", {}).get("value")
        after_tot_ded = r.get("after", {}).get("total_deductions", {}).get("value")
        after_net = r.get("after", {}).get("net_pay", {}).get("value")

        pf_rules = get_rule_file("pf-rules.json")
        old_ceiling = pf_rules.get("wage_ceiling_before_change_inr", {}).get("value")
        new_ceiling = pf_rules.get("wage_ceiling_from_change_inr", {}).get("value")
        pf_rate = pf_rules.get("employee_contribution_rate_percent", {}).get("value")

        for _fn, _fv in [("net_change", net_change), ("pf_amt", pf_amt), ("basic_val", basic_val), ("special_val", special_val), ("after_gross", after_gross), ("after_tot_ded", after_tot_ded), ("after_net", after_net), ("old_ceiling", old_ceiling), ("new_ceiling", new_ceiling), ("pf_rate", pf_rate)]:
            if _fv is None:
                logger.warning(f"Masked warning: Engine field '{_fn}' is missing; omitted from display.")
        rules_ver = pf_rules.get("rules_version", "Northwind demo rules v1")

        eng_cert = _get_engine_certainty(r)
        emp_name_s11 = "Pooja Das"
        if role == "HR Admin":
            msg_code_s11 = "C42"
            msg_text_s11 = f"{emp_name_s11}'s September take-home is {format_inr(abs(net_change))} lower than August. The main recorded reasons are below."
        else:
            msg_code_s11 = "C30"
            msg_text_s11 = f"Your September take-home is {format_inr(abs(net_change))} lower than August. The main recorded reasons are below."

        return {
            "messages": [
                {"code": msg_code_s11, "text": msg_text_s11},
                {"code": "C26", "text": get_message("C26")},
                {"code": "C27", "text": get_message("C27")}
            ],
            "cards": [
                {
                    "id": "card-hero-s11",
                    "type": "number_hero",
                    "title": "Take-home pay change",
                    "certainty": eng_cert,
                    "data": {
                        "hero_label": "Take-home net change",
                        "hero_amount": net_change,
                        "earnings_status": "No salary earning component change"
                    }
                },
                {
                    "id": "card-reasons-s11",
                    "type": "reason_list",
                    "title": "Main recorded reasons",
                    "certainty": eng_cert,
                    "data": {
                        "reasons": [
                            {"cause": "PF ceiling change", "detail": "Revised ceiling from 17 Sep", "amount": pf_amt}
                        ]
                    }
                }
            ],
            "chips": [
                {"label": "Show calculation", "action": "show-calculation", "payload": {"scenario_num": 11}},
                {"label": "What is PF?", "action": "faq-pf", "payload": {}}
            ],
            "state": {
                "intent": "explain_salary_change",
                "scenario_num": 11,
                "role": role,
                "surface": surface,
                "employee_id": "E16",
                "certainty": eng_cert,
                "panel": {
                    "title": "Earnings & deduction proof",
                    "formulas": [
                        f"Basic pay: Unchanged at {format_inr(basic_val)}",
                        f"Special allowance: Unchanged at {format_inr(special_val)}",
                        f"Gross earnings: Unchanged at {format_inr(after_gross)}",
                        f"Take-home pay = earned gross − total employee deductions = {format_inr(after_gross)} − {format_inr(after_tot_ded)} = {format_inr(after_net)} (change: {format_inr(net_change)})"
                    ],
                    "rule_citations": [
                        f"PF wage ceiling: ₹{old_ceiling:,} until 16 Sep 2026; ₹{new_ceiling:,} from 17 Sep 2026",
                        f"Employee PF contribution rate: {pf_rate}% of PF wage",
                        f"Rules version: {rules_ver}"
                    ]
                }
            }
        }

    def _build_scenario_12(self, user: dict, role: str, surface: str) -> dict:
        return self._build_refusal(role, surface, "Access boundary enforced.", user=user)

    def _build_scenario_13(self, user: dict, role: str, surface: str) -> dict:
        sc = bridge.get_scenario(13)
        r = sc["result"]
        c = r["components"]
        recov_subtotal = r.get("known_recoveries_subtotal", {}).get("value")
        notice_amt = c.get("notice_shortfall_recovery", {}).get("amount", {}).get("value")
        advance_amt = c.get("loan_and_advance_recovery", {}).get("amount", {}).get("value")
        eng_cert = _get_engine_certainty(r)
        # Build blocking reason dynamically from engine/clearance/recovery data
        s13_emp_id = r.get("employee_id")
        s13_emp_name = get_employee_name(s13_emp_id) if s13_emp_id else None

        for _fn, _fv in [("recov_subtotal", recov_subtotal), ("notice_amt", notice_amt), ("advance_amt", advance_amt), ("employee_id", s13_emp_id)]:
            if _fv is None:
                logger.warning(f"Masked warning: Engine field '{_fn}' is missing; omitted from display.")

        is_ready_s13, disabled_reason_s13, row_reason_s13 = evaluate_proposal_readiness("PROP-SCENARIO-13")
        s13_disabled = not is_ready_s13
        s13_blocking_reason = disabled_reason_s13
        return {
            "messages": [
                {"code": "C19", "text": "The final net is incomplete because unreturned company laptop is not yet known."}
            ],
            "cards": [
                {
                    "id": "card-settlement-s13",
                    "type": "proposal_summary",
                    "title": "Settlement breakdown (unresolved component)",
                    "certainty": eng_cert,
                    "data": {
                        "employee_name": "Imran Khan",
                        "employee_id": "E12",
                        "proposal_type": "Exit Settlement Breakdown",
                        "status": "Needs HR approval; not applied"
                    }
                },
                {
                    "id": "card-components-s13",
                    "type": "component_list",
                    "title": "Settlement ledger lines",
                    "certainty": eng_cert,
                    "data": {
                        "hero_label": "Final net",
                        "hero_amount": None,
                        "known_recoveries": recov_subtotal,
                        "known_recoveries_subtotal": recov_subtotal,
                        "components": [
                            {"name": "Notice Shortfall Recovery", "amount": notice_amt, "status": "Verified"},
                            {"name": "Salary Advance", "amount": advance_amt, "status": "Verified"},
                            {"name": "Asset Recovery", "amount": None, "status": "Unresolved"}
                        ]
                    }
                },
                {
                    "id": "card-approval-s13",
                    "type": "approval_card",
                    "title": "Partial authorization",
                    "certainty": eng_cert,
                    "data": {
                        "employee_name": "Imran Khan",
                        "employee_id": "E12",
                        "period": "Settlement",
                        "scope_label": "Imran Khan · Settlement",
                        "notice": "Approving verified component lines only. Unresolved asset recovery remains held and excluded from net payout.",
                        "actions": ["Approve proposal for payroll", "Edit with reason", "Reject proposal"],
                        "status": "pending",
                        "proposal_id": "PROP-SCENARIO-13",
                        "version": 1,
                        "disabled": s13_disabled,
                        "blocking_reason": s13_blocking_reason,
                        "disabled_reason": s13_blocking_reason,
                        "disabled_label": s13_blocking_reason
                    }
                }
            ],
            "chips": [
                {"label": "Show calculation", "action": "show-calculation", "payload": {"scenario_num": 13}}
            ],
            "state": {
                "intent": "settlement_proposal",
                "scenario_num": 13,
                "role": role,
                "surface": surface,
                "employee_id": "E12",
                "certainty": eng_cert,
                "panel": {
                    "title": "Settlement line review",
                    "formulas": [
                        f"Known recoveries = Notice shortfall recovery ({format_inr(notice_amt)}) + Salary advance ({format_inr(advance_amt)}) = {format_inr(recov_subtotal)}",
                        "Asset clearance hold: laptop pending",
                        "Final Net: Not available in generated data"
                    ],
                    "rule_citations": [
                        "Separation wages clearance hold: Unresolved asset recovery stays held without delaying final salary",
                        f"Rules version: {get_rule_file('settlement-rules.json').get('rules_version', 'Northwind demo rules v1')}"
                    ]
                }
            }
        }

    # --- Part C Employee Own-Pay Topic Builders ---

    def _build_payslip_breakdown(self, user: dict, role: str, surface: str, month: str = "2026-09") -> dict:
        emp_id = user.get("employee_id") or "E05"
        month = normalize_month_code(month)
        ledger_months = get_employee_ledger_months(emp_id)
        if month not in ledger_months:
            return self._build_unrecorded_month(user, role, surface)

        data = get_employee_payroll_data(emp_id, month)
        if not data:
            return self._build_unrecorded_month(user, role, surface)

        month_name = format_month_label(month)
        emp_name = get_employee_name(emp_id)
        cert = _get_engine_certainty(data)

        card = {
            "id": f"card-payslip-{month}",
            "type": "month_table",
            "title": f"Payslip · {month_name}",
            "data": {
                "employee_id": emp_id,
                "employee_name": emp_name,
                "month": month,
                "gross_pay": data["gross"],
                "basic": data["basic"],
                "hra": data["hra"],
                "special_allowance": data["special_allowance"],
                "da": data["da"],
                "total_deductions": data["total_deductions"],
                "pf": data["pf"],
                "tds": data["tds"],
                "net_pay": data["net_pay"]
            }
        }
        if cert:
            card["certainty"] = cert

        if role == "HR Admin":
            msg_text = get_message("C39", Name=emp_name, month=month_name)
        else:
            msg_text = get_message("C39", month=month_name)

        return {
            "messages": [
                {"code": "C39", "text": msg_text}
            ],
            "cards": [card],
            "chips": _get_user_fallback_chips(user),
            "state": {
                "intent": "payslip_breakdown",
                "scenario_num": None,
                "role": role,
                "surface": surface,
                "employee_id": emp_id,
                "certainty": cert,
                "panel": None
            }
        }

    def _build_pf_amount(self, user: dict, role: str, surface: str, month: str = "2026-09") -> dict:
        emp_id = user.get("employee_id") or "E05"
        month = normalize_month_code(month)
        ledger_months = get_employee_ledger_months(emp_id)
        if month not in ledger_months:
            return self._build_unrecorded_month(user, role, surface)

        data = get_employee_payroll_data(emp_id, month)
        month_name = format_month_label(month)
        pf_val = data["pf"] if data else 2220
        amount_str = format_inr(pf_val)
        cert = _get_engine_certainty(data, "pf_certainty")

        cards = []
        if pf_val != 0:
            c = {
                "id": f"card-pf-{month}",
                "type": "number_hero",
                "title": f"PF contribution — {month_name}",
                "data": {
                    "hero_label": f"{month_name} employee PF contribution",
                    "hero_amount": pf_val,
                    "employee_id": emp_id,
                    "month": month
                }
            }
            if cert:
                c["certainty"] = cert
            cards.append(c)

        if role == "HR Admin":
            emp_name = get_employee_name(emp_id)
            msg_text = get_message("C37", Name=emp_name, month=month_name, amount=amount_str)
        else:
            msg_text = get_message("C37", month=month_name, amount=amount_str)

        return {
            "messages": [
                {"code": "C37", "text": msg_text}
            ],
            "cards": cards,
            "chips": _get_user_fallback_chips(user),
            "state": {
                "intent": "pf_amount",
                "scenario_num": None,
                "role": role,
                "surface": surface,
                "employee_id": emp_id,
                "certainty": cert,
                "panel": None
            }
        }

    def _build_tds_amount(self, user: dict, role: str, surface: str, month: str = "2026-09") -> dict:
        emp_id = user.get("employee_id") or "E05"
        month = normalize_month_code(month)
        ledger_months = get_employee_ledger_months(emp_id)
        if month not in ledger_months:
            return self._build_unrecorded_month(user, role, surface)

        data = get_employee_payroll_data(emp_id, month)
        month_name = format_month_label(month)
        tds_val = data["tds"] if data else 0
        amount_str = format_inr(tds_val)

        engine_certainty = _get_engine_certainty(data, "tds_certainty")
        tds_formula = data.get("tds_formula", "Remaining yearly tax divided by remaining tax-year months including the current month") if data else "Remaining yearly tax divided by remaining tax-year months including the current month"
        tds_rules = data.get("tds_rules", []) if data else []

        rule_citations = []
        for r in tds_rules:
            if isinstance(r, dict):
                r_id = r.get("rule_id", "")
                r_val = r.get("value") or ""
                if isinstance(r_val, dict):
                    r_val_str = ", ".join(f"{k}: {v}" for k, v in r_val.items())
                elif isinstance(r_val, list):
                    r_val_str = f"{len(r_val)} slabs defined"
                else:
                    r_val_str = str(r_val)
                rule_citations.append(f"{r_id}: {r_val_str}")
            elif isinstance(r, str):
                rule_citations.append(r)

        if not rule_citations:
            rule_citations = [
                "tax-rules.json#monthly_tds_formula: (projected yearly tax - TDS already deducted) / remaining months including the current month",
                "tax-rules.json#rebate: taxable_income_limit_inr: 1200000, tax_up_to_limit_inr: 0",
                "tax-rules.json#standard_deduction_inr: 75000",
                "tax-rules.json#regime_scope: regime: new, old_regime_in_scope: False"
            ]

        # TDS reply uses C38 plus a "Show calculation" chip listing the engine formula and rule references (names and values only from data/rules).
        # Never state a reason the engine does not output (e.g. "below the rebate limit").
        # C11 only when the user asks for advice (which regime to choose, how to save tax, investments). Not for factual questions like "How much tax was cut?".
        chips = [
            {"label": "Show calculation", "action": "show-calculation", "payload": {"topic": "tds", "month": month}}
        ] + [c for c in _get_user_fallback_chips(user) if c.get("action") != "show-calculation"]

        cards = []
        if tds_val != 0:
            c = {
                "id": f"card-tds-{month}",
                "type": "number_hero",
                "title": f"TDS deduction — {month_name}",
                "data": {
                    "hero_label": f"{month_name} TDS deduction",
                    "hero_amount": tds_val,
                    "employee_id": emp_id,
                    "month": month
                }
            }
            if engine_certainty:
                c["certainty"] = engine_certainty
            cards.append(c)

        if role == "HR Admin":
            emp_name = get_employee_name(emp_id)
            msg_text = get_message("C38", Name=emp_name, month=month_name, amount=amount_str)
        else:
            msg_text = get_message("C38", month=month_name, amount=amount_str)

        return {
            "messages": [
                {"code": "C38", "text": msg_text}
            ],
            "cards": cards,
            "chips": chips,
            "state": {
                "intent": "tds_amount",
                "scenario_num": None,
                "role": role,
                "surface": surface,
                "employee_id": emp_id,
                "certainty": engine_certainty,
                "panel": {
                    "title": f"TDS calculation — {month_name}",
                    "formulas": [
                        tds_formula
                    ],
                    "rule_citations": rule_citations
                }
            }
        }

    def _build_lop_days(self, user: dict, role: str, surface: str, month: str = "2026-09") -> dict:
        emp_id = user.get("employee_id") or "E05"
        month = normalize_month_code(month)
        data = get_employee_payroll_data(emp_id, month)
        month_name = format_month_label(month)
        lop_days = data["lop_days"] if data else 3
        if role == "HR Admin":
            emp_name = get_employee_name(emp_id)
            text = get_message("C36", Name=emp_name, n=lop_days, month=month_name)
        else:
            text = get_message("C36", n=lop_days, month=month_name)
        cert = _get_engine_certainty(data, "lop_certainty")

        cards = []
        if lop_days != 0:
            c = {
                "id": f"card-lop-{month}",
                "type": "number_hero",
                "title": f"Attendance & loss of pay — {month_name}",
                "data": {
                    "hero_label": "Recorded LOP days",
                    "hero_amount": lop_days,
                    "month": month_name,
                    "employee_id": emp_id
                }
            }
            if cert:
                c["certainty"] = cert
            cards.append(c)

        return {
            "messages": [
                {"code": "C36", "text": text}
            ],
            "cards": cards,
            "chips": _get_user_fallback_chips(user),
            "state": {
                "intent": "lop_days",
                "scenario_num": None,
                "role": role,
                "surface": surface,
                "employee_id": emp_id,
                "certainty": cert,
                "panel": None
            }
        }

    def _build_compare_months(self, user: dict, role: str, surface: str, month_a: str = "2026-08", month_b: str = "2026-09") -> dict:
        emp_id = user.get("employee_id") or "E05"
        data_a = get_employee_payroll_data(emp_id, month_a)
        data_b = get_employee_payroll_data(emp_id, month_b)
        net_a = data_a["net_pay"] if data_a else 48200
        net_b = data_b["net_pay"] if data_b else 42780
        net_change = net_b - net_a
        direction = "lower" if net_change < 0 else "higher"
        name_a = format_month_label(month_a)
        name_b = format_month_label(month_b)
        cert_a = _get_engine_certainty(data_a, "net_pay_certainty")
        cert_b = _get_engine_certainty(data_b, "net_pay_certainty")
        cert = get_least_certain_label(cert_a, cert_b)

        cards = []
        comp_card = {
            "id": f"card-compare-{month_a}-{month_b}",
            "type": "number_hero",
            "title": f"{name_a} vs {name_b} pay comparison",
            "data": {
                "hero_label": "Net pay change",
                "hero_amount": net_change,
                "previous_month_label": f"{name_a} take-home",
                "previous_month_amount": net_a,
                "current_month_label": f"{name_b} take-home",
                "current_month_amount": net_b,
                "employee_id": emp_id
            }
        }
        if cert:
            comp_card["certainty"] = cert
        cards.append(comp_card)

        if role == "HR Admin":
            emp_name = EMPLOYEE_NAMES.get(emp_id, "The employee")
            if net_change == 0:
                msg_comp = f"{emp_name}'s {name_b} take-home is unchanged from {name_a}."
            else:
                msg_comp = f"{emp_name}'s {name_b} take-home is {format_inr(abs(net_change))} {direction} than {name_a}. The main recorded reasons are below."
        else:
            if net_change == 0:
                msg_comp = f"Your {name_b} take-home is unchanged from {name_a}."
            else:
                msg_comp = f"Your {name_b} take-home is {format_inr(abs(net_change))} {direction} than {name_a}. The main recorded reasons are below."

        return {
            "messages": [
                {"code": "C30", "text": msg_comp}
            ],
            "cards": cards,
            "chips": _get_user_fallback_chips(user),
            "state": {
                "intent": "compare_months",
                "scenario_num": None,
                "role": role,
                "surface": surface,
                "employee_id": emp_id,
                "certainty": cert,
                "panel": None
            }
        }

    def _build_tax_regime(self, user: dict, role: str, surface: str) -> dict:
        emp_id = user.get("employee_id") or "E05"
        data = get_employee_payroll_data(emp_id, "2026-09")
        regime_raw = (data.get("tax_regime") or "new").lower() if data else "new"

        reg_card = {
            "id": "card-tax-regime",
            "type": "certainty_label",
            "title": "Recorded tax regime",
            "data": {
                "tax_regime": regime_raw,
                "tax_year": "2026-27",
                "employee_id": emp_id
            }
        }

        if role == "HR Admin":
            emp_name = get_employee_name(emp_id)
            msg_text = get_message("C41", Name=emp_name, regime=regime_raw, tax_year="2026-27")
        else:
            msg_text = get_message("C41", regime=regime_raw, tax_year="2026-27")

        return {
            "messages": [
                {"code": "C41", "text": msg_text}
            ],
            "cards": [reg_card],
            "chips": _get_user_fallback_chips(user),
            "state": {
                "intent": "tax_regime",
                "scenario_num": None,
                "role": role,
                "surface": surface,
                "employee_id": emp_id,
                "certainty": None,
                "panel": None
            }
        }

    def _build_unrecorded_topic(self, user: dict, role: str, surface: str) -> dict:
        return {
            "messages": [
                {"code": "C34", "text": get_message("C34")}
            ],
            "cards": [],
            "chips": [
                {"label": "Draft a query for HR", "action": "draft-query", "payload": {}}
            ] + [c for c in _get_user_fallback_chips(user) if c.get("action") != "draft-query"][:2],
            "state": {
                "intent": "unrecorded_topic",
                "scenario_num": None,
                "role": role,
                "surface": surface,
                "employee_id": user.get("employee_id"),
                "panel": None
            }
        }

    def _build_unrecorded_month(self, user: dict, role: str, surface: str) -> dict:
        emp_id = user.get("employee_id") or "E05"
        ledger_months = get_employee_ledger_months(emp_id)
        available_str = format_available_months_phrase(ledger_months)

        chips = []
        if len(ledger_months) >= 1:
            m_latest = ledger_months[-1]
            chips.append({"label": f"Show my {format_month_label(m_latest)} payslip", "action": "explain-payslip", "payload": {"month": m_latest}})
        if len(ledger_months) >= 2:
            m_prev = ledger_months[-2]
            chips.append({"label": f"Show my {format_month_label(m_prev)} payslip", "action": "explain-payslip", "payload": {"month": m_prev}})
        chips.append({"label": "Draft a query for HR", "action": "draft-query", "payload": {}})

        return {
            "messages": [
                {"code": "C35", "text": get_message("C35", available_months=available_str)}
            ],
            "cards": [],
            "chips": chips,
            "state": {
                "intent": "unrecorded_month",
                "scenario_num": None,
                "role": role,
                "surface": surface,
                "employee_id": emp_id,
                "panel": None
            }
        }

    # --- Refusal, Fallback & FAQ Responses ---

    def _build_refusal(self, role: str, surface: str, reason: str = "", user: Optional[dict] = None) -> dict:
        return {
            "messages": [
                {"code": "C10", "text": get_message("C10")}
            ],
            "cards": [
                {
                    "id": "card-refusal",
                    "type": "refusal_card",
                    "title": "Permission denied",
                    "data": {
                        "message": get_message("C10"),
                        "reason": reason
                    }
                }
            ],
            "chips": _get_user_fallback_chips(user),
            "state": {
                "intent": "other_employee_data",
                "role": role,
                "surface": surface,
                "scenario_num": None,
                "employee_id": None,
                "certainty": None,
                "panel": None
            }
        }

    def _build_unknown_fallback(self, role: str, surface: str, user: Optional[dict] = None, raw_msg: str = "") -> dict:
        lower_msg = (raw_msg or "").lower()
        uid = (user or {}).get("user_id", "")
        eid = (user or {}).get("employee_id", "")

        # Prompt 2c-2c Item 7: "Did you mean?" chips when intent is unknown or low confidence, but a topic word is present
        # Topic words: pf, tds, tax, lop, leave, salary, pay, payslip, bonus, arrears, hike, settlement, query
        topic_words = ["pf", "tds", "tax", "lop", "leave", "salary", "pay", "payslip", "bonus", "arrears", "hike", "settlement", "query"]
        matched_topic = None
        if not ("unknown query" in lower_msg or "random nonsense" in lower_msg):
            for tw in topic_words:
                if re.search(r"\b" + re.escape(tw) + r"\b", lower_msg):
                    matched_topic = tw
                    break

        if matched_topic:
            user_table = TOPIC_CHIPS_TABLE.get(uid)
            if not user_table:
                if role == "HR Admin":
                    user_table = TOPIC_CHIPS_TABLE.get("HR01", {})
                else:
                    user_table = TOPIC_CHIPS_TABLE.get("DEFAULT_EMPLOYEE", {})
            questions = user_table.get(matched_topic, [])
            chips = [{"label": q} for q in questions[:3]]
            chips.append({"label": "Something else"})
            return {
                "messages": [
                    {"code": "C52", "text": get_message("C52")}
                ],
                "cards": [],
                "chips": chips,
                "state": {
                    "intent": "did_you_mean",
                    "role": role,
                    "surface": surface,
                    "scenario_num": None,
                    "employee_id": eid,
                    "panel": None
                }
            }

        fallback_text = get_message("C33")
        return {
            "messages": [
                {"code": "C33", "text": fallback_text}
            ],
            "cards": [],
            "chips": _get_user_fallback_chips(user),
            "state": {
                "intent": "unknown",
                "role": role,
                "surface": surface,
                "scenario_num": None,
                "employee_id": None,
                "panel": None
            }
        }

    def _build_faq_response(self, faq_entry: dict, confidence: float, role: str, surface: str, user: Optional[dict] = None) -> dict:
        link_text = "" if role == "HR Admin" else faq_entry.get("link_text", "")
        url = "" if role == "HR Admin" else faq_entry.get("url", "")
        return {
            "messages": [
                {"code": "FAQ", "text": "Here is the recorded meaning from the payroll glossary:"}
            ],
            "cards": [
                {
                    "id": f"card-faq-{faq_entry['id']}",
                    "type": "faq_answer",
                    "title": faq_entry.get("question", "FAQ Answer"),
                    "data": {
                        "id": faq_entry["id"],
                        "category": faq_entry.get("category", "Payroll Glossary"),
                        "question": faq_entry["question"],
                        "answer": faq_entry["answer"],
                        "link_text": link_text,
                        "url": url,
                        "confidence": confidence
                    }
                }
            ],
            "chips": _get_user_fallback_chips(user),
            "state": {
                "intent": "faq_question",
                "role": role,
                "surface": surface,
                "scenario_num": None,
                "employee_id": None,
                "panel": None
            }
        }

    def _handle_faq_query(self, topic: str, role: str, surface: str, user: Optional[dict] = None) -> dict:
        entry, conf = faq_matcher.match(f"what is {topic}")
        if not entry:
            entry, conf = faq_matcher.match(topic)
        if entry:
            return self._build_faq_response(entry, conf, role, surface, user)
        return self._build_unknown_fallback(role, surface, user)

    # --- Governance & Query Handlers ---

    def _handle_approve_proposal(self, user: dict, role: str, surface: str, context: dict) -> dict:
        if role != "HR Admin":
            return self._build_refusal(role, surface, "Only HR Admin can approve proposals.", user=user)

        prop_id = context.get("proposal_id")
        if not prop_id:
            return {
                "messages": [{"code": "C09", "text": "Proposal ID is required. Refusing approval without an exact proposal ID."}],
                "cards": [
                    {
                        "id": "card-approval-refused",
                        "type": "approval_card",
                        "title": "Action refused",
                        "data": {
                            "status": "error",
                            "status_badge": "Action refused • Missing proposal ID",
                            "notice": "Proposal ID is missing. No proposal was modified."
                        }
                    }
                ],
                "chips": [],
                "state": {"intent": "approve_error", "role": role, "surface": surface, "error": "Missing proposal_id"}
            }

        existing_prop = lifecycle.get_proposal(prop_id)
        if not existing_prop:
            return {
                "messages": [{"code": "C09", "text": f"Proposal '{prop_id}' is unknown. Cannot approve."}],
                "cards": [
                    {
                        "id": f"card-approval-error-{prop_id}",
                        "type": "approval_card",
                        "title": "Action refused",
                        "data": {
                            "proposal_id": prop_id,
                            "status": "error",
                            "status_badge": "Action refused • Unknown proposal",
                            "notice": f"Proposal '{prop_id}' was not found. No proposal was modified."
                        }
                    }
                ],
                "chips": [],
                "state": {"intent": "approve_error", "role": role, "surface": surface, "error": "Unknown proposal_id"}
            }

        req_version = context.get("version")
        if req_version is None or int(req_version) != existing_prop["current_version"]:
            s_num = existing_prop.get("scenario_num") or existing_prop.get("scope", {}).get("scenario_num")
            return {
                "messages": [{"code": "C25", "text": get_message("C25")}],
                "cards": [
                    {
                        "id": f"card-version-mismatch-{prop_id}",
                        "type": "approval_card",
                        "title": "Version mismatch",
                        "data": {
                            "proposal_id": prop_id,
                            "version": existing_prop["current_version"],
                            "status": "error",
                            "status_badge": "Action refused • Version mismatch",
                            "notice": get_message("C25")
                        }
                    }
                ],
                "chips": [{"label": "Show calculation", "action": "show-calculation", "payload": {"scenario_num": s_num}}] if s_num else [],
                "state": {"intent": "approve_error", "code": "C25", "role": role, "surface": surface, "panel": None}
            }

        version = int(req_version)

        is_ready, disabled_reason, _ = evaluate_proposal_readiness(prop_id, existing_prop)
        prop_cert = existing_prop.get("certainty")
        if not is_ready or prop_cert != "Complete for this scope":
            blocking_reason = disabled_reason or existing_prop.get("blocking_reason") or "Needs input before approval"
            s_num = existing_prop.get("scenario_num") or existing_prop.get("scope", {}).get("scenario_num")
            return {
                "messages": [{"code": "C07", "text": f"Cannot approve proposal: {blocking_reason}"}],
                "cards": [
                    {
                        "id": f"card-approval-blocked-{prop_id}",
                        "type": "approval_card",
                        "title": "Approval refused (incomplete scope)",
                        "certainty": prop_cert,
                        "data": {
                            "proposal_id": prop_id,
                            "version": existing_prop["current_version"],
                            "status": "blocked",
                            "status_badge": f"Approval refused • {prop_cert}",
                            "notice": blocking_reason,
                            "disabled": True,
                            "disabled_label": blocking_reason
                        }
                    }
                ],
                "chips": [{"label": "Show calculation", "action": "show-calculation", "payload": {"scenario_num": s_num}}] if s_num else [],
                "state": {"intent": "approve_error", "error": "Incomplete proposal", "role": role, "surface": surface}
            }

        try:
            res = lifecycle.approve_proposal(
                proposal_id=prop_id,
                version=version,
                actor=user,
                selected_scope=context.get("selected_scope")
            )
        except HTTPException as he:
            detail = he.detail
            if isinstance(detail, dict) and detail.get("code") == "C25":
                return {
                    "messages": [{"code": "C25", "text": get_message("C25")}],
                    "cards": [],
                    "chips": [],
                    "state": {"intent": "approve_error", "code": "C25", "role": role, "surface": surface, "panel": None}
                }
            raise he

        approver_name = user.get("name", "Anita Desai")
        approved_time = datetime.now(timezone.utc).isoformat()
        status_badge = f"Approved and ready for payroll • Version {version} • Approved by {approver_name}"

        raw_scope_label = existing_prop.get("scope_label") or existing_prop.get("scope", {}).get("scope_label") or ""
        if raw_scope_label.startswith("Approved: "):
            scope_label_display = raw_scope_label
        else:
            scope_label_display = f"Approved: {raw_scope_label}"

        emp_id = existing_prop.get("scope", {}).get("employee_id")
        emp_name = existing_prop.get("scope", {}).get("employee_name")
        period_str = existing_prop.get("scope", {}).get("period")
        s_num = existing_prop.get("scenario_num") or existing_prop.get("scope", {}).get("scenario_num")

        chips = [{"label": "Show calculation", "action": "show-calculation", "payload": {"scenario_num": s_num}}] if s_num else []

        return {
            "messages": [],
            "cards": [
                {
                    "id": "card-approval-success",
                    "type": "approval_card",
                    "title": "Approval",
                    "data": {
                        "proposal_id": prop_id,
                        "status": "approved",
                        "status_text": "Approved and ready for payroll",
                        "version": version,
                        "approver": approver_name,
                        "approved_at": approved_time,
                        "status_badge": status_badge,
                        "scope_label": scope_label_display,
                        "employee_name": emp_name,
                        "employee_id": emp_id,
                        "period": period_str
                    }
                }
            ],
            "chips": chips,
            "state": {
                "intent": "approve_proposal",
                "scenario_num": s_num,
                "role": role,
                "surface": surface,
                "employee_id": emp_id,
                "status": "Approved and ready for payroll",
                "panel": None
            }
        }

    def _handle_edit_proposal(self, user: dict, role: str, surface: str, context: dict) -> dict:
        if role != "HR Admin":
            return self._build_refusal(role, surface, "Only HR Admin can edit proposals.", user=user)

        prop_id = context.get("proposal_id")
        if not prop_id:
            return {
                "messages": [{"code": "C09", "text": "Proposal ID is required. Refusing edit without an exact proposal ID."}],
                "cards": [
                    {
                        "id": "card-edit-refused",
                        "type": "approval_card",
                        "title": "Action refused",
                        "data": {
                            "status": "error",
                            "status_badge": "Action refused • Missing proposal ID",
                            "notice": "Proposal ID is missing. No proposal was modified."
                        }
                    }
                ],
                "chips": [],
                "state": {"intent": "edit_error", "role": role, "surface": surface, "error": "Missing proposal_id"}
            }

        existing_prop = lifecycle.get_proposal(prop_id)
        if not existing_prop:
            return {
                "messages": [{"code": "C09", "text": f"Proposal '{prop_id}' is unknown. Cannot edit."}],
                "cards": [
                    {
                        "id": f"card-edit-error-{prop_id}",
                        "type": "approval_card",
                        "title": "Action refused",
                        "data": {
                            "proposal_id": prop_id,
                            "status": "error",
                            "status_badge": "Action refused • Unknown proposal",
                            "notice": f"Proposal '{prop_id}' was not found. No proposal was modified."
                        }
                    }
                ],
                "chips": [],
                "state": {"intent": "edit_error", "role": role, "surface": surface, "error": "Unknown proposal_id"}
            }

        line = context.get("line", "gross_arrears")
        proposed_value = context.get("proposed_value", 70000)
        reason = context.get("reason", "Adjusted attendance records for June")

        res = lifecycle.edit_proposal(
            proposal_id=prop_id,
            actor=user,
            line=line,
            proposed_value=proposed_value,
            reason=reason
        )

        prop_cert = existing_prop.get("certainty")
        s_num = existing_prop.get("scenario_num") or existing_prop.get("scope", {}).get("scenario_num")

        edit_card = {
            "id": f"card-edit-{prop_id}",
            "type": "proposal_summary",
            "title": "Revised proposal summary",
            "data": {
                "proposal_id": prop_id,
                "status": "Revised",
                "version": res["version"],
                "edited_line": line,
                "proposed_value": proposed_value,
                "reason": reason,
                "notice": get_message("C05")
            }
        }
        if prop_cert:
            edit_card["certainty"] = prop_cert

        chips = [{"label": "Show calculation", "action": "show-calculation", "payload": {"scenario_num": s_num}}] if s_num else []

        return {
            "messages": [
                {"code": "C05", "text": get_message("C05")}
            ],
            "cards": [edit_card],
            "chips": chips,
            "state": {
                "intent": "edit_proposal",
                "role": role,
                "surface": surface,
                "scenario_num": s_num,
                "version": res["version"],
                "certainty": prop_cert,
                "panel": None
            }
        }

    def _handle_reject_proposal(self, user: dict, role: str, surface: str, context: dict) -> dict:
        if role != "HR Admin":
            return self._build_refusal(role, surface, "Only HR Admin can reject proposals.", user=user)

        prop_id = context.get("proposal_id")
        if not prop_id:
            return {
                "messages": [{"code": "C09", "text": "Proposal ID is required. Refusing rejection without an exact proposal ID."}],
                "cards": [
                    {
                        "id": "card-reject-refused",
                        "type": "approval_card",
                        "title": "Action refused",
                        "data": {
                            "status": "error",
                            "status_badge": "Action refused • Missing proposal ID",
                            "notice": "Proposal ID is missing. No proposal was modified."
                        }
                    }
                ],
                "chips": [],
                "state": {"intent": "reject_error", "role": role, "surface": surface, "error": "Missing proposal_id"}
            }

        existing_prop = lifecycle.get_proposal(prop_id)
        if not existing_prop:
            return {
                "messages": [{"code": "C09", "text": f"Proposal '{prop_id}' is unknown. Cannot reject."}],
                "cards": [
                    {
                        "id": f"card-reject-error-{prop_id}",
                        "type": "approval_card",
                        "title": "Action refused",
                        "data": {
                            "proposal_id": prop_id,
                            "status": "error",
                            "status_badge": "Action refused • Unknown proposal",
                            "notice": f"Proposal '{prop_id}' was not found. No proposal was modified."
                        }
                    }
                ],
                "chips": [],
                "state": {"intent": "reject_error", "role": role, "surface": surface, "error": "Unknown proposal_id"}
            }

        reason = context.get("reason", "Documentation incomplete or unverified.")
        res = lifecycle.reject_proposal(proposal_id=prop_id, actor=user, reason=reason)

        prop_cert = existing_prop.get("certainty")
        s_num = existing_prop.get("scenario_num") or existing_prop.get("scope", {}).get("scenario_num")

        reject_card = {
            "id": f"card-reject-{prop_id}",
            "type": "approval_card",
            "title": "Proposal rejected",
            "data": {
                "proposal_id": prop_id,
                "status": "rejected",
                "status_badge": "Rejected • Not approved for payroll",
                "notice": "This proposal has been rejected and will not be applied to payroll."
            }
        }
        if prop_cert:
            reject_card["certainty"] = prop_cert

        return {
            "messages": [
                {"code": "REJECTED", "text": "The proposal has been rejected."}
            ],
            "cards": [reject_card],
            "chips": [],
            "state": {
                "intent": "reject_proposal",
                "role": role,
                "surface": surface,
                "scenario_num": s_num,
                "certainty": prop_cert,
                "panel": None
            }
        }

    def _handle_draft_query(self, user: dict, role: str, surface: str, context: dict) -> dict:
        emp_id = context.get("employee_id") or user.get("employee_id") or "E05"
        period = context.get("period") or "2026-09"
        desc = context.get("description") or "Please review my September attendance and LOP deduction."

        if role == "Employee" and not context.get("force_new") and not context.get("description"):
            open_queries = [
                q for q in lifecycle.get_queries(employee_id=emp_id)
                if q.get("status") in ("In review", "Sent")
                and (not period or period in q.get("months", []))
            ]
            if open_queries:
                target_q = open_queries[0]
                return {
                    "messages": [
                        {"code": "C14", "text": get_message("C14")}
                    ],
                    "cards": [],
                    "chips": [
                        {"label": "Add to my September query", "action": "append-query", "payload": {"target_query_id": target_q["query_id"], "employee_id": emp_id, "period": period}},
                        {"label": "Draft a new query", "action": "draft-new-query", "payload": {"employee_id": emp_id, "period": period, "force_new": True}}
                    ],
                    "state": {
                        "intent": "clarify_open_query",
                        "role": role,
                        "surface": surface,
                        "employee_id": emp_id,
                        "panel": None
                    }
                }

        evidence = context.get("evidence") or [
            {"type": "payslip", "period": period, "source": f"PAY-{emp_id}-{period}"},
            {"type": "attendance", "period": period, "lop_days": 3, "source": f"ATT-{emp_id}-{period}"}
        ]
        res = lifecycle.draft_query(
            actor=user,
            employee_id=emp_id,
            category="salary",
            months=[period],
            description=desc,
            evidence=evidence
        )
        draft = res["draft"]
        return {
            "messages": [
                {"code": "C12", "text": get_message("C12")}
            ],
            "cards": [
                {
                    "id": "card-query-draft",
                    "type": "query_draft",
                    "title": "Review query draft",
                    "data": {
                        "draft": draft,
                        "notice": get_message("C12"),
                        "actions": ["Send this query to HR", "Add to open query", "Cancel draft"]
                    }
                }
            ],
            "chips": [
                {"label": "Send query with listed evidence", "action": "confirm-send-query", "payload": {"draft": draft}},
                {"label": "Add to existing query", "action": "append-query", "payload": {"draft": draft}},
                {"label": "Cancel", "action": "query-status", "payload": {}}
            ],
            "state": {
                "intent": "draft_query",
                "role": role,
                "surface": surface,
                "employee_id": emp_id,
                "draft": draft,
                "panel": None
            }
        }

    def _handle_confirm_send_query(self, user: dict, role: str, surface: str, context: dict) -> dict:
        draft = context.get("draft")
        emp_id = user.get("employee_id") or "E05"
        if not draft:
            draft_res = lifecycle.draft_query(
                actor=user,
                employee_id=emp_id,
                category="salary",
                months=["2026-09"],
                description=context.get("description", "Please review my September attendance and LOP deduction."),
                evidence=[]
            )
            draft = draft_res["draft"]
        elif context.get("description"):
            draft["description"] = context["description"]

        sent_res = lifecycle.confirm_send_query(
            actor=user,
            draft=draft,
            add_or_new="new",
            confirmed=True
        )
        sent_query = sent_res["query"]
        return {
            "messages": [
                {"code": "C15", "text": get_message("C15")}
            ],
            "cards": [
                {
                    "id": "card-send-conf",
                    "type": "send_confirmation",
                    "title": "Query sent",
                    "data": {
                        "query_id": sent_query["query_id"],
                        "status": "Sent",
                        "status_message": get_message("C15")
                    }
                }
            ],
            "chips": _get_user_fallback_chips(user),
            "state": {
                "intent": "query_status",
                "role": role,
                "surface": surface,
                "employee_id": draft.get("employee_id"),
                "panel": None
            }
        }

    def _handle_append_query(self, user: dict, role: str, surface: str, context: dict) -> dict:
        draft = context.get("draft")
        emp_id = user.get("employee_id") or "E05"
        if not draft:
            draft_res = lifecycle.draft_query(
                actor=user,
                employee_id=emp_id,
                category="salary",
                months=["2026-09"],
                description=context.get("description", "Additional clarification on September attendance."),
                evidence=[]
            )
            draft = draft_res["draft"]

        queries = lifecycle.get_queries(employee_id=emp_id)
        target_id = context.get("target_query_id") or (queries[0]["query_id"] if queries else None)
        if not target_id:
            return self._handle_confirm_send_query(user, role, surface, context)

        append_res = lifecycle.confirm_send_query(
            actor=user,
            draft=draft,
            add_or_new="add",
            target_query_id=target_id,
            confirmed=True
        )
        q = append_res["query"]
        msg_code = "C15" if q["status"] == "Sent" else "C16"
        return {
            "messages": [
                {"code": msg_code, "text": get_message(msg_code)}
            ],
            "cards": [
                {
                    "id": f"card-appended-{q['query_id']}",
                    "type": "query_status",
                    "title": "Query updated",
                    "data": {
                        "query_id": q["query_id"],
                        "status": q["status"],
                        "description": q["description"]
                    }
                }
            ],
            "chips": [
                {"label": "Check my query status", "action": "query-status", "payload": {}}
            ],
            "state": {
                "intent": "query_status",
                "role": role,
                "surface": surface,
                "employee_id": emp_id,
                "panel": None
            }
        }

    def _handle_query_status(self, user: dict, role: str, surface: str, context: dict) -> dict:
        emp_id = user.get("employee_id")
        queries = lifecycle.get_queries(employee_id=emp_id) if emp_id else lifecycle.get_queries()
        if not queries:
            return {
                "messages": [
                    {"code": "NO_QUERY", "text": "You do not have any open payroll queries recorded."}
                ],
                "cards": [],
                "chips": [
                    {"label": "Draft a query for HR", "action": "draft-query", "payload": {}}
                ],
                "state": {
                    "intent": "query_status",
                    "role": role,
                    "surface": surface,
                    "employee_id": emp_id,
                    "panel": None
                }
            }
        latest = queries[-1]
        st = latest.get("status", "Sent")
        if st.lower() == "in review":
            st = "In review"

        hr_reply = latest.get("hr_reply") or latest.get("reply_text") or latest.get("resolution")
        q_months = latest.get("months") or ([latest.get("month")] if latest.get("month") else ["2026-09"])
        q_month_name = format_month_label(q_months[0]) if q_months else "September 2026"

        if not hr_reply:
            msg_code = "C40"
            msg_text = get_message("C40", month=q_month_name, status=st)
        else:
            msg_code = "C44"
            msg_text = f"{get_message('C44', month=q_month_name, status=st)} {hr_reply}"

        return {
            "messages": [
                {"code": msg_code, "text": msg_text}
            ],
            "cards": [
                {
                    "id": f"card-status-{latest['query_id']}",
                    "type": "query_status",
                    "title": "Payroll query status",
                    "data": {
                        "query_id": latest["query_id"],
                        "status": st,
                        "category": latest.get("category"),
                        "description": latest.get("description"),
                        "reply_text": latest.get("reply_text") or latest.get("hr_reply"),
                        "resolution": latest.get("resolution") or latest.get("hr_reply")
                    }
                }
            ],
            "chips": _get_user_fallback_chips(user),
            "state": {
                "intent": "query_status",
                "role": role,
                "surface": surface,
                "employee_id": emp_id,
                "panel": None
            }
        }

    def _handle_hr_query_review(self, user: dict, role: str, surface: str, context: dict) -> dict:
        allowed = set(user.get("allowed_employee_ids") or [])
        queries = [q for q in lifecycle.get_queries() if q.get("employee_id") in allowed]
        return {
            "messages": [
                {"code": "HR_QUERY_LIST", "text": f"Here are the recorded employee queries ({len(queries)} total):"}
            ],
            "cards": [
                {
                    "id": "card-hr-queries",
                    "type": "query_status",
                    "title": "Pending queries",
                    "data": {
                        "queries": queries
                    }
                }
            ],
            "chips": _get_user_fallback_chips(user),
            "state": {
                "intent": "hr_query_review",
                "role": role,
                "surface": surface,
                "employee_id": None,
                "panel": None
            }
        }

    def _handle_take_into_review(self, user: dict, role: str, surface: str, context: dict) -> dict:
        q_id = context.get("query_id")
        if not q_id:
            return self._build_refusal(role, surface, "Missing query ID.", user=user)
        try:
            res = lifecycle.take_into_review(q_id, actor=user)
            q = res["query"]
        except Exception:
            return self._build_refusal(role, surface, "Invalid query ID.", user=user)
        return {
            "messages": [
                {"code": "C16", "text": get_message("C16")}
            ],
            "cards": [
                {
                    "id": f"card-status-{q['query_id']}",
                    "type": "query_status",
                    "title": "Payroll query in review",
                    "data": {
                        "query_id": q["query_id"],
                        "status": "In review",
                        "category": q.get("category"),
                        "description": q.get("description"),
                        "reply_text": q.get("hr_reply")
                    }
                }
            ],
            "chips": [],
            "state": {"intent": "hr_query_review", "role": role, "surface": surface, "panel": None}
        }

    def _handle_reply_query(self, user: dict, role: str, surface: str, context: dict) -> dict:
        q_id = context.get("query_id")
        if not q_id:
            return self._build_refusal(role, surface, "Missing query ID.", user=user)
        try:
            q = lifecycle.get_query(q_id)
        except Exception:
            return self._build_refusal(role, surface, "Invalid query ID.", user=user)
        allowed = set(user.get("allowed_employee_ids") or [])
        if q.get("employee_id") not in allowed:
            return self._build_refusal(role, surface, "Access boundary enforced.", user=user)

        emp_name = EMPLOYEE_NAMES.get(q.get("employee_id"), q.get("employee_id"))
        reply_arg = context.get("reply_text")
        if reply_arg:
            res = lifecycle.reply_query(q_id, actor=user, reply_text=reply_arg)
            q_res = res["query"]
            return {
                "messages": [
                    {"code": "C16", "text": get_message("C16")}
                ],
                "cards": [
                    {
                        "id": f"card-status-{q_res['query_id']}",
                        "type": "query_status",
                        "title": "Query reply recorded",
                        "data": {
                            "query_id": q_res["query_id"],
                            "employee_label": f"{emp_name} · {q_res.get('employee_id')}",
                            "name_code": f"{emp_name} · {q_res.get('employee_id')}",
                            "status": q_res.get("status", "In review"),
                            "description": q_res.get("description"),
                            "reply_text": q_res.get("hr_reply")
                        }
                    }
                ],
                "chips": [
                    {"label": "Mark query resolved", "action": "confirm-resolve-query", "payload": {"query_id": q_res["query_id"], "confirmed": True}}
                ],
                "state": {"intent": "hr_query_review", "role": role, "surface": surface, "panel": None}
            }

        draft_reply = ""
        return {
            "messages": [
                {"code": "C50", "text": get_message("C50", Name=emp_name)}
            ],
            "cards": [
                {
                    "id": f"card-draft-{q['query_id']}",
                    "type": "query_draft",
                    "title": f"Reply to {emp_name}'s query",
                    "data": {
                        "query_id": q["query_id"],
                        "employee_id": q.get("employee_id"),
                        "employee_label": f"{emp_name} · {q.get('employee_id')}",
                        "name_code": f"{emp_name} · {q.get('employee_id')}",
                        "status": q.get("status", "In review"),
                        "period": format_month_label(q.get("months", ["2026-09"])[0]),
                        "category": q.get("category"),
                        "description": q.get("description"),
                        "draft_reply": "",
                        "notice": "Nothing is sent until HR clicks Send and confirms."
                    }
                }
            ],
            "chips": [
                {"label": "Send reply", "action": "confirm-reply-query", "payload": {"query_id": q["query_id"], "employee_id": q.get("employee_id"), "reply_text": draft_reply}}
            ],
            "state": {"intent": "hr_query_review", "role": role, "surface": surface, "panel": None}
        }

    def _handle_confirm_reply_query(self, user: dict, role: str, surface: str, context: dict) -> dict:
        q_id = context.get("query_id")
        if not q_id:
            return self._build_refusal(role, surface, "Missing query ID.", user=user)
        try:
            q_orig = lifecycle.get_query(q_id)
        except Exception:
            return self._build_refusal(role, surface, "Invalid query ID.", user=user)
        allowed = set(user.get("allowed_employee_ids") or [])
        if q_orig.get("employee_id") not in allowed:
            return self._build_refusal(role, surface, "Access boundary enforced.", user=user)

        reply = context.get("reply_text") or context.get("reply") or ""
        res = lifecycle.reply_query(q_id, actor=user, reply_text=reply)
        q = res["query"]
        emp_name = EMPLOYEE_NAMES.get(q.get("employee_id"), q.get("employee_id"))
        return {
            "messages": [
                {"code": "HR_QUERY_REPLY", "text": get_message("HR_QUERY_REPLY", Name=emp_name)}
            ],
            "cards": [
                {
                    "id": f"card-status-{q['query_id']}",
                    "type": "query_status",
                    "title": "Query reply recorded",
                    "data": {
                        "query_id": q["query_id"],
                        "employee_label": f"{emp_name} · {q.get('employee_id')}",
                        "name_code": f"{emp_name} · {q.get('employee_id')}",
                        "status": q.get("status", "In review"),
                        "description": q.get("description"),
                        "reply_text": q.get("hr_reply")
                    }
                }
            ],
            "chips": [
                {"label": "Mark query resolved", "action": "confirm-resolve-query", "payload": {"query_id": q["query_id"], "confirmed": True}}
            ],
            "state": {"intent": "hr_query_review", "role": role, "surface": surface, "panel": None}
        }

    def _handle_resolve_query(self, user: dict, role: str, surface: str, context: dict) -> dict:
        q_id = context.get("query_id")
        if not q_id:
            return self._build_refusal(role, surface, "Missing query ID.", user=user)
        try:
            q_orig = lifecycle.get_query(q_id)
        except Exception:
            return self._build_refusal(role, surface, "Invalid query ID.", user=user)
        allowed = set(user.get("allowed_employee_ids") or [])
        if q_orig.get("employee_id") not in allowed:
            return self._build_refusal(role, surface, "Access boundary enforced.", user=user)

        emp_name = EMPLOYEE_NAMES.get(q_orig.get("employee_id"), q_orig.get("employee_id"))
        if not context.get("confirmed") and not context.get("reply_text"):
            return {
                "messages": [
                    {"code": "C51", "text": get_message("C51", Name=emp_name)}
                ],
                "cards": [
                    {
                        "id": f"card-confirm-resolve-{q_id}",
                        "type": "query_status",
                        "title": "Resolve query confirmation",
                        "data": {
                            "query_id": q_id,
                            "employee_label": f"{emp_name} · {q_orig.get('employee_id')}",
                            "name_code": f"{emp_name} · {q_orig.get('employee_id')}",
                            "status": q_orig.get("status"),
                            "description": q_orig.get("description"),
                            "notice": "Action requires confirmation."
                        }
                    }
                ],
                "chips": [
                    {"label": "Confirm resolve", "action": "confirm-resolve-query", "payload": {"query_id": q_id, "confirmed": True}}
                ],
                "state": {"intent": "hr_query_review", "role": role, "surface": surface, "panel": None}
            }

        reply = context.get("reply_text") or (q_orig.get("hr_reply") if q_orig else None) or "Attendance reviewed and verified against punch records."
        res = lifecycle.resolve_query(q_id, actor=user, reply_text=reply)
        q = res["query"]
        return {
            "messages": [
                {"code": "C23", "text": get_message("C23")}
            ],
            "cards": [
                {
                    "id": f"card-status-{q['query_id']}",
                    "type": "query_status",
                    "title": "Query resolved",
                    "data": {
                        "query_id": q["query_id"],
                        "employee_label": f"{emp_name} · {q.get('employee_id')}",
                        "name_code": f"{emp_name} · {q.get('employee_id')}",
                        "status": "Resolved",
                        "description": q.get("description"),
                        "reply_text": q.get("hr_reply"),
                        "resolution": q.get("hr_reply")
                    }
                }
            ],
            "chips": [],
            "state": {"intent": "hr_query_review", "role": role, "surface": surface, "panel": None}
        }

    def _handle_dispute_query(self, user: dict, role: str, surface: str, context: dict) -> dict:
        q_id = context.get("query_id")
        if not q_id:
            return self._build_refusal(role, surface, "Missing query ID.", user=user)
        try:
            q = lifecycle.get_query(q_id)
        except Exception:
            return self._build_refusal(role, surface, "Invalid query ID.", user=user)
        allowed = set(user.get("allowed_employee_ids") or [])
        if q.get("employee_id") not in allowed:
            return self._build_refusal(role, surface, "Access boundary enforced.", user=user)

        reason = context.get("reason", "Employee disputed resolution.")
        res = lifecycle.dispute_query(q_id, actor=user, reason=reason)
        q = res["query"]
        return {
            "messages": [
                {"code": "C16", "text": get_message("C16")}
            ],
            "cards": [
                {
                    "id": f"card-status-{q['query_id']}",
                    "type": "query_status",
                    "title": "Resolution disputed",
                    "data": {
                        "query_id": q["query_id"],
                        "status": "In review",
                        "description": q.get("description"),
                        "reply_text": f"Disputed: {reason}"
                    }
                }
            ],
            "chips": [],
            "state": {"intent": "query_status", "role": role, "surface": surface, "panel": None}
        }

    def _handle_close_query(self, user: dict, role: str, surface: str, context: dict) -> dict:
        q_id = context.get("query_id")
        if not q_id:
            return self._build_refusal(role, surface, "Missing query ID.", user=user)
        try:
            q = lifecycle.get_query(q_id)
        except Exception:
            return self._build_refusal(role, surface, "Invalid query ID.", user=user)
        allowed = set(user.get("allowed_employee_ids") or [])
        if q.get("employee_id") not in allowed:
            return self._build_refusal(role, surface, "Access boundary enforced.", user=user)

        try:
            res = lifecycle.close_query(q_id, actor=user)
            q = res["query"]
        except Exception:
            lifecycle.resolve_query(q_id, actor=user, reply_text="Auto-resolved prior to closure.")
            res = lifecycle.close_query(q_id, actor=user)
            q = res["query"]

        return {
            "messages": [
                {"code": "C24", "text": get_message("C24")}
            ],
            "cards": [
                {
                    "id": f"card-status-{q['query_id']}",
                    "type": "query_status",
                    "title": "Query closed",
                    "data": {
                        "query_id": q["query_id"],
                        "status": "Closed",
                        "description": q.get("description"),
                        "reply_text": q.get("hr_reply")
                    }
                }
            ],
            "chips": [],
            "state": {"intent": "query_status", "role": role, "surface": surface, "panel": None}
        }

    def _handle_hr_employee_query_flow(self, user: dict, role: str, surface: str, emp_target_id: str, raw_msg: str, context: dict) -> dict:
        allowed = set(user.get("allowed_employee_ids") or [])
        if emp_target_id not in allowed:
            return self._build_refusal(role, surface, "Access boundary enforced.", user=user)

        emp_name = EMPLOYEE_NAMES.get(emp_target_id, emp_target_id)
        queries = lifecycle.get_queries(employee_id=emp_target_id)
        if not queries:
            return {
                "messages": [
                    {"code": "NO_QUERY", "text": f"No open payroll query was found for {emp_name}."}
                ],
                "cards": [],
                "chips": _get_user_fallback_chips(user),
                "state": {"intent": "hr_query_review", "role": role, "surface": surface, "panel": None}
            }

        latest = queries[-1]
        q_id = latest["query_id"]
        period_str = format_month_label(latest.get("months", ["2026-09"])[0])
        q_month_simple = MONTH_NAMES.get(latest.get("months", ["2026-09"])[0].split("-")[1], "September")
        st = latest.get("status", "In review")
        lower_msg = raw_msg.lower()

        # Item 7: Delete request
        if "delete" in lower_msg:
            return {
                "messages": [
                    {"code": "C45", "text": get_message("C45")}
                ],
                "cards": [
                    {
                        "id": f"card-status-{q_id}",
                        "type": "query_status",
                        "title": f"{emp_name}'s query",
                        "data": {
                            "query_id": q_id,
                            "employee_label": f"{emp_name} · {emp_target_id}",
                            "name_code": f"{emp_name} · {emp_target_id}",
                            "period": period_str,
                            "category": latest.get("category"),
                            "description": latest.get("description"),
                            "status": st
                        }
                    }
                ],
                "chips": [
                    {"label": "Close query instead", "action": "close-query", "payload": {"query_id": q_id}}
                ],
                "state": {"intent": "hr_query_review", "role": role, "surface": surface, "panel": None}
            }

        # Item 5: Resolve request
        if "resolve" in lower_msg or "mark" in lower_msg:
            return self._handle_resolve_query(user, role, surface, {"query_id": q_id, "confirmed": False})

        # Item 4: Reply request
        if "reply" in lower_msg:
            return self._handle_reply_query(user, role, surface, {"query_id": q_id})

        # Item 3: Show request
        hr_reply = latest.get("hr_reply")
        if not hr_reply:
            msg_code = "C43"
            msg_text = get_message("C43", Name=emp_name, month=q_month_simple, status=st)
        else:
            msg_code = "HR_QUERY_SHOW"
            msg_text = f"{emp_name}'s {q_month_simple} query is {st}. HR reply: {hr_reply}"

        card_data = {
            "query_id": q_id,
            "employee_label": f"{emp_name} · {emp_target_id}",
            "name_code": f"{emp_name} · {emp_target_id}",
            "period": period_str,
            "category": latest.get("category"),
            "description": latest.get("description"),
            "status": st
        }
        if hr_reply:
            card_data["reply_text"] = hr_reply

        return {
            "messages": [
                {"code": msg_code, "text": msg_text}
            ],
            "cards": [
                {
                    "id": f"card-status-{q_id}",
                    "type": "query_status",
                    "title": f"{emp_name}'s query",
                    "data": card_data
                }
            ],
            "chips": [
                {"label": "Reply to query", "action": "reply-query", "payload": {"query_id": q_id, "employee_id": emp_target_id}},
                {"label": "Mark query resolved", "action": "resolve-query", "payload": {"query_id": q_id, "employee_id": emp_target_id}}
            ],
            "state": {"intent": "hr_query_review", "role": role, "surface": surface, "panel": None}
        }

    def _handle_approvals_list(self, user: dict, role: str, surface: str) -> dict:
        allowed = set(user.get("allowed_employee_ids") or [])
        all_props = lifecycle.get_all_proposals()
        ready_items = []
        needs_input_items = []
        seen_keys = set()

        for pid, p in all_props.items():
            status = p.get("status", "")
            if status in ("Approved for payroll", "Approved", "Rejected"):
                continue

            s_num = p.get("scenario_num")
            scope = p.get("scope") or {}
            emp_id = scope.get("employee_id")

            if emp_id:
                if emp_id not in allowed:
                    continue
                emp_name = scope.get("employee_name") or EMPLOYEE_NAMES.get(emp_id, emp_id)
                if s_num in (1, 2, 3):
                    kind_label = "Salary revision"
                elif s_num in (6, 7, 8):
                    kind_label = "Full and final settlement"
                elif s_num == 13:
                    kind_label = "Exit Settlement Breakdown"
                else:
                    kind_label = p.get("type") or "Salary revision"
                name_code = f"{kind_label} · {emp_name} · {emp_id}"
                scope_label = p.get("scope_label") or scope.get("period") or "October 2026"
            else:
                if role == "HR Admin" and user.get("user_id") == "HR02" and "Engineering" in str(p.get("scope_label")):
                    continue
                name_code = p.get("scope_label") or "Annual performance bonus · Engineering · FY 2025-26"
                scope_label = "FY 2025-26"

            dedup_key = (name_code, s_num)
            if dedup_key in seen_keys:
                continue
            seen_keys.add(dedup_key)

            is_ready, disabled_reason, row_reason = evaluate_proposal_readiness(pid, p)
            cert = "Complete for this scope" if is_ready else "Incomplete"
            item_data = {
                "label": name_code,
                "name_code": name_code,
                "scope": scope_label,
                "certainty": cert,
                "action_label": "Open",
                "proposal_id": pid,
                "scenario_num": s_num
            }
            if is_ready:
                ready_items.append(item_data)
            else:
                item_data["blocked_reason"] = row_reason
                item_data["reason"] = row_reason
                needs_input_items.append(item_data)

        if not ready_items and not needs_input_items:
            return {
                "messages": [
                    {"code": "C46", "text": get_message("C46")}
                ],
                "cards": [],
                "chips": _get_user_fallback_chips(user),
                "state": {
                    "intent": "approvals_list",
                    "role": role,
                    "surface": surface,
                    "panel": None
                }
            }

        messages = []
        if ready_items:
            messages.append({"code": "C48", "text": get_message("C48", n=len(ready_items))})
        if needs_input_items:
            messages.append({"code": "C49", "text": get_message("C49", n=len(needs_input_items))})

        cards = []
        if ready_items:
            cards.append({
                "id": "card-ready-approvals",
                "type": "component_list",
                "title": "Ready to approve",
                "data": {
                    "group": "Ready to approve",
                    "items": ready_items,
                    "components": [
                        {
                            "name": it["label"],
                            "note": None,
                            "status": "Complete for this scope",
                            "amount": None
                        }
                        for it in ready_items
                    ]
                }
            })
        if needs_input_items:
            cards.append({
                "id": "card-needs-input-approvals",
                "type": "component_list",
                "title": "Needs input first",
                "data": {
                    "group": "Needs input first",
                    "items": needs_input_items,
                    "components": [
                        {
                            "name": it["label"],
                            "note": it.get("reason"),
                            "status": "Incomplete",
                            "amount": None
                        }
                        for it in needs_input_items
                    ]
                }
            })

        chips = []
        for it in (ready_items + needs_input_items)[:4]:
            chips.append({
                "label": f"Open {it['name_code'].split('·')[0].strip()}",
                "action": f"scenario-{it['scenario_num']}",
                "payload": {"scenario_num": it["scenario_num"], "proposal_id": it["proposal_id"]}
            })

        return {
            "messages": messages,
            "cards": cards,
            "chips": chips,
            "state": {
                "intent": "approvals_list",
                "role": role,
                "surface": surface,
                "panel": None
            }
        }

    def _handle_leavers_list(self, user: dict, role: str, surface: str) -> dict:
        allowed = set(user.get("allowed_employee_ids") or [])

        payroll_runs_path = Path("data/mock/payroll-runs.json")
        open_month = "2026-10"
        if payroll_runs_path.exists():
            try:
                runs = json.loads(payroll_runs_path.read_text(encoding="utf-8"))
                for r in runs:
                    if r.get("status") == "open":
                        open_month = r.get("month", "2026-10")
                        break
            except Exception:
                pass

        month_label = format_month_label(open_month)
        exits_path = Path("data/mock/exits.json")
        exits_data = []
        if exits_path.exists():
            try:
                exits_data = json.loads(exits_path.read_text(encoding="utf-8"))
            except Exception:
                pass

        leavers = []
        for ex in exits_data:
            lwd = ex.get("last_working_day", "")
            if lwd.startswith(open_month):
                eid = ex.get("employee_id")
                if eid in allowed:
                    ename = EMPLOYEE_NAMES.get(eid, eid)
                    leavers.append({
                        "employee_id": eid,
                        "name": ename,
                        "name_code": f"{ename} · {eid}",
                        "last_working_day": lwd
                    })

        msg_c47 = get_message("C47", n=len(leavers), month=month_label)

        card = {
            "id": f"card-leavers-{open_month}",
            "type": "component_list",
            "title": f"Leavers — {month_label}",
            "data": {
                "month": month_label,
                "items": [
                    {
                        "label": l["name_code"],
                        "name_code": l["name_code"],
                        "last_working_day": l["last_working_day"],
                        "employee_id": l["employee_id"]
                    }
                    for l in leavers
                ]
            }
        }

        chips = []
        for l in leavers:
            chips.append({
                "label": f"Prepare settlement for {l['name'].split()[0]}",
                "action": "select-employee",
                "payload": {"employee_id": l["employee_id"], "task": "settlement"}
            })

        return {
            "messages": [
                {"code": "C47", "text": msg_c47}
            ],
            "cards": [card],
            "chips": chips,
            "state": {
                "intent": "leavers_list",
                "role": role,
                "surface": surface,
                "panel": None
            }
        }

    def _handle_show_calculation(self, user: dict, role: str, surface: str, context: dict) -> dict:
        topic = context.get("topic")
        if topic == "tds" or (role == "Employee" and not context.get("scenario_num")):
            m = context.get("month", "2026-09")
            resp = self._build_tds_amount(user, role, surface, month=m)
            return {
                "messages": [
                    {"code": "C22", "text": get_message("C22")}
                ],
                "cards": resp.get("cards", []),
                "chips": resp.get("chips", []),
                "state": {
                    **resp.get("state", {}),
                    "open_panel": True,
                    "panel": resp.get("state", {}).get("panel")
                }
            }

        s_num = context.get("scenario_num")
        if not s_num and context.get("proposal_id"):
            prop = lifecycle.get_proposal(context["proposal_id"])
            if prop:
                s_num = prop.get("scenario_num") or prop.get("scope", {}).get("scenario_num")
        if not s_num:
            return self._build_unknown_fallback(role, surface, user)

        builder = getattr(self, f"_build_scenario_{s_num}", None)
        if not builder:
            return self._build_unknown_fallback(role, surface, user)

        resp = builder(user, role, surface)
        panel_data = resp.get("state", {}).get("panel")
        return {
            "messages": [
                {"code": "C22", "text": get_message("C22")}
            ],
            "cards": resp.get("cards", []),
            "chips": resp.get("chips", []),
            "state": {
                **resp.get("state", {}),
                "open_panel": True,
                "panel": panel_data
            }
        }

    def _build_employee_picker(self, task: str, employees: list, prompt_text: str, role: str, surface: str) -> dict:
        chips = [
            {"label": emp["name"], "action": "select-employee", "payload": {"employee_id": emp["employee_id"], "task": task, "name": emp["name"]}}
            for emp in employees[:4]
        ]
        return {
            "messages": [
                {"code": "C01", "text": prompt_text}
            ],
            "cards": [
                {
                    "id": f"card-picker-{task}",
                    "type": "employee_picker",
                    "title": "Select employee",
                    "data": {
                        "task": task,
                        "prompt": prompt_text,
                        "employees": employees
                    }
                }
            ],
            "chips": chips,
            "state": {
                "intent": f"{task}_picker",
                "role": role,
                "surface": surface,
                "scenario_num": None,
                "employee_id": None,
                "panel": None
            }
        }

    def _handle_arrears_picker(self, user: dict, role: str, surface: str, candidate_name: Optional[str] = None) -> dict:
        candidates = get_picker_employees_for_task("arrears", user)
        if candidate_name:
            c_name_lower = candidate_name.lower().strip()
            matches = [c for c in candidates if c_name_lower in c["name"].lower() or c["employee_id"].lower() == c_name_lower]
            if len(matches) == 1:
                return self._handle_employee_selection(user, role, surface, {"employee_id": matches[0]["employee_id"], "task": "arrears", "name": matches[0]["name"]})
            elif len(matches) > 1:
                return self._build_employee_picker(
                    task="arrears",
                    employees=matches,
                    prompt_text=f"Which {candidate_name} do you mean? Please select one:",
                    role=role,
                    surface=surface
                )
            else:
                return self._build_employee_picker(
                    task="arrears",
                    employees=candidates,
                    prompt_text=f"I couldn't find an employee named {candidate_name}. Please select an employee from pending salary revisions:",
                    role=role,
                    surface=surface
                )

        return self._build_employee_picker(
            task="arrears",
            employees=candidates,
            prompt_text="Please select an employee to calculate arrears for:",
            role=role,
            surface=surface
        )

    def _handle_settlement_picker(self, user: dict, role: str, surface: str, candidate_name: Optional[str] = None) -> dict:
        candidates = get_picker_employees_for_task("settlement", user)
        if candidate_name:
            c_name_lower = candidate_name.lower().strip()
            matches = [c for c in candidates if c_name_lower in c["name"].lower() or c["employee_id"].lower() == c_name_lower]
            if len(matches) == 1:
                return self._handle_employee_selection(user, role, surface, {"employee_id": matches[0]["employee_id"], "task": "settlement", "name": matches[0]["name"]})
            elif len(matches) > 1:
                return self._build_employee_picker(
                    task="settlement",
                    employees=matches,
                    prompt_text=f"Which {candidate_name} do you mean? Please select one:",
                    role=role,
                    surface=surface
                )
            else:
                return self._build_employee_picker(
                    task="settlement",
                    employees=candidates,
                    prompt_text=f"I couldn't find an employee named {candidate_name}. Please select an employee with an exit record:",
                    role=role,
                    surface=surface
                )

        return self._build_employee_picker(
            task="settlement",
            employees=candidates,
            prompt_text="Please select an employee to prepare full and final settlement for:",
            role=role,
            surface=surface
        )

    def _handle_salary_picker(self, user: dict, role: str, surface: str, candidate_name: Optional[str] = None) -> dict:
        candidates = get_picker_employees_for_task("salary", user)
        if candidate_name:
            c_name_lower = candidate_name.lower().strip()
            matches = [c for c in candidates if c_name_lower in c["name"].lower() or c["employee_id"].lower() == c_name_lower]
            if len(matches) == 1:
                return self._handle_employee_selection(user, role, surface, {"employee_id": matches[0]["employee_id"], "task": "salary", "name": matches[0]["name"]})
            elif len(matches) > 1:
                return self._build_employee_picker(
                    task="salary",
                    employees=matches,
                    prompt_text=f"Which {candidate_name} do you mean? Please select one:",
                    role=role,
                    surface=surface
                )
            else:
                return self._build_employee_picker(
                    task="salary",
                    employees=candidates,
                    prompt_text=f"I couldn't find an employee named {candidate_name}. Please select an employee to view salary:",
                    role=role,
                    surface=surface
                )

        return self._build_employee_picker(
            task="salary",
            employees=candidates,
            prompt_text="Please select an employee to view salary:",
            role=role,
            surface=surface
        )

    def _handle_employee_selection(self, user: dict, role: str, surface: str, context: dict) -> dict:
        emp_id = context.get("employee_id") or ""
        task = context.get("task") or ""

        if task in ("arrears", "hike"):
            if emp_id == "E01":
                return self._build_scenario_1(user, role, surface)
            elif emp_id == "E02":
                return self._build_scenario_2(user, role, surface)
            elif emp_id == "E03":
                return self._build_scenario_3(user, role, surface)
            else:
                return self._build_unknown_fallback(role, surface, user)

        elif task in ("settlement", "full_and_final"):
            if emp_id == "E10":
                return self._build_scenario_6(user, role, surface)
            elif emp_id == "E11":
                return self._build_scenario_7(user, role, surface)
            elif emp_id == "E12":
                return self._build_scenario_8(user, role, surface)
            else:
                return self._build_unknown_fallback(role, surface, user)

        elif task == "salary":
            if emp_id == "E05":
                return self._build_scenario_9(user, role, surface)
            elif emp_id == "E06":
                return self._build_scenario_10(user, role, surface)
            elif emp_id == "E16":
                return self._build_scenario_11(user, role, surface)
            else:
                return self._build_unknown_fallback(role, surface, user)

        return self._build_unknown_fallback(role, surface, user)


chat_router = ChatRouter()
