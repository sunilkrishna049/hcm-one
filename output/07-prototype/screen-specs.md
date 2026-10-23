# HCM One: Screen Specifications

Revised for G07. The code prototype is the next implementation; Figma is optional later for visual polish and case study images. These documents specify screens and runtime behavior; they have not created an application, payroll approval, sent query or Figma file. Requirements have High confidence. Layout choices remain Proposed where not expressly approved. Existing AS-14, AS-16 and AS-17 remain unvalidated.

Sources: [inventory](screen-inventory.md); [current BRD v1.2](../../input/requirements/Payroll_brd_v1.2.md), Sections 3, 5–9; approved [flows](../05-architecture/user-flows.md), Section 3; [states](../05-architecture/edge-cases-states.md), Sections 2–5; [Agent 06](../06-ai-interaction/); [UX principles](../04-strategy/ux-principles.md); [personas](../03-analysis/personas.md); [decisions](../../project-memory/design-decisions.md), DEC-011–DEC-029 and the new approved prototype and typography decisions.

## Data and content contract

Every visible payroll amount, date, period, day count, percentage and numeric record ID binds to the exact generated file, record and JSON pointer in Section 8. Copy the literal value with its sign and an adjacent INR label; never compact, round, total, count, subtract or back-solve it. Named binding keys are designer references, not labels to display in the product. Missing or null required numbers render exactly **Not available in generated data**. A null applicable due date renders **Not applicable** only when the complete generated date object says no separate due date applies. Known zero remains zero.

Design tokens and the prescribed frame sizes are authoring parameters, not visible payroll facts. Screen IDs, requirement IDs and array indexes are references, not UI counters. No unsupported count badge, progress percentage, approval-version number or response-time estimate is shown.

Names come from [employees.json](../../data/mock/employees.json), matching the generated employee ID. The existing non-numeric query category and description come from [queries.json](../../data/mock/queries.json), QUERY-E05-SEPTEMBER. Do not copy a raw mock amount, day count or date to fill a screen. Every displayed period and numeric ID still uses its generated binding.

The copy catalog in Section 7 preserves Agent 06's exact sentences. Braces are its existing slots; replace only a named slot with an authorized recorded fact. Headings and field labels below are UI labels, not new causal AI sentences. Read the selected amount object's exact formula, inputs, rule_ids, certainty and flags in the proof view. Do not invent an arithmetic substitution line.

Generated proposals are unapproved. Complete calculation certainty is not approval or payment. **PQ-08 and PQ-09: Resolved by design.** Created by the code prototype at runtime as demo lifecycle records (version, actor, time, query ID, HR reply) when the user acts. Never pre-filled. Current calculation fixtures may initialize a demo version on explicit request confirmation. That runtime record must identify the user, time, exact source calculation and selected scope before review can become actionable. A success state appears only after the actual action is recorded. A generated fixture is never relabeled Approved or Sent by itself. G07 is a project gate, not payroll approval.

## 1. SCR-01 — Prepare a proposal

**Role and frame:** HR desktop, 1440 px. **Flow:** F1-01–F1-05; later F2-01–F2-03 and F3-01–F3-03. **Purpose:** Capture and confirm the authorized request. **Principles:** UXP-01, UXP-02, UXP-04, UXP-07. Persona basis: The Payroll Admin's input reconciliation.

**Layout, top to bottom:** HCM One header and role; title; proposal type; plain-language composer; authorized employee; one clarifying question; confirmation panel; existing-calculation link. Use a narrow reading column within the desktop grid. No dashboard or unrelated records.

**Exact content:** “Prepare a proposal.” MVP type “Back-dated hike.” Later types “Bonus and incentives” and “Full and final settlement.” Composer label “Your payroll request”; example “Prepare Priya Sharma's pending back-dated hike.” Employee Priya Sharma, E01 from scenario-01 /result/employee_id and matching mock name. Intro C01. C02 appears only in the missing-effective-date variant; the populated default proceeds to explicit request confirmation.

Confirmation labels: “Employee,” “Requested hike,” “Effective date,” “Old salary,” “Proposed salary.” Priya’s percentage is **10** (D01-requested_hike_percentage) percent; effective date **2026-04-01** (D01-effective_date); contractual old total **120000** (D01-old_monthly_salary-total) INR; proposed total **132000** (D01-proposed_monthly_salary-total) INR. Expand the D01 old and proposed component bindings. Arjun and Kavya use matching D02 and D03 records. The separate existing-period HM amounts remain earned values, not contractual request inputs. Later bonus periods use B0-period or B1-period. Later exit inputs use the D06, D07 and D13 resignation, last-working-day, required/served notice and waiver bindings. They are now populated directly from display_inputs.

**Actions:** “Confirm request” is available when required sourced fields are usable and the user confirms the exact request. Confirmation creates the demo lifecycle version record; it does not approve or apply payroll. “Edit request” returns to capture and invalidates prior confirmation. “Review existing calculation” opens SCR-02 for that recorded request and matching generated result. Changes to calculation inputs require a new engine result; never reuse a stale result as a fresh calculation.

**States:** Draft default; clarification; confirmation only with real input; loading C06; missing data C07 and Needs input; rule limitation C08; error C09; permission denied C10, with all private context removed. No calculation certainty is guessed before a result exists.

## 2. SCR-02 — Review a proposal

**Role and frame:** HR desktop, 1440 px. **Flow:** F1-06–F1-12; later F2-04–F2-10 and F3-04–F3-12. **Purpose:** Review proof and decide on a valid version and scope. **Principles:** UXP-01, UXP-02, UXP-04, UXP-05, UXP-07.

**Layout, top to bottom:** Authorized scope and unapproved status; title; blocker before unsupported totals; approved AI scope sentence; hero number; gross and deduction cards; persistent flags; period, employee or component table; calculation drawer; edit panel; approval bar. Numbers dominate; no decorative charts.

### Hike default

“Back-dated hike proposal.” Priya Sharma, E01. Status is scenario-01 /result/proposal_status, “Needs HR approval; not applied.” Certainty is its /result/certainty, “Complete for this scope.” C03 is the assistant message. Periods use the HM bindings.

Hero “Expected net arrears,” H-net_arrears. Cards “Gross arrears,” H-gross_arrears; “Employee PF change,” H-pf; “Estimated TDS impact,” H-tds_impact. Show H-flag in full, beside H-month. Tax detail uses H-recurring_salary_tds_impact and H-arrears_only_tds_impact. Do not add another tax deduction or combine these numbers yourself.

Table columns: “Period,” “Old earned amount,” “Revised earned amount,” “Arrears,” “Employee PF change,” “Incremental estimated arrears TDS,” “Show calculation.” Copy the HM rows. The monthly TDS column is the incremental arrears-only effect. It is not the overall receipt-month estimate repeated per month. Employer EPF and EPS are separate detail fields bound directly to each month's generated pf_change objects; they are not employee deductions.

### Hike alternate states

Arjun Rao, scenario-02: use the H2 gross, TDS and net bindings. The September proof uses H2-old, H2-new, H2-diff, H2-date and H2 segment day counts. Copy historical ceiling values and effective dates from the selected segment's rule_ids; do not use one undated ceiling for the whole month.

Kavya Iyer, scenario-03: lead with Incomplete and Needs input. C07 binds record type to “attendance record” and period to H3-july. H3 gross, TDS and net render **Not available in generated data**. Show only separately scoped H3-aug-diff and H3-sep-diff. Missing July is not zero and blocks full approval.

### Later bonus mode

“Bonus and incentives proposal.” Use the generated type and B0-period or B1-period. Show Eligible, Not eligible and Needs input lists with the matching request’s engine counts. Annual counts and totals use X-001–X-006; Sales uses X-007–X-012. The Annual gross is **213929** (X-004) INR for known eligible employees. Its TDS and net are null and Incomplete. Sales gross is **120000** (X-010) INR, TDS **0** (X-011) INR and net **120000** (X-012) INR. These are request aggregates, not arbitrary selected-scope totals. Never count or sum the lists in the specification.

E08 reason: “On notice at the time of calculation.” E09 reason: “Performance record missing.” E03’s gross is known but its TDS and net remain Incomplete, so the Annual group TDS and net still render **Not available in generated data**. E09’s rating and rate remain null. Selected-scope counts and totals are also **Not available in generated data** until a matching engine scope is returned; do not relabel request aggregates as a custom selection.

E07 proof uses B annual Basic, eligible days, period days and award bindings, plus D04 rating and applied rating rate. E04’s rating is **4** (D04-bonus_requests-0-employees-E04-rating) and applied rate **10** (D04-bonus_requests-0-employees-E04-applied_rating_rate_percent) percent. E08 has a known policy rate but no applied rate: use its recorded Not applied status, not zero or an invented award. Sales raw target and achievement use D04 bonus_requests-1 employee bindings beside the existing percentage, slab, award, TDS and net. All operands are copied; none are solved backwards.

“Approve selected scope” requires a valid stored review scope, dependent values and selected totals. It is disabled when any is missing. E03's unknown net and E09's absent performance cannot be approved. The approved partial-approval template in Agent 06 Section 4 is used only with actual selected records, not invented counts.

### Later settlement mode

“Full and final settlement proposal.” Rahul Verma, E10, is the complete default. Lakshmi Reddy, E11, and Imran Khan, E12, are alternates. Amounts and applicable due dates use S bindings; request fields use D06, D07 and D13. Proof includes encashable_leave_days_used, last_drawn_basic, last_drawn_da and last_drawn_basic_plus_da from the corresponding display_inputs bindings.

Table columns: “Component,” “Classification,” “Amount,” “Applicable due date,” “Preparation,” “Approval,” “Reason,” “Show calculation.” Copy classification, preparation status, flag and unresolved reason from the selected generated component. Its certainty sits beside the amount. “Calculated; needs HR approval” is not Approved. Approval metadata is created and displayed only after recording the user's demo lifecycle action; never pre-fill an approval state.

E10 uses S6 gross payables, total deductions, final net, employee PF and TDS. Show its separate engine recoveries_total and known_recoveries_subtotal bindings; PF and TDS are excluded from both. Each component retains its applicable due date and C20. Non-applicable deduction dates stay Not applicable. Do not relabel total deductions as recoveries-only totals.

E11 gratuity is Not applicable, with its generated zero and “Close to minimum service.” Actual years, months and days use S7 service bindings. The flag is informational, not an eligibility override.

E12 uses scenario-13’s shared settlement result for scenarios 8 and 13. Known salary, leave, notice, advance, PF, TDS and gross payables remain visible. The asset is Unresolved with “Asset clearance pending; final net incomplete.” Asset recovery, recoveries total (X-041) and final net remain **Not available in generated data**. Show known recoveries subtotal **56667** (X-042) INR with the exact flag “Excludes unresolved asset recovery” (X-043). This is a subtotal, not the final recovery or net. Salary held remains false; pending clearance never becomes a whole-settlement hold.

### Review controls and proof drawer

C04 accompanies “Approve selected scope,” “Edit with a reason,” and “Reject.” PQ-08 is resolved by design: Created by the code prototype at runtime as demo lifecycle records (version, actor, time, query ID, HR reply) when the user acts. Never pre-filled. Enable approval only after a current version-bound review record exists, the selected calculation scope is valid and dependent values are complete. Store the authorized decision before displaying success. Never prefill a version, approver or timestamp; silence has no transition.

Edit panel labels “Line to edit,” “Proposed amount,” “Reason”; use C05. The static preview supplies no invented edited value. Recalculated and Revised layouts need actual recorded version results. A stale submission uses C25. Conditional success states are populated only after storage, not by a prototype click.

Every number opens “Show calculation.” Copy its exact value, formula, input references, rule IDs, rules_version, verified_on, certainty and flags. Display actual effective dates where present. For an undated rule, show the exact date_note “Applies to all demo periods” rather than a fabricated date. verified_on is verification metadata, not an effective or payment date. Use the selected authorized result’s own rule references; the Section 8 metadata bindings document their exported contract. display_inputs proof reads its copied source and nested calculation where present. Source access remains available from the first card.

**States:** Calculated unapproved default; guarded Ready for review; loading C06; Needs input C07; Rule not verified C08; calculation error C09; denied C10; edit/Revised C05; stale C25; conditional Rejected or Approved and ready for payroll. Later components include Not applicable and unresolved. A Held state needs a recorded verified hold basis; E12 is not an invented known held amount.

## 3. SCR-03 — Review a payroll query

**Role and frame:** HR desktop, 1440 px. **Flow:** F6-09–F6-11, guarded by F6-01. **Purpose:** Review the employee-confirmed issue and record HR reply and resolution. **Principles:** UXP-01, UXP-02, UXP-04, UXP-06, UXP-07.

**Layout:** “Payroll queries”; Q-id; Q-status; own authorized employee and C9-after_month; original description; relevant evidence; “What the payroll calculation shows”; actual reply; reply editor; explicit resolution controls. No query-count badge or response timer.

**Exact content:** Neha Gupta, generated E05. Category “salary.” Description “Please check my September attendance.” These are seed text, not proof of an error. Existing Q-status is In review and numeric previews use C9 and D09. “Your reply” starts as an empty editor. PQ-09 is resolved by design: Created by the code prototype at runtime as demo lifecycle records (version, actor, time, query ID, HR reply) when the user acts. Never pre-filled. The prototype records actual demo replies and lifecycle events after authorized actions. The calculation alone does not prove attendance correctness.

**Actions:** “Save reply” persists the actual user-entered demo reply and keeps In review unless HR explicitly records resolution. “Record resolution” requires that reply and a recorded authorized action. “Close query” keeps the approved prior-resolution guard. Show success only after recording the action; failure preserves the last real state. Query resolution does not approve a payroll change.

**States:** Default recorded In review; conditional Sent with “Take into review”; loading C06; missing evidence C07; failed payroll check C09; dependent rule limitation C08 without changing query status; storage/retrieval failure preserves the last actual status and claims no success; denied C10 clears private context; conditional Resolved and Closed require real reply and event records. Do not infer resolution from any reply or from silence.

## 4. SCR-04 — Understand my payroll

**Role and frame:** Employee mobile, 390 px. **Flow:** F4-01–F4-10; F5-01–F5-10; later F3-12 statement output. **Purpose:** Explain an own recorded change before optional detail. **Principles:** UXP-01–UXP-07, particularly UXP-03 and UXP-07. Persona basis: The Pay-Change Employee's explanation and record-checking needs.

**Layout:** HCM One; “Understand my payroll”; own context; “Salary” or “TDS”; period choice; blocker if needed; change hero; recorded reason labels; brief approved AI text; breakdown, calculation and source actions; follow-up; “Draft a query for HR.” The detail sheet stays within this screen. No employee picker or unrelated records.

### Salary default: Neha Gupta

