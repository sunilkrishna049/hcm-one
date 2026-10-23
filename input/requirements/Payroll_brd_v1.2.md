# HCM One: Business Requirements Document

## Change log
- Version: 1.2
- Date: 2026-10-13
- Scenario 10 reframed: under the new tax regime, investment declarations rarely change TDS. A previous-employer income declaration does.
- BR-4.5 added: new tax regime only.
- Reason: Approved by Project owner after rules config decision GAP-05.

- Version: 1.1
- Date: 2026-10-13
- PBRD-01: Require a verified rule for a related clearance hold. Reason: Approved at Gate G04.
- PBRD-02: Distinguish settlement component bases, due dates and statuses in one reconciled summary with HR approval. Reason: Approved at Gate G04.
- PBRD-03: Record component classification, verified due-date basis and permitted hold basis, and test unresolved and confirmed components together. Reason: Approved at Gate G04.
- PBRD-04: Include complete Flow 6 as supporting scope for priority 1. Reason: Approved at Gate G04.

Product: HCM One, an agentic AI payroll assistant
Document type: Business Requirements Document (BRD)
Location in project: input/requirements/Payroll_brd.md (input file, never changed by agents)

---

## 1. Project Overview

HCM One is an AI payroll assistant for mid-size Indian companies (200 to 2,000 employees).

It helps two types of users:
- HR Admins, who process salary changes such as back-dated hikes, arrears, PF, bonuses, incentives, and full and final settlements.
- Employees, who want to understand why their salary or tax changed.

The AI calculates step by step, shows proof for every number, and waits for HR approval before any change is applied. For employees, it explains salary and tax changes in simple language.

---

## 2. Business Goals

1. Reduce manual work for HR when processing salary changes.
2. Reduce calculation mistakes in arrears, PF, bonus and settlement.
3. Give a clear record of who calculated, checked and approved every salary change.
4. Reduce the number of salary and tax questions employees send to HR.
5. Increase employee trust by explaining every salary change clearly, with proof.
6. Keep humans in control: AI prepares and explains, HR decides.

---

## 3. Users and Roles

### 3.1 HR Admin
Processes salary changes for employees in the company.

Can see:
- Salary details, salary history and payslips of employees they are authorized to manage
- Attendance, leave and LOP records needed for payroll
- PF, tax, bonus and settlement rules used by the company

Can do:
- Ask the AI to calculate a back-dated hike, arrears and PF impact
- Ask the AI to calculate bonuses and incentives
- Ask the AI to prepare a full and final settlement
- Review every calculation step
- Approve, edit or reject the AI's proposal

Cannot do:
- Let the AI apply any salary change without their approval

### 3.2 Employee
Receives salary and wants to understand it.

Can see:
- Only their own payslips, salary history, PF and tax details

Can do:
- Ask why their salary changed this month
- Ask why their tax (TDS) changed
- See a simple explanation first, then the detailed calculation if they want
- Raise a query to HR if something looks wrong

Cannot do:
- See any other employee's data
- Change any payroll data

---

## 4. Problems

### 4.1 HR Admin Problems
1. Back-dated hikes: each past month must be recalculated because leave days, salary parts and PF can be different each month. This is often done in spreadsheets, with approvals over email.
2. Bonus and incentives: different rules for different teams or roles make calculations slow and easy to get wrong.
3. Full and final settlement: when an employee leaves, HR must calculate leave encashment, gratuity, notice-period recovery and pending dues using data from different places.

### 4.2 Employee Problems
1. Salary change confusion: employees see a different amount in their bank and do not know why. Terms like PF, arrears and LOP are confusing.
2. Tax confusion: employees do not understand why TDS was deducted or why it changed after a hike or bonus.

### 4.3 Why It Matters
When salary numbers cannot be explained clearly, HR spends more time fixing errors and answering questions, and employees stop trusting the company.

---

## 5. Scope

### 5.1 In Scope

HR Admin flows:
1. Back-dated salary hike: calculate the new salary, month-by-month arrears and PF impact, then send for HR approval.
2. Bonus and incentives: calculate bonus or incentive amounts based on team or role rules, including tax impact, then send for HR approval.
3. Full and final settlement: calculate leave encashment, gratuity, notice-period recovery and pending dues for an employee who is leaving, then send for HR approval.

