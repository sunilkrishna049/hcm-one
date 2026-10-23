# HCM One: UX Principles

Sources: [problem statements](problem-statements.md), the approved [personas](../03-analysis/personas.md), [pain points](../03-analysis/pain-points.md), [research](../02-research/secondary-research.md) and [BRD guardrails](../../input/requirements/Payroll_brd.md). These principles are proposed for G04 review. Existing BRD guardrails remain mandatory. Research confidence describes the evidence, not a proven design outcome.

## UXP-01
- **Principle:** Check inputs before trusting the amount.
- **What it means:** Use the affected person's records and the inputs for the relevant period. Let deterministic code calculate the result, and stop the affected part when required data is missing or unusual.
- **Do:** Identify the month with missing attendance and state that its arrears cannot be calculated from the available data.
- **Don't:** Substitute zero unpaid days to complete an otherwise missing month.
- **Source:** PS-01; PP-01–PP-04, PP-14–PP-15, PP-17; EVD-03–EVD-05, EVD-49–EVD-50, EVD-57; FR-1.12, FR-2.13, FR-3.17; GR-3.1–GR-3.3.
- **Confidence:** High for documented input risks and the guardrail. Medium for settlement effort interpretation. Relative effort remains unvalidated in AS-10, AS-12 and AS-13.

## UXP-02
- **Principle:** Show the month and rule behind each amount.
- **What it means:** Keep each calculation tied to its period, input records and dated rule version. A total must not hide different months or company policy bases.
- **Do:** Explain the arrears for each affected month and identify the PF wage, company setting and rule version used.
- **Don't:** Show only total arrears with an undated PF rate or an unexplained recovery basis.
- **Source:** PS-01, PS-04; PP-01, PP-06, PP-19–PP-20; EVD-01–EVD-02, EVD-25–EVD-26, EVD-62–EVD-64; FR-1.6, FR-1.10–FR-1.11, FR-3.15; BR-0.1–BR-0.4; GR-3.5.
- **Confidence:** High for the traceability requirement and documented period calculations. Medium for historical PF and company-policy interpretation. Rule parameters still require verification before build.

## UXP-03
- **Principle:** Explain the net change before payroll terms.
- **What it means:** Start with the take-home or TDS change and its main reasons in simple words. Offer the component details and sources without making the employee work through terms before understanding the change.
- **Do:** Explain the payroll-recorded net change and the relevant unpaid days before offering the detailed calculation.
- **Don't:** Answer a question about lower pay with only a deduction label or a gross arrears amount.
- **Source:** PS-02, PS-03; PP-07–PP-10; EVD-09–EVD-10, EVD-13, EVD-15; FR-4.4–FR-4.13, FR-5.3–FR-5.10; GR-3.5; The Pay-Change Employee, goals and needs.
- **Confidence:** High for the required explanation order. Medium for the complaint patterns and AS-2. A causal trust gain remains Low and Unvalidated in AS-4.

## UXP-04
- **Principle:** Make approval explicit; never imply payment.
- **What it means:** Distinguish a calculated proposal from HR approval and readiness for payroll. Employee query sending also needs explicit employee confirmation, and no state implies that this demo has paid money.
- **Do:** Describe an approved hike as ready for payroll and record who approved it and when.
- **Don't:** Treat silence as approval, send a query without confirmation or call a prepared settlement paid.
- **Source:** PS-05; PP-05, PP-16; EVD-06, EVD-30–EVD-31, EVD-52; FR-1.13–FR-1.17, FR-2.15–FR-2.19, FR-3.18–FR-3.21, FR-6.7; BR-7.1–BR-7.3; GR-1.1–GR-1.3, GR-7.1; BRD 5.3.
- **Confidence:** High for mandatory human control and the named approval capabilities. Medium for approval-history problems. Target HR acceptance remains Low and Unvalidated in AS-3.

## UXP-05
- **Principle:** Keep unresolved settlement components visible.
- **What it means:** Distinguish confirmed amounts from components with missing data or an unresolved basis. A clearance dependency is not proof that a wage component can be held; component due dates and statuses remain subject to the proposed GAP-09 direction.
- **Do:** Explain which line has an unresolved basis and why, while preserving the distinction between that line and confirmed components. If Option B is approved, show only dates and hold bases supported by verified rules.
- **Don't:** Hide an unresolved recovery inside one trusted net total or use an asset clearance to justify holding every component.
- **Source:** PS-01, PS-03–PS-05; PP-17–PP-21; EVD-58–EVD-59, EVD-61, EVD-65, EVD-68–EVD-69, EVD-71, EVD-81; FR-3.5, FR-3.14–FR-3.20; GR-3.1, GR-3.3–GR-3.5; [MVP scope](mvp-scope.md), Section 5; GAP-09, DEC-004.
- **Confidence:** High for stopping missing-data calculations and documented product dependencies. Medium for the recovery complaint. Component-model clarity is Low and Unvalidated in AS-14; permitted holds and classifications remain EG-25. Rules reported effective 2025-11-21 require verification from official source before build.

## UXP-06
- **Principle:** Escalate unresolved pay questions with relevant proof.
- **What it means:** Say when payroll data cannot explain a difference instead of creating a reason. Carry the question and minimum relevant evidence into the employee-confirmed query so HR can understand what has already been checked.
- **Do:** State the payroll-only limit for a reported bank mismatch, prepare the relevant query evidence and ask for confirmation before sending.
- **Don't:** Claim to have checked a bank credit or resolve a disputed recovery by guessing its cause.
- **Source:** PS-03, PS-05; PP-11–PP-13, PP-21; EVD-10, EVD-16–EVD-18, EVD-68; FR-4.14–FR-4.15, FR-5.12, FR-6.3–FR-6.7, FR-6.12; GR-3.4, GR-6.1–GR-6.2; The Pay-Change Employee, unknowns.
- **Confidence:** High for required honesty and escalation. Medium for qualitative unresolved questions. Actual resolution times and evidence sufficiency are unknown in EG-03 and GAP-08.

## UXP-07
- **Principle:** Use only authorized payroll data for this question.
- **What it means:** Check identity and role before returning records, and use only records needed for the task. Mask identifiers and refuse requests for another person's pay without confirming whether their records exist.
- **Do:** Answer an employee's TDS question from their own relevant salary and declaration data, with masked identifiers.
- **Don't:** Include another employee's pay, full identifiers or unnecessary records in an answer, query attachment or audit log.
- **Source:** FR-4.3, FR-4.17, FR-5.2, FR-5.13, FR-6.5; GR-2.1–GR-2.6, GR-5.1–GR-5.3, GR-7.2, GR-8.1; EVD-42 and EVD-44 provide enterprise context only; persona AI trust concerns; EG-05.
- **Confidence:** High for mandatory access and privacy controls. Low for target employees' AI data comfort. Enterprise evidence does not establish their personal fears.

## How to use these principles
Compare each design option with the relevant principle and its cited source; retain the option that satisfies the BRD guardrails and makes the applicable payroll basis clear.
Record the reason in the decision log, and keep unvalidated benefits and the GAP-09 recommendation open for review and testing.
None of these principles authorizes personal advice, promises about future pay, guessed rules or real payroll data. (GR-3.1, GR-4.1–GR-4.3, GR-8.1)
