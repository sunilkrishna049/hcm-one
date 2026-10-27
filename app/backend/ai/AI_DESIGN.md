# HCM One AI Layer Architecture & Design Specification
**Option B: Guarded Natural Replies with CrewAI Agent Crew (Slot-Based Drafting & Mechanical Guards)**

- **Document Version:** 1.1.0
- **Status:** Approved Architecture Plan (PLAN ONLY — NO CODE)
- **Branch:** `ai-crew`
- **Date:** 2026-10-26
- **Governing Directives:** Project Owner Decisions (Option B & DEC-041), `app/backend/chat_contract.md`, `output/06-ai-interaction/`, `output/07-prototype/screen-specs.md`, `project-memory/design-decisions.md` (DEC-011 through DEC-041).

---

## 1. Executive Summary & Core Invariants

The HCM One AI layer introduces natural language understanding and natural 1–3 sentence responses to the `/api/chat` conversational interface while maintaining **100% adherence to the existing UI/API contract (`chat_contract.md`)**. 

Under **DEC-041 (Guarded Natural Replies with Slot-Based Drafting)**:
1. **Zero Digits Typed by AI:** The AI Drafting agent *never* writes numbers, amounts, percentages, or dates. It writes named slots (e.g. `{net_change}`, `{later_month}`) chosen strictly from a `facts_list` supplied by the tools specifically for *this reply*.
2. **Server Slot Filling:** The backend server safely replaces valid slots with formatted engine values (e.g., `₹5,420`). Any unknown slot or any raw digit (`[0-9]`) typed by the AI immediately fails the guard and triggers deterministic fallback.
3. **Server-Appended Critical Sentences:** The server itself appends approved compliance and governance statements (`C01` AI identity, `C04` approval != payment, `C10` permission denied, `C11` tax advice limits, `C09`/`C17`/`C25` failure stops, and engine certainty labels). The AI does not write them; the guard checks that the AI does not paraphrase them.
4. **Latency Budget & Selective LLM Calls:** Only the Classifier and Drafting agents call the LLM (`gpt-4o-mini`, temperature 0.1). Retrieval and Escalation are CrewAI agents that execute *deterministic tools only* with zero LLM reasoning. Execution timeout is **20 seconds**. The UI renders a clear `"Thinking…"` loading indicator.
5. **Purely Mechanical Runtime Guards:** Runtime guards evaluate only objective, programmatic conditions: slot whitelist, zero digits, provenance against *this reply's* facts list, employee names, forbidden concepts, banned terms, policy wording, and length (1 to 3 sentences, maximum 60 words). Tone and helpfulness are evaluated offline, not at runtime.
6. **Deterministic Fallback:** If any guard fails, or if an error or timeout (>20s) occurs, the user immediately receives the deterministic router's reply (`ChatRouter.handle_chat()`). The user experiences zero breakage.
7. **Permissions & Data Minimization:** RBAC is checked on the server before any tool runs. Scenario 12 (cross-employee salary inquiries) is blocked at the gate without invoking the AI crew. Zero PAN, bank details, or unauthorized records are ever sent to an external model.

---

## 2. Architecture Diagram & End-to-End Request Lifecycle

### 2.1 System Architecture Flow