Use C9 periods and E05 scope. Hero is C9-net_change, with generated Complete for this scope. Label the reason list **“Ranked by effect on take-home pay.”** Render /result/reasons in its stored array order, without sorting or recalculating: LOP **-5000** (X-021) INR (X-020); PF ceiling change **-420** (X-024) INR (X-023). Keep each reason’s signed effect, sources and flags. The PF effect retains earned wage after LOP and dated ceiling segments. C27 offers breakdown.

“Unpaid leave days” uses **3** (D09-months-2026-09-lop_days) and “Calendar days” uses **30** (D09-months-2026-09-calendar_days). Earlier and later values use the matching D09 records; Paid days stays bound to C9. The breakdown retains Basic, DA, HRA, Special allowance, earned gross, employee deductions and net. Employer contributions remain separate from take-home deductions.

“Show calculation” gives the selected exact formula, generated value, source IDs, dated rules and flags. The glossary copies Agent 06 Section 6. Missing operands remain missing; no formula is evaluated here.

### Salary alternate: Pooja Das

Use E16 and C11 periods. Keep “No salary earning component change,” its net and PF changes, and the existing breakdown. Add D11 LOP and calendar days to proof. Reasons are **ranked by effect on take-home pay**, copied in engine order: PF ceiling change **-420** (X-038) INR (X-037). Zero earning change does not imply unchanged deductions or net.

### TDS mode: Siddharth Jain

Use E06 and C10 periods. Hero “TDS change,” C10-tds_change; earlier and later monthly TDS use C10 before/after TDS. Reason data heading “Previous-employer income declaration,” supported by the scenario's used declaration reference and MR-01 and current BRD scenario 10. Do not use the old missing-declaration cause.

C29 is the DEC-029 approved main reason; C22 remains its detail message. “Show tax calculation” includes the existing T bindings plus declared previous-employer gross **450000** (D10-previous_employer_declared_gross) INR, previous-employer TDS **15000** (D10-previous_employer_tds) INR, Northwind TDS already deducted **0** (D10-northwind_tds_already_deducted) INR and remaining yearly tax **87180** (D10-remaining_yearly_tax) INR. Keep aggregate tax already deducted separate from these components; never subtract to obtain a display amount.

The regime is the exact generated regime_scope value. Show exported rules_version and verified_on, real effective dates, and date_note for undated rules. C11 still handles personal advice. TDS-mode reasons are **ranked by effect on take-home pay**, copied in engine order: TDS change **-12454** (X-028) INR (X-027); PF ceiling change **-560** (X-031) INR (X-030). The declared month range is not exported in scenario-10 display_inputs; the C29 preview shows **Not available in generated data** in that slot. Do not use comparison months or consult raw mock dates to fill it. Calculation certainty remains scoped to the known TDS result; the missing wording operand stays visible.

### Permission denied

Scenario-12 shows “Payroll access,” generated “Permission denied,” and C10. Remove target name, ID, periods, amounts, source links and cached private data. Do not render the attempted E01 target. Offer “Ask about my payroll.” Do not confirm that another record exists.

### Later statement output within Flow 3

“Settlement statement” reuses the component sheet. DEC-019 limits access to when the Employee still has access; the company's existing exit process handles later delivery. No new channel or post-exit portal.

A real statement needs the runtime approved snapshot, version, scope, actor and time. PQ-08 is resolved by design: Created by the code prototype at runtime as demo lifecycle records (version, actor, time, query ID, HR reply) when the user acts. Never pre-filled. Before an actual recorded approval, show only the generated unapproved calculation preview. C18 belongs only to the actual post-approval layout. Statement access and follow-up retain DEC-019’s boundary.

The conditional statement order is approved scope and C18; complete net/direction or C19 with actual unresolved component; known payables and recoveries/PF/TDS; preparation and approval status; reasons; individual due dates with C20; proof; optional Flow 6 follow-up while access remains. E12's unknown asset and final net remain unavailable. Do not fabricate approval or collect a recovery.

**Actions:** “Show breakdown,” “Show calculation,” “Show tax calculation,” “View source,” glossary, topic/period selection, follow-up, and “Draft a query for HR.” A changed comparison scope needs Employee confirmation. Unsupported periods stop comparison. Query entry never sends. C26 handles future-pay questions; C21 and C11 preserve limits.

**States:** Default question; valid salary/TDS; no earning change; loading C06; missing source C07; rule limitation C08; error C09; denied C10; dispute/unexplained C28, with “Cannot explain from available payroll data” only for its actual condition; later conditional complete or incomplete statement. No confidence score.

## 5. SCR-05 — Review my query draft

**Role and frame:** Employee mobile, 390 px. **Flow:** F6-01–F6-09. **Purpose:** Review the draft and control sending. **Principles:** UXP-01, UXP-02, UXP-04, UXP-06, UXP-07.

**Layout:** “Review my query draft”; unsent Draft; category; period; employee's words; removable evidence; what was checked and remains disputed; own candidate; add-or-new choice; confirmation; action. Draft is not a newly persisted query.

**Exact fixture:** Neha Gupta, E05; C9-after_month; category salary; description “Please check my September attendance.” This seed wording is editable demonstration text, not a new submission. Relevant evidence is the seed attendance reference and selected own payroll comparison. Numeric evidence previews use C9-after-gross, C9-after-paid and C9-after-pf-employee. Never expose raw mock financial/day values.

Candidate Q-id and Q-status remain sourced to the existing own seed query. Use C14, “Add to my open query” and “Create a new query.” Use C12 or C13 only for the selected action. PQ-09 is resolved by design: Created by the code prototype at runtime as demo lifecycle records (version, actor, time, query ID, HR reply) when the user acts. Never pre-filled. A new ID comes from the recorded send, never from the candidate. An append retains the recorded existing query ID and status.

**Actions:** Edit description, remove evidence, choose add or new, and explicitly confirm actual content and destination. Changes clear confirmation. Cancel or silence leaves Draft. The code prototype persists its demo action before claiming Sent or an append, with generated runtime identity and event metadata. A failed write keeps the draft and C17. Existing-query lookup still opens SCR-06.

**States:** Draft; edit; removed evidence; candidate; confirmation; loading C06; missing evidence C07 without secret replacement; dependent rule limitation C08; delivery failure C17 with Draft retained; denied C10 clears unsafe attachments. Actual successful Sent needs persistence and stable ID; append retains the actual existing ID and status. Evidence sufficiency belongs to GAP-08.

## 6. SCR-06 — Track my payroll query

**Role and frame:** Employee mobile, 390 px. **Flow:** F6-12 and approved query state transitions. **Purpose:** Read the own query status and reply. **Principles:** UXP-02, UXP-04, UXP-06, UXP-07.

**Layout:** “My payroll query”; Q-id; Q-status with icon and text; own employee and C9-after_month; original description; evidence link; “HR reply”; supported actions; return to payroll. No response countdown.

**Exact default:** Q-id and Q-status initialize QUERY-E05-SEPTEMBER and In review from generated data; Neha Gupta, generated period and the original seed description stay unchanged. Use C16. PQ-09 is resolved by design: Created by the code prototype at runtime as demo lifecycle records (version, actor, time, query ID, HR reply) when the user acts. Never pre-filled. No fake HR reply, creation date or timeline is prefilled. Show only recorded runtime events; no timer or progress percentage.

**Actions:** “View evidence,” “Back to payroll,” and own-status lookup. Conditional Resolved permits explicit dispute back to In review and explicit closure acknowledgment; they are unavailable in the current In review fixture. Closed retains history and may lead to a new unsent draft.

**States:** In review default; loading C06; missing own ID C07 with no guessed ID; retrieval failure retains actual status and claims no success; permission denied C10; rule limitation C08 only on a dependent payroll explanation, not a query lifecycle change; conditional Sent C15, Resolved C23 and Closed C24 need actual stored state and reply. Payroll calculation error C09 applies only when that is the actual failed check. A generic new query-storage error sentence is not invented.

## 7. Exact approved AI copy

Use these sentences verbatim. Only named existing braces can be filled from the recorded scope. Source references are authoring details; they are not extra conversation text. Glossary terms are copied from conversation-design Section 6.

### C01

> I am HCM One's AI payroll assistant. I explain payroll records and payroll calculation results. I can help prepare a proposal or a query for you to review. I cannot approve a change, apply it or pay it. I send a query only after you confirm.

Source: [trust-explainability.md](../06-ai-interaction/trust-explainability.md), Section 6.

### C02

> From which date should this proposed hike take effect?

Source: [conversation-design.md](../06-ai-interaction/conversation-design.md), Section 4.

### C03

> This is a proposal for the recorded affected months.

Source: [conversation-design.md](../06-ai-interaction/conversation-design.md), Section 8, Example A.

### C04

> Approving records this version and the selected scope as ready for payroll. It does not apply the change or make a payment.

Source: [approval-failure-handling.md](../06-ai-interaction/approval-failure-handling.md), Section 2.

### C05

> Your edit will create a revised proposal. HCM One will recheck the affected amounts and totals. You will need to review the new version before approving it.

Source: [approval-failure-handling.md](../06-ai-interaction/approval-failure-handling.md), Section 3.

### C06

> I am waiting for the payroll records needed for this request. The result is not ready.

Source: [approval-failure-handling.md](../06-ai-interaction/approval-failure-handling.md), Section 6, Loading.

### C07

> The required {record type} for {period or component} is missing. I cannot explain a complete result for this scope.

Source: [approval-failure-handling.md](../06-ai-interaction/approval-failure-handling.md), Section 6, Missing data.

### C08

> The applicable rule basis for {affected scope} is not verified. That part cannot be calculated.

Source: [approval-failure-handling.md](../06-ai-interaction/approval-failure-handling.md), Section 6, Rule not verified.

### C09

> The payroll calculation did not produce a usable result for {affected scope}. I cannot give a complete amount for it.

Source: [approval-failure-handling.md](../06-ai-interaction/approval-failure-handling.md), Section 6, Calculation error.

### C10

> I cannot provide that information. I can help with payroll records you are authorized to access.

Source: [approval-failure-handling.md](../06-ai-interaction/approval-failure-handling.md), Section 6, Permission denied.

### C11

> I can explain the tax recorded in your payroll. I cannot recommend a tax regime or investment. Please consult a tax professional for personal advice.

Source: [conversation-design.md](../06-ai-interaction/conversation-design.md), Section 5, Personal tax advice.

### C12

> Send this query with the listed evidence to HR?

Source: [approval-failure-handling.md](../06-ai-interaction/approval-failure-handling.md), Section 5.

### C13

> Add this description and the listed evidence to your selected open query?

Source: [approval-failure-handling.md](../06-ai-interaction/approval-failure-handling.md), Section 5.

### C14

> Is this the same issue as your open query, or a different issue?

Source: [conversation-design.md](../06-ai-interaction/conversation-design.md), Section 4.

### C15

> Your query is Sent. HR can access it for review.

Source: [conversation-design.md](../06-ai-interaction/conversation-design.md), Section 7, A06-12.

### C16

> Your query is In review. HR has taken it for review.

Source: [conversation-design.md](../06-ai-interaction/conversation-design.md), Section 7, A06-12.

### C17

> Your query has not been sent. It remains a draft.

Source: [approval-failure-handling.md](../06-ai-interaction/approval-failure-handling.md), Section 6, Query delivery failure.

### C18

> This statement explains the scope approved by HR. Approval does not mean payment.

Source: [trust-explainability.md](../06-ai-interaction/trust-explainability.md), Section 8.

### C19

> The final net is incomplete because {recorded unresolved component} is not yet known.

Source: [trust-explainability.md](../06-ai-interaction/trust-explainability.md), Section 8.

### C20

> This is the applicable recorded due date. This assistant has not made a payment.

Source: [trust-explainability.md](../06-ai-interaction/trust-explainability.md), Section 8.

### C21

> I can use only your own payroll records. I cannot check your bank credit or give personal tax, legal or financial advice.

Source: [trust-explainability.md](../06-ai-interaction/trust-explainability.md), Section 6.

### C22

> The payroll calculation detail includes projected yearly income, applied deductions and exemptions, yearly tax, tax already deducted and remaining months. It identifies your recorded tax regime and applicable rule version.

Source: [conversation-design.md](../06-ai-interaction/conversation-design.md), Section 8, Example C.

### C23

> HR recorded a resolution. Here is the recorded reply. You can dispute the resolution if it does not answer your issue.

Source: [conversation-design.md](../06-ai-interaction/conversation-design.md), Section 7, A06-12.

### C24

> Your query is Closed. Its history is retained. A new issue can be drafted separately.

Source: [conversation-design.md](../06-ai-interaction/conversation-design.md), Section 7, A06-12.

### C25

> This proposal changed after you reviewed it. Review the current version before approving.

Source: [approval-failure-handling.md](../06-ai-interaction/approval-failure-handling.md), Section 6, Changed version.

### C26

> This explains the recorded months. I cannot promise next month's pay. It depends on that month's recorded inputs and applicable rules.

Source: [conversation-design.md](../06-ai-interaction/conversation-design.md), Section 8, Example B.

### C27

> Would you like the earnings and deductions breakdown?

Source: [conversation-design.md](../06-ai-interaction/conversation-design.md), Section 8, Example B.

### C28

> The available payroll records do not explain this difference. I can help draft a query for HR.

Source: [approval-failure-handling.md](../06-ai-interaction/approval-failure-handling.md), Section 6, Unexplained mismatch.

### C29

> Your TDS is higher because you declared income from your previous employer for {declared months}. That income is added to your yearly income, so your expected yearly tax is higher. The tax your previous employer already deducted is counted, so it is not deducted twice.

Source: [conversation-design.md](../06-ai-interaction/conversation-design.md), Section 7, A06-10; Approved DEC-029.

**Current fixture preview with the unexported period slot visibly missing:**

> Your TDS is higher because you declared income from your previous employer for Not available in generated data. That income is added to your yearly income, so your expected yearly tax is higher. The tax your previous employer already deducted is counted, so it is not deducted twice.

The slot requires the accepted declaration’s declared month range. Neither /display_inputs/months comparison periods nor the declaration ID supplies that range. It stays unavailable until the engine exports it. Other words are unchanged from approved C29.

## 8. Exact generated data bindings

The exact-value column is the source value, not an instruction to render null as a number. Null required amounts render **Not available in generated data**; null non-applicable due dates follow their complete generated formula. All IDs and pointers are designer references. Every ordinary source calculation also exposes its own inputs, formula, rule_ids, certainty and flags in the authorized proof view.

### hike

