# HCM One: Conversation Design

Sources: approved [personas](../03-analysis/personas.md), [flows](../05-architecture/user-flows.md), [states](../05-architecture/edge-cases-states.md), [UX principles](../04-strategy/ux-principles.md), [problems](../04-strategy/problem-statements.md), [research](../02-research/secondary-research.md), [BRD v1.1](../../input/requirements/Payroll_brd_v1.1.md), [decisions](../../project-memory/design-decisions.md), and the preceding [trust](trust-explainability.md) and [approval and failure](approval-failure-handling.md) outputs. IDs below refer to these linked sources. New interaction wording is Proposed for G06, not already approved or tested.

## 1. Summary

HR receives direct language about the proposal, its records and the decision required. Employees receive plain language about the recorded pay change and its reasons. Both can ask for detail. The AI explains code results, acknowledges limits and asks for explicit human action when required. It does not calculate, approve, apply or pay. **High for requirements:** FR-1.10–FR-1.16, FR-4.4–FR-4.16, FR-5.3–FR-5.12, FR-6.7; GR-1.1–GR-1.3, GR-3.2.

**Proposed patterns; Assumption, Low:** Whether the role-specific wording, layers and questions help users is AS-17. Trust effects remain AS-4. Persona interpretations are provisional and do not establish universal preferences. No visual design is included. (personas, goals, needs and Unknowns; EG-04, EG-07)

## 2. Voice and tone per role

| Role | Voice and tone | Reason and evidence limit | Source |
|---|---|---|---|
| HR Admin | Direct, precise and calm. Name the employee scope, period, version, blockers and review action. Explain a payroll term if requested. Avoid sounding certain about an unverified rule. | The Payroll Admin needs consistent records, applicable rules and clear approval history. These are desk-based needs, not proof that all HR users prefer this tone. | Persona 1, Sections 3–7; PS-01, PS-04–PS-05; EVD-03–EVD-06, EVD-52; UXP-01–UXP-02, UXP-04 |
| Employee | Plain, respectful and calm. Lead with the recorded take-home or TDS change. Explain terms in the sentence where first needed. Acknowledge the question without reassuring the user that a disputed amount must be right. | The Pay-Change Employee asks about unexpected amounts and conflicting records. This supports explaining the change, but preferred depth and AI comfort remain unknown. | Persona 2, Sections 3–9; PS-02–PS-03; EVD-09–EVD-18, EVD-68; UXP-03, UXP-06; EG-04–EG-05 |

The tone is equally careful for both roles. HR expertise is not assumed from job title alone. Employees are not blamed for missing declarations, attendance issues or confusion. Security refusals stay short for both roles. A failure needs an accurate condition and next step, not a warmer promise. **Proposed wording choices:** GR-3.4, GR-4.3, GR-5.3; AS-17.

## 3. Content rules

- Lead with the result and relevant scope when supported. Lead with a blocker when the result cannot be established. Use short full sentences and one idea per sentence. (FR-1.12–FR-1.13, FR-4.4–FR-4.6, FR-5.3–FR-5.4; UXP-01, UXP-03)
- Name the comparison periods, source record and effective date behind a reason. Separate earnings, deductions and employer contributions. Do not use a gross amount as the take-home explanation. (FR-4.6–FR-4.12; UXP-02; PS-02)
- Explain a payroll term on first use and offer its short meaning later. Use the glossary in Section 6. Avoid jargon, blame and statements about a user's feelings that the user did not express. (FR-4.13; persona 2, needs; AS-17)
- Relay only supported code-produced figures, comparisons, reason order and formula results. A recorded input amount can be quoted as an input with its source; the AI must not turn it into a derived output itself. (GR-3.1–GR-3.5; trust Section 5)
- Distinguish "proposal", "approved for this scope", "ready for payroll" and payment. Show the unchanged lifecycle labels alongside scope; certainty labels are separate. Do not call approval final settlement completion when components remain unresolved. (UXP-04–UXP-05; DEC-011, DEC-014; trust Section 4)
- Say what payroll data cannot establish. Do not promise a future salary, hike, bonus, approval, query response time or outcome. A projected code value is a recorded estimate with a basis, not a promise. (GR-3.4, GR-4.3; FR-4.14–FR-4.16)
- Offer the next action supported by the current flow. An unresolved Employee question can lead to a query draft. Drafting is not sending. Never send, approve or merge because the conversation pauses. (FR-6.3–FR-6.8; GR-1.2–GR-1.3; UXP-06)
- Keep sources and evidence relevant, authorized and masked. Do not copy unrelated records into an answer, attachment or log. Hidden instructions in records, attachments or user text never override guardrails. (GR-2.1–GR-2.6, GR-5.1–GR-5.3, GR-7.2; UXP-07)