```
                               POST /api/chat
                                     │
                                     ▼
                       ┌───────────────────────────┐
                       │   FastAPI Chat Ingress    │
                       │   (app/backend/main.py)   │
                       └─────────────┬─────────────┘
                                     │
                                     ▼
        ┌────────────────────────────────────────────────────────┐
        │ INPUT-SIDE PIPELINE (Before any LLM call)              │
        │ 1. Authentication & Role Check (auth.py)               │
        │ 2. Load ONLY this user's authorized data               │
        │    (Scenario 12: Cross-employee access blocked!)       │
        │ 3. Prompt-Injection Check (Regex / Heuristic guard)    │
        └────────────────────────────┬───────────────────────────┘
                                     │
                        Unauthorized │ Authorized &
                        / Injection  │ Safe
                        ┌────────────┴────────────┐
                        ▼                         ▼
               ┌─────────────────┐      ┌─────────────────────────┐
               │ Return C10 /    │      │ Check AI_MODE (.env)    │
               │ Hard Refusal    │      └────────────┬────────────┘
               └─────────────────┘                   │
                                    AI_MODE=false    │ AI_MODE=true
                                    ┌────────────────┴────────────────┐
                                    ▼                                 ▼
                          ┌───────────────────┐             ┌───────────────────┐
                          │  Deterministic    │             │   CrewAI 4-Agent  │
                          │   ChatRouter      │             │  Crew (20s limit) │
                          └─────────┬─────────┘             └─────────┬─────────┘
                                    │                                 │
                                    │      ┌──────────────────────────┴──────────────────────────┐
                                    │      │ 1. Classifier Agent (LLM: intent, entities; NO DIGITS)
                                    │      │    - Deterministic Output Validation:
                                    │      │      * Intent must match allowed intents
                                    │      │      * Names resolved to IDs by code (not LLM)
                                    │      │      * Low confidence / ambiguous -> Clarifying card
                                    │      │ 2. Retrieval Agent (Deterministic Tools: cards + facts_list)
                                    │      │    - Facts formatted from engine with signs (-₹420)
                                    │      │ 3. Drafting Agent (LLM: 1-3 sentences, SLOTS ONLY, NO DIGITS)
                                    │      │ 4. Escalation Agent (Deterministic Tools: action chips)
                                    │      └──────────────────────────┬──────────────────────────┘

                                    │                                 │
                                    │                                 ▼
                                    │                       ┌───────────────────┐
                                    │                       │  Pre-Fill Guards  │
                                    │                       │ (Zero Digits,     │
                                    │                       │  Slot Whitelist)  │
                                    │                       └─────────┬─────────┘
                                    │                                 │ Pass
                                    │                                 ▼
                                    │                       ┌───────────────────┐
                                    │                       │ Server Slot Fill  │
                                    │                       │ (facts_list values│
                                    │                       └─────────┬─────────┘
                                    │                                 │
                                    │                                 ▼
                                    │                       ┌───────────────────┐
                                    │                       │ Post-Fill Guards  │
                                    │                       │ (Provenance, Name,│
                                    │                       │  Policy, Length)  │
                                    │                       └─────────┬─────────┘
                                    │                                 │ Pass
                                    │                                 ▼
                                    │                       ┌───────────────────┐
                                    │                       │ Server Sentence   │
                                    │                       │ Appender (C04/C30)│
                                    │                       └─────────┬─────────┘
                                    │                                 │
                                    │          Guard Failure /        │ All Guards
                                    │          Timeout (>20s) / Error │ Passed
                                    │          ┌──────────────────────┴───────────┐
                                    ▼          ▼                                  ▼
                          ┌─────────────────────────────┐               ┌───────────────────┐
                          │  Deterministic Fallback     │               │ Guarded Natural   │
                          │   (chat_router.py result)   │               │   AI Response     │
                          └──────────────┬──────────────┘               └─────────┬─────────┘
                                         │                                        │
                                         └───────────────────┬────────────────────┘
                                                             │
                                                             ▼
                                               ┌───────────────────────────┐
                                               │ Masked Audit Logger       │
                                               │ (data/runtime/ai_runs)    │
                                               └─────────────┬─────────────┘
                                                             │
                                                             ▼
                                                   Serialized JSON Response
                                                    (chat_contract.md)
```

