# HCM One: Project Brief

## 1. Product summary
- **High:** HCM One is a payroll assistant for Indian companies with 200–2,000 employees. It prepares proposals and explains changes with proof. Code does the calculations. HR must approve changes. (BRD 1; GR-1.1–1.2, GR-3.2)

## 2. Users and roles
- **High:** HR reviews, edits and approves proposals for employees they are allowed to manage. Employees view their own pay and tax data and ask for explanations. They confirm queries before sending. They cannot edit payroll or see other people's data. (BRD 3.1–3.2; GR-2.1–2.4)

## 3. Problems
- **High:** HR must recalculate past pay and combine records from different places. This creates work and errors in arrears, bonuses and settlements. (BRD 4.1; Research: HR Administrator findings, pp. 2–7)
- **Medium:** Confusion about take-home pay and TDS can weaken trust. Complaints show this pattern. They do not show how common it is or measure its effect on trust. (BRD 4.2–4.3; Research: Employee findings, pp. 8–11)

## 4. Scope (in and out)
- **High:** The six flows below are in scope. Build the hike flow and salary and TDS explanations first. Build bonuses next, then settlement. Complete each flow before starting the next. (BRD 5.1–5.2)
- **High:** Full monthly payroll, payments and bank files are out of scope. Statutory filing, the Manager role and Form 26AS comparison are also excluded. Do not use real data or let AI make changes on its own. Statutory bonus is excluded. (BRD 5.3; BR-5.5)

## 5. Key flows (with FR ID ranges)
| Flow | Required experience and source |
|---|---|
| Hike | **High:** Confirm the details. Recalculate each affected month, PF and TDS. Show proof. HR can edit, reject or approve the proposal. Approval makes it ready for payroll. (FR-1.1–1.17) |
| Bonus | **High:** Check who qualifies and adjust amounts for eligible days. Calculate each employee's amount and flag exceptions. HR can approve all or some amounts, or edit them with reasons. (FR-2.1–2.19) |
| Settlement | **High:** Check clearances and hold related amounts. Calculate dues, recoveries and TDS. HR reviews and approves the proposal. Prepare a statement. (FR-3.1–3.21) |
| Salary explanation | **High:** Compare months. Start with the net change and its reasons. Offer breakdowns, sources and term meanings. Escalate when unsure. (FR-4.1–4.17) |
| TDS explanation | **High:** Explain the reasons, declarations and tax regime. Offer the calculation. Do not give personal advice. Escalate when unsure. (FR-5.1–5.13) |
| Query | **High:** Check the issue and draft a query with evidence. Allow attachment edits and removal. Confirm before sending. Handle similar queries, status and HR replies. (FR-6.1–6.13) |

## 6. Key business rules and guardrails (summary)
- **High:** Use dated rules and round amounts to the nearest rupee. Use each month's paid days. Add monthly arrears and pay them after approval. PF uses Basic plus DA and the company's wage cap setting. Show employee PF, employer EPF and EPS separately. (BR-0.1–3.7)
- **High:** Project yearly tax and apply accepted deductions. Use the configured bonus and settlement rules. Record reasons for edits and each calculation version. (BR-4.1–7.3)
- **High:** Require clear approval and check roles. Use only needed data and mask sensitive details. Code must calculate results the same way each time and link them to sources. Stop when needed inputs are missing. Refuse attempts to change the rules or reveal secrets. Stay within scope, escalate issues and keep safe audit logs. (GR-1.1–8.1)

## 7. Success measures
- **High:** These measures are proposed. There are no baselines yet. HR should prepare proposals without spreadsheets. Test calculations should be correct. Proof should be one click away. Flag all missing or unusual data cases. Explanations should be clear and queries should include complete evidence. Tests must show no unapproved changes, access to other users' data or guessing. (SM-1.1–3.3; BRD 10, 9.10)

## 8. Constraints
- **High:** Use desk research only. Do not conduct interviews. Use fictional Northwind data in JSON files with 15–20 sample employees. Use simplified demo rules. One designer will use Codex, Antigravity, CrewAI and OpenAI API. (BRD 9; C-1–C-6; Project config: Constraints)

