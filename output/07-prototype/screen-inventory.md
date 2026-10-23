# HCM One: Screen Inventory

## 1. Summary

Proposed for G07. Use six screens: three HR desktop screens and three Employee mobile screens. All six are needed in the MVP. Bonus and settlement use later modes of existing screens. Calculation drawers, mobile detail sheets, confirmation panels and failure states are parts of their parent screen, not extra screens.

**High for scope:** The MVP includes hike, salary explanation, TDS explanation and the complete query path. Bonus and settlement remain later scope. The Employee settlement statement is an output of Flow 3 while access remains; it does not add a new employee flow or post-exit channel. **Proposed design choice; user suitability remains unvalidated:** The screen reuse is a design recommendation, not a measured usability result. Existing AS-14, AS-16 and AS-17 apply.

Sources: [current BRD v1.2](../../input/requirements/Payroll_brd_v1.2.md), Sections 3, 5 and 6; [approved flows](../05-architecture/user-flows.md), Section 3; [approved states](../05-architecture/edge-cases-states.md), Sections 2–5; [approved MVP scope](../04-strategy/mvp-scope.md), Sections 2–3; [decision log](../../project-memory/design-decisions.md), DEC-007, DEC-011–DEC-019 and DEC-023–DEC-025. Historical proposal wording in approved artifacts does not undo subsequent approvals or BRD v1.2.

## 2. Screen table

All screens have the existing loading, missing-data, rule-not-verified, calculation-error and permission-denied conditions where their operation requires them. These are display states within approved flows, not new workflow transitions. Certainty is separate from preparation, approval and query status.

| ID | Screen name | Role | Platform | Flow steps (F IDs) | Reason to exist | States | MVP or later |
|---|---|---|---|---|---|---|---|
| SCR-01 | Prepare a proposal | HR Admin | Desktop | F1-01–F1-05; F2-01–F2-03; F3-01–F3-03 | Capture and confirm the authorized request before calculation. Reuse the structure with fields for each proposal type. | Default Draft; clarification; confirmation; loading; Needs input; rule not verified; error; permission denied | MVP: hike. Later: bonus and settlement modes. |
| SCR-02 | Review a proposal | HR Admin | Desktop | F1-06–F1-12; F2-04–F2-10; F3-04–F3-12 | Review amounts and proof, retain blockers, and make an explicit version-bound decision. | Calculated; Ready for review only with a valid stored version; Needs input; loading; rule not verified; error; edit with reason and Revised; Rejected; Approved and ready for payroll only after storage; component Not applicable or unresolved; permitted Held only with a valid recorded basis | MVP: hike and its calculation drawer. Later: bonus, settlement and scoped review modes. |
| SCR-03 | Review a payroll query | HR Admin | Desktop | F6-01; F6-09–F6-11 | Let authorized HR review an employee-confirmed issue and evidence, reply and record explicit resolution. | Default recorded query; loading; missing evidence; rule not verified for a dependent payroll check; error; permission denied; Sent; In review; Resolved; Closed where the approved closure guard permits it | MVP |
| SCR-04 | Understand my payroll | Employee | Mobile | F4-01–F4-10; F5-01–F5-10; F3-12 statement output under DEC-015 and DEC-019 | Explain an own salary or TDS change, then offer breakdown, proof and a query draft. Reuse its component layout for the later employee-facing statement. | Default question and period choice; loading; salary result; TDS result; no earning change; missing data; rule not verified; calculation error; permission denied; disputed explanation; later statement complete or incomplete, only from an approved snapshot while access remains | MVP: salary and TDS. Later: settlement statement mode. |
| SCR-05 | Review my query draft | Employee | Mobile | F6-01–F6-09; entry from F4-09–F4-10 or F5-09–F5-10 | Review the employee's words and relevant evidence, choose add or new, and explicitly confirm sending. | Default unsent Draft; editable description; removed evidence; candidate choice; confirmation; loading; missing evidence; rule not verified for a dependent explanation; delivery error with Draft retained; permission denied | MVP |
| SCR-06 | Track my payroll query | Employee | Mobile | F6-12; recorded transitions in states Section 4 | Show only the employee's actual query state and recorded HR reply; allow the approved explicit dispute or closure action. | Default In review fixture; loading; missing ID or reply; rule-not-verified limitation on attached explanation; retrieval error; permission denied; Sent; In review; Resolved; Closed | MVP |

All row mappings refer to the exact step IDs in [user-flows.md](../05-architecture/user-flows.md). SCR-03 is required by FR-6.12–FR-6.13; SCR-05 and SCR-06 separate unsent review from persisted query lookup to keep sending consent visible. Drawers and sheets keep the parent screen's authorization and scope. This proposed screen structure does not change the approved step sequence.

## 3. Scenario-to-screen map

All thirteen BRD v1.2 scenarios have a screen and state. The table uses existing generated results. It does not mark an engine proposal Approved, Ready for review or paid. The fixture can preview calculated values; actual approval still requires the approved version and scope guards.

