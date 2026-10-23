# HCM One: MVP Scope

Sources: [problem statements](problem-statements.md), the [BRD](../../input/requirements/Payroll_brd.md), the approved [brief](../01-project/project-brief.md), [research](../02-research/secondary-research.md), [analysis](../03-analysis/pain-points.md) and [decision log](../../project-memory/design-decisions.md). This document proposes scope decisions for G04. It does not change the BRD.

## 1. Summary
Keep the BRD's first build priority: the back-dated hike and salary and TDS explanations. Build bonus next and settlement later. Include the existing query flow as supporting work for the first employee flows, subject to Project owner approval, because those flows must offer an unresolved issue a complete path to HR. (BRD 5.2; FR-4.15, FR-5.12, FR-6.1–FR-6.13)

**High for BRD scope:** Every flow remains a proposal or explanation using fictional data. Salary payments, bank files, full monthly payroll, statutory filing, a Manager role and Form 26AS comparison remain excluded. No effort, cost, completion date or business value is estimated. (BRD 5.3, 7; C-3–C-5; GR-1.1, GR-8.1)

## 2. Flow-to-problem map

The map links each flow's purpose to problems. It does not imply that every control inside a flow has direct user evidence. Section 4 identifies requirements without a direct problem link. FR ranges and priorities come from BRD Sections 5 and 6.

| Flow | BRD FR range | Problem statements (PS IDs) | Build priority | Notes |
|---|---|---|---|---|
| Back-dated salary hike | FR-1.1–FR-1.17 | PS-01, PS-04, PS-05 | 1 | Reconcile periods and inputs, establish the rule basis and obtain explicit HR approval. Approved means ready for payroll, not paid. |
| Bonus and incentives | FR-2.1–FR-2.19 | PS-01, PS-04, PS-05, PS-06 | 2 | Keep eligibility, proration, input checks and approval in scope despite missing target-company policy evidence. PS-06 is requirements-led. Statutory bonus remains excluded by BR-5.5. |
| Full and final settlement | FR-3.1–FR-3.21 | PS-01, PS-03, PS-04, PS-05 | 3 | Reconcile dues and recoveries, establish company terms and prepare an understandable statement after approval. GAP-09 remains open; Section 5 proposes a direction. No payment execution is added. |
| Salary change explanation | FR-4.1–FR-4.17 | PS-02, PS-03, PS-05 | 1 | Explain the received amount and payroll sources. External bank or statutory records in complaints do not authorize integrations. |
| Tax (TDS) explanation | FR-5.1–FR-5.13 | PS-02, PS-03, PS-05 | 1 | Explain the applicable reasons and payroll calculation with source limits. Do not recommend a regime or investment. |
| Raise a query | FR-6.1–FR-6.13 | PS-02, PS-03, PS-05 | Not separately ranked in BRD 5.2; proposed support for priority 1 | Salary and TDS explanations refer to this flow when they cannot resolve an issue. Keep its complete existing draft, confirmation, tracking and HR response scope. Exact delivery and status transitions remain GAP-07 for Agent 05. |

## 3. MVP definition

### In: first release
- **High for scope:** Complete the back-dated hike and salary and TDS explanation flows, including their missing-data paths, calculation proof, approval or escalation limits. Complete each flow from request through its defined outcome before starting the next build stage. (BRD 5.2; FR-1.1–FR-1.17, FR-4.1–FR-4.17, FR-5.1–FR-5.13)
- **Proposed. Project owner decides:** Include the complete existing query flow as support for this release. This clarifies an unranked dependency; it does not move bonus or settlement ahead of priority 1. Do not present escalation as complete if employee confirmation, query tracking or the HR response path is absent. (FR-4.15, FR-5.12, FR-6.1–FR-6.13; PS-05; proposed change PBRD-04)
- **High for guardrails:** Identity checks, minimum necessary data, deterministic calculations, explicit HR approval, audit and honest uncertainty apply from the first release. They are not optional items for a later release. (BRD 8; GR-1.1–GR-8.1)

### Next
- **High for scope:** Bonus and incentives, end to end, after the first-priority flows. Resolve the applicable company policies and input gaps rather than treating statutory bonus rules as incentive rules. (BRD 5.2; FR-2.1–FR-2.19; BR-5.1–BR-5.5; EG-20–EG-22)

### Later
- **High for scope:** Full and final settlement, end to end, after bonus. Carry GAP-04 and GAP-09 into its design. Do not silently implement the proposed component model as if it were approved. (BRD 5.2; FR-3.1–FR-3.21; brief Section 9; DEC-004)

