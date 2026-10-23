# HCM One: Figma AI Prompts

Updated for G07. Code prototype first; Figma is optional later for visual polish and case study images. figma-ai-prompts.md is kept as a bonus. Each section is one self-contained prompt for an MVP screen. Paste only the chosen section into the AI design tool. These prompts create design frames, not new calculations, approvals, sent queries or payments. No Figma file has been created in this run.

Sources: [screen inventory](screen-inventory.md), [screen specifications](screen-specs.md) and [visual specification](visual-spec.md); approved [flows](../05-architecture/user-flows.md), [AI interaction](../06-ai-interaction/) and [UX principles](../04-strategy/ux-principles.md). Every numeric fixture below is a direct generated binding. Names and the non-numeric query description match the allowed mock records. The UI must not print designer reference keys, file paths or JSON pointers as part of an AI sentence.

Bonus and settlement are later modes specified in screen-specs. They do not receive extra MVP prompts or new screens here. Missing values must remain visible; do not fill them to make the mockup look finished.

## SCR-01 — Prepare a proposal

Design HCM One's HR desktop request screen at 1440 px wide. It captures and confirms a back-dated hike before calculation, following F1-01–F1-05. It applies UXP-01, UXP-02, UXP-04 and UXP-07. Use a 12-column grid with 64 px margins and 24 px gutters; keep request reading width at most 720 px.

Use a white background, deep teal #0F766E as the only brand accent, dark text #0F172A, supporting text #475569 and surface #F8FAFC. Use Inter for all text and numbers. Apply tabular figures with font-feature-settings: "tnum" to amounts, dates and tables. Use a monospace font only for query IDs and record references. Reason: "Tabular figures align numbers in columns and feel calmer for payroll; monospace is kept for technical IDs." Use semantic status icons with full text, never color alone. Use generous white space, an 8 px card radius, 6 px controls and at least 44 px touch targets. Desktop title is 24 px and number hero is 40 px; mobile title is 24 px and number hero is 32 px. These are authoring tokens, not payroll facts.

Copy each displayed payroll number, period, date and record ID literally from the source table below. INR is a separate amount label. Do not round, abbreviate, total, count or infer a value. Do not use a raw mock number. Keep source file, record and JSON pointer as designer annotations; provide authorized Show calculation and View source in the product. The proof view copies the selected generated object's formula, inputs, rule_ids, effective dates, certainty and flags without evaluating it. Missing numeric operands stay Not available in generated data. Do not expose a complete dataset or another employee's record.

Use the exact AI sentences below. Braces are the approved named slots; fill only from an authorized actual record. Headings and labels are interface content, not new AI causal sentences. No confidence percentages. Keep certainty, workflow status and payment separate. Do not add charts, invented counts, timestamps, version numbers, bank actions or extra screens. Label controls, use semantic headings, give keyboard focus a visible outline and design for screen reader order. A drawer or sheet stays within its parent screen and returns focus when closed.

From top to bottom: HCM One and HR Admin; title Prepare a proposal; type Back-dated hike; label Your payroll request; editable request Prepare Priya Sharma's pending back-dated hike.; employee Priya Sharma; assistant introduction; clarification only when a required input is missing; confirmation panel; separate existing-calculation card.

Priya Sharma is the allowed mock name for the employee ID in data/generated/scenarios/scenario-01.json, record scenario-01 /result/employee_id, value E01. Keep that source annotation with the name and ID. Do not invent another person.

Assistant introduction:

> I am HCM One's AI payroll assistant. I explain payroll records and payroll calculation results. I can help prepare a proposal or a query for you to review. I cannot approve a change, apply it or pay it. I send a query only after you confirm.

Copy source: output/06-ai-interaction/trust-explainability.md, Section 6.

Only in the missing-effective-date variant, use this clarifying question:

> From which date should this proposed hike take effect?

Copy source: output/06-ai-interaction/conversation-design.md, Section 4.

Confirmation fields are Employee, Requested hike, Effective date, Old salary and Proposed salary. They are now filled from scenario-01 display_inputs in the table below. Label percentage as percent and amounts as INR. Expand contractual components from their own bindings; do not use earned period amounts as salary inputs. The existing first-period calculation remains a separate card.

| Visible field | Literal value | File, record and JSON pointer |
|---|---|---|
| Period (HM-0-period) | 2026-04 | data/generated/scenarios/scenario-01.json; scenario-01; REV-E01; 2026-04; /result/months/0/month |
| Old earned amount (HM-0-old) | 120000 | data/generated/scenarios/scenario-01.json; scenario-01; REV-E01; 2026-04; /result/months/0/old/gross/value |
| Revised earned amount (HM-0-new) | 132000 | data/generated/scenarios/scenario-01.json; scenario-01; REV-E01; 2026-04; /result/months/0/revised/gross/value |

Actions are Edit request, Confirm request and Review existing calculation. Confirm request is available for the complete sourced request, but requires the HR user's actual confirmation. In the code prototype, that action creates the demo version and scope record; it does not approve or apply payroll. Editing clears confirmation. Show a success state only after recording the actual action. The design frame itself records nothing.

Show Draft, clarification and conditional confirmation variants. No invented successful request or approval. Use the shared failure variants below; permission denial removes the name, ID, calculation and sources. Later bonus and settlement modes are not new MVP frames.

Design these alternate states as variants of the same screen. Keep the default fixture independent of them. Loading has no completed amount. Missing data keeps the affected field unavailable. Rule not verified stops only the affected calculation. Calculation error does not manufacture a total. Permission denial removes private context, numbers, source links and any target existence cue. Do not activate an alternate lifecycle state without an actual stored event.

Loading:

> I am waiting for the payroll records needed for this request. The result is not ready.

Copy source: output/06-ai-interaction/approval-failure-handling.md, Section 6, Loading.

Missing data:

> The required {record type} for {period or component} is missing. I cannot explain a complete result for this scope.

Copy source: output/06-ai-interaction/approval-failure-handling.md, Section 6, Missing data.

Rule not verified:

> The applicable rule basis for {affected scope} is not verified. That part cannot be calculated.

Copy source: output/06-ai-interaction/approval-failure-handling.md, Section 6, Rule not verified.

Calculation error, only when a payroll check actually fails:

> The payroll calculation did not produce a usable result for {affected scope}. I cannot give a complete amount for it.

Copy source: output/06-ai-interaction/approval-failure-handling.md, Section 6, Calculation error.

Permission denied:

> I cannot provide that information. I can help with payroll records you are authorized to access.

Copy source: output/06-ai-interaction/approval-failure-handling.md, Section 6, Permission denied.

---


### Filled request and attendance bindings

| Visible field and binding | Literal value | File, record and JSON pointer |
|---|---|---|
| requested hike percentage (D01-requested_hike_percentage) | 10 | data/generated/scenarios/scenario-01.json; scenario-01; REV-E01; /display_inputs/requested_hike_percentage/value |
| effective date (D01-effective_date) | 2026-04-01 | data/generated/scenarios/scenario-01.json; scenario-01; REV-E01; /display_inputs/effective_date/value |
| old monthly salary components basic (D01-old_monthly_salary-components-basic) | 60000 | data/generated/scenarios/scenario-01.json; scenario-01; SS-E01; /display_inputs/old_monthly_salary/components/basic/value |
| old monthly salary components da (D01-old_monthly_salary-components-da) | 0 | data/generated/scenarios/scenario-01.json; scenario-01; SS-E01; /display_inputs/old_monthly_salary/components/da/value |
| old monthly salary components hra (D01-old_monthly_salary-components-hra) | 30000 | data/generated/scenarios/scenario-01.json; scenario-01; SS-E01; /display_inputs/old_monthly_salary/components/hra/value |
| old monthly salary components special allowance (D01-old_monthly_salary-components-special_allowance) | 30000 | data/generated/scenarios/scenario-01.json; scenario-01; SS-E01; /display_inputs/old_monthly_salary/components/special_allowance/value |
| old monthly salary total (D01-old_monthly_salary-total) | 120000 | data/generated/scenarios/scenario-01.json; scenario-01; scenario-01; /display_inputs/old_monthly_salary/total/value |
| proposed monthly salary components basic (D01-proposed_monthly_salary-components-basic) | 66000 | data/generated/scenarios/scenario-01.json; scenario-01; scenario-01; /display_inputs/proposed_monthly_salary/components/basic/value |
| proposed monthly salary components da (D01-proposed_monthly_salary-components-da) | 0 | data/generated/scenarios/scenario-01.json; scenario-01; scenario-01; /display_inputs/proposed_monthly_salary/components/da/value |
| proposed monthly salary components hra (D01-proposed_monthly_salary-components-hra) | 33000 | data/generated/scenarios/scenario-01.json; scenario-01; scenario-01; /display_inputs/proposed_monthly_salary/components/hra/value |
| proposed monthly salary components special allowance (D01-proposed_monthly_salary-components-special_allowance) | 33000 | data/generated/scenarios/scenario-01.json; scenario-01; scenario-01; /display_inputs/proposed_monthly_salary/components/special_allowance/value |
| proposed monthly salary total (D01-proposed_monthly_salary-total) | 132000 | data/generated/scenarios/scenario-01.json; scenario-01; scenario-01; /display_inputs/proposed_monthly_salary/total/value |
| months 2026 04 lop days (D01-months-2026-04-lop_days) | 0 | data/generated/scenarios/scenario-01.json; scenario-01; ATT-E01-2026-04; /display_inputs/months/2026-04/lop_days/value |
| months 2026 04 calendar days (D01-months-2026-04-calendar_days) | 30 | data/generated/scenarios/scenario-01.json; scenario-01; ATT-E01-2026-04; /display_inputs/months/2026-04/calendar_days/value |
| months 2026 05 lop days (D01-months-2026-05-lop_days) | 0 | data/generated/scenarios/scenario-01.json; scenario-01; ATT-E01-2026-05; /display_inputs/months/2026-05/lop_days/value |
| months 2026 05 calendar days (D01-months-2026-05-calendar_days) | 31 | data/generated/scenarios/scenario-01.json; scenario-01; ATT-E01-2026-05; /display_inputs/months/2026-05/calendar_days/value |
| months 2026 06 lop days (D01-months-2026-06-lop_days) | 2 | data/generated/scenarios/scenario-01.json; scenario-01; ATT-E01-2026-06; /display_inputs/months/2026-06/lop_days/value |
| months 2026 06 calendar days (D01-months-2026-06-calendar_days) | 30 | data/generated/scenarios/scenario-01.json; scenario-01; ATT-E01-2026-06; /display_inputs/months/2026-06/calendar_days/value |
| months 2026 07 lop days (D01-months-2026-07-lop_days) | 0 | data/generated/scenarios/scenario-01.json; scenario-01; ATT-E01-2026-07; /display_inputs/months/2026-07/lop_days/value |
| months 2026 07 calendar days (D01-months-2026-07-calendar_days) | 31 | data/generated/scenarios/scenario-01.json; scenario-01; ATT-E01-2026-07; /display_inputs/months/2026-07/calendar_days/value |
| months 2026 08 lop days (D01-months-2026-08-lop_days) | 0 | data/generated/scenarios/scenario-01.json; scenario-01; ATT-E01-2026-08; /display_inputs/months/2026-08/lop_days/value |
| months 2026 08 calendar days (D01-months-2026-08-calendar_days) | 31 | data/generated/scenarios/scenario-01.json; scenario-01; ATT-E01-2026-08; /display_inputs/months/2026-08/calendar_days/value |
| months 2026 09 lop days (D01-months-2026-09-lop_days) | 0 | data/generated/scenarios/scenario-01.json; scenario-01; ATT-E01-2026-09; /display_inputs/months/2026-09/lop_days/value |
| months 2026 09 calendar days (D01-months-2026-09-calendar_days) | 30 | data/generated/scenarios/scenario-01.json; scenario-01; ATT-E01-2026-09; /display_inputs/months/2026-09/calendar_days/value |
## SCR-02 — Review a proposal

Design HCM One's HR desktop proposal review at 1440 px wide. It follows F1-06–F1-12 and applies UXP-01, UXP-02, UXP-04, UXP-05 and UXP-07. Use a 12-column grid with 64 px margins and 24 px gutters. A 480 px proof drawer is a state of this same screen.

Use a white background, deep teal #0F766E as the only brand accent, dark text #0F172A, supporting text #475569 and surface #F8FAFC. Use Inter for all text and numbers. Apply tabular figures with font-feature-settings: "tnum" to amounts, dates and tables. Use a monospace font only for query IDs and record references. Reason: "Tabular figures align numbers in columns and feel calmer for payroll; monospace is kept for technical IDs." Use semantic status icons with full text, never color alone. Use generous white space, an 8 px card radius, 6 px controls and at least 44 px touch targets. Desktop title is 24 px and number hero is 40 px; mobile title is 24 px and number hero is 32 px. These are authoring tokens, not payroll facts.

Copy each displayed payroll number, period, date and record ID literally from the source table below. INR is a separate amount label. Do not round, abbreviate, total, count or infer a value. Do not use a raw mock number. Keep source file, record and JSON pointer as designer annotations; provide authorized Show calculation and View source in the product. The proof view copies the selected generated object's formula, inputs, rule_ids, effective dates, certainty and flags without evaluating it. Missing numeric operands stay Not available in generated data. Do not expose a complete dataset or another employee's record.

Use the exact AI sentences below. Braces are the approved named slots; fill only from an authorized actual record. Headings and labels are interface content, not new AI causal sentences. No confidence percentages. Keep certainty, workflow status and payment separate. Do not add charts, invented counts, timestamps, version numbers, bank actions or extra screens. Label controls, use semantic headings, give keyboard focus a visible outline and design for screen reader order. A drawer or sheet stays within its parent screen and returns focus when closed.

From top to bottom: authorized employee and scope; title Back-dated hike proposal; recorded proposal status; certainty; approved scope sentence; expected net arrears hero; gross, PF and TDS cards; full estimate flag; monthly table; Show calculation; edit panel; approval bar.

