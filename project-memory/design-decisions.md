# Design Decision Log

- ID: DEC-001
- Date: 2026-10-12
- Decision: Carry the 8 brief gaps forward instead of resolving them before research.
- Options considered: (a) resolve all gaps now in the BRD, (b) carry them forward to the stage that owns them.
- Reason: The gaps are calculation details, flow details and testing details. They do not affect research. Each is assigned to the stage best placed to resolve it.
- Evidence or source: [output/01-project/project-brief.md](../output/01-project/project-brief.md), Section 9.
- Proposed by: Project owner
- Status: Approved
- Approved by: Project owner

- ID: DEC-002
- Date: 2026-10-12
- Decision: Use the brief's GAP IDs (GAP-01 to GAP-08) as the main record for calculation and workflow gaps. EG-11 to EG-18 are cross-references only.
- Options considered: (a) track both ID sets separately, (b) keep one main ID set and cross-reference the other.
- Reason: One gap should have one owner and one ID, to avoid duplicate work and confusion in later stages.
- Evidence or source: [output/02-research/secondary-research.md](../output/02-research/secondary-research.md), Section 3.
- Proposed by: Project owner
- Status: Approved
- Approved by: Project owner

- ID: DEC-003
- Date: 2026-10-12
- Decision: Present historical input checking for HR and record comparison for employees as provisional main opportunity areas. Keep their highest-pain rankings as unvalidated assumptions AS-10 and AS-11.
- Options considered: (a) emphasize calculation and approval for HR, and HR contact for employees, (b) emphasize historical input checking and record comparison as provisional areas, (c) defer all highest-pain selections until testing.
- Reason: The approved evidence documents input reconciliation problems and conflicting employee records. It does not measure relative stage pain. The journey skill requires a highest-pain selection, so these selections remain explicit assumptions for review and validation in Agent 08.
- Evidence or source: [output/02-research/secondary-research.md](../output/02-research/secondary-research.md), EVD-03 through EVD-05, EVD-17, EVD-18 and EG-01 through EG-04; [output/01-project/assumptions.md](../output/01-project/assumptions.md), existing AS-6.
- Proposed by: Agent 03 (Analysis)
- Status: Approved
- Approved by: Project owner

- ID: DEC-004
- Date: 2026-10-12
- Decision: Record GAP-09: the BRD's settlement hold rule (FR-3.5) may conflict with the 2-working-day separation wages rule. Settlement may need to be split into components with separate due dates and statuses.
- Owner: Agent 04 (Strategy) and Agent 05 (Architecture)
- Options considered: (a) retain one combined settlement hold state, (b) review settlement components separately with their applicable due dates and statuses.
- Reason: The new research distinguishes separation wages from other settlement items and documents clearance dependencies. The potential conflict needs review before choosing a hold or component-splitting approach. Applicability and permitted holds have not been verified.
- Evidence or source: [input/research/desk-research-bonus-settlement.pdf](../input/research/desk-research-bonus-settlement.pdf), pages 7–8 and 12–13; [output/02-research/secondary-research.md](../output/02-research/secondary-research.md), EVD-65, EVD-71, EVD-81 and EG-25; FR-3.5 as identified in Project owner's update instruction.
- Rule effective date reported by research: 2025-11-21; verify from official source before build.
- Follow-up: Project owner will update the BRD to version 1.1 if needed.
- Proposed by: Agent 02 (Research)
- Status: Approved (gap recorded; resolution open)
- Approved by: Project owner

- ID: DEC-005
- Date: 2026-10-13
- Decision: Extend the provisional opportunity selections in DEC-003 to bonus and settlement. Present variable-pay input preparation and exit-input reconciliation as candidates. Keep their highest-pain rankings as unvalidated assumptions AS-12 and AS-13.
- Options considered: (a) emphasize approvals and final processing, (b) emphasize input preparation and reconciliation as provisional areas, (c) defer both selections until testing.
- Reason: The approved research documents spreadsheet risks, imported input dependencies and several settlement records and exit prerequisites. It does not compare stage pain. These selections meet the requested journey format while keeping the ranking and combined stage sequences open for validation in Agent 08.
- Evidence or source: [output/02-research/secondary-research.md](../output/02-research/secondary-research.md), EVD-49 through EVD-52, EVD-57, EVD-58, EVD-61, EVD-65, EVD-66, EG-01, EG-10 and EG-26; [output/03-analysis/journey-maps.md](../output/03-analysis/journey-maps.md), Sections 3 and 4; [output/01-project/assumptions.md](../output/01-project/assumptions.md), AS-12 and AS-13. DEC-003 remains unchanged.
- Proposed by: Agent 03 (Analysis)
- Status: Approved
- Approved by: Project owner

- ID: DEC-006
- Date: 2026-10-13
- Decision: Propose six problem groups: five evidence-backed and one requirements-led bonus-policy problem. Rank consistent inputs (PS-01) first, followed by record trust (PS-03), received-amount explanations (PS-02), calculation basis (PS-04), unresolved work (PS-05) and bonus policy cases (PS-06).
- Options considered: (a) one statement per pain point, (b) group related pains and rank by evidence and the input-gathering and record-trust insight, (c) rank by assumed time or business value.
- Reason: Grouping connects the approved journeys without repeating every pain point. The research supports problems but not relative effort or value. Keep the requirements-led policy problem visible despite missing user evidence. This extends DEC-003 and DEC-005 without validating AS-10 through AS-13.
- Evidence or source: [problem-statements.md](../output/04-strategy/problem-statements.md), Sections 2–4; PP-01 through PP-21; EVD-03 through EVD-05, EVD-17, EVD-18, EVD-49 through EVD-51, EVD-57, EVD-68; EG-01, EG-04, EG-21; FR-2.4 through FR-2.8.
- Proposed by: Agent 04 (Strategy)
- Status: Approved
- Approved by: Project owner

