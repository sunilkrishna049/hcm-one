# HCM One: Trust and Explainability

Sources: approved [flows](../05-architecture/user-flows.md), [states](../05-architecture/edge-cases-states.md), [UX principles](../04-strategy/ux-principles.md), [problems](../04-strategy/problem-statements.md), [research](../02-research/secondary-research.md), [personas](../03-analysis/personas.md), [assumptions](../01-project/assumptions.md), [decision log](../../project-memory/design-decisions.md) and [BRD v1.1](../../input/requirements/Payroll_brd_v1.1.md). IDs below refer to these linked sources. Current BRD v1.1 and approved DEC-008 through DEC-015 govern earlier proposal wording. This file proposes content and behavior for G06. It adds no flow, lifecycle state or visual design.

## 1. Summary

Show what changed, why it changed and which records support it. Calculation code produces the figures, comparisons, reasons based on recorded inputs, formulas and applicable dates. The AI explains that result. A result is not approval or payment. Stop unsupported explanations rather than completing them with a guess. **High for requirements:** FR-1.10–FR-1.13, FR-4.4–FR-4.15, FR-5.3–FR-5.12; GR-1.1–GR-1.3, GR-3.1–GR-3.5; UXP-01–UXP-06.

**Proposed patterns; Low confidence in user suitability:** The wording, detail choices and certainty labels below need testing. Vendor source features are documented in EVD-35 and EVD-41. They do not prove a trust increase. Trust benefit remains an **Assumption, AS-4**. Understanding these labels is **Assumption, AS-16**. No AI confidence score is shown. (EG-04, EG-06, EG-07; AS-3, AS-4)

## 2. Explanation layers

The detail order is the same across roles. The first message includes a brief scope and status statement before the layers. It identifies the employee or authorized group, period, result version where applicable, and any blocker. A blocker appears before an unsupported amount. It remains visible when details are requested. (UXP-01, UXP-04, UXP-05, UXP-07; FR-1.12–FR-1.13, FR-2.13, FR-3.17–FR-3.18)

| Order | Layer | HR Admin | Employee | Source |
|---|---|---|---|---|
| First | Change or result summary | State that this is a proposal. Give code-produced gross, deductions and expected net for the named valid scope. Identify incomplete scope before totals. | Start with the code-produced take-home change or TDS change and comparison periods. In a settlement statement, start with the known net direction or explain why the net is incomplete. | FR-1.9, FR-1.13, FR-2.11, FR-2.15, FR-3.14, FR-3.18, FR-4.4, FR-5.3; UXP-03–UXP-05 |
| Second | Main reasons | Identify the input changes, affected periods, dependencies and unusual items requiring review. | Explain the largest recorded reasons first. Say what changed, why and when. Do not invent a reason if the code cannot establish it. | FR-1.6–FR-1.12, FR-2.14, FR-3.16–FR-3.17, FR-4.5–FR-4.8, FR-5.4–FR-5.6; GR-3.4 |
| Third | Breakdown | Show the named amounts and deductions per employee or settlement component, with preparation and approval scope. | Offer earnings and deductions separately. Explain terms when first used. Keep employee PF separate from employer EPF and EPS. | FR-2.12, FR-3.14–FR-3.15, FR-4.9, FR-4.11–FR-4.13, FR-5.7; UXP-02 |
| Fourth | Period detail and calculation | Show affected months, applicable inputs, formula and code result. Bonus uses its period and proration detail. Settlement uses each component's period and basis. | Offer month detail for arrears and relevant tax calculation detail. Do not invent monthly detail for a component that has none. | FR-1.6–FR-1.11, FR-2.6–FR-2.8, FR-3.15, FR-4.10, FR-5.7–FR-5.9 |
| Fifth | Sources and rule versions | Identify authorized input records, company settings, dated rules and the approval record for the current scope. | Identify the relevant own records and applicable dated rules in plain words. Mask identifiers. | GR-2.1–GR-2.6, GR-3.5; BR-0.1–BR-0.2; FR-4.12 |

