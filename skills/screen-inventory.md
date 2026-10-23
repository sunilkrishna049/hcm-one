# Skill: Screen Inventory

## Description
Derives a lean list of screens from the approved flows, giving every screen a traceable reason to exist.

## Role
Act as a product designer who keeps the screen count as small as possible.

## Inputs
- Required: output/05-architecture/user-flows.md
- Required: output/05-architecture/edge-cases-states.md
- Required: output/04-strategy/mvp-scope.md

## Instructions
1. List the screens needed for each flow, starting with the MVP flows (hike, salary explanation, TDS explanation, query), then bonus and settlement.
2. Prefer reusing one screen with different states over creating a new screen.
3. For each screen, record the fields in the output format.
4. Map each of the 13 BRD v1.2 scenarios to the screen and state that shows it.
5. Mark which screens are in the MVP and which are later.

## Output
File: output/07-prototype/screen-inventory.md
Sections:
1. Summary (number of screens per role, simple English)
2. Screen table. Columns: ID (SCR-01…) | Screen name | Role | Platform (desktop or mobile) | Flow steps (F IDs) | Reason to exist | States | MVP or later
3. Scenario-to-screen map (scenario, screen, state, data file)
4. Screens considered and removed, with reasons

## Rules
- Every screen must trace to at least one flow step.
- No screen for a feature outside BRD v1.2.
- Use simple English.