Use Priya Sharma for generated employee E01, data/generated/scenarios/scenario-01.json, scenario-01 /result/employee_id. Show Needs HR approval; not applied from /result/proposal_status and Complete for this scope from /result/certainty. These labels do not authorize approval.

Assistant message:

> This is a proposal for the recorded affected months.

Copy source: output/06-ai-interaction/conversation-design.md, Section 8, Example A.

Use these card and tax-detail values. Keep the estimate flag fully visible. The stored estimate month is not a promised payment date.

| Visible field | Literal value | File, record and JSON pointer |
|---|---|---|
| Expected net arrears (H-net_arrears) | 67476 | data/generated/scenarios/scenario-01.json; scenario-01; REV-E01; /result/totals/net_arrears/value |
| Gross arrears (H-gross_arrears) | 71200 | data/generated/scenarios/scenario-01.json; scenario-01; REV-E01; /result/totals/gross_arrears/value |
| Employee PF change (H-pf) | 0 | data/generated/scenarios/scenario-01.json; scenario-01; REV-E01; /result/totals/pf_change/employee/value |
| Estimated TDS impact (H-tds_impact) | 3724 | data/generated/scenarios/scenario-01.json; scenario-01; REV-E01; /result/totals/tds_impact/value |
| Estimated payment month (H-month) | 2026-10 | data/generated/scenarios/scenario-01.json; scenario-01; REV-E01; /result/estimated_payment_month |
| Estimate flag (H-flag) | Estimated TDS if approved and paid in October 2026 payroll | data/generated/scenarios/scenario-01.json; scenario-01; REV-E01; /result/flags/0 |
| Recurring salary TDS impact (H-recurring_salary_tds_impact) | 1872 | data/generated/scenarios/scenario-01.json; scenario-01; REV-E01; /result/totals/recurring_salary_tds_impact/value |
| Arrears-only TDS impact (H-arrears_only_tds_impact) | 1852 | data/generated/scenarios/scenario-01.json; scenario-01; REV-E01; /result/totals/arrears_only_tds_impact/value |

Use the following source values for the monthly table. Group each period's entries into one row with Period, Old earned amount, Revised earned amount, Arrears, Employee PF change, Incremental estimated arrears TDS and Show calculation. The monthly tax value is the incremental arrears-only effect, not the full receipt-month estimate.

| Visible field | Literal value | File, record and JSON pointer |
|---|---|---|
| Period (HM-0-period) | 2026-04 | data/generated/scenarios/scenario-01.json; scenario-01; REV-E01; 2026-04; /result/months/0/month |
| Old earned amount (HM-0-old) | 120000 | data/generated/scenarios/scenario-01.json; scenario-01; REV-E01; 2026-04; /result/months/0/old/gross/value |
| Revised earned amount (HM-0-new) | 132000 | data/generated/scenarios/scenario-01.json; scenario-01; REV-E01; 2026-04; /result/months/0/revised/gross/value |
| Arrears (HM-0-diff) | 12000 | data/generated/scenarios/scenario-01.json; scenario-01; REV-E01; 2026-04; /result/months/0/difference/value |
| Employee PF change (HM-0-pf) | 0 | data/generated/scenarios/scenario-01.json; scenario-01; REV-E01; 2026-04; /result/months/0/pf_change/employee/value |
| Incremental estimated arrears TDS (HM-0-tds) | 312 | data/generated/scenarios/scenario-01.json; scenario-01; REV-E01; 2026-04; /result/months/0/tds_impact/value |
| Period (HM-1-period) | 2026-05 | data/generated/scenarios/scenario-01.json; scenario-01; REV-E01; 2026-05; /result/months/1/month |
| Old earned amount (HM-1-old) | 120000 | data/generated/scenarios/scenario-01.json; scenario-01; REV-E01; 2026-05; /result/months/1/old/gross/value |
| Revised earned amount (HM-1-new) | 132000 | data/generated/scenarios/scenario-01.json; scenario-01; REV-E01; 2026-05; /result/months/1/revised/gross/value |
| Arrears (HM-1-diff) | 12000 | data/generated/scenarios/scenario-01.json; scenario-01; REV-E01; 2026-05; /result/months/1/difference/value |
| Employee PF change (HM-1-pf) | 0 | data/generated/scenarios/scenario-01.json; scenario-01; REV-E01; 2026-05; /result/months/1/pf_change/employee/value |
| Incremental estimated arrears TDS (HM-1-tds) | 312 | data/generated/scenarios/scenario-01.json; scenario-01; REV-E01; 2026-05; /result/months/1/tds_impact/value |
| Period (HM-2-period) | 2026-06 | data/generated/scenarios/scenario-01.json; scenario-01; REV-E01; 2026-06; /result/months/2/month |
| Old earned amount (HM-2-old) | 112000 | data/generated/scenarios/scenario-01.json; scenario-01; REV-E01; 2026-06; /result/months/2/old/gross/value |
| Revised earned amount (HM-2-new) | 123200 | data/generated/scenarios/scenario-01.json; scenario-01; REV-E01; 2026-06; /result/months/2/revised/gross/value |
| Arrears (HM-2-diff) | 11200 | data/generated/scenarios/scenario-01.json; scenario-01; REV-E01; 2026-06; /result/months/2/difference/value |
| Employee PF change (HM-2-pf) | 0 | data/generated/scenarios/scenario-01.json; scenario-01; REV-E01; 2026-06; /result/months/2/pf_change/employee/value |
| Incremental estimated arrears TDS (HM-2-tds) | 292 | data/generated/scenarios/scenario-01.json; scenario-01; REV-E01; 2026-06; /result/months/2/tds_impact/value |
| Period (HM-3-period) | 2026-07 | data/generated/scenarios/scenario-01.json; scenario-01; REV-E01; 2026-07; /result/months/3/month |
| Old earned amount (HM-3-old) | 120000 | data/generated/scenarios/scenario-01.json; scenario-01; REV-E01; 2026-07; /result/months/3/old/gross/value |
| Revised earned amount (HM-3-new) | 132000 | data/generated/scenarios/scenario-01.json; scenario-01; REV-E01; 2026-07; /result/months/3/revised/gross/value |
| Arrears (HM-3-diff) | 12000 | data/generated/scenarios/scenario-01.json; scenario-01; REV-E01; 2026-07; /result/months/3/difference/value |
| Employee PF change (HM-3-pf) | 0 | data/generated/scenarios/scenario-01.json; scenario-01; REV-E01; 2026-07; /result/months/3/pf_change/employee/value |
| Incremental estimated arrears TDS (HM-3-tds) | 312 | data/generated/scenarios/scenario-01.json; scenario-01; REV-E01; 2026-07; /result/months/3/tds_impact/value |
| Period (HM-4-period) | 2026-08 | data/generated/scenarios/scenario-01.json; scenario-01; REV-E01; 2026-08; /result/months/4/month |
| Old earned amount (HM-4-old) | 120000 | data/generated/scenarios/scenario-01.json; scenario-01; REV-E01; 2026-08; /result/months/4/old/gross/value |
| Revised earned amount (HM-4-new) | 132000 | data/generated/scenarios/scenario-01.json; scenario-01; REV-E01; 2026-08; /result/months/4/revised/gross/value |
| Arrears (HM-4-diff) | 12000 | data/generated/scenarios/scenario-01.json; scenario-01; REV-E01; 2026-08; /result/months/4/difference/value |
| Employee PF change (HM-4-pf) | 0 | data/generated/scenarios/scenario-01.json; scenario-01; REV-E01; 2026-08; /result/months/4/pf_change/employee/value |
| Incremental estimated arrears TDS (HM-4-tds) | 312 | data/generated/scenarios/scenario-01.json; scenario-01; REV-E01; 2026-08; /result/months/4/tds_impact/value |
| Period (HM-5-period) | 2026-09 | data/generated/scenarios/scenario-01.json; scenario-01; REV-E01; 2026-09; /result/months/5/month |
| Old earned amount (HM-5-old) | 120000 | data/generated/scenarios/scenario-01.json; scenario-01; REV-E01; 2026-09; /result/months/5/old/gross/value |
| Revised earned amount (HM-5-new) | 132000 | data/generated/scenarios/scenario-01.json; scenario-01; REV-E01; 2026-09; /result/months/5/revised/gross/value |
| Arrears (HM-5-diff) | 12000 | data/generated/scenarios/scenario-01.json; scenario-01; REV-E01; 2026-09; /result/months/5/difference/value |
| Employee PF change (HM-5-pf) | 0 | data/generated/scenarios/scenario-01.json; scenario-01; REV-E01; 2026-09; /result/months/5/pf_change/employee/value |
| Incremental estimated arrears TDS (HM-5-tds) | 312 | data/generated/scenarios/scenario-01.json; scenario-01; REV-E01; 2026-09; /result/months/5/tds_impact/value |

The proof drawer uses the selected amount object, its stored formula, inputs, rule IDs, dated rule basis, certainty and flags. Do not invent numerical formula substitutions. Employer contributions remain separate from employee deductions.

The approval bar has Approve selected scope, Edit with a reason and Reject. PQ-08 is resolved by design: Created by the code prototype at runtime as demo lifecycle records (version, actor, time, query ID, HR reply) when the user acts. Never pre-filled. Require a current version, matching source result, complete selected scope and authorization. Record the action before showing success. Never pre-fill version, actor or time. Include this consequence sentence:

> Approving records this version and the selected scope as ready for payroll. It does not apply the change or make a payment.

Copy source: output/06-ai-interaction/approval-failure-handling.md, Section 2.

The edit panel has Line to edit, Proposed amount and Reason. Do not fill a new edited value. Use:

> Your edit will create a revised proposal. HCM One will recheck the affected amounts and totals. You will need to review the new version before approving it.

Copy source: output/06-ai-interaction/approval-failure-handling.md, Section 3.

For stale submission use:

> This proposal changed after you reviewed it. Review the current version before approving.

Copy source: output/06-ai-interaction/approval-failure-handling.md, Section 6, Changed version.

Design alternate hike fixtures inside this same screen: Arjun Rao, E02 from scenario-02 /result/employee_id, uses the dated PF segment drawer; Kavya Iyer, E03 from scenario-03 /result/employee_id, has Incomplete and Needs input for the missing month. Their available values are below. Null totals must remain unavailable, never zero. Do not approve incomplete scope.

| Visible field | Literal value | File, record and JSON pointer |
|---|---|---|
| gross_arrears (H2-gross_arrears) | 7200 | data/generated/scenarios/scenario-02.json; scenario-02; REV-E02; /result/totals/gross_arrears/value |
| tds_impact (H2-tds_impact) | 0 | data/generated/scenarios/scenario-02.json; scenario-02; REV-E02; /result/totals/tds_impact/value |
| net_arrears (H2-net_arrears) | 7099 | data/generated/scenarios/scenario-02.json; scenario-02; REV-E02; /result/totals/net_arrears/value |
| Original September employee PF (H2-old) | 1968 | data/generated/scenarios/scenario-02.json; scenario-02; REV-E02; 2026-09; /result/months/1/old_pf/employee/value |
| Revised September employee PF (H2-new) | 2069 | data/generated/scenarios/scenario-02.json; scenario-02; REV-E02; 2026-09; /result/months/1/revised_pf/employee/value |
| September employee PF change (H2-diff) | 101 | data/generated/scenarios/scenario-02.json; scenario-02; REV-E02; 2026-09; /result/months/1/pf_change/employee/value |
| Changed PF segment begins (H2-date) | 2026-09-17 | data/generated/scenarios/scenario-02.json; scenario-02; REV-E02; 2026-09; /result/months/1/old_pf/segments/1/start/value |
| PF segment calendar days (H2-segment-0-days) | 16 | data/generated/scenarios/scenario-02.json; scenario-02; REV-E02; /result/months/1/old_pf/segments/0/days/value |
| PF segment calendar days (H2-segment-1-days) | 14 | data/generated/scenarios/scenario-02.json; scenario-02; REV-E02; /result/months/1/old_pf/segments/1/days/value |
| Missing period (H3-july) | 2026-07 | data/generated/scenarios/scenario-03.json; scenario-03; REV-E03; /result/months/0/month |
| gross_arrears (H3-gross_arrears) | Not available in generated data | data/generated/scenarios/scenario-03.json; scenario-03; REV-E03; /result/totals/gross_arrears/value |
| tds_impact (H3-tds_impact) | Not available in generated data | data/generated/scenarios/scenario-03.json; scenario-03; REV-E03; /result/totals/tds_impact/value |
| net_arrears (H3-net_arrears) | Not available in generated data | data/generated/scenarios/scenario-03.json; scenario-03; REV-E03; /result/totals/net_arrears/value |
| Known August arrears (H3-aug-diff) | 4800 | data/generated/scenarios/scenario-03.json; scenario-03; REV-E03; /result/months/1/difference/value |
| Known September arrears (H3-sep-diff) | 4800 | data/generated/scenarios/scenario-03.json; scenario-03; REV-E03; /result/months/2/difference/value |

Ready for review, Revised, Rejected and Approved and ready for payroll are conditional stored lifecycle variants, not the default generated status. Later bonus and settlement reuse this screen and its guarded scope; do not add new MVP frames or call any state Paid.

Design these alternate states as variants of the same screen. Keep the default fixture independent of them. Loading has no completed amount. Missing data keeps the affected field unavailable. Rule not verified stops only the affected calculation. Calculation error does not manufacture a total. Permission denial removes private context, numbers, source links and any target existence cue. Do not activate an alternate lifecycle state without an actual stored event.

Loading:

> I am waiting for the payroll records needed for this request. The result is not ready.

Copy source: output/06-ai-interaction/approval-failure-handling.md, Section 6, Loading.

Missing data:

> The required {record type} for {period or component} is missing. I cannot explain a complete result for this scope.

Copy source: output/06-ai-interaction/approval-failure-handling.md, Section 6, Missing data.

Rule not verified:

> The applicable rule basis for {affected scope} is not verified. That part cannot be calculated.