### 2.2 End-to-End Request Steps
1. **Intake & UI Loading:** Client posts to `/api/chat`. The chat UI instantly shows a `"Thinking…"` loading state.
2. **Pre-AI Authorization Gate:** If an employee asks about another employee's salary (Scenario 12), the server immediately returns pre-approved refusal `C10` without invoking CrewAI.
3. **CrewAI Pipeline (20s Deadline):**
   - **Classifier Agent (LLM):** Categorizes query into structured intent and entities (English only). Never extracts or emits numbers.
   - **Retrieval Agent (Deterministic Tools):** Calls existing scenario/FAQ builders; packages structured cards, panel data, and a turn-specific `facts_list` (whitelist of allowed slots and formatted strings).
   - **Drafting Agent (LLM):** Generates 1 to 3 sentences (max 60 words) using natural phrasing and slot tags `{...}`. Contains zero digits.
   - **Escalation Agent (Deterministic Tools):** Sets suggestion chips and ensures state mutation actions (Approve, Send, Resolve) require explicit human button clicks.
4. **Mechanical Pre-Fill Guards:** Verifies that AI draft contains 0 raw digits (`\d`) and all `{slot}` names exist in `facts_list`.
5. **Server Slot Filling:** The server interpolates slot values from `facts_list`.
6. **Mechanical Post-Fill Guards:** Validates number provenance against *this reply's facts list*, employee name spelling, forbidden concepts, banned terms, policy/paraphrasing checks, and length (<= 60 words).
7. **Server Sentence Appending:** Appends mandatory approved sentences (`C04`, `C10`, `C11`, etc.) and engine certainty labels directly from backend constants.
8. **Fallback Interceptor:** If any check fails, or on timeout (>20s), immediately returns deterministic `ChatRouter.handle_chat()` output.
9. **Masked Audit Logging:** Records intent, execution latency, guard results, token counts, and fallback status in `data/runtime/ai_runs.jsonl`.

---

## 3. The 4 CrewAI Agents (Course Pattern)

```
┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐
│ 1. Classifier    │ ───> │ 2. Retrieval     │ ───> │ 3. Drafting      │ ───> │ 4. Escalation    │
│ (Uses LLM)       │      │ (Deterministic   │      │ (Uses LLM)       │      │ (Deterministic   │
│ Intent, Entities │      │  Tools Only)     │      │ Slots Only!      │      │  Tools Only)     │
│ Zero Numbers!    │      │ Cards+facts_list │      │ Zero Digits!     │      │ Human Click Gate │
└──────────────────┘      └──────────────────┘      └──────────────────┘      └──────────────────┘
```

### 3.1 Agent 1: Classifier Agent (LLM Enabled)
- **Role:** HCM One Payroll Intent Classifier
- **Goal:** Accurately classify user queries into structured intents and entities without generating or extracting numbers.
- **Execution Mode:** Invokes LLM (`gpt-4o-mini`, temperature=0.1, max_tokens=100).
- **Language Scope:**
  - English only (Approved by: Project owner). Understands standard and casual enterprise English phrasing:
    * *"Review back-dated hike for Arjun Rao"* -> `review_hike`, Scenario 2
    * *"Why is my September take-home pay lower than August?"* -> `explain_salary`, Scenario 9
    * *"Why did my take-home pay decrease when my gross did not change?"* -> `explain_deduction`, Scenario 11
    * *"Prepare quarterly bonus run for Hyderabad sales team"* -> `bonus_proposal`, Scenario 4
- **Prompt Injection Guard:** Sets `is_prompt_injection=True` on jailbreak or system prompt queries.
- **Output (Pydantic Model):**
  ```python
  class ClassifierOutput(BaseModel):
      intent: str
      scenario_num: Optional[int]
      entities: Dict[str, Optional[str]]  # employee_name, month, bonus_type
      confidence: float
      is_prompt_injection: bool
      clarification_needed: bool
  ```
- **Deterministic Classifier Output Validation:**
  - `intent` must be one of the strictly allowed intents: `prepare_hike`, `review_hike`, `bonus_proposal`, `settlement_proposal`, `settlement_review`, `explain_salary`, `explain_tds`, `explain_deduction`, `faq_query`, `query_flow`, `out_of_scope`, `prompt_injection`, `unknown`.
  - Employee names are resolved to IDs strictly by **deterministic code with role checks** (never by the LLM).
  - If confidence is low or the request is ambiguous (e.g. bonus without type), the system renders the `clarifying_question` card instead of guessing.