Employee flows:
4. Salary change explanation: explain why this month's salary is different from last month, starting with the total change, then the reasons, then the detailed calculation.
5. Tax (TDS) explanation: explain why TDS was deducted or why it changed after a hike or bonus.
6. Raise a query: if something looks wrong, the AI prepares a query with the evidence attached, and the employee confirms before it is sent to HR.

### 5.2 Build Priority
1. Back-dated hike flow (HR) and salary change explanation with TDS (Employee), with existing Flow 6 as supporting scope for priority 1, including its complete draft, confirmation, tracking and HR response requirements.
2. Bonus and incentives
3. Full and final settlement

Each flow must work end to end before the next one starts.

### 5.3 Out of Scope
- Running the full monthly payroll
- Bank transfer files and salary payments
- Statutory filing and compliance submissions (PF, ESI, TDS returns)
- Manager role
- Payslip vs Form 26AS check
- Real company or employee data (only fictional mock data is used)
- AI applying any change without HR approval

---

## 6. Functional Requirements

Each requirement has an ID so agents and tests can refer to it.

### 6.1 Flow 1: Back-dated Salary Hike (HR Admin)

Request
- FR-1.1 HR can ask in plain language, for example: "Apply a 10% hike for Priya from 1 April."
- FR-1.2 If details are missing (employee, hike amount or effective date), the AI asks for them before calculating.
- FR-1.3 The AI confirms the employee, old salary, new salary and effective date before starting.

Calculation
- FR-1.4 The AI finds all past payroll months affected by the effective date.
- FR-1.5 For each affected month, the AI recalculates what should have been paid, using that month's attendance, LOP and salary structure.
- FR-1.6 For each month, the AI shows: old amount, new amount and difference.
- FR-1.7 The AI recalculates PF for each affected month based on the new PF wage.
- FR-1.8 The AI calculates the tax (TDS) impact of the hike and arrears.
- FR-1.9 The AI shows total gross arrears, total PF change, tax impact and expected net arrears.

Proof and clarity
- FR-1.10 Every number has a "Show calculation" option with the formula and source record used.
- FR-1.11 The AI shows which PF rule version and effective date it used.
- FR-1.12 If any data is missing or unusual (for example, missing attendance for a month), the AI flags it clearly and does not guess.

Approval
- FR-1.13 The AI presents the result as a proposal, not a final change.
- FR-1.14 HR can Approve, Edit or Reject the proposal.
- FR-1.15 If HR edits, the AI recalculates and shows the updated proposal.
- FR-1.16 Only after HR approves is the change marked as ready for payroll.
- FR-1.17 The system records who requested, who approved, and when.

### 6.2 Flow 2: Bonus and Incentives (HR Admin)

Request
- FR-2.1 HR can ask for one employee or a group, for example: "Calculate Q2 sales incentive for the Hyderabad sales team."
- FR-2.2 The AI identifies the bonus type (performance bonus, sales incentive, festival bonus or one-time bonus) and asks if it is unclear.
- FR-2.3 If the rule, period or target employees are missing, the AI asks before calculating.

Eligibility
- FR-2.4 The AI checks each employee against the eligibility rules (for example: role, team, joining date, minimum days worked, employees on notice period).
- FR-2.5 The AI lists eligible and not eligible employees separately, with the reason for each.
- FR-2.6 For employees who joined or left in the middle of the period, the AI applies the proration rule and shows how it was applied.

Calculation
- FR-2.7 The AI calculates the amount for each employee using the rule for their team or role (for example: fixed amount, percentage of salary, or slab based on target achieved).
- FR-2.8 For target-based incentives, the AI shows target, achievement and the slab applied.
- FR-2.9 The AI calculates the tax (TDS) impact of the bonus for each employee.
- FR-2.10 The AI applies PF only if the company rule says the bonus type counts as PF wage, and shows which rule was used.
- FR-2.11 The AI shows a summary: total employees, total bonus amount, total TDS and expected net payout.

Proof and clarity
- FR-2.12 Every employee's amount has a "Show calculation" option with the rule, inputs and formula used.
- FR-2.13 If performance or target data is missing for any employee, the AI flags it and does not guess.
- FR-2.14 The AI flags unusual results, for example a bonus much higher than the employee's past bonuses.

