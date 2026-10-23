# HCM One: Chat Contract Specification (`/api/chat`)

This document defines the formal request and response JSON schema for the unified conversational endpoint `POST /api/chat`.

HCM One operates a single conversational API endpoint that serves both **`CHAT-HR`** (Desktop HR Admin workspace) and **`CHAT-EMP`** (Mobile Employee workspace). Behind this contract, a deterministic router responds to actions and natural language intents today; in Step 4, an agentic CrewAI crew will replace the router without modifying this schema.

---

## 1. Endpoint Definition

- **Path:** `/api/chat`
- **Method:** `POST`
- **Headers:**
  - `Content-Type: application/json`
  - `X-User-Id: <user_id>` (optional; if omitted, `user_id` in request body is used)

---

## 2. Request Schema

### 2.1. JSON Schema Definition

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ChatRequest",
  "type": "object",
  "required": ["user_id"],
  "properties": {
    "user_id": {
      "type": "string",
      "description": "Authenticated user identifier (e.g. 'HR01', 'HR02', 'USER-E01', 'USER-E05', 'USER-E06', 'USER-E16')."
    },
    "message": {
      "type": "string",
      "description": "User's typed message or query prose in the chat composer."
    },
    "action": {
      "type": ["string", "null"],
      "description": "Optional identifier for a chip tap or button action (e.g. 'scenario-1', 'show-calculation', 'draft-query', 'approve-proposal', 'confirm-send-query')."
    },
    "context": {
      "type": "object",
      "description": "Optional client-side state parameters (e.g. active scenario, proposal id, target month, query id).",
      "additionalProperties": true
    }
  }
}
```

### 2.2. Request Examples

#### Natural Language Message
```json
{
  "user_id": "HR01",
  "message": "Prepare Priya Sharma's pending back-dated hike.",
  "action": null,
  "context": {}
}
```

#### Action Triggered from Suggestion Chip
```json
{
  "user_id": "USER-E05",
  "message": "Why is my take-home pay lower in September?",
  "action": "explain-salary",
  "context": {
    "target_month": "2026-09"
  }
}
```

#### Governance Action (Proposal Approval)
```json
{
  "user_id": "HR01",
  "message": "",
  "action": "approve-proposal",
  "context": {
    "proposal_id": "PROP-SCENARIO-1",
    "scenario_num": 1,
    "scope": "2026-04 to 2026-09"
  }
}
```

---

## 3. Response Schema

### 3.1. JSON Schema Definition

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ChatResponse",
  "type": "object",
  "required": ["messages", "cards", "chips", "state"],
  "properties": {
    "messages": {
      "type": "array",
      "description": "List of assistant response text bubbles. Wording uses only approved sentences C01–C30 verbatim.",
      "items": {
        "type": "object",
        "required": ["code", "text"],
        "properties": {
          "code": {
            "type": "string",
            "description": "Approved sentence code (e.g. 'C01', 'C03', 'C04', 'C07', 'C10', 'C27', 'C30'). Never displayed in UI."
          },
          "text": {
            "type": "string",
            "description": "Verbatim approved prose with runtime slot interpolation."
          }
        }
      }
    },
    "cards": {
      "type": "array",
      "description": "List of structured rich cards embedded in the conversation thread.",
      "items": {
        "type": "object",
        "required": ["id", "type", "title", "certainty", "data"],
        "properties": {
          "id": {
            "type": "string",
            "description": "Unique card identifier."
          },
          "type": {
            "type": "string",
            "enum": [
              "proposal_summary",
              "number_hero",
              "number_cards",
              "month_table",
              "component_list",
              "reason_list",
              "certainty_label",
              "show_calculation",
              "clarifying_question",
              "approval_card",
              "query_draft",
              "send_confirmation",
              "query_status",
              "refusal_card",
              "faq_answer"
            ],
            "description": "Card component variant from the 14 design system specifications."
          },
          "title": {
            "type": "string",
            "description": "User-facing card title."
          },
          "certainty": {
            "type": "string",
            "enum": [
              "Complete for this scope",
              "Incomplete",
              "Rule not verified",
              "Needs HR decision",
              "Cannot explain from available payroll data",
              "Permission denied"
            ],
            "description": "Epistemic certainty status attached to this calculation card."
          },
          "data": {
            "type": "object",
            "description": "Deterministic payroll figures, breakdown tables, sources, or rule citations bound from engine.",
            "additionalProperties": true
          }
        }
      }
    },
    "chips": {
      "type": "array",
      "description": "Suggestion chips rendered below assistant turn for guided interaction.",
      "items": {
        "type": "object",
        "required": ["label", "action"],
        "properties": {
          "label": {
            "type": "string",
            "description": "Button label on the chip."
          },
          "action": {
            "type": "string",
            "description": "Action key sent on tap."
          },
          "payload": {
            "type": "object",
            "description": "Optional parameters to include in request context.",
            "additionalProperties": true
          }
        }
      }
    },
    "state": {
      "type": "object",
      "description": "Conversation lifecycle state tracking active scenario, role, target employee, and heavy review panel contents.",
      "properties": {
        "intent": {
          "type": "string",
          "description": "Classified intent name."
        },
        "scenario_num": {
          "type": ["integer", "null"],
          "description": "Active BRD scenario number (1–13) if applicable."
        },
        "role": {
          "type": "string",
          "enum": ["HR Admin", "Employee"]
        },
        "surface": {
          "type": "string",
          "enum": ["CHAT-HR", "CHAT-EMP"]
        },
        "employee_id": {
          "type": ["string", "null"]
        },
        "panel": {
          "type": ["object", "null"],
          "description": "Data payload for PANEL-HR (Desktop side panel) or SHEET-EMP (Mobile bottom sheet)."
        }
      },
      "additionalProperties": true
    }
  }
}
```