Copy source: output/06-ai-interaction/approval-failure-handling.md, Section 6, Rule not verified.

Calculation error, only when a payroll check actually fails:

> The payroll calculation did not produce a usable result for {affected scope}. I cannot give a complete amount for it.

Copy source: output/06-ai-interaction/approval-failure-handling.md, Section 6, Calculation error.

Permission denied:

> I cannot provide that information. I can help with payroll records you are authorized to access.

Copy source: output/06-ai-interaction/approval-failure-handling.md, Section 6, Permission denied.

---


### Filled hike request, attendance and rule metadata

| Visible field and binding | Literal value | File, record and JSON pointer |
|---|---|---|
| requested hike percentage (D01-requested_hike_percentage) | 10 | data/generated/scenarios/scenario-01.json; scenario-01; REV-E01; /display_inputs/requested_hike_percentage/value |
| effective date (D01-effective_date) | 2026-04-01 | data/generated/scenarios/scenario-01.json; scenario-01; REV-E01; /display_inputs/effective_date/value |
| old monthly salary components basic (D01-old_monthly_salary-components-basic) | 60000 | data/generated/scenarios/scenario-01.json; scenario-01; SS-E01; /display_inputs/old_monthly_salary/components/basic/value |
| old monthly salary components da (D01-old_monthly_salary-components-da) | 0 | data/generated/scenarios/scenario-01.json; scenario-01; SS-E01; /display_inputs/old_monthly_salary/components/da/value |
| old monthly salary components hra (D01-old_monthly_salary-components-hra) | 30000 | data/generated/scenarios/scenario-01.json; scenario-01; SS-E01; /display_inputs/old_monthly_salary/components/hra/value |
| old monthly salary components special allowance (D01-old_monthly_salary-components-special_allowance) | 30000 | data/generated/scenarios/scenario-01.json; scenario-01; SS-E01; /display_inputs/old_monthly_salary/components/special_allowance/value |
| old monthly salary total (D01-old_monthly_salary-total) | 120000 | data/generated/scenarios/scenario-01.json; scenario-01; scenario-01; /display_inputs/old_monthly_salary/total/value |
| proposed monthly salary components basic (D01-proposed_monthly_salary-components-basic) | 66000 | data/generated/scenarios/scenario-01.json; scenario-01; scenario-01; /display_inputs/proposed_monthly_salary/components/basic/value |
| proposed monthly salary components da (D01-proposed_monthly_salary-components-da) | 0 | data/generated/scenarios/scenario-01.json; scenario-01; scenario-01; /display_inputs/proposed_monthly_salary/components/da/value |
| proposed monthly salary components hra (D01-proposed_monthly_salary-components-hra) | 33000 | data/generated/scenarios/scenario-01.json; scenario-01; scenario-01; /display_inputs/proposed_monthly_salary/components/hra/value |
| proposed monthly salary components special allowance (D01-proposed_monthly_salary-components-special_allowance) | 33000 | data/generated/scenarios/scenario-01.json; scenario-01; scenario-01; /display_inputs/proposed_monthly_salary/components/special_allowance/value |
| proposed monthly salary total (D01-proposed_monthly_salary-total) | 132000 | data/generated/scenarios/scenario-01.json; scenario-01; scenario-01; /display_inputs/proposed_monthly_salary/total/value |
| months 2026 04 lop days (D01-months-2026-04-lop_days) | 0 | data/generated/scenarios/scenario-01.json; scenario-01; ATT-E01-2026-04; /display_inputs/months/2026-04/lop_days/value |
| months 2026 04 calendar days (D01-months-2026-04-calendar_days) | 30 | data/generated/scenarios/scenario-01.json; scenario-01; ATT-E01-2026-04; /display_inputs/months/2026-04/calendar_days/value |
| months 2026 05 lop days (D01-months-2026-05-lop_days) | 0 | data/generated/scenarios/scenario-01.json; scenario-01; ATT-E01-2026-05; /display_inputs/months/2026-05/lop_days/value |
| months 2026 05 calendar days (D01-months-2026-05-calendar_days) | 31 | data/generated/scenarios/scenario-01.json; scenario-01; ATT-E01-2026-05; /display_inputs/months/2026-05/calendar_days/value |
| months 2026 06 lop days (D01-months-2026-06-lop_days) | 2 | data/generated/scenarios/scenario-01.json; scenario-01; ATT-E01-2026-06; /display_inputs/months/2026-06/lop_days/value |
| months 2026 06 calendar days (D01-months-2026-06-calendar_days) | 30 | data/generated/scenarios/scenario-01.json; scenario-01; ATT-E01-2026-06; /display_inputs/months/2026-06/calendar_days/value |
| months 2026 07 lop days (D01-months-2026-07-lop_days) | 0 | data/generated/scenarios/scenario-01.json; scenario-01; ATT-E01-2026-07; /display_inputs/months/2026-07/lop_days/value |
| months 2026 07 calendar days (D01-months-2026-07-calendar_days) | 31 | data/generated/scenarios/scenario-01.json; scenario-01; ATT-E01-2026-07; /display_inputs/months/2026-07/calendar_days/value |
| months 2026 08 lop days (D01-months-2026-08-lop_days) | 0 | data/generated/scenarios/scenario-01.json; scenario-01; ATT-E01-2026-08; /display_inputs/months/2026-08/lop_days/value |
| months 2026 08 calendar days (D01-months-2026-08-calendar_days) | 31 | data/generated/scenarios/scenario-01.json; scenario-01; ATT-E01-2026-08; /display_inputs/months/2026-08/calendar_days/value |
| months 2026 09 lop days (D01-months-2026-09-lop_days) | 0 | data/generated/scenarios/scenario-01.json; scenario-01; ATT-E01-2026-09; /display_inputs/months/2026-09/lop_days/value |
| months 2026 09 calendar days (D01-months-2026-09-calendar_days) | 30 | data/generated/scenarios/scenario-01.json; scenario-01; ATT-E01-2026-09; /display_inputs/months/2026-09/calendar_days/value |
| requested hike percentage (D02-requested_hike_percentage) | 10 | data/generated/scenarios/scenario-02.json; scenario-02; REV-E02; /display_inputs/requested_hike_percentage/value |
| effective date (D02-effective_date) | 2026-08-01 | data/generated/scenarios/scenario-02.json; scenario-02; REV-E02; /display_inputs/effective_date/value |
| old monthly salary components basic (D02-old_monthly_salary-components-basic) | 18000 | data/generated/scenarios/scenario-02.json; scenario-02; SS-E02; /display_inputs/old_monthly_salary/components/basic/value |
| old monthly salary components da (D02-old_monthly_salary-components-da) | 0 | data/generated/scenarios/scenario-02.json; scenario-02; SS-E02; /display_inputs/old_monthly_salary/components/da/value |
| old monthly salary components hra (D02-old_monthly_salary-components-hra) | 9000 | data/generated/scenarios/scenario-02.json; scenario-02; SS-E02; /display_inputs/old_monthly_salary/components/hra/value |
| old monthly salary components special allowance (D02-old_monthly_salary-components-special_allowance) | 9000 | data/generated/scenarios/scenario-02.json; scenario-02; SS-E02; /display_inputs/old_monthly_salary/components/special_allowance/value |
| old monthly salary total (D02-old_monthly_salary-total) | 36000 | data/generated/scenarios/scenario-02.json; scenario-02; scenario-02; /display_inputs/old_monthly_salary/total/value |
| proposed monthly salary components basic (D02-proposed_monthly_salary-components-basic) | 19800 | data/generated/scenarios/scenario-02.json; scenario-02; scenario-02; /display_inputs/proposed_monthly_salary/components/basic/value |
| proposed monthly salary components da (D02-proposed_monthly_salary-components-da) | 0 | data/generated/scenarios/scenario-02.json; scenario-02; scenario-02; /display_inputs/proposed_monthly_salary/components/da/value |
| proposed monthly salary components hra (D02-proposed_monthly_salary-components-hra) | 9900 | data/generated/scenarios/scenario-02.json; scenario-02; scenario-02; /display_inputs/proposed_monthly_salary/components/hra/value |
| proposed monthly salary components special allowance (D02-proposed_monthly_salary-components-special_allowance) | 9900 | data/generated/scenarios/scenario-02.json; scenario-02; scenario-02; /display_inputs/proposed_monthly_salary/components/special_allowance/value |
| proposed monthly salary total (D02-proposed_monthly_salary-total) | 39600 | data/generated/scenarios/scenario-02.json; scenario-02; scenario-02; /display_inputs/proposed_monthly_salary/total/value |
| months 2026 08 lop days (D02-months-2026-08-lop_days) | 0 | data/generated/scenarios/scenario-02.json; scenario-02; ATT-E02-2026-08; /display_inputs/months/2026-08/lop_days/value |
| months 2026 08 calendar days (D02-months-2026-08-calendar_days) | 31 | data/generated/scenarios/scenario-02.json; scenario-02; ATT-E02-2026-08; /display_inputs/months/2026-08/calendar_days/value |
| months 2026 09 lop days (D02-months-2026-09-lop_days) | 0 | data/generated/scenarios/scenario-02.json; scenario-02; ATT-E02-2026-09; /display_inputs/months/2026-09/lop_days/value |
| months 2026 09 calendar days (D02-months-2026-09-calendar_days) | 30 | data/generated/scenarios/scenario-02.json; scenario-02; ATT-E02-2026-09; /display_inputs/months/2026-09/calendar_days/value |
| requested hike percentage (D03-requested_hike_percentage) | 8 | data/generated/scenarios/scenario-03.json; scenario-03; REV-E03; /display_inputs/requested_hike_percentage/value |
| effective date (D03-effective_date) | 2026-07-01 | data/generated/scenarios/scenario-03.json; scenario-03; REV-E03; /display_inputs/effective_date/value |
| old monthly salary components basic (D03-old_monthly_salary-components-basic) | 30000 | data/generated/scenarios/scenario-03.json; scenario-03; SS-E03; /display_inputs/old_monthly_salary/components/basic/value |
| old monthly salary components da (D03-old_monthly_salary-components-da) | 0 | data/generated/scenarios/scenario-03.json; scenario-03; SS-E03; /display_inputs/old_monthly_salary/components/da/value |
| old monthly salary components hra (D03-old_monthly_salary-components-hra) | 15000 | data/generated/scenarios/scenario-03.json; scenario-03; SS-E03; /display_inputs/old_monthly_salary/components/hra/value |
| old monthly salary components special allowance (D03-old_monthly_salary-components-special_allowance) | 15000 | data/generated/scenarios/scenario-03.json; scenario-03; SS-E03; /display_inputs/old_monthly_salary/components/special_allowance/value |
| old monthly salary total (D03-old_monthly_salary-total) | 60000 | data/generated/scenarios/scenario-03.json; scenario-03; scenario-03; /display_inputs/old_monthly_salary/total/value |
| proposed monthly salary components basic (D03-proposed_monthly_salary-components-basic) | 32400 | data/generated/scenarios/scenario-03.json; scenario-03; scenario-03; /display_inputs/proposed_monthly_salary/components/basic/value |
| proposed monthly salary components da (D03-proposed_monthly_salary-components-da) | 0 | data/generated/scenarios/scenario-03.json; scenario-03; scenario-03; /display_inputs/proposed_monthly_salary/components/da/value |
| proposed monthly salary components hra (D03-proposed_monthly_salary-components-hra) | 16200 | data/generated/scenarios/scenario-03.json; scenario-03; scenario-03; /display_inputs/proposed_monthly_salary/components/hra/value |
| proposed monthly salary components special allowance (D03-proposed_monthly_salary-components-special_allowance) | 16200 | data/generated/scenarios/scenario-03.json; scenario-03; scenario-03; /display_inputs/proposed_monthly_salary/components/special_allowance/value |
| proposed monthly salary total (D03-proposed_monthly_salary-total) | 64800 | data/generated/scenarios/scenario-03.json; scenario-03; scenario-03; /display_inputs/proposed_monthly_salary/total/value |
| months 2026 07 lop days (D03-months-2026-07-lop_days) | Not available in generated data | data/generated/scenarios/scenario-03.json; scenario-03; missing:E03:2026-07; /display_inputs/months/2026-07/lop_days/value |
| months 2026 07 calendar days (D03-months-2026-07-calendar_days) | Not available in generated data | data/generated/scenarios/scenario-03.json; scenario-03; missing:E03:2026-07; /display_inputs/months/2026-07/calendar_days/value |
| months 2026 08 lop days (D03-months-2026-08-lop_days) | 0 | data/generated/scenarios/scenario-03.json; scenario-03; ATT-E03-2026-08; /display_inputs/months/2026-08/lop_days/value |
| months 2026 08 calendar days (D03-months-2026-08-calendar_days) | 31 | data/generated/scenarios/scenario-03.json; scenario-03; ATT-E03-2026-08; /display_inputs/months/2026-08/calendar_days/value |
| months 2026 09 lop days (D03-months-2026-09-lop_days) | 0 | data/generated/scenarios/scenario-03.json; scenario-03; ATT-E03-2026-09; /display_inputs/months/2026-09/lop_days/value |
| months 2026 09 calendar days (D03-months-2026-09-calendar_days) | 30 | data/generated/scenarios/scenario-03.json; scenario-03; ATT-E03-2026-09; /display_inputs/months/2026-09/calendar_days/value |
| settlement-rules.json rules_version (RV-1-rules_version) | Northwind demo rules v1 | data/generated/scenarios/scenario-01.json; scenario-01; settlement-rules.json#final_month_days; /result/months/0/paid_days/rule_ids/0/rules_version |
| settlement-rules.json verified_on (RV-1-verified_on) | 2026-10-13 | data/generated/scenarios/scenario-01.json; scenario-01; settlement-rules.json#final_month_days; /result/months/0/paid_days/rule_ids/0/verified_on |
| settlement-rules.json date_note (RV-1-date_note) | Applies to all demo periods | data/generated/scenarios/scenario-01.json; scenario-01; settlement-rules.json#final_month_days; /result/months/0/paid_days/rule_ids/0/date_note |
| company-settings.json rules_version (RV-2-rules_version) | Northwind demo rules v1 | data/generated/scenarios/scenario-01.json; scenario-01; company-settings.json#rounding; /result/months/0/old/lines/basic/rule_ids/1/rules_version |
| company-settings.json verified_on (RV-2-verified_on) | 2026-10-13 | data/generated/scenarios/scenario-01.json; scenario-01; company-settings.json#rounding; /result/months/0/old/lines/basic/rule_ids/1/verified_on |
| company-settings.json date_note (RV-2-date_note) | Applies to all demo periods | data/generated/scenarios/scenario-01.json; scenario-01; company-settings.json#rounding; /result/months/0/old/lines/basic/rule_ids/1/date_note |
| pf-rules.json rules_version (RV-3-rules_version) | Northwind demo rules v1 | data/generated/scenarios/scenario-01.json; scenario-01; pf-rules.json#pf_wage_formula; /result/months/0/old_pf/employee/rule_ids/0/rules_version |
| pf-rules.json verified_on (RV-3-verified_on) | 2026-10-13 | data/generated/scenarios/scenario-01.json; scenario-01; pf-rules.json#pf_wage_formula; /result/months/0/old_pf/employee/rule_ids/0/verified_on |
| pf-rules.json date_note (RV-3-date_note) | Applies to all demo periods | data/generated/scenarios/scenario-01.json; scenario-01; pf-rules.json#pf_wage_formula; /result/months/0/old_pf/employee/rule_ids/0/date_note |
| tax-rules.json rules_version (RV-4-rules_version) | Northwind demo rules v1 | data/generated/scenarios/scenario-01.json; scenario-01; tax-rules.json#regime_scope; /result/months/0/tds_impact/rule_ids/0/rules_version |
| tax-rules.json verified_on (RV-4-verified_on) | 2026-10-13 | data/generated/scenarios/scenario-01.json; scenario-01; tax-rules.json#regime_scope; /result/months/0/tds_impact/rule_ids/0/verified_on |
| tax-rules.json date_note (RV-4-date_note) | Applies to all demo periods | data/generated/scenarios/scenario-01.json; scenario-01; tax-rules.json#regime_scope; /result/months/0/tds_impact/rule_ids/0/date_note |
| bonus-rules.json rules_version (RV-5-rules_version) | Northwind demo rules v1 | data/generated/scenarios/scenario-04.json; scenario-04; bonus-rules.json#annual_performance_bonus; /result/bonus_requests/0/employees/0/annual_basic/rule_ids/0/rules_version |
| bonus-rules.json verified_on (RV-5-verified_on) | 2026-10-13 | data/generated/scenarios/scenario-04.json; scenario-04; bonus-rules.json#annual_performance_bonus; /result/bonus_requests/0/employees/0/annual_basic/rule_ids/0/verified_on |
| bonus-rules.json date_note (RV-5-date_note) | Applies to all demo periods | data/generated/scenarios/scenario-04.json; scenario-04; bonus-rules.json#annual_performance_bonus; /result/bonus_requests/0/employees/0/annual_basic/rule_ids/0/date_note |
| gratuity-rules.json rules_version (RV-6-rules_version) | Northwind demo rules v1 | data/generated/scenarios/scenario-06.json; scenario-06; gratuity-rules.json#formula; /result/components/gratuity/amount/rule_ids/0/rules_version |
| gratuity-rules.json verified_on (RV-6-verified_on) | 2026-10-13 | data/generated/scenarios/scenario-06.json; scenario-06; gratuity-rules.json#formula; /result/components/gratuity/amount/rule_ids/0/verified_on |
| gratuity-rules.json date_note (RV-6-date_note) | Applies to all demo periods | data/generated/scenarios/scenario-06.json; scenario-06; gratuity-rules.json#formula; /result/components/gratuity/amount/rule_ids/0/date_note |
| pf-rules.json#wage_ceiling_before_change_inr effective_from (RD-wage_ceiling_before_change_inr-effective_from) | Not available in generated data | data/generated/scenarios/scenario-01.json; scenario-01; /result/months/0/old_pf/employee/rule_ids/8/effective_from |
| pf-rules.json#wage_ceiling_before_change_inr effective_to (RD-wage_ceiling_before_change_inr-effective_to) | 2026-09-16 | data/generated/scenarios/scenario-01.json; scenario-01; /result/months/0/old_pf/employee/rule_ids/8/effective_to |
| pf-rules.json#wage_ceiling_from_change_inr effective_from (RD-wage_ceiling_from_change_inr-effective_from) | 2026-09-17 | data/generated/scenarios/scenario-01.json; scenario-01; /result/months/5/old_pf/employee/rule_ids/10/effective_from |
| pf-rules.json#wage_ceiling_from_change_inr effective_to (RD-wage_ceiling_from_change_inr-effective_to) | Not available in generated data | data/generated/scenarios/scenario-01.json; scenario-01; /result/months/5/old_pf/employee/rule_ids/10/effective_to |