Sources are available for every amount from the first layer. The fifth layer gives fuller provenance; it does not postpone access to proof. HR receives the proposal scope and blockers first because review requires knowing what is being approved. Employees receive the net or TDS change first because FR-4.4 and FR-5.3 require that order. Their preferred detail depth remains unknown. The Payroll Admin's record-checking needs and The Pay-Change Employee's explanation needs support the distinction as a synthesis, not a tested preference. **Medium for persona interpretations; Low for preferred depth:** PS-01–PS-05; EVD-03–EVD-05, EVD-15–EVD-18; EG-04; AS-2, AS-17.

## 3. Source and rule-version pattern

For each code-produced amount or date, the explanation uses the following information from System and Calculation code. The AI does not construct missing provenance. **High for traceability requirements; Proposed content structure:** GR-3.1–GR-3.5; BR-0.1–BR-0.4; UXP-02.

- Name the amount, unit, employee scope and relevant period. Identify whether it is historical payroll, a current proposal, a scoped subtotal or an approved snapshot. (FR-1.6, FR-2.12, FR-3.14–FR-3.20, FR-4.12)
- Provide the source record type and its authorized reference, period and recorded revision where available. Identify the salary revision, attendance, payslip, declaration or recovery record actually used. Mask full identifiers. Do not imply that a bank record was read. (GR-2.1–GR-2.6; FR-4.12, FR-4.14)
- Provide the applicable rule identifier, version, effective-from date, source and relevant company setting. Distinguish the rule's effective date from its publication date. Show the historical rule for each affected month; never present one undated PF rule for all periods. (BR-0.1–BR-0.2; FR-1.11; EVD-21–EVD-26)
- On a calculation request, relay the formula, inputs, period basis, code-produced result and recorded rounding basis. Totals link to their contributing code-produced lines. Differences and reason ranking come from code. The AI does not subtract, add or rank by doing arithmetic. (FR-1.10, FR-2.12, FR-3.15; BR-0.3; GR-3.2)
- For a settlement date, include component classification, verified due-date rule and effective date, recorded trigger and calendar basis. Show the derived date only when code has returned it. Missing basis is explicit. An applicable due date is not a promised payment date. (FR-3.5, FR-3.14, FR-3.18; states Section 3; GR-4.3)
- If a required input, rule or provenance cannot support the amount, identify that limitation and stop the affected result. Do not silently reuse an old rule or show an old value as current. Historical values may be explained only with their historical scope clearly stated. (GR-3.1–GR-3.3; BR-0.4; states EC-02, EC-04)

Suggested structure: "From {authorized record reference} for {period}. The payroll calculation used {rule identifier and version}, effective from {recorded date}, with {company setting}. Show calculation for the inputs and formula." Braces are unfilled content slots, not actual records or results. (FR-1.10–FR-1.11; GR-3.5)

## 4. Certainty model

These are explanation labels derived from existing data and system conditions. They are not new workflow states. They can apply to individual periods or components at the same time. System supplies the condition and scope; the AI cannot declare its own certainty. Preparation, approval and query states retain their exact approved meanings separately. **High for guards; Proposed label wording:** GR-3.1–GR-3.4; DEC-014; states Sections 2–5.

