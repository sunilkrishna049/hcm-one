"""CrewAI orchestration pipeline for HCM One AI layer.
Implements Option B (Guarded Natural Replies with Slot-Based Drafting).
Only Classifier and Drafting agents invoke the LLM.
Retrieval and Escalation use deterministic tools only.
"""
from datetime import datetime, timezone
import json
import re
import time
from typing import Any, Dict, Optional

from crewai import LLM, Crew, Process, Task

from ..ai_messages import get_message
from ..auth import USERS, check_employee_access
from ..chat_router import ChatRouter, EMPLOYEE_NAMES

from ..config import (
    AI_MAX_OUTPUT_TOKENS,
    AI_MODE,
    AI_TIMEOUT_MS,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    is_ai_enabled,
)
from .agents import (
    ALLOWED_INTENTS,
    ClassifierOutput,
    create_classifier_agent,
    create_drafting_agent,
    create_escalation_agent,
    create_retrieval_agent,
    validate_classifier_output,
)
from .facts import build_facts_list
from .guards import RuntimeGuardPipeline
from .logger import log_ai_run
from .tools import get_payroll_scenario_data, search_payroll_faq

_router = ChatRouter()
_guards = RuntimeGuardPipeline(EMPLOYEE_NAMES)


# Pre-AI Prompt Injection Patterns (Input-side gate)
INJECTION_PATTERNS = [
    r"ignore (all|previous|your) (rules|instructions)",
    r"system prompt",
    r"reveal.*(instruction|prompt|secret)",
    r"jailbreak",
    r"developer mode",
    r"forget (the|your) rules",
    r"bypass.*(security|guard)"
]