**High for project boundaries; Low for readiness:** GAP-01, GAP-02, GAP-03 and GAP-05 require rules-config clarification before build. GAP-06 and GAP-07 belong to Agent 05. GAP-08 and AS-10 through AS-13 belong to testing in Agent 08. These remain their main IDs; EG-11 through EG-18 are cross-references only. No gate is passed by this file. (Brief Section 9; DEC-001–DEC-002; G03 approval)

## 4. Requirements not linked to any problem

All six flow purposes have PS links. Some mandatory requirements address safety or specify an interaction choice without a direct problem statement establishing that particular need. Keep them and mark the evidence limit.

| Requirement | Direct PS link | Treatment and source |
|---|---|---|
| Plain-language request channel: FR-1.1, FR-2.1, FR-3.1, FR-4.1, FR-5.1, FR-6.1 | None for the channel preference itself | High for the requirement. The problems establish payroll needs, not a measured preference for a particular request channel. Retain the BRD choice. |
| Employee access limits: FR-4.3, FR-4.17, FR-5.2, FR-5.13; role and data controls GR-2.1–GR-2.6 | None for a directly evidenced personal privacy problem | High for mandatory controls. Employee AI data comfort remains unknown, not a reason to weaken access limits. (EG-05) |
| Employee control over query contents and sending: FR-6.5–FR-6.7; GR-1.3 | None for an observed loss-of-control complaint | High for the requirement. PS-05 supports query closure, but does not establish that these exact controls solve a measured complaint. Keep relevant evidence, removal and explicit confirmation. |
| Similar open query handling: FR-6.8 | None for an observed duplicate-query problem | High for the requirement. PS-05 is related context, not evidence of duplicate volume. Keep it; matching details remain GAP-07. |
| Security, advice limits and fictional data: GR-4.1–GR-5.4, GR-7.2, GR-8.1 | None as separate user pain statements | High for mandatory guardrails. Do not invent user fears or remove controls because a pain point is absent. |

Other functional requirements implement the mapped flow purposes, calculation basis, explanation or closure. Their prescribed mechanisms and success targets are BRD requirements, not proven solutions. The test baselines remain GAP-08. (FR-1.2–FR-1.17, FR-2.2–FR-2.19, FR-3.2–FR-3.21, FR-4.2–FR-4.16, FR-5.3–FR-5.12, FR-6.2–FR-6.13; BRD 10)

## 5. GAP-09 strategic direction

**Proposed. Project owner decides.** DEC-004 approves recording the gap; its resolution is open. The BRD's FR-3.5 connects a pending clearance to a related held amount. Vendor exit dependencies do not establish permission to hold wages. (Brief GAP-09; DEC-004; EVD-58, EVD-65; EG-25)

The research reports a separation-wages deadline of two working days and a distinct gratuity deadline of 30 days from when gratuity becomes payable. Reported effective date for both frameworks: **2025-11-21**. These are source reports, not verified classifications of this project's components. **Verify from official source before build.** Do not apply either deadline to the whole net settlement by default. (EVD-71, EVD-81; BRD 7, BR-0.1–BR-0.4)

| Option | Direction | Trade-offs |
|---|---|---|
| A. One combined completion state | Keep one overall settlement proposal and completion state. List pending clearances and related holds within it. Do not assume that a product's clearance rule permits delaying a due component. | Closer to the current overall summary. A single state can obscure which amount is ready or due while another remains unresolved. The source-reported different deadlines remain difficult to represent. Any hold still needs a verified basis. (FR-3.5, FR-3.14, FR-3.18–FR-3.20; EVD-58, EVD-65, EVD-71, EVD-81) |
| B. Component-level due dates and statuses | Keep one reconciled settlement summary, while separately identifying each payable or recovery component's basis, applicable due date and preparation or approval status. A clearance affects only a component where a verified rule permits it. | Makes unresolved components distinct from amounts whose basis is confirmed. Requires component classification and careful reconciliation so an overall total is not mistaken for an approved or paid amount. Clarity for HR and employees remains an assumption to test. This adds detail inside the existing flow, not a payment service. (FR-3.6–FR-3.20; EVD-59, EVD-61, EVD-68–EVD-69, EVD-71, EVD-81; AS-14) |