- **Invariant:** Emits **ZERO numbers**.

### 3.2 Agent 2: Retrieval Agent (Deterministic Tools Only — No LLM)
- **Role:** Deterministic Payroll Data Retriever
- **Goal:** Fetch exact cards, formulas, citations, and the scoped `facts_list` for this specific turn.
- **Execution Mode:** Deterministic CrewAI agent (`llm=None` / zero LLM reasoning). Invokes Python tools directly.
- **Facts List Formatting Rule:**
  - Facts list values are copied **exactly as formatted from engine output, including signs** (e.g. the PF effect is `−₹420`, not `₹420`; net change is `−₹5,420`).
- **Output Payload:**
  ```python
  class RetrievalOutput(BaseModel):
      scenario_num: Optional[int]
      cards: List[dict]
      chips: List[dict]
      panel_data: dict
      certainty_label: str
      facts_list: Dict[str, str]  # Scoped slots & formatted engine strings for THIS reply (with signs)
  ```
- **Invariant:** Never estimates, calculates, or rounds numbers.


### 3.3 Agent 3: Drafting Agent (LLM Enabled — Slot-Based Drafting)
- **Role:** HCM One Slot-Based Communications Drafter
- **Goal:** Write a natural, calm explanation of 1 to 3 sentences (max 60 words) using exclusively slot tokens `{slot_name}` from `facts_list`.
- **Execution Mode:** Invokes LLM (`gpt-4o-mini`, temperature=0.1, max_tokens=120).
- **Hard Constraints:**
  - **Zero Digits Rule:** Must never type digits (`0-9`). Any character in `0-9` fails Guard 2 immediately.
  - **Slot Whitelist Rule:** May only use slots provided in the turn's `facts_list`. Any unrecognized `{...}` fails Guard 1 immediately.
  - **No Paraphrasing of Critical Sentences:** Must not write or paraphrase payment claims, approval grants, tax advice, or permission disclaimers.
- **Output:**
  ```python
  class DraftingOutput(BaseModel):
      raw_draft_with_slots: str  # e.g., "Your {later_month} take-home pay is {net_change} {net_change_direction} than {earlier_month}."
      used_slots: List[str]
  ```

### 3.4 Agent 4: Escalation Agent (Deterministic Tools Only — No LLM)
- **Role:** Human Governance and Action Router
- **Goal:** Configure action chips and human review gates based on certainty labels and query status.
- **Execution Mode:** Deterministic CrewAI agent (`llm=None` / zero LLM reasoning).
- **Rules:**
  - Suggests action chips (e.g. `"Approve proposal"`, `"Draft a query for HR"`).
  - **Zero Auto-Execution:** Never performs actions automatically. Approval, sending, and resolving require explicit user button clicks.

---

## 4. Concrete Example: Scenario 9 (Slot Drafting & Server Filling)

### 4.1 Input Context
- **User:** `USER-E05` (Neha Gupta)
- **Query:** *"Why is my take-home pay lower in September?"*
- **Scenario:** Scenario 9 (`data/generated/scenarios/scenario-09.json`)

### 4.2 Facts List Supplied by Retrieval Tool for this Reply
```json
{
  "employee_first_name": "Neha",
  "earlier_month": "August",
  "later_month": "September",
  "net_change": "₹5,420",
  "net_change_direction": "lower",
  "after_net": "₹42,780",
  "before_net": "₹48,200",
  "lop_days": "3",
  "lop_amount": "−₹5,000",
  "pf_change": "₹420",
  "primary_reason": "Loss of Pay (LOP)",
  "secondary_reason": "PF ceiling change"
}
```

### 4.3 Raw AI Draft with Slots (Zero Digits!)
```
Your {later_month} take-home pay is {net_change} {net_change_direction} than {earlier_month}. This change is primarily due to {lop_days} days of unpaid leave and the revised PF ceiling.
```
*Note: The AI draft contains exactly 0 digits (`\d`). It references only valid slots from `facts_list`.*