---

## 4. Supported Intent Types

The deterministic router classifies incoming requests into one of 13 intents:

1. **`prepare_hike_proposal`**: Back-dated salary revision proposals across affected periods (Scenarios 1, 2, 3).
2. **`bonus_proposal`**: Team bonus eligibility and proration runs (Scenarios 4, 5).
3. **`settlement_proposal`**: Full & final settlement calculation and component holds (Scenarios 6, 7, 8, 13).
4. **`explain_salary_change`**: Pay variation explanations with causal ranking (Scenarios 9, 11).
5. **`explain_tds_change`**: TDS variation explanations and previous-employer projections (Scenario 10).
6. **`other_employee_data`**: Cross-employee salary requests; strictly refused with sentence C10 and Refusal Card (Scenario 12).
7. **`draft_query`**: Formulates employee inquiries into structured drafts with evidence (Flow 6 / Scenario 9/10/12).
8. **`query_status`**: Queries existing employee payroll tickets across their lifecycle (`Draft`, `Sent`, `In review`, `Resolved`, `Closed`).
9. **`hr_query_review`**: HR administrator review, take-into-review, and resolution recording.
10. **`faq_question`**: General payroll policy and statutory rule queries answered from `payroll_faq.json`.
11. **`out_of_scope`**: Disallowed advice requests (personal tax advice, bank deposit verification) answered with C11 or C21.
12. **`prompt_injection`**: Prompt leak or system prompt bypass attempts refused with C10.
13. **`unknown`**: Unmapped queries; returned with honest fallback and relevant suggestion chips.

---

## 5. Architectural Handoff to CrewAI

In Step 4, a CrewAI crew composed of:
- **Classifier Agent**
- **Retrieval Agent**
- **Response Drafting Agent**
- **Governance / Guard Agent**

will replace the deterministic pattern-matching router. Because the crew outputs this exact JSON schema, frontend chat surfaces (`CHAT-HR` and `CHAT-EMP`) and automated Vitest validation suites remain unchanged.