| Binding | Field | Exact value | Generated file and record | JSON pointer |
|---|---|---|---|---|
| H-gross_arrears | Gross arrears | `71200` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; REV-E01 | `/result/totals/gross_arrears/value` |
| H-tds_impact | Estimated TDS impact | `3724` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; REV-E01 | `/result/totals/tds_impact/value` |
| H-recurring_salary_tds_impact | Recurring salary TDS impact | `1872` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; REV-E01 | `/result/totals/recurring_salary_tds_impact/value` |
| H-arrears_only_tds_impact | Arrears-only TDS impact | `1852` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; REV-E01 | `/result/totals/arrears_only_tds_impact/value` |
| H-net_arrears | Expected net arrears | `67476` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; REV-E01 | `/result/totals/net_arrears/value` |
| H-pf | Employee PF change | `0` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; REV-E01 | `/result/totals/pf_change/employee/value` |
| H-month | Estimated payment month | `2026-10` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; REV-E01 | `/result/estimated_payment_month` |
| H-flag | Estimate flag | `Estimated TDS if approved and paid in October 2026 payroll` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; REV-E01 | `/result/flags/0` |

### hike-months

| Binding | Field | Exact value | Generated file and record | JSON pointer |
|---|---|---|---|---|
| HM-0-period | Period | `2026-04` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; REV-E01; 2026-04 | `/result/months/0/month` |
| HM-0-old | Old earned amount | `120000` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; REV-E01; 2026-04 | `/result/months/0/old/gross/value` |
| HM-0-new | Revised earned amount | `132000` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; REV-E01; 2026-04 | `/result/months/0/revised/gross/value` |
| HM-0-diff | Arrears | `12000` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; REV-E01; 2026-04 | `/result/months/0/difference/value` |
| HM-0-pf | Employee PF change | `0` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; REV-E01; 2026-04 | `/result/months/0/pf_change/employee/value` |
| HM-0-tds | Incremental estimated arrears TDS | `312` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; REV-E01; 2026-04 | `/result/months/0/tds_impact/value` |
| HM-1-period | Period | `2026-05` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; REV-E01; 2026-05 | `/result/months/1/month` |
| HM-1-old | Old earned amount | `120000` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; REV-E01; 2026-05 | `/result/months/1/old/gross/value` |
| HM-1-new | Revised earned amount | `132000` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; REV-E01; 2026-05 | `/result/months/1/revised/gross/value` |
| HM-1-diff | Arrears | `12000` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; REV-E01; 2026-05 | `/result/months/1/difference/value` |
| HM-1-pf | Employee PF change | `0` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; REV-E01; 2026-05 | `/result/months/1/pf_change/employee/value` |
| HM-1-tds | Incremental estimated arrears TDS | `312` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; REV-E01; 2026-05 | `/result/months/1/tds_impact/value` |
| HM-2-period | Period | `2026-06` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; REV-E01; 2026-06 | `/result/months/2/month` |
| HM-2-old | Old earned amount | `112000` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; REV-E01; 2026-06 | `/result/months/2/old/gross/value` |
| HM-2-new | Revised earned amount | `123200` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; REV-E01; 2026-06 | `/result/months/2/revised/gross/value` |
| HM-2-diff | Arrears | `11200` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; REV-E01; 2026-06 | `/result/months/2/difference/value` |
| HM-2-pf | Employee PF change | `0` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; REV-E01; 2026-06 | `/result/months/2/pf_change/employee/value` |
| HM-2-tds | Incremental estimated arrears TDS | `292` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; REV-E01; 2026-06 | `/result/months/2/tds_impact/value` |
| HM-3-period | Period | `2026-07` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; REV-E01; 2026-07 | `/result/months/3/month` |
| HM-3-old | Old earned amount | `120000` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; REV-E01; 2026-07 | `/result/months/3/old/gross/value` |
| HM-3-new | Revised earned amount | `132000` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; REV-E01; 2026-07 | `/result/months/3/revised/gross/value` |
| HM-3-diff | Arrears | `12000` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; REV-E01; 2026-07 | `/result/months/3/difference/value` |
| HM-3-pf | Employee PF change | `0` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; REV-E01; 2026-07 | `/result/months/3/pf_change/employee/value` |
| HM-3-tds | Incremental estimated arrears TDS | `312` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; REV-E01; 2026-07 | `/result/months/3/tds_impact/value` |
| HM-4-period | Period | `2026-08` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; REV-E01; 2026-08 | `/result/months/4/month` |
| HM-4-old | Old earned amount | `120000` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; REV-E01; 2026-08 | `/result/months/4/old/gross/value` |
| HM-4-new | Revised earned amount | `132000` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; REV-E01; 2026-08 | `/result/months/4/revised/gross/value` |
| HM-4-diff | Arrears | `12000` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; REV-E01; 2026-08 | `/result/months/4/difference/value` |
| HM-4-pf | Employee PF change | `0` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; REV-E01; 2026-08 | `/result/months/4/pf_change/employee/value` |
| HM-4-tds | Incremental estimated arrears TDS | `312` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; REV-E01; 2026-08 | `/result/months/4/tds_impact/value` |
| HM-5-period | Period | `2026-09` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; REV-E01; 2026-09 | `/result/months/5/month` |
| HM-5-old | Old earned amount | `120000` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; REV-E01; 2026-09 | `/result/months/5/old/gross/value` |
| HM-5-new | Revised earned amount | `132000` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; REV-E01; 2026-09 | `/result/months/5/revised/gross/value` |
| HM-5-diff | Arrears | `12000` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; REV-E01; 2026-09 | `/result/months/5/difference/value` |
| HM-5-pf | Employee PF change | `0` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; REV-E01; 2026-09 | `/result/months/5/pf_change/employee/value` |
| HM-5-tds | Incremental estimated arrears TDS | `312` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; REV-E01; 2026-09 | `/result/months/5/tds_impact/value` |

### hike-alternates

| Binding | Field | Exact value | Generated file and record | JSON pointer |
|---|---|---|---|---|
| H2-gross_arrears | gross_arrears | `7200` | [scenarios/scenario-02.json](../../data/generated/scenarios/scenario-02.json); scenario-02; REV-E02 | `/result/totals/gross_arrears/value` |
| H2-tds_impact | tds_impact | `0` | [scenarios/scenario-02.json](../../data/generated/scenarios/scenario-02.json); scenario-02; REV-E02 | `/result/totals/tds_impact/value` |
| H2-net_arrears | net_arrears | `7099` | [scenarios/scenario-02.json](../../data/generated/scenarios/scenario-02.json); scenario-02; REV-E02 | `/result/totals/net_arrears/value` |
| H3-gross_arrears | gross_arrears | `null` | [scenarios/scenario-03.json](../../data/generated/scenarios/scenario-03.json); scenario-03; REV-E03 | `/result/totals/gross_arrears/value` |
| H3-tds_impact | tds_impact | `null` | [scenarios/scenario-03.json](../../data/generated/scenarios/scenario-03.json); scenario-03; REV-E03 | `/result/totals/tds_impact/value` |
| H3-net_arrears | net_arrears | `null` | [scenarios/scenario-03.json](../../data/generated/scenarios/scenario-03.json); scenario-03; REV-E03 | `/result/totals/net_arrears/value` |
| H2-old | Original September employee PF | `1968` | [scenarios/scenario-02.json](../../data/generated/scenarios/scenario-02.json); scenario-02; REV-E02; 2026-09 | `/result/months/1/old_pf/employee/value` |
| H2-new | Revised September employee PF | `2069` | [scenarios/scenario-02.json](../../data/generated/scenarios/scenario-02.json); scenario-02; REV-E02; 2026-09 | `/result/months/1/revised_pf/employee/value` |
| H2-diff | September employee PF change | `101` | [scenarios/scenario-02.json](../../data/generated/scenarios/scenario-02.json); scenario-02; REV-E02; 2026-09 | `/result/months/1/pf_change/employee/value` |
| H2-date | Changed PF segment begins | `2026-09-17` | [scenarios/scenario-02.json](../../data/generated/scenarios/scenario-02.json); scenario-02; REV-E02; 2026-09 | `/result/months/1/old_pf/segments/1/start/value` |
| H3-july | Missing period | `2026-07` | [scenarios/scenario-03.json](../../data/generated/scenarios/scenario-03.json); scenario-03; REV-E03 | `/result/months/0/month` |
| H3-aug-diff | Known August arrears | `4800` | [scenarios/scenario-03.json](../../data/generated/scenarios/scenario-03.json); scenario-03; REV-E03 | `/result/months/1/difference/value` |
| H3-sep-diff | Known September arrears | `4800` | [scenarios/scenario-03.json](../../data/generated/scenarios/scenario-03.json); scenario-03; REV-E03 | `/result/months/2/difference/value` |
| H-june-pf | Original June employee PF | `1800` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; REV-E01 | `/result/months/2/old_pf/employee/value` |
| H-june-earned-pf | June earned PF wage | `56000` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; REV-E01 | `/result/months/2/old_pf/monthly_earned_pf_wage/value` |
| H2-segment-0-days | PF segment calendar days | `16` | [scenarios/scenario-02.json](../../data/generated/scenarios/scenario-02.json); scenario-02; REV-E02 | `/result/months/1/old_pf/segments/0/days/value` |
| H2-segment-1-days | PF segment calendar days | `14` | [scenarios/scenario-02.json](../../data/generated/scenarios/scenario-02.json); scenario-02; REV-E02 | `/result/months/1/old_pf/segments/1/days/value` |

### salary

| Binding | Field | Exact value | Generated file and record | JSON pointer |
|---|---|---|---|---|
| C9-before_month | Earlier period | `2026-08` | [scenarios/scenario-09.json](../../data/generated/scenarios/scenario-09.json); scenario-09 | `/result/before_month` |
| C9-after_month | Later period | `2026-09` | [scenarios/scenario-09.json](../../data/generated/scenarios/scenario-09.json); scenario-09 | `/result/after_month` |
| C9-net_change | Take-home change | `-5420` | [scenarios/scenario-09.json](../../data/generated/scenarios/scenario-09.json); scenario-09 | `/result/net_change/value` |
| C9-gross_change | Gross change | `-5000` | [scenarios/scenario-09.json](../../data/generated/scenarios/scenario-09.json); scenario-09 | `/result/gross_change/value` |
| C9-employee_pf_change | Employee PF change | `420` | [scenarios/scenario-09.json](../../data/generated/scenarios/scenario-09.json); scenario-09 | `/result/employee_pf_change/value` |
| C9-tds_change | TDS change | `0` | [scenarios/scenario-09.json](../../data/generated/scenarios/scenario-09.json); scenario-09 | `/result/tds_change/value` |
| C9-before-net_pay | Take-home pay | `48200` | [scenarios/scenario-09.json](../../data/generated/scenarios/scenario-09.json); scenario-09 | `/result/before/net_pay/value` |
| C9-before-total_deductions | Total employee deductions | `1800` | [scenarios/scenario-09.json](../../data/generated/scenarios/scenario-09.json); scenario-09 | `/result/before/total_deductions/value` |
| C9-before-pf-employee | Employee PF | `1800` | [scenarios/scenario-09.json](../../data/generated/scenarios/scenario-09.json); scenario-09 | `/result/before/pf/employee/value` |
| C9-before-pf-employer | Employer contribution | `1800` | [scenarios/scenario-09.json](../../data/generated/scenarios/scenario-09.json); scenario-09 | `/result/before/pf/employer/value` |
| C9-before-pf-eps | Employer pension share | `1250` | [scenarios/scenario-09.json](../../data/generated/scenarios/scenario-09.json); scenario-09 | `/result/before/pf/eps/value` |
| C9-before-pf-epf | Employer provident fund share | `550` | [scenarios/scenario-09.json](../../data/generated/scenarios/scenario-09.json); scenario-09 | `/result/before/pf/epf/value` |
| C9-before-gross | Earned gross | `50000` | [scenarios/scenario-09.json](../../data/generated/scenarios/scenario-09.json); scenario-09 | `/result/before/earnings/gross/value` |
| C9-before-tds | Monthly TDS | `0` | [scenarios/scenario-09.json](../../data/generated/scenarios/scenario-09.json); scenario-09 | `/result/before/tds/amount/value` |
| C9-before-paid | Paid days | `31` | [scenarios/scenario-09.json](../../data/generated/scenarios/scenario-09.json); scenario-09 | `/result/before/earnings/paid_days/value` |
| C9-before-basic | basic | `25000` | [scenarios/scenario-09.json](../../data/generated/scenarios/scenario-09.json); scenario-09 | `/result/before/earnings/lines/basic/value` |
| C9-before-da | da | `0` | [scenarios/scenario-09.json](../../data/generated/scenarios/scenario-09.json); scenario-09 | `/result/before/earnings/lines/da/value` |
| C9-before-hra | hra | `12500` | [scenarios/scenario-09.json](../../data/generated/scenarios/scenario-09.json); scenario-09 | `/result/before/earnings/lines/hra/value` |
| C9-before-special_allowance | special_allowance | `12500` | [scenarios/scenario-09.json](../../data/generated/scenarios/scenario-09.json); scenario-09 | `/result/before/earnings/lines/special_allowance/value` |
| C9-after-net_pay | Take-home pay | `42780` | [scenarios/scenario-09.json](../../data/generated/scenarios/scenario-09.json); scenario-09 | `/result/after/net_pay/value` |
| C9-after-total_deductions | Total employee deductions | `2220` | [scenarios/scenario-09.json](../../data/generated/scenarios/scenario-09.json); scenario-09 | `/result/after/total_deductions/value` |
| C9-after-pf-employee | Employee PF | `2220` | [scenarios/scenario-09.json](../../data/generated/scenarios/scenario-09.json); scenario-09 | `/result/after/pf/employee/value` |
| C9-after-pf-employer | Employer contribution | `2220` | [scenarios/scenario-09.json](../../data/generated/scenarios/scenario-09.json); scenario-09 | `/result/after/pf/employer/value` |
| C9-after-pf-eps | Employer pension share | `1541` | [scenarios/scenario-09.json](../../data/generated/scenarios/scenario-09.json); scenario-09 | `/result/after/pf/eps/value` |
| C9-after-pf-epf | Employer provident fund share | `679` | [scenarios/scenario-09.json](../../data/generated/scenarios/scenario-09.json); scenario-09 | `/result/after/pf/epf/value` |
| C9-after-gross | Earned gross | `45000` | [scenarios/scenario-09.json](../../data/generated/scenarios/scenario-09.json); scenario-09 | `/result/after/earnings/gross/value` |
| C9-after-tds | Monthly TDS | `0` | [scenarios/scenario-09.json](../../data/generated/scenarios/scenario-09.json); scenario-09 | `/result/after/tds/amount/value` |
| C9-after-paid | Paid days | `27` | [scenarios/scenario-09.json](../../data/generated/scenarios/scenario-09.json); scenario-09 | `/result/after/earnings/paid_days/value` |
| C9-after-basic | basic | `22500` | [scenarios/scenario-09.json](../../data/generated/scenarios/scenario-09.json); scenario-09 | `/result/after/earnings/lines/basic/value` |
| C9-after-da | da | `0` | [scenarios/scenario-09.json](../../data/generated/scenarios/scenario-09.json); scenario-09 | `/result/after/earnings/lines/da/value` |
| C9-after-hra | hra | `11250` | [scenarios/scenario-09.json](../../data/generated/scenarios/scenario-09.json); scenario-09 | `/result/after/earnings/lines/hra/value` |
| C9-after-special_allowance | special_allowance | `11250` | [scenarios/scenario-09.json](../../data/generated/scenarios/scenario-09.json); scenario-09 | `/result/after/earnings/lines/special_allowance/value` |