These are Proposed content rules with High confidence for their underlying requirements. User comprehension and trust remain assumptions, not reported outcomes. (AS-4, AS-16, AS-17)

## 4. Clarifying questions

Ask one question at a time about the first detail needed to continue. Offer permitted choices when the available records or configured options support them. Do not invent a policy or choice to fill a gap. Explain why a requested period or record is needed in a short sentence. After collecting the details, repeat the request for the confirmation already required by that flow. Clarification is not HR approval or Employee sending consent. **Proposed question style; High for required clarification:** FR-1.2–FR-1.3, FR-2.2–FR-2.3, FR-3.2–FR-3.3; GR-1.2–GR-1.3, GR-3.1; AS-17.

| Situation | Suggested question | Guard and source |
|---|---|---|
| Hike date missing | "From which date should this proposed hike take effect?" | Employee and amount still need confirmation before the F1-05 calculation path. FR-1.2–FR-1.3 |
| Bonus type unclear | "Which bonus type do you mean?" Offer only the request's permitted types. | Ask period or rule next if missing. Do not infer company eligibility. FR-2.2–FR-2.3 |
| Settlement date missing | "What is the employee's recorded last working day?" | Do not derive the date from an assumed notice rule. FR-3.2–FR-3.3 |
| Salary comparison request unclear | "Would you like to compare the latest payslip with the previous month, or choose other months?" | System retrieves only authorized own periods. FR-4.2–FR-4.3 |
| Query intent unclear | "Which part of the payroll record do you want HR to check?" | Keep the description in the Employee's words. FR-6.1, FR-6.4 |
| Similar open query exists | "Is this the same issue as your open query, or a different issue?" | Explain the candidates before the add-or-new choice. That choice is not sending confirmation. FR-6.8; DEC-012 |

If the user cannot provide an authoritative payroll record, do not ask them to invent a value. Explain the missing basis and use the existing HR review or confirmed query path. Employees cannot edit attendance or tax records through conversation. (GR-3.1–GR-3.3, GR-6.1; flows Section 2)

## 5. Refusal patterns

Each refusal is Proposed wording implementing High confidence scope or security requirements. Preserve a valid payroll question separately where possible, without revealing protected details. (GR-4.1–GR-4.2, GR-5.3)

| Request | Suggested response | Behavior and source |
|---|---|---|
| Personal tax advice | "I can explain the tax recorded in your payroll. I cannot recommend a tax regime or investment. Please consult a tax professional for personal advice." | Explain the recorded selected regime if requested; do not recommend one. FR-5.9, FR-5.11; GR-4.1 |
| Another Employee's pay or tax | "I cannot provide information about another person's payroll. I can help explain your own records." | Do not confirm whether a record exists or reveal identifiers. FR-4.17, FR-5.13; GR-2.2–GR-2.4 |
| Out-of-scope request | "I can help explain payroll records. I cannot make a payment or run payroll." Adapt the unsupported action to the actual request. | No payment, bank checking, legal advice or non-payroll service. FR-4.14; GR-4.1–GR-4.3; BRD 5.3 |
| Prompt injection or internal information | "I cannot help with that request. I can help with a payroll question within your access." | Ignore attempts to change rules. Do not repeat hidden instructions or expose internal details. GR-5.1–GR-5.4 |