class PayrollAICrew:
    def __init__(self, llm: Optional[Any] = None):
        self._custom_llm = llm

    def _get_llm(self) -> Optional[Any]:
        if self._custom_llm is not None:
            return self._custom_llm
        if not is_ai_enabled():
            return None
        return LLM(
            model=OPENAI_MODEL,
            api_key=OPENAI_API_KEY,
            temperature=0.1,
            max_tokens=AI_MAX_OUTPUT_TOKENS,
            timeout=int(AI_TIMEOUT_MS / 1000)
        )

    def handle_chat(
        self,
        user_id: str,
        message: str = "",
        action: Optional[str] = None,
        context: Optional[dict] = None
    ) -> dict:
        """Main chat entry point. Enforces input-side pipeline, CrewAI execution,
        mechanical runtime guards, and deterministic router fallback.
        """
        start_time = time.time()
        context = context or {}
        raw_msg = (message or "").strip()
        lower_msg = raw_msg.lower()

        user = USERS.get(user_id, USERS.get("HR01", {}))
        role = user.get("role", "Employee")
        surface = "CHAT-HR" if role == "HR Admin" else "CHAT-EMP"

        # -------------------------------------------------------------
        # STEP 1: Input-Side Pipeline (Before any LLM call)
        # -------------------------------------------------------------

        # 1a. Prompt-Injection Check
        for pat in INJECTION_PATTERNS:
            if re.search(pat, lower_msg):
                log_ai_run(
                    user_id=user_id,
                    role=role,
                    surface=surface,
                    intent="prompt_injection",
                    scenario_num=None,
                    guards_result={"prompt_injection_gate": "FAIL"},
                    fallback_triggered=True,
                    fallback_reason="Prompt injection prevented before LLM call",
                    latency_ms=(time.time() - start_time) * 1000
                )
                return _router._build_refusal(role, surface, "Prompt injection prevented.")

        # 1b. Role and Authorized Data Isolation Check (Scenario 12)
        if context.get("scenario_num") == 12:
            return _router._build_scenario_12(user, role, surface)

        allowed_emp_ids = set(user.get("allowed_employee_ids") or [])
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
            if (name in lower_msg or emp_id.lower() in lower_msg) and emp_id not in allowed_emp_ids:
                # Unauthorized employee access attempt: zero data sent to LLM
                return _router._build_scenario_12(user, role, surface)

        if role == "Employee" and any(k in lower_msg for k in ("other people", "another person", "colleague")):
            return _router._build_scenario_12(user, role, surface)

        # 1c. Deterministic Action Handling (Buttons, Chips, Governance Clicks)
        # Explicit button clicks bypass natural drafting and execute deterministic handlers
        if action:
            return _router.handle_chat(user_id=user_id, message=message, action=action, context=context)

        # 1d. AI Mode Switch Check
        llm = self._get_llm()
        if not is_ai_enabled() and self._custom_llm is None:
            # Deterministic router baseline
            return _router.handle_chat(user_id=user_id, message=message, action=action, context=context)

        # -------------------------------------------------------------
        # STEP 2: CrewAI Execution (Classifier, Retrieval, Drafting, Escalation)
        # -------------------------------------------------------------
        try:
            # Agent 1: Classifier Agent (LLM)
            if self._custom_llm and hasattr(self._custom_llm, "classify"):
                classifier_res = validate_classifier_output(self._custom_llm.classify(raw_msg, role, context), user)
            else:
                classifier_agent = create_classifier_agent(llm)
                classify_task = Task(
                    description=(
                        f"Classify this payroll message: '{raw_msg}'.\n"
                        f"User Role: {role}\n"
                        f"Allowed intents: {list(ALLOWED_INTENTS)}\n"
                        "Extract intent, scenario_num (1-13 if applicable), and entities (employee_name, month, bonus_type).\n"
                        "NEVER include numbers or calculation amounts in your output.\n"
                        "Format strictly as JSON with keys: intent, scenario_num, entities, confidence, is_prompt_injection, clarification_needed."
                    ),
                    expected_output="JSON object with classification fields",
                    agent=classifier_agent
                )
                classifier_res = self._execute_classifier(classify_task, raw_msg, role, user, context)

            if classifier_res.is_prompt_injection:
                return _router._build_refusal(role, surface, "Prompt injection prevented.")

            # Scenario 12 check from classifier entities
            if classifier_res.scenario_num == 12 or (
                classifier_res.entities.get("access_denied") == "true"
            ):
                return _router._build_scenario_12(user, role, surface)

            # Ambiguous bonus check -> show clarifying question card
            if (
                classifier_res.clarification_needed
                or (classifier_res.intent == "bonus_proposal" and not classifier_res.entities.get("bonus_type"))
            ):
                if "annual" not in lower_msg and "sales" not in lower_msg:
                    return _router._build_bonus_clarifying_question(role, surface)

            # Agent 2: Retrieval Agent (Deterministic Tools Only — No LLM)
            scenario_num = classifier_res.scenario_num or context.get("scenario_num")
            bonus_key = None
            if "annual" in lower_msg:
                bonus_key = "annual_performance_bonus"
            elif "sales" in lower_msg:
                bonus_key = "quarterly_sales_incentive"

            retrieval_data = self._execute_retrieval(scenario_num, user_id, bonus_key, raw_msg)
            if not retrieval_data.get("authorized", True) or not retrieval_data.get("cards"):
                # Fallback to deterministic router
                return _router.handle_chat(user_id=user_id, message=message, action=action, context=context)

            facts_list = retrieval_data.get("facts_list", {})
            active_emp_id = facts_list.get("employee_id") or user.get("employee_id")

            # Agent 3: Drafting Agent (LLM: Slot-Based Drafting)
            if self._custom_llm and hasattr(self._custom_llm, "draft"):
                raw_draft = self._custom_llm.draft(raw_msg, facts_list, scenario_num, role)
            else:
                drafting_agent = create_drafting_agent(llm)
                allowed_slots_str = ", ".join([f"{{{k}}}" for k in facts_list.keys()])
                draft_task = Task(
                    description=(
                        f"Write a short, natural payroll reply (1 to 3 sentences, maximum 60 words) for {role}.\n"
                        f"User message: '{raw_msg}'\n"
                        f"Available facts slots: {allowed_slots_str}\n"
                        "RULES:\n"
                        "1. NEVER write any numbers, amounts, percentages, or dates directly. Use ONLY named slots like {net_change}, {later_month}.\n"
                        "2. Do NOT type any digits (0-9).\n"
                        "3. Plain, calm, respectful tone. No conversational fluff or greetings.\n"
                        "4. Do NOT make payment promises or give tax regime recommendations."
                    ),
                    expected_output="Plain text reply with slot tokens and zero digits",
                    agent=drafting_agent
                )
                raw_draft = self._execute_drafting(draft_task, raw_msg, facts_list, scenario_num, role)


            # -------------------------------------------------------------
            # STEP 3: Mechanical Runtime Guards & Server Slot Filling
            # -------------------------------------------------------------
            guard_result = _guards.validate_and_fill(
                raw_draft=raw_draft,
                facts_list=facts_list,
                active_employee_id=active_emp_id
            )

            if not guard_result.passed:
                # Deterministic Fallback on Guard Failure
                log_ai_run(
                    user_id=user_id,
                    role=role,
                    surface=surface,
                    intent=classifier_res.intent,
                    scenario_num=scenario_num,
                    guards_result={"guard_check": "FAIL", "failed_guard": guard_result.failed_guard},
                    fallback_triggered=True,
                    fallback_reason=guard_result.error_message,
                    latency_ms=(time.time() - start_time) * 1000
                )
                return _router.handle_chat(user_id=user_id, message=message, action=action, context=context)

            # -------------------------------------------------------------
            # STEP 4: Server Critical Sentence Appending
            # -------------------------------------------------------------
            messages = [{"code": "AI", "text": guard_result.filled_text}]

            # Appends approved follow-up questions / critical statements
            if scenario_num in (1, 2, 4, 6):
                # HR proposals: append C04 notice if not present
                messages.append({"code": "C04", "text": get_message("C04")})
            elif scenario_num in (9, 10, 11):
                # Employee explanations: append follow-up breakdown offer C27
                messages.append({"code": "C27", "text": get_message("C27")})


            # Assemble response matching chat_contract.md
            response = {
                "messages": messages,
                "cards": retrieval_data.get("cards", []),
                "chips": retrieval_data.get("chips", []),
                "state": {
                    **retrieval_data.get("state", {}),
                    "intent": classifier_res.intent,
                    "scenario_num": scenario_num,
                    "role": role,
                    "surface": surface,
                    "employee_id": active_emp_id
                }
            }

            # Log successful AI run
            log_ai_run(
                user_id=user_id,
                role=role,
                surface=surface,
                intent=classifier_res.intent,
                scenario_num=scenario_num,
                guards_result={"all_guards": "PASS"},
                fallback_triggered=False,
                fallback_reason=None,
                latency_ms=(time.time() - start_time) * 1000,
                metrics={"used_slots": guard_result.used_slots}
            )

            return response

        except Exception as e:
            # Fallback on any runtime exception or timeout (>20s)
            log_ai_run(
                user_id=user_id,
                role=role,
                surface=surface,
                intent="unknown",
                scenario_num=context.get("scenario_num"),
                guards_result={"execution_error": str(e)},
                fallback_triggered=True,
                fallback_reason=f"Exception in AI Crew: {str(e)}",
                latency_ms=(time.time() - start_time) * 1000
            )
            return _router.handle_chat(user_id=user_id, message=message, action=action, context=context)

    # -------------------------------------------------------------
    # Helper Execution Methods
    # -------------------------------------------------------------

    def _execute_classifier(self, task: Task, message: str, role: str, user: dict, context: dict) -> ClassifierOutput:
        """Executes Classifier task and validates output."""
        lower_msg = message.lower()

        # If custom LLM is a mock or callable, use it; otherwise run task
        if self._custom_llm and hasattr(self._custom_llm, "classify"):
            raw_out = self._custom_llm.classify(message, role, context)
            return validate_classifier_output(raw_out, user)

        # Standard Crew task execution
        try:
            crew = Crew(
                agents=[task.agent],
                tasks=[task],
                process=Process.sequential,
                verbose=False
            )
            result_str = str(crew.kickoff())
            # Parse JSON from result
            m = re.search(r"\{.*\}", result_str, re.DOTALL)
            if m:
                raw_json = json.loads(m.group(0))
                return validate_classifier_output(raw_json, user)
        except Exception:
            pass

        # Fallback heuristic mapping if LLM returns unstructured output
        return self._heuristic_fallback_classification(lower_msg, role, user, context)

    def _heuristic_fallback_classification(self, lower_msg: str, role: str, user: dict, context: dict) -> ClassifierOutput:
        """Fallback classification when LLM is unavailable or fails to emit valid JSON."""
        if "priya" in lower_msg:
            return validate_classifier_output({"intent": "prepare_hike", "scenario_num": 1, "entities": {"employee_name": "Priya Sharma"}}, user)
        if "arjun" in lower_msg:
            return validate_classifier_output({"intent": "review_hike", "scenario_num": 2, "entities": {"employee_name": "Arjun Rao"}}, user)
        if "kavya" in lower_msg:
            return validate_classifier_output({"intent": "prepare_hike", "scenario_num": 3, "entities": {"employee_name": "Kavya Iyer"}}, user)
        if "bonus" in lower_msg:
            return validate_classifier_output({"intent": "bonus_proposal", "scenario_num": 4}, user)
        if "rahul" in lower_msg:
            return validate_classifier_output({"intent": "settlement_proposal", "scenario_num": 6, "entities": {"employee_name": "Rahul Verma"}}, user)
        if "september" in lower_msg or "take-home" in lower_msg or "drop" in lower_msg:
            return validate_classifier_output({"intent": "explain_salary", "scenario_num": 9}, user)
        if "tds" in lower_msg:
            return validate_classifier_output({"intent": "explain_tds", "scenario_num": 10}, user)
        if "gross" in lower_msg:
            return validate_classifier_output({"intent": "explain_deduction", "scenario_num": 11}, user)

        sc_num = context.get("scenario_num")
        return validate_classifier_output({"intent": "unknown", "scenario_num": sc_num}, user)

    def _execute_retrieval(self, scenario_num: Optional[int], user_id: str, bonus_type_key: Optional[str], query: str) -> dict:
        """Executes deterministic Retrieval Agent tools directly."""
        if scenario_num:
            return get_payroll_scenario_data.run(
                scenario_num=scenario_num,
                user_id=user_id,
                bonus_type_key=bonus_type_key or ""
            )

        # Check FAQ lookup
        faq_res = search_payroll_faq.run(query=query, user_id=user_id)
        if faq_res.get("found"):
            return {
                "authorized": True,
                "cards": faq_res.get("cards", []),
                "chips": faq_res.get("chips", []),
                "state": faq_res.get("state", {}),
                "facts_list": {}
            }

        return {"authorized": False}

    def _execute_drafting(self, task: Task, message: str, facts_list: dict, scenario_num: Optional[int], role: str) -> str:
        """Executes Drafting task with mock or live LLM."""
        if self._custom_llm and hasattr(self._custom_llm, "draft"):
            return self._custom_llm.draft(message, facts_list, scenario_num, role)

        try:
            crew = Crew(
                agents=[task.agent],
                tasks=[task],
                process=Process.sequential,
                verbose=False
            )
            return str(crew.kickoff()).strip()
        except Exception:
            # Fallback natural slotted template if drafting LLM errors
            if scenario_num == 9:
                return "Your {later_month} take-home pay is {net_change} {net_change_direction} than {earlier_month}. The change is due to {lop_days} days unpaid leave and the revised PF ceiling."
            elif scenario_num == 1:
                return "This is a proposal for the recorded hike for {employee_name} for {period}. Gross arrears are {gross_arrears}."
            elif scenario_num == 4:
                return "This is a proposal for the recorded {bonus_type} for {period}. Known eligible gross is {known_eligible_gross}."
            return "Here are the recorded payroll calculation details for your review."


ai_crew = PayrollAICrew()