### Later-mode bonus and settlement values within the same screen

These are later modes, not additional MVP screens. Fill exit inputs, performance operands, counts, full-request aggregates and recovery proof from these exact bindings. Keep E03 bonus TDS/net and Annual group TDS/net null; E09 rating and award missing. For E08 show the policy rate and recorded Not applied status, never an applied award. E12 asset, recoveries total and final net remain unresolved. Show the known subtotal with Excludes unresolved asset recovery. Arbitrary selected-scope counts and totals are not exported; approval of a custom selection requires a matching engine result. For undated rules show Applies to all demo periods; never use verified_on as an effective date.

| Visible field and binding | Literal value | File, record and JSON pointer |
|---|---|---|
| bonus requests 0 employees E01 rating (D04-bonus_requests-0-employees-E01-rating) | 5 | data/generated/scenarios/scenario-04.json; scenario-04; PERF-E01-FY2025-26; /display_inputs/bonus_requests/0/employees/E01/rating/value |
| bonus requests 0 employees E01 policy rating rate percent (D04-bonus_requests-0-employees-E01-policy_rating_rate_percent) | 15 | data/generated/scenarios/scenario-04.json; scenario-04; annual_performance_bonus; /display_inputs/bonus_requests/0/employees/E01/policy_rating_rate_percent/value |
| bonus requests 0 employees E01 applied rating rate percent (D04-bonus_requests-0-employees-E01-applied_rating_rate_percent) | 15 | data/generated/scenarios/scenario-04.json; scenario-04; annual_performance_bonus; /display_inputs/bonus_requests/0/employees/E01/applied_rating_rate_percent/value |
| bonus requests 0 employees E03 rating (D04-bonus_requests-0-employees-E03-rating) | 4 | data/generated/scenarios/scenario-04.json; scenario-04; PERF-E03-FY2025-26; /display_inputs/bonus_requests/0/employees/E03/rating/value |
| bonus requests 0 employees E03 policy rating rate percent (D04-bonus_requests-0-employees-E03-policy_rating_rate_percent) | 10 | data/generated/scenarios/scenario-04.json; scenario-04; annual_performance_bonus; /display_inputs/bonus_requests/0/employees/E03/policy_rating_rate_percent/value |
| bonus requests 0 employees E03 applied rating rate percent (D04-bonus_requests-0-employees-E03-applied_rating_rate_percent) | 10 | data/generated/scenarios/scenario-04.json; scenario-04; annual_performance_bonus; /display_inputs/bonus_requests/0/employees/E03/applied_rating_rate_percent/value |
| bonus requests 0 employees E04 rating (D04-bonus_requests-0-employees-E04-rating) | 4 | data/generated/scenarios/scenario-04.json; scenario-04; PERF-E04-FY2025-26; /display_inputs/bonus_requests/0/employees/E04/rating/value |
| bonus requests 0 employees E04 policy rating rate percent (D04-bonus_requests-0-employees-E04-policy_rating_rate_percent) | 10 | data/generated/scenarios/scenario-04.json; scenario-04; annual_performance_bonus; /display_inputs/bonus_requests/0/employees/E04/policy_rating_rate_percent/value |
| bonus requests 0 employees E04 applied rating rate percent (D04-bonus_requests-0-employees-E04-applied_rating_rate_percent) | 10 | data/generated/scenarios/scenario-04.json; scenario-04; annual_performance_bonus; /display_inputs/bonus_requests/0/employees/E04/applied_rating_rate_percent/value |
| bonus requests 0 employees E07 rating (D04-bonus_requests-0-employees-E07-rating) | 3 | data/generated/scenarios/scenario-04.json; scenario-04; PERF-E07-FY2025-26; /display_inputs/bonus_requests/0/employees/E07/rating/value |
| bonus requests 0 employees E07 policy rating rate percent (D04-bonus_requests-0-employees-E07-policy_rating_rate_percent) | 5 | data/generated/scenarios/scenario-04.json; scenario-04; annual_performance_bonus; /display_inputs/bonus_requests/0/employees/E07/policy_rating_rate_percent/value |
| bonus requests 0 employees E07 applied rating rate percent (D04-bonus_requests-0-employees-E07-applied_rating_rate_percent) | 5 | data/generated/scenarios/scenario-04.json; scenario-04; annual_performance_bonus; /display_inputs/bonus_requests/0/employees/E07/applied_rating_rate_percent/value |
| bonus requests 0 employees E08 rating (D04-bonus_requests-0-employees-E08-rating) | 4 | data/generated/scenarios/scenario-04.json; scenario-04; PERF-E08-FY2025-26; /display_inputs/bonus_requests/0/employees/E08/rating/value |
| bonus requests 0 employees E08 policy rating rate percent (D04-bonus_requests-0-employees-E08-policy_rating_rate_percent) | 10 | data/generated/scenarios/scenario-04.json; scenario-04; annual_performance_bonus; /display_inputs/bonus_requests/0/employees/E08/policy_rating_rate_percent/value |
| bonus requests 0 employees E08 applied rating rate percent (D04-bonus_requests-0-employees-E08-applied_rating_rate_percent) | Not available in generated data | data/generated/scenarios/scenario-04.json; scenario-04; annual_performance_bonus; /display_inputs/bonus_requests/0/employees/E08/applied_rating_rate_percent/value |
| bonus requests 0 employees E09 rating (D04-bonus_requests-0-employees-E09-rating) | Not available in generated data | data/generated/scenarios/scenario-04.json; scenario-04; missing:E09:FY 2025-26; /display_inputs/bonus_requests/0/employees/E09/rating/value |
| bonus requests 0 employees E09 policy rating rate percent (D04-bonus_requests-0-employees-E09-policy_rating_rate_percent) | Not available in generated data | data/generated/scenarios/scenario-04.json; scenario-04; annual_performance_bonus; /display_inputs/bonus_requests/0/employees/E09/policy_rating_rate_percent/value |
| bonus requests 0 employees E09 applied rating rate percent (D04-bonus_requests-0-employees-E09-applied_rating_rate_percent) | Not available in generated data | data/generated/scenarios/scenario-04.json; scenario-04; annual_performance_bonus; /display_inputs/bonus_requests/0/employees/E09/applied_rating_rate_percent/value |
| bonus requests 1 employees E13 target (D04-bonus_requests-1-employees-E13-target) | 1000000 | data/generated/scenarios/scenario-04.json; scenario-04; PERF-E13-Q2-2026-27; /display_inputs/bonus_requests/1/employees/E13/target/value |
| bonus requests 1 employees E13 achievement (D04-bonus_requests-1-employees-E13-achievement) | 850000 | data/generated/scenarios/scenario-04.json; scenario-04; PERF-E13-Q2-2026-27; /display_inputs/bonus_requests/1/employees/E13/achievement/value |
| bonus requests 1 employees E14 target (D04-bonus_requests-1-employees-E14-target) | 1000000 | data/generated/scenarios/scenario-04.json; scenario-04; PERF-E14-Q2-2026-27; /display_inputs/bonus_requests/1/employees/E14/target/value |
| bonus requests 1 employees E14 achievement (D04-bonus_requests-1-employees-E14-achievement) | 1050000 | data/generated/scenarios/scenario-04.json; scenario-04; PERF-E14-Q2-2026-27; /display_inputs/bonus_requests/1/employees/E14/achievement/value |
| bonus requests 1 employees E15 target (D04-bonus_requests-1-employees-E15-target) | 1000000 | data/generated/scenarios/scenario-04.json; scenario-04; PERF-E15-Q2-2026-27; /display_inputs/bonus_requests/1/employees/E15/target/value |
| bonus requests 1 employees E15 achievement (D04-bonus_requests-1-employees-E15-achievement) | 1250000 | data/generated/scenarios/scenario-04.json; scenario-04; PERF-E15-Q2-2026-27; /display_inputs/bonus_requests/1/employees/E15/achievement/value |
| employees E09 rating (D05-employees-E09-rating) | Not available in generated data | data/generated/scenarios/scenario-05.json; scenario-05; missing:E09:FY 2025-26; /display_inputs/employees/E09/rating/value |
| employees E09 policy rating rate percent (D05-employees-E09-policy_rating_rate_percent) | Not available in generated data | data/generated/scenarios/scenario-05.json; scenario-05; annual_performance_bonus; /display_inputs/employees/E09/policy_rating_rate_percent/value |
| employees E09 applied rating rate percent (D05-employees-E09-applied_rating_rate_percent) | Not available in generated data | data/generated/scenarios/scenario-05.json; scenario-05; annual_performance_bonus; /display_inputs/employees/E09/applied_rating_rate_percent/value |
| resignation date (D06-resignation_date) | 2026-09-01 | data/generated/scenarios/scenario-06.json; scenario-06; EXIT-E10; /display_inputs/resignation_date/value |
| last working day (D06-last_working_day) | 2026-10-31 | data/generated/scenarios/scenario-06.json; scenario-06; EXIT-E10; /display_inputs/last_working_day/value |
| notice period required (D06-notice_period_required) | 60 | data/generated/scenarios/scenario-06.json; scenario-06; EXIT-E10; /display_inputs/notice_period_required/value |
| notice period served (D06-notice_period_served) | 60 | data/generated/scenarios/scenario-06.json; scenario-06; EXIT-E10; /display_inputs/notice_period_served/value |
| notice waived (D06-notice_waived) | false | data/generated/scenarios/scenario-06.json; scenario-06; EXIT-E10; /display_inputs/notice_waived/value |
| encashable leave days used (D06-encashable_leave_days_used) | 20 | data/generated/scenarios/scenario-06.json; scenario-06; LEAVE-E10; /display_inputs/encashable_leave_days_used/value |
| last drawn basic (D06-last_drawn_basic) | 50000 | data/generated/scenarios/scenario-06.json; scenario-06; SS-E10; /display_inputs/last_drawn_basic/value |
| last drawn da (D06-last_drawn_da) | 0 | data/generated/scenarios/scenario-06.json; scenario-06; SS-E10; /display_inputs/last_drawn_da/value |
| last drawn basic plus da (D06-last_drawn_basic_plus_da) | 50000 | data/generated/scenarios/scenario-06.json; scenario-06; scenario-06; /display_inputs/last_drawn_basic_plus_da/value |
| resignation date (D07-resignation_date) | 2026-09-01 | data/generated/scenarios/scenario-07.json; scenario-07; EXIT-E11; /display_inputs/resignation_date/value |
| last working day (D07-last_working_day) | 2026-10-31 | data/generated/scenarios/scenario-07.json; scenario-07; EXIT-E11; /display_inputs/last_working_day/value |
| notice period required (D07-notice_period_required) | 60 | data/generated/scenarios/scenario-07.json; scenario-07; EXIT-E11; /display_inputs/notice_period_required/value |
| notice period served (D07-notice_period_served) | 60 | data/generated/scenarios/scenario-07.json; scenario-07; EXIT-E11; /display_inputs/notice_period_served/value |
| notice waived (D07-notice_waived) | false | data/generated/scenarios/scenario-07.json; scenario-07; EXIT-E11; /display_inputs/notice_waived/value |
| encashable leave days used (D07-encashable_leave_days_used) | 12 | data/generated/scenarios/scenario-07.json; scenario-07; LEAVE-E11; /display_inputs/encashable_leave_days_used/value |
| last drawn basic (D07-last_drawn_basic) | 40000 | data/generated/scenarios/scenario-07.json; scenario-07; SS-E11; /display_inputs/last_drawn_basic/value |
| last drawn da (D07-last_drawn_da) | 0 | data/generated/scenarios/scenario-07.json; scenario-07; SS-E11; /display_inputs/last_drawn_da/value |
| last drawn basic plus da (D07-last_drawn_basic_plus_da) | 40000 | data/generated/scenarios/scenario-07.json; scenario-07; scenario-07; /display_inputs/last_drawn_basic_plus_da/value |
| resignation date (D08-resignation_date) | 2026-09-22 | data/generated/scenarios/scenario-08.json; scenario-08; EXIT-E12; /display_inputs/resignation_date/value |
| last working day (D08-last_working_day) | 2026-10-31 | data/generated/scenarios/scenario-08.json; scenario-08; EXIT-E12; /display_inputs/last_working_day/value |
| notice period required (D08-notice_period_required) | 60 | data/generated/scenarios/scenario-08.json; scenario-08; EXIT-E12; /display_inputs/notice_period_required/value |
| notice period served (D08-notice_period_served) | 40 | data/generated/scenarios/scenario-08.json; scenario-08; EXIT-E12; /display_inputs/notice_period_served/value |
| notice waived (D08-notice_waived) | false | data/generated/scenarios/scenario-08.json; scenario-08; EXIT-E12; /display_inputs/notice_waived/value |
| encashable leave days used (D08-encashable_leave_days_used) | 8 | data/generated/scenarios/scenario-08.json; scenario-08; LEAVE-E12; /display_inputs/encashable_leave_days_used/value |
| last drawn basic (D08-last_drawn_basic) | 35000 | data/generated/scenarios/scenario-08.json; scenario-08; SS-E12; /display_inputs/last_drawn_basic/value |
| last drawn da (D08-last_drawn_da) | 0 | data/generated/scenarios/scenario-08.json; scenario-08; SS-E12; /display_inputs/last_drawn_da/value |
| last drawn basic plus da (D08-last_drawn_basic_plus_da) | 35000 | data/generated/scenarios/scenario-08.json; scenario-08; scenario-08; /display_inputs/last_drawn_basic_plus_da/value |
| resignation date (D13-resignation_date) | 2026-09-22 | data/generated/scenarios/scenario-13.json; scenario-13; EXIT-E12; /display_inputs/resignation_date/value |
| last working day (D13-last_working_day) | 2026-10-31 | data/generated/scenarios/scenario-13.json; scenario-13; EXIT-E12; /display_inputs/last_working_day/value |
| notice period required (D13-notice_period_required) | 60 | data/generated/scenarios/scenario-13.json; scenario-13; EXIT-E12; /display_inputs/notice_period_required/value |
| notice period served (D13-notice_period_served) | 40 | data/generated/scenarios/scenario-13.json; scenario-13; EXIT-E12; /display_inputs/notice_period_served/value |
| notice waived (D13-notice_waived) | false | data/generated/scenarios/scenario-13.json; scenario-13; EXIT-E12; /display_inputs/notice_waived/value |
| encashable leave days used (D13-encashable_leave_days_used) | 8 | data/generated/scenarios/scenario-13.json; scenario-13; LEAVE-E12; /display_inputs/encashable_leave_days_used/value |
| last drawn basic (D13-last_drawn_basic) | 35000 | data/generated/scenarios/scenario-13.json; scenario-13; SS-E12; /display_inputs/last_drawn_basic/value |
| last drawn da (D13-last_drawn_da) | 0 | data/generated/scenarios/scenario-13.json; scenario-13; SS-E12; /display_inputs/last_drawn_da/value |
| last drawn basic plus da (D13-last_drawn_basic_plus_da) | 35000 | data/generated/scenarios/scenario-13.json; scenario-13; scenario-13; /display_inputs/last_drawn_basic_plus_da/value |
| eligible_count (X-001) | 4 | data/generated/scenarios/scenario-04.json; scenario-04; /result/bonus_requests/0/aggregates/eligible_count/value |
| not_eligible_count (X-002) | 1 | data/generated/scenarios/scenario-04.json; scenario-04; /result/bonus_requests/0/aggregates/not_eligible_count/value |
| needs_input_count (X-003) | 1 | data/generated/scenarios/scenario-04.json; scenario-04; /result/bonus_requests/0/aggregates/needs_input_count/value |
| group_total_gross (X-004) | 213929 | data/generated/scenarios/scenario-04.json; scenario-04; /result/bonus_requests/0/aggregates/group_total_gross/value |
| group_total_tds (X-005) | Not available in generated data | data/generated/scenarios/scenario-04.json; scenario-04; /result/bonus_requests/0/aggregates/group_total_tds/value |
| group_total_net (X-006) | Not available in generated data | data/generated/scenarios/scenario-04.json; scenario-04; /result/bonus_requests/0/aggregates/group_total_net/value |
| eligible_count (X-007) | 3 | data/generated/scenarios/scenario-04.json; scenario-04; /result/bonus_requests/1/aggregates/eligible_count/value |
| not_eligible_count (X-008) | 0 | data/generated/scenarios/scenario-04.json; scenario-04; /result/bonus_requests/1/aggregates/not_eligible_count/value |
| needs_input_count (X-009) | 0 | data/generated/scenarios/scenario-04.json; scenario-04; /result/bonus_requests/1/aggregates/needs_input_count/value |
| group_total_gross (X-010) | 120000 | data/generated/scenarios/scenario-04.json; scenario-04; /result/bonus_requests/1/aggregates/group_total_gross/value |
| group_total_tds (X-011) | 0 | data/generated/scenarios/scenario-04.json; scenario-04; /result/bonus_requests/1/aggregates/group_total_tds/value |
| group_total_net (X-012) | 120000 | data/generated/scenarios/scenario-04.json; scenario-04; /result/bonus_requests/1/aggregates/group_total_net/value |
| recoveries_total (X-013) | 0 | data/generated/scenarios/scenario-06.json; scenario-06; /result/recoveries_total/value |
| known_recoveries_subtotal (X-014) | 0 | data/generated/scenarios/scenario-06.json; scenario-06; /result/known_recoveries_subtotal/value |
| recoveries_total (X-015) | 0 | data/generated/scenarios/scenario-07.json; scenario-07; /result/recoveries_total/value |
| known_recoveries_subtotal (X-016) | 0 | data/generated/scenarios/scenario-07.json; scenario-07; /result/known_recoveries_subtotal/value |
| recoveries_total (X-017) | Not available in generated data | data/generated/scenarios/scenario-08.json; scenario-08; /result/recoveries_total/value |
| known_recoveries_subtotal (X-018) | 56667 | data/generated/scenarios/scenario-08.json; scenario-08; /result/known_recoveries_subtotal/value |
| known_recoveries_subtotal flag (X-019) | Excludes unresolved asset recovery | data/generated/scenarios/scenario-08.json; scenario-08; /result/known_recoveries_subtotal/flags/0 |
| recoveries_total (X-041) | Not available in generated data | data/generated/scenarios/scenario-13.json; scenario-13; /result/recoveries_total/value |
| known_recoveries_subtotal (X-042) | 56667 | data/generated/scenarios/scenario-13.json; scenario-13; /result/known_recoveries_subtotal/value |
| known_recoveries_subtotal flag (X-043) | Excludes unresolved asset recovery | data/generated/scenarios/scenario-13.json; scenario-13; /result/known_recoveries_subtotal/flags/0 |
| bonus-rules.json rules_version (RV-5-rules_version) | Northwind demo rules v1 | data/generated/scenarios/scenario-04.json; scenario-04; bonus-rules.json#annual_performance_bonus; /result/bonus_requests/0/employees/0/annual_basic/rule_ids/0/rules_version |
| bonus-rules.json verified_on (RV-5-verified_on) | 2026-10-13 | data/generated/scenarios/scenario-04.json; scenario-04; bonus-rules.json#annual_performance_bonus; /result/bonus_requests/0/employees/0/annual_basic/rule_ids/0/verified_on |
| bonus-rules.json date_note (RV-5-date_note) | Applies to all demo periods | data/generated/scenarios/scenario-04.json; scenario-04; bonus-rules.json#annual_performance_bonus; /result/bonus_requests/0/employees/0/annual_basic/rule_ids/0/date_note |
| gratuity-rules.json rules_version (RV-6-rules_version) | Northwind demo rules v1 | data/generated/scenarios/scenario-06.json; scenario-06; gratuity-rules.json#formula; /result/components/gratuity/amount/rule_ids/0/rules_version |
| gratuity-rules.json verified_on (RV-6-verified_on) | 2026-10-13 | data/generated/scenarios/scenario-06.json; scenario-06; gratuity-rules.json#formula; /result/components/gratuity/amount/rule_ids/0/verified_on |
| gratuity-rules.json date_note (RV-6-date_note) | Applies to all demo periods | data/generated/scenarios/scenario-06.json; scenario-06; gratuity-rules.json#formula; /result/components/gratuity/amount/rule_ids/0/date_note |
## SCR-03 — Review a payroll query