- ID: DEC-007
- Date: 2026-10-13
- Decision: Retain the BRD build order and propose the complete existing query flow as supporting scope for the first employee explanation flows. Clarify its placement in BRD 5.2 through proposed change PBRD-04.
- Options considered: (a) retain the unranked query placement without clarification, (b) include existing Flow 6 with priority 1 because the employee flows depend on it, (c) move bonus or settlement ahead of the first priority.
- Reason: Salary and TDS explanations require escalation to Flow 6 when unresolved. The BRD does not separately rank that flow. No evidence justifies moving bonus or settlement earlier. This is a dependency proposal, not a new flow or an estimate of feasibility.
- Evidence or source: [mvp-scope.md](../output/04-strategy/mvp-scope.md), Sections 2–4 and PBRD-04; BRD 5.2; FR-4.15, FR-5.12, FR-6.1 through FR-6.13; PS-05; GAP-07.
- Proposed by: Agent 04 (Strategy)
- Status: Approved
- Approved by: Project owner

- ID: DEC-008
- Date: 2026-10-13
- Decision: Recommend Option B for GAP-09: retain one reconciled settlement summary while separating component bases, applicable due dates and statuses. Recommend proposed BRD clarifications PBRD-01 through PBRD-03 for Project owner review.
- Options considered: (a) one combined completion state with pending clearances and related holds, (b) component-level due dates and statuses within the existing settlement flow.
- Reason: The approved evidence distinguishes operational exit dependencies from source-reported component deadlines. A combined state can obscure the unresolved basis of a component. Understanding the proposed model is unvalidated in AS-14. Classification, permitted holds and date triggers remain open; this recommendation does not authorize a hold or payment.
- Evidence or source: [mvp-scope.md](../output/04-strategy/mvp-scope.md), Sections 5–7; brief GAP-09; DEC-004 Approved (gap recorded; resolution open); EVD-58, EVD-59, EVD-61, EVD-65, EVD-68, EVD-69, EVD-71, EVD-81; EG-25, EG-27; FR-3.5, FR-3.14 through FR-3.20; BR-0.1 through BR-0.4; GR-1.1, GR-3.3.
- Rule effective date reported by research: 2025-11-21 for the separation-wages and gratuity frameworks; verify from official source before build.
- Owner: Agent 04 (Strategy) and Agent 05 (Architecture). Project owner decides the direction and updates the BRD to v1.1 if needed.
- Proposed by: Agent 04 (Strategy)
- Status: Approved
- Approved by: Project owner

- ID: DEC-009
- Date: 2026-10-13
- Decision: Propose UXP-01 through UXP-07 as design rules for checking inputs, tracing periods and rules, explaining net changes, requiring approval, exposing unresolved settlement components, escalating with proof and limiting data access.
- Options considered: (a) use generic usability slogans, (b) use seven payroll-specific rules with examples and source limits.
- Reason: These rules help compare design options using the approved problems and mandatory BRD guardrails. They do not prove a trust increase or approve the proposed component model. The component direction remains subject to DEC-008 and AS-14.
- Evidence or source: [ux-principles.md](../output/04-strategy/ux-principles.md); PS-01 through PS-05; PP-01 through PP-21 as cited there; GR-1.1 through GR-8.1; AS-3, AS-4, AS-14.
- Proposed by: Agent 04 (Strategy)
- Status: Approved
- Approved by: Project owner

- ID: DEC-010
- Date: 2026-10-13
- Decision: Approve proposed BRD changes PBRD-01 to PBRD-04 and create BRD v1.1.
- Options considered: (a) keep BRD v1.0 without the proposed clarifications, (b) apply PBRD-01 through PBRD-04 in a new v1.1 file and preserve v1.0.
- Reason: Section 6 of MVP scope records the approved reasons: clearance holds need a verified basis, separate component states and dates must remain reconciled, rule and exit data need traceable component bases, and the existing query flow supports priority 1. Approved at Gate G04.
- Evidence or source: [output/04-strategy/mvp-scope.md](../output/04-strategy/mvp-scope.md), Section 6, PBRD-01 through PBRD-04; [input/requirements/Payroll_brd_v1.1.md](../input/requirements/Payroll_brd_v1.1.md), Change log. DEC-008 records the approved Option B direction; DEC-007 remains an unchanged proposal record for query placement.
- Proposed by: Project owner
- Status: Approved
- Approved by: Project owner

- ID: DEC-011
- Date: 2026-10-13
- Decision: Propose GAP-06 Option B: store a durable readiness reference to the explicitly approved calculation version and scope, with authorized HR responsible for that record. No external payroll application or payment is added.
- Options considered: (a) store only a readiness flag with an implicit calculation reference, (b) store the approved version, scope, actor and time.
- Reason: A readiness flag alone can lose the distinction between calculation versions. Explicit approval must remain tied to its basis. This proposal specifies the existing ready-for-payroll outcome without inventing an external handoff actor or second approver.
- Evidence or source: [user-flows.md](../output/05-architecture/user-flows.md), Section 4; GAP-06; FR-1.16, FR-1.17, FR-2.18, FR-2.19, FR-3.21; BR-7.1 through BR-7.3; GR-1.1; BRD v1.1 Section 5.3.
- Proposed by: Agent 05 (Architecture)
- Status: Approved
- Approved by: Project owner