| Certainty label | Meaning and system basis | What the user can do | Source |
|---|---|---|---|
| Complete for this scope | Required inputs and applicable verified rules are available. Code succeeded and no unresolved or unusual dependency prevents reliance on this scoped result. This says nothing about HR approval or payment. | Request details. Authorized HR can review only a scope the System marks Ready for review. Employees can question a result. | GR-3.2–GR-3.5; FR-1.13–FR-1.16; states Sections 2–3 |
| Incomplete | A required record, input, usable result or dependency is missing. A known subtotal can exist, but a dependent full total cannot. | HR supplies request details or requests authoritative correction. Employee can choose supported periods or request a query draft. | FR-1.12, FR-2.13, FR-3.17, FR-4.15, FR-5.12; GR-3.3 |
| Rule not verified | A required applicable rule, version, source, effective date, classification or permitted hold basis is absent or not verified. The affected result is blocked. | Authorized HR seeks verified configuration and source correction. Recalculate only after System accepts a usable basis. | BR-0.1–BR-0.4; FR-3.5; states EC-02 |
| Needs HR decision | System flags ambiguous eligibility or a review issue requiring authorized HR judgment. This does not allow HR to replace a missing rule with a guess. | HR reviews the records and valid rule basis. An employee can prepare a factual query for HR. | FR-3.16; GR-3.3–GR-3.4, GR-6.1–GR-6.2 |
| Cannot explain from available payroll data | Code and authorized records do not establish the cause of a discrepancy, or the user disputes the result. Known figures do not prove an explanation. | Review known evidence and request a Flow 6 draft. Sending still needs Employee confirmation. | FR-4.14–FR-4.15, FR-5.12, FR-6.3–FR-6.7; GR-1.3, GR-3.4 |

When several labels apply, lead with the blocking condition and name its scope. For example, Rule not verified can explain why a component is Incomplete. Show Needs HR decision without concealing a missing rule. A confirmed component and an unresolved component remain distinct. Calculation error and Loading remain the existing system conditions, explained in the [failure patterns](approval-failure-handling.md). Held, Not applicable, Approved and ready for payroll, and the query statuses remain lifecycle labels rather than confidence labels. (FR-3.14–FR-3.20; GR-3.3; states Sections 2–5)

No percentage score is used. The allowed inputs provide facts about availability, verification, computation and approval. They provide no measured probability of answer correctness. A language model rating itself would not establish these facts and could conceal the need for a record or HR decision. **Proposed reasoning, not a research finding:** GR-3.1–GR-3.4; EVD-31; EG-07. Label comprehension remains **Assumption, AS-16**.

## 5. Code result vs AI explanation

Describe amounts and dates as "Payroll calculation result" and prose as "AI explanation of that result." System identifies the record version and scope. The AI can paraphrase verified reasons but cannot create a formula, numeric difference, eligibility result, reason ranking or due date. If requested detail is missing from the code result, state the gap and seek the existing authorized recovery path. (GR-3.1–GR-3.5; BRD C-5; flows Section 2)

Code-produced means traceable, not automatically correct, complete or approved. The explanation must still flag unusable inputs and unexpected values. A statement uses the approved snapshot and identifies its approval scope; later drafts do not overwrite it. Security checks still govern follow-up source requests. (UXP-01, UXP-04, UXP-07; FR-1.12, FR-2.14, FR-3.17; DEC-011, DEC-014)

## 6. AI identity and limits

Suggested introduction: "I am HCM One's AI payroll assistant. I explain payroll records and payroll calculation results. I can help prepare a proposal or a query for you to review. I cannot approve a change, apply it or pay it. I send a query only after you confirm." The introduction explains capability; it is not evidence of user trust. **Proposed wording:** GR-1.1–GR-1.3, GR-3.2; AS-3, AS-4.

For Employees, add the relevant limit: "I can use only your own payroll records. I cannot check your bank credit or give personal tax, legal or financial advice." For HR, state that only authorized employees are accessible. Do not claim future pay, universal legal compliance or access to external records. This is a fictional payroll demo with simplified rules. (GR-2.1–GR-2.6, GR-4.1–GR-4.3, GR-8.1; FR-4.14; BRD 7, 12)

## 7. Patterns for A06-01, A06-05, A06-07, A06-09

All wording is Proposed. Requirements have High confidence as explicit requirements. Suitability and trust benefits are untested; AS-4, AS-16 and AS-17 apply.