### tax

| Binding | Field | Exact value | Generated file and record | JSON pointer |
|---|---|---|---|---|
| C10-before_month | Earlier period | `2026-08` | [scenarios/scenario-10.json](../../data/generated/scenarios/scenario-10.json); scenario-10 | `/result/before_month` |
| C10-after_month | Later period | `2026-09` | [scenarios/scenario-10.json](../../data/generated/scenarios/scenario-10.json); scenario-10 | `/result/after_month` |
| C10-net_change | Take-home change | `-13014` | [scenarios/scenario-10.json](../../data/generated/scenarios/scenario-10.json); scenario-10 | `/result/net_change/value` |
| C10-gross_change | Gross change | `0` | [scenarios/scenario-10.json](../../data/generated/scenarios/scenario-10.json); scenario-10 | `/result/gross_change/value` |
| C10-employee_pf_change | Employee PF change | `560` | [scenarios/scenario-10.json](../../data/generated/scenarios/scenario-10.json); scenario-10 | `/result/employee_pf_change/value` |
| C10-tds_change | TDS change | `12454` | [scenarios/scenario-10.json](../../data/generated/scenarios/scenario-10.json); scenario-10 | `/result/tds_change/value` |
| C10-before-net_pay | Take-home pay | `118200` | [scenarios/scenario-10.json](../../data/generated/scenarios/scenario-10.json); scenario-10 | `/result/before/net_pay/value` |
| C10-before-total_deductions | Total employee deductions | `1800` | [scenarios/scenario-10.json](../../data/generated/scenarios/scenario-10.json); scenario-10 | `/result/before/total_deductions/value` |
| C10-before-pf-employee | Employee PF | `1800` | [scenarios/scenario-10.json](../../data/generated/scenarios/scenario-10.json); scenario-10 | `/result/before/pf/employee/value` |
| C10-before-gross | Earned gross | `120000` | [scenarios/scenario-10.json](../../data/generated/scenarios/scenario-10.json); scenario-10 | `/result/before/earnings/gross/value` |
| C10-before-tds | Monthly TDS | `0` | [scenarios/scenario-10.json](../../data/generated/scenarios/scenario-10.json); scenario-10 | `/result/before/tds/amount/value` |
| C10-after-net_pay | Take-home pay | `105186` | [scenarios/scenario-10.json](../../data/generated/scenarios/scenario-10.json); scenario-10 | `/result/after/net_pay/value` |
| C10-after-total_deductions | Total employee deductions | `14814` | [scenarios/scenario-10.json](../../data/generated/scenarios/scenario-10.json); scenario-10 | `/result/after/total_deductions/value` |
| C10-after-pf-employee | Employee PF | `2360` | [scenarios/scenario-10.json](../../data/generated/scenarios/scenario-10.json); scenario-10 | `/result/after/pf/employee/value` |
| C10-after-gross | Earned gross | `120000` | [scenarios/scenario-10.json](../../data/generated/scenarios/scenario-10.json); scenario-10 | `/result/after/earnings/gross/value` |
| C10-after-tds | Monthly TDS | `12454` | [scenarios/scenario-10.json](../../data/generated/scenarios/scenario-10.json); scenario-10 | `/result/after/tds/amount/value` |
| T-projected_gross | Projected yearly gross income | `1530000` | [scenarios/scenario-10.json](../../data/generated/scenarios/scenario-10.json); scenario-10 | `/result/after/tds/projected_gross/value` |
| T-standard_deduction | Standard deduction | `75000` | [scenarios/scenario-10.json](../../data/generated/scenarios/scenario-10.json); scenario-10 | `/result/after/tds/standard_deduction/value` |
| T-taxable_income | Projected taxable income | `1455000` | [scenarios/scenario-10.json](../../data/generated/scenarios/scenario-10.json); scenario-10 | `/result/after/tds/taxable_income/value` |
| T-slab_tax | Yearly tax before cess | `98250` | [scenarios/scenario-10.json](../../data/generated/scenarios/scenario-10.json); scenario-10 | `/result/after/tds/slab_tax/value` |
| T-cess | Cess | `3930` | [scenarios/scenario-10.json](../../data/generated/scenarios/scenario-10.json); scenario-10 | `/result/after/tds/cess/value` |
| T-yearly_tax | Yearly tax including cess | `102180` | [scenarios/scenario-10.json](../../data/generated/scenarios/scenario-10.json); scenario-10 | `/result/after/tds/yearly_tax/value` |
| T-tax_already_deducted | Tax already deducted | `15000` | [scenarios/scenario-10.json](../../data/generated/scenarios/scenario-10.json); scenario-10 | `/result/after/tds/tax_already_deducted/value` |
| T-remaining_months | Remaining months | `7` | [scenarios/scenario-10.json](../../data/generated/scenarios/scenario-10.json); scenario-10 | `/result/after/tds/remaining_months/value` |

### unchanged

| Binding | Field | Exact value | Generated file and record | JSON pointer |
|---|---|---|---|---|
| C11-before_month | Earlier period | `2026-08` | [scenarios/scenario-11.json](../../data/generated/scenarios/scenario-11.json); scenario-11 | `/result/before_month` |
| C11-after_month | Later period | `2026-09` | [scenarios/scenario-11.json](../../data/generated/scenarios/scenario-11.json); scenario-11 | `/result/after_month` |
| C11-net_change | Take-home change | `-420` | [scenarios/scenario-11.json](../../data/generated/scenarios/scenario-11.json); scenario-11 | `/result/net_change/value` |
| C11-gross_change | Gross change | `0` | [scenarios/scenario-11.json](../../data/generated/scenarios/scenario-11.json); scenario-11 | `/result/gross_change/value` |
| C11-employee_pf_change | Employee PF change | `420` | [scenarios/scenario-11.json](../../data/generated/scenarios/scenario-11.json); scenario-11 | `/result/employee_pf_change/value` |
| C11-tds_change | TDS change | `0` | [scenarios/scenario-11.json](../../data/generated/scenarios/scenario-11.json); scenario-11 | `/result/tds_change/value` |
| C11-before-net_pay | Take-home pay | `43200` | [scenarios/scenario-11.json](../../data/generated/scenarios/scenario-11.json); scenario-11 | `/result/before/net_pay/value` |
| C11-before-total_deductions | Total employee deductions | `1800` | [scenarios/scenario-11.json](../../data/generated/scenarios/scenario-11.json); scenario-11 | `/result/before/total_deductions/value` |
| C11-before-pf-employee | Employee PF | `1800` | [scenarios/scenario-11.json](../../data/generated/scenarios/scenario-11.json); scenario-11 | `/result/before/pf/employee/value` |
| C11-before-gross | Earned gross | `45000` | [scenarios/scenario-11.json](../../data/generated/scenarios/scenario-11.json); scenario-11 | `/result/before/earnings/gross/value` |
| C11-before-tds | Monthly TDS | `0` | [scenarios/scenario-11.json](../../data/generated/scenarios/scenario-11.json); scenario-11 | `/result/before/tds/amount/value` |
| C11-after-net_pay | Take-home pay | `42780` | [scenarios/scenario-11.json](../../data/generated/scenarios/scenario-11.json); scenario-11 | `/result/after/net_pay/value` |
| C11-after-total_deductions | Total employee deductions | `2220` | [scenarios/scenario-11.json](../../data/generated/scenarios/scenario-11.json); scenario-11 | `/result/after/total_deductions/value` |
| C11-after-pf-employee | Employee PF | `2220` | [scenarios/scenario-11.json](../../data/generated/scenarios/scenario-11.json); scenario-11 | `/result/after/pf/employee/value` |
| C11-after-gross | Earned gross | `45000` | [scenarios/scenario-11.json](../../data/generated/scenarios/scenario-11.json); scenario-11 | `/result/after/earnings/gross/value` |
| C11-after-tds | Monthly TDS | `0` | [scenarios/scenario-11.json](../../data/generated/scenarios/scenario-11.json); scenario-11 | `/result/after/tds/amount/value` |

### bonus

| Binding | Field | Exact value | Generated file and record | JSON pointer |
|---|---|---|---|---|
| B0-gross | Known eligible gross | `213929` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04 | `/result/bonus_requests/0/known_eligible_gross/value` |
| B0-period | Bonus period | `FY 2025-26` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04 | `/result/bonus_requests/0/period` |
| B-E01-amount | amount | `108000` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04; E01 | `/result/bonus_requests/0/employees/0/amount/value` |
| B-E01-tds_impact | tds_impact | `2808` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04; E01 | `/result/bonus_requests/0/employees/0/tds_impact/value` |
| B-E01-net_amount | net_amount | `105192` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04; E01 | `/result/bonus_requests/0/employees/0/net_amount/value` |
| B-E03-amount | amount | `36000` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04; E03 | `/result/bonus_requests/0/employees/1/amount/value` |
| B-E03-tds_impact | tds_impact | `null` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04; E03 | `/result/bonus_requests/0/employees/1/tds_impact/value` |
| B-E03-net_amount | net_amount | `null` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04; E03 | `/result/bonus_requests/0/employees/1/net_amount/value` |
| B-E04-amount | amount | `60000` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04; E04 | `/result/bonus_requests/0/employees/2/amount/value` |
| B-E04-tds_impact | tds_impact | `0` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04; E04 | `/result/bonus_requests/0/employees/2/tds_impact/value` |
| B-E04-net_amount | net_amount | `60000` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04; E04 | `/result/bonus_requests/0/employees/2/net_amount/value` |
| B-E07-amount | amount | `9929` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04; E07 | `/result/bonus_requests/0/employees/3/amount/value` |
| B-E07-tds_impact | tds_impact | `0` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04; E07 | `/result/bonus_requests/0/employees/3/tds_impact/value` |
| B-E07-net_amount | net_amount | `9929` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04; E07 | `/result/bonus_requests/0/employees/3/net_amount/value` |
| B-E07-annual_basic | annual_basic | `480000` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04; E07 | `/result/bonus_requests/0/employees/3/annual_basic/value` |
| B-E07-eligible_days | eligible_days | `151` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04; E07 | `/result/bonus_requests/0/employees/3/eligible_days/value` |
| B-E07-period_days | period_days | `365` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04; E07 | `/result/bonus_requests/0/employees/3/period_days/value` |
| B-E08-amount | amount | `0` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04; E08 | `/result/bonus_requests/0/employees/4/amount/value` |
| B-E09-amount | amount | `null` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04; E09 | `/result/bonus_requests/0/employees/5/amount/value` |
| B1-gross | Known eligible gross | `120000` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04 | `/result/bonus_requests/1/known_eligible_gross/value` |
| B1-period | Bonus period | `Q2 2026-27` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04 | `/result/bonus_requests/1/period` |
| B-E13-amount | amount | `20000` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04; E13 | `/result/bonus_requests/1/employees/0/amount/value` |
| B-E13-tds_impact | tds_impact | `0` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04; E13 | `/result/bonus_requests/1/employees/0/tds_impact/value` |
| B-E13-net_amount | net_amount | `20000` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04; E13 | `/result/bonus_requests/1/employees/0/net_amount/value` |
| B-E13-achievement_percent | achievement_percent | `85.00` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04; E13 | `/result/bonus_requests/1/employees/0/achievement_percent/value` |
| B-E14-amount | amount | `40000` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04; E14 | `/result/bonus_requests/1/employees/1/amount/value` |
| B-E14-tds_impact | tds_impact | `0` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04; E14 | `/result/bonus_requests/1/employees/1/tds_impact/value` |
| B-E14-net_amount | net_amount | `40000` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04; E14 | `/result/bonus_requests/1/employees/1/net_amount/value` |
| B-E14-achievement_percent | achievement_percent | `105.00` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04; E14 | `/result/bonus_requests/1/employees/1/achievement_percent/value` |
| B-E15-amount | amount | `60000` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04; E15 | `/result/bonus_requests/1/employees/2/amount/value` |
| B-E15-tds_impact | tds_impact | `0` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04; E15 | `/result/bonus_requests/1/employees/2/tds_impact/value` |
| B-E15-net_amount | net_amount | `60000` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04; E15 | `/result/bonus_requests/1/employees/2/net_amount/value` |
| B-E15-achievement_percent | achievement_percent | `125.00` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04; E15 | `/result/bonus_requests/1/employees/2/achievement_percent/value` |

### settlement