- ID: DEC-012
- Date: 2026-10-13
- Decision: Propose GAP-07 Option B: persist employee-confirmed queries for authorized HR access, offer conservative own-query candidates and use explicit Sent, In review, Resolved and Closed transitions with safe retries.
- Options considered: (a) leave delivery unspecified and compare descriptions broadly, (b) define internal delivery, same-employee category and month candidates, Employee add-or-new choice and explicit state actions.
- Reason: The BRD requires confirmation, duplicate choice, status lookup and HR replies. Exact routing and transitions are open. Candidate usefulness remains unvalidated in AS-15, and no response time or external message channel is invented.
- Evidence or source: [user-flows.md](../output/05-architecture/user-flows.md), Section 5; [edge-cases-states.md](../output/05-architecture/edge-cases-states.md), Sections 4 and 7; GAP-07; FR-6.6 through FR-6.13; GR-1.3, GR-2.1 through GR-2.5, GR-7.1.
- Proposed by: Agent 05 (Architecture)
- Status: Approved
- Approved by: Project owner

- ID: DEC-013
- Date: 2026-10-13
- Decision: Propose GAP-04 Option B: calculate final-month earned salary with the full calendar-month divisor and scoped eligible days through the last working day, less LOP in that period. Release a permitted held component through a new version, recalculation and fresh HR review and approval.
- Options considered: (a) use the shortened period as divisor and reuse approval on clearance, (b) retain the calendar-month divisor with scoped inputs and require fresh review of a release version.
- Reason: BR-1.2 gives a calendar-month divisor while BR-6.1 limits work to the last working day. Whole-month LOP cannot be allocated by guessing. Clearance completion can change the component basis or dependent totals, so it must not automatically inherit approval.
- Evidence or source: [edge-cases-states.md](../output/05-architecture/edge-cases-states.md), Section 8; GAP-04; FR-3.4 through FR-3.6, FR-3.13 through FR-3.21; BR-1.1, BR-1.2, BR-6.1, BR-7.1 through BR-7.3; GR-1.1, GR-1.2, GR-3.3.
- Proposed by: Agent 05 (Architecture)
- Status: Approved
- Approved by: Project owner

- ID: DEC-014
- Date: 2026-10-13
- Decision: Propose the seven-state HR proposal lifecycle and explicit settlement component preparation and approval scopes. Preserve historical approvals, recheck changed dependencies and keep incomplete totals distinct from valid approved scope.
- Options considered: (a) use one mutable proposal status and overall completion label, (b) use version-linked approval records with scoped component preparation and approval states.
- Reason: Approved Option B requires component bases, due dates and statuses. Missing components must not become zero or an apparently complete net, and approval must not imply payment. The exact names, scoped approval guards and correction-version behavior remain recommendations for G05.
- Evidence or source: [edge-cases-states.md](../output/05-architecture/edge-cases-states.md), Sections 2, 3 and EC-18; approved DEC-008 and DEC-010; FR-1.13 through FR-1.17, FR-2.16 through FR-2.19, FR-3.14 through FR-3.21; BR-7.1 through BR-7.3; GR-1.1, GR-1.2, GR-3.3.
- Proposed by: Agent 05 (Architecture)
- Status: Approved
- Approved by: Project owner

- ID: DEC-015
- Date: 2026-10-13
- Decision: The employee-facing explanation of the settlement statement (FR-3.20) is designed by Agent 06 as part of Flow 3's output. Employee follow-up questions about the statement use Flow 6 (Query). Employee portal access after the last working day is out of scope.
- Options considered: (a) add a new employee settlement flow, (b) explain the statement within Flow 3 and route questions through Flow 6.
- Reason: Covers PP-21 and PS-03 without adding a flow outside BRD v1.1.
- Evidence or source: [pain-points.md](../output/03-analysis/pain-points.md), PP-21; [problem-statements.md](../output/04-strategy/problem-statements.md), PS-03; [secondary-research.md](../output/02-research/secondary-research.md), EVD-68; [BRD v1.1](../input/requirements/Payroll_brd_v1.1.md), FR-3.20 and FR-6.1 to FR-6.13.
- Proposed by: Project owner
- Status: Approved
- Approved by: Project owner

- ID: DEC-016
- Date: 2026-10-13
- Decision: Propose scope-first explanations with five detail layers and system-derived certainty labels. Keep certainty separate from the approved proposal, component and query lifecycle states.
- Options considered: (a) show all detail at once with AI confidence scores, (b) use layered detail with source access from the first amount and certainty labels tied to system facts.
- Reason: Employees need the recorded net or TDS change first, while HR must know the proposal scope and blockers before reviewing. Input availability and verified rule status explain a limit without a model rating itself. Understanding these labels remains AS-16; trust benefit remains AS-4.
- Evidence or source: [trust-explainability.md](../output/06-ai-interaction/trust-explainability.md), Sections 2–7; FR-1.10–FR-1.13, FR-4.4–FR-4.13, FR-5.3–FR-5.10; GR-3.1–GR-3.5; UXP-01–UXP-05; EVD-31, EVD-35, EVD-41; EG-04, EG-07; approved DEC-014.
- Proposed by: Agent 06 (AI Interaction)
- Status: Approved
- Approved by: Project owner

- ID: DEC-017
- Date: 2026-10-13
- Decision: Propose explicit version-and-scope wording for HR review, partial approval and release review, content-bound Employee query confirmation, and failure messages tied to observed system conditions and existing authorized recovery.
- Options considered: (a) use generic success, approval and error messages, (b) name the reviewed scope, excluded or blocked work, action consequence and responsible actor under the approved architecture.
- Reason: Generic wording can conceal incomplete totals or imply approval, sending or payment before the authorized action is stored. The content follows DEC-011 through DEC-014 without changing their states or powers. Understanding remains untested in AS-14 and AS-16. Statement delivery and follow-up access after portal access ends are recorded for Agent 05 rather than filled with a new flow.
- Evidence or source: [approval-failure-handling.md](../output/06-ai-interaction/approval-failure-handling.md), Sections 2–8; FR-1.14–FR-1.17, FR-2.16–FR-2.19, FR-3.5, FR-3.19–FR-3.21, FR-6.6–FR-6.13; GR-1.1–GR-1.3, GR-3.3–GR-3.4, GR-5.3; UXP-04–UXP-07; approved DEC-011 through DEC-015; [edge-cases-states.md](../output/05-architecture/edge-cases-states.md), Sections 2–5 and EC-18.
- Proposed by: Agent 06 (AI Interaction)
- Status: Approved
- Approved by: Project owner

