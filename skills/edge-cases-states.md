# Skill: Edge Cases and States

## Description
Defines all states each flow can be in, and the realistic edge cases it must handle.

## Role
Act as an interaction designer and QA-minded architect who plans for what goes wrong.

## Inputs
- Required: output/05-architecture/user-flows.md
- Required: input/requirements/Payroll_brd_v1.1.md (Sections 7, 8, 9.10)
- Required: output/01-project/project-brief.md (Section 9 gaps)

## Instructions
1. Define the proposal states used by HR flows (for example: Draft, Needs input, Calculated, Ready for review, Revised, Approved and ready for payroll, Rejected). Show the allowed transitions and who can trigger each one.
2. Define settlement component states using the approved GAP-09 Option B: each component has its own basis, due date basis, status and hold reason.
3. Define query states (for example: Draft, Sent, In review, Resolved, Closed) and transitions.
4. Define system states for every flow: loading, missing data, permission denied, low confidence, calculation error, out of scope request.
5. Map all 13 BRD test scenarios (Section 9.10) to the flow, the path and the expected state.
6. List additional realistic edge cases not covered by the 13 scenarios.
7. Propose a resolution for GAP-04 (final-month day calculation and release or re-approval of held components).

## Output
File: output/05-architecture/edge-cases-states.md
Sections:
1. Summary (simple English)
2. HR proposal states and transitions (table plus a Mermaid state diagram)
3. Settlement component states (Option B)
4. Query states and transitions (table plus a Mermaid state diagram)
5. System states per flow
6. BRD test scenarios mapped (scenario, flow, path, expected state, requirement IDs)
7. Additional edge cases (case, expected handling, known or recommended, source)
8. GAP-04 proposed resolution (options, trade-offs, recommendation)
9. Open questions

## Rules
- Separate known handling (from the BRD) from recommended handling (your proposal).
- No state may let the AI approve, apply or pay anything (GR-1.1).
- "Approved" never means "paid".
- Resolutions are proposals. Mark them "Proposed. Project owner decides."
- Use simple English.