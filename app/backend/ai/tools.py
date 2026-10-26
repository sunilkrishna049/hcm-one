"""Deterministic tools for the HCM One AI Layer.
These tools are read-only and strictly deterministic.
They produce the exact scenario cards, facts lists, and FAQ responses.
The AI never calculates, sums, rounds, or invents a number.
"""
from typing import Dict, List, Optional
from crewai.tools import tool

from ..auth import USERS, check_employee_access
from ..chat_router import ChatRouter
from ..faq_matcher import faq_matcher
from ..engine_bridge import bridge
from .facts import build_facts_list

_router = ChatRouter()


@tool("get_payroll_scenario_data")
def get_payroll_scenario_data(scenario_num: int, user_id: str = "HR01", bonus_type_key: str = "") -> dict:
    """Fetches deterministic payroll scenario calculation, UI cards, and turn-scoped facts list.
    AI must never calculate numbers. This tool provides the verified calculation results.
    """
    user = USERS.get(user_id, USERS.get("HR01", {}))
    role = user.get("role", "HR Admin")
    surface = "CHAT-HR" if role == "HR Admin" else "CHAT-EMP"

    # Pre-flight authorization check
    if scenario_num == 12:
        return {
            "authorized": False,
            "response": _router._build_scenario_12(user, role, surface),
            "facts_list": {}
        }

    # Execute deterministic scenario builder
    method_name = f"_build_scenario_{scenario_num}"
    if not hasattr(_router, method_name):
        return {
            "authorized": False,
            "response": _router._build_unknown_fallback(role, surface),
            "facts_list": {}
        }

    builder = getattr(_router, method_name)
    if scenario_num == 4 and bonus_type_key:
        res = builder(user, role, surface, bonus_type_key=bonus_type_key)
    else:
        res = builder(user, role, surface)

    facts = build_facts_list(scenario_num, user, bonus_type_key=bonus_type_key or None)

    return {
        "authorized": True,
        "scenario_num": scenario_num,
        "cards": res.get("cards", []),
        "chips": res.get("chips", []),
        "state": res.get("state", {}),
        "facts_list": facts,
        "certainty_label": res.get("cards", [{}])[0].get("certainty", "Complete for this scope") if res.get("cards") else "Complete for this scope"
    }


@tool("search_payroll_faq")
def search_payroll_faq(query: str, user_id: str = "HR01") -> dict:
    """Searches the official HCM One Payroll FAQ knowledge repository for glossary definitions and policy rules.
    Returns the verified answer, link, and related chips.
    """
    user = USERS.get(user_id, USERS.get("HR01", {}))
    role = user.get("role", "HR Admin")
    surface = "CHAT-HR" if role == "HR Admin" else "CHAT-EMP"

    matched_faq, conf = faq_matcher.match(query)
    if matched_faq and conf >= 0.35:
        res = _router._build_faq_response(matched_faq, conf, role, surface)
        return {
            "found": True,
            "faq_id": matched_faq.get("id"),
            "question": matched_faq.get("question"),
            "answer": matched_faq.get("answer"),
            "cards": res.get("cards", []),
            "chips": res.get("chips", []),
            "state": res.get("state", {})
        }

    return {"found": False}