Approval
- FR-2.15 The AI presents the result as a proposal, not a final payment.
- FR-2.16 HR can approve all, approve some, edit individual amounts or reject.
- FR-2.17 If HR edits an amount, the AI records the reason and recalculates the summary.
- FR-2.18 Only approved amounts are marked as ready for payroll.
- FR-2.19 The system records who requested, who approved, and when.

### 6.3 Flow 3: Full and Final Settlement (HR Admin)

Request
- FR-3.1 HR can ask in plain language, for example: "Prepare full and final settlement for Rahul, last working day 31 October."
- FR-3.2 The AI confirms the employee, resignation date, last working day and notice period before starting.
- FR-3.3 If any key detail is missing, the AI asks before calculating.

Pre-checks
- FR-3.4 The AI checks the status of exit clearances (for example: asset return, IT, finance) and lists any that are pending.
- FR-3.5 Pending clearance does not automatically hold every settlement component. A related hold needs a verified applicable rule. If the basis is unknown, flag it and stop that part.

Calculation: amounts payable to the employee
- FR-3.6 Salary for days worked in the final month, based on attendance and LOP.
- FR-3.7 Leave encashment, based on the leave balance and the company's encashment rule.
- FR-3.8 Gratuity, only if the employee meets the eligibility rule, with years of service and formula shown.
- FR-3.9 Pending bonus, incentives and reimbursements that are already approved.

Calculation: amounts recoverable from the employee
- FR-3.10 Notice period shortfall recovery, if the employee did not serve the full notice and it was not waived.
- FR-3.11 Outstanding loans, salary advances or other recoveries.
- FR-3.12 Recovery for unreturned company assets, only if the company rule allows it.

Tax and summary
- FR-3.13 The AI calculates the tax (TDS) on the final settlement.
- FR-3.14 The AI shows a settlement summary: total payable, total recoverable, TDS and final net amount (payable or recoverable). Retain the overall reconciliation and distinguish component preparation and approval statuses and applicable due dates.

Proof and clarity
- FR-3.15 Every line has a "Show calculation" option with the rule, inputs and formula used.
- FR-3.16 If eligibility is unclear (for example, gratuity when service is close to the minimum), the AI flags it for HR to decide.
- FR-3.17 If any data is missing, the AI flags it and does not guess.

Approval and output
- FR-3.18 The AI presents the settlement as a proposal, not a final payment. Distinguish component preparation and approval statuses and applicable due dates.
- FR-3.19 HR can approve, edit individual lines (with a reason) or reject. HR still approves; no payment execution is added.
- FR-3.20 After approval, the AI prepares a settlement statement the employee can understand. Carry unresolved or permitted held components into the statement with their reasons.
- FR-3.21 The system records who requested, who approved, and when.

### 6.4 Flow 4: Salary Change Explanation (Employee)

Request
- FR-4.1 The employee can ask in plain language, for example: "Why is my salary less this month?" or "Why did I get extra money?"
- FR-4.2 By default, the AI compares the latest payslip with the previous month. The employee can choose any other two months.
- FR-4.3 The AI only uses the logged-in employee's own data.

Explanation: simple first
- FR-4.4 The AI starts with the total change in take-home pay, for example: "Your take-home is ₹3,500 lower than last month."
- FR-4.5 The AI then lists the main reasons, biggest first, in simple words. For example: "2 days of unpaid leave in May reduced your salary by ₹3,200."
- FR-4.6 Each reason states what changed, why, and when it took effect.
- FR-4.7 If there was a back-dated hike, the AI explains the hike, the arrears for past months, and why PF and tax also changed.
- FR-4.8 If nothing changed in salary components, the AI says so clearly instead of creating a reason.

Explanation: details on request
- FR-4.9 The employee can open "Show breakdown" to see a component-by-component comparison (earnings and deductions, last month vs this month).
- FR-4.10 For arrears, the employee can see a month-by-month breakdown.
- FR-4.11 For PF, the AI explains the employee share and the employer share (EPF and EPS) separately.
- FR-4.12 Every number shows its source record, for example: "From salary revision effective 1 April" or "From May attendance."
- FR-4.13 Payroll terms (PF, LOP, arrears, TDS) can be tapped to see a short, simple meaning.

