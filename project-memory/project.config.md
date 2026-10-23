# Project Config: HCM One Design Orchestrator

## Project
- Name: HCM One, AI Payroll Assistant
- Purpose: Use AI agents and skills to run the UX design process for HCM One, from BRD to tested prototype.
- Owner and approver: Project owner (UX Designer). Only he can approve gates.

## Paths
- Input (read-only): input/requirements/Payroll_brd_v1.2.md (current), input/requirements/Payroll_brd_v1.1.md (v1.1, historical, do not edit), input/requirements/Payroll_brd.md (v1.0, historical, do not edit), input/research/
- Agents: agents/
- Skills: skills/
- Gates: gates/
- Workflow and orchestrator: workflow/
- Outputs: output/01-project/ to output/08-testing/
- Memory: project-memory/
- Rules config: data/rules/
- Mock data: data/mock/
- Calculation engine: engine/
- Generated results: data/generated/
- Runtime data store: data/runtime/
- Backend application: app/backend/
- Frontend application: app/frontend/
- Frontend design system: app/frontend/src/design-system/
- Prototype screenshots: app/screenshots/

## Agent Sequence
| # | Agent | Skills | Output folder | Gate |
|---|---|---|---|---|
| 01 | Project | brief-synthesis, assumption-tracking, skill-validation | output/01-project/ | G01 Project approval |
| 02 | Research | secondary-research-synthesis, competitor-analysis | output/02-research/ | G02 Research approval |
| 03 | Analysis | pain-point-extraction, persona-synthesis, journey-mapping | output/03-analysis/ | G03 Synthesis approval |
| 04 | Strategy | problem-framing-hmw, mvp-scope, ux-principles | output/04-strategy/ | G04 Strategy approval |
| 05 | Architecture | user-flows, edge-cases-states | output/05-architecture/ | G05 Architecture approval |
| 06 | AI Interaction | trust-explainability, approval-failure-handling, conversation-design | output/06-ai-interaction/ | G06 AI interaction approval |
| 07 | Prototype | screen-inventory, ux-content-visual-spec | output/07-prototype/ | G07 Prototype approval |
| 08 | Testing | test-plan, findings-iteration-backlog | output/08-testing/ | G08 Testing review |

Shared skill used by all agents: design-decision-log (writes to project-memory/design-decisions.md)

## Loops
- Testing can send work back to Prototype, then Prototype returns to Testing.
- Any agent can send work back to an earlier agent if a requirement or rule is unclear.

## Rules for All Agents
1. Never change anything in input/.
2. Never invent research, users, numbers or requirements.
3. Label every finding: High, Medium, Low confidence, or Assumption.
4. Keep contradictions visible. Do not hide them.
5. Every artifact links back to its source (BRD requirement ID or research section).
6. A gate is passed only when Project owner explicitly approves. Silence or a created file is not approval.
7. Record every important decision in the design decision log.

## Constraints
- Desk research only. No user interviews.
- Fictional mock data only.
- Simplified Indian payroll rules, not real compliance.
- Tools: Codex, Antigravity, CrewAI, OpenAI API.
