# Skill: Approval and Failure Handling

## Description
Designs the approval moments and the AI's behavior when data is missing, rules are unverified, calculations fail, access is denied or a request is unsafe.

## Role
Act as an AI interaction designer who designs for human control and graceful failure.

## Inputs
- Required: output/05-architecture/user-flows.md
- Required: output/05-architecture/edge-cases-states.md
- Required: output/04-strategy/ux-principles.md
- Required: input/requirements/Payroll_brd_v1.1.md (Sections 7 and 8)

## Instructions
1. Design the HR approval moment: what HR must see before approving (version, scope, what changed since the last version, unresolved items, sources), and what makes the approve action unavailable.
2. Design the edit-with-reason pattern and what happens after an edit.
3. Design partial approval for bonus and settlement (approving some items, with clear separation of what is not approved).
4. Design the employee query confirmation moment (what they see before sending, and what clears confirmation).
5. Design the AI's behavior for each system state: missing data, rule not verified, low confidence, calculation error, permission denied, out-of-scope request, prompt injection.
6. For each failure, define: what the AI says happened, what it will not do, what the user can do next, and who is responsible.
7. Cover these handoff points: A06-02 (missing data and uncertainty), A06-04 (unusual result, partial approval, summary), A06-06 (uncertain eligibility, held components), A06-13 (all system states).

## Output
File: output/06-ai-interaction/approval-failure-handling.md
Sections:
1. Summary (simple English)
2. HR approval moment
3. Edit with reason
4. Partial approval (bonus and settlement)
5. Employee query confirmation
6. Failure and fallback patterns (table: state, what AI says, what AI will not do, user next step, owner, source IDs)
7. Patterns for A06-02, A06-04, A06-06, A06-13
8. Assumptions and open questions

## Rules
- The AI never approves, applies, pays or sends on its own.
- Silence is never approval or consent.
- Failure messages never guess a cause, a number or a deadline.
- Security refusals are short and reveal nothing internal (GR-5.3).
- No visual design. Describe structure and behavior only.
- Use simple English.
