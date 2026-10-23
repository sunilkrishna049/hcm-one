# Skill: Pain Point Extraction

## Description
Turns approved evidence into clear, evidence-backed user pain points.

## Role
Act as a UX analyst who describes problems without suggesting solutions.

## Inputs
- Required: output/02-research/secondary-research.md
- Required: output/01-project/project-brief.md

## Instructions
1. Read the evidence table and the brief.
2. Find pain points for each role: HR Admin and Employee.
3. Group related pain points into themes.
4. For each pain point, record the fields in the output format.
5. Write a short summary of the top pain points per role.

## Output
File: output/03-analysis/pain-points.md
Sections:
1. Summary (top 3 pain points per role, in simple English)
2. HR Admin pain points
3. Employee pain points
Table columns for sections 2 and 3: ID (PP-01, PP-02…) | Pain point | What happens because of it (impact) | Evidence IDs | Confidence (High, Medium, Low, Assumption) | Related flow (Hike, Bonus, Settlement, Salary explanation, TDS explanation, Query)
4. Pain points with weak evidence (listed separately)

## Rules
- Describe the problem only. Never describe a feature or solution.
- Every pain point needs at least one evidence ID, or it must be labeled "Assumption".
- Do not say how common a pain point is unless the evidence shows it.
- Use simple English.

## Example
Good: "HR cannot see which past month caused a difference in total arrears." (EVD-02)
Bad: "HR needs an AI arrears calculator." (This is a solution, not a pain point.)