| Binding | Field | Exact value | Generated file and record | JSON pointer |
|---|---|---|---|---|
| S6-gross_payables | gross_payables | `335256` | [scenarios/scenario-06.json](../../data/generated/scenarios/scenario-06.json); scenario-06; E10 | `/result/gross_payables/value` |
| S6-total_deductions | total_deductions | `3000` | [scenarios/scenario-06.json](../../data/generated/scenarios/scenario-06.json); scenario-06; E10 | `/result/total_deductions/value` |
| S6-final_net | final_net | `332256` | [scenarios/scenario-06.json](../../data/generated/scenarios/scenario-06.json); scenario-06; E10 | `/result/final_net/value` |
| S6-employee_pf | employee_pf | `3000` | [scenarios/scenario-06.json](../../data/generated/scenarios/scenario-06.json); scenario-06; E10 | `/result/employee_pf/value` |
| S6-tds | tds | `0` | [scenarios/scenario-06.json](../../data/generated/scenarios/scenario-06.json); scenario-06; E10 | `/result/tds/value` |
| S6-final_month_salary | final_month_salary | `100000` | [scenarios/scenario-06.json](../../data/generated/scenarios/scenario-06.json); scenario-06; E10 | `/result/components/final_month_salary/amount/value` |
| S6-final_month_salary-date | final_month_salary applicable due date | `2026-11-03` | [scenarios/scenario-06.json](../../data/generated/scenarios/scenario-06.json); scenario-06; E10 | `/result/components/final_month_salary/applicable_due_date/value` |
| S6-leave_encashment | leave_encashment | `33333` | [scenarios/scenario-06.json](../../data/generated/scenarios/scenario-06.json); scenario-06; E10 | `/result/components/leave_encashment/amount/value` |
| S6-leave_encashment-date | leave_encashment applicable due date | `2026-11-03` | [scenarios/scenario-06.json](../../data/generated/scenarios/scenario-06.json); scenario-06; E10 | `/result/components/leave_encashment/applicable_due_date/value` |
| S6-gratuity | gratuity | `201923` | [scenarios/scenario-06.json](../../data/generated/scenarios/scenario-06.json); scenario-06; E10 | `/result/components/gratuity/amount/value` |
| S6-gratuity-date | gratuity applicable due date | `2026-12-01` | [scenarios/scenario-06.json](../../data/generated/scenarios/scenario-06.json); scenario-06; E10 | `/result/components/gratuity/applicable_due_date/value` |
| S6-notice_shortfall_recovery | notice_shortfall_recovery | `0` | [scenarios/scenario-06.json](../../data/generated/scenarios/scenario-06.json); scenario-06; E10 | `/result/components/notice_shortfall_recovery/amount/value` |
| S6-notice_shortfall_recovery-date | notice_shortfall_recovery applicable due date | `null` | [scenarios/scenario-06.json](../../data/generated/scenarios/scenario-06.json); scenario-06; E10 | `/result/components/notice_shortfall_recovery/applicable_due_date/value` |
| S6-loan_and_advance_recovery | loan_and_advance_recovery | `0` | [scenarios/scenario-06.json](../../data/generated/scenarios/scenario-06.json); scenario-06; E10 | `/result/components/loan_and_advance_recovery/amount/value` |
| S6-loan_and_advance_recovery-date | loan_and_advance_recovery applicable due date | `null` | [scenarios/scenario-06.json](../../data/generated/scenarios/scenario-06.json); scenario-06; E10 | `/result/components/loan_and_advance_recovery/applicable_due_date/value` |
| S6-asset_recovery | asset_recovery | `0` | [scenarios/scenario-06.json](../../data/generated/scenarios/scenario-06.json); scenario-06; E10 | `/result/components/asset_recovery/amount/value` |
| S6-asset_recovery-date | asset_recovery applicable due date | `null` | [scenarios/scenario-06.json](../../data/generated/scenarios/scenario-06.json); scenario-06; E10 | `/result/components/asset_recovery/applicable_due_date/value` |
| S6-service-years | Actual service years | `7` | [scenarios/scenario-06.json](../../data/generated/scenarios/scenario-06.json); scenario-06; E10 | `/result/components/gratuity/service/years/value` |
| S6-service-months | Actual service months | `4` | [scenarios/scenario-06.json](../../data/generated/scenarios/scenario-06.json); scenario-06; E10 | `/result/components/gratuity/service/months/value` |
| S6-service-days | Actual service days | `30` | [scenarios/scenario-06.json](../../data/generated/scenarios/scenario-06.json); scenario-06; E10 | `/result/components/gratuity/service/days/value` |
| S7-gross_payables | gross_payables | `96000` | [scenarios/scenario-07.json](../../data/generated/scenarios/scenario-07.json); scenario-07; E11 | `/result/gross_payables/value` |
| S7-total_deductions | total_deductions | `3000` | [scenarios/scenario-07.json](../../data/generated/scenarios/scenario-07.json); scenario-07; E11 | `/result/total_deductions/value` |
| S7-final_net | final_net | `93000` | [scenarios/scenario-07.json](../../data/generated/scenarios/scenario-07.json); scenario-07; E11 | `/result/final_net/value` |
| S7-employee_pf | employee_pf | `3000` | [scenarios/scenario-07.json](../../data/generated/scenarios/scenario-07.json); scenario-07; E11 | `/result/employee_pf/value` |
| S7-tds | tds | `0` | [scenarios/scenario-07.json](../../data/generated/scenarios/scenario-07.json); scenario-07; E11 | `/result/tds/value` |
| S7-final_month_salary | final_month_salary | `80000` | [scenarios/scenario-07.json](../../data/generated/scenarios/scenario-07.json); scenario-07; E11 | `/result/components/final_month_salary/amount/value` |
| S7-final_month_salary-date | final_month_salary applicable due date | `2026-11-03` | [scenarios/scenario-07.json](../../data/generated/scenarios/scenario-07.json); scenario-07; E11 | `/result/components/final_month_salary/applicable_due_date/value` |
| S7-leave_encashment | leave_encashment | `16000` | [scenarios/scenario-07.json](../../data/generated/scenarios/scenario-07.json); scenario-07; E11 | `/result/components/leave_encashment/amount/value` |
| S7-leave_encashment-date | leave_encashment applicable due date | `2026-11-03` | [scenarios/scenario-07.json](../../data/generated/scenarios/scenario-07.json); scenario-07; E11 | `/result/components/leave_encashment/applicable_due_date/value` |
| S7-gratuity | gratuity | `0` | [scenarios/scenario-07.json](../../data/generated/scenarios/scenario-07.json); scenario-07; E11 | `/result/components/gratuity/amount/value` |
| S7-gratuity-date | gratuity applicable due date | `null` | [scenarios/scenario-07.json](../../data/generated/scenarios/scenario-07.json); scenario-07; E11 | `/result/components/gratuity/applicable_due_date/value` |
| S7-notice_shortfall_recovery | notice_shortfall_recovery | `0` | [scenarios/scenario-07.json](../../data/generated/scenarios/scenario-07.json); scenario-07; E11 | `/result/components/notice_shortfall_recovery/amount/value` |
| S7-notice_shortfall_recovery-date | notice_shortfall_recovery applicable due date | `null` | [scenarios/scenario-07.json](../../data/generated/scenarios/scenario-07.json); scenario-07; E11 | `/result/components/notice_shortfall_recovery/applicable_due_date/value` |
| S7-loan_and_advance_recovery | loan_and_advance_recovery | `0` | [scenarios/scenario-07.json](../../data/generated/scenarios/scenario-07.json); scenario-07; E11 | `/result/components/loan_and_advance_recovery/amount/value` |
| S7-loan_and_advance_recovery-date | loan_and_advance_recovery applicable due date | `null` | [scenarios/scenario-07.json](../../data/generated/scenarios/scenario-07.json); scenario-07; E11 | `/result/components/loan_and_advance_recovery/applicable_due_date/value` |
| S7-asset_recovery | asset_recovery | `0` | [scenarios/scenario-07.json](../../data/generated/scenarios/scenario-07.json); scenario-07; E11 | `/result/components/asset_recovery/amount/value` |
| S7-asset_recovery-date | asset_recovery applicable due date | `null` | [scenarios/scenario-07.json](../../data/generated/scenarios/scenario-07.json); scenario-07; E11 | `/result/components/asset_recovery/applicable_due_date/value` |
| S7-service-years | Actual service years | `4` | [scenarios/scenario-07.json](../../data/generated/scenarios/scenario-07.json); scenario-07; E11 | `/result/components/gratuity/service/years/value` |
| S7-service-months | Actual service months | `11` | [scenarios/scenario-07.json](../../data/generated/scenarios/scenario-07.json); scenario-07; E11 | `/result/components/gratuity/service/months/value` |
| S7-service-days | Actual service days | `11` | [scenarios/scenario-07.json](../../data/generated/scenarios/scenario-07.json); scenario-07; E11 | `/result/components/gratuity/service/days/value` |
| S13-gross_payables | gross_payables | `79333` | [scenarios/scenario-13.json](../../data/generated/scenarios/scenario-13.json); scenario-13; E12 | `/result/gross_payables/value` |
| S13-total_deductions | total_deductions | `null` | [scenarios/scenario-13.json](../../data/generated/scenarios/scenario-13.json); scenario-13; E12 | `/result/total_deductions/value` |
| S13-employee_pf | employee_pf | `3000` | [scenarios/scenario-13.json](../../data/generated/scenarios/scenario-13.json); scenario-13; E12 | `/result/employee_pf/value` |
| S13-tds | tds | `0` | [scenarios/scenario-13.json](../../data/generated/scenarios/scenario-13.json); scenario-13; E12 | `/result/tds/value` |
| S13-final_month_salary | final_month_salary | `70000` | [scenarios/scenario-13.json](../../data/generated/scenarios/scenario-13.json); scenario-13; E12 | `/result/components/final_month_salary/amount/value` |
| S13-final_month_salary-date | final_month_salary applicable due date | `2026-11-03` | [scenarios/scenario-13.json](../../data/generated/scenarios/scenario-13.json); scenario-13; E12 | `/result/components/final_month_salary/applicable_due_date/value` |
| S13-leave_encashment | leave_encashment | `9333` | [scenarios/scenario-13.json](../../data/generated/scenarios/scenario-13.json); scenario-13; E12 | `/result/components/leave_encashment/amount/value` |
| S13-leave_encashment-date | leave_encashment applicable due date | `2026-11-03` | [scenarios/scenario-13.json](../../data/generated/scenarios/scenario-13.json); scenario-13; E12 | `/result/components/leave_encashment/applicable_due_date/value` |
| S13-gratuity | gratuity | `0` | [scenarios/scenario-13.json](../../data/generated/scenarios/scenario-13.json); scenario-13; E12 | `/result/components/gratuity/amount/value` |
| S13-gratuity-date | gratuity applicable due date | `null` | [scenarios/scenario-13.json](../../data/generated/scenarios/scenario-13.json); scenario-13; E12 | `/result/components/gratuity/applicable_due_date/value` |
| S13-notice_shortfall_recovery | notice_shortfall_recovery | `46667` | [scenarios/scenario-13.json](../../data/generated/scenarios/scenario-13.json); scenario-13; E12 | `/result/components/notice_shortfall_recovery/amount/value` |
| S13-notice_shortfall_recovery-date | notice_shortfall_recovery applicable due date | `null` | [scenarios/scenario-13.json](../../data/generated/scenarios/scenario-13.json); scenario-13; E12 | `/result/components/notice_shortfall_recovery/applicable_due_date/value` |
| S13-loan_and_advance_recovery | loan_and_advance_recovery | `10000` | [scenarios/scenario-13.json](../../data/generated/scenarios/scenario-13.json); scenario-13; E12 | `/result/components/loan_and_advance_recovery/amount/value` |
| S13-loan_and_advance_recovery-date | loan_and_advance_recovery applicable due date | `null` | [scenarios/scenario-13.json](../../data/generated/scenarios/scenario-13.json); scenario-13; E12 | `/result/components/loan_and_advance_recovery/applicable_due_date/value` |
| S13-asset_recovery | asset_recovery | `null` | [scenarios/scenario-13.json](../../data/generated/scenarios/scenario-13.json); scenario-13; E12 | `/result/components/asset_recovery/amount/value` |
| S13-asset_recovery-date | asset_recovery applicable due date | `null` | [scenarios/scenario-13.json](../../data/generated/scenarios/scenario-13.json); scenario-13; E12 | `/result/components/asset_recovery/applicable_due_date/value` |

### query

| Binding | Field | Exact value | Generated file and record | JSON pointer |
|---|---|---|---|---|
| Q-id | Existing query ID | `QUERY-E05-SEPTEMBER` | [scenarios/scenario-09.json](../../data/generated/scenarios/scenario-09.json); scenario-09; QUERY-E05-SEPTEMBER | `/result/existing_query/query_id` |
| Q-status | Recorded query status | `In review` | [scenarios/scenario-09.json](../../data/generated/scenarios/scenario-09.json); scenario-09; QUERY-E05-SEPTEMBER | `/result/existing_query/status` |


### display inputs

