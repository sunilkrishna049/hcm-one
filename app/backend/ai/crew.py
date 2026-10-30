"""CrewAI orchestration pipeline for HCM One AI layer.
Implements Option B (Guarded Natural Replies with Slot-Based Drafting).
Only Classifier and Drafting agents invoke the LLM.
Retrieval and Escalation use deterministic tools only.
"""
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import time
from typing import Any, Dict, List, Optional

from crewai import LLM, Crew, Process, Task

from ..ai_messages import get_message
from ..auth import USERS, check_employee_access
from ..chat_router import ChatRouter, EMPLOYEE_NAMES
from ..faq_matcher import faq_matcher
from ..permissions import get_mentioned_employee_ids, enforce_reply_permissions

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



def get_required_slots_for_intent(intent: Optional[str], scenario_num: Optional[int]) -> List[str]:
    """Returns required slots that drafting must include for specific explanation intents (Item 8)."""
    if scenario_num == 9 or intent in ("explain_salary", "explain_salary_change"):
        return ["{net_change}", "{earlier_month}", "{later_month}", "{lop_amount}", "{pf_change}"]
    elif scenario_num == 10 or intent in ("explain_tds", "explain_tds_change"):
        return ["{net_change}", "{earlier_month}", "{later_month}", "{tds_increase}", "{pf_change}"]
    elif scenario_num == 11 or intent in ("explain_deduction",):
        return ["{net_change}", "{earlier_month}", "{later_month}", "{pf_change}"]
    return []