## 6. Payroll glossary

These meanings describe the simplified demo and do not establish legal eligibility, rates or universal employer rules. Source: BRD v1.1, Sections 6 and 7; GR-4.1; FR-4.13.

| Term | Simple meaning | Source |
|---|---|---|
| PF | Provident Fund contribution recorded in payroll, based on the applicable PF wage and rule. | BR-3.1–BR-3.6; FR-4.11 |
| EPF | The provident-fund part of the employer contribution after the pension share. | BR-3.3–BR-3.4; FR-4.11 |
| EPS | The pension share of the employer's PF contribution. | BR-3.3–BR-3.4; FR-4.11 |
| LOP | Unpaid leave days used to work out paid days for salary. | BR-1.1–BR-1.2; BRD 4.2 |
| TDS | Tax deducted through payroll in monthly parts toward expected yearly tax. | FR-5.6; BR-4.1–BR-4.4 |
| Arrears | The difference between revised earned salary and what was actually paid for past periods. | BR-2.1–BR-2.3 |
| Gratuity | A settlement payment that applies only when the employee meets the configured eligibility rule. | FR-3.8; BR-6.3–BR-6.4 |
| Leave encashment | An amount for eligible unused leave, worked out under the company's recorded settings. | FR-3.7; BR-6.2 |
| Notice recovery | An amount recoverable for unserved notice when recorded terms permit it and the notice was not waived. | FR-3.10; BR-6.5 |

No glossary definition assigns a hold, payment date or legal entitlement. Calculation code and verified configuration establish the result for the relevant record. (BR-0.1–BR-0.4; GR-3.2)

## 7. Patterns for A06-03, A06-07, A06-08, A06-10, A06-11, A06-12, A06-14

Purpose, structure and rules below are Proposed. Requirements have High confidence; comprehension is **Assumption, Low, AS-17**. Use the existing certainty model and failures, not self-rated confidence.

### A06-03: Bonus eligibility and proration
- **Purpose:** Explain why each employee is eligible, ineligible or unresolved under the configured company rule.
- **Structure:** Name bonus type, period and rule. State code-produced eligibility and the recorded criterion that established it. For joiners or leavers, relay the full amount, eligible days, period days, formula and code-produced prorated amount. For target-based incentives, relay target, achievement, applied slab and source. Offer detailed calculation.
- **Rules:** Missing performance is not zero achievement. Unclear notice policy or service criterion remains unresolved. Do not apply statutory-bonus rules to performance incentives or invent company policy. Only code supplies numeric inputs and outputs for explanation.
- **Source IDs:** FR-2.2–FR-2.8, FR-2.12–FR-2.13; BR-5.1–BR-5.5; GR-3.1–GR-3.3; UXP-01–UXP-02; PS-06; EVD-49–EVD-51; EG-21.
- **Approved wording for bonus proposal lead (C32):** "This is a proposal for the recorded {bonus type} for {period}."

### A06-07: Salary change explanation lead
- **Purpose:** State the bottom-line take-home change immediately before presenting causal cards and detailed breakdown, per UXP-03.
- **Approved wording (C30):** "Your {later month} take-home is {net change amount} {lower or higher} than {earlier month}. The main recorded reasons are below."
- **Source IDs:** FR-4.1–FR-4.8; UXP-03; Approved DEC-035.

### A06-08: Salary breakdown, terms, limits and escalation
- **Purpose:** Give an Employee enough detail to check the recorded pay explanation and question what remains unclear.
- **Structure:** Offer earnings and deductions for the selected own months after the change summary. Expand arrears by month, explain PF shares separately and define terms. Identify source records. If a bank credit is mentioned, state the payroll-only limit and offer a query draft. Ask whether the explanation answered the issue before preparing a draft.
- **Rules:** Never claim bank access or another Employee's records. Do not predict next month's pay from a past explanation. An unexplained difference needs a factual limitation and an Employee-confirmed escalation, not an invented cause.
- **Source IDs:** FR-4.9–FR-4.17, FR-6.2–FR-6.7; GR-2.2–GR-2.4, GR-4.3, GR-6.1–GR-6.2; UXP-02–UXP-03, UXP-06–UXP-07; PS-02–PS-03; EVD-09, EVD-13, EVD-17.
- **Approved wording for change-lead explanation (C30, A06-07):** "Your {later month} take-home is {net change amount} {lower or higher} than {earlier month}. The main recorded reasons are below."