Limits and next steps
- FR-4.14 If the employee mentions a bank credit that does not match the payslip, the AI explains that it can only see payroll data and suggests raising a query.
- FR-4.15 If the AI finds something unusual or cannot explain a difference, it says so honestly and offers to raise a query to HR (Flow 6).
- FR-4.16 The employee can ask follow-up questions in the same conversation, for example: "Will this happen next month too?"
- FR-4.17 The AI never shows other employees' data or confirms anything about another employee.

### 6.5 Flow 5: Tax (TDS) Explanation (Employee)

Request
- FR-5.1 The employee can ask in plain language, for example: "Why was tax cut from my salary?" or "Why is my TDS higher this month?"
- FR-5.2 The AI only uses the logged-in employee's own salary, tax and declaration data.

Explanation: simple first
- FR-5.3 The AI starts with the change, for example: "Your TDS is ₹2,100 higher than last month."
- FR-5.4 The AI explains the main reason in simple words, for example: "Your salary hike increased your expected yearly income, so your monthly tax went up."
- FR-5.5 The AI explains the common reasons when they apply:
  - Salary hike or arrears increased yearly taxable income
  - A bonus or incentive was paid this month
  - Investment declarations were not submitted, or proofs were rejected
  - New declarations were accepted, reducing tax
  - Tax regime used (old or new) as selected by the employee
- FR-5.6 If the employee asks why any TDS is deducted at all, the AI explains in simple words that the company deducts expected yearly tax in monthly parts.

Explanation: details on request
- FR-5.7 The employee can open "Show tax calculation" to see: projected yearly income, deductions and exemptions applied, yearly tax, tax already deducted, and remaining months.
- FR-5.8 The AI shows how monthly TDS is calculated: remaining yearly tax divided by remaining months.
- FR-5.9 The AI shows which tax regime and which tax rule version it used.
- FR-5.10 The AI lists any pending or rejected declarations that affect TDS, with their status.

Limits and next steps
- FR-5.11 The AI explains TDS but does not give personal tax advice, such as which regime to choose or where to invest. It suggests the employee consult a tax professional for that.
- FR-5.12 If the AI cannot explain a TDS change, it says so honestly and offers to raise a query to HR (Flow 6).
- FR-5.13 The AI never shows other employees' tax data.

### 6.6 Flow 6: Raise a Query (Employee)

Starting a query
- FR-6.1 The employee can raise a query directly, for example: "I think my LOP is wrong for May."
- FR-6.2 The AI can also offer to raise a query when it cannot explain a difference (from Flow 4 or Flow 5).
- FR-6.3 The AI first checks whether the issue can be explained from payroll data. If it can, it explains and asks if the employee still wants to raise a query.

Drafting
- FR-6.4 The AI drafts the query with:
  - Category (salary, arrears, PF, TDS, bonus, settlement, other)
  - The month or months involved
  - A short description in the employee's own words
  - Evidence attached automatically (relevant payslip lines, attendance records, calculation shown)
  - What the AI already checked and could not explain
- FR-6.5 The draft only includes data relevant to the issue, not the employee's full records.
- FR-6.6 The employee can edit the description and remove any attached item before sending.

Confirmation and sending
- FR-6.7 The AI never sends a query without the employee's clear confirmation.
- FR-6.8 If a similar open query already exists, the AI shows it and asks whether to add to it or create a new one.
- FR-6.9 After sending, the employee gets a query ID and the expected next step.

Tracking
- FR-6.10 The employee can ask about the status of their queries, for example: "What happened to my LOP query?"
- FR-6.11 The AI shows the status (sent, in review, resolved, closed) and any reply from HR.

HR side
- FR-6.12 HR receives the query with the summary and evidence already attached, so they do not need to ask the employee again.
- FR-6.13 HR's reply and resolution are recorded against the query ID.

---

## 7. Business Rules

Important: These are simplified rules for a portfolio demo using fictional mock data. They are not for real payroll use. All rate values (PF ceiling, tax slabs, gratuity cap) are stored in a separate rules config file, each with an effective date and source, and must be verified from official sources before use.

