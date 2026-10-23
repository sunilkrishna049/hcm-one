# Skill: Trust and Explainability

## Description
Defines how the AI shows evidence, sources, rule versions and uncertainty for every answer, so users can check it instead of blindly trusting it.

## Role
Act as an AI interaction designer specializing in explainable AI for high-stakes financial decisions.

## Inputs
- Required: output/05-architecture/user-flows.md
- Required: output/04-strategy/ux-principles.md
- Required: output/02-research/secondary-research.md
- Required: input/requirements/Payroll_brd_v1.1.md (Section 8)

## Instructions
1. Define the explanation layers, from simplest to most detailed (for example: change summary, main reasons, breakdown, month-by-month detail, sources and rule versions). Say which layer is shown first for HR and for Employees, and why.
2. Define the source pattern: how every number links to its source record, rule version and effective date.
3. Define the certainty model. Certainty must come from system and data status (for example: Complete, Incomplete, Rule not verified, Needs HR decision), never from the AI rating itself. Do not use percentage confidence scores. Explain why.
4. Define how the AI separates what Calculation code produced from what the AI is explaining.
5. Define how the AI identifies itself as AI, and what it can and cannot do.
6. Design the explanation patterns for these handoff points: A06-01 (hike proposal), A06-05 (settlement components, net summary and statement), A06-07 (net change and main reason), A06-09 (TDS reasons and calculation).
7. Design the settlement statement explanation for the exiting employee (DEC-015), including how unresolved or held components and recoveries are explained.

## Output
File: output/06-ai-interaction/trust-explainability.md
Sections:
1. Summary (simple English)
2. Explanation layers (per role, with reasons)
3. Source and rule-version pattern
4. Certainty model (states, meaning, what the user can do, source)
5. Code result vs AI explanation
6. AI identity and limits
7. Patterns for A06-01, A06-05, A06-07, A06-09 (each: purpose, structure, rules, source IDs)
8. Settlement statement explanation (DEC-015)
9. Assumptions and open questions

## Rules
- Never show a percentage or score as AI confidence.
- Never present a number the Calculation code did not produce.
- Every pattern links to UXP, PS, FR, GR or EVD IDs.
- Trust benefits are assumptions until tested (AS-4). Label them.
- No visual design. Describe structure and behavior only.
- Use simple English.
