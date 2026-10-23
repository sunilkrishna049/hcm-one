# Skill: UX Content and Visual Spec

## Description
Defines the exact content, layout structure, states and visual system for every screen, using real calculated data, and writes AI prompts to design each screen in Figma.

## Role
Act as a senior product designer creating a precise, buildable specification.

## Inputs
- Required: output/07-prototype/screen-inventory.md
- Required: output/06-ai-interaction/ (all three files)
- Required: data/generated/ (scenario files, payslips, bonus proposals, calculation ledger)
- Required: output/04-strategy/ux-principles.md

## Instructions
1. For each screen, write the specification in screen-specs.md: purpose, layout structure (top to bottom), exact content (headings, labels, AI messages, numbers), actions, states and the UX principles it applies (UXP IDs).
2. For every number, give its exact value and its source: data/generated/ file and record reference. Never round, estimate or invent.
3. Use the scenario data to fill each screen with a real example (for example, the hike screen uses E01 Priya Sharma, scenario 1).
4. Show how certainty labels, approval states, flags and "Show calculation" appear on each screen.
5. Write visual-spec.md: design tokens (typography scale, colors including one accent and status colors, spacing, grid, radius), core components (message bubble, number card, calculation breakdown, source link, certainty label, approval bar, component list, query draft), and accessibility rules.
6. Write figma-ai-prompts.md: one ready-to-paste prompt per MVP screen for an AI design tool. Each prompt includes the screen purpose, platform size, layout, exact content and numbers, states to show and the visual direction.

## Output
- output/07-prototype/screen-specs.md
- output/07-prototype/visual-spec.md
- output/07-prototype/figma-ai-prompts.md

## Rules
- Every number comes from data/generated/ with a source reference.
- AI wording follows output/06-ai-interaction/ exactly. No internal terms (like "Calculation code") in user-facing text.
- No confidence percentages. Use the approved certainty labels.
- Approval never looks like payment.
- Status is never shown by color alone.
- Use simple English.