- ID: DEC-018
- Date: 2026-10-13
- Decision: Propose direct, precise HR language and plain, change-first Employee language, with short payroll meanings, one clarifying question at a time and five fictional conversation scripts using unfilled, labeled numeric result slots.
- Options considered: (a) use one generic voice and fixed invented example amounts, (b) use role-specific emphasis and illustrative placeholders that must be populated from authorized records and Calculation code in a working demo.
- Reason: The provisional personas support different task emphasis without proving tone preferences. Unfilled illustrative slots avoid presenting invented amounts as computed results. The scripts cover four priority 1 flows and a missing-data failure. They are not executed tests, observed users or new requirements. Wording usefulness remains AS-17.
- Evidence or source: [conversation-design.md](../output/06-ai-interaction/conversation-design.md), Sections 2–8; [personas.md](../output/03-analysis/personas.md), goals, needs and Unknowns; FR-1.2, FR-4.4–FR-4.16, FR-5.3–FR-5.12, FR-6.4–FR-6.11; GR-3.1–GR-3.2, GR-4.1–GR-4.3, GR-8.1; UXP-03, UXP-06–UXP-07; EG-04.
- Proposed by: Agent 06 (AI Interaction)
- Status: Approved
- Approved by: Project owner

- ID: DEC-019
- Date: 2026-10-13
- Decision: The settlement statement is available to the employee in HCM One while they still have access. Delivery after the last working day happens through the company's existing exit process, outside HCM One. Follow-up questions use Flow 6 only while the employee has access. No new channel or portal is added.
- Options considered: (a) add a post-exit access channel, (b) keep statement access within existing access and leave post-exit delivery to the company's exit process.
- Reason: Resolves the open DEC-015 boundary without adding a flow or channel outside BRD v1.1.
- Evidence or source: [Design decision log](design-decisions.md), DEC-015; [BRD v1.1](../input/requirements/Payroll_brd_v1.1.md), FR-3.20; FR-6.1 to FR-6.13.
- Proposed by: Project owner
- Status: Approved
- Approved by: Project owner

- ID: DEC-020
- Date: 2026-10-13
- Decision: GAP-02 resolved: September split by calendar days. Days before the ceiling change use the old ceiling. Days from the change use the new ceiling. Each segment is pro-rated by days.
- Options considered: Not specified in the Project owner's instruction.
- Reason: Record the Project owner's approved simplified calculation rule for the mid-month ceiling split in the demo rules config.
- Evidence or source: Project owner rules setup instruction, 2026-10-13; [pf-rules.json](../data/rules/pf-rules.json), mid_month_ceiling_change; [project brief](../output/01-project/project-brief.md), GAP-02.
- Proposed by: Project owner
- Status: Approved
- Approved by: Project owner

- ID: DEC-021
- Date: 2026-10-13
- Decision: GAP-03 resolved: proportional hike allocation, mid-month pro-rating by calendar days, and rounding each line to the nearest rupee before adding rounded lines for totals.
- Options considered: Not specified in the Project owner's instruction.
- Reason: Record the Project owner's approved simplified rules for hike allocation, partial months and rounding order in the demo rules config.
- Evidence or source: Project owner rules setup instruction, 2026-10-13; [company-settings.json](../data/rules/company-settings.json), hike_allocation, mid_month_hike and rounding; [project brief](../output/01-project/project-brief.md), GAP-03.
- Proposed by: Project owner
- Status: Approved
- Approved by: Project owner

- ID: DEC-022
- Date: 2026-10-13
- Decision: GAP-05 resolved: new regime only; negative remaining tax gives monthly TDS 0 with the flag "Excess tax is claimed through the tax return, not payroll."; the last month deducts all remaining tax; past-year arrears are taxed in the year received, with relief claims out of scope.
- Options considered: Not specified in the Project owner's instruction.
- Reason: Record the Project owner's approved simplified tax scope and edge-case handling in the demo rules config. Tax-year applicability, slabs, deduction, rebate and cess retain their supplied verification status.
- Evidence or source: Project owner rules setup instruction, 2026-10-13; [tax-rules.json](../data/rules/tax-rules.json); [project brief](../output/01-project/project-brief.md), GAP-05; [BRD v1.1](../input/requirements/Payroll_brd_v1.1.md), BR-4.3.
- Proposed by: Project owner
- Status: Approved
- Approved by: Project owner

- ID: DEC-023
- Date: 2026-10-13
- Decision: Reframe BRD scenario 10 to a previous-employer income declaration, and add BR-4.5 (new regime only), in BRD v1.2.
- Options considered: (a) reframe scenario 10, (b) add the old tax regime for one employee.
- Reason: The new-regime-only decision (GAP-05) made the original scenario 10 unrealistic. Reframing keeps the same test purpose without adding a second tax calculation.
- Evidence or source: [Design decision log](design-decisions.md), GAP-05 decision DEC-022; [tax-rules.json](../data/rules/tax-rules.json); [BRD v1.1](../input/requirements/Payroll_brd_v1.1.md), Section 9.10.
- Proposed by: Project owner
- Status: Approved
- Approved by: Project owner

- ID: DEC-024
- Date: 2026-10-13
- Decision: Resolve missing rules MR-01 to MR-08 before writing calculation code.
- Options considered: for each rule, the options are recorded in the Project owner's decisions on 2026-10-13.
- Reason: Without these rules, calculation code would have to guess. Every rule is now explicit, versioned and traceable.
- Evidence or source: [data/mock/README.md](../data/mock/README.md), Missing rules; [data/rules/](../data/rules/).
- Proposed by: Project owner
- Status: Approved
- Approved by: Project owner