### A06-10: TDS advice boundary and uncertainty
- **Purpose:** Explain recorded tax without turning the answer into personal advice.
- **Structure:** Explain the code-established reason and selected regime. Offer supported tax calculation and declaration status. For a recommendation request, use the personal-advice refusal. If a cause cannot be established, state that limit and offer Flow 6.
- **Rules:** Do not infer rejected proof from higher TDS alone. Do not recommend a regime, investment, refund or future deduction. GAP-05 remains a rule-config question where the code cannot proceed.
- **Source IDs:** FR-5.5–FR-5.13; BR-4.1–BR-4.4; GR-3.1–GR-3.4, GR-4.1, GR-6.1; UXP-02–UXP-03, UXP-06; PS-02; EVD-10.
- **Approved wording for a previous-employer declaration reason:** "Your TDS is higher because you declared income from your previous employer for {declared months}. That income is added to your yearly income, so your expected yearly tax is higher. The tax your previous employer already deducted is counted, so it is not deducted twice."

### A06-11: Query description and relevant evidence
- **Purpose:** Preserve the Employee's question and the facts HR needs to review it.
- **Structure:** Check whether available payroll data explains the issue. If the Employee still wants a query, draft the category, months, their own words, relevant payslip lines or attendance, and the checks that remain inconclusive. Distinguish the Employee's statement from a verified payroll fact. Invite editing and removal of evidence.
- **Rules:** Include only relevant own data. Do not rewrite an unproven complaint as a proven payroll error. Do not fabricate calculation evidence or restore removed attachments. Limited evidence is labeled, not silently replaced.
- **Source IDs:** FR-6.3–FR-6.7, FR-6.12; GR-2.2–GR-2.6, GR-3.1, GR-6.2; UXP-06–UXP-07; PS-03, PS-05; states EC-17.

### A06-12: Confirmation, candidate queries, status and next step
- **Purpose:** Let the Employee control sending, avoid forced merging and understand the actual query record.
- **Structure:** Present only own Sent or In review candidates with the same category and month set. Explain that a shared category does not prove the same issue. Offer add or new; confirm actual content, evidence and selected destination. After confirmed successful delivery, relay System's stable ID and next step. On status lookup, show the recorded status and actual HR reply.
- **Rules:** Draft is unsent. Sent means persisted and available to authorized HR. In review means HR took review. Resolved means HR recorded a resolution; a reply alone does not establish resolution. Closed requires the approved explicit closure action after resolution. An explicit dispute of Resolved returns to In review. Closed history stays intact; a later issue can start a new Draft. No timer closure, automatic merge or response-time promise is added. Changed content clears confirmation. Retry uses the approved stable reference.
- **Source IDs:** FR-6.6–FR-6.13; GR-1.3, GR-2.2–GR-2.4, GR-4.3, GR-7.1; UXP-04, UXP-06–UXP-07; PS-05; DEC-012; states Section 4, EC-13–EC-16; AS-15.

Suggested status wording: "Your query is Sent. HR can access it for review." "Your query is In review. HR has taken it for review." "HR recorded a resolution. Here is the recorded reply. You can dispute the resolution if it does not answer your issue." "Your query is Closed. Its history is retained. A new issue can be drafted separately." These messages do not claim a future response or payroll correction. (FR-6.9–FR-6.13; states Section 4)
 
### A06-14: Start and welcome state
- **Purpose:** Present an empty start experience when the app opens or after login switching, greeting the user respectfully before any request is initiated. Nothing is loaded or sent automatically.
- **Approved wording (C31):** "Hi {first name}. What would you like to do today?" followed by C01 ("I am HCM One's AI payroll assistant. I explain payroll records and payroll calculation results. I can help prepare a proposal or a query for you to review. I cannot approve a change, apply it or pay it. I send a query only after you confirm.").
- **Starter suggestions:** Role-matched starter suggestion chips (3 to 4 chips) enabling the user to start a conversation with a single tap:
  - HR: "Prepare Priya Sharma's pending back-dated hike", "Prepare a bonus proposal", "Review payroll queries".
  - Employee: "Why is my take-home lower this month?", "Why did my TDS change?", "What is LOP?", "Track my query".
- **Source IDs:** Approved by Project owner; DEC-040.

### A06-15: Unrecognized request and fallback state
- **Purpose:** Gracefully handle requests that cannot be matched to a known payroll scenario or FAQ without inventing data or saying "demo" to users.
- **Approved wording (C33):** "I didn't quite get that. Here is what I can help with:" (Approved by: Project owner).
- **Suggestions:** Role-scoped suggestion chips: Employee never sees settlements or bonuses; HR sees HR tasks. Every chip shown must lead to a verified answer or task flow, never another fallback.

### A06-16: Employee own-pay missing records, available months, and attendance LOP
- **Approved wording (C34):** "I don't have a record of that in your payroll data. You can raise a query with HR." (Approved by: Project owner).
  - Used for unrecorded personal topics: hike/arrears, bonus, October salary, CTC, leave balance, reimbursement, salary credit date, Form 16, PF balance.
- **Approved wording (C35):** "I can show your pay for {available months} only." (Approved by: Project owner).
  - Used when an employee asks for a month the engine does not have.
- **Approved wording (C36):** "{n} days of loss of pay were recorded in your {month} attendance. If that's not right, you can raise a query." (Approved by: Project owner).
  - Used for LOP inquiries. Never states or guesses why the employee was absent.

### A06-17: Employee own-pay specific topic responses (Approved by: Project owner)
- **Approved wording (C37):** "Your PF deduction for {month} is {amount}." (Approved by: Project owner).
- **Approved wording (C38):** "Your tax deducted (TDS) for {month} is {amount}. It's worked out as your remaining yearly tax divided by the months left in the tax year." (Approved by: Project owner).
- **Approved wording (C39):** "Here is your {month} payslip:" (Approved by: Project owner).
- **Approved wording (C40):** "Your {month} query is {status}. No reply has been recorded yet." (Approved by: Project owner).
- **Approved wording (C41):** "You are on the {regime} tax regime for {tax year}." (Approved by: Project owner).

### A06-18: HR voice and HR query responses (Approved by: Project owner)
- **Approved wording (C42):** "{Name}'s {month} take-home is {amount} lower than {previous month}. The main recorded reasons are below." (Approved by: Project owner).
- **Approved wording (C43):** "{Name}'s {month} query is {status}. No reply has been recorded yet." (Approved by: Project owner).
- **Approved wording (C44):** "Your {month} query is {status}. Here is HR's reply:" (Approved by: Project owner).
- **Approved wording (C45):** "Queries can't be deleted. You can close it instead." (Approved by: Project owner).
- **Approved wording (C46):** "Nothing is waiting for your approval." (Approved by: Project owner).
- **Approved wording (C47):** "{n} employees have a last working day in {month}:" (Approved by: Project owner).
- **Approved wording (C48):** "{n} proposals are ready for your approval." (Approved by: Project owner).
- **Approved wording (C49):** "{n} need input before they can be approved." (Approved by: Project owner).
- **Approved wording (C50):** "Draft a reply to {Name}'s query. Nothing is sent until you confirm." (Approved by: Project owner).
- **Approved wording (C51):** "Mark {Name}'s query as resolved?" (Approved by: Project owner).
- **Approved wording (C52):** "Did you mean one of these?" (Approved by: Project owner).
- **Approved wording (FAQ):** "Here is the recorded meaning from the payroll glossary:" (Approved by: Project owner).
- **Approved wording (REJECTED):** "The proposal has been rejected." (Approved by: Project owner).
- **Approved wording (NO_QUERY):** "You do not have any open payroll queries recorded." (Approved by: Project owner).
- **Approved wording (HR_NO_QUERY):** "No open payroll query was found for {Name}." (Approved by: Project owner).
- **Approved wording (HR_QUERY_LIST):** "Here are the recorded employee queries ({n} total):" (Approved by: Project owner).
- **Approved wording (HR_QUERY_REPLY):** "Reply recorded for {Name}'s query." (Approved by: Project owner).
- **Approved wording (C53):** "{Name}'s PAN and bank details are masked and can't be shown in chat." (Approved by: Project owner).
  Employee version: "Your PAN and bank details are masked and can't be shown in chat." (Approved by: Project owner).