| Binding | Field | Exact value | Generated file and record | JSON pointer |
|---|---|---|---|---|
| D01-requested_hike_percentage | requested hike percentage | `10` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; REV-E01 | `/display_inputs/requested_hike_percentage/value` |
| D01-effective_date | effective date | `2026-04-01` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; REV-E01 | `/display_inputs/effective_date/value` |
| D01-old_monthly_salary-components-basic | old monthly salary components basic | `60000` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; SS-E01 | `/display_inputs/old_monthly_salary/components/basic/value` |
| D01-old_monthly_salary-components-da | old monthly salary components da | `0` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; SS-E01 | `/display_inputs/old_monthly_salary/components/da/value` |
| D01-old_monthly_salary-components-hra | old monthly salary components hra | `30000` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; SS-E01 | `/display_inputs/old_monthly_salary/components/hra/value` |
| D01-old_monthly_salary-components-special_allowance | old monthly salary components special allowance | `30000` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; SS-E01 | `/display_inputs/old_monthly_salary/components/special_allowance/value` |
| D01-old_monthly_salary-total | old monthly salary total | `120000` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; scenario-01 | `/display_inputs/old_monthly_salary/total/value` |
| D01-proposed_monthly_salary-components-basic | proposed monthly salary components basic | `66000` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; scenario-01 | `/display_inputs/proposed_monthly_salary/components/basic/value` |
| D01-proposed_monthly_salary-components-da | proposed monthly salary components da | `0` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; scenario-01 | `/display_inputs/proposed_monthly_salary/components/da/value` |
| D01-proposed_monthly_salary-components-hra | proposed monthly salary components hra | `33000` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; scenario-01 | `/display_inputs/proposed_monthly_salary/components/hra/value` |
| D01-proposed_monthly_salary-components-special_allowance | proposed monthly salary components special allowance | `33000` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; scenario-01 | `/display_inputs/proposed_monthly_salary/components/special_allowance/value` |
| D01-proposed_monthly_salary-total | proposed monthly salary total | `132000` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; scenario-01 | `/display_inputs/proposed_monthly_salary/total/value` |
| D01-months-2026-04-lop_days | months 2026 04 lop days | `0` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; ATT-E01-2026-04 | `/display_inputs/months/2026-04/lop_days/value` |
| D01-months-2026-04-calendar_days | months 2026 04 calendar days | `30` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; ATT-E01-2026-04 | `/display_inputs/months/2026-04/calendar_days/value` |
| D01-months-2026-05-lop_days | months 2026 05 lop days | `0` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; ATT-E01-2026-05 | `/display_inputs/months/2026-05/lop_days/value` |
| D01-months-2026-05-calendar_days | months 2026 05 calendar days | `31` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; ATT-E01-2026-05 | `/display_inputs/months/2026-05/calendar_days/value` |
| D01-months-2026-06-lop_days | months 2026 06 lop days | `2` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; ATT-E01-2026-06 | `/display_inputs/months/2026-06/lop_days/value` |
| D01-months-2026-06-calendar_days | months 2026 06 calendar days | `30` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; ATT-E01-2026-06 | `/display_inputs/months/2026-06/calendar_days/value` |
| D01-months-2026-07-lop_days | months 2026 07 lop days | `0` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; ATT-E01-2026-07 | `/display_inputs/months/2026-07/lop_days/value` |
| D01-months-2026-07-calendar_days | months 2026 07 calendar days | `31` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; ATT-E01-2026-07 | `/display_inputs/months/2026-07/calendar_days/value` |
| D01-months-2026-08-lop_days | months 2026 08 lop days | `0` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; ATT-E01-2026-08 | `/display_inputs/months/2026-08/lop_days/value` |
| D01-months-2026-08-calendar_days | months 2026 08 calendar days | `31` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; ATT-E01-2026-08 | `/display_inputs/months/2026-08/calendar_days/value` |
| D01-months-2026-09-lop_days | months 2026 09 lop days | `0` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; ATT-E01-2026-09 | `/display_inputs/months/2026-09/lop_days/value` |
| D01-months-2026-09-calendar_days | months 2026 09 calendar days | `30` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; ATT-E01-2026-09 | `/display_inputs/months/2026-09/calendar_days/value` |
| D02-requested_hike_percentage | requested hike percentage | `10` | [scenarios/scenario-02.json](../../data/generated/scenarios/scenario-02.json); scenario-02; REV-E02 | `/display_inputs/requested_hike_percentage/value` |
| D02-effective_date | effective date | `2026-08-01` | [scenarios/scenario-02.json](../../data/generated/scenarios/scenario-02.json); scenario-02; REV-E02 | `/display_inputs/effective_date/value` |
| D02-old_monthly_salary-components-basic | old monthly salary components basic | `18000` | [scenarios/scenario-02.json](../../data/generated/scenarios/scenario-02.json); scenario-02; SS-E02 | `/display_inputs/old_monthly_salary/components/basic/value` |
| D02-old_monthly_salary-components-da | old monthly salary components da | `0` | [scenarios/scenario-02.json](../../data/generated/scenarios/scenario-02.json); scenario-02; SS-E02 | `/display_inputs/old_monthly_salary/components/da/value` |
| D02-old_monthly_salary-components-hra | old monthly salary components hra | `9000` | [scenarios/scenario-02.json](../../data/generated/scenarios/scenario-02.json); scenario-02; SS-E02 | `/display_inputs/old_monthly_salary/components/hra/value` |
| D02-old_monthly_salary-components-special_allowance | old monthly salary components special allowance | `9000` | [scenarios/scenario-02.json](../../data/generated/scenarios/scenario-02.json); scenario-02; SS-E02 | `/display_inputs/old_monthly_salary/components/special_allowance/value` |
| D02-old_monthly_salary-total | old monthly salary total | `36000` | [scenarios/scenario-02.json](../../data/generated/scenarios/scenario-02.json); scenario-02; scenario-02 | `/display_inputs/old_monthly_salary/total/value` |
| D02-proposed_monthly_salary-components-basic | proposed monthly salary components basic | `19800` | [scenarios/scenario-02.json](../../data/generated/scenarios/scenario-02.json); scenario-02; scenario-02 | `/display_inputs/proposed_monthly_salary/components/basic/value` |
| D02-proposed_monthly_salary-components-da | proposed monthly salary components da | `0` | [scenarios/scenario-02.json](../../data/generated/scenarios/scenario-02.json); scenario-02; scenario-02 | `/display_inputs/proposed_monthly_salary/components/da/value` |
| D02-proposed_monthly_salary-components-hra | proposed monthly salary components hra | `9900` | [scenarios/scenario-02.json](../../data/generated/scenarios/scenario-02.json); scenario-02; scenario-02 | `/display_inputs/proposed_monthly_salary/components/hra/value` |
| D02-proposed_monthly_salary-components-special_allowance | proposed monthly salary components special allowance | `9900` | [scenarios/scenario-02.json](../../data/generated/scenarios/scenario-02.json); scenario-02; scenario-02 | `/display_inputs/proposed_monthly_salary/components/special_allowance/value` |
| D02-proposed_monthly_salary-total | proposed monthly salary total | `39600` | [scenarios/scenario-02.json](../../data/generated/scenarios/scenario-02.json); scenario-02; scenario-02 | `/display_inputs/proposed_monthly_salary/total/value` |
| D02-months-2026-08-lop_days | months 2026 08 lop days | `0` | [scenarios/scenario-02.json](../../data/generated/scenarios/scenario-02.json); scenario-02; ATT-E02-2026-08 | `/display_inputs/months/2026-08/lop_days/value` |
| D02-months-2026-08-calendar_days | months 2026 08 calendar days | `31` | [scenarios/scenario-02.json](../../data/generated/scenarios/scenario-02.json); scenario-02; ATT-E02-2026-08 | `/display_inputs/months/2026-08/calendar_days/value` |
| D02-months-2026-09-lop_days | months 2026 09 lop days | `0` | [scenarios/scenario-02.json](../../data/generated/scenarios/scenario-02.json); scenario-02; ATT-E02-2026-09 | `/display_inputs/months/2026-09/lop_days/value` |
| D02-months-2026-09-calendar_days | months 2026 09 calendar days | `30` | [scenarios/scenario-02.json](../../data/generated/scenarios/scenario-02.json); scenario-02; ATT-E02-2026-09 | `/display_inputs/months/2026-09/calendar_days/value` |
| D03-requested_hike_percentage | requested hike percentage | `8` | [scenarios/scenario-03.json](../../data/generated/scenarios/scenario-03.json); scenario-03; REV-E03 | `/display_inputs/requested_hike_percentage/value` |
| D03-effective_date | effective date | `2026-07-01` | [scenarios/scenario-03.json](../../data/generated/scenarios/scenario-03.json); scenario-03; REV-E03 | `/display_inputs/effective_date/value` |
| D03-old_monthly_salary-components-basic | old monthly salary components basic | `30000` | [scenarios/scenario-03.json](../../data/generated/scenarios/scenario-03.json); scenario-03; SS-E03 | `/display_inputs/old_monthly_salary/components/basic/value` |
| D03-old_monthly_salary-components-da | old monthly salary components da | `0` | [scenarios/scenario-03.json](../../data/generated/scenarios/scenario-03.json); scenario-03; SS-E03 | `/display_inputs/old_monthly_salary/components/da/value` |
| D03-old_monthly_salary-components-hra | old monthly salary components hra | `15000` | [scenarios/scenario-03.json](../../data/generated/scenarios/scenario-03.json); scenario-03; SS-E03 | `/display_inputs/old_monthly_salary/components/hra/value` |
| D03-old_monthly_salary-components-special_allowance | old monthly salary components special allowance | `15000` | [scenarios/scenario-03.json](../../data/generated/scenarios/scenario-03.json); scenario-03; SS-E03 | `/display_inputs/old_monthly_salary/components/special_allowance/value` |
| D03-old_monthly_salary-total | old monthly salary total | `60000` | [scenarios/scenario-03.json](../../data/generated/scenarios/scenario-03.json); scenario-03; scenario-03 | `/display_inputs/old_monthly_salary/total/value` |
| D03-proposed_monthly_salary-components-basic | proposed monthly salary components basic | `32400` | [scenarios/scenario-03.json](../../data/generated/scenarios/scenario-03.json); scenario-03; scenario-03 | `/display_inputs/proposed_monthly_salary/components/basic/value` |
| D03-proposed_monthly_salary-components-da | proposed monthly salary components da | `0` | [scenarios/scenario-03.json](../../data/generated/scenarios/scenario-03.json); scenario-03; scenario-03 | `/display_inputs/proposed_monthly_salary/components/da/value` |
| D03-proposed_monthly_salary-components-hra | proposed monthly salary components hra | `16200` | [scenarios/scenario-03.json](../../data/generated/scenarios/scenario-03.json); scenario-03; scenario-03 | `/display_inputs/proposed_monthly_salary/components/hra/value` |
| D03-proposed_monthly_salary-components-special_allowance | proposed monthly salary components special allowance | `16200` | [scenarios/scenario-03.json](../../data/generated/scenarios/scenario-03.json); scenario-03; scenario-03 | `/display_inputs/proposed_monthly_salary/components/special_allowance/value` |
| D03-proposed_monthly_salary-total | proposed monthly salary total | `64800` | [scenarios/scenario-03.json](../../data/generated/scenarios/scenario-03.json); scenario-03; scenario-03 | `/display_inputs/proposed_monthly_salary/total/value` |
| D03-months-2026-07-lop_days | months 2026 07 lop days | `null` | [scenarios/scenario-03.json](../../data/generated/scenarios/scenario-03.json); scenario-03; missing:E03:2026-07 | `/display_inputs/months/2026-07/lop_days/value` |
| D03-months-2026-07-calendar_days | months 2026 07 calendar days | `null` | [scenarios/scenario-03.json](../../data/generated/scenarios/scenario-03.json); scenario-03; missing:E03:2026-07 | `/display_inputs/months/2026-07/calendar_days/value` |
| D03-months-2026-08-lop_days | months 2026 08 lop days | `0` | [scenarios/scenario-03.json](../../data/generated/scenarios/scenario-03.json); scenario-03; ATT-E03-2026-08 | `/display_inputs/months/2026-08/lop_days/value` |
| D03-months-2026-08-calendar_days | months 2026 08 calendar days | `31` | [scenarios/scenario-03.json](../../data/generated/scenarios/scenario-03.json); scenario-03; ATT-E03-2026-08 | `/display_inputs/months/2026-08/calendar_days/value` |
| D03-months-2026-09-lop_days | months 2026 09 lop days | `0` | [scenarios/scenario-03.json](../../data/generated/scenarios/scenario-03.json); scenario-03; ATT-E03-2026-09 | `/display_inputs/months/2026-09/lop_days/value` |
| D03-months-2026-09-calendar_days | months 2026 09 calendar days | `30` | [scenarios/scenario-03.json](../../data/generated/scenarios/scenario-03.json); scenario-03; ATT-E03-2026-09 | `/display_inputs/months/2026-09/calendar_days/value` |
| D04-bonus_requests-0-employees-E01-rating | bonus requests 0 employees E01 rating | `5` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04; PERF-E01-FY2025-26 | `/display_inputs/bonus_requests/0/employees/E01/rating/value` |
| D04-bonus_requests-0-employees-E01-policy_rating_rate_percent | bonus requests 0 employees E01 policy rating rate percent | `15` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04; annual_performance_bonus | `/display_inputs/bonus_requests/0/employees/E01/policy_rating_rate_percent/value` |
| D04-bonus_requests-0-employees-E01-applied_rating_rate_percent | bonus requests 0 employees E01 applied rating rate percent | `15` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04; annual_performance_bonus | `/display_inputs/bonus_requests/0/employees/E01/applied_rating_rate_percent/value` |
| D04-bonus_requests-0-employees-E03-rating | bonus requests 0 employees E03 rating | `4` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04; PERF-E03-FY2025-26 | `/display_inputs/bonus_requests/0/employees/E03/rating/value` |
| D04-bonus_requests-0-employees-E03-policy_rating_rate_percent | bonus requests 0 employees E03 policy rating rate percent | `10` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04; annual_performance_bonus | `/display_inputs/bonus_requests/0/employees/E03/policy_rating_rate_percent/value` |
| D04-bonus_requests-0-employees-E03-applied_rating_rate_percent | bonus requests 0 employees E03 applied rating rate percent | `10` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04; annual_performance_bonus | `/display_inputs/bonus_requests/0/employees/E03/applied_rating_rate_percent/value` |
| D04-bonus_requests-0-employees-E04-rating | bonus requests 0 employees E04 rating | `4` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04; PERF-E04-FY2025-26 | `/display_inputs/bonus_requests/0/employees/E04/rating/value` |
| D04-bonus_requests-0-employees-E04-policy_rating_rate_percent | bonus requests 0 employees E04 policy rating rate percent | `10` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04; annual_performance_bonus | `/display_inputs/bonus_requests/0/employees/E04/policy_rating_rate_percent/value` |
| D04-bonus_requests-0-employees-E04-applied_rating_rate_percent | bonus requests 0 employees E04 applied rating rate percent | `10` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04; annual_performance_bonus | `/display_inputs/bonus_requests/0/employees/E04/applied_rating_rate_percent/value` |
| D04-bonus_requests-0-employees-E07-rating | bonus requests 0 employees E07 rating | `3` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04; PERF-E07-FY2025-26 | `/display_inputs/bonus_requests/0/employees/E07/rating/value` |
| D04-bonus_requests-0-employees-E07-policy_rating_rate_percent | bonus requests 0 employees E07 policy rating rate percent | `5` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04; annual_performance_bonus | `/display_inputs/bonus_requests/0/employees/E07/policy_rating_rate_percent/value` |
| D04-bonus_requests-0-employees-E07-applied_rating_rate_percent | bonus requests 0 employees E07 applied rating rate percent | `5` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04; annual_performance_bonus | `/display_inputs/bonus_requests/0/employees/E07/applied_rating_rate_percent/value` |
| D04-bonus_requests-0-employees-E08-rating | bonus requests 0 employees E08 rating | `4` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04; PERF-E08-FY2025-26 | `/display_inputs/bonus_requests/0/employees/E08/rating/value` |
| D04-bonus_requests-0-employees-E08-policy_rating_rate_percent | bonus requests 0 employees E08 policy rating rate percent | `10` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04; annual_performance_bonus | `/display_inputs/bonus_requests/0/employees/E08/policy_rating_rate_percent/value` |
| D04-bonus_requests-0-employees-E08-applied_rating_rate_percent | bonus requests 0 employees E08 applied rating rate percent | `null` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04; annual_performance_bonus | `/display_inputs/bonus_requests/0/employees/E08/applied_rating_rate_percent/value` |
| D04-bonus_requests-0-employees-E09-rating | bonus requests 0 employees E09 rating | `null` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04; missing:E09:FY 2025-26 | `/display_inputs/bonus_requests/0/employees/E09/rating/value` |
| D04-bonus_requests-0-employees-E09-policy_rating_rate_percent | bonus requests 0 employees E09 policy rating rate percent | `null` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04; annual_performance_bonus | `/display_inputs/bonus_requests/0/employees/E09/policy_rating_rate_percent/value` |
| D04-bonus_requests-0-employees-E09-applied_rating_rate_percent | bonus requests 0 employees E09 applied rating rate percent | `null` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04; annual_performance_bonus | `/display_inputs/bonus_requests/0/employees/E09/applied_rating_rate_percent/value` |
| D04-bonus_requests-1-employees-E13-target | bonus requests 1 employees E13 target | `1000000` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04; PERF-E13-Q2-2026-27 | `/display_inputs/bonus_requests/1/employees/E13/target/value` |
| D04-bonus_requests-1-employees-E13-achievement | bonus requests 1 employees E13 achievement | `850000` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04; PERF-E13-Q2-2026-27 | `/display_inputs/bonus_requests/1/employees/E13/achievement/value` |
| D04-bonus_requests-1-employees-E14-target | bonus requests 1 employees E14 target | `1000000` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04; PERF-E14-Q2-2026-27 | `/display_inputs/bonus_requests/1/employees/E14/target/value` |
| D04-bonus_requests-1-employees-E14-achievement | bonus requests 1 employees E14 achievement | `1050000` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04; PERF-E14-Q2-2026-27 | `/display_inputs/bonus_requests/1/employees/E14/achievement/value` |
| D04-bonus_requests-1-employees-E15-target | bonus requests 1 employees E15 target | `1000000` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04; PERF-E15-Q2-2026-27 | `/display_inputs/bonus_requests/1/employees/E15/target/value` |
| D04-bonus_requests-1-employees-E15-achievement | bonus requests 1 employees E15 achievement | `1250000` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04; PERF-E15-Q2-2026-27 | `/display_inputs/bonus_requests/1/employees/E15/achievement/value` |
| D05-employees-E09-rating | employees E09 rating | `null` | [scenarios/scenario-05.json](../../data/generated/scenarios/scenario-05.json); scenario-05; missing:E09:FY 2025-26 | `/display_inputs/employees/E09/rating/value` |
| D05-employees-E09-policy_rating_rate_percent | employees E09 policy rating rate percent | `null` | [scenarios/scenario-05.json](../../data/generated/scenarios/scenario-05.json); scenario-05; annual_performance_bonus | `/display_inputs/employees/E09/policy_rating_rate_percent/value` |
| D05-employees-E09-applied_rating_rate_percent | employees E09 applied rating rate percent | `null` | [scenarios/scenario-05.json](../../data/generated/scenarios/scenario-05.json); scenario-05; annual_performance_bonus | `/display_inputs/employees/E09/applied_rating_rate_percent/value` |
| D06-resignation_date | resignation date | `2026-09-01` | [scenarios/scenario-06.json](../../data/generated/scenarios/scenario-06.json); scenario-06; EXIT-E10 | `/display_inputs/resignation_date/value` |
| D06-last_working_day | last working day | `2026-10-31` | [scenarios/scenario-06.json](../../data/generated/scenarios/scenario-06.json); scenario-06; EXIT-E10 | `/display_inputs/last_working_day/value` |
| D06-notice_period_required | notice period required | `60` | [scenarios/scenario-06.json](../../data/generated/scenarios/scenario-06.json); scenario-06; EXIT-E10 | `/display_inputs/notice_period_required/value` |
| D06-notice_period_served | notice period served | `60` | [scenarios/scenario-06.json](../../data/generated/scenarios/scenario-06.json); scenario-06; EXIT-E10 | `/display_inputs/notice_period_served/value` |
| D06-notice_waived | notice waived | `false` | [scenarios/scenario-06.json](../../data/generated/scenarios/scenario-06.json); scenario-06; EXIT-E10 | `/display_inputs/notice_waived/value` |
| D06-encashable_leave_days_used | encashable leave days used | `20` | [scenarios/scenario-06.json](../../data/generated/scenarios/scenario-06.json); scenario-06; LEAVE-E10 | `/display_inputs/encashable_leave_days_used/value` |
| D06-last_drawn_basic | last drawn basic | `50000` | [scenarios/scenario-06.json](../../data/generated/scenarios/scenario-06.json); scenario-06; SS-E10 | `/display_inputs/last_drawn_basic/value` |
| D06-last_drawn_da | last drawn da | `0` | [scenarios/scenario-06.json](../../data/generated/scenarios/scenario-06.json); scenario-06; SS-E10 | `/display_inputs/last_drawn_da/value` |
| D06-last_drawn_basic_plus_da | last drawn basic plus da | `50000` | [scenarios/scenario-06.json](../../data/generated/scenarios/scenario-06.json); scenario-06; scenario-06 | `/display_inputs/last_drawn_basic_plus_da/value` |
| D07-resignation_date | resignation date | `2026-09-01` | [scenarios/scenario-07.json](../../data/generated/scenarios/scenario-07.json); scenario-07; EXIT-E11 | `/display_inputs/resignation_date/value` |
| D07-last_working_day | last working day | `2026-10-31` | [scenarios/scenario-07.json](../../data/generated/scenarios/scenario-07.json); scenario-07; EXIT-E11 | `/display_inputs/last_working_day/value` |
| D07-notice_period_required | notice period required | `60` | [scenarios/scenario-07.json](../../data/generated/scenarios/scenario-07.json); scenario-07; EXIT-E11 | `/display_inputs/notice_period_required/value` |
| D07-notice_period_served | notice period served | `60` | [scenarios/scenario-07.json](../../data/generated/scenarios/scenario-07.json); scenario-07; EXIT-E11 | `/display_inputs/notice_period_served/value` |
| D07-notice_waived | notice waived | `false` | [scenarios/scenario-07.json](../../data/generated/scenarios/scenario-07.json); scenario-07; EXIT-E11 | `/display_inputs/notice_waived/value` |
| D07-encashable_leave_days_used | encashable leave days used | `12` | [scenarios/scenario-07.json](../../data/generated/scenarios/scenario-07.json); scenario-07; LEAVE-E11 | `/display_inputs/encashable_leave_days_used/value` |
| D07-last_drawn_basic | last drawn basic | `40000` | [scenarios/scenario-07.json](../../data/generated/scenarios/scenario-07.json); scenario-07; SS-E11 | `/display_inputs/last_drawn_basic/value` |
| D07-last_drawn_da | last drawn da | `0` | [scenarios/scenario-07.json](../../data/generated/scenarios/scenario-07.json); scenario-07; SS-E11 | `/display_inputs/last_drawn_da/value` |
| D07-last_drawn_basic_plus_da | last drawn basic plus da | `40000` | [scenarios/scenario-07.json](../../data/generated/scenarios/scenario-07.json); scenario-07; scenario-07 | `/display_inputs/last_drawn_basic_plus_da/value` |
| D08-resignation_date | resignation date | `2026-09-22` | [scenarios/scenario-08.json](../../data/generated/scenarios/scenario-08.json); scenario-08; EXIT-E12 | `/display_inputs/resignation_date/value` |
| D08-last_working_day | last working day | `2026-10-31` | [scenarios/scenario-08.json](../../data/generated/scenarios/scenario-08.json); scenario-08; EXIT-E12 | `/display_inputs/last_working_day/value` |
| D08-notice_period_required | notice period required | `60` | [scenarios/scenario-08.json](../../data/generated/scenarios/scenario-08.json); scenario-08; EXIT-E12 | `/display_inputs/notice_period_required/value` |
| D08-notice_period_served | notice period served | `40` | [scenarios/scenario-08.json](../../data/generated/scenarios/scenario-08.json); scenario-08; EXIT-E12 | `/display_inputs/notice_period_served/value` |
| D08-notice_waived | notice waived | `false` | [scenarios/scenario-08.json](../../data/generated/scenarios/scenario-08.json); scenario-08; EXIT-E12 | `/display_inputs/notice_waived/value` |
| D08-encashable_leave_days_used | encashable leave days used | `8` | [scenarios/scenario-08.json](../../data/generated/scenarios/scenario-08.json); scenario-08; LEAVE-E12 | `/display_inputs/encashable_leave_days_used/value` |
| D08-last_drawn_basic | last drawn basic | `35000` | [scenarios/scenario-08.json](../../data/generated/scenarios/scenario-08.json); scenario-08; SS-E12 | `/display_inputs/last_drawn_basic/value` |
| D08-last_drawn_da | last drawn da | `0` | [scenarios/scenario-08.json](../../data/generated/scenarios/scenario-08.json); scenario-08; SS-E12 | `/display_inputs/last_drawn_da/value` |
| D08-last_drawn_basic_plus_da | last drawn basic plus da | `35000` | [scenarios/scenario-08.json](../../data/generated/scenarios/scenario-08.json); scenario-08; scenario-08 | `/display_inputs/last_drawn_basic_plus_da/value` |
| D09-months-2026-08-lop_days | months 2026 08 lop days | `0` | [scenarios/scenario-09.json](../../data/generated/scenarios/scenario-09.json); scenario-09; ATT-E05-2026-08 | `/display_inputs/months/2026-08/lop_days/value` |
| D09-months-2026-08-calendar_days | months 2026 08 calendar days | `31` | [scenarios/scenario-09.json](../../data/generated/scenarios/scenario-09.json); scenario-09; ATT-E05-2026-08 | `/display_inputs/months/2026-08/calendar_days/value` |
| D09-months-2026-09-lop_days | months 2026 09 lop days | `3` | [scenarios/scenario-09.json](../../data/generated/scenarios/scenario-09.json); scenario-09; ATT-E05-2026-09 | `/display_inputs/months/2026-09/lop_days/value` |
| D09-months-2026-09-calendar_days | months 2026 09 calendar days | `30` | [scenarios/scenario-09.json](../../data/generated/scenarios/scenario-09.json); scenario-09; ATT-E05-2026-09 | `/display_inputs/months/2026-09/calendar_days/value` |
| D10-months-2026-08-lop_days | months 2026 08 lop days | `0` | [scenarios/scenario-10.json](../../data/generated/scenarios/scenario-10.json); scenario-10; ATT-E06-2026-08 | `/display_inputs/months/2026-08/lop_days/value` |
| D10-months-2026-08-calendar_days | months 2026 08 calendar days | `31` | [scenarios/scenario-10.json](../../data/generated/scenarios/scenario-10.json); scenario-10; ATT-E06-2026-08 | `/display_inputs/months/2026-08/calendar_days/value` |
| D10-months-2026-09-lop_days | months 2026 09 lop days | `0` | [scenarios/scenario-10.json](../../data/generated/scenarios/scenario-10.json); scenario-10; ATT-E06-2026-09 | `/display_inputs/months/2026-09/lop_days/value` |
| D10-months-2026-09-calendar_days | months 2026 09 calendar days | `30` | [scenarios/scenario-10.json](../../data/generated/scenarios/scenario-10.json); scenario-10; ATT-E06-2026-09 | `/display_inputs/months/2026-09/calendar_days/value` |
| D10-previous_employer_declared_gross | previous employer declared gross | `450000` | [scenarios/scenario-10.json](../../data/generated/scenarios/scenario-10.json); scenario-10; DECL-E06-PREVIOUS-EMPLOYER | `/display_inputs/previous_employer_declared_gross/value` |
| D10-previous_employer_tds | previous employer tds | `15000` | [scenarios/scenario-10.json](../../data/generated/scenarios/scenario-10.json); scenario-10; DECL-E06-PREVIOUS-EMPLOYER | `/display_inputs/previous_employer_tds/value` |
| D10-northwind_tds_already_deducted | northwind tds already deducted | `0` | [scenarios/scenario-10.json](../../data/generated/scenarios/scenario-10.json); scenario-10; scenario-10 | `/display_inputs/northwind_tds_already_deducted/value` |
| D10-remaining_yearly_tax | remaining yearly tax | `87180` | [scenarios/scenario-10.json](../../data/generated/scenarios/scenario-10.json); scenario-10; scenario-10 | `/display_inputs/remaining_yearly_tax/value` |
| D11-months-2026-08-lop_days | months 2026 08 lop days | `0` | [scenarios/scenario-11.json](../../data/generated/scenarios/scenario-11.json); scenario-11; ATT-E16-2026-08 | `/display_inputs/months/2026-08/lop_days/value` |
| D11-months-2026-08-calendar_days | months 2026 08 calendar days | `31` | [scenarios/scenario-11.json](../../data/generated/scenarios/scenario-11.json); scenario-11; ATT-E16-2026-08 | `/display_inputs/months/2026-08/calendar_days/value` |
| D11-months-2026-09-lop_days | months 2026 09 lop days | `0` | [scenarios/scenario-11.json](../../data/generated/scenarios/scenario-11.json); scenario-11; ATT-E16-2026-09 | `/display_inputs/months/2026-09/lop_days/value` |
| D11-months-2026-09-calendar_days | months 2026 09 calendar days | `30` | [scenarios/scenario-11.json](../../data/generated/scenarios/scenario-11.json); scenario-11; ATT-E16-2026-09 | `/display_inputs/months/2026-09/calendar_days/value` |
| D13-resignation_date | resignation date | `2026-09-22` | [scenarios/scenario-13.json](../../data/generated/scenarios/scenario-13.json); scenario-13; EXIT-E12 | `/display_inputs/resignation_date/value` |
| D13-last_working_day | last working day | `2026-10-31` | [scenarios/scenario-13.json](../../data/generated/scenarios/scenario-13.json); scenario-13; EXIT-E12 | `/display_inputs/last_working_day/value` |
| D13-notice_period_required | notice period required | `60` | [scenarios/scenario-13.json](../../data/generated/scenarios/scenario-13.json); scenario-13; EXIT-E12 | `/display_inputs/notice_period_required/value` |
| D13-notice_period_served | notice period served | `40` | [scenarios/scenario-13.json](../../data/generated/scenarios/scenario-13.json); scenario-13; EXIT-E12 | `/display_inputs/notice_period_served/value` |
| D13-notice_waived | notice waived | `false` | [scenarios/scenario-13.json](../../data/generated/scenarios/scenario-13.json); scenario-13; EXIT-E12 | `/display_inputs/notice_waived/value` |
| D13-encashable_leave_days_used | encashable leave days used | `8` | [scenarios/scenario-13.json](../../data/generated/scenarios/scenario-13.json); scenario-13; LEAVE-E12 | `/display_inputs/encashable_leave_days_used/value` |
| D13-last_drawn_basic | last drawn basic | `35000` | [scenarios/scenario-13.json](../../data/generated/scenarios/scenario-13.json); scenario-13; SS-E12 | `/display_inputs/last_drawn_basic/value` |
| D13-last_drawn_da | last drawn da | `0` | [scenarios/scenario-13.json](../../data/generated/scenarios/scenario-13.json); scenario-13; SS-E12 | `/display_inputs/last_drawn_da/value` |
| D13-last_drawn_basic_plus_da | last drawn basic plus da | `35000` | [scenarios/scenario-13.json](../../data/generated/scenarios/scenario-13.json); scenario-13; scenario-13 | `/display_inputs/last_drawn_basic_plus_da/value` |

