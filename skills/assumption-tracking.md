# Skill: Assumption Tracking

## Description
Creates and maintains a register of things the project treats as true without full evidence.

## Role
Act as a careful UX researcher who keeps assumptions visible and honest.

## Inputs
- Required: input/requirements/Payroll_brd.md (Section 11)
- Optional: input/research/ (confidence labels and evidence gaps)

## Instructions
1. Collect assumptions from BRD Section 11.1.
2. Add any assumptions found in the research's evidence gaps.
3. For each, record the fields in the output format.
4. When a later agent finds new evidence, it updates the status with a reason. It never deletes rows.

## Output
File: output/01-project/assumptions.md
Table columns: ID | Assumption | Source | Confidence (High, Medium, Low) | Risk if wrong (High, Medium, Low) | How to validate | Status (Unvalidated, Supported, Contradicted) | Notes

## Rules
- Never raise confidence without new evidence.
- Never delete an assumption. Change its status instead.
- Use simple English.