Design HCM One's HR desktop query review at 1440 px wide. It follows F6-01 and F6-09–F6-11, applying UXP-01, UXP-02, UXP-04, UXP-06 and UXP-07. Use a 12-column grid with 64 px margins and 24 px gutters.

Use a white background, deep teal #0F766E as the only brand accent, dark text #0F172A, supporting text #475569 and surface #F8FAFC. Use Inter for all text and numbers. Apply tabular figures with font-feature-settings: "tnum" to amounts, dates and tables. Use a monospace font only for query IDs and record references. Reason: "Tabular figures align numbers in columns and feel calmer for payroll; monospace is kept for technical IDs." Use semantic status icons with full text, never color alone. Use generous white space, an 8 px card radius, 6 px controls and at least 44 px touch targets. Desktop title is 24 px and number hero is 40 px; mobile title is 24 px and number hero is 32 px. These are authoring tokens, not payroll facts.

Copy each displayed payroll number, period, date and record ID literally from the source table below. INR is a separate amount label. Do not round, abbreviate, total, count or infer a value. Do not use a raw mock number. Keep source file, record and JSON pointer as designer annotations; provide authorized Show calculation and View source in the product. The proof view copies the selected generated object's formula, inputs, rule_ids, effective dates, certainty and flags without evaluating it. Missing numeric operands stay Not available in generated data. Do not expose a complete dataset or another employee's record.

Use the exact AI sentences below. Braces are the approved named slots; fill only from an authorized actual record. Headings and labels are interface content, not new AI causal sentences. No confidence percentages. Keep certainty, workflow status and payment separate. Do not add charts, invented counts, timestamps, version numbers, bank actions or extra screens. Label controls, use semantic headings, give keyboard focus a visible outline and design for screen reader order. A drawer or sheet stays within its parent screen and returns focus when closed.

From top to bottom: HCM One and HR Admin; title Payroll queries; recorded query ID and status; Neha Gupta; period; original employee words; relevant evidence; What the payroll calculation shows; HR reply; empty reply editor; explicit resolution controls.

Neha Gupta matches generated E05 at data/generated/scenarios/scenario-09.json, scenario-09 /result/employee_id. The original non-numeric description is Please check my September attendance. Category is salary. These words come from data/mock/queries.json, QUERY-E05-SEPTEMBER; they are a seed description, not a new submitted complaint.

Use these exact generated fields for the recorded query and comparison evidence:

| Visible field | Literal value | File, record and JSON pointer |
|---|---|---|
| Existing query ID (Q-id) | QUERY-E05-SEPTEMBER | data/generated/scenarios/scenario-09.json; scenario-09; QUERY-E05-SEPTEMBER; /result/existing_query/query_id |
| Recorded query status (Q-status) | In review | data/generated/scenarios/scenario-09.json; scenario-09; QUERY-E05-SEPTEMBER; /result/existing_query/status |
| Later period (C9-after_month) | 2026-09 | data/generated/scenarios/scenario-09.json; scenario-09; /result/after_month |
| Earlier period (C9-before_month) | 2026-08 | data/generated/scenarios/scenario-09.json; scenario-09; /result/before_month |
| Take-home pay (C9-before-net_pay) | 48200 | data/generated/scenarios/scenario-09.json; scenario-09; /result/before/net_pay/value |
| Take-home pay (C9-after-net_pay) | 42780 | data/generated/scenarios/scenario-09.json; scenario-09; /result/after/net_pay/value |
| Earned gross (C9-before-gross) | 50000 | data/generated/scenarios/scenario-09.json; scenario-09; /result/before/earnings/gross/value |
| Earned gross (C9-after-gross) | 45000 | data/generated/scenarios/scenario-09.json; scenario-09; /result/after/earnings/gross/value |
| Paid days (C9-before-paid) | 31 | data/generated/scenarios/scenario-09.json; scenario-09; /result/before/earnings/paid_days/value |
| Paid days (C9-after-paid) | 27 | data/generated/scenarios/scenario-09.json; scenario-09; /result/after/earnings/paid_days/value |
| Employee PF (C9-before-pf-employee) | 1800 | data/generated/scenarios/scenario-09.json; scenario-09; /result/before/pf/employee/value |
| Employee PF (C9-after-pf-employee) | 2220 | data/generated/scenarios/scenario-09.json; scenario-09; /result/after/pf/employee/value |

The relevant attendance source is data/mock/attendance.json, ATT-E05-2026-09, already referenced by the existing query; it is a record link, not permission to copy raw mock numeric values. Show only authorized relevant evidence. The calculation does not prove the attendance entry is correct.

HR reply, Created at, Reviewed by and event times are not prefilled. Your reply starts as an empty editor. PQ-09 is resolved by design: Created by the code prototype at runtime as demo lifecycle records (version, actor, time, query ID, HR reply) when the user acts. Never pre-filled. Save the actual entered demo reply before showing it. Record resolution only on the explicit authorized action; closure retains its approved guard. No static design frame claims that a write occurred.

Design recorded In review as default, conditional Sent with Take into review, and conditional Resolved and Closed with real reply and event records. Do not claim resolution from a reply alone or from silence. Retrieval or storage failure keeps the last actual state; do not use a payroll-calculation error to imply that query storage succeeded. Include Show calculation and View evidence, with the same scope and focus behavior as the parent.

Design these alternate states as variants of the same screen. Keep the default fixture independent of them. Loading has no completed amount. Missing data keeps the affected field unavailable. Rule not verified stops only the affected calculation. Calculation error does not manufacture a total. Permission denial removes private context, numbers, source links and any target existence cue. Do not activate an alternate lifecycle state without an actual stored event.

Loading:

> I am waiting for the payroll records needed for this request. The result is not ready.

Copy source: output/06-ai-interaction/approval-failure-handling.md, Section 6, Loading.

Missing data:

> The required {record type} for {period or component} is missing. I cannot explain a complete result for this scope.

Copy source: output/06-ai-interaction/approval-failure-handling.md, Section 6, Missing data.

Rule not verified:

> The applicable rule basis for {affected scope} is not verified. That part cannot be calculated.

Copy source: output/06-ai-interaction/approval-failure-handling.md, Section 6, Rule not verified.

Calculation error, only when a payroll check actually fails:

> The payroll calculation did not produce a usable result for {affected scope}. I cannot give a complete amount for it.

Copy source: output/06-ai-interaction/approval-failure-handling.md, Section 6, Calculation error.

Permission denied:

> I cannot provide that information. I can help with payroll records you are authorized to access.

Copy source: output/06-ai-interaction/approval-failure-handling.md, Section 6, Permission denied.

---


### Filled attendance detail

| Visible field and binding | Literal value | File, record and JSON pointer |
|---|---|---|
| months 2026 08 lop days (D09-months-2026-08-lop_days) | 0 | data/generated/scenarios/scenario-09.json; scenario-09; ATT-E05-2026-08; /display_inputs/months/2026-08/lop_days/value |
| months 2026 08 calendar days (D09-months-2026-08-calendar_days) | 31 | data/generated/scenarios/scenario-09.json; scenario-09; ATT-E05-2026-08; /display_inputs/months/2026-08/calendar_days/value |
| months 2026 09 lop days (D09-months-2026-09-lop_days) | 3 | data/generated/scenarios/scenario-09.json; scenario-09; ATT-E05-2026-09; /display_inputs/months/2026-09/lop_days/value |
| months 2026 09 calendar days (D09-months-2026-09-calendar_days) | 30 | data/generated/scenarios/scenario-09.json; scenario-09; ATT-E05-2026-09; /display_inputs/months/2026-09/calendar_days/value |
## SCR-04 — Understand my payroll

Design HCM One's Employee mobile explanation at 390 px wide. It follows F4-01–F4-10 and F5-01–F5-10 and applies UXP-01–UXP-07. Use one column, 20 px outer padding and 16 px component gaps. A detail sheet belongs to this same screen; salary, TDS and denial are modes, not extra screens.

Use a white background, deep teal #0F766E as the only brand accent, dark text #0F172A, supporting text #475569 and surface #F8FAFC. Use Inter for all text and numbers. Apply tabular figures with font-feature-settings: "tnum" to amounts, dates and tables. Use a monospace font only for query IDs and record references. Reason: "Tabular figures align numbers in columns and feel calmer for payroll; monospace is kept for technical IDs." Use semantic status icons with full text, never color alone. Use generous white space, an 8 px card radius, 6 px controls and at least 44 px touch targets. Desktop title is 24 px and number hero is 40 px; mobile title is 24 px and number hero is 32 px. These are authoring tokens, not payroll facts.

Copy each displayed payroll number, period, date and record ID literally from the source table below. INR is a separate amount label. Do not round, abbreviate, total, count or infer a value. Do not use a raw mock number. Keep source file, record and JSON pointer as designer annotations; provide authorized Show calculation and View source in the product. The proof view copies the selected generated object's formula, inputs, rule_ids, effective dates, certainty and flags without evaluating it. Missing numeric operands stay Not available in generated data. Do not expose a complete dataset or another employee's record.

Use the exact AI sentences below. Braces are the approved named slots; fill only from an authorized actual record. Headings and labels are interface content, not new AI causal sentences. No confidence percentages. Keep certainty, workflow status and payment separate. Do not add charts, invented counts, timestamps, version numbers, bank actions or extra screens. Label controls, use semantic headings, give keyboard focus a visible outline and design for screen reader order. A drawer or sheet stays within its parent screen and returns focus when closed.

From top to bottom: HCM One; title Understand my payroll; own context; Salary and TDS choice; recorded period choice; blocker if present; change hero; factual reason labels; brief approved AI message; Show breakdown, Show calculation and View source; follow-up; Draft a query for HR. Do not add an employee picker.

Salary default is Neha Gupta, generated E05 at data/generated/scenarios/scenario-09.json, scenario-09 /result/employee_id. Show Complete for this scope from /result/certainty. Take-home change is the hero. Render the engine's reasons array in stored order, labeled Ranked by effect on take-home pay. For E05, show LOP then PF ceiling change with the corresponding signed effects and source references below. Do not sort, estimate or recompute the order. Keep the PF interaction flag visible in proof.

Use these exact values for the hero and earlier-versus-later breakdown:

| Visible field | Literal value | File, record and JSON pointer |
|---|---|---|
| Earlier period (C9-before_month) | 2026-08 | data/generated/scenarios/scenario-09.json; scenario-09; /result/before_month |
| Later period (C9-after_month) | 2026-09 | data/generated/scenarios/scenario-09.json; scenario-09; /result/after_month |
| Take-home change (C9-net_change) | -5420 | data/generated/scenarios/scenario-09.json; scenario-09; /result/net_change/value |
| Gross change (C9-gross_change) | -5000 | data/generated/scenarios/scenario-09.json; scenario-09; /result/gross_change/value |
| Employee PF change (C9-employee_pf_change) | 420 | data/generated/scenarios/scenario-09.json; scenario-09; /result/employee_pf_change/value |
| Earned gross (C9-before-gross) | 50000 | data/generated/scenarios/scenario-09.json; scenario-09; /result/before/earnings/gross/value |
| Earned gross (C9-after-gross) | 45000 | data/generated/scenarios/scenario-09.json; scenario-09; /result/after/earnings/gross/value |
| Employee PF (C9-before-pf-employee) | 1800 | data/generated/scenarios/scenario-09.json; scenario-09; /result/before/pf/employee/value |
| Employee PF (C9-after-pf-employee) | 2220 | data/generated/scenarios/scenario-09.json; scenario-09; /result/after/pf/employee/value |
| Monthly TDS (C9-before-tds) | 0 | data/generated/scenarios/scenario-09.json; scenario-09; /result/before/tds/amount/value |
| Monthly TDS (C9-after-tds) | 0 | data/generated/scenarios/scenario-09.json; scenario-09; /result/after/tds/amount/value |
| Total employee deductions (C9-before-total_deductions) | 1800 | data/generated/scenarios/scenario-09.json; scenario-09; /result/before/total_deductions/value |
| Total employee deductions (C9-after-total_deductions) | 2220 | data/generated/scenarios/scenario-09.json; scenario-09; /result/after/total_deductions/value |
| Take-home pay (C9-before-net_pay) | 48200 | data/generated/scenarios/scenario-09.json; scenario-09; /result/before/net_pay/value |
| Take-home pay (C9-after-net_pay) | 42780 | data/generated/scenarios/scenario-09.json; scenario-09; /result/after/net_pay/value |
| basic (C9-before-basic) | 25000 | data/generated/scenarios/scenario-09.json; scenario-09; /result/before/earnings/lines/basic/value |
| basic (C9-after-basic) | 22500 | data/generated/scenarios/scenario-09.json; scenario-09; /result/after/earnings/lines/basic/value |
| da (C9-before-da) | 0 | data/generated/scenarios/scenario-09.json; scenario-09; /result/before/earnings/lines/da/value |
| da (C9-after-da) | 0 | data/generated/scenarios/scenario-09.json; scenario-09; /result/after/earnings/lines/da/value |
| hra (C9-before-hra) | 12500 | data/generated/scenarios/scenario-09.json; scenario-09; /result/before/earnings/lines/hra/value |
| hra (C9-after-hra) | 11250 | data/generated/scenarios/scenario-09.json; scenario-09; /result/after/earnings/lines/hra/value |
| special_allowance (C9-before-special_allowance) | 12500 | data/generated/scenarios/scenario-09.json; scenario-09; /result/before/earnings/lines/special_allowance/value |
| special_allowance (C9-after-special_allowance) | 11250 | data/generated/scenarios/scenario-09.json; scenario-09; /result/after/earnings/lines/special_allowance/value |
| Paid days (C9-before-paid) | 31 | data/generated/scenarios/scenario-09.json; scenario-09; /result/before/earnings/paid_days/value |
| Paid days (C9-after-paid) | 27 | data/generated/scenarios/scenario-09.json; scenario-09; /result/after/earnings/paid_days/value |

Unpaid leave days and Calendar days now use the matching scenario-09 display_inputs. The reasons list and its signed effects come directly from /result/reasons. Employee deductions and employer contributions remain separate. Never calculate leave days by subtracting paid days.

Use this approved offer:

> Would you like the earnings and deductions breakdown?

Copy source: output/06-ai-interaction/conversation-design.md, Section 8, Example B.

TDS alternate is Siddharth Jain, generated E06 at data/generated/scenarios/scenario-10.json, scenario-10 /result/employee_id. Hero label TDS change. The recorded reason is the accepted previous-employer income declaration, matching BRD v1.2 and Approved DEC-029. Use the approved main reason below; its declared month range is not present in display_inputs and must remain visibly unavailable.

Approved main reason template, copied from Agent 06 A06-10 and DEC-029:

> Your TDS is higher because you declared income from your previous employer for {declared months}. That income is added to your yearly income, so your expected yearly tax is higher. The tax your previous employer already deducted is counted, so it is not deducted twice.

Current preview with the unexported month slot visibly missing:

> Your TDS is higher because you declared income from your previous employer for Not available in generated data. That income is added to your yearly income, so your expected yearly tax is higher. The tax your previous employer already deducted is counted, so it is not deducted twice.

Keep the missing month operand visible. Do not fill it from comparison periods, a record ID or raw mock data. Use the existing approved detail message:

> The payroll calculation detail includes projected yearly income, applied deductions and exemptions, yearly tax, tax already deducted and remaining months. It identifies your recorded tax regime and applicable rule version.

Copy source: output/06-ai-interaction/conversation-design.md, Section 8, Example C.

The tax sheet uses these exact stored values:

| Visible field | Literal value | File, record and JSON pointer |
|---|---|---|
| Earlier period (C10-before_month) | 2026-08 | data/generated/scenarios/scenario-10.json; scenario-10; /result/before_month |
| Later period (C10-after_month) | 2026-09 | data/generated/scenarios/scenario-10.json; scenario-10; /result/after_month |
| TDS change (C10-tds_change) | 12454 | data/generated/scenarios/scenario-10.json; scenario-10; /result/tds_change/value |
| Monthly TDS (C10-before-tds) | 0 | data/generated/scenarios/scenario-10.json; scenario-10; /result/before/tds/amount/value |
| Monthly TDS (C10-after-tds) | 12454 | data/generated/scenarios/scenario-10.json; scenario-10; /result/after/tds/amount/value |
| Projected yearly gross income (T-projected_gross) | 1530000 | data/generated/scenarios/scenario-10.json; scenario-10; /result/after/tds/projected_gross/value |
| Standard deduction (T-standard_deduction) | 75000 | data/generated/scenarios/scenario-10.json; scenario-10; /result/after/tds/standard_deduction/value |
| Projected taxable income (T-taxable_income) | 1455000 | data/generated/scenarios/scenario-10.json; scenario-10; /result/after/tds/taxable_income/value |
| Yearly tax before cess (T-slab_tax) | 98250 | data/generated/scenarios/scenario-10.json; scenario-10; /result/after/tds/slab_tax/value |
| Cess (T-cess) | 3930 | data/generated/scenarios/scenario-10.json; scenario-10; /result/after/tds/cess/value |
| Yearly tax including cess (T-yearly_tax) | 102180 | data/generated/scenarios/scenario-10.json; scenario-10; /result/after/tds/yearly_tax/value |
| Tax already deducted (T-tax_already_deducted) | 15000 | data/generated/scenarios/scenario-10.json; scenario-10; /result/after/tds/tax_already_deducted/value |
| Remaining months (T-remaining_months) | 7 | data/generated/scenarios/scenario-10.json; scenario-10; /result/after/tds/remaining_months/value |

Label tax_already_deducted as aggregate already deducted. Show previous-employer declared gross, previous-employer TDS, Northwind TDS already deducted and remaining yearly tax from scenario-10 display_inputs below, separately. Copy all values; never subtract or relabel to fill a subtotal. Show the generated rules_version and verified_on. For null effective dates show the stored date_note Applies to all demo periods, not a made-up date.

For personal advice use:

> I can explain the tax recorded in your payroll. I cannot recommend a tax regime or investment. Please consult a tax professional for personal advice.

Copy source: output/06-ai-interaction/conversation-design.md, Section 5, Personal tax advice.

No earning change alternate is Pooja Das, generated E16 at data/generated/scenarios/scenario-11.json, scenario-11 /result/employee_id. Heading No salary earning component change. Show the engine's reason array in stored order and label it Ranked by effect on take-home pay. Unchanged earnings do not imply unchanged net. Use D11 for LOP and calendar-day detail.

| Visible field | Literal value | File, record and JSON pointer |
|---|---|---|
| Earlier period (C11-before_month) | 2026-08 | data/generated/scenarios/scenario-11.json; scenario-11; /result/before_month |
| Later period (C11-after_month) | 2026-09 | data/generated/scenarios/scenario-11.json; scenario-11; /result/after_month |
| Gross change (C11-gross_change) | 0 | data/generated/scenarios/scenario-11.json; scenario-11; /result/gross_change/value |
| Employee PF change (C11-employee_pf_change) | 420 | data/generated/scenarios/scenario-11.json; scenario-11; /result/employee_pf_change/value |
| Take-home change (C11-net_change) | -420 | data/generated/scenarios/scenario-11.json; scenario-11; /result/net_change/value |
| Earned gross (C11-before-gross) | 45000 | data/generated/scenarios/scenario-11.json; scenario-11; /result/before/earnings/gross/value |
| Earned gross (C11-after-gross) | 45000 | data/generated/scenarios/scenario-11.json; scenario-11; /result/after/earnings/gross/value |
| Employee PF (C11-before-pf-employee) | 1800 | data/generated/scenarios/scenario-11.json; scenario-11; /result/before/pf/employee/value |
| Employee PF (C11-after-pf-employee) | 2220 | data/generated/scenarios/scenario-11.json; scenario-11; /result/after/pf/employee/value |
| Take-home pay (C11-before-net_pay) | 43200 | data/generated/scenarios/scenario-11.json; scenario-11; /result/before/net_pay/value |
| Take-home pay (C11-after-net_pay) | 42780 | data/generated/scenarios/scenario-11.json; scenario-11; /result/after/net_pay/value |

Scenario-12 permission denial shows Payroll access and Permission denied, from data/generated/scenarios/scenario-12.json, scenario-12 /result/status. Remove every target name, ID, period, amount, source and cached detail. Offer Ask about my payroll and use only the refusal below.

Future-pay follow-up uses:

> This explains the recorded months. I cannot promise next month's pay. It depends on that month's recorded inputs and applicable rules.

Copy source: output/06-ai-interaction/conversation-design.md, Section 8, Example B.

Unexplained mismatch uses:

> The available payroll records do not explain this difference. I can help draft a query for HR.

Copy source: output/06-ai-interaction/approval-failure-handling.md, Section 6, Unexplained mismatch.

Draft a query never sends. Changed comparison scope needs Employee confirmation. Later settlement statement belongs to Flow 3's output and requires a real approved snapshot; the generated unapproved settlement is not an issued statement. DEC-019 allows statement access and Flow 6 follow-up only while the Employee has access; no post-exit portal or channel is added.

Design these alternate states as variants of the same screen. Keep the default fixture independent of them. Loading has no completed amount. Missing data keeps the affected field unavailable. Rule not verified stops only the affected calculation. Calculation error does not manufacture a total. Permission denial removes private context, numbers, source links and any target existence cue. Do not activate an alternate lifecycle state without an actual stored event.

Loading:

> I am waiting for the payroll records needed for this request. The result is not ready.

Copy source: output/06-ai-interaction/approval-failure-handling.md, Section 6, Loading.

Missing data:

> The required {record type} for {period or component} is missing. I cannot explain a complete result for this scope.

Copy source: output/06-ai-interaction/approval-failure-handling.md, Section 6, Missing data.

Rule not verified:

> The applicable rule basis for {affected scope} is not verified. That part cannot be calculated.

Copy source: output/06-ai-interaction/approval-failure-handling.md, Section 6, Rule not verified.

Calculation error, only when a payroll check actually fails:

> The payroll calculation did not produce a usable result for {affected scope}. I cannot give a complete amount for it.

Copy source: output/06-ai-interaction/approval-failure-handling.md, Section 6, Calculation error.

Permission denied:

> I cannot provide that information. I can help with payroll records you are authorized to access.

Copy source: output/06-ai-interaction/approval-failure-handling.md, Section 6, Permission denied.

---


### Filled attendance, tax operands and ranked reasons

| Visible field and binding | Literal value | File, record and JSON pointer |
|---|---|---|
| months 2026 08 lop days (D09-months-2026-08-lop_days) | 0 | data/generated/scenarios/scenario-09.json; scenario-09; ATT-E05-2026-08; /display_inputs/months/2026-08/lop_days/value |
| months 2026 08 calendar days (D09-months-2026-08-calendar_days) | 31 | data/generated/scenarios/scenario-09.json; scenario-09; ATT-E05-2026-08; /display_inputs/months/2026-08/calendar_days/value |
| months 2026 09 lop days (D09-months-2026-09-lop_days) | 3 | data/generated/scenarios/scenario-09.json; scenario-09; ATT-E05-2026-09; /display_inputs/months/2026-09/lop_days/value |
| months 2026 09 calendar days (D09-months-2026-09-calendar_days) | 30 | data/generated/scenarios/scenario-09.json; scenario-09; ATT-E05-2026-09; /display_inputs/months/2026-09/calendar_days/value |
| months 2026 08 lop days (D10-months-2026-08-lop_days) | 0 | data/generated/scenarios/scenario-10.json; scenario-10; ATT-E06-2026-08; /display_inputs/months/2026-08/lop_days/value |
| months 2026 08 calendar days (D10-months-2026-08-calendar_days) | 31 | data/generated/scenarios/scenario-10.json; scenario-10; ATT-E06-2026-08; /display_inputs/months/2026-08/calendar_days/value |
| months 2026 09 lop days (D10-months-2026-09-lop_days) | 0 | data/generated/scenarios/scenario-10.json; scenario-10; ATT-E06-2026-09; /display_inputs/months/2026-09/lop_days/value |
| months 2026 09 calendar days (D10-months-2026-09-calendar_days) | 30 | data/generated/scenarios/scenario-10.json; scenario-10; ATT-E06-2026-09; /display_inputs/months/2026-09/calendar_days/value |
| previous employer declared gross (D10-previous_employer_declared_gross) | 450000 | data/generated/scenarios/scenario-10.json; scenario-10; DECL-E06-PREVIOUS-EMPLOYER; /display_inputs/previous_employer_declared_gross/value |
| previous employer tds (D10-previous_employer_tds) | 15000 | data/generated/scenarios/scenario-10.json; scenario-10; DECL-E06-PREVIOUS-EMPLOYER; /display_inputs/previous_employer_tds/value |
| northwind tds already deducted (D10-northwind_tds_already_deducted) | 0 | data/generated/scenarios/scenario-10.json; scenario-10; scenario-10; /display_inputs/northwind_tds_already_deducted/value |
| remaining yearly tax (D10-remaining_yearly_tax) | 87180 | data/generated/scenarios/scenario-10.json; scenario-10; scenario-10; /display_inputs/remaining_yearly_tax/value |
| months 2026 08 lop days (D11-months-2026-08-lop_days) | 0 | data/generated/scenarios/scenario-11.json; scenario-11; ATT-E16-2026-08; /display_inputs/months/2026-08/lop_days/value |
| months 2026 08 calendar days (D11-months-2026-08-calendar_days) | 31 | data/generated/scenarios/scenario-11.json; scenario-11; ATT-E16-2026-08; /display_inputs/months/2026-08/calendar_days/value |
| months 2026 09 lop days (D11-months-2026-09-lop_days) | 0 | data/generated/scenarios/scenario-11.json; scenario-11; ATT-E16-2026-09; /display_inputs/months/2026-09/lop_days/value |
| months 2026 09 calendar days (D11-months-2026-09-calendar_days) | 30 | data/generated/scenarios/scenario-11.json; scenario-11; ATT-E16-2026-09; /display_inputs/months/2026-09/calendar_days/value |
| Ranked reason type (X-020) | LOP | data/generated/scenarios/scenario-09.json; scenario-09; /result/reasons/0/type |
| Ranked take-home effect (X-021) | -5000 | data/generated/scenarios/scenario-09.json; scenario-09; /result/reasons/0/effect_amount/value |
| Ranked reason sources (X-022) | [{"source_file":"data/mock/employees.json","record_id":"E05"},{"source_file":"data/mock/salary-structures.json","record_id":"SS-E05"},{"source_file":"data/mock/company.json","record_id":"NORTHWIND-DEMO"},{"source_file":"data/mock/attendance.json","record_id":"ATT-E05-2026-09"},{"source_file":"data/mock/attendance.json","record_id":"ATT-E05-2026-08"}] | data/generated/scenarios/scenario-09.json; scenario-09; /result/reasons/0/source_references |
| Ranked reason type (X-023) | PF ceiling change | data/generated/scenarios/scenario-09.json; scenario-09; /result/reasons/1/type |
| Ranked take-home effect (X-024) | -420 | data/generated/scenarios/scenario-09.json; scenario-09; /result/reasons/1/effect_amount/value |
| Ranked reason flag (X-025) | PF effect includes earned wage after LOP and dated ceiling segments | data/generated/scenarios/scenario-09.json; scenario-09; /result/reasons/1/effect_amount/flags/0 |
| Ranked reason sources (X-026) | [{"source_file":"data/mock/employees.json","record_id":"E05"},{"source_file":"data/mock/salary-structures.json","record_id":"SS-E05"},{"source_file":"data/mock/company.json","record_id":"NORTHWIND-DEMO"},{"source_file":"data/mock/attendance.json","record_id":"ATT-E05-2026-09"},{"source_file":"data/mock/attendance.json","record_id":"ATT-E05-2026-08"}] | data/generated/scenarios/scenario-09.json; scenario-09; /result/reasons/1/source_references |
| Ranked reason type (X-027) | TDS change | data/generated/scenarios/scenario-10.json; scenario-10; /result/reasons/0/type |
| Ranked take-home effect (X-028) | -12454 | data/generated/scenarios/scenario-10.json; scenario-10; /result/reasons/0/effect_amount/value |
| Ranked reason sources (X-029) | [{"source_file":"data/mock/employees.json","record_id":"E06"},{"source_file":"data/mock/salary-structures.json","record_id":"SS-E06"},{"source_file":"data/mock/company.json","record_id":"NORTHWIND-DEMO"},{"source_file":"data/mock/declarations.json","record_id":"DECL-E06-PREVIOUS-EMPLOYER"}] | data/generated/scenarios/scenario-10.json; scenario-10; /result/reasons/0/source_references |
| Ranked reason type (X-030) | PF ceiling change | data/generated/scenarios/scenario-10.json; scenario-10; /result/reasons/1/type |
| Ranked take-home effect (X-031) | -560 | data/generated/scenarios/scenario-10.json; scenario-10; /result/reasons/1/effect_amount/value |
| Ranked reason flag (X-032) | PF effect includes earned wage after LOP and dated ceiling segments | data/generated/scenarios/scenario-10.json; scenario-10; /result/reasons/1/effect_amount/flags/0 |
| Ranked reason sources (X-033) | [{"source_file":"data/mock/employees.json","record_id":"E06"},{"source_file":"data/mock/salary-structures.json","record_id":"SS-E06"},{"source_file":"data/mock/company.json","record_id":"NORTHWIND-DEMO"},{"source_file":"data/mock/attendance.json","record_id":"ATT-E06-2026-09"},{"source_file":"data/mock/attendance.json","record_id":"ATT-E06-2026-08"}] | data/generated/scenarios/scenario-10.json; scenario-10; /result/reasons/1/source_references |
| rules_version (X-034) | Northwind demo rules v1 | data/generated/scenarios/scenario-10.json; scenario-10; /result/after/tds/amount/rule_ids/9/rules_version |
| verified_on (X-035) | 2026-10-13 | data/generated/scenarios/scenario-10.json; scenario-10; /result/after/tds/amount/rule_ids/9/verified_on |
| date_note (X-036) | Applies to all demo periods | data/generated/scenarios/scenario-10.json; scenario-10; /result/after/tds/amount/rule_ids/9/date_note |
| Ranked reason type (X-037) | PF ceiling change | data/generated/scenarios/scenario-11.json; scenario-11; /result/reasons/0/type |
| Ranked take-home effect (X-038) | -420 | data/generated/scenarios/scenario-11.json; scenario-11; /result/reasons/0/effect_amount/value |
| Ranked reason flag (X-039) | PF effect includes earned wage after LOP and dated ceiling segments | data/generated/scenarios/scenario-11.json; scenario-11; /result/reasons/0/effect_amount/flags/0 |
| Ranked reason sources (X-040) | [{"source_file":"data/mock/employees.json","record_id":"E16"},{"source_file":"data/mock/salary-structures.json","record_id":"SS-E16"},{"source_file":"data/mock/company.json","record_id":"NORTHWIND-DEMO"},{"source_file":"data/mock/attendance.json","record_id":"ATT-E16-2026-09"},{"source_file":"data/mock/attendance.json","record_id":"ATT-E16-2026-08"}] | data/generated/scenarios/scenario-11.json; scenario-11; /result/reasons/0/source_references |
## SCR-05 — Review my query draft