### A06-01: Hike proposal
- **Purpose:** Help HR understand and review the current hike proposal.
- **Structure:** Identify employee, period, version and proposal status. Relay the confirmed old and new salary and effective date from F1-05. Give code-produced gross arrears, PF change, TDS and expected net. Explain affected months and deductions. Offer each month's old amount, new amount, difference, formula, sources and rule dates. End with the existing review choices for the valid current scope.
- **Rules:** Flag missing or unusual months before totals. Do not complete a total from a subset. Treat employee PF and employer EPF and EPS separately. The proposal is not an applied salary change or a payment. Confirmation of request details is not approval.
- **Source IDs:** FR-1.3, FR-1.6–FR-1.16; GR-1.1–GR-1.2, GR-3.1–GR-3.5; UXP-01, UXP-02, UXP-04; PS-01, PS-04; EVD-01–EVD-05.

### A06-05: Settlement components, net summary and statement
- **Purpose:** Explain the reconciliation and preserve the distinction between known amounts, readiness and unresolved work.
- **Structure:** Identify version, employee and last working day. List code-produced payables, recoveries and TDS. State whether the final net is complete. Explain each component's basis, applicable due date, preparation status, approval status and any permitted hold. Offer its source and calculation. After approval, use the scoped snapshot for the employee statement described in Section 8.
- **Rules:** Unknown is not zero. A fully known negative net is recoverable from the employee; it is not money paid. A complete net including a known held amount does not mean that amount is ready for release. An unknown component or dependent tax makes the final net incomplete. Do not use a missing hold basis to hold everything.
- **Source IDs:** FR-3.5–FR-3.21; BR-6.7; GR-1.1, GR-3.3–GR-3.5; UXP-02, UXP-04–UXP-06; PS-03–PS-05; EVD-61, EVD-68–EVD-69; DEC-008, DEC-014, DEC-015.

### A06-07: Net change and main reason
- **Purpose:** Answer the Employee's pay-change question before requiring payroll terminology.
- **Structure:** Name both payslip periods. Lead with code-produced take-home difference, then the biggest code-established reasons in order. For each, say what changed, why and its recorded effective period. Offer earnings and deductions, month detail, terms and sources. Ask whether the explanation answers the question before drafting a query.
- **Rules:** Use only the Employee's own payroll. If salary components did not change, say so and check the recorded deduction and net results separately. Do not invent a cause to make a sum match. Explain employer shares separately from deductions from the Employee's pay. Future pay is not promised.
- **Source IDs:** FR-4.2–FR-4.17; GR-2.2, GR-3.1–GR-3.5, GR-4.3; UXP-02, UXP-03, UXP-06; PS-02, PS-03; EVD-09, EVD-13, EVD-15–EVD-18.

### A06-09: TDS reason and calculation
- **Purpose:** Explain the recorded TDS change and let the Employee check its basis.
- **Structure:** Lead with the code-produced TDS change and periods. Name only reasons supported by code and records, such as accepted or missing declarations, a hike or a bonus. On request, relay projected annual income, applied deductions and exemptions, yearly tax, tax already deducted, remaining tax and months, and the formula result. Identify selected regime, rule version, effective date and declaration statuses.
- **Rules:** Explain that payroll deducts expected yearly tax in monthly parts when asked. Do not recommend a regime or investment. If tax inputs or GAP-05 cases lack a rule, stop that computation; do not invent a refund or a remaining month count.
- **Source IDs:** FR-5.3–FR-5.12; BR-4.1–BR-4.4, BR-0.4; GR-3.1–GR-3.5, GR-4.1; UXP-02, UXP-03, UXP-06; PS-02, PS-04; EVD-10; GAP-05.

## 8. Settlement statement explanation (DEC-015)

This is employee-facing wording within Flow 3's output after HR approves a valid scope. It is not a new Employee settlement flow. Follow-up questions use Flow 6 under its existing identity and access checks. Employee portal access after the last working day remains out of scope. No delivery channel is invented. **High for approved scope:** DEC-015; FR-3.20; GR-2.1–GR-2.5.

The statement follows this content order:

1. Identify the employee with masked identifiers, settlement version, recorded last working day and the HR approval reference, scope and time. Say "This statement explains the scope approved by HR. Approval does not mean payment." (FR-3.2, FR-3.19–FR-3.21; GR-1.1, GR-2.6; DEC-014)
2. Give the code-produced final net and whether it is payable or recoverable only when the full basis is known. Otherwise say "The final net is incomplete because {recorded unresolved component} is not yet known." Name each scoped subtotal as incomplete rather than treating it as final. (FR-3.14, FR-3.17; BR-6.7; GR-3.3)
3. Explain each payable, recovery and TDS line in simple words. For recoveries, identify the recorded obligation, relevant period, waiver status where relevant, permitted rule, formula and source. Say "This is an amount recorded as recoverable" rather than "This has been collected." Do not infer an obligation from a net figure alone. (FR-3.6–FR-3.15; BR-6.5–BR-6.7; PS-03; PP-21; EVD-68–EVD-69)
4. Keep preparation and approval separate on every relevant component. For a verified permitted hold, name the recorded reason and its verified basis: "This component is held for {recorded dependency} under {verified rule}. Its approval status is {recorded status}." Say which dependency remains open. Do not imply that all wages are held. (FR-3.5, FR-3.14, FR-3.18–FR-3.20; UXP-05; states Section 3)
5. For an unresolved line, name the missing record, eligibility decision, classification or rule basis. State that its amount or due date is not established where applicable. Preserve it even when other components are approved. Say who must review it, without setting an unsupported deadline. (FR-3.16–FR-3.20; GR-3.3–GR-3.4; PS-05)
6. Provide code-derived applicable component due dates only from verified bases. Identify the rule and trigger. Say "This is the applicable recorded due date. This assistant has not made a payment." Never infer a common date for every component. (FR-3.14, FR-3.18; GR-1.1, GR-4.3; states Section 3)
7. Offer the existing query path for a disputed or unexplained line, including only relevant evidence and requiring Employee confirmation. Keep later corrections linked to a new reviewed version; do not replace the approved snapshot. (FR-6.1–FR-6.13; BR-7.3; states EC-18; DEC-015)

**Assumption, Low:** Whether this structure prevents confusion between an approved component, the net and payment remains AS-14. Whether evidence increases trust remains AS-4. EVD-68 is one complaint, not proof of preferred statement detail. (EG-27)

## 9. Assumptions and open questions

- **Existing assumptions:** AS-3, AS-4 and AS-14 remain unvalidated. No trust, acceptance or comprehension benefit is claimed as proven. (EVD-30–EVD-31, EVD-35, EVD-41; EG-06–EG-07, EG-27)
- **New Assumption, Low, AS-16:** Users can distinguish data certainty labels from approval and payment states when both are stated with their scope. Validate in Agent 08 with real HR users and Employees on fictional complete, incomplete, disputed and approved tasks. (GR-3.3–GR-3.4; UXP-04–UXP-05; EG-04, EG-07)
- **New Assumption, Low, AS-17:** Role-specific layered explanations and one clarifying question at a time help users understand the result and supply missing request details. Test detail choices, term understanding and correction behavior in Agent 08. Do not interpret this as a measured trust gain. (FR-1.2, FR-4.4–FR-4.13; personas; EG-04)
- **Open, Low:** GAP-01, GAP-02, GAP-03 and GAP-05 need verified rules configuration before build. Component classification, permitted holds and due-date triggers remain unverified. No reported research deadline or rate is configured here. (BR-0.1–BR-0.4; EG-25; states Section 9)
- **For Agent 05, resolved:** Resolved by DEC-019. The statement is available to the employee in HCM One while they still have access. Delivery after the last working day uses the company's existing exit process, outside HCM One. Follow-up questions use Flow 6 only while the employee has access. No new channel or portal is added. (DEC-015; FR-3.20, FR-6.1–FR-6.13; DEC-019)
- **For Agent 05, open, Low:** Target-company ownership of a post-approval correction remains unspecified. Use the approved versioned correction path without naming a new owner or workflow. (states EC-18; EG-28; DEC-014)