### aggregates and ranked reasons

| Binding | Field | Exact value | Generated file and record | JSON pointer |
|---|---|---|---|---|
| X-001 | eligible_count | `4` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04 | `/result/bonus_requests/0/aggregates/eligible_count/value` |
| X-002 | not_eligible_count | `1` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04 | `/result/bonus_requests/0/aggregates/not_eligible_count/value` |
| X-003 | needs_input_count | `1` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04 | `/result/bonus_requests/0/aggregates/needs_input_count/value` |
| X-004 | group_total_gross | `213929` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04 | `/result/bonus_requests/0/aggregates/group_total_gross/value` |
| X-005 | group_total_tds | `null` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04 | `/result/bonus_requests/0/aggregates/group_total_tds/value` |
| X-006 | group_total_net | `null` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04 | `/result/bonus_requests/0/aggregates/group_total_net/value` |
| X-007 | eligible_count | `3` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04 | `/result/bonus_requests/1/aggregates/eligible_count/value` |
| X-008 | not_eligible_count | `0` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04 | `/result/bonus_requests/1/aggregates/not_eligible_count/value` |
| X-009 | needs_input_count | `0` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04 | `/result/bonus_requests/1/aggregates/needs_input_count/value` |
| X-010 | group_total_gross | `120000` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04 | `/result/bonus_requests/1/aggregates/group_total_gross/value` |
| X-011 | group_total_tds | `0` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04 | `/result/bonus_requests/1/aggregates/group_total_tds/value` |
| X-012 | group_total_net | `120000` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04 | `/result/bonus_requests/1/aggregates/group_total_net/value` |
| X-013 | recoveries_total | `0` | [scenarios/scenario-06.json](../../data/generated/scenarios/scenario-06.json); scenario-06 | `/result/recoveries_total/value` |
| X-014 | known_recoveries_subtotal | `0` | [scenarios/scenario-06.json](../../data/generated/scenarios/scenario-06.json); scenario-06 | `/result/known_recoveries_subtotal/value` |
| X-015 | recoveries_total | `0` | [scenarios/scenario-07.json](../../data/generated/scenarios/scenario-07.json); scenario-07 | `/result/recoveries_total/value` |
| X-016 | known_recoveries_subtotal | `0` | [scenarios/scenario-07.json](../../data/generated/scenarios/scenario-07.json); scenario-07 | `/result/known_recoveries_subtotal/value` |
| X-017 | recoveries_total | `null` | [scenarios/scenario-08.json](../../data/generated/scenarios/scenario-08.json); scenario-08 | `/result/recoveries_total/value` |
| X-018 | known_recoveries_subtotal | `56667` | [scenarios/scenario-08.json](../../data/generated/scenarios/scenario-08.json); scenario-08 | `/result/known_recoveries_subtotal/value` |
| X-019 | known_recoveries_subtotal flag | `Excludes unresolved asset recovery` | [scenarios/scenario-08.json](../../data/generated/scenarios/scenario-08.json); scenario-08 | `/result/known_recoveries_subtotal/flags/0` |
| X-020 | Ranked reason type | `LOP` | [scenarios/scenario-09.json](../../data/generated/scenarios/scenario-09.json); scenario-09 | `/result/reasons/0/type` |
| X-021 | Ranked take-home effect | `-5000` | [scenarios/scenario-09.json](../../data/generated/scenarios/scenario-09.json); scenario-09 | `/result/reasons/0/effect_amount/value` |
| X-022 | Ranked reason sources | `[{"source_file":"data/mock/employees.json","record_id":"E05"},{"source_file":"data/mock/salary-structures.json","record_id":"SS-E05"},{"source_file":"data/mock/company.json","record_id":"NORTHWIND-DEMO"},{"source_file":"data/mock/attendance.json","record_id":"ATT-E05-2026-09"},{"source_file":"data/mock/attendance.json","record_id":"ATT-E05-2026-08"}]` | [scenarios/scenario-09.json](../../data/generated/scenarios/scenario-09.json); scenario-09 | `/result/reasons/0/source_references` |
| X-023 | Ranked reason type | `PF ceiling change` | [scenarios/scenario-09.json](../../data/generated/scenarios/scenario-09.json); scenario-09 | `/result/reasons/1/type` |
| X-024 | Ranked take-home effect | `-420` | [scenarios/scenario-09.json](../../data/generated/scenarios/scenario-09.json); scenario-09 | `/result/reasons/1/effect_amount/value` |
| X-025 | Ranked reason flag | `PF effect includes earned wage after LOP and dated ceiling segments` | [scenarios/scenario-09.json](../../data/generated/scenarios/scenario-09.json); scenario-09 | `/result/reasons/1/effect_amount/flags/0` |
| X-026 | Ranked reason sources | `[{"source_file":"data/mock/employees.json","record_id":"E05"},{"source_file":"data/mock/salary-structures.json","record_id":"SS-E05"},{"source_file":"data/mock/company.json","record_id":"NORTHWIND-DEMO"},{"source_file":"data/mock/attendance.json","record_id":"ATT-E05-2026-09"},{"source_file":"data/mock/attendance.json","record_id":"ATT-E05-2026-08"}]` | [scenarios/scenario-09.json](../../data/generated/scenarios/scenario-09.json); scenario-09 | `/result/reasons/1/source_references` |
| X-027 | Ranked reason type | `TDS change` | [scenarios/scenario-10.json](../../data/generated/scenarios/scenario-10.json); scenario-10 | `/result/reasons/0/type` |
| X-028 | Ranked take-home effect | `-12454` | [scenarios/scenario-10.json](../../data/generated/scenarios/scenario-10.json); scenario-10 | `/result/reasons/0/effect_amount/value` |
| X-029 | Ranked reason sources | `[{"source_file":"data/mock/employees.json","record_id":"E06"},{"source_file":"data/mock/salary-structures.json","record_id":"SS-E06"},{"source_file":"data/mock/company.json","record_id":"NORTHWIND-DEMO"},{"source_file":"data/mock/declarations.json","record_id":"DECL-E06-PREVIOUS-EMPLOYER"}]` | [scenarios/scenario-10.json](../../data/generated/scenarios/scenario-10.json); scenario-10 | `/result/reasons/0/source_references` |
| X-030 | Ranked reason type | `PF ceiling change` | [scenarios/scenario-10.json](../../data/generated/scenarios/scenario-10.json); scenario-10 | `/result/reasons/1/type` |
| X-031 | Ranked take-home effect | `-560` | [scenarios/scenario-10.json](../../data/generated/scenarios/scenario-10.json); scenario-10 | `/result/reasons/1/effect_amount/value` |
| X-032 | Ranked reason flag | `PF effect includes earned wage after LOP and dated ceiling segments` | [scenarios/scenario-10.json](../../data/generated/scenarios/scenario-10.json); scenario-10 | `/result/reasons/1/effect_amount/flags/0` |
| X-033 | Ranked reason sources | `[{"source_file":"data/mock/employees.json","record_id":"E06"},{"source_file":"data/mock/salary-structures.json","record_id":"SS-E06"},{"source_file":"data/mock/company.json","record_id":"NORTHWIND-DEMO"},{"source_file":"data/mock/attendance.json","record_id":"ATT-E06-2026-09"},{"source_file":"data/mock/attendance.json","record_id":"ATT-E06-2026-08"}]` | [scenarios/scenario-10.json](../../data/generated/scenarios/scenario-10.json); scenario-10 | `/result/reasons/1/source_references` |
| X-034 | rules_version | `Northwind demo rules v1` | [scenarios/scenario-10.json](../../data/generated/scenarios/scenario-10.json); scenario-10 | `/result/after/tds/amount/rule_ids/9/rules_version` |
| X-035 | verified_on | `2026-10-13` | [scenarios/scenario-10.json](../../data/generated/scenarios/scenario-10.json); scenario-10 | `/result/after/tds/amount/rule_ids/9/verified_on` |
| X-036 | date_note | `Applies to all demo periods` | [scenarios/scenario-10.json](../../data/generated/scenarios/scenario-10.json); scenario-10 | `/result/after/tds/amount/rule_ids/9/date_note` |
| X-037 | Ranked reason type | `PF ceiling change` | [scenarios/scenario-11.json](../../data/generated/scenarios/scenario-11.json); scenario-11 | `/result/reasons/0/type` |
| X-038 | Ranked take-home effect | `-420` | [scenarios/scenario-11.json](../../data/generated/scenarios/scenario-11.json); scenario-11 | `/result/reasons/0/effect_amount/value` |
| X-039 | Ranked reason flag | `PF effect includes earned wage after LOP and dated ceiling segments` | [scenarios/scenario-11.json](../../data/generated/scenarios/scenario-11.json); scenario-11 | `/result/reasons/0/effect_amount/flags/0` |
| X-040 | Ranked reason sources | `[{"source_file":"data/mock/employees.json","record_id":"E16"},{"source_file":"data/mock/salary-structures.json","record_id":"SS-E16"},{"source_file":"data/mock/company.json","record_id":"NORTHWIND-DEMO"},{"source_file":"data/mock/attendance.json","record_id":"ATT-E16-2026-09"},{"source_file":"data/mock/attendance.json","record_id":"ATT-E16-2026-08"}]` | [scenarios/scenario-11.json](../../data/generated/scenarios/scenario-11.json); scenario-11 | `/result/reasons/0/source_references` |
| X-041 | recoveries_total | `null` | [scenarios/scenario-13.json](../../data/generated/scenarios/scenario-13.json); scenario-13 | `/result/recoveries_total/value` |
| X-042 | known_recoveries_subtotal | `56667` | [scenarios/scenario-13.json](../../data/generated/scenarios/scenario-13.json); scenario-13 | `/result/known_recoveries_subtotal/value` |
| X-043 | known_recoveries_subtotal flag | `Excludes unresolved asset recovery` | [scenarios/scenario-13.json](../../data/generated/scenarios/scenario-13.json); scenario-13 | `/result/known_recoveries_subtotal/flags/0` |