Settlement rules record component classification, verified due-date basis and permitted hold basis.

### 7.1 General Rules
- BR-0.1 Every rule has a version, an effective-from date and a source.
- BR-0.2 The AI always uses the rule version that was valid for the month being calculated.
- BR-0.3 All amounts are rounded to the nearest rupee.
- BR-0.4 If a needed rule or value is missing, the AI stops and flags it. It never guesses a rate.

### 7.2 Paid Days and LOP
- BR-1.1 Paid days = days in the month minus LOP days.
- BR-1.2 Monthly earned salary = monthly salary × paid days ÷ days in the month.

### 7.3 Back-dated Hike and Arrears
- BR-2.1 Affected months = every payroll month from the effective date up to the last processed month.
- BR-2.2 For each affected month: arrears = revised earned salary − salary actually paid, using that month's paid days.
- BR-2.3 Total arrears = sum of all monthly differences.
- BR-2.4 Arrears are paid in the next payroll month after HR approval.

### 7.4 PF (Provident Fund)
- BR-3.1 PF wage = Basic + DA (as defined in the salary structure).
- BR-3.2 Employee contribution = 12% of PF wage.
- BR-3.3 Employer contribution = 12% of PF wage, split into EPS (pension) and EPF.
- BR-3.4 EPS is calculated on PF wage up to the wage ceiling in the rules config. The rest of the employer share goes to EPF.
- BR-3.5 Whether PF is calculated on full PF wage or capped at the ceiling is a company setting.
- BR-3.6 For arrears, PF is recalculated month by month using the rule version valid for that month.
- BR-3.7 PF wage ceiling in the rules config: ₹15,000 per month before 17 September 2026, and ₹25,000 per month from 17 September 2026.

### 7.5 Tax (TDS)
- BR-4.1 Projected yearly taxable income = salary paid so far + expected salary for remaining months + arrears, bonus or other one-time payments − allowed exemptions and deductions.
- BR-4.2 Yearly tax is calculated using the tax regime the employee selected and the slab rates in the rules config.
- BR-4.3 Monthly TDS = (yearly tax − TDS already deducted) ÷ remaining months in the financial year.
- BR-4.4 If declarations are not submitted or proofs are rejected, those deductions are not applied.
- BR-4.5 The demo uses the new tax regime only. The old regime and its deductions are out of scope.

### 7.6 Bonus and Incentives
- BR-5.1 Each bonus type has its own rule: fixed amount, percentage of salary, or slab based on target achievement.
- BR-5.2 Eligibility is checked using the rule's criteria (role, team, joining date, minimum days worked, notice period status).
- BR-5.3 Proration = full amount × eligible days in the period ÷ total days in the period.
- BR-5.4 PF applies to a bonus only if the company rule marks that bonus type as part of PF wage.
- BR-5.5 Statutory bonus under the Payment of Bonus Act is out of scope for this demo.

### 7.7 Full and Final Settlement
- BR-6.1 Final month salary follows the paid days rule (BR-1.2) up to the last working day.
- BR-6.2 Leave encashment = encashable leave days × (salary base ÷ day divisor). The salary base, day divisor (30 or 26) and maximum encashable days are company settings.
- BR-6.3 Gratuity is paid only if the employee meets the minimum service rule in the rules config.
- BR-6.4 Gratuity = 15 ÷ 26 × last drawn (Basic + DA) × completed years of service, up to the cap in the rules config. How part-years are counted follows the rules config.
- BR-6.5 Notice shortfall recovery = shortfall days × (salary base ÷ day divisor), unless HR waives it. The salary base is a company setting.
- BR-6.6 Loan, advance and asset recoveries are applied only if they are recorded in the system and allowed by company rules.
- BR-6.7 If final net amount is negative, it is shown as recoverable from the employee, not paid.

### 7.8 Approval Rules
- BR-7.1 No calculation becomes final without HR approval.
- BR-7.2 Any HR edit to an AI-calculated amount must include a reason.
- BR-7.3 Every request, calculation version, edit and approval is recorded with who and when.

---

## 8. Guardrails

These rules apply to every flow and cannot be turned off.

