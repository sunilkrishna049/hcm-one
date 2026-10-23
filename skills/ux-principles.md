# Skill: UX Principles

## Description
Defines project-specific UX principles that guide every design decision after this stage.

## Role
Act as a design lead who creates decision rules, not slogans.

## Inputs
- Required: output/04-strategy/problem-statements.md
- Required: output/03-analysis/personas.md
- Required: input/requirements/Payroll_brd.md (Section 8 Guardrails)
- Required: output/02-research/secondary-research.md

## Instructions
1. Write 5 to 7 UX principles specific to HCM One.
2. Each principle must help decide between two design options.
3. For each principle, record the fields in the output format.
4. Check that the principles do not contradict the BRD guardrails.

## Output
File: output/04-strategy/ux-principles.md
For each principle:
- ID (UXP-01…)
- Principle (short, memorable, one line)
- What it means (2 to 3 simple sentences)
- Do (one example)
- Don't (one example)
- Source (PS IDs, PP IDs, EVD IDs or BRD guardrail IDs)
- Confidence

End with: "How to use these principles" (2 to 3 lines).

## Rules
- No generic principles like "Keep it simple" or "Be user-friendly". Every principle must be specific to payroll, trust or AI in HCM One.
- Every principle must trace to evidence or a BRD guardrail.
- Use simple English.

## Example
Good: "Show the month, not just the total." Do: show arrears for each affected month. Don't: show one arrears number only. Source: PP-01, EVD-01, EVD-02.
Bad: "Make it intuitive." (generic, not testable)