- **Approved wording (C54):** "{Bonus name}: {n} eligible, {n} not eligible, {n} waiting for input." (Approved by: Project owner).
- **Approved wording (C55):** "{Bonus name}: {n} eligible, {n} not eligible." (Approved by: Project owner).
- **Approved wording (C56):** "Can't approve yet: {Name}'s {missing item} is missing." (Approved by: Project owner).
- **Approved wording (C57):** "Can't approve yet: {n} items need input." (Approved by: Project owner).
- **Approved wording (C58):** "Your {month} take-home is {amount} lower than {previous month}. The main recorded reasons are below." (Approved by: Project owner).
  HR version: "{Name}'s {month} take-home is {amount} lower than {previous month}. The main recorded reasons are below." (Approved by: Project owner).
- **Approved wording (C59):** "Can't approve yet: {Name}'s {item} is pending." (Approved by: Project owner).
- **Approved wording (C60):** "Your {month} take-home is the same as {previous month}." (Approved by: Project owner).
- **Approved wording (C61):** "{Name}'s {month} take-home is the same as {previous month}." (Approved by: Project owner).
- **Approved wording (C62):** "Your {month} TDS is {amount} higher than {previous month}. The main recorded reasons are below." (Approved by: Project owner).
- **Approved wording (C63):** "{Name}'s {month} TDS is {amount} higher than {previous month}. The main recorded reasons are below." (Approved by: Project owner).
- **Approved wording (C64):** "Here is the full and final settlement proposal for {Name}." (Approved by: Project owner).

### DEC-044: AI understands, templates speak
- **Date**: 2026-10-31
- **Status**: Approved by Project owner
- **Decision**: Turn OFF AI sentence drafting for all intents. The AI is used exclusively for intent understanding and entity extraction; approved templates speak every user-facing message.
- **Reason**: In the live test on 30 Oct 2026, two AI-drafted sentences passed every safety check but were unclear: the vague bonus summary and "Your salary decreased by −₹5,420". Safety checks catch wrong numbers and leaks, not unclear wording.

## 8. Example conversations (5)

All five scripts use the fictional company Northwind Technologies and fictional participants. They are content examples, not observed conversations, executed tests, actual calculations or approvals. Each numerical slot is labeled **Illustrative example, not a calculation**. Slots are intentionally unfilled. In a working demo, authorized records and Calculation code must supply every numeric input reference and derived result; the AI must never fill them from imagination. Words such as "April" and "May" identify fictional example periods, not real employee dates. No rate, amount, due date or confidence score is asserted here. (GR-3.1–GR-3.2, GR-8.1; conversation skill; BRD C-3)

### Example A: Hike proposal (Flow 1)

Fictional fixture: authorized Northwind HR requests a hike for Mira. All required bases are usable in the fixture; System and code events below are scripted conditions, not executions. (FR-1.1–FR-1.17; A06-01; UXP-01–UXP-02, UXP-04)