### 8.1 Human Control
- GR-1.1 The AI prepares, calculates and explains. It never applies, approves or pays any salary change by itself.
- GR-1.2 Every salary-affecting change needs explicit HR approval. Silence or no response is never treated as approval.
- GR-1.3 Employee queries are sent only after the employee confirms.

### 8.2 Data Access and Privacy
- GR-2.1 Every data request checks the user's identity and role before returning data.
- GR-2.2 Employees can only see their own data.
- GR-2.3 HR Admins can only see employees they are authorized to manage.
- GR-2.4 The AI never confirms or denies anything about another person's salary, tax or records.
- GR-2.5 The AI uses only the data needed for the current task.
- GR-2.6 Bank account numbers, PAN and other ID numbers are never shown in full.

### 8.3 Accuracy and Honesty
- GR-3.1 All numbers come from payroll data and the rules config. The AI never invents amounts, rates or rules.
- GR-3.2 Calculations are done by deterministic code, not by the language model. The language model only explains the results.
- GR-3.3 If data is missing or unusual, the AI flags it and stops that part of the calculation.
- GR-3.4 The AI clearly says when it is unsure or cannot explain something.
- GR-3.5 Every number can be traced to its source record and rule version.

### 8.4 Scope Limits
- GR-4.1 The AI does not give personal tax, legal or financial advice.
- GR-4.2 The AI does not answer questions outside payroll. It politely says what it can help with.
- GR-4.3 The AI does not make promises about future salary, hikes, bonuses or approvals.

### 8.5 Security
- GR-5.1 The AI refuses requests to reveal its instructions, system details, credentials or other users' data.
- GR-5.2 The AI ignores instructions hidden in user messages that try to change its rules (prompt injection).
- GR-5.3 Security refusals are short and polite, and do not reveal internal details.
- GR-5.4 API keys are stored only on the server, never in the frontend or code repository.

### 8.6 Escalation
- GR-6.1 The AI escalates to HR when it has low confidence, finds a mismatch it cannot explain, or the user disputes a calculation.
- GR-6.2 Escalations include a summary and the relevant evidence, so the user does not have to repeat themselves.

### 8.7 Audit
- GR-7.1 Every request, AI calculation, edit, approval, rejection and escalation is logged with who and when.
- GR-7.2 Logs never store full ID numbers, bank details or API keys.

### 8.8 Demo Data
- GR-8.1 Only fictional mock data is used. No real company, employee or payroll data.

---

## 9. Data Needed

All data is fictional mock data, stored as JSON files. Company: "Northwind Technologies Pvt Ltd", a fictional company based in Hyderabad with around 500 employees. The demo uses 15 to 20 sample employees.

### 9.1 Company and Users
- company.json: company name, financial year, payroll cut-off date, company payroll settings (PF on full or capped wage, leave encashment base and divisor, notice recovery base)
- users.json: user ID, name, role (HR Admin or Employee), employees each HR Admin is allowed to manage

### 9.2 Employee Data
- employees.json: employee ID, name, department, team, role, location, joining date, employment status, tax regime selected, masked PAN, masked UAN, masked bank account
- salary-structures.json: for each employee, monthly components (Basic, DA, HRA, special allowance, others) and which components count as PF wage
- salary-revisions.json: revision ID, employee ID, old salary, new salary, effective date, created date, status

### 9.3 Attendance and Leave
- attendance.json: employee ID, month, days in month, days present, LOP days, missing records (if any)
- leave-balances.json: employee ID, leave type, balance, encashable days

### 9.4 Payroll History
- payslips.json: employee ID, month, each earning and deduction line, gross pay, total deductions, net pay, PF (employee, EPF, EPS), TDS
- payroll-runs.json: month, status (processed or open), processed date

### 9.5 Rules Config
- pf-rules.json: rule version, effective from, wage ceiling, contribution rates, EPS rate, source
- tax-rules.json: financial year, regime, slab rates, standard deduction, rebate rules, source
- gratuity-rules.json: minimum service, formula values, cap, part-year rule, source
- bonus-rules.json: bonus type, eligibility criteria, calculation type (fixed, percentage or slab), slabs, proration rule, whether it counts as PF wage

For settlement components, the existing rules config records component classification, verified due-date basis and permitted hold basis.

