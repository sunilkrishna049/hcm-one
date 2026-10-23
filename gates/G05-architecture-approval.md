# Gate G05: Architecture Approval

## Reviews
- output/05-architecture/user-flows.md
- output/05-architecture/edge-cases-states.md
- Any new decisions in project-memory/design-decisions.md

## Checklist
- [ ] All six flows are mapped. Priority 1 flows are in full detail with Mermaid flowcharts.
- [ ] Every step links to FR, BR or GR IDs.
- [ ] Calculation code does the maths; the AI agent only explains.
- [ ] Every flow has error and recovery paths.
- [ ] No state lets the AI approve, apply or pay. "Approved" never means "paid".
- [ ] Settlement uses component-level states (GAP-09 Option B).
- [ ] All 13 BRD test scenarios are mapped.
- [ ] GAP-04, GAP-06 and GAP-07 have clear options and recommendations.
- [ ] No visual design. AI wording and trust points are marked "For Agent 06".
- [ ] Written in simple English.

## Decision (Project owner only)
- Approve: move to Agent 06 (AI Interaction)
- Revise: list what to fix, then Agent 05 runs again
- Reject: go back to Agent 04

## Record
Update project-memory/project.state.md with the decision, date and notes.