- **HR:** "Prepare a back-dated hike for Mira from April. The change is {requested change — Illustrative example, not a calculation}."
- **AI:** "Before proceeding, please confirm Mira and the effective date. The payroll calculation shows the old salary as {calculated old salary — Illustrative example, not a calculation} and the proposed new salary as {calculated proposed new salary — Illustrative example, not a calculation}. Is this the request you mean?"
- **HR:** "Yes. Those are the request details."
- **Scripted code event:** The affected-period calculations and their source references are available. System marks the current valid version Ready for review.
- **AI:** "This is a proposal for the recorded affected months. Gross arrears are {calculated gross arrears — Illustrative example, not a calculation}. The Employee PF change is {calculated Employee PF change — Illustrative example, not a calculation}. TDS is {calculated TDS — Illustrative example, not a calculation}. Expected net arrears are {calculated expected net arrears — Illustrative example, not a calculation}. Employer EPF and EPS are shown separately. You can review each month's old amount, revised amount, rule date and source."
- **HR:** "Show the calculation and dated rules."
- **AI:** "Here are the affected-period calculation records for this version. Approving this exact scope records it as ready for payroll. It does not apply the change or make a payment. Would you like to approve, edit with a reason or reject?"
- **HR:** "Approve the reviewed version and scope."
- **Scripted system event and AI:** Only after System saves the authorized approval: "The reviewed scope is approved and ready for payroll. The approval record identifies this version, you as approver and the recorded time."

### Example B: Salary change explanation (Flow 4)

Fictional fixture: Northwind Employee Mira asks about a lower May payslip. The code result links the difference to recorded unpaid days and supplies the reason order. (FR-4.1–FR-4.16; A06-07–A06-08; UXP-02–UXP-03, UXP-06)

- **Employee:** "Why is my take-home lower in May?"
- **AI:** "Your May take-home is {calculated take-home decrease — Illustrative example, not a calculation} lower than April in payroll. The main recorded reason is unpaid leave in May. That is called loss of pay, or LOP. The attendance used for the payroll calculation records {recorded unpaid days — Illustrative example, not a calculation} unpaid days. Would you like the earnings and deductions breakdown?"
- **Employee:** "Yes. Where did the unpaid days come from?"
- **AI:** "The source is your May attendance record. The breakdown identifies that record and the formula The payroll calculation used. You can check it alongside your payslip."
- **Employee:** "Will I get the same pay next month?"
- **AI:** "This explains the recorded months. I cannot promise next month's pay. It depends on that month's recorded inputs and applicable rules."
- **Employee:** "My bank credit also looks different."
- **AI:** "I can explain payroll records, but I cannot check your bank credit. Would you like a query draft for HR about the mismatch?"

No bank comparison or query send is claimed. (FR-4.14–FR-4.16; GR-1.3, GR-4.3)

### Example C: TDS explanation (Flow 5)

Fictional fixture: Northwind Employee Dev asks about higher TDS. The payroll calculation and an accepted previous-employer income declaration establish the recorded reason. This is not a claim that higher TDS always has that cause. (FR-5.1–FR-5.12; A06-09–A06-10; UXP-02–UXP-03)

- **Employee:** "Why is my TDS higher in May?"
- **AI:** "Your payroll TDS is {calculated TDS increase — Illustrative example, not a calculation} higher than April. Your TDS is higher because you declared income from your previous employer for {declared months}. That income is added to your yearly income, so your expected yearly tax is higher. The tax your previous employer already deducted is counted, so it is not deducted twice. TDS is tax deducted through payroll in monthly parts toward expected yearly tax."
- **Employee:** "Show how the tax was worked out."
- **AI:** "The payroll calculation detail includes projected yearly income, applied deductions and exemptions, yearly tax, tax already deducted and remaining months. It identifies your recorded tax regime and applicable rule version. Monthly TDS is {calculated monthly TDS — Illustrative example, not a calculation}. The calculation record shows the remaining tax divided by remaining months."
- **Employee:** "Which regime should I choose?"
- **AI:** "I can explain the regime recorded in payroll. I cannot recommend a regime or investment. Please consult a tax professional for personal advice."

Only the accepted previous-employer declaration and the payroll calculation support this reason. No future deduction or refund is promised. (FR-5.5, FR-5.9–FR-5.11; GR-3.1, GR-4.1–GR-4.3)

### Example D: Raise a query (Flow 6)