**Recommendation: Option B.** Separate components with their own applicable due dates and statuses, while retaining a reconciled overall summary and explicit HR approval. Do not let an unrelated clearance automatically place every amount on hold. Do not mark an amount ready for payroll until its required checks and approval are complete. If a component's rule or classification is unknown, flag and stop that part instead of inventing a due date or permission. (PS-01, PS-03–PS-05; GR-1.1–GR-1.2, GR-3.1–GR-3.5; FR-3.17–FR-3.20)

This recommendation does not determine which component is legally wages, authorize a deduction, confirm a deadline for every exit or execute a payment. Those unresolved bases must be verified before build. Agent 05 should detail the flow and states only after the Project owner's direction. The Project owner will update the BRD to v1.1 if needed. (DEC-004; GAP-04, GAP-09; EG-25; BRD 5.3)

## 6. Proposed BRD v1.1 changes

All four changes are **Proposed. Project owner decides.** No change is applied to input/.

| ID | Change | Reason | Source |
|---|---|---|---|
| PBRD-01 | Clarify FR-3.5: pending clearance does not automatically hold every settlement component. A related hold needs a verified applicable rule. If the basis is unknown, flag it and stop that part. | Clearance dependencies are operational evidence, not proof that a due wage component can be held. | GAP-09; DEC-004; EVD-65, EVD-71; GR-3.1, GR-3.3 |
| PBRD-02 | Clarify FR-3.14 and FR-3.18–FR-3.20: retain the overall reconciliation, distinguish component preparation and approval statuses and applicable due dates, and carry unresolved or permitted held components into the statement with their reasons. HR still approves; no payment execution is added. | One net figure or completion state can hide different component bases and deadlines. Understandability needs testing. | PS-03, PS-05; EVD-59, EVD-61, EVD-68–EVD-69, EVD-71, EVD-81; AS-14; GR-1.1–GR-1.2 |
| PBRD-03 | Extend the existing rule and exit-data definitions in BRD 7, 9.5 and 9.8, and settlement scenarios in 9.10, to record component classification, verified due-date basis and permitted hold basis. Cover an unresolved component alongside a confirmed component in mock tests. | Architecture needs a traceable basis for separate states and dates. No classification, rate or deadline should be guessed. | BR-0.1–BR-0.4; GR-3.3–GR-3.5; GAP-04, GAP-09; EVD-71, EVD-81; EG-25 |
| PBRD-04 | Clarify BRD 5.2 that existing Flow 6 is supporting scope for priority 1, with its complete draft, confirmation, tracking and HR response requirements. Retain hike and salary and TDS explanations first, bonus second and settlement third. | Flow 6 has no separate build priority, while both employee explanation flows require an escalation path. | FR-4.15, FR-5.12, FR-6.1–FR-6.13; PS-05; GAP-07 |

## 7. Risks and open questions
- **Low:** Component classification, permitted holds and due-date triggers remain EG-25 and GAP-09. Source-reported dates are not substitutes for official verification. The recommendation remains open for Project owner review. (EVD-65, EVD-71, EVD-81; DEC-004)
- **Low — Assumption AS-14:** HR and employees may understand component statuses and the net summary without confusing approval with payment. This benefit is unvalidated. Test it with real users and fictional scenarios in Agent 08. ([Assumption register](../01-project/assumptions.md))
- **Low:** No evidence supports moving bonus or settlement ahead of the BRD's first priority. The problem ranking is not the build sequence. The query placement is a proposed dependency clarification, not a measured value claim. (BRD 5.2; FR-4.15, FR-5.12; problem statements Section 4)
- **Low:** Company eligibility, proration and formula ownership remain unknown. Do not reuse statutory annual-bonus criteria as corporate incentive rules; statutory bonus stays out of scope. (PS-06; EG-20–EG-24; BR-5.5)
- **Low:** PF parameters, historical date splits, current TDS mapping, leave tax treatment and gratuity eligibility need rules-config clarification or verification before build. This run supplies no new legal evidence. (GAP-01–GAP-05; EVD-21–EVD-26, EVD-78–EVD-85; EG-23, EG-29)
- **Low:** Required handoffs, query delivery, settlement corrections and statement detail are not established. Ask Agent 02 for supporting evidence and carry flow details to Agent 05. (GAP-06–GAP-07; EG-09, EG-22, EG-27–EG-28)
- **Low:** Highest-pain stages AS-10 through AS-13, trust effects AS-4 and demo suitability AS-5 remain unvalidated. G03 approval did not validate them. Testing thresholds belong to Agent 08 through GAP-08.