## 9. Conflicts and gaps
- **Medium:** No contradiction has been confirmed. The gaps remain unresolved. Research does not add to the scope. (BRD 5–12; Research: Validation gaps, pp. 15–17)
- **GAP-01 — High:** Tax, EPS, gratuity and company settings are missing. Official proof of the stated PF ceiling change is also missing. (BRD 7, 9.5; BR-3.7; Research: PF impact, pp. 5–6)
  This will be resolved before build, in the rules config.
  Values recorded in data/rules/ with verification status. Values marked verify_before_build must be checked before build.
- **GAP-02 — Medium:** Rules are selected by month. It is unclear how to split September at the stated 17 September effective date. (BR-0.2, BR-3.6–3.7; BRD 9.10.2)
  This will be resolved before build, in the rules config.
  Resolved by DEC-020: demo rule in data/rules/.
- **GAP-03 — High:** It is unclear how to spread a hike across salary components or handle a hike for part of a month. The rounding order is also unspecified. (FR-1.3–1.9; BR-0.3, BR-1.2, BR-2.2, BR-3.1)
  This will be resolved before build, in the rules config.
  Resolved by DEC-021: demo rule in data/rules/.
- **GAP-04 — Medium:** The final month's day calculation needs clarification. It is also unclear how to release and approve held amounts again after clearance. (BR-1.1–1.2, BR-6.1; FR-3.4–3.5, FR-3.19–3.20)
  This will be resolved by Agent 05 (Architecture).
  Resolved at G05 (Option B). See DEC-013.
- **GAP-05 — High:** TDS rules do not explain what happens when remaining tax is negative or no months remain. They also do not explain arrears across financial years. (BR-4.1–4.3)
  This will be resolved before build, in the rules config.
  Resolved by DEC-022: demo rule in data/rules/.
- **GAP-06 — Medium:** It is unclear who handles an approved change or how it reaches payroll. Payment is out of scope. (FR-1.16, FR-2.18; BR-2.4; GR-1.1; BRD 5.3)
  This will be resolved by Agent 05 (Architecture).
  Resolved at G05 (Option B). See DEC-011.
- **GAP-07 — High:** Query delivery is unspecified. It is unclear how to identify similar queries, change their status or set expected response times. (FR-6.8–6.13)
  This will be resolved by Agent 05 (Architecture).
  Resolved at G05 (Option B). See DEC-012.
- **GAP-08 — High:** The testing method and baselines are unspecified. It is unclear how to judge understanding or enough evidence while using desk research only. (SM-1.1, SM-2.1–2.3; BRD 10; C-2; Project config: Constraints)
  This will be resolved by Agent 08 (Testing).
- **GAP-09 — High:** The settlement hold rule (FR-3.5) may conflict with the 2-working-day separation wages rule. Settlement may need to be split into components with separate due dates and statuses. (FR-3.5; DEC-004; EVD-65, EVD-71, EVD-81)
  This will be resolved by Agent 04 (Strategy) and Agent 05 (Architecture).
  Resolved at G04 (Option B). See DEC-008.

## 10. Open questions
- **OQ-1 — Low:** How much time does HR spend on arrears and settlements? (BRD 11.2; Research: Validation gaps, p. 17)
- **OQ-2 — Low:** Are employees comfortable with AI accessing their salary and tax data? (BRD 11.2; Research: Employee-specific willingness, p. 15)
- **OQ-3 — Low:** Does HR prefer to approve bonuses individually or for a team? Both options are supported. The preference is unknown. (BRD 11.2; FR-2.16)
- **OQ-4 — Low:** How much detail do employees need to feel confident? (BRD 11.2; AS-2, AS-4)
- **OQ-5 — Low:** Is a second approver, such as Finance, needed? (BRD 11.2; Research: Approval steps, p. 7)

## 11. Sources used
- **High:** Sections 1–12 of the [BRD](../../input/requirements/Payroll_brd.md) provide the requirements. High confidence means the wording is explicit. It does not mean compliance has been verified. (BRD 7, 11)
- **High:** Pages 1–19 of the [research PDF](../../input/research/desk-research.pdf) provide supporting evidence. Its external sources have not been checked again. (Research: Evidence standard, p. 2)
- **High:** The [config](../../project-memory/project.config.md) and [state](../../project-memory/project.state.md) provide the constraints and identify who can review the project. (Config: Rules, Constraints; State: Gate Status)
