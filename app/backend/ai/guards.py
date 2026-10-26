"""Purely mechanical runtime guards for HCM One AI replies.
No subjective evaluation (tone/helpfulness) is performed at runtime.
All checks are deterministic regex, string parsing, set membership, or length boundaries.
"""
import re
from typing import Dict, List, Optional, Set, Tuple
from pydantic import BaseModel

from .facts import extract_numbers_from_facts


FORBIDDEN_INVENTED_CONCEPTS = [
    "professional tax",
    "pt deduction",
    "Notice shortfall recovery & known deductions",
]

BANNED_INTERNAL_TERMS = [
    "engine_bridge",
    "chatrouter",
    "crewai",
    "system prompt",
    "developer mode",
    "agent 06",
    "instructions",
]

FORBIDDEN_POLICY_PATTERNS = [
    # Payment claims
    r"\b(has been paid|money was paid|credited to your|transferred to your|deposited in your|disbursed to your)\b",
    r"\b(we have paid|i have paid|already paid into bank)\b",
    # Tax regime recommendation / personal advice
    r"\b(recommend.*tax regime|should choose.*regime|you should opt for.*(old|new) regime)\b",
    r"\b(invest in.*(80c|80d|nps)|save tax by investing)\b",
    # Approval claims
    r"\b(i have approved|i approved this|proposal is approved by me|i hereby approve)\b",
    # Promise of future pay
    r"\b(your next month.*(will be|is guaranteed)|i promise next month)\b"
]


class GuardResult(BaseModel):
    passed: bool
    failed_guard: Optional[str] = None
    error_message: Optional[str] = None
    filled_text: Optional[str] = None
    used_slots: List[str] = []


class RuntimeGuardPipeline:
    def __init__(self, employee_names_map: Optional[Dict[str, str]] = None):
        self.employee_names_map = employee_names_map or {}

    def validate_and_fill(
        self,
        raw_draft: str,
        facts_list: Dict[str, str],
        active_employee_id: Optional[str] = None
    ) -> GuardResult:
        """Runs the 7 mechanical runtime guards and performs server slot interpolation.
        Returns GuardResult with passed=True and filled_text on success.
        """
        raw_draft = (raw_draft or "").strip()
        if not raw_draft:
            return GuardResult(passed=False, failed_guard="EmptyDraftGuard", error_message="Draft is empty.")

        # Guard 1: Zero Digits Guard (Before slot filling)
        # The Drafting agent must never type digits [0-9]
        if re.search(r"\d", raw_draft):
            digit_match = re.search(r"\d+", raw_draft)
            found_digit = digit_match.group(0) if digit_match else "digit"
            return GuardResult(
                passed=False,
                failed_guard="ZeroDigitsGuard",
                error_message=f"Draft contains raw digit '{found_digit}'. AI must write named slots only."
            )

        # Guard 2: Slot Whitelist Guard
        # All {slot} tokens must exist in facts_list for this reply
        slot_tokens = re.findall(r"\{([a-zA-Z0-9_]+)\}", raw_draft)
        for slot in slot_tokens:
            if slot not in facts_list:
                return GuardResult(
                    passed=False,
                    failed_guard="SlotWhitelistGuard",
                    error_message=f"Unknown slot '{{{slot}}}' not found in turn facts list."
                )

        # Guard 3: Concept & Banned Terms Guard (on raw draft)
        lower_raw = raw_draft.lower()
        for forbidden in FORBIDDEN_INVENTED_CONCEPTS:
            if forbidden.lower() in lower_raw:
                return GuardResult(
                    passed=False,
                    failed_guard="ConceptGuard",
                    error_message=f"Forbidden invented concept '{forbidden}' detected in draft."
                )
        for banned in BANNED_INTERNAL_TERMS:
            if banned.lower() in lower_raw:
                return GuardResult(
                    passed=False,
                    failed_guard="BannedTermsGuard",
                    error_message=f"Banned internal term '{banned}' detected in draft."
                )

        # Guard 4: Policy & Paraphrasing Guard (on raw draft)
        for pat in FORBIDDEN_POLICY_PATTERNS:
            if re.search(pat, lower_raw):
                return GuardResult(
                    passed=False,
                    failed_guard="PolicyParaphraseGuard",
                    error_message=f"Prohibited policy/payment phrasing matched pattern '{pat}'."
                )

        # Server Slot Interpolation
        filled_text = raw_draft
        for slot in slot_tokens:
            val = str(facts_list.get(slot, ""))
            filled_text = filled_text.replace(f"{{{slot}}}", val)

        # Guard 5: Scoped Number Provenance Guard (Second safety net on filled text)
        facts_numbers, facts_dates = extract_numbers_from_facts(facts_list)

        # Extract numbers from filled text (₹ amounts, plain grouped numbers, percentages)
        filled_numbers: Set[float | int] = set()
        for m in re.finditer(r"[−\-]?\s*₹?\s*([0-9]{1,3}(?:,[0-9]{2,3})*(?:\.[0-9]+)?|[0-9]+(?:\.[0-9]+)?)", filled_text):
            clean = m.group(1).replace(",", "")
            try:
                num = float(clean)
                n_val = int(num) if num.is_integer() else num
                filled_numbers.add(n_val)
            except ValueError:
                pass

        for m in re.finditer(r"(\d+(?:\.\d+)?)\s*%", filled_text):
            try:
                num = float(m.group(1))
                filled_numbers.add(int(num) if num.is_integer() else num)
            except ValueError:
                pass

        for fn in filled_numbers:
            # Check positive or negative presence
            if (fn not in facts_numbers) and (-fn not in facts_numbers):
                return GuardResult(
                    passed=False,
                    failed_guard="ScopedNumberProvenanceGuard",
                    error_message=f"Number '{fn}' in filled text does not exist in this reply's facts list."
                )

        # Guard 6: Entity & Employee Name Guard
        # If an employee name is mentioned, verify against active employee ID
        if active_employee_id and active_employee_id in self.employee_names_map:
            expected_name = self.employee_names_map[active_employee_id]
            # Verify if other employee names from the directory are improperly referenced
            for other_id, other_name in self.employee_names_map.items():
                if other_id != active_employee_id:
                    if other_name.lower() in filled_text.lower():
                        return GuardResult(
                            passed=False,
                            failed_guard="EntityNameGuard",
                            error_message=f"Name '{other_name}' (ID {other_id}) improperly referenced in context of {expected_name}."
                        )

        # Guard 7: Mechanical Length Guard (1 to 3 sentences, maximum 60 words)
        words = filled_text.split()
        if len(words) > 60:
            return GuardResult(
                passed=False,
                failed_guard="LengthGuard",
                error_message=f"Word count ({len(words)}) exceeds maximum 60 words."
            )

        # Sentence counting: split by sentence delimiters
        sentences = [s.strip() for s in re.split(r"[.!?]+", filled_text) if s.strip()]
        if not (1 <= len(sentences) <= 3):
            return GuardResult(
                passed=False,
                failed_guard="LengthGuard",
                error_message=f"Sentence count ({len(sentences)}) must be between 1 and 3."
            )

        # All mechanical guards passed!
        return GuardResult(
            passed=True,
            filled_text=filled_text,
            used_slots=slot_tokens
        )


runtime_guards = RuntimeGuardPipeline()