### 4.4 Server-Filled Version
```
Your September take-home pay is ₹5,420 lower than August. This change is primarily due to 3 days of unpaid leave and the revised PF ceiling.
```

### 4.5 Server-Appended Critical Sentences & Contract Output
The server appends the follow-up prompt `C27` and renders the exact contract cards:
```json
{
  "messages": [
    {
      "code": "AI",
      "text": "Your September take-home pay is ₹5,420 lower than August. This change is primarily due to 3 days of unpaid leave and the revised PF ceiling."
    },
    {
      "code": "C27",
      "text": "Would you like the earnings and deductions breakdown?"
    }
  ],
  "cards": [
    {
      "id": "card-hero-s9",
      "type": "number_hero",
      "title": "Take-Home Pay Comparison",
      "certainty": "Complete for this scope",
      "data": {
        "hero_label": "September Take-Home",
        "hero_amount": 42780,
        "net_change": -5420,
        "previous_month_label": "August Take-Home",
        "previous_month_amount": 48200
      }
    },
    {
      "id": "card-reasons-s9",
      "type": "reason_list",
      "title": "Ranked by effect on take-home pay",
      "certainty": "Complete for this scope",
      "data": {
        "net_change": -5420,
        "reasons": [
          {"cause": "Loss of Pay (LOP)", "detail": "3 days unpaid leave", "amount": -5000},
          {"cause": "PF ceiling change", "detail": "Revised ceiling from 17 Sep", "amount": -420}
        ],
        "tds_change": 0
      }
    }
  ],
  "chips": [
    {"label": "Show calculation", "action": "show-calculation", "payload": {"scenario_num": 9}},
    {"label": "Draft a query for HR", "action": "draft-query", "payload": {"employee_id": "E05", "period": "2026-09"}}
  ],
  "state": {
    "intent": "explain_salary",
    "scenario_num": 9,
    "role": "Employee",
    "surface": "CHAT-EMP",
    "employee_id": "E05"
  }
}
```

---

## 5. The Purely Mechanical Runtime Guard Pipeline

Runtime guards are **100% mechanical**. They execute deterministic string matching, regex scans, and set operations. No subjective evaluation (such as tone or helpfulness) is executed at runtime.

```
                  Raw AI Draft with Slots
                            │
                            ▼
     ┌──────────────────────────────────────────────┐
     │ Guard 1: Slot Whitelist Guard                │
     │ Regex extracts all {slot} tokens.            │
     │ All slots MUST exist in turn's facts_list!   │
     └──────────────────────┬───────────────────────┘
                            │ Pass
                            ▼
     ┌──────────────────────────────────────────────┐
     │ Guard 2: Zero Digits Guard                   │
     │ Scans draft for any raw digit: [0-9].        │
     │ MUST CONTAIN ZERO DIGITS!                    │
     └──────────────────────┬───────────────────────┘
                            │ Pass
                            ▼
     ┌──────────────────────────────────────────────┐
     │ Server Slot Interpolation                    │
     │ Fills {slot} tokens using facts_list values. │
     └──────────────────────┬───────────────────────┘
                            │
                            ▼
     ┌──────────────────────────────────────────────┐
     │ Guard 3: Scoped Number Provenance Guard      │
     │ Second safety net: verifies filled numbers   │
     │ match numbers in THIS reply's facts_list.    │
     └──────────────────────┬───────────────────────┘
                            │ Pass
                            ▼
     ┌──────────────────────────────────────────────┐
     │ Guard 4: Entity & Employee Name Guard        │
     │ All employee names in text must match        │
     │ data/mock/employees.json for that ID.        │
     └──────────────────────┬───────────────────────┘
                            │ Pass
                            ▼
     ┌──────────────────────────────────────────────┐
     │ Guard 5: Concept & Banned Terms Guard        │
     │ Banned: "professional tax", "pt deduction",  │
     │ internal terms ("engine_bridge", "prompt").  │
     └──────────────────────┬───────────────────────┘
                            │ Pass
                            ▼
     ┌──────────────────────────────────────────────┐
     │ Guard 6: Policy & Paraphrasing Guard         │
     │ Rejects payment claims ("paid", "credited"), │
     │ tax advice ("choose new regime"), approval   │
     │ grants, or unauthorized permissions.        │
     └──────────────────────┬───────────────────────┘
                            │ Pass
                            ▼
     ┌──────────────────────────────────────────────┐
     │ Guard 7: Length Guard                        │
     │ Exactly 1 to 3 sentences; maximum 60 words.  │
     └──────────────────────┬───────────────────────┘
                            │ Pass
                            ▼
     ┌──────────────────────────────────────────────┐
     │ Server Sentence Appender                     │
     │ Server appends approved statements (C04/C10) │
     │ and engine certainty labels directly.        │
     └──────────────────────┬───────────────────────┘
                            │
            ┌───────────────┴───────────────┐
            │ All Passed                    │ Any Guard Failed
            ▼                               ▼
     Serve Guarded AI Response       Trigger Deterministic Fallback!
                                     Log: [GUARD_FAILED: Guard Name]
                                     Return: ChatRouter.handle_chat()
```