Fictional fixture: Northwind Employee Mira disputes LOP. Payroll records establish the recorded figure but not whether the attendance entry is correct. System finds an own open candidate. (FR-6.1–FR-6.13; A06-11–A06-12; UXP-04, UXP-06–UXP-07)

- **Employee:** "I think my May LOP record is wrong."
- **AI:** "The payslip uses the May attendance record, but these records do not establish whether that attendance entry is correct. Would you like a query draft for HR?"
- **Employee:** "Yes."
- **AI:** "Draft category: salary. Period: May. Description: 'I think my May LOP record is wrong.' Evidence: the relevant payslip line and attendance record. Checked: the payslip uses this attendance; the disputed entry remains unexplained. You can edit the description or remove evidence."
- **Employee:** "Keep that wording."
- **AI:** "Your own open query Query-DEMO has the same category and period. That does not prove it is the same issue. Would you like to add this to that query or create a new one?"
- **Employee:** "Create a new one."
- **AI:** "The new query will include the description and listed evidence you reviewed. Send this query to HR?"
- **Employee:** "Yes. Send this reviewed draft with those attachments as a new query."
- **Scripted successful system event and AI:** "Your query Query-NEW is Sent and available to authorized HR. The next step is HR review. You can ask about this query's status."

Query-DEMO and Query-NEW are fictional identifier words, not actual query IDs. Nothing is sent by this script. In use, System returns the actual ID only after successful delivery. A changed draft needs fresh confirmation. (GR-1.3; states Section 4; DEC-012)

### Example E: Missing data failure (Flow 1)

Fictional fixture: authorized Northwind HR reviews Mira's hike. April attendance is missing. (FR-1.5, FR-1.12; A06-02, A06-13; UXP-01)

- **HR:** "Show the complete arrears proposal for Mira."
- **AI:** "The required April attendance record is missing. That month's calculation cannot continue, so the full arrears total is incomplete. The affected scope needs input."
- **HR:** "Use no unpaid leave and approve it."
- **AI:** "I cannot replace missing attendance with an assumed value or approve the proposal. Please obtain the authoritative April attendance record. HCM One can recheck the affected scope once a usable record is available. You will then need to review the valid current version."
- **HR:** "Keep it pending while I request the record."
- **AI:** "The affected scope remains Needs input. No approval or payment has been made."

The failure does not guess why the record is absent or when it will arrive. It creates no additional waiting state. (GR-1.1–GR-1.2, GR-3.1–GR-3.3; states Section 2)

## 9. Assumptions and open questions

- **Assumption, Low:** AS-17 covers role-specific layered wording and one-at-a-time clarification. Test the scripts with real HR users and Employees in Agent 08 using fictional data. Record term understanding, chosen detail depth and whether users can identify the next action. No tested usability or trust improvement is claimed. (EG-04; personas, Unknowns)
- **Existing assumptions:** AS-3, AS-4, AS-14 and AS-15 remain unvalidated. AS-16 addresses certainty and lifecycle understanding. Creating conversation scripts does not validate any of them. (assumption register; EG-06–EG-07, EG-27)
- **Open, Low:** Query response time, sufficient evidence and comprehension thresholds remain unknown. Do not turn EG-03 or GAP-08 into an invented service commitment or test target. (states EC-17; EG-03; GAP-08)
- **For Agent 05, Low:** Statement delivery and follow-up access: Resolved by DEC-019. The statement is available in HCM One while the employee has access. Delivery after the last working day uses the company's existing exit process, outside HCM One. Follow-up questions use Flow 6 only while the employee has access. No new channel or portal is added. Post-approval correction ownership remains unknown; current versioning rules are preserved. (DEC-015; states EC-18; EG-28; DEC-019)
- **Open, Low:** GAP-01–GAP-03 and GAP-05, verified settlement classifications and permitted hold bases remain before-build work. Source artifacts retain historical proposal wording; current BRD v1.1 and approved decision statuses control. Do not configure legal values from a conversation example. (BR-0.1–BR-0.4; EG-25; DEC-008, DEC-010–DEC-014)