### rules metadata

| Binding | Field | Exact value | Generated file and record | JSON pointer |
|---|---|---|---|---|
| RV-1-rules_version | settlement-rules.json rules_version | `Northwind demo rules v1` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; settlement-rules.json#final_month_days | `/result/months/0/paid_days/rule_ids/0/rules_version` |
| RV-1-verified_on | settlement-rules.json verified_on | `2026-10-13` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; settlement-rules.json#final_month_days | `/result/months/0/paid_days/rule_ids/0/verified_on` |
| RV-1-date_note | settlement-rules.json date_note | `Applies to all demo periods` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; settlement-rules.json#final_month_days | `/result/months/0/paid_days/rule_ids/0/date_note` |
| RV-2-rules_version | company-settings.json rules_version | `Northwind demo rules v1` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; company-settings.json#rounding | `/result/months/0/old/lines/basic/rule_ids/1/rules_version` |
| RV-2-verified_on | company-settings.json verified_on | `2026-10-13` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; company-settings.json#rounding | `/result/months/0/old/lines/basic/rule_ids/1/verified_on` |
| RV-2-date_note | company-settings.json date_note | `Applies to all demo periods` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; company-settings.json#rounding | `/result/months/0/old/lines/basic/rule_ids/1/date_note` |
| RV-3-rules_version | pf-rules.json rules_version | `Northwind demo rules v1` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; pf-rules.json#pf_wage_formula | `/result/months/0/old_pf/employee/rule_ids/0/rules_version` |
| RV-3-verified_on | pf-rules.json verified_on | `2026-10-13` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; pf-rules.json#pf_wage_formula | `/result/months/0/old_pf/employee/rule_ids/0/verified_on` |
| RV-3-date_note | pf-rules.json date_note | `Applies to all demo periods` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; pf-rules.json#pf_wage_formula | `/result/months/0/old_pf/employee/rule_ids/0/date_note` |
| RV-4-rules_version | tax-rules.json rules_version | `Northwind demo rules v1` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; tax-rules.json#regime_scope | `/result/months/0/tds_impact/rule_ids/0/rules_version` |
| RV-4-verified_on | tax-rules.json verified_on | `2026-10-13` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; tax-rules.json#regime_scope | `/result/months/0/tds_impact/rule_ids/0/verified_on` |
| RV-4-date_note | tax-rules.json date_note | `Applies to all demo periods` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01; tax-rules.json#regime_scope | `/result/months/0/tds_impact/rule_ids/0/date_note` |
| RV-5-rules_version | bonus-rules.json rules_version | `Northwind demo rules v1` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04; bonus-rules.json#annual_performance_bonus | `/result/bonus_requests/0/employees/0/annual_basic/rule_ids/0/rules_version` |
| RV-5-verified_on | bonus-rules.json verified_on | `2026-10-13` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04; bonus-rules.json#annual_performance_bonus | `/result/bonus_requests/0/employees/0/annual_basic/rule_ids/0/verified_on` |
| RV-5-date_note | bonus-rules.json date_note | `Applies to all demo periods` | [scenarios/scenario-04.json](../../data/generated/scenarios/scenario-04.json); scenario-04; bonus-rules.json#annual_performance_bonus | `/result/bonus_requests/0/employees/0/annual_basic/rule_ids/0/date_note` |
| RV-6-rules_version | gratuity-rules.json rules_version | `Northwind demo rules v1` | [scenarios/scenario-06.json](../../data/generated/scenarios/scenario-06.json); scenario-06; gratuity-rules.json#formula | `/result/components/gratuity/amount/rule_ids/0/rules_version` |
| RV-6-verified_on | gratuity-rules.json verified_on | `2026-10-13` | [scenarios/scenario-06.json](../../data/generated/scenarios/scenario-06.json); scenario-06; gratuity-rules.json#formula | `/result/components/gratuity/amount/rule_ids/0/verified_on` |
| RV-6-date_note | gratuity-rules.json date_note | `Applies to all demo periods` | [scenarios/scenario-06.json](../../data/generated/scenarios/scenario-06.json); scenario-06; gratuity-rules.json#formula | `/result/components/gratuity/amount/rule_ids/0/date_note` |
| RD-wage_ceiling_before_change_inr-effective_from | pf-rules.json#wage_ceiling_before_change_inr effective_from | `null` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01 | `/result/months/0/old_pf/employee/rule_ids/8/effective_from` |
| RD-wage_ceiling_before_change_inr-effective_to | pf-rules.json#wage_ceiling_before_change_inr effective_to | `2026-09-16` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01 | `/result/months/0/old_pf/employee/rule_ids/8/effective_to` |
| RD-wage_ceiling_from_change_inr-effective_from | pf-rules.json#wage_ceiling_from_change_inr effective_from | `2026-09-17` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01 | `/result/months/5/old_pf/employee/rule_ids/10/effective_from` |
| RD-wage_ceiling_from_change_inr-effective_to | pf-rules.json#wage_ceiling_from_change_inr effective_to | `null` | [scenarios/scenario-01.json](../../data/generated/scenarios/scenario-01.json); scenario-01 | `/result/months/5/old_pf/employee/rule_ids/10/effective_to` |

## 9. Still unavailable

These are the only remaining unavailable fixture data. Every relevant number renders **Not available in generated data**; intentional Not applicable dates and an ineligible employee's Not applied rate are not missing data.

| Scope | Still unavailable and reason |
|---|---|
| Scenario 3; missing attendance | July LOP and calendar days, affected earnings and aggregate hike gross, TDS and net remain null or incomplete. The new D03 export preserves missing attendance instead of filling it. |
| Scenario 4 and 5; bonus | E09 performance rating, policy/applied rate and award remain unknown. E03 bonus TDS/net remain unknown because prior payroll is incomplete, so Annual group TDS/net also remain null. |
| Custom selected bonus scope | Request-level counts and aggregates now exist. Arbitrary selected-scope counts, gross, TDS and net are not exported. Do not calculate or relabel a request aggregate; require the matching engine result before approving that scope. |
| Scenario 10; approved C29 month slot | The accepted previous-employer declaration's declared month range is absent from display_inputs. Keep the slot visibly unavailable. Never substitute comparison months or derive a range from a record ID. |
| E12; unresolved asset | Asset recovery, recoveries total and final net remain unresolved. Keep known recoveries subtotal and Excludes unresolved asset recovery visible. Do not replace the missing values with zero or the subtotal. |
