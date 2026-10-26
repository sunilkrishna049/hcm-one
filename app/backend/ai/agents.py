"""CrewAI agent definitions and structured schemas for HCM One AI layer.
Only Classifier and Drafting agents invoke the LLM.
Retrieval and Escalation use deterministic tools only.
"""
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field
from crewai import Agent

from ..auth import check_employee_access
from ..chat_router import EMPLOYEE_NAMES
from .tools import get_payroll_scenario_data, search_payroll_faq

ALLOWED_INTENTS = {
    "prepare_hike",
    "review_hike",
    "bonus_proposal",
    "settlement_proposal",
    "settlement_review",
    "explain_salary",
    "explain_tds",
    "explain_deduction",
    "faq_query",
    "query_flow",
    "out_of_scope",
    "prompt_injection",
    "unknown"
}


class ClassifierOutput(BaseModel):
    intent: str
    scenario_num: Optional[int] = None
    entities: Dict[str, Optional[str]] = Field(default_factory=dict)
    confidence: float = 1.0
    is_prompt_injection: bool = False
    clarification_needed: bool = False


def validate_classifier_output(raw_output: dict, user: dict) -> ClassifierOutput:
    """Deterministic validation of Classifier Agent output:
    1. Validates intent against ALLOWED_INTENTS.
    2. Resolves employee names to IDs deterministically with role checks (never by LLM).
    3. Handles ambiguity or low confidence.
    """
    intent = raw_output.get("intent", "unknown")
    if intent not in ALLOWED_INTENTS:
        intent = "unknown"

    scenario_num = raw_output.get("scenario_num")
    entities = raw_output.get("entities", {}) or {}
    confidence = float(raw_output.get("confidence", 1.0))
    is_injection = bool(raw_output.get("is_prompt_injection", False))
    clarification_needed = bool(raw_output.get("clarification_needed", False))

    # Deterministic employee name resolution and RBAC check
    emp_name_query = entities.get("employee_name")
    if emp_name_query:
        resolved_id, resolved_name, is_allowed = resolve_employee_by_name(emp_name_query, user)
        entities["employee_id"] = resolved_id
        if resolved_name:
            entities["employee_name"] = resolved_name
        if resolved_id and not is_allowed:
            # Cross-employee access attempt!
            return ClassifierOutput(
                intent="out_of_scope",
                scenario_num=12,
                entities={"employee_id": resolved_id, "access_denied": "true"},
                confidence=1.0,
                is_prompt_injection=False,
                clarification_needed=False
            )

    if confidence < 0.65 or clarification_needed:
        clarification_needed = True

    return ClassifierOutput(
        intent=intent,
        scenario_num=scenario_num,
        entities=entities,
        confidence=confidence,
        is_prompt_injection=is_injection,
        clarification_needed=clarification_needed
    )


def resolve_employee_by_name(name_query: str, user: dict) -> Tuple[Optional[str], Optional[str], bool]:
    """Deterministically maps an employee name query to employee ID and checks user role access."""
    q = (name_query or "").strip().lower()
    matched_id = None
    matched_name = None

    for eid, full_name in EMPLOYEE_NAMES.items():
        if q in full_name.lower() or full_name.lower() in q:
            matched_id = eid
            matched_name = full_name
            break

    if not matched_id:
        return None, None, True

    is_allowed = check_employee_access(user, matched_id)
    return matched_id, matched_name, is_allowed


def create_classifier_agent(llm) -> Agent:
    return Agent(
        role="HCM One Payroll Intent Classifier",
        goal="Accurately classify payroll questions into allowed intents and entities without numbers.",
        backstory="Expert classifier trained on enterprise payroll terminology, casual English, and common transliterated Hinglish. Emits zero numbers.",
        llm=llm,
        verbose=False,
        allow_delegation=False
    )


def create_retrieval_agent(llm=None) -> Agent:
    return Agent(
        role="Deterministic Payroll Data Retriever",
        goal="Retrieve verified cards, numbers, and facts list from deterministic tools.",
        backstory="Strictly deterministic tool runner. Never calculates, estimates, or guesses numbers.",
        tools=[get_payroll_scenario_data, search_payroll_faq],
        llm=llm,
        verbose=False,
        allow_delegation=False
    )


def create_drafting_agent(llm) -> Agent:
    return Agent(
        role="HCM One Slot-Based Communications Drafter",
        goal="Write a natural, calm 1-to-3 sentence explanation using named slots from facts list and zero digits.",
        backstory="Speaks in Agent 06 voice: plain, respectful, reassuring, objective. Never types digits (0-9) and never promises payment.",
        llm=llm,
        verbose=False,
        allow_delegation=False
    )


def create_escalation_agent(llm=None) -> Agent:
    return Agent(
        role="Governance and Human Action Router",
        goal="Configure action chips and human review gates without executing state changes.",
        backstory="Deterministic human-in-the-loop router. Enforces that actions require explicit clicks.",
        llm=llm,
        verbose=False,
        allow_delegation=False
    )
