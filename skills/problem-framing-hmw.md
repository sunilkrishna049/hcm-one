# Skill: Problem Framing and How Might We

## Description
Turns pain points into clear, bounded problem statements and How Might We questions.

## Role
Act as a UX strategist who frames problems without jumping to solutions.

## Inputs
- Required: output/03-analysis/pain-points.md
- Required: output/03-analysis/personas.md
- Required: output/03-analysis/journey-maps.md

## Instructions
1. Group related pain points into problem areas. Aim for 4 to 7 problem statements in total, not one per pain point.
2. Write each problem statement in this format:
   "[Persona] needs a way to [need] because [insight from evidence], but today [current barrier]."
3. For each problem statement, write 2 or 3 How Might We questions.
4. Mark which problems are evidence-backed and which are requirements-led (from the BRD only).
5. Rank the problems by the strength of evidence and how central they are to the cross-journey insight (input gathering and record trust). Explain the ranking. Do not invent effort or business value.

## Output
File: output/04-strategy/problem-statements.md
Sections:
1. Summary (the core problem in 2 to 3 sentences, simple English)
2. Problem statements table. Columns: ID (PS-01…) | Problem statement | Persona | Pain points (PP IDs) | Evidence IDs | Type (Evidence-backed or Requirements-led) | Confidence
3. How Might We questions, grouped by problem statement (HMW-01…)
4. Ranking and reasoning
5. What these problems do not cover

## Rules
- Never name a feature, screen, button or technology in a problem statement or HMW.
- HMW questions must be open enough to allow several solutions, but focused enough to act on.
- Do not invent evidence. Keep confidence levels as recorded.
- Use simple English.

## Example
Good HMW: "How might we help the Payroll Admin trust that every input for a past month is correct before calculating?"
Bad HMW: "How might we build an AI dashboard for arrears?" (names a solution)