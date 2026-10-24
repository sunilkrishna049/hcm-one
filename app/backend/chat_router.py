"""Deterministic intent router and response generator for POST /api/chat.
Follows app/backend/chat_contract.md and output/07-prototype/screen-specs.md.
Zero dynamic LLM calls. All payroll figures come from engine_bridge (data/generated/scenarios/).
"""
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Any, Dict, List, Optional
from fastapi import HTTPException

from .ai_messages import get_message
from .auth import USERS, check_employee_access
from .engine_bridge import bridge
from .faq_matcher import faq_matcher
from .lifecycle import lifecycle

RULES_DIR = Path(__file__).resolve().parents[2] / "data" / "rules"
_RULES_CACHE: Dict[str, dict] = {}


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


class ChatRouter:
    def handle_chat(self, user_id: str, message: str = "", action: Optional[str] = None, context: Optional[dict] = None) -> dict:
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
                return self._build_refusal(role, surface, "Prompt injection prevented.")

        # 2. Cross-employee Data Access Guardrail (Scenario 12 / GR-2.1 - GR-2.6)
        if context.get("scenario_num") == 12:
            return self._build_scenario_12(user, role, surface)

        allowed = set(user.get("allowed_employee_ids") or [])
        other_employee_mentions = [
            ("priya", "E01"),
            ("sharma", "E01"),
            ("arjun", "E02"),
            ("rao", "E02"),
            ("kavya", "E03"),
            ("iyer", "E03"),
            ("rahul", "E10"),
            ("verma", "E10"),
            ("lakshmi", "E11"),
            ("reddy", "E11"),
            ("imran", "E12"),
            ("khan", "E12")
        ]
        for name, emp_id in other_employee_mentions:
            if (name in lower_msg or emp_id.lower() in lower_msg) and emp_id not in allowed:
                return self._build_scenario_12(user, role, surface)

        if role == "Employee":
            # Generic "other people's salary" inquiry
            if "other people" in lower_msg or "another person" in lower_msg or "colleague" in lower_msg:
                return self._build_scenario_12(user, role, surface)

        # 3. Out-of-Scope Requests (Personal Tax advice, Bank account verification)
        if re.search(r"\b(which|recommend)\b.*\btax regime\b|\btax investment\b|\bshould i choose (new|old)\b", lower_msg):
            return {
                "messages": [
                    {"code": "C11", "text": get_message("C11")}
                ],
                "cards": [],
                "chips": [
                    {"label": "Show my TDS change", "action": "explain-tds", "payload": {}},
                    {"label": "What is TDS?", "action": "faq-tds", "payload": {}}
                ],
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
            return {
                "messages": [
                    {"code": "C21", "text": get_message("C21")},
                    {"code": "C28", "text": get_message("C28")}
                ],
                "cards": [],
                "chips": [
                    {"label": "Draft a query for HR", "action": "draft-query", "payload": {}},
                    {"label": "Show my latest payslip change", "action": "explain-salary", "payload": {}}
                ],
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
            if act in ("scenario-1", "scenario-01"):
                return self._build_scenario_1(user, role, surface)
            elif act in ("scenario-2", "scenario-02"):
                return self._build_scenario_2(user, role, surface)
            elif act in ("scenario-3", "scenario-03"):
                return self._build_scenario_3(user, role, surface)
            elif act in ("scenario-4", "scenario-04"):
                return self._build_scenario_4(user, role, surface)
            elif act in ("scenario-5", "scenario-05"):
                return self._build_scenario_5(user, role, surface)
            elif act in ("scenario-6", "scenario-06"):
                return self._build_scenario_6(user, role, surface)
            elif act in ("scenario-7", "scenario-07"):
                return self._build_scenario_7(user, role, surface)
            elif act in ("scenario-8", "scenario-08"):
                return self._build_scenario_8(user, role, surface)
            elif act in ("scenario-9", "scenario-09", "explain-salary"):
                return self._build_scenario_9(user, role, surface)
            elif act in ("scenario-10", "scenario-10", "explain-tds"):
                return self._build_scenario_10(user, role, surface)
            elif act in ("scenario-11", "scenario-11"):
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
            elif act in ("confirm-send-query", "send-query", "confirm and send", "send this query to hr", "send query with listed evidence"):
                return self._handle_confirm_send_query(user, role, surface, context)
            elif act in ("append-query", "add to open query", "add to existing query"):
                return self._handle_append_query(user, role, surface, context)
            elif act in ("query-status", "check my query status"):
                return self._handle_query_status(user, role, surface, context)
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
            elif act in ("show-calculation", "show calculation", "show calculation proof", "view full month breakdown"):
                return self._handle_show_calculation(user, role, surface, context)
            elif act.startswith("faq-"):
                faq_topic = act.replace("faq-", "")
                return self._handle_faq_query(faq_topic, role, surface)

        # 5. Natural Language Intent Mapping

        # Direct Natural Language Action Matchers
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
        if re.search(r"\b(show calculation|view full month breakdown)\b", lower_msg):
            return self._handle_show_calculation(user, role, surface, context)

        # FAQ lookup priority for general questions
        if re.search(r"^(what is|what are|explain|who is|can hcm one|does approving|why is my bank|what does|how does)\b", lower_msg) or "faq" in lower_msg or len(lower_msg.split()) <= 4:
            matched_faq, conf = faq_matcher.match(raw_msg)
            if matched_faq and conf >= 0.35:
                return self._build_faq_response(matched_faq, conf, role, surface)

        # Scenario 1 (Priya Sharma hike)
        if "priya" in lower_msg or "sharma" in lower_msg or ("hike" in lower_msg and "lop" in lower_msg):
            if role != "HR Admin":
                return self._build_refusal(role, surface, "Access denied")
            return self._build_scenario_1(user, role, surface)

        # Scenario 2 (Arjun Rao PF ceiling hike)
        if "arjun" in lower_msg or "rao" in lower_msg or ("hike" in lower_msg and "ceiling" in lower_msg):
            if role != "HR Admin":
                return self._build_refusal(role, surface, "Access denied")
            return self._build_scenario_2(user, role, surface)

        # Scenario 3 (Kavya Iyer missing attendance)
        if "kavya" in lower_msg or "iyer" in lower_msg or ("hike" in lower_msg and "attendance" in lower_msg):
            if role != "HR Admin":
                return self._build_refusal(role, surface, "Access denied")
            return self._build_scenario_3(user, role, surface)

        # Scenario 4 (Team bonus)
        if "bonus" in lower_msg and ("team" in lower_msg or "annual" in lower_msg or "sales" in lower_msg or "calculate" in lower_msg or "run" in lower_msg or "proposal" in lower_msg):
            if role != "HR Admin":
                return self._build_refusal(role, surface, "Access denied")
            return self._build_scenario_4(user, role, surface)

        # Scenario 5 (Meera Nair missing rating)
        if "meera" in lower_msg or "nair" in lower_msg or ("bonus" in lower_msg and "rating" in lower_msg):
            if role != "HR Admin":
                return self._build_refusal(role, surface, "Access denied")
            return self._build_scenario_5(user, role, surface)

        # Scenario 6 (Rahul Verma settlement)
        if "rahul" in lower_msg or "verma" in lower_msg or ("settlement" in lower_msg and "gratuity" in lower_msg):
            if role != "HR Admin":
                return self._build_refusal(role, surface, "Access denied")
            return self._build_scenario_6(user, role, surface)

        # Scenario 7 (Lakshmi Reddy settlement)
        if "lakshmi" in lower_msg or "reddy" in lower_msg or ("settlement" in lower_msg and "minimum service" in lower_msg):
            if role != "HR Admin":
                return self._build_refusal(role, surface, "Access denied")
            return self._build_scenario_7(user, role, surface)

        # Scenario 8 (Imran Khan exit recovery)
        if ("imran" in lower_msg or "khan" in lower_msg) and ("recovery" in lower_msg or "prepare" in lower_msg or "exit recovery" in lower_msg) and "calculation" not in lower_msg and "unresolved" not in lower_msg:
            if role != "HR Admin":
                return self._build_refusal(role, surface, "Access denied")
            return self._build_scenario_8(user, role, surface)

        # Scenario 13 (Imran Khan settlement review / breakdown / calculation)
        if ("imran" in lower_msg or "khan" in lower_msg) and ("review" in lower_msg or "calculation" in lower_msg or "breakdown" in lower_msg or "unresolved" in lower_msg or "settlement" in lower_msg):
            if role != "HR Admin":
                return self._build_refusal(role, surface, "Access denied")
            return self._build_scenario_13(user, role, surface)

        # Scenario 11 (Pooja Das / gross did not change / basic pay / allowance)
        if "pooja" in lower_msg or "e16" in lower_msg or "basic pay" in lower_msg or "allowance" in lower_msg or "gross did not change" in lower_msg or "no earning" in lower_msg or ("decrease" in lower_msg and "gross" in lower_msg):
            return self._build_scenario_11(user, role, surface)

        # Scenario 10 (Siddharth Jain / TDS increase)
        if "siddharth" in lower_msg or "e06" in lower_msg or ("tds" in lower_msg and ("increase" in lower_msg or "higher" in lower_msg or "deduction" in lower_msg or "tax" in lower_msg or "why" in lower_msg or "change" in lower_msg)):
            return self._build_scenario_10(user, role, surface)

        # Scenario 9 (Neha Gupta / September salary drop)
        if "neha" in lower_msg or "e05" in lower_msg or (("take-home" in lower_msg or "salary" in lower_msg or "payslip" in lower_msg) and ("lower" in lower_msg or "drop" in lower_msg or "change" in lower_msg or "september" in lower_msg)):
            return self._build_scenario_9(user, role, surface)

        # Query Flows
        if "draft" in lower_msg and "query" in lower_msg:
            return self._handle_draft_query(user, role, surface, context)
        if ("status" in lower_msg or "track" in lower_msg) and ("query" in lower_msg or "queries" in lower_msg):
            return self._handle_query_status(user, role, surface, context)
        if "review" in lower_msg and ("query" in lower_msg or "queries" in lower_msg):
            return self._handle_hr_query_review(user, role, surface, context)

        # Fallback to FAQ keyword match
        matched_faq, conf = faq_matcher.match(raw_msg)
        if matched_faq and conf >= 0.35:
            return self._build_faq_response(matched_faq, conf, role, surface)

        # 6. Fallback Response (Never hallucinate)
        return self._build_unknown_fallback(role, surface)

    # --- Scenario Builders ---

    def _build_scenario_1(self, user: dict, role: str, surface: str) -> dict:
        sc = bridge.get_scenario(1)
        r = sc["result"]
        t = r["totals"]
        disp = sc.get("display_inputs", {})
        old_sal = disp.get("old_monthly_salary", {}).get("total", {}).get("value", 120000)
        prop_sal = disp.get("proposed_monthly_salary", {}).get("total", {}).get("value", 132000)
        hike_pct = disp.get("requested_hike_percentage", {}).get("value", 10)
        eff_date = disp.get("effective_date", {}).get("value", "2026-04-01")

        pf_rules = get_rule_file("pf-rules.json")
        tax_rules = get_rule_file("tax-rules.json")
        old_ceiling = pf_rules.get("wage_ceiling_before_change_inr", {}).get("value", 15000)
        old_eff_to = pf_rules.get("wage_ceiling_before_change_inr", {}).get("effective_to", "2026-09-16")
        new_ceiling = pf_rules.get("wage_ceiling_from_change_inr", {}).get("value", 25000)
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

        return {
            "messages": [
                {"code": "C03", "text": get_message("C03")}
            ],
            "cards": [
                {
                    "id": "card-prop-s1",
                    "type": "proposal_summary",
                    "title": "Proposal Summary",
                    "certainty": r.get("certainty", "Complete for this scope"),
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
                    "title": "Arrears & Tax Breakdown",
                    "certainty": r.get("certainty", "Complete for this scope"),
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
                    "title": "Affected Months Summary",
                    "certainty": r.get("certainty", "Complete for this scope"),
                    "data": {
                        "months": [
                            {
                                "month": m["month"],
                                "old_gross": m["old"]["gross"]["value"],
                                "revised_gross": m["revised"]["gross"]["value"],
                                "diff": m["difference"]["value"],
                                "tds_impact": m["tds_impact"]["value"],
                                "paid_days": m["paid_days"]["value"],
                                "lop_days": disp.get("months", {}).get(m["month"], {}).get("lop_days", {}).get("value", 0)
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
                    "certainty": r.get("certainty", "Complete for this scope"),
                    "data": {
                        "scope_label": "Priya Sharma · Apr–Sep 2026",
                        "notice": get_message("C04"),
                        "actions": ["Approve proposal for payroll", "Edit with reason", "Reject proposal"],
                        "status": "pending",
                        "proposal_id": "PROP-SCENARIO-1"
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
                "panel": {
                    "title": "Calculation Proof & Month Breakdown",
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
                            "lop_days": disp.get("months", {}).get(m["month"], {}).get("lop_days", {}).get("value", 0),
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
                        f"Standard deduction: {format_inr(tax_rules.get('standard_deduction_inr', {}).get('value', 75000))}",
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
        old_sal = disp.get("old_monthly_salary", {}).get("total", {}).get("value", 36000)
        prop_sal = disp.get("proposed_monthly_salary", {}).get("total", {}).get("value", 39600)
        hike_pct = disp.get("requested_hike_percentage", {}).get("value", 10)
        eff_date = disp.get("effective_date", {}).get("value", "2026-08-01")
        return {
            "messages": [
                {"code": "C03", "text": get_message("C03")}
            ],
            "cards": [
                {
                    "id": "card-prop-s2",
                    "type": "proposal_summary",
                    "title": "Proposal Summary",
                    "certainty": r.get("certainty", "Complete for this scope"),
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
                    "title": "Arrears & PF Impact",
                    "certainty": r.get("certainty", "Complete for this scope"),
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
                    "title": "HR Authorization",
                    "certainty": r.get("certainty", "Complete for this scope"),
                    "data": {
                        "scope_label": "Arjun Rao (E02) • September 2026",
                        "notice": get_message("C04"),
                        "actions": ["Approve proposal for payroll", "Edit with reason", "Reject proposal"],
                        "status": "pending",
                        "proposal_id": "PROP-SCENARIO-2"
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
                "panel": {
                    "title": "September 2026 PF Dual-Segment Proof",
                    "employee_name": "Arjun Rao",
                    "employee_id": "E02",
                    "formulas": [
                        f"Segment 1 (1–16 Sep): Wage ceiling ₹{get_rule_file('pf-rules.json').get('wage_ceiling_before_change_inr', {}).get('value', 15000):,} (16 of 30 calendar days)",
                        f"Segment 2 (17–30 Sep): Wage ceiling ₹{get_rule_file('pf-rules.json').get('wage_ceiling_from_change_inr', {}).get('value', 25000):,} (14 of 30 calendar days)",
                        f"Total PF change across dual segments = {format_inr(t['pf_change']['employee']['value'])}"
                    ],
                    "rule_citations": [
                        f"PF wage ceiling: ₹{get_rule_file('pf-rules.json').get('wage_ceiling_before_change_inr', {}).get('value', 15000):,} until 16 Sep 2026; ₹{get_rule_file('pf-rules.json').get('wage_ceiling_from_change_inr', {}).get('value', 25000):,} from 17 Sep 2026",
                        f"Employee PF contribution rate: {get_rule_file('pf-rules.json').get('employee_contribution_rate_percent', {}).get('value', 12)}% of PF wage",
                        "Mid-month ceiling change: Pro-rated across dated calendar segments",
                        f"Rules version: {get_rule_file('pf-rules.json').get('rules_version', 'Northwind demo rules v1')}"
                    ]
                }
            }
        }

    def _build_scenario_3(self, user: dict, role: str, surface: str) -> dict:
        sc = bridge.get_scenario(3)
        r = sc["result"]
        aug_diff = next((m.get("difference", {}).get("value") for m in r.get("months", []) if m.get("month") == "2026-08"), 4800)
        sep_diff = next((m.get("difference", {}).get("value") for m in r.get("months", []) if m.get("month") == "2026-09"), 4800)
        return {
            "messages": [
                {"code": "C07", "text": "The required attendance record for 2026-07 is missing. I cannot explain a complete result for this scope."}
            ],
            "cards": [
                {
                    "id": "card-prop-s3",
                    "type": "proposal_summary",
                    "title": "Incomplete Proposal Summary",
                    "certainty": "Incomplete",
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
                    "title": "Known Monthly Differences",
                    "certainty": "Incomplete",
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
                    "title": "HR Authorization (Blocked)",
                    "certainty": "Incomplete",
                    "data": {
                        "scope_label": "Kavya Iyer (E03)",
                        "notice": "Cannot approve an incomplete proposal while required records are missing.",
                        "actions": [],
                        "disabled": True
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
                "panel": {
                    "title": "Missing Attendance Proof",
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

    def _build_scenario_4(self, user: dict, role: str, surface: str) -> dict:
        sc = bridge.get_scenario(4)
        r = sc["result"]
        annual = r["bonus_requests"][0]
        gross_total = annual["known_eligible_gross"]["value"]

        ann_req = next((req for req in sc["result"]["bonus_requests"] if req.get("bonus_type") == "annual_performance_bonus"), {})
        emp_map = {e["employee_id"]: e for e in ann_req.get("employees", [])}
        e01_amt = emp_map.get("E01", {}).get("amount", {}).get("value")
        e03_amt = emp_map.get("E03", {}).get("amount", {}).get("value")
        e04_amt = emp_map.get("E04", {}).get("amount", {}).get("value")
        e07_amt = emp_map.get("E07", {}).get("amount", {}).get("value")
        e08_amt = emp_map.get("E08", {}).get("amount", {}).get("value", 0)

        return {
            "messages": [
                {"code": "C03", "text": get_message("C03")}
            ],
            "cards": [
                {
                    "id": "card-bonus-s4",
                    "type": "proposal_summary",
                    "title": "Team Bonus Run Summary",
                    "certainty": r.get("certainty", "Needs HR decision"),
                    "data": {
                        "proposal_type": "Annual & Sales Bonus Run",
                        "eligible_count": 3,
                        "ineligible_count": 1,
                        "needs_input_count": 1,
                        "gross_eligible_total": gross_total,
                        "status": "Needs HR decision"
                    }
                },
                {
                    "id": "card-approval-s4",
                    "type": "approval_card",
                    "title": "HR Authorization",
                    "certainty": "Needs HR decision",
                    "data": {
                        "scope_label": "Team Bonus Run • 5 employees evaluated",
                        "notice": get_message("C04"),
                        "actions": ["Approve proposal for payroll", "Edit with reason", "Reject proposal"],
                        "status": "pending",
                        "proposal_id": "PROP-SCENARIO-4"
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
                "panel": {
                    "title": "Bonus Eligibility & Scope Roster",
                    "formulas": [
                        f"E01 (Priya Sharma): Annual bonus {format_inr(e01_amt)}",
                        f"E03 (Kavya Iyer): Annual bonus {format_inr(e03_amt)}",
                        f"E04 (Rohan Joshi): Sales bonus {format_inr(e04_amt)}",
                        f"E07 (Ananya Sen): Joiner proration {format_inr(e07_amt)}",
                        f"E08 (Vikramaditya Verma): Notice exclusion: {format_inr(e08_amt)} (Ineligible)",
                        "E09 (Meera Nair): Missing performance rating (Needs input)"
                    ],
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
        return {
            "messages": [
                {"code": "C07", "text": "The required performance record for FY 2025-26 is missing. I cannot explain a complete result for this scope."}
            ],
            "cards": [
                {
                    "id": "card-bonus-s5",
                    "type": "proposal_summary",
                    "title": "Employee Bonus Evaluation",
                    "certainty": "Incomplete",
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
                    "title": "HR Authorization (Blocked)",
                    "certainty": "Incomplete",
                    "data": {
                        "scope_label": "Meera Nair (E09)",
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
                "panel": {
                    "title": "Missing Performance Record",
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
        return {
            "messages": [
                {"code": "C03", "text": get_message("C03")}
            ],
            "cards": [
                {
                    "id": "card-settlement-s6",
                    "type": "proposal_summary",
                    "title": "Full & Final Settlement Proposal",
                    "certainty": r.get("certainty", "Complete for this scope"),
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
                    "title": "Settlement Components Ledger",
                    "certainty": r.get("certainty", "Complete for this scope"),
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
                    "title": "HR Authorization",
                    "certainty": r.get("certainty", "Complete for this scope"),
                    "data": {
                        "scope_label": "Rahul Verma (E10) • Exit Settlement",
                        "notice": get_message("C04"),
                        "actions": ["Approve proposal for payroll", "Edit with reason", "Reject proposal"],
                        "status": "pending",
                        "proposal_id": "PROP-SCENARIO-6"
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
                "panel": {
                    "title": "Settlement Proof & Component Ledger",
                    "employee_name": "Rahul Verma",
                    "employee_id": "E10",
                    "formulas": [
                        f"Final Net = Gross Payables ({format_inr(r.get('gross_payables', {}).get('value'))}) − Total Deductions ({format_inr(r.get('total_deductions', {}).get('value'))}) = {format_inr(r.get('final_net', {}).get('value'))}",
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
        grat_amt = c.get("gratuity", {}).get("amount", {}).get("value", 0)
        return {
            "messages": [
                {"code": "C03", "text": get_message("C03")}
            ],
            "cards": [
                {
                    "id": "card-settlement-s7",
                    "type": "proposal_summary",
                    "title": "Full & Final Settlement Proposal",
                    "certainty": r.get("certainty", "Complete for this scope"),
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
                    "title": "Settlement Components",
                    "certainty": r.get("certainty", "Complete for this scope"),
                    "data": {
                        "components": [
                            {"name": "Gratuity", "amount": grat_amt, "status": "Ineligible", "note": "Close to minimum service: Continuous service less than statutory 5-year requirement"}
                        ]
                    }
                },
                {
                    "id": "card-approval-s7",
                    "type": "approval_card",
                    "title": "HR Authorization",
                    "certainty": r.get("certainty", "Complete for this scope"),
                    "data": {
                        "scope_label": "Lakshmi Reddy (E11)",
                        "notice": get_message("C04"),
                        "actions": ["Approve proposal for payroll", "Edit with reason", "Reject proposal"],
                        "status": "pending",
                        "proposal_id": "PROP-SCENARIO-7"
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
                "panel": {
                    "title": "Gratuity Service Eligibility Proof",
                    "formulas": [
                        "Tenure: Continuous service is less than statutory 5-year threshold",
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
        notice_amt = c.get("notice_shortfall_recovery", {}).get("amount", {}).get("value", 46667)
        recov_subtotal = r.get("known_recoveries_subtotal", {}).get("value", notice_amt)
        return {
            "messages": [
                {"code": "C07", "text": "The required asset clearance record for exit clearance is missing. I cannot explain a complete result for this scope."},
                {"code": "C19", "text": "The final net is incomplete because unreturned company laptop is not yet known."}
            ],
            "cards": [
                {
                    "id": "card-settlement-s8",
                    "type": "proposal_summary",
                    "title": "Incomplete Settlement Proposal",
                    "certainty": "Incomplete",
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
                    "title": "Recovery Line Items",
                    "certainty": "Incomplete",
                    "data": {
                        "hero_label": "Final Net",
                        "hero_amount": None,
                        "components": [
                            {"name": "Notice Shortfall Recovery", "amount": notice_amt, "status": "Verified"},
                            {"name": "Asset Recovery", "amount": None, "status": "Unresolved"}
                        ]
                    }
                },
                {
                    "id": "card-approval-s8",
                    "type": "approval_card",
                    "title": "HR Authorization (Blocked)",
                    "certainty": "Incomplete",
                    "data": {
                        "scope_label": "Imran Khan (E12)",
                        "notice": "Cannot approve an incomplete settlement while clearance is pending.",
                        "actions": [],
                        "disabled": True
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
                "panel": {
                    "title": "Asset Clearance Status",
                    "formulas": [
                        f"Notice shortfall recovery & known deductions = {format_inr(recov_subtotal)}",
                        "Asset clearance pending: Company laptop not received",
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
        pf_amt = reasons_list[1]["effect_amount"]["value"] if len(reasons_list) > 1 else -420
        tds_chg = r.get("tds_change", {}).get("value", 0)

        after_gross = r.get("after", {}).get("earnings", {}).get("gross", {}).get("value", 45000)
        after_tot_ded = r.get("after", {}).get("total_deductions", {}).get("value", 2220)
        before_gross = r.get("before", {}).get("earnings", {}).get("gross", {}).get("value", 50000)
        before_pf = r.get("before", {}).get("pf", {}).get("value", 1800)
        after_pf = r.get("after", {}).get("pf", {}).get("value", 2220)
        pf_diff = r.get("employee_pf_change", {}).get("value", 420)
        gross_diff = abs(r.get("gross_change", {}).get("value", 5000))

        pf_rules = get_rule_file("pf-rules.json")
        old_ceiling = pf_rules.get("wage_ceiling_before_change_inr", {}).get("value", 15000)
        new_ceiling = pf_rules.get("wage_ceiling_from_change_inr", {}).get("value", 25000)
        rules_ver = pf_rules.get("rules_version", "Northwind demo rules v1")

        return {
            "messages": [
                {"code": "C30", "text": f"Your September take-home is {format_inr(abs(net_change))} lower than August. The main recorded reasons are below."},
                {"code": "C27", "text": get_message("C27")}
            ],
            "cards": [
                {
                    "id": "card-hero-s9",
                    "type": "number_hero",
                    "title": "Take-Home Pay Comparison",
                    "certainty": r.get("certainty", "Complete for this scope"),
                    "data": {
                        "hero_label": "September Take-Home",
                        "hero_amount": after_net,
                        "net_change": net_change,
                        "previous_month_label": "August Take-Home",
                        "previous_month_amount": before_net
                    }
                },
                {
                    "id": "card-reasons-s9",
                    "type": "reason_list",
                    "title": "Ranked by effect on take-home pay",
                    "certainty": r.get("certainty", "Complete for this scope"),
                    "data": {
                        "net_change": net_change,
                        "reasons": [
                            {"cause": "Loss of Pay (LOP)", "detail": "3 days unpaid leave", "amount": lop_amt},
                            {"cause": "PF ceiling change", "detail": "Revised ceiling from 17 Sep", "amount": pf_amt}
                        ],
                        "tds_change": tds_chg
                    }
                }
            ],
            "chips": [
                {"label": "Show calculation", "action": "show-calculation", "payload": {"scenario_num": 9}},
                {"label": "Draft a query for HR", "action": "draft-query", "payload": {"employee_id": "E05", "period": "2026-09"}},
                {"label": "What is LOP?", "action": "faq-lop", "payload": {}},
                {"label": "What is PF?", "action": "faq-pf", "payload": {}}
            ],
            "state": {
                "intent": "explain_salary_change",
                "scenario_num": 9,
                "role": role,
                "surface": surface,
                "employee_id": "E05",
                "panel": {
                    "title": "September Pay Breakdown",
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
        net_change = abs(r.get("net_change", {}).get("value", 13014))
        reasons_list = r.get("reasons", [])
        prior_tds_amt = reasons_list[0]["effect_amount"]["value"] if len(reasons_list) > 0 else -12454
        pf_amt = reasons_list[1]["effect_amount"]["value"] if len(reasons_list) > 1 else -560

        disp = sc.get("display_inputs", {})
        prev_gross = disp.get("previous_employer_declared_gross", {}).get("value")
        prev_tds = disp.get("previous_employer_tds", {}).get("value")
        rem_tax = disp.get("remaining_yearly_tax", {}).get("value")

        tax_rules = get_rule_file("tax-rules.json")
        rules_ver = tax_rules.get("rules_version", "Northwind demo rules v1")
        tax_year = tax_rules.get("tax_year", {}).get("value", {}).get("year", "2026-27")

        return {
            "messages": [
                {"code": "C30", "text": f"Your September take-home is {format_inr(net_change)} lower than August. The main recorded reasons are below."},
                {"code": "C29", "text": "Your TDS is higher because you declared income from your previous employer for Not available in generated data. That income is added to your yearly income, so your expected yearly tax is higher. The tax your previous employer already deducted is counted, so it is not deducted twice."},
                {"code": "C27", "text": get_message("C27")}
            ],
            "cards": [
                {
                    "id": "card-hero-s10",
                    "type": "number_hero",
                    "title": "TDS Deduction Increase",
                    "certainty": r.get("certainty", "Complete for this scope"),
                    "data": {
                        "hero_label": "September TDS Deduction",
                        "hero_amount": after_tds,
                        "tds_increase": tds_increase
                    }
                },
                {
                    "id": "card-reasons-s10",
                    "type": "reason_list",
                    "title": "Ranked by effect on take-home pay",
                    "certainty": r.get("certainty", "Complete for this scope"),
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
                "panel": {
                    "title": "Tax Calculation Proof",
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
        net_change = r.get("net_change", {}).get("value", -420)
        reasons_list = r.get("reasons", [])
        pf_amt = reasons_list[0].get("effect_amount", {}).get("value", -420) if reasons_list else -420

        after_lines = r.get("after", {}).get("earnings", {}).get("lines", {})
        basic_val = after_lines.get("basic", {}).get("value", 22500)
        special_val = after_lines.get("special_allowance", {}).get("value", 11250)
        after_gross = r.get("after", {}).get("earnings", {}).get("gross", {}).get("value", 45000)
        after_tot_ded = r.get("after", {}).get("total_deductions", {}).get("value", 2220)
        after_net = r.get("after", {}).get("net_pay", {}).get("value", 42780)

        pf_rules = get_rule_file("pf-rules.json")
        old_ceiling = pf_rules.get("wage_ceiling_before_change_inr", {}).get("value", 15000)
        new_ceiling = pf_rules.get("wage_ceiling_from_change_inr", {}).get("value", 25000)
        pf_rate = pf_rules.get("employee_contribution_rate_percent", {}).get("value", 12)
        rules_ver = pf_rules.get("rules_version", "Northwind demo rules v1")

        return {
            "messages": [
                {"code": "C30", "text": f"Your September take-home is {format_inr(abs(net_change))} lower than August. The main recorded reasons are below."},
                {"code": "C26", "text": get_message("C26")},
                {"code": "C27", "text": get_message("C27")}
            ],
            "cards": [
                {
                    "id": "card-hero-s11",
                    "type": "number_hero",
                    "title": "Take-Home Pay Change",
                    "certainty": r.get("certainty", "Complete for this scope"),
                    "data": {
                        "hero_label": "Take-Home Net Change",
                        "hero_amount": net_change,
                        "earnings_status": "No salary earning component change"
                    }
                },
                {
                    "id": "card-reasons-s11",
                    "type": "reason_list",
                    "title": "Main recorded reasons",
                    "certainty": r.get("certainty", "Complete for this scope"),
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
                "panel": {
                    "title": "Earnings & Deduction Proof",
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
        return self._build_refusal(role, surface, "Access boundary enforced.")

    def _build_scenario_13(self, user: dict, role: str, surface: str) -> dict:
        sc = bridge.get_scenario(13)
        r = sc["result"]
        c = r["components"]
        recov_subtotal = r.get("known_recoveries_subtotal", {}).get("value", 56667)
        notice_amt = c.get("notice_shortfall_recovery", {}).get("amount", {}).get("value", 46667)
        return {
            "messages": [
                {"code": "C19", "text": "The final net is incomplete because unreturned company laptop is not yet known."}
            ],
            "cards": [
                {
                    "id": "card-settlement-s13",
                    "type": "proposal_summary",
                    "title": "Settlement Breakdown (Unresolved Component)",
                    "certainty": "Incomplete",
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
                    "title": "Settlement Ledger Lines",
                    "certainty": "Incomplete",
                    "data": {
                        "hero_label": "Final Net",
                        "hero_amount": None,
                        "known_recoveries_subtotal": recov_subtotal,
                        "components": [
                            {"name": "Notice Shortfall Recovery", "amount": notice_amt, "status": "Verified"},
                            {"name": "Asset Recovery", "amount": None, "status": "Unresolved"}
                        ]
                    }
                },
                {
                    "id": "card-approval-s13",
                    "type": "approval_card",
                    "title": "Partial Authorization",
                    "certainty": "Incomplete",
                    "data": {
                        "scope_label": "Imran Khan (E12)",
                        "notice": "Approving verified component lines only. Unresolved asset recovery remains held and excluded from net payout.",
                        "actions": ["Approve verified lines only", "Edit with reason", "Reject proposal"],
                        "status": "pending",
                        "proposal_id": "PROP-SCENARIO-13"
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
                "panel": {
                    "title": "Settlement Line Review",
                    "formulas": [
                        f"Notice shortfall recovery & known deductions = {format_inr(recov_subtotal)}",
                        "Asset clearance hold: Laptop status unconfirmed",
                        "Final Net: Not available in generated data"
                    ],
                    "rule_citations": [
                        "Separation wages clearance hold: Unresolved asset recovery stays held without delaying final salary",
                        f"Rules version: {get_rule_file('settlement-rules.json').get('rules_version', 'Northwind demo rules v1')}"
                    ]
                }
            }
        }

    # --- Refusal, Fallback & FAQ Responses ---

    def _build_refusal(self, role: str, surface: str, reason: str = "") -> dict:
        return {
            "messages": [
                {"code": "C10", "text": get_message("C10")}
            ],
            "cards": [
                {
                    "id": "card-refusal",
                    "type": "refusal_card",
                    "title": "Permission Denied",
                    "certainty": "Permission denied",
                    "data": {
                        "message": get_message("C10"),
                        "reason": reason
                    }
                }
            ],
            "chips": [
                {"label": "Ask about my payroll", "action": "explain-salary", "payload": {}},
                {"label": "What is LOP?", "action": "faq-lop", "payload": {}},
                {"label": "What is PF?", "action": "faq-pf", "payload": {}}
            ],
            "state": {
                "intent": "other_employee_data",
                "role": role,
                "surface": surface,
                "scenario_num": None,
                "employee_id": None,
                "panel": None
            }
        }

    def _build_unknown_fallback(self, role: str, surface: str) -> dict:
        fallback_text = (
            "I cannot answer that question in this demo. You can ask about recorded salary and tax "
            "changes, full and final settlements, bonus eligibility, or choose a topic below:"
        )
        if role == "HR Admin":
            chips = [
                {"label": "Prepare Priya Sharma hike", "action": "scenario-1", "payload": {}},
                {"label": "Prepare team bonus proposal", "action": "scenario-4", "payload": {}},
                {"label": "Prepare Rahul Verma settlement", "action": "scenario-6", "payload": {}},
                {"label": "What is LOP?", "action": "faq-lop", "payload": {}}
            ]
        else:
            chips = [
                {"label": "Why is my take-home pay lower in September?", "action": "explain-salary", "payload": {}},
                {"label": "What is LOP?", "action": "faq-lop", "payload": {}},
                {"label": "What is PF?", "action": "faq-pf", "payload": {}},
                {"label": "Draft a query for HR", "action": "draft-query", "payload": {}}
            ]
        return {
            "messages": [
                {"code": "FALLBACK", "text": fallback_text}
            ],
            "cards": [],
            "chips": chips,
            "state": {
                "intent": "unknown",
                "role": role,
                "surface": surface,
                "scenario_num": None,
                "employee_id": None,
                "panel": None
            }
        }

    def _build_faq_response(self, faq_entry: dict, confidence: float, role: str, surface: str) -> dict:
        if role == "HR Admin":
            chips = [
                {"label": "Prepare Priya Sharma hike", "action": "scenario-1", "payload": {}},
                {"label": "What is PF?", "action": "faq-pf", "payload": {}},
                {"label": "What is TDS?", "action": "faq-tds", "payload": {}}
            ]
        else:
            chips = [
                {"label": "Why is my take-home pay lower in September?", "action": "explain-salary", "payload": {}},
                {"label": "What is PF?", "action": "faq-pf", "payload": {}},
                {"label": "What is TDS?", "action": "faq-tds", "payload": {}}
            ]
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
                        "category": faq_entry["category"],
                        "question": faq_entry["question"],
                        "answer": faq_entry["answer"],
                        "link_text": faq_entry.get("link_text", ""),
                        "url": faq_entry.get("url", ""),
                        "confidence": confidence
                    }
                }
            ],
            "chips": chips,
            "state": {
                "intent": "faq_question",
                "role": role,
                "surface": surface,
                "scenario_num": None,
                "employee_id": None,
                "panel": None
            }
        }

    def _handle_faq_query(self, topic: str, role: str, surface: str) -> dict:
        entry, conf = faq_matcher.match(topic)
        if entry:
            return self._build_faq_response(entry, conf, role, surface)
        return self._build_unknown_fallback(role, surface)

    # --- Governance & Query Handlers ---

    def _handle_approve_proposal(self, user: dict, role: str, surface: str, context: dict) -> dict:
        if role != "HR Admin":
            return self._build_refusal(role, surface, "Only HR Admin can approve proposals.")
        s_num = context.get("scenario_num", 1)
        prop_id = context.get("proposal_id", f"PROP-SCENARIO-{s_num}")
        version = int(context.get("version", 1))

        lifecycle.get_or_create_proposal(prop_id, {
            "status": "Calculated; needs HR approval",
            "certainty": "Complete for this scope",
            "scope": {"employee_id": context.get("employee_id", "E01"), "scenario_num": s_num}
        })

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
                    "chips": [{"label": "Show calculation", "action": "show-calculation", "payload": {"scenario_num": s_num}}],
                    "state": {"intent": "approve_error", "code": "C25", "role": role, "surface": surface, "panel": None}
                }
            raise he

        approver_name = user.get("name", "Anita Desai")
        approved_time = datetime.now(timezone.utc).isoformat()
        status_badge = f"Approved and ready for payroll • Version {version} • Approved by {approver_name}"

        scope_base = "Priya Sharma · Apr–Sep 2026"
        if s_num == 2:
            scope_base = "Arjun Rao · Apr–Sep 2026"
        elif s_num == 3:
            scope_base = "Sneha Kulkarni · Apr–Sep 2026"
        elif s_num == 4:
            scope_base = "Vikram Malhotra · Apr–Sep 2026"
        elif s_num == 5:
            scope_base = "Ananya Sen · Apr–Sep 2026"
        elif s_num == 6:
            scope_base = "Rahul Verma · Settlement"
        elif s_num == 7:
            scope_base = "Lakshmi Reddy · Settlement"
        elif s_num == 8:
            scope_base = "Amit Patel · Settlement"

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
                        "scope_label": f"Approved: {scope_base}"
                    }
                }
            ],
            "chips": [
                {"label": "Show calculation", "action": "show-calculation", "payload": {"scenario_num": s_num}}
            ],
            "state": {
                "intent": "approve_proposal",
                "scenario_num": s_num,
                "role": role,
                "surface": surface,
                "employee_id": context.get("employee_id"),
                "status": "Approved and ready for payroll",
                "panel": None
            }
        }

    def _handle_edit_proposal(self, user: dict, role: str, surface: str, context: dict) -> dict:
        if role != "HR Admin":
            return self._build_refusal(role, surface, "Only HR Admin can edit proposals.")
        s_num = context.get("scenario_num", 1)
        prop_id = context.get("proposal_id", f"PROP-SCENARIO-{s_num}")
        line = context.get("line", "gross_arrears")
        proposed_value = context.get("proposed_value", 70000)
        reason = context.get("reason", "Adjusted attendance records for June")

        lifecycle.get_or_create_proposal(prop_id, {
            "status": "Calculated; needs HR approval",
            "certainty": "Complete for this scope",
            "scope": {"employee_id": context.get("employee_id", "E01"), "scenario_num": s_num}
        })

        res = lifecycle.edit_proposal(
            proposal_id=prop_id,
            actor=user,
            line=line,
            proposed_value=proposed_value,
            reason=reason
        )
        return {
            "messages": [
                {"code": "C05", "text": get_message("C05")}
            ],
            "cards": [
                {
                    "id": f"card-edit-{prop_id}",
                    "type": "proposal_summary",
                    "title": "Revised Proposal Summary",
                    "certainty": "Complete for this scope",
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
            ],
            "chips": [
                {"label": "Show calculation", "action": "show-calculation", "payload": {"scenario_num": s_num}}
            ],
            "state": {
                "intent": "edit_proposal",
                "role": role,
                "surface": surface,
                "scenario_num": s_num,
                "version": res["version"],
                "panel": None
            }
        }

    def _handle_reject_proposal(self, user: dict, role: str, surface: str, context: dict) -> dict:
        if role != "HR Admin":
            return self._build_refusal(role, surface, "Only HR Admin can reject proposals.")
        s_num = context.get("scenario_num", 1)
        prop_id = context.get("proposal_id", f"PROP-SCENARIO-{s_num}")
        reason = context.get("reason", "Documentation incomplete or unverified.")

        lifecycle.get_or_create_proposal(prop_id, {
            "status": "Calculated; needs HR approval",
            "certainty": "Complete for this scope",
            "scope": {"employee_id": context.get("employee_id", "E01"), "scenario_num": s_num}
        })

        res = lifecycle.reject_proposal(proposal_id=prop_id, actor=user, reason=reason)
        return {
            "messages": [
                {"code": "REJECTED", "text": "The proposal has been rejected."}
            ],
            "cards": [
                {
                    "id": f"card-reject-{prop_id}",
                    "type": "approval_card",
                    "title": "Proposal Rejected",
                    "data": {
                        "proposal_id": prop_id,
                        "status": "rejected",
                        "status_badge": "Rejected • Not approved for payroll",
                        "notice": "This proposal has been rejected and will not be applied to payroll."
                    }
                }
            ],
            "chips": [],
            "state": {
                "intent": "reject_proposal",
                "role": role,
                "surface": surface,
                "scenario_num": s_num,
                "panel": None
            }
        }

    def _handle_draft_query(self, user: dict, role: str, surface: str, context: dict) -> dict:
        emp_id = context.get("employee_id") or user.get("employee_id") or "E05"
        period = context.get("period") or "2026-09"
        desc = context.get("description") or "Please review my September attendance and LOP deduction."
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
                    "title": "Review Query Draft",
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
                    "title": "Query Sent",
                    "data": {
                        "query_id": sent_query["query_id"],
                        "status": "Sent",
                        "status_message": get_message("C15")
                    }
                }
            ],
            "chips": [
                {"label": "Check my query status", "action": "query-status", "payload": {}},
                {"label": "Why is my take-home pay lower in September?", "action": "explain-salary", "payload": {}}
            ],
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
                    "title": "Query Updated",
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
        code_map = {"Sent": "C15", "In review": "C16", "Resolved": "C23", "Closed": "C24", "Draft": "C17"}
        msg_code = code_map.get(st, "C15")

        return {
            "messages": [
                {"code": msg_code, "text": get_message(msg_code)}
            ],
            "cards": [
                {
                    "id": f"card-status-{latest['query_id']}",
                    "type": "query_status",
                    "title": "Payroll Query Status",
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
            "chips": [
                {"label": "Draft a query for HR", "action": "draft-query", "payload": {}},
                {"label": "Why is my take-home pay lower in September?", "action": "explain-salary", "payload": {}}
            ],
            "state": {
                "intent": "query_status",
                "role": role,
                "surface": surface,
                "employee_id": emp_id,
                "panel": None
            }
        }

    def _handle_hr_query_review(self, user: dict, role: str, surface: str, context: dict) -> dict:
        queries = lifecycle.get_queries()
        return {
            "messages": [
                {"code": "HR_QUERY_LIST", "text": f"Here are the recorded employee queries ({len(queries)} total):"}
            ],
            "cards": [
                {
                    "id": "card-hr-queries",
                    "type": "query_status",
                    "title": "Pending Queries",
                    "data": {
                        "queries": queries
                    }
                }
            ],
            "chips": [],
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
            queries = lifecycle.get_queries()
            q_id = queries[0]["query_id"] if queries else "QUERY-E05-20260901"
        res = lifecycle.take_into_review(q_id, actor=user)
        q = res["query"]
        return {
            "messages": [
                {"code": "C16", "text": get_message("C16")}
            ],
            "cards": [
                {
                    "id": f"card-status-{q['query_id']}",
                    "type": "query_status",
                    "title": "Payroll Query In Review",
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
            queries = lifecycle.get_queries()
            q_id = queries[0]["query_id"] if queries else "QUERY-E05-20260901"
        reply = context.get("reply_text") or context.get("reply") or "Attendance records reviewed and verified against biometric logs."
        res = lifecycle.reply_query(q_id, actor=user, reply_text=reply)
        q = res["query"]
        return {
            "messages": [
                {"code": "C16", "text": get_message("C16")}
            ],
            "cards": [
                {
                    "id": f"card-status-{q['query_id']}",
                    "type": "query_status",
                    "title": "Query Reply Recorded",
                    "data": {
                        "query_id": q["query_id"],
                        "status": q.get("status", "In review"),
                        "description": q.get("description"),
                        "reply_text": q.get("hr_reply")
                    }
                }
            ],
            "chips": [],
            "state": {"intent": "hr_query_review", "role": role, "surface": surface, "panel": None}
        }

    def _handle_resolve_query(self, user: dict, role: str, surface: str, context: dict) -> dict:
        q_id = context.get("query_id")
        if not q_id:
            queries = lifecycle.get_queries()
            q_id = queries[0]["query_id"] if queries else "QUERY-E05-20260901"
        reply = context.get("reply_text") or "Attendance reviewed and verified against punch records."
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
                    "title": "Query Resolved",
                    "data": {
                        "query_id": q["query_id"],
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
            queries = lifecycle.get_queries()
            q_id = queries[0]["query_id"] if queries else "QUERY-E05-20260901"
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
                    "title": "Resolution Disputed",
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
            queries = lifecycle.get_queries()
            resolved_q = next((q for q in queries if q.get("status") == "Resolved"), None)
            q_id = resolved_q["query_id"] if resolved_q else (queries[0]["query_id"] if queries else "QUERY-E05-20260901")
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
                    "title": "Query Closed",
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

    def _handle_show_calculation(self, user: dict, role: str, surface: str, context: dict) -> dict:
        s_num = context.get("scenario_num", 1)
        builder = getattr(self, f"_build_scenario_{s_num}", self._build_scenario_1)
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


chat_router = ChatRouter()
