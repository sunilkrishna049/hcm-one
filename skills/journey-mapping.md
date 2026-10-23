# Skill: Journey Mapping

## Description
Maps the current-state journey for each role, showing what happens today without HCM One.

## Role
Act as a UX researcher mapping today's experience, not designing the future one.

## Inputs
- Required: output/03-analysis/personas.md
- Required: output/03-analysis/pain-points.md
- Required: output/02-research/secondary-research.md

## Instructions
1. Create two current-state journeys:
   - HR Admin: processing a back-dated salary hike
   - Employee: noticing and trying to understand a salary change
2. Break each journey into stages (for example: Trigger, Gather data, Calculate, Review and approve, Communicate).
3. For each stage, record the fields in the output format.
4. Mark the stage with the highest pain as the main opportunity area.

## Output
File: output/03-analysis/journey-maps.md
For each journey, a table with columns: Stage | What the user does | Tools and touchpoints | Thoughts and feelings (from evidence only) | Pain points (PP IDs) | Evidence IDs | Confidence
After each table:
- Highest pain stage and why
- Gaps: stages where evidence is missing

## Rules
- Map today's experience only. Do not describe HCM One features.
- Thoughts and feelings must come from evidence (for example, complaint patterns). Otherwise label them "Assumption".
- Do not invent steps the evidence does not support. Mark unsupported steps as "Assumption".
- Bonus and settlement journeys are not required now. Note them as future work.
- Use simple English.
