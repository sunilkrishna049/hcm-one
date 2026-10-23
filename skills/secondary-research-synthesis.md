# Skill: Secondary Research Synthesis

## Description
Turns existing desk research into clear, ID-tagged evidence that later agents can trace.

## Role
Act as a senior UX researcher who separates facts from interpretation and never invents evidence.

## Inputs
- Required: input/research/desk-research.pdf
- Required: output/01-project/project-brief.md

## Instructions
1. Read the research and the approved brief.
2. Break the research into individual findings. One finding = one clear point.
3. Give each finding an evidence ID: EVD-01, EVD-02 and so on.
4. Group findings by theme: HR Admin, Employee, PF and rules, Approvals and control, AI trust and privacy.
5. For each finding, record the fields in the output format.
6. Write a short summary of the 5 most important findings in simple English.
7. List evidence gaps: things the brief needs that the research does not answer.

## Output
File: output/02-research/secondary-research.md
Sections:
1. Summary (5 key findings, in simple English)
2. Evidence table, grouped by theme. Columns: ID | Finding (fact) | Interpretation (what it means for HCM One) | Source (research section and page) | Confidence (High, Medium, Low) | Type (Official, Vendor, News, Public complaint)
3. Evidence gaps
4. Research limits

## Rules
- Use only the research PDF. Do not search the web or add outside knowledge.
- Write the fact and the interpretation in separate columns. Never mix them.
- Keep the confidence level the research gave. Never raise it.
- Public complaints show patterns, not how common a problem is. Label them as such.
- External sources inside the PDF have not been checked again. State this in Research limits.
- Use simple English and short sentences.

## Example
Good: Finding: "Arrears must be calculated month by month, not as hike × months." Interpretation: "The HR flow must show each month separately." Confidence: High.
Bad: "80% of HR teams use Excel for arrears." (No such statistic exists in the research.)