- ID: DEC-025
- Date: 2026-10-13
- Decision: Resolve engine ambiguities AMB-01 (round half up), AMB-02 (LOP spread evenly, PF capped per dated segment) and AMB-03 (proposal TDS estimated for the next open payroll month, with the assumption shown).
- Options considered: AMB-01: round half up or half to even. AMB-02: spread LOP evenly or require dated LOP. AMB-03: estimate with a stated assumption or keep TDS blocked.
- Reason: Each rule is simple, explainable to users and keeps every number traceable without guessing.
- Evidence or source: [data/generated/ambiguities.json](../data/generated/ambiguities.json); [engine/README.md](../engine/README.md), Ambiguities found.
- Proposed by: Project owner
- Status: Approved
- Approved by: Project owner

- ID: DEC-026
- Date: 2026-10-13
- Decision: Use six prototype screens: three HR desktop screens and three Employee mobile screens. Reuse request and review modes for later bonus and settlement. Keep calculation drawers, detail sheets and confirmation panels within their parent screen.
- Options considered: (a) a separate screen for each flow and action, (b) shared screens with the approved flow-specific fields and states.
- Reason: The approved steps share capture, review, proof and confirmation needs. Reuse keeps the inventory lean without removing those steps or adding a flow. This is a proposed layout choice, not a tested usability result.
- Evidence or source: [Screen inventory](../output/07-prototype/screen-inventory.md), Sections 2–4; [user flows](../output/05-architecture/user-flows.md), Section 3; [MVP scope](../output/04-strategy/mvp-scope.md), Sections 2–3; DEC-015 and DEC-019; FR-1.1–FR-6.13.
- Proposed by: Agent 07 (Prototype)
- Status: Approved
- Approved by: Project owner

- ID: DEC-027
- Date: 2026-10-13
- Decision: Use deep teal #0F766E as the single brand accent, Inter for interface text and IBM Plex Mono for financial numbers. Use white space and prominent sourced amounts, with separate text-and-icon certainty and workflow labels.
- Options considered: (a) dense panels and charts, (b) typography-led layouts with progressive calculation detail.
- Reason: This implements the required minimal design direction and the approved outcome-first explanation. Color does not substitute for a status label. Font availability, accessibility in the actual design and user comprehension still need verification.
- Evidence or source: [Agent 07](../agents/07-prototype.md), Design direction; [visual specification](../output/07-prototype/visual-spec.md), Sections 1–6; UXP-02–UXP-04 and UXP-07; DEC-016; AS-16 and AS-17.
- Proposed by: Agent 07 (Prototype)
- Status: Approved (typography superseded by DEC-031)
- Approved by: Project owner

- ID: DEC-028
- Date: 2026-10-13
- Decision: Show generated calculations as unapproved fixture previews. Display unavailable numeric request and event fields as "Not available in generated data". Keep version-bound approval and successful-send states conditional on actual recorded events. For scenario 10, use existing generic approved AI wording with the sourced previous-employer-income heading and refer the stale illustrative cause to Agent 06.
- Options considered: (a) show only available result fields and omit incomplete request or event states, (b) specify those states with visible unavailable fields and retain the existing guards.
- Reason: The design must cover the approved flow while every displayed number remains a literal generated value. A complete calculation cannot supply missing confirmation inputs, an approval or a query delivery event. The BRD v1.2 cause must not be replaced by the old illustrative script or newly invented AI wording.
- Evidence or source: [Screen specifications](../output/07-prototype/screen-specs.md), content contract, Sections 1–7 and 9; [Figma prompts](../output/07-prototype/figma-ai-prompts.md); [scenario 10](../data/generated/scenarios/scenario-10.json), scenario-10 /result; [current BRD v1.2](../input/requirements/Payroll_brd_v1.2.md), Section 9.10; DEC-011, DEC-014, DEC-017 and DEC-023; Agent 07 Boundaries.
- Proposed by: Agent 07 (Prototype)
- Status: Approved
- Approved by: Project owner

- ID: DEC-029
- Date: 2026-10-14
- Decision: Update the Agent 06 TDS example and A06-10 wording to the previous-employer income reason, matching BRD v1.2 scenario 10.
- Options considered: Not specified in the Project owner's instruction.
- Reason: Agent 07 found that the approved TDS script used the old scenario 10 cause.
- Evidence or source: [Screen specifications](../output/07-prototype/screen-specs.md), Section 9, open questions; [Design decision log](design-decisions.md), DEC-023.
- Proposed by: Project owner
- Status: Approved
- Approved by: Project owner

- ID: DEC-030
- Date: 2026-10-14
- Decision: Code prototype first; Figma is optional later for visual polish and case study images. figma-ai-prompts.md is kept as a bonus.
- Options considered: Not specified in the Project owner's instruction.
- Reason: Project owner selected the implementation direction while retaining the Figma prompts for optional later use.
- Evidence or source: Project owner instruction, 2026-10-14; [prototype screen specifications](../output/07-prototype/screen-specs.md); [Figma AI prompts](../output/07-prototype/figma-ai-prompts.md).
- Proposed by: Project owner
- Status: Approved
- Approved by: Project owner

- ID: DEC-031
- Date: 2026-10-14
- Decision: Typography: Inter with tabular figures; monospace only for IDs.
- Options considered: Not specified in the Project owner's instruction.
- Reason: Tabular figures align numbers in columns and feel calmer for payroll; monospace is kept for technical IDs.
- Evidence or source: Project owner instruction, 2026-10-14; [visual specification](../output/07-prototype/visual-spec.md), Section 1; [Figma AI prompts](../output/07-prototype/figma-ai-prompts.md).
- Proposed by: Project owner
- Status: Approved
- Approved by: Project owner