### 9.6 Tax Declarations
- declarations.json: employee ID, financial year, declaration type, declared amount, proof status (pending, accepted, rejected)

### 9.7 Bonus and Performance
- performance.json: employee ID, period, target, achievement, rating

### 9.8 Exit and Settlement
- exits.json: employee ID, resignation date, last working day, notice period required, notice period served, notice waived (yes or no)
- clearances.json: employee ID, clearance type (asset, IT, finance), status
- recoveries.json: employee ID, type (loan, advance, asset), amount, status

Existing exit and settlement data record component classification, verified due-date basis and permitted hold basis.

### 9.9 Queries and Audit
- queries.json: query ID, employee ID, category, months, description, evidence, status, HR reply
- audit-log.json: event ID, user, action, item, time, details

### 9.10 Test Scenarios the Data Must Cover
1. Back-dated hike with LOP in one of the affected months
2. Back-dated hike crossing 17 September 2026, when the PF wage ceiling changed
3. Back-dated hike where one month's attendance is missing
4. Bonus for a team with one mid-year joiner and one employee on notice period
5. Bonus where one employee's performance data is missing
6. Full and final settlement for an employee eligible for gratuity
7. Full and final settlement for an employee just below gratuity eligibility
8. Full and final settlement with a pending asset clearance and notice shortfall
9. Employee whose salary dropped because of LOP
10. Employee whose TDS increased because they declared income from a previous employer mid-year
11. Employee with no salary change between two months
12. An employee trying to see another employee's salary
13. An unresolved settlement component alongside a confirmed component.

---

## 10. Success Measures

These are proposed measures. There are no real baselines yet, because this project uses desk research only. They will be checked during testing.

### 10.1 HR Admin
- SM-1.1 HR can complete a back-dated hike, bonus or settlement proposal without using a spreadsheet.
- SM-1.2 Every calculated amount matches the expected result in the test scenarios (Section 9.10).
- SM-1.3 HR can find the source and formula of any number in one click.
- SM-1.4 Missing or unusual data is flagged in 100% of the test scenarios that include it.

### 10.2 Employee
- SM-2.1 In testing, employees can explain in their own words why their salary or TDS changed after reading the AI's answer.
- SM-2.2 Employees find the main reason for a salary change without opening the detailed breakdown.
- SM-2.3 Queries raised through the AI include enough evidence that HR does not need to ask the employee again.

### 10.3 Safety and Trust
- SM-3.1 The AI never applies a change without approval in any test.
- SM-3.2 The AI refuses every attempt to access another employee's data in testing.
- SM-3.3 The AI says "I'm not sure" or escalates, instead of guessing, in every low-confidence test case.

---

## 11. Assumptions and Open Questions

### 11.1 Assumptions
- AS-1 HR teams in mid-size Indian companies find back-dated arrears and settlements time-consuming. (Supported by desk research, not validated with users.)
- AS-2 Employees mainly want to know why their take-home changed, before learning payroll terms. (Medium confidence, from public complaints.)
- AS-3 HR will accept AI that prepares and explains calculations, if they approve before anything changes. (Not validated.)
- AS-4 Employees will trust an explanation more if every number shows its source. (Not validated.)
- AS-5 Simplified rules are enough to demonstrate the experience, even though real payroll has more cases.

### 11.2 Open Questions
- OQ-1 How much time do HR teams actually spend on arrears and settlements today?
- OQ-2 Are employees comfortable with an AI reading their salary and tax data?
- OQ-3 Does HR want to approve each employee's bonus separately, or approve a whole team at once?
- OQ-4 How much detail do employees actually want before they feel confident?
- OQ-5 Should an approved proposal be sent to a second approver (for example, Finance) in larger companies?

---

## 12. Constraints

- C-1 Tools: Codex and Antigravity for building, CrewAI for the agent workflow, OpenAI API for the language model.
- C-2 Research: desk research only. No user interviews before design.
- C-3 Data: fictional mock data only.
- C-4 Rules: simplified Indian payroll rules for demo purposes, not real compliance logic.
- C-5 Calculations must be done by code, not by the language model.
- C-6 The project is built by one person (UX Designer) with AI coding assistants.