Design HCM One's Employee mobile draft review at 390 px wide. It follows F6-01–F6-09 and applies UXP-01, UXP-02, UXP-04, UXP-06 and UXP-07. Use one column with 20 px outer padding and 16 px component gaps.

Use a white background, deep teal #0F766E as the only brand accent, dark text #0F172A, supporting text #475569 and surface #F8FAFC. Use Inter for all text and numbers. Apply tabular figures with font-feature-settings: "tnum" to amounts, dates and tables. Use a monospace font only for query IDs and record references. Reason: "Tabular figures align numbers in columns and feel calmer for payroll; monospace is kept for technical IDs." Use semantic status icons with full text, never color alone. Use generous white space, an 8 px card radius, 6 px controls and at least 44 px touch targets. Desktop title is 24 px and number hero is 40 px; mobile title is 24 px and number hero is 32 px. These are authoring tokens, not payroll facts.

Copy each displayed payroll number, period, date and record ID literally from the source table below. INR is a separate amount label. Do not round, abbreviate, total, count or infer a value. Do not use a raw mock number. Keep source file, record and JSON pointer as designer annotations; provide authorized Show calculation and View source in the product. The proof view copies the selected generated object's formula, inputs, rule_ids, effective dates, certainty and flags without evaluating it. Missing numeric operands stay Not available in generated data. Do not expose a complete dataset or another employee's record.

Use the exact AI sentences below. Braces are the approved named slots; fill only from an authorized actual record. Headings and labels are interface content, not new AI causal sentences. No confidence percentages. Keep certainty, workflow status and payment separate. Do not add charts, invented counts, timestamps, version numbers, bank actions or extra screens. Label controls, use semantic headings, give keyboard focus a visible outline and design for screen reader order. A drawer or sheet stays within its parent screen and returns focus when closed.

From top to bottom: title Review my query draft; unsent Draft label; category; period; editable employee description; removable relevant evidence; disputed point; own open candidate; add-or-new choice; explicit confirmation; actions.

Use Neha Gupta for generated E05 at data/generated/scenarios/scenario-09.json, scenario-09 /result/employee_id. Category salary and description Please check my September attendance. are allowed non-numeric seed text from data/mock/queries.json, QUERY-E05-SEPTEMBER. This is editable demonstration content, not a new submission.

The period, numeric evidence previews and actual existing candidate are:

| Visible field | Literal value | File, record and JSON pointer |
|---|---|---|
| Later period (C9-after_month) | 2026-09 | data/generated/scenarios/scenario-09.json; scenario-09; /result/after_month |
| Earned gross (C9-after-gross) | 45000 | data/generated/scenarios/scenario-09.json; scenario-09; /result/after/earnings/gross/value |
| Paid days (C9-after-paid) | 27 | data/generated/scenarios/scenario-09.json; scenario-09; /result/after/earnings/paid_days/value |
| Employee PF (C9-after-pf-employee) | 2220 | data/generated/scenarios/scenario-09.json; scenario-09; /result/after/pf/employee/value |
| Existing query ID (Q-id) | QUERY-E05-SEPTEMBER | data/generated/scenarios/scenario-09.json; scenario-09; QUERY-E05-SEPTEMBER; /result/existing_query/query_id |
| Recorded query status (Q-status) | In review | data/generated/scenarios/scenario-09.json; scenario-09; QUERY-E05-SEPTEMBER; /result/existing_query/status |

The candidate matches the same own employee, category and period. Never use its ID as a newly sent query ID. Do not show an invented candidate count. Relevant attendance evidence is the existing ATT-E05-2026-09 reference, not raw mock numeric content.

Ask:

> Is this the same issue as your open query, or a different issue?

Copy source: output/06-ai-interaction/conversation-design.md, Section 4.

Choices are Add to my open query and Create a new query. After the Employee chooses new, show:

> Send this query with the listed evidence to HR?

Copy source: output/06-ai-interaction/approval-failure-handling.md, Section 5.

After the Employee chooses append, show:

> Add this description and the listed evidence to your selected open query?

Copy source: output/06-ai-interaction/approval-failure-handling.md, Section 5.

Destination is authorized HR in HCM One. Actions are Back to edit, Cancel and explicit Confirm and send or Confirm and add. Content or destination changes clear confirmation. PQ-09 is resolved by design: Created by the code prototype at runtime as demo lifecycle records (version, actor, time, query ID, HR reply) when the user acts. Never pre-filled. Persist the actual confirmed demo action before claiming Sent or an append. Never reuse the existing candidate ID as a new ID. The static frame itself creates no sent event.

Show default Draft, edited and removed-evidence variants, candidate choice and confirmation. Cancel and silence leave Draft. Existing recorded query lookup leads to SCR-06. A successful new Sent state requires actual persistence and a stable returned ID; append retains the existing query's actual ID and status.

For delivery failure, retain the draft and use:

> Your query has not been sent. It remains a draft.

Copy source: output/06-ai-interaction/approval-failure-handling.md, Section 6, Query delivery failure.

Do not claim Sent after failure. Evidence sufficiency remains the existing GAP-08 question for testing.

Design these alternate states as variants of the same screen. Keep the default fixture independent of them. Loading has no completed amount. Missing data keeps the affected field unavailable. Rule not verified stops only the affected calculation. Calculation error does not manufacture a total. Permission denial removes private context, numbers, source links and any target existence cue. Do not activate an alternate lifecycle state without an actual stored event.

Loading:

> I am waiting for the payroll records needed for this request. The result is not ready.

Copy source: output/06-ai-interaction/approval-failure-handling.md, Section 6, Loading.

Missing data:

> The required {record type} for {period or component} is missing. I cannot explain a complete result for this scope.

Copy source: output/06-ai-interaction/approval-failure-handling.md, Section 6, Missing data.

Rule not verified:

> The applicable rule basis for {affected scope} is not verified. That part cannot be calculated.

Copy source: output/06-ai-interaction/approval-failure-handling.md, Section 6, Rule not verified.

Calculation error, only when a payroll check actually fails:

> The payroll calculation did not produce a usable result for {affected scope}. I cannot give a complete amount for it.

Copy source: output/06-ai-interaction/approval-failure-handling.md, Section 6, Calculation error.

Permission denied:

> I cannot provide that information. I can help with payroll records you are authorized to access.

Copy source: output/06-ai-interaction/approval-failure-handling.md, Section 6, Permission denied.

---


### Filled attendance evidence

| Visible field and binding | Literal value | File, record and JSON pointer |
|---|---|---|
| months 2026 08 lop days (D09-months-2026-08-lop_days) | 0 | data/generated/scenarios/scenario-09.json; scenario-09; ATT-E05-2026-08; /display_inputs/months/2026-08/lop_days/value |
| months 2026 08 calendar days (D09-months-2026-08-calendar_days) | 31 | data/generated/scenarios/scenario-09.json; scenario-09; ATT-E05-2026-08; /display_inputs/months/2026-08/calendar_days/value |
| months 2026 09 lop days (D09-months-2026-09-lop_days) | 3 | data/generated/scenarios/scenario-09.json; scenario-09; ATT-E05-2026-09; /display_inputs/months/2026-09/lop_days/value |
| months 2026 09 calendar days (D09-months-2026-09-calendar_days) | 30 | data/generated/scenarios/scenario-09.json; scenario-09; ATT-E05-2026-09; /display_inputs/months/2026-09/calendar_days/value |
## SCR-06 — Track my payroll query

Design HCM One's Employee mobile own-query tracking at 390 px wide. It follows F6-12 and the approved query state transitions, applying UXP-02, UXP-04, UXP-06 and UXP-07. Use one column with 20 px outer padding and 16 px component gaps.

Use a white background, deep teal #0F766E as the only brand accent, dark text #0F172A, supporting text #475569 and surface #F8FAFC. Use Inter for all text and numbers. Apply tabular figures with font-feature-settings: "tnum" to amounts, dates and tables. Use a monospace font only for query IDs and record references. Reason: "Tabular figures align numbers in columns and feel calmer for payroll; monospace is kept for technical IDs." Use semantic status icons with full text, never color alone. Use generous white space, an 8 px card radius, 6 px controls and at least 44 px touch targets. Desktop title is 24 px and number hero is 40 px; mobile title is 24 px and number hero is 32 px. These are authoring tokens, not payroll facts.

Copy each displayed payroll number, period, date and record ID literally from the source table below. INR is a separate amount label. Do not round, abbreviate, total, count or infer a value. Do not use a raw mock number. Keep source file, record and JSON pointer as designer annotations; provide authorized Show calculation and View source in the product. The proof view copies the selected generated object's formula, inputs, rule_ids, effective dates, certainty and flags without evaluating it. Missing numeric operands stay Not available in generated data. Do not expose a complete dataset or another employee's record.

Use the exact AI sentences below. Braces are the approved named slots; fill only from an authorized actual record. Headings and labels are interface content, not new AI causal sentences. No confidence percentages. Keep certainty, workflow status and payment separate. Do not add charts, invented counts, timestamps, version numbers, bank actions or extra screens. Label controls, use semantic headings, give keyboard focus a visible outline and design for screen reader order. A drawer or sheet stays within its parent screen and returns focus when closed.

From top to bottom: title My payroll query; own recorded ID; full status and icon; Neha Gupta and period; original description; evidence link; HR reply; actions; Back to payroll. Do not add a response countdown, progress percentage or fabricated timeline.

Neha Gupta matches generated E05 at data/generated/scenarios/scenario-09.json, scenario-09 /result/employee_id. The description Please check my September attendance. comes from the allowed non-numeric seed at data/mock/queries.json, QUERY-E05-SEPTEMBER.

The recorded ID, status and period are:

| Visible field | Literal value | File, record and JSON pointer |
|---|---|---|
| Existing query ID (Q-id) | QUERY-E05-SEPTEMBER | data/generated/scenarios/scenario-09.json; scenario-09; QUERY-E05-SEPTEMBER; /result/existing_query/query_id |
| Recorded query status (Q-status) | In review | data/generated/scenarios/scenario-09.json; scenario-09; QUERY-E05-SEPTEMBER; /result/existing_query/status |
| Later period (C9-after_month) | 2026-09 | data/generated/scenarios/scenario-09.json; scenario-09; /result/after_month |

Use this exact message for the actual In review state:

> Your query is In review. HR has taken it for review.

Copy source: output/06-ai-interaction/conversation-design.md, Section 7, A06-12.

HR reply, Created at, Reviewed at, Resolved at and Closed at are not prefilled. PQ-09 is resolved by design: Created by the code prototype at runtime as demo lifecycle records (version, actor, time, query ID, HR reply) when the user acts. Never pre-filled. Show only the actual stored runtime reply and event records after authorized actions. Keep View evidence, status lookup and Back to payroll. A reply alone never implies Resolved.

Design the following conditional variants, populated only if the corresponding actual stored state exists:

Sent:

> Your query is Sent. HR can access it for review.

Copy source: output/06-ai-interaction/conversation-design.md, Section 7, A06-12.

Resolved, with the actual recorded reply, explicit Dispute resolution and Close query acknowledgment:

> HR recorded a resolution. Here is the recorded reply. You can dispute the resolution if it does not answer your issue.

Copy source: output/06-ai-interaction/conversation-design.md, Section 7, A06-12.

Closed, retaining history and allowing a new unsent draft for a new issue:

> Your query is Closed. Its history is retained. A new issue can be drafted separately.

Copy source: output/06-ai-interaction/conversation-design.md, Section 7, A06-12.

Dispute returns to In review only through the approved explicit transition. Closing requires the approved prior-resolution guard. The current In review fixture does not enable a fake dispute or closure event. Retrieval failure retains the last actual state and claims no successful update. A rule or calculation limitation applies only to dependent payroll evidence; it does not automatically change the query's lifecycle status.

Design these alternate states as variants of the same screen. Keep the default fixture independent of them. Loading has no completed amount. Missing data keeps the affected field unavailable. Rule not verified stops only the affected calculation. Calculation error does not manufacture a total. Permission denial removes private context, numbers, source links and any target existence cue. Do not activate an alternate lifecycle state without an actual stored event.

Loading:

> I am waiting for the payroll records needed for this request. The result is not ready.

Copy source: output/06-ai-interaction/approval-failure-handling.md, Section 6, Loading.

Missing data:

> The required {record type} for {period or component} is missing. I cannot explain a complete result for this scope.

Copy source: output/06-ai-interaction/approval-failure-handling.md, Section 6, Missing data.

Rule not verified:

> The applicable rule basis for {affected scope} is not verified. That part cannot be calculated.

Copy source: output/06-ai-interaction/approval-failure-handling.md, Section 6, Rule not verified.

Calculation error, only when a payroll check actually fails:

> The payroll calculation did not produce a usable result for {affected scope}. I cannot give a complete amount for it.

Copy source: output/06-ai-interaction/approval-failure-handling.md, Section 6, Calculation error.

Permission denied:

> I cannot provide that information. I can help with payroll records you are authorized to access.

Copy source: output/06-ai-interaction/approval-failure-handling.md, Section 6, Permission denied.
