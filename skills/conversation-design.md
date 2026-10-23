# Skill: Conversation Design

## Description
Defines how the AI talks: voice and tone per role, message structures, clarifying questions, refusals and example conversations.

## Role
Act as a conversation designer for a trustworthy enterprise AI assistant.

## Inputs
- Required: output/03-analysis/personas.md
- Required: output/05-architecture/user-flows.md
- Required: output/06-ai-interaction/trust-explainability.md
- Required: output/06-ai-interaction/approval-failure-handling.md
- Required: input/requirements/Payroll_brd_v1.1.md (Section 8)

## Instructions
1. Define the voice and tone for each role: HR Admin and Employee. Explain why they differ, linked to the personas.
2. Write content rules (for example: lead with the change, short sentences, explain payroll terms on first use, no jargon, no blame, no promises).
3. Define how the AI asks clarifying questions (one question at a time, offer choices when possible).
4. Define refusal patterns: personal tax advice, other employees' data, out-of-scope requests, prompt injection.
5. Write a short glossary of payroll terms with one-line simple meanings (PF, EPF, EPS, LOP, TDS, arrears, gratuity, leave encashment, notice recovery).
6. Cover these handoff points: A06-03 (eligibility and proration), A06-08 (breakdown, terms, payroll-only limits, escalation), A06-10 (advice boundary and uncertainty), A06-11 (query description and evidence), A06-12 (confirmation, candidate queries, status, next step with no response-time promise).
7. Write one example conversation for each priority 1 flow (hike, salary explanation, TDS explanation, raise a query), plus one failure example (missing data). Use the fictional company Northwind Technologies. Label every number "Illustrative example, not a calculation".

## Output
File: output/06-ai-interaction/conversation-design.md
Sections:
1. Summary (simple English)
2. Voice and tone per role
3. Content rules
4. Clarifying questions
5. Refusal patterns
6. Payroll glossary
7. Patterns for A06-03, A06-08, A06-10, A06-11, A06-12
8. Example conversations (5)
9. Assumptions and open questions

## Rules
- The AI never promises response times, outcomes or future pay.
- The AI never gives personal tax, legal or financial advice.
- Example numbers are illustrative and clearly labeled.
- No real company, employee or payroll data.
- No visual design.
- Use simple English.