- ID: DEC-032
- Date: 2026-10-23
- Decision: Build HCM One clickable prototype using FastAPI backend (`app/backend/`) and React + TypeScript + Vite frontend (`app/frontend/`) with Radix UI unstyled primitives, strictly deterministic engine calculations (`engine/payroll/`), and zero LLM calls. UI assistant copy is strictly limited to approved sentences C01–C29 with runtime slot interpolation. Runtime state (events, proposals, queries) persists exclusively in `data/runtime/` with demo reset capability.
- Options considered: (a) Static mockup with hardcoded state, (b) Full stack React/Vite + FastAPI backed by deterministic engine calculations and runtime event store.
- Reason: Satisfies all prototype requirements across 13 scenarios and 6 screens while preserving immutability of mock and rule data, ensuring zero frontend math, preventing unauthorized access via server-side RBAC, and enforcing strict governance (C04 approval warning, C05 revision warning, C25 stale version guard).
- Evidence or source: [app/README.md](../app/README.md), [app/frontend/](../app/frontend/), [app/backend/](../app/backend/), [engine/payroll/](../engine/payroll/), DEC-028, DEC-029, DEC-030, DEC-031.
- Proposed by: Prototype Agent
- Status: Approved
- Approved by: Project owner

- ID: DEC-033
- Date: 2026-10-23
- Decision: Every number on screen is verified by automated tests against the API. The frontend never contains payroll data.
- Options considered: (a) Hardcoded fallback or presentation values in frontend components, (b) Zero hardcoded numbers in frontend source; every figure sourced dynamically from the backend/engine and strictly verified by automated Vitest suite.
- Reason: Design review found fabricated numbers on screen (e.g., hardcoded CTC, fictitious net pay, invented leave story). HCM One architectural principles mandate zero frontend payroll calculations or data fabrication; all figures must originate from the deterministic payroll engine and backend API.
- Evidence or source: [app/frontend/src/tests/screens_api_match.test.tsx](../app/frontend/src/tests/screens_api_match.test.tsx), `data/generated/scenarios/`, [output/07-prototype/screen-specs.md](../output/07-prototype/screen-specs.md).
- Proposed by: Prototype Agent
- Status: Approved
- Approved by: Project owner

- ID: DEC-034
- Date: 2026-10-23
- Decision: Prototype changes from six screens to a chat-first design with rich cards (CHAT-HR, CHAT-EMP), because HCM One is an agentic chatbot and the class submission requires a chatbot experience. Heavy review moves into side panels and sheets. General payroll questions are answered from a payroll FAQ knowledge source in the course dataset format.
- Options considered: (a) Retain six static application screens with embedded forms, (b) Transition to two chat surfaces (CHAT-HR desktop 1440 px with side panel, CHAT-EMP mobile 390 px with bottom sheet) featuring 14 rich card types and general payroll FAQ support.
- Reason: HCM One is designed as an agentic AI assistant, and the class submission requires a true chatbot experience. Moving heavy review (multi-month tables, settlement ledgers, calculation formulas) into collapsible side panels and sheets keeps conversational threads clean and responsive while maintaining strict mathematical transparency.
- Evidence or source: Project owner instruction, 2026-10-23; [output/07-prototype/screen-inventory.md](../output/07-prototype/screen-inventory.md); [output/07-prototype/screen-specs.md](../output/07-prototype/screen-specs.md); [output/07-prototype/visual-spec.md](../output/07-prototype/visual-spec.md); [output/07-prototype/figma-ai-prompts.md](../output/07-prototype/figma-ai-prompts.md).
- Proposed by: Project owner
- Status: Approved
- Approved by: Project owner

- ID: DEC-035
- Date: 2026-10-23
- Decision: C30 added so explanations lead with the change, per UXP-03.
- Options considered: (a) Start salary/TDS explanation with breakdown offer C27 or period limitation C26, (b) Introduce approved sentence C30 ("Your {later month} take-home is {net change amount} {lower or higher} than {earlier month}. The main recorded reasons are below.") so the assistant immediately states the bottom-line change before presenting causal cards.
- Reason: Implements UXP-03 ("Lead with the change, not the calculation"). Employees asking about a pay drop need the bottom-line difference confirmed first. C27 moves to the end of the turn as the follow-up breakdown offer.
- Evidence or source: Project owner instruction, 2026-10-23; [UX principles](../output/04-strategy/ux-principles.md), UXP-03; [conversation-design.md](../output/06-ai-interaction/conversation-design.md), Section 7, A06-07; [screen-specs.md](../output/07-prototype/screen-specs.md), Section 7, C30.
- Proposed by: Project owner
- Status: Approved
- Approved by: Project owner

- ID: DEC-036
- Date: 2026-10-23
- Decision: General payroll questions are answered from data/knowledge/payroll_faq.json, in the course FAQ format, built only from approved content.
- Options considered: (a) Allow AI model to answer general payroll questions from unstructured weights or ad-hoc prompts, (b) Restrict general payroll Q&A to a curated, validated knowledge file in the course dataset format containing 30 entries built strictly from approved project sources with zero digits, verified sources, and explicit action links.
- Reason: Enforces strict epistemic boundaries and avoids hallucination. Answers are limited to approved glossary definitions, certainty label meanings, query lifecycle steps, settlement rules, and privacy guardrails. All answers use simple English without numbers or personal advice.
- Evidence or source: Project owner instruction, 2026-10-23; [payroll_faq.json](../data/knowledge/payroll_faq.json); [validate_faq.py](../data/knowledge/validate_faq.py); [conversation-design.md](../output/06-ai-interaction/conversation-design.md) Section 6; [trust-explainability.md](../output/06-ai-interaction/trust-explainability.md) Section 4 & 6; [Payroll_brd_v1.2.md](../input/requirements/Payroll_brd_v1.2.md) Section 8.
- Proposed by: Project owner
- Status: Approved
- Approved by: Project owner