| Scenario | Screen | State | Data file |
|---|---|---|---|
| 1. Hike with LOP | SCR-02, hike mode | Complete calculation, unapproved proposal; monthly proof and October TDS estimate flag | [scenario-01.json](../../data/generated/scenarios/scenario-01.json), `/result` |
| 2. Hike across the PF ceiling change | SCR-02, hike mode | Complete calculation; dated PF segments in the calculation drawer | [scenario-02.json](../../data/generated/scenarios/scenario-02.json), `/result` |
| 3. Hike with missing attendance | SCR-02, hike mode | Incomplete; July missing; dependent totals unavailable; no approval of incomplete scope | [scenario-03.json](../../data/generated/scenarios/scenario-03.json), `/result` |
| 4. Team bonus with joiner and notice cases | SCR-02, later bonus mode | Known gross awards, ineligible and needs-input lists; incomplete overall group | [scenario-04.json](../../data/generated/scenarios/scenario-04.json), `/result/bonus_requests` |
| 5. Missing performance | SCR-02, later bonus mode | Needs input for the affected employee; Incomplete amount, not zero | [scenario-05.json](../../data/generated/scenarios/scenario-05.json), `/result/employee` |
| 6. Eligible gratuity | SCR-02, later settlement mode; conditional SCR-04 statement mode | Complete calculation; unapproved components. Statement preview is gated until a real approved snapshot exists. | [scenario-06.json](../../data/generated/scenarios/scenario-06.json), `/result` |
| 7. Below gratuity minimum | SCR-02, later settlement mode | Gratuity Not applicable with the generated informational flag; retain reason and proof | [scenario-07.json](../../data/generated/scenarios/scenario-07.json), `/result/components/gratuity` |
| 8. Asset clearance and notice shortfall | SCR-02, later settlement mode | Incomplete; notice recovery known; asset recovery unresolved; no final net | [scenario-08.json](../../data/generated/scenarios/scenario-08.json), `/result` |
| 9. Salary drop with LOP | SCR-04, salary mode | Complete for this scope; net change first, earnings and PF changes below | [scenario-09.json](../../data/generated/scenarios/scenario-09.json), `/result` |
| 10. Previous-employer income declared mid-year | SCR-04, TDS mode | Complete TDS calculation; accepted prior-employer income reason. Do not reuse the old missing-declaration script. | [scenario-10.json](../../data/generated/scenarios/scenario-10.json), `/result` |
| 11. No salary earning change | SCR-04, salary mode | No earning component change; separate PF and net changes remain visible | [scenario-11.json](../../data/generated/scenarios/scenario-11.json), `/result` |
| 12. Another employee's data requested | SCR-04, permission-denied state | Permission denied; no target name, ID, amount, source or record-existence confirmation in the rendered refusal | [scenario-12.json](../../data/generated/scenarios/scenario-12.json), `/result/status` |
| 13. Known and unresolved settlement components | SCR-02, later settlement mode; conditional SCR-04 statement mode | Known salary and advance beside unresolved asset recovery; Incomplete, no final net. No approved statement is fabricated. | [scenario-13.json](../../data/generated/scenarios/scenario-13.json), `/result` |

The query screens use the existing query carried in [scenario-09.json](../../data/generated/scenarios/scenario-09.json), `/result/existing_query`. Its recorded status is In review. No new sent query, approval event or HR reply is invented.

## 4. Screens considered and removed, with reasons

| Considered screen | Treatment | Reason and source |
|---|---|---|
| HR dashboard with totals and charts | Removed | No dashboard is required by the BRD. It would need unsupported aggregate numbers. FR-1.1, FR-2.1 and FR-3.1 start requests directly. |
| Separate request screen for every HR flow | Reuse SCR-01 later modes | Scope capture and confirmation can share a frame while keeping each flow's required fields. F1-02–F1-05, F2-02–F2-03, F3-02–F3-03. |
| Separate bonus and settlement review shells | Reuse SCR-02 later modes | Employee and component tables differ, but proposal scope, proof and guarded review remain common. F1-09–F1-12, F2-07–F2-10, F3-09–F3-12. |
| Standalone calculation screen | Drawer on SCR-02; sheet on SCR-04 | Proof must be available from every amount without adding a separate workflow. FR-1.10, FR-2.12, FR-3.15, FR-4.9–FR-4.13, FR-5.7–FR-5.10. |
| Separate salary and TDS chat shells | Reuse SCR-04 modes | Both are authorized own-record explanations with the approved layers and existing Flow 6 entry. F4-01–F4-10; F5-01–F5-10. |
| New employee settlement flow or post-exit portal | Removed | Statement content belongs to Flow 3's output; access and delivery limits are DEC-015 and DEC-019. |
| Separate approve, edit, reject and query confirmation pages | Inline panels within parent screen | Preserve explicit human actions and guards without creating new lifecycle states. DEC-011–DEC-014, DEC-017. |
| Payment, bank comparison, payroll execution or compliance screen | Removed | Outside BRD v1.2 Section 5.3. Approval never becomes payment. |

## Remaining fixture limits and implementation handoff

- **Approved direction:** Code prototype first; Figma is optional later for visual polish and case study images. figma-ai-prompts.md remains a bonus. The screen count, MVP scope and approved flow mappings are unchanged.
- **High for generated facts:** display_inputs, request-level bonus aggregates, recovery totals, ranked reasons and rule metadata now fill the resolved gaps. Exact bindings are in screen-specs Section 8.
- **PQ-08 and PQ-09, Resolved by design:** Created by the code prototype at runtime as demo lifecycle records (version, actor, time, query ID, HR reply) when the user acts. Never pre-filled. Show success only after the action is recorded; retain all approval, authorization and sending guards.
- **Remaining:** Missing July attendance, missing or incomplete bonus inputs and tax, custom selected-scope aggregates, the unexported declaration month range and E12's unresolved asset/net. See screen-specs Section 9. Do not calculate a missing display value.
- **Resolved wording:** DEC-029 approves the previous-employer declaration cause for A06-10. The approved month slot still needs its generated source value.
- **Assumption, Low:** Existing AS-14, AS-16 and AS-17 remain unvalidated. No comprehension improvement has been measured.
