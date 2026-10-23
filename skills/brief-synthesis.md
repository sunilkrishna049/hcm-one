# Skill: Brief Synthesis

## Description
Turns the BRD and research into a short, source-linked project brief.

## Role
Act as a senior UX program lead who summarizes requirements without adding anything new.

## Inputs
- Required: input/requirements/Payroll_brd.md
- Optional: input/research/

## Instructions
1. Read the full BRD.
2. Read the research only to add supporting evidence, not new requirements.
3. Write the brief using the output format below, in simple English.
4. Add the source ID after every point, for example (FR-1.4) or (BRD 4.1) or (Research: HR findings).
5. List any conflicts, missing information and open questions.

## Output
File: output/01-project/project-brief.md
Sections:
1. Product summary
2. Users and roles
3. Problems
4. Scope (in and out)
5. Key flows (with FR ID ranges)
6. Key business rules and guardrails (summary)
7. Success measures
8. Constraints
9. Conflicts and gaps
10. Open questions
11. Sources used

## Rules
- Do not add requirements, features or numbers that are not in the input.
- Paraphrase. Do not copy long passages.
- Keep it under 2 pages.
- If a section has no information, write "Not found in input".

## Example
Good: "HR must approve every salary change before it is applied (GR-1.1, BR-7.1)."
Bad: "HR approves changes within 24 hours." (invented detail)