- ID: DEC-037
- Date: 2026-10-23
- Decision: The chat uses one /api/chat contract. A deterministic router answers it now; the CrewAI crew will replace only the router in step 4.
- Options considered: (a) Multiple custom endpoints for different chat actions, screens, and card types, (b) Single unified `/api/chat` contract returning assistant messages (approved sentence codes + rendered text), cards, suggestion chips, and state changes, handled now by a deterministic router and later by the CrewAI crew.
- Reason: Establishes a clean, stable API schema (`app/backend/chat_contract.md`) for the chat-first prototype. The frontend interacts strictly with this single endpoint. The deterministic router handles all 13 BRD v1.2 scenarios, role-based access checks, FAQ retrieval, and guardrails with 100% predictability for testing now, allowing the CrewAI agentic crew to replace only the router implementation in step 4 without breaking the contract or frontend components.
- Evidence or source: Project owner instruction, 2026-10-23; [chat_contract.md](../app/backend/chat_contract.md); [chat_router.py](../app/backend/chat_router.py); [test_chat_endpoint.py](../app/backend/tests/test_chat_endpoint.py).
- Proposed by: Project owner
- Status: Approved
- Approved by: Project owner

- ID: DEC-038
- Date: 2026-10-24
- Decision: Both chats are responsive: desktop layout with a side panel, and on mobile the panel becomes a bottom sheet.
- Options considered: (a) Keep a fixed phone frame for CHAT-EMP and a desktop screen for CHAT-HR, (b) Single unified responsive layout system for both CHAT-HR and CHAT-EMP: desktop (>= 1024 px) full-width workspace with 480 px right side panel, tablet (768–1023 px) with 520 px overlay panel, and mobile (< 768 px) where chat fills the screen, the panel becomes an accessible bottom sheet, composer stays docked at bottom, and tables switch to a stacked card layout without horizontal scrolling.
- Reason: Project owner decision. Removes artificial device frames. Both employee and HR workspaces adapt naturally to any screen width while maintaining identical content, cards, numbers, actions, rules, and WCAG 2.2 AA accessibility (min 44 px touch targets). Breakpoints and dimensions are centralized in tokens.css.
- Evidence or source: Project owner instruction, 2026-10-24; [output/07-prototype/screen-inventory.md](../output/07-prototype/screen-inventory.md); [output/07-prototype/visual-spec.md](../output/07-prototype/visual-spec.md); [tokens.css](../app/frontend/src/design-system/tokens.css); [components.css](../app/frontend/src/design-system/components.css); [responsive_dark_theme.test.tsx](../app/frontend/src/tests/responsive_dark_theme.test.tsx).
- Proposed by: Project owner
- Status: Approved
- Approved by: Project owner

