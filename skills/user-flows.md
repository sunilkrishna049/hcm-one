# Skill: User Flows

## Description
Maps requirement-backed user flows with steps, decisions, alternatives, errors and recovery, without making visual decisions.

## Role
Act as an interaction designer who designs the logic of each flow before any screen exists.

## Inputs
- Required: input/requirements/Payroll_brd_v1.1.md (Sections 5, 6, 7, 8)
- Required: output/04-strategy/mvp-scope.md
- Required: output/04-strategy/ux-principles.md

## Instructions
1. Create one flow for each of the six BRD flows. Use full detail for priority 1 flows (back-dated hike, salary explanation, TDS explanation, raise a query). Use the same structure for bonus and settlement.
2. For each flow, record:
   - Trigger (what starts it)
   - Actor (HR Admin, Employee, System or AI agent)
   - Preconditions (what must be true first)
   - Main path (numbered steps)
   - Decision points (yes or no branches)
   - Alternative paths (valid variations)
   - Error and recovery paths (missing data, permission denied, low confidence, user rejects)
   - End states (how the flow can finish)
3. For each step, show who acts: User, AI agent, Calculation code or System. Remember: calculation code does all maths, the AI agent explains (GR-3.2).
4. Add a Mermaid flowchart for each priority 1 flow.
5. Propose a resolution for GAP-06 (what happens after HR approval) and GAP-07 (query delivery, matching and status transitions).
6. Mark any point about AI wording, confidence display or trust as "For Agent 06".

## Output
File: output/05-architecture/user-flows.md
Sections:
1. Summary (simple English)
2. Actors and responsibilities (User, AI agent, Calculation code, System)
3. Flow 1 to Flow 6, each with the fields above, a Mermaid flowchart for priority 1 flows, and requirement IDs per step
4. GAP-06 proposed resolution (options, trade-offs, recommendation)
5. GAP-07 proposed resolution (options, trade-offs, recommendation)
6. Open questions

## Rules
- Every step links to an FR, BR or GR ID.
- Do not describe screens, layouts or visual design.
- Do not promise response times or payment.
- Resolutions are proposals. Mark them "Proposed. Project owner decides."
- Use simple English.