### 5.1 Guard Details & Failure Responses
1. **Guard 1 (Slot Whitelist):**
   - Extracts all `{...}` patterns.
   - If any extracted key is not present in `facts_list` -> **FAIL**.
2. **Guard 2 (Zero Digits):**
   - Executes `bool(re.search(r"\d", raw_draft))`.
   - If true -> **FAIL**.
3. **Guard 3 (Scoped Number Provenance):**
   - Extracts all numbers (`[0-9,]+`) from the *filled* string.
   - Verifies each number against the formatted numbers in `facts_list` for *this turn* (not the whole scenario file). If untraced -> **FAIL**.
4. **Guard 4 (Entity Name Integrity):**
   - Matches all names against `data/mock/employees.json`. If wrong employee is mentioned -> **FAIL**.
5. **Guard 5 (Invented Concepts & Banned Terms):**
   - Checks against `["professional tax", "pt deduction", "Notice shortfall recovery & known deductions"]` and internal identifiers. If found -> **FAIL**.
6. **Guard 6 (Policy & Paraphrase Check):**
   - Regex scan for forbidden claims:
     * Payment claims: `\b(paid|transferred|credited|disbursed|deposited in bank)\b`
     * Tax advice: `\b(recommend|should choose|opt for|invest in)\b.*\b(regime|80c|tax)\b`
     * Unauthorized approvals: `\b(i have approved|proposal is approved)\b`
   - If matched -> **FAIL**.
7. **Guard 7 (Length Check):**
   - Splits by sentence boundary (`[.!?]`). Sentence count must be 1, 2, or 3.
   - Word count must be <= 60 words. If exceeded -> **FAIL**.

---

## 6. Answers to Open Questions & Governance Alignment

1. **Acceptance Benchmark Targets:**
   - **Intent Classification Accuracy:** >= 90% across the 30-question evaluation set.
   - **Wrong Numbers Shown:** Exactly **0** (Zero wrong numbers shown).
   - **Fallback Rate:** <= 15% across all valid test interactions.
   - **Cross-Employee Data Leaks:** Exactly **0** (Zero cross-employee data sent to the AI).
2. **Language Scope:**
   - English only (Approved by: Project owner). Common transliterated Hinglish is removed across all components.
3. **Bonus Choice Disambiguation & Session Memory:**
   - The user's bonus selection (Annual vs. Sales) is remembered within the active chat session state across subsequent turns.
   - Clicking `"New chat"` clears the session state and returns to the initial disambiguation prompt if an ambiguous query is asked again.

---

## 7. Configuration & Operational Parameters

Managed in `app/backend/config.py`:

| Variable | Value | Description |
|---|---|---|
| `AI_MODE` | `true` | Master switch. If `false`, bypasses CrewAI and uses deterministic router directly. |
| `AI_MODEL` | `gpt-4o-mini` | LLM model identifier (Classifier & Drafting only). |
| `AI_TEMPERATURE` | `0.1` | Low temperature for deterministic classification and slot drafting. |
| `AI_MAX_OUTPUT_TOKENS` | `120` | Strict token limit to enforce <= 60 word replies. |
| `AI_TIMEOUT_MS` | `20000` | **20.0-second** execution deadline before triggering deterministic fallback. |

---

## 8. UI Changes

1. **Thinking State:**
   - While the AI evaluates `/api/chat`, the chat UI in `Composer.tsx` and the message stream displays an accessible `"Thinking…"` loading indicator with a subtle animated pulse.
2. **Provenance Micro-Badge:**
   - Cards display the existing subtitle: `"Calculated by HCM One Payroll Engine • AI explained"`.
3. **Session State Retention:**
   - Conversation state preserves disambiguated selections (such as bonus run type) until `"New chat"` or `"Reset demo"` is triggered.

---

## 9. Comprehensive Test & Evaluation Plan

### 9.1 Mocked Automated Tests (`app/backend/tests/test_ai_crew_mocked.py`)
- Test 1: Valid slot draft passes all guards, fills slots correctly, and returns 200.
- Test 2: AI writing a raw digit (`"3 days"`) fails Guard 2 and triggers deterministic fallback.
- Test 3: AI writing an unknown slot (`{bonus_estimate}`) fails Guard 1 and triggers fallback.
- Test 4: AI claiming payment (*"money was sent"*) fails Guard 6 and triggers fallback.
- Test 5: Scenario 12 cross-employee request blocked server-side; zero data sent to AI.
- Test 6: AI execution exceeding 20 seconds triggers deterministic fallback.
- Test 7: Master switch `AI_MODE=false` routes directly to deterministic router.

### 9.2 30-Question Evaluation Suite (`app/backend/ai/eval_ai_crew.py`)
Evaluates the live crew across 30 questions (Scenarios 1–13, casual English, glossary FAQs, and adversarial prompts) and reports:
- Intent Accuracy (Target >= 90%)
- Guard Pass Rate
- Fallback Trigger Rate (Target <= 15%)
- Offline Tone & Helpfulness Score (Target >= 4.5 / 5.0)

---

## 10. Inventory of Files to Create or Modify

### 10.1 Files to Create (PLAN ONLY — NO CODE WRITTEN YET)
1. `app/backend/ai/AI_DESIGN.md` (This document)
2. `app/backend/ai/__init__.py` (Package root)
3. `app/backend/ai/crew.py` (CrewAI orchestration: Classifier, Retrieval, Drafting, Escalation)
4. `app/backend/ai/agents.py` (Agent specifications with LLM / tool bindings)
5. `app/backend/ai/tools.py` (Deterministic scenario, engine, and FAQ tool wrappers)
6. `app/backend/ai/facts.py` (Turn-specific `facts_list` builder mapping slots to formatted values)
7. `app/backend/ai/guards.py` (The 7 mechanical runtime guards and slot interpolator)
8. `app/backend/ai/logger.py` (Masked JSONL audit run logger)
9. `app/backend/tests/test_ai_crew_mocked.py` (Automated pytest suite with mocked LLM)
10. `app/backend/ai/eval_ai_crew.py` (30-question manual evaluation and benchmark script)

### 10.2 Files to Modify
1. `project-memory/design-decisions.md`: Added DEC-041 (Completed).
2. `app/backend/requirements.txt`: Add `crewai` and `pydantic`.
3. `app/backend/config.py`: Add `AI_TIMEOUT_MS = 20000`, `AI_MAX_OUTPUT_TOKENS = 120`.
4. `app/backend/main.py`: Route `/api/chat` through the guarded AI crew pipeline.
5. `app/frontend/src/components/Composer.tsx`: Add `"Thinking…"` loading indicator.