- ID: DEC-039
- Date: 2026-10-24
- Decision: The app uses a dark theme only, built by changing token values. A light theme can be added later the same way.
- Options considered: (a) Light theme only, (b) Light/dark theme toggle, (c) Single high-contrast dark theme configured purely via token values in tokens.css without modifying component logic, with no light theme and no toggle.
- Reason: Project owner decision. Centralizing all colors in design tokens allows instantaneous theme definition. Avoiding pure black (#000000) prevents eye strain; deep slate-navy surfaces (#0B0F19, #111827) provide depth and crisp tabular financial figures (#F8FAFC, 17:1 AAA contrast). Semantic status badges use dark surfaces with high-luminance text (> 5.9:1 to 8.6:1), ensuring status is never conveyed by color alone. A light theme can be reintroduced cleanly in the future simply by defining an alternate token map.
- Evidence or source: Project owner instruction, 2026-10-24; [tokens.css](../app/frontend/src/design-system/tokens.css); [output/07-prototype/visual-spec.md](../output/07-prototype/visual-spec.md); [responsive_dark_theme.test.tsx](../app/frontend/src/tests/responsive_dark_theme.test.tsx).
- Proposed by: Project owner
- Status: Approved
- Approved by: Project owner

- ID: DEC-040
- Date: 2026-10-24
- Decision: The app opens to an empty new chat with a greeting and role-based starter suggestions. Nothing loads until the user asks. New chat clears the conversation only; Reset demo resets demo data.
- Options considered: (a) Automatically send scenario or initial message on load and user change, (b) Empty start experience showing welcome greeting C31 and C01 with role-specific starter suggestion chips. Choosing a scenario pre-types the opening question without auto-sending. "New chat" button in the chat header clears the conversation and returns to the welcome state without altering demo data, while "Reset demo" resets demo data and opens a new chat.
- Reason: Project owner decision. Empowers the user to initiate the conversational interaction rather than being presented with pre-loaded state. Matches modern chat expectations, eliminates accidental or unrequested API invocations on login/scenario switch, and clearly decouples conversation clearing from demo state resetting.
- Evidence or source: Project owner instruction, 2026-10-24; [conversation-design.md](../output/06-ai-interaction/conversation-design.md); [screen-specs.md](../output/07-prototype/screen-specs.md); [screen-inventory.md](../output/07-prototype/screen-inventory.md); [visual-spec.md](../output/07-prototype/visual-spec.md); [ChatHR.tsx](../app/frontend/src/design-system/components/chat/ChatHR.tsx); [ChatEMP.tsx](../app/frontend/src/design-system/components/chat/ChatEMP.tsx); [App.tsx](../app/frontend/src/App.tsx).
- Proposed by: Project owner
- Status: Approved
- Approved by: Project owner

- ID: DEC-041
- Date: 2026-10-26
- Decision: Real AI layer architecture (Option B: Guarded natural replies with CrewAI 4-agent crew, slot-based drafting, server-side critical sentences, and mechanical runtime guards).
- Options considered: (a) Option A: Unconstrained LLM generation, (b) Option B: Guarded natural replies with slot-based drafting, deterministic tools, server-side critical sentences, and mechanical runtime guards with deterministic router fallback, (c) Option C: Pure deterministic templates without AI.
- Reason: Project owner decision. Keeps /api/chat contract 100% stable. Only Classifier and Drafting agents invoke LLM; Retrieval and Escalation use deterministic tools only (no LLM reasoning). Timeout is 20s with a "Thinking…" loading state in the UI. Drafting agent never writes numbers, amounts, percentages, or dates; it writes named slots (e.g. {net_change}, {later_month}) chosen from a facts list supplied by the tools for that reply. Server fills slots from formatted engine values and appends critical approved sentences (C01, C04, C10, C11, C09, C17, C25, and certainty labels). Guards are mechanical only (slots, numbers, names, concepts, banned terms, policy wording, length 1–3 sentences and max 60 words); tone and helpfulness are judged in evaluation, not at runtime. Acceptance targets: intent accuracy >= 90%, zero wrong numbers shown, fallback rate <= 15%, zero cross-employee data sent to AI. English only (Approved by: Project owner). Bonus choice remembered within session, cleared on New chat.
- Evidence or source: Project owner instructions, 2026-10-26; [app/backend/ai/AI_DESIGN.md](../app/backend/ai/AI_DESIGN.md); [app/backend/chat_contract.md](../app/backend/chat_contract.md); [chat_router.py](../app/backend/chat_router.py); [output/06-ai-interaction/](../output/06-ai-interaction/).
- Proposed by: Project owner
- Status: Approved
- Approved by: Project owner

- ID: DEC-042
- Date: 2026-10-27
- Decision: Demo uses two people (Anita Desai HR, Neha Gupta Employee) with a toggle; scenario dropdown removed; HR picks employees by name or picker card.
- Options considered: (a) Multi-user dropdown with scenario selector, (b) Two-person toggle (Anita Desai HR01 / Neha Gupta USER-E05) with scenario dropdown removed and employee picker card for HR tasks.
- Reason: Project owner decision. Simplifies demo presentation to real-world workflow where HR and Employee views are clearly differentiated, frontend never sends scenario numbers, and HR selects employees dynamically via name input or data-driven employee picker cards.
- Evidence or source: Project owner instructions, 2026-10-27; [chat_contract.md](../app/backend/chat_contract.md); [TopDemoBar.tsx](../app/frontend/src/design-system/components/TopDemoBar.tsx).
- Proposed by: Project owner
- Status: Approved
- Approved by: Project owner

- ID: DEC-043
- Date: 2026-10-28
- Decision: HR views show employee name with code (muted); employee views never show codes
- Options considered: (a) Show employee codes on all surfaces, (b) Option B: HR surfaces show employee name and code everywhere an employee is named (picker, proposal, bonus list, settlement, query review, side panel) in format "Priya Sharma · E01" with code in muted text token; employee surfaces never show any employee code, including their own.
- Reason: Project owner decision. HR needs clear identifiers when disambiguating records across enterprise staff, while employee self-service interfaces maintain personal, clean conversational presentation without displaying internal administrative identifiers.
- Evidence or source: Project owner instructions, 2026-10-28; [EmployeePickerCard.tsx](../app/frontend/src/design-system/components/cards/EmployeePickerCard.tsx); [ProposalSummaryCard.tsx](../app/frontend/src/design-system/components/cards/ProposalSummaryCard.tsx); [PanelHR.tsx](../app/frontend/src/design-system/components/chat/PanelHR.tsx); [ChatEMP.tsx](../app/frontend/src/design-system/components/chat/ChatEMP.tsx).
- Proposed by: Project owner
- Status: Approved
- Approved by: Project owner


- ID: DEC-044
- Date: 2026-10-31
- Decision: AI only classifies intent; replies are approved templates (AI sentence drafting disabled for all intents).
- Options considered: (a) Option B: Guarded natural replies with slot-based drafting, (b) Option A: The AI understands; approved templates speak.
- Reason: Project owner decision. In the live test on 30 Oct 2026, two AI-drafted sentences passed every safety check but were unclear: the vague bonus summary and "Your salary decreased by ₹15,420". Safety checks catch wrong numbers and leaks, not unclear wording.
- Evidence or source: Project owner instruction, 2026-10-31; [README.md](../README.md); [config.py](../app/backend/config.py); [conversation-design.md](../output/06-ai-interaction/conversation-design.md); [crew.py](../app/backend/ai/crew.py).
- Proposed by: Project owner
- Status: Approved
- Approved by: Project owner


- ID: DEC-045
- Date: 2026-11-03
- Decision: HR welcome shortened, intro safety line moved to the bottom note, chat-style employee picker replaces the full list.
- Options considered: (a) Keep full 16-record employee picker card and C01 intro message in HR welcome turn, (b) Chat-style flow: HR welcome shortened to greeting and Select an employee button; intro safety line moved to bottom composer note; clicking button adds two turns (user Select an employee and assistant C69 turn with searchable combobox dropdown) which collapses to read-only pill upon selection.
- Reason: Project owner decision (Round 11). Printing the full employee list in the HR welcome message will not scale to hundreds of employees. A chat-style flow with a compact button and searchable combobox dropdown provides scalable employee selection while preserving RBAC and keyboard navigation. The intro safety line moves to the global bottom composer note (Demo with fictional data. HCM One never approves, applies or pays anything on its own.).
- Evidence or source: Project owner instructions, Round 11 (2026-11-03); [welcomeTurn.ts](../app/frontend/src/utils/welcomeTurn.ts); [ChatHR.tsx](../app/frontend/src/design-system/components/chat/ChatHR.tsx); [EmployeeDropdownPicker.tsx](../app/frontend/src/design-system/components/cards/EmployeeDropdownPicker.tsx); [Footer.tsx](../app/frontend/src/design-system/components/Footer.tsx).
- Proposed by: Project owner
- Status: Approved
- Approved by: Project owner
