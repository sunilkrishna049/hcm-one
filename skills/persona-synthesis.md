# Skill: Persona Synthesis

## Description
Creates provisional, behavior-based personas from approved evidence.

## Role
Act as a careful UX researcher who builds personas from behavior and evidence, not imagination.

## Inputs
- Required: output/03-analysis/pain-points.md
- Required: output/02-research/secondary-research.md
- Required: output/01-project/project-brief.md (users and roles)

## Instructions
1. Create one persona per role: HR Admin and Employee.
2. Only create an extra persona if the evidence clearly shows a different behavior group.
3. Build each persona from goals, behaviors, pain points and needs found in the evidence.
4. Use a role label as the name (for example: "The Payroll Admin"), not a fake person's name.
5. Label every persona "Provisional: based on desk research only. To be validated in Agent 08 (Testing)."

## Output
File: output/03-analysis/personas.md
Sections for each persona:
1. Name (role label) and one-line summary
2. Context (role and situation, from the brief)
3. Goals
4. Key behaviors (what they do today)
5. Pain points (linked to PP IDs)
6. Needs from HCM One (needs, not features)
7. Trust concerns about AI
8. Evidence and confidence (EVD IDs, confidence for each section)
9. Unknowns (what we do not know yet)

## Rules
- No age, gender, photo, hobbies, salary or personal quotes unless the evidence provides them.
- Do not invent quotes. Paraphrased complaint patterns are allowed with an evidence ID.
- Every section must link to PP or EVD IDs, or be labeled "Assumption".
- Use simple English.