def build_draft_task_description(
    raw_msg: str,
    role: str,
    facts_list: dict,
    intent: Optional[str],
    scenario_num: Optional[int]
) -> str:
    allowed_slots_str = ", ".join([f"{{{k}}}" for k in facts_list.keys()])
    req_slots = get_required_slots_for_intent(intent, scenario_num)
    req_instruction = f"Required slots that MUST be included in your draft: {', '.join(req_slots)}.\n" if req_slots else ""

    return (
        f"Write a short, natural payroll reply (1 to 3 sentences, maximum 60 words) for {role}.\n"
        f"User message: '{raw_msg}'\n"
        f"Available facts slots: {allowed_slots_str}\n"
        f"{req_instruction}"
        "RULES:\n"
        "1. For salary and TDS explanations: lead with the net change amount {net_change} and the two months {earlier_month} and {later_month}, then the reasons with their amounts (including {lop_amount} for LOP and {pf_change} for PF), in plain words. State facts directly.\n"
        "2. NEVER write any numbers, amounts, percentages, or dates directly. Use ONLY named slots like {net_change}, {later_month}, {lop_amount}.\n"
        "3. Do NOT type any digits (0-9).\n"
        "4. State facts directly. Do NOT use hedging words (no may, might, possibly, could be, perhaps, likely, seems) when facts are complete.\n"
        "5. Absolutely NO closing filler (no 'If you have further questions', 'please let me know', 'Hope this helps', 'Feel free to ask'). End immediately after stating facts.\n"
        "6. Plain, calm, respectful tone. No conversational fluff or greetings.\n"
        "7. Do NOT make payment promises or give tax regime recommendations."
    )


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
        user = USERS.get(user_id, USERS.get("HR01", {}))
        response = self._handle_chat_internal(user_id=user_id, message=message, action=action, context=context)
        return enforce_reply_permissions(response, user)

    def _handle_chat_internal(
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
        run_tag = context.get("tag") if isinstance(context, dict) else None
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
                    latency_ms=(time.time() - start_time) * 1000,
                    tag=run_tag
                )
                return _router._build_refusal(role, surface, "Prompt injection prevented.")

        # 1b. Role and Authorized Data Isolation Check (Scenario 12)
        if context.get("scenario_num") == 12:
            return _router._build_scenario_12(user, role, surface)

        allowed_emp_ids = set(user.get("allowed_employee_ids") or [])
        mentioned_emp_ids = get_mentioned_employee_ids(lower_msg)
        for emp_id in mentioned_emp_ids:
            if emp_id not in allowed_emp_ids:
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
        classifier_res: Optional[ClassifierOutput] = None
        scenario_num: Optional[int] = None
        bonus_key: Optional[str] = None

        try:
            # Agent 1: Classifier Agent (LLM)
            merged_ctx = {"user_id": user_id, "employee_id": user.get("employee_id"), **context}
            if self._custom_llm and hasattr(self._custom_llm, "classify"):
                classifier_res = validate_classifier_output(self._custom_llm.classify(raw_msg, role, merged_ctx), user)
            else:
                classifier_agent = create_classifier_agent(llm)
                classify_task = Task(
                    description=(
                        f"Classify this English payroll message: '{raw_msg}'. (English only).\n"
                        f"User Role: {role}\n"
                        f"Allowed intents: {list(ALLOWED_INTENTS)}\n"
                        "Extract intent, scenario_num (1-13 if applicable), and entities (employee_name, month, bonus_type).\n"
                        "NEVER include numbers or calculation amounts in your output.\n"
                        "Format strictly as JSON with keys: intent, scenario_num, entities, confidence, is_prompt_injection, clarification_needed."
                    ),
                    expected_output="JSON object with classification fields",
                    agent=classifier_agent
                )
                classifier_res = self._execute_classifier(classify_task, raw_msg, role, user, merged_ctx)

            if classifier_res.is_prompt_injection:
                return _router._build_refusal(role, surface, "Prompt injection prevented.")

            # Scenario 12 check from classifier entities
            if classifier_res.scenario_num == 12 or (
                classifier_res.entities.get("access_denied") == "true"
            ):
                return _router._build_scenario_12(user, role, surface)

            # Ambiguous bonus check -> show clarifying question card (only for team bonus without specific employee)
            if (
                classifier_res.intent == "bonus_proposal"
                and (
                    classifier_res.clarification_needed
                    or (
                        not classifier_res.entities.get("bonus_type")
                        and classifier_res.scenario_num != 5
                        and classifier_res.entities.get("employee_id") != "E09"
                    )
                )
            ):
                if "annual" not in lower_msg and "sales" not in lower_msg:
                    return _router._build_bonus_clarifying_question(role, surface)

            # Agent 2: Retrieval Agent (Deterministic Tools Only — No LLM)
            scenario_num = classifier_res.scenario_num or context.get("scenario_num")
            if not scenario_num:
                if classifier_res.intent == "explain_salary" and ((role == "HR Admin" and "E05" in allowed_emp_ids) or user.get("employee_id") == "E05"):
                    scenario_num = 9
                elif classifier_res.intent == "explain_tds" and ((role == "HR Admin" and "E06" in allowed_emp_ids) or user.get("employee_id") == "E06"):
                    scenario_num = 10
                elif classifier_res.intent == "explain_deduction" and ((role == "HR Admin" and "E16" in allowed_emp_ids) or user.get("employee_id") == "E16"):
                    scenario_num = 11

            bonus_key = None
            if "annual" in lower_msg:
                bonus_key = "annual_performance_bonus"
            elif "sales" in lower_msg:
                bonus_key = "quarterly_sales_incentive"

            retrieval_data = self._execute_retrieval(scenario_num, user_id, bonus_key, raw_msg)
            if not retrieval_data.get("authorized", True):
                if "response" in retrieval_data:
                    return retrieval_data["response"]
                return _router._build_scenario_12(user, role, surface)

            if not retrieval_data.get("cards"):
                # Fallback to deterministic reply for that same intent
                if classifier_res and classifier_res.confidence >= 0.65 and classifier_res.intent in ALLOWED_INTENTS:
                    target_m = classifier_res.entities.get("month") if classifier_res.entities else None
                    if not target_m:
                        for m_name, m_code in [
                            ("january", "2026-01"), ("february", "2026-02"), ("march", "2026-03"),
                            ("april", "2026-04"), ("may", "2026-05"), ("june", "2026-06"),
                            ("july", "2026-07"), ("august", "2026-08"), ("september", "2026-09"),
                            ("october", "2026-10"), ("november", "2026-11"), ("december", "2026-12")
                        ]:
                            if re.search(r"\b" + m_name + r"\b", lower_msg):
                                target_m = m_code
                                break
                    fallback_resp = self._build_deterministic_fallback_for_intent(
                        classifier_res.intent, scenario_num, user, role, surface, bonus_key, month=target_m
                    )
                    if fallback_resp:
                        return fallback_resp
                return _router.handle_chat(user_id=user_id, message=message, action=action, context=context)

            # If this is an FAQ result or FAQ intent, return the deterministic FAQ response directly
            if not scenario_num or retrieval_data.get("state", {}).get("intent") == "faq_question":
                return _router.handle_chat(user_id=user_id, message=message, action=action, context=context)

            facts_list = retrieval_data.get("facts_list", {})
            active_emp_id = facts_list.get("employee_id") or user.get("employee_id")

            # Agent 3: Drafting Agent (LLM: Slot-Based Drafting)
            if self._custom_llm and hasattr(self._custom_llm, "draft"):
                raw_draft = self._custom_llm.draft(raw_msg, facts_list, scenario_num, role)
            else:
                drafting_agent = create_drafting_agent(llm)
                draft_desc = build_draft_task_description(raw_msg, role, facts_list, classifier_res.intent if classifier_res else None, scenario_num)
                draft_task = Task(
                    description=draft_desc,
                    expected_output="Plain text reply with slot tokens and zero digits",
                    agent=drafting_agent
                )
                raw_draft = self._execute_drafting(draft_task, raw_msg, facts_list, scenario_num, role)


            # -------------------------------------------------------------
            # STEP 3: Mechanical Runtime Guards & Server Slot Filling
            # -------------------------------------------------------------
            certainty_lbl = retrieval_data.get("certainty_label") or "Complete for this scope"
            guard_result = _guards.validate_and_fill(
                raw_draft=raw_draft,
                facts_list=facts_list,
                active_employee_id=active_emp_id,
                intent=classifier_res.intent,
                scenario_num=scenario_num,
                certainty_label=certainty_lbl
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
                    latency_ms=(time.time() - start_time) * 1000,
                    tag=run_tag
                )
                if classifier_res.confidence >= 0.65 and classifier_res.intent in ALLOWED_INTENTS:
                    fallback_resp = self._build_deterministic_fallback_for_intent(
                        classifier_res.intent, scenario_num, user, role, surface, bonus_key
                    )
                    if fallback_resp:
                        return fallback_resp

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
                metrics={"used_slots": guard_result.used_slots},
                tag=run_tag
            )

            return response

        except Exception as e:
            # Fallback on any runtime exception or timeout (>20s)
            curr_intent = classifier_res.intent if classifier_res else "unknown"
            curr_sc = scenario_num if scenario_num else (classifier_res.scenario_num if classifier_res else context.get("scenario_num"))
            log_ai_run(
                user_id=user_id,
                role=role,
                surface=surface,
                intent=curr_intent,
                scenario_num=curr_sc,
                guards_result={"execution_error": str(e)},
                fallback_triggered=True,
                fallback_reason=f"Exception in AI Crew: {str(e)}",
                latency_ms=(time.time() - start_time) * 1000,
                tag=run_tag
            )
            if classifier_res and classifier_res.confidence >= 0.65 and classifier_res.intent in ALLOWED_INTENTS:
                target_m = classifier_res.entities.get("month") if classifier_res.entities else None
                fallback_resp = self._build_deterministic_fallback_for_intent(
                    classifier_res.intent, curr_sc, user, role, surface, bonus_key, month=target_m
                )
                if fallback_resp:
                    return fallback_resp

            return _router.handle_chat(user_id=user_id, message=message, action=action, context=context)

    # -------------------------------------------------------------
    # Helper Execution Methods
    # -------------------------------------------------------------

    def _build_deterministic_fallback_for_intent(
        self,
        intent: str,
        scenario_num: Optional[int],
        user: dict,
        role: str,
        surface: str,
        bonus_key: Optional[str] = None,
        month: Optional[str] = None
    ) -> Optional[dict]:
        """Returns the deterministic reply for the identified intent without fresh keyword routing."""
        allowed = set(user.get("allowed_employee_ids") or [])
        target_month = month or "2026-09"
        if intent == "explain_salary":
            if (role == "HR Admin" and "E05" in allowed) or user.get("employee_id") == "E05":
                return _router._build_scenario_9(user, role, surface)
            return _router._build_unknown_fallback(role, surface)
        elif intent == "explain_tds":
            if (role == "HR Admin" and "E06" in allowed) or user.get("employee_id") == "E06":
                return _router._build_scenario_10(user, role, surface)
            return _router._build_unknown_fallback(role, surface)
        elif intent == "explain_deduction":
            if (role == "HR Admin" and "E16" in allowed) or user.get("employee_id") == "E16":
                return _router._build_scenario_11(user, role, surface)
            return _router._build_unknown_fallback(role, surface)
        elif intent in ("prepare_hike", "review_hike"):
            if scenario_num == 2:
                return _router._build_scenario_2(user, role, surface)
            elif scenario_num == 3:
                return _router._build_scenario_3(user, role, surface)
            elif scenario_num == 1:
                return _router._build_scenario_1(user, role, surface)
            return None
        elif intent == "settlement_proposal":
            if scenario_num == 6:
                return _router._build_scenario_6(user, role, surface)
            elif scenario_num == 7:
                return _router._build_scenario_7(user, role, surface)
            elif scenario_num == 8:
                return _router._build_scenario_8(user, role, surface)
            elif scenario_num == 13:
                return _router._build_scenario_13(user, role, surface)
            return None
        elif intent == "settlement_review":
            return _router._build_scenario_13(user, role, surface)
        elif intent == "payslip_breakdown":
            return _router._build_payslip_breakdown(user, role, surface, month=target_month)
        elif intent == "pf_amount":
            return _router._build_pf_amount(user, role, surface, month=target_month)
        elif intent == "tds_amount":
            return _router._build_tds_amount(user, role, surface, month=target_month)
        elif intent == "lop_days":
            return _router._build_lop_days(user, role, surface, month=target_month)
        elif intent == "compare_months":
            return _router._build_compare_months(user, role, surface)
        elif intent == "query_status":
            return _router._handle_query_status(user, role, surface, {})
        elif intent == "tax_regime":
            return _router._build_tax_regime(user, role, surface)
        elif intent == "unrecorded_topic":
            return _router._build_unrecorded_topic(user, role, surface)
        elif intent == "unrecorded_month":
            return _router._build_unrecorded_month(user, role, surface)
        return None

    def _execute_classifier(self, task: Task, message: str, role: str, user: dict, context: dict) -> ClassifierOutput:
        """Executes Classifier task and validates output."""
        lower_msg = message.lower()

        # If custom LLM is a mock or callable, use it; otherwise run task
        if self._custom_llm and hasattr(self._custom_llm, "classify"):
            raw_out = self._custom_llm.classify(message, role, context)
            res = validate_classifier_output(raw_out, user)
            if res.intent == "explain_salary" and not res.scenario_num:
                res.scenario_num = 9
            return res

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
                res = validate_classifier_output(raw_json, user)
                if res.intent == "explain_salary" and not res.scenario_num:
                    res.scenario_num = 9
                return res
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
        if "meera" in lower_msg:
            return validate_classifier_output({"intent": "bonus_proposal", "scenario_num": 5, "entities": {"employee_name": "Meera Nair"}}, user)
        if "bonus" in lower_msg:
            return validate_classifier_output({"intent": "bonus_proposal", "scenario_num": 4}, user)
        if "rahul" in lower_msg:
            return validate_classifier_output({"intent": "settlement_proposal", "scenario_num": 6, "entities": {"employee_name": "Rahul Verma"}}, user)
        if "lakshmi" in lower_msg:
            return validate_classifier_output({"intent": "settlement_proposal", "scenario_num": 7, "entities": {"employee_name": "Lakshmi Reddy"}}, user)
        if "imran" in lower_msg:
            return validate_classifier_output({"intent": "settlement_proposal", "scenario_num": 8, "entities": {"employee_name": "Imran Khan"}}, user)

        # Tax advice out of scope
        if re.search(r"\b(tax\s+)?regime\b.*\b(choose|select|recommend|advise|better)\b|\b(recommend|advise|suggestion|suggest|should i choose|choose|is better to choose)\b.*(\btax\s+)?regime\b|\b(tax\s+)?investment\b|\bhow (can|to|do) (i )?save tax\b|\bshould i choose (new|old)\b|\bwhich regime should i choose\b", lower_msg):
            return validate_classifier_output({"intent": "out_of_scope", "scenario_num": None}, user)

        if (lower_msg.startswith("what is") or lower_msg.startswith("what are") or "faq" in lower_msg) and not faq_matcher.is_personal_pay_question(lower_msg):
            return validate_classifier_output({"intent": "faq_question", "scenario_num": None}, user)

        # Part C intents for signed-in employee
        if role == "Employee":
            if bool(re.search(r"\b(bonus|incentive)\b", lower_msg)) or bool(re.search(r"\b(ctc|leave balance|remaining leave|reimbursement|claim|salary credit date|when.*salary.*credit|when.*pay.*credit|form 16|pf balance)\b", lower_msg)) or (re.search(r"\b(hike|arrears)\b", lower_msg) and not any(k in lower_msg for k in ("priya", "arjun", "kavya"))):
                return validate_classifier_output({"intent": "unrecorded_topic", "scenario_num": None}, user)

            if re.search(r"\bcompare\b.*\b(august|september|months|pay|salary)\b|\bcompare\b", lower_msg):
                return validate_classifier_output({"intent": "compare_months", "scenario_num": None}, user)

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
                from ..chat_router import get_employee_ledger_months
                emp_id = user.get("employee_id") or "E05"
                ledger_months = get_employee_ledger_months(emp_id)
                if m_code not in ledger_months:
                    if any(k in lower_msg for k in ("pay", "salary", "payslip", "pf", "tds", "tax", "lop", "breakdown")) or "what is my" in lower_msg or "explain" in lower_msg:
                        return validate_classifier_output({"intent": "unrecorded_month", "scenario_num": None, "entities": {"month": m_code}}, user)
                else:
                    is_salary_drop = bool(re.search(
                        r"\b(why is my salary less|why did i get less|why is my pay less|less this month|salary.*less|pay.*less|take-home.*less|cut in.*salary|salary.*drop|take-home.*lower)\b",
                        lower_msg
                    )) or (("take-home" in lower_msg or "salary" in lower_msg or "payslip" in lower_msg) and ("lower" in lower_msg or "drop" in lower_msg or "less" in lower_msg))

                    is_tds_increase = ("tds" in lower_msg and ("increase" in lower_msg or "higher" in lower_msg or "more" in lower_msg))
                    is_basic_allowance = ("basic pay" in lower_msg or "allowance" in lower_msg or "gross did not change" in lower_msg or ("change" in lower_msg and "allowance" in lower_msg))

                    if is_salary_drop and (user.get("employee_id") == "E05" or (role == "HR Admin" and "E05" in allowed)):
                        return validate_classifier_output({"intent": "explain_salary", "scenario_num": 9, "entities": {"month": m_code}}, user)
                    elif is_tds_increase and (user.get("employee_id") == "E06" or (role == "HR Admin" and "E06" in allowed)):
                        return validate_classifier_output({"intent": "explain_tds", "scenario_num": 10, "entities": {"month": m_code}}, user)
                    elif is_basic_allowance and (user.get("employee_id") == "E16" or (role == "HR Admin" and "E16" in allowed)):
                        return validate_classifier_output({"intent": "explain_deduction", "scenario_num": 11, "entities": {"month": m_code}}, user)
                    elif "pf" in lower_msg:
                        return validate_classifier_output({"intent": "pf_amount", "scenario_num": None, "entities": {"month": m_code}}, user)
                    elif "tds" in lower_msg or ("tax" in lower_msg and "regime" not in lower_msg):
                        return validate_classifier_output({"intent": "tds_amount", "scenario_num": None, "entities": {"month": m_code}}, user)
                    elif "lop" in lower_msg:
                        return validate_classifier_output({"intent": "lop_days", "scenario_num": None, "entities": {"month": m_code}}, user)
                    elif any(k in lower_msg for k in ("pay", "salary", "payslip", "breakdown")) or "explain" in lower_msg:
                        return validate_classifier_output({"intent": "payslip_breakdown", "scenario_num": None, "entities": {"month": m_code}}, user)

            if re.search(r"\b(which|what)\b.*\btax regime\b.*\b(am i in|do i have|on my record|in my record)\b|\bwhich tax regime am i in\b|\bwhat is my tax regime\b|\bregime am i in\b|\bmy tax regime\b", lower_msg) and not ("choose" in lower_msg or "recommend" in lower_msg or "better" in lower_msg or "advise" in lower_msg):
                return validate_classifier_output({"intent": "tax_regime", "scenario_num": None}, user)
            if re.search(r"what('s| is) happening with my query\b|\b(track.*query|status of.*query)\b", lower_msg):
                return validate_classifier_output({"intent": "query_status", "scenario_num": None}, user)
            if (re.search(r"\bwhy is my tds zero\b|\btds zero\b|\bwhy.*zero.*tds\b|\bwhy.*no tds\b|\bhow much (tax|tds)\b|\bwhat is my (tax|tds)\b|\btax was cut\b|\bcut in tax\b|\btax cut\b", lower_msg) or (lower_msg.strip() in ("tds", "my tds") and user.get("employee_id") != "E06")) and not ("increase" in lower_msg or "higher" in lower_msg or "more" in lower_msg):
                return validate_classifier_output({"intent": "tds_amount", "scenario_num": None}, user)
            if re.search(r"\b(how many|why was there|why.*is there|why.*lop)\b.*\blop\b|\blop days\b|\bloss of pay days\b|\bhow many.*unpaid\b", lower_msg):
                return validate_classifier_output({"intent": "lop_days", "scenario_num": None}, user)
            if re.search(r"\b(how much|hw much|amount of|cut in)\b.*\bpf\b|\bmy pf\b|\bpf amount\b|\bpf was cut\b|\bhw much pf\b", lower_msg):
                return validate_classifier_output({"intent": "pf_amount", "scenario_num": None}, user)
            if re.search(r"\bexplain my (september|august) pay\b|\b(september|august) (payslip|breakdown|pay breakdown)\b|\b(payslip|pay) breakdown\b|\bexplain my pay\b", lower_msg):
                return validate_classifier_output({"intent": "payslip_breakdown", "scenario_num": None}, user)

        # Casual phrasings and personal pay queries for Neha / salary explanation
        allowed = set(user.get("allowed_employee_ids") or [])
        is_salary_drop = bool(re.search(
            r"\b(why is my salary less|why did i get less|why is my pay less|less this month|salary.*less|pay.*less|take-home.*less|cut in.*salary|salary.*drop|take-home.*lower)\b",
            lower_msg
        ))
        if is_salary_drop or "september" in lower_msg or "take-home" in lower_msg or "drop" in lower_msg or "less" in lower_msg:
            sc = 9 if ((role == "HR Admin" and "E05" in allowed) or user.get("employee_id") == "E05") else None
            return validate_classifier_output({"intent": "explain_salary", "scenario_num": sc}, user)
        if "tds" in lower_msg or "tax" in lower_msg:
            sc = 10 if ((role == "HR Admin" and "E06" in allowed) or user.get("employee_id") == "E06") else None
            return validate_classifier_output({"intent": "explain_tds", "scenario_num": sc}, user)
        if "gross" in lower_msg:
            sc = 11 if ((role == "HR Admin" and "E16" in allowed) or user.get("employee_id") == "E16") else None
            return validate_classifier_output({"intent": "explain_deduction", "scenario_num": sc}, user)

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

        return {"authorized": True, "cards": [], "chips": [], "state": {"intent": "unknown"}, "facts_list": {}}

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
                return "Your {later_month} take-home pay changed by {net_change} compared to {earlier_month}. Loss of Pay was {lop_amount} and the PF ceiling change was {pf_change}."
            elif scenario_num == 10:
                return "Your {later_month} take-home pay changed by {net_change} compared to {earlier_month}. TDS increased by {tds_increase} and the PF ceiling change was {pf_change}."
            elif scenario_num == 11:
                return "Your {later_month} take-home pay changed by {net_change} compared to {earlier_month}. The PF ceiling change was {pf_change}."
            elif scenario_num == 1:
                return "This is a proposal for the recorded hike for {employee_name} for {period}. Gross arrears are {gross_arrears}."
            elif scenario_num == 4:
                return "This is a proposal for the recorded {bonus_type} for {period}. Known eligible gross is {known_eligible_gross}."
            return "Here are the recorded payroll calculation details for your review."


ai_crew = PayrollAICrew()
