# HCM One: Screen Specifications (Chat-First Architecture)

## Data and content contract

Every displayed number, period, count and identifier is bound to the exact generated data in Section 8. The prototype must not calculate, round, split or infer any payroll value. Monospace font is reserved strictly for technical IDs (Query IDs, record references). Financial amounts use Inter with tabular figures (`tnum`).

Assistant wording uses only the approved sentences C01–C30 in Section 7, used verbatim. Named slots are filled exclusively from authorized actual records. Headings and labels are interface content, not new AI causal sentences.

No internal labels (screen IDs, sentence codes, file paths or JSON pointers) are visible to users. No "Verified" badges are shown. Query statuses are strictly: `Draft`, `Sent`, `In review`, `Resolved`, `Closed`.

---

## 1. Surface Architecture: CHAT-HR and CHAT-EMP

### 1.1. CHAT-HR — HR Admin Chat Workspace (Desktop 1440 px)
- **Viewport:** 1440 px reference width (min 1280 px).
- **Primary Chat Thread:** Center-left conversational container (max reading width 840 px). Contains user bubbles, assistant bubbles, suggestion chips, rich cards, and sticky bottom composer (height 80 px).
- **PANEL-HR (Heavy Review Side Panel):** Dedicated right-docked side panel (width 480 px, full viewport height). Opens on demand when the user clicks "Show calculation" or "View full month breakdown". Displays dense multi-month arrears grids, settlement ledgers, bonus eligibility tables, plain-language formulas, and human-readable statutory rule citations with rules version "Northwind demo rules v1". Never shows raw JSON keys, file names or internal rule IDs to users.
- **Focus & Keyboard Navigation:** When `PANEL-HR` opens, focus shifts to the panel close button (`✕` or `Escape`). Closing `PANEL-HR` restores focus to the triggering control.

### 1.2. CHAT-EMP — Employee Chat Workspace (Mobile 390 px)
- **Viewport:** 390 px reference width (min 320 px).
- **Primary Chat Feed:** Single-column mobile feed with 16 px padding. Contains user bubbles, assistant bubbles, suggestion chips, hero cards, ranked reasons, query drafts, and sticky bottom composer (height 64 px).
- **SHEET-EMP (Detail & Calculation Proof Bottom Sheet):** Modal bottom sheet (width 100%, max-height 85vh) with drag handle. Opens on demand when the employee taps "Show calculation" or "Review evidence". Displays step-by-step plain-language formulas, tax calculation breakdowns, evidence checklists, and glossary explanations.

---

## 2. Turn-by-Turn Conversation Scripts (All 13 BRD v1.2 Scenarios)

### Scenario 1: Back-dated hike with LOP in one of the affected months
- **Surface:** `CHAT-HR` (Desktop 1440 px)
- **Role:** HR Admin (`HR01`)
- **Employee Context:** Priya Sharma (`E01`)
- **Turn 1 (User):** "Prepare Priya Sharma's pending back-dated hike."
- **Turn 2 (Assistant Bubble):** C03: "This is a proposal for the recorded affected months."
- **Cards Shown in Thread:**
  1. *Proposal Summary Card:* Employee: Priya Sharma (`E01`); Requested hike: `10%` (Binding: `D01-requested_hike_percentage`); Effective date: `2026-04-01` (`D01-effective_date`); Old monthly salary total: `₹1,20,000` (`D01-old_monthly_salary-total`); Proposed monthly salary total: `₹1,32,000` (`D01-proposed_monthly_salary-total`); Status: `Needs HR approval; not applied`; Certainty: `Complete for this scope`.
  2. *Number Cards Cluster (Indian Rupee format with tabular figures):*
     - Hero Card: Expected net arrears `₹67,476` (Binding: `H-net_arrears`)
     - Gross arrears: `₹71,200` (`H-gross_arrears`)
     - Employee PF change: `₹0` (`H-pf`)
     - Estimated TDS impact: `₹3,724` (`H-tds_impact`)
     - Sourced payment month: `2026-10` (`H-month`)
     - Estimate flag: "Estimated TDS if approved and paid in October 2026 payroll" (`H-flag`)
  3. *Month Table Card:* Summary of 6 affected months (2026-04 to 2026-09), total gross arrears `₹71,200`. Action: "Show calculation" (opens `PANEL-HR`).
  4. *Approval Card:*
     - Notice (C04): "Approving records this version and the selected scope as ready for payroll. It does not apply the change or make a payment."
     - Actions: [Approve proposal for payroll] [Edit with reason] [Reject proposal]
- **PANEL-HR View (Open State):**
  - Month-by-Month Breakdown Table (Tabular figures):
    * 2026-04: Old gross `₹1,20,000` (`HM-0-old`), Revised gross `₹1,32,000` (`HM-0-new`), Arrears `₹12,000` (`HM-0-diff`), PF change `₹0` (`HM-0-pf`), TDS impact `₹312` (`HM-0-tds`), Paid days `30`
    * 2026-05: Old gross `₹1,20,000` (`HM-1-old`), Revised gross `₹1,32,000` (`HM-1-new`), Arrears `₹12,000` (`HM-1-diff`), PF change `₹0` (`HM-1-pf`), TDS impact `₹312` (`HM-1-tds`), Paid days `31`
    * 2026-06: Old gross `₹1,12,000` (`HM-2-old`), Revised gross `₹1,23,200` (`HM-2-new`), Arrears `₹11,200` (`HM-2-diff`), PF change `₹0` (`HM-2-pf`), TDS impact `₹292` (`HM-2-tds`), Paid days `28` (2 LOP days)
    * 2026-07: Old gross `₹1,20,000` (`HM-3-old`), Revised gross `₹1,32,000` (`HM-3-new`), Arrears `₹12,000` (`HM-3-diff`), PF change `₹0` (`HM-3-pf`), TDS impact `₹312` (`HM-3-tds`), Paid days `31`
    * 2026-08: Old gross `₹1,20,000` (`HM-4-old`), Revised gross `₹1,32,000` (`HM-4-new`), Arrears `₹12,000` (`HM-4-diff`), PF change `₹0` (`HM-4-pf`), TDS impact `₹312` (`HM-4-tds`), Paid days `31`
    * 2026-09: Old gross `₹1,20,000` (`HM-5-old`), Revised gross `₹1,32,000` (`HM-5-new`), Arrears `₹12,000` (`HM-5-diff`), PF change `₹0` (`HM-5-pf`), TDS impact `₹312` (`HM-5-tds`), Paid days `30`
    * Totals: Gross Arrears `₹71,200`, Arrears-only TDS impact `₹1,852` (`H-arrears_only_tds_impact`), Recurring salary TDS impact `₹1,872` (`H-recurring_salary_tds_impact`), Net Arrears `₹67,476`
  - Plain-Language Formulas:
    * Earned salary formula: "Earned salary = monthly salary × paid days ÷ calendar days"
    * Arrears formula: "Monthly arrears = revised earned gross − old earned gross"
    * Net arrears summary: "Net Arrears = Gross Arrears (₹71,200) − Employee PF Change (₹0) − Estimated TDS Impact (₹3,724) = ₹67,476"
  - Human-Readable Rule Citations (Relevant to explained numbers only):
    * "Hike allocation rule: Proportional allocation across basic, HRA and special allowance"
    * "Rounding rule: Round each line to nearest rupee, then add rounded lines for totals (round half up)"
    * "Income tax regime: New tax regime FY 2026-27"
    * "Standard deduction: ₹75,000"
    * "Health and education cess: 4%"
    * "Rules version: Northwind demo rules v1"
    *(No file names, no JSON keys, no internal rule IDs shown to users)*
- **Resulting State:** Tapping [Approve proposal for payroll] records authorization for Version 1 and scope (2026-04 to 2026-09) in runtime store; card updates to approved state without claiming payment.

---

### Scenario 2: Back-dated hike crossing 17 September 2026 PF wage ceiling change
- **Surface:** `CHAT-HR` (Desktop 1440 px)
- **Role:** HR Admin (`HR01`)
- **Employee Context:** Arjun Rao (`E02`)
- **Turn 1 (User):** "Review back-dated hike for Arjun Rao."
- **Turn 2 (Assistant Bubble):** C03: "This is a proposal for the recorded affected months."
- **Cards Shown in Thread:**
  1. *Proposal Summary Card:* Employee: Arjun Rao (`E02`); Requested hike: `6%` (`D02-requested_hike_percentage`); Effective date: `2026-09-01` (`D02-effective_date`); Old monthly salary total: `₹20,000` (`D02-old_monthly_salary-total`); Proposed monthly salary total: `₹21,200` (`D02-proposed_monthly_salary-total`); Status: `Needs HR approval; not applied`; Certainty: `Complete for this scope`.
  2. *Number Cards Cluster:* Expected net arrears `₹7,099` (`H2-net_arrears`), Gross arrears `₹7,200` (`H2-gross_arrears`), Employee PF change `₹101` (`H2-pf`), TDS impact `₹0` (`H2-tds`).
  3. *Approval Card:* Notice C04 verbatim. Actions: Approve, Edit, Reject.
- **PANEL-HR View:**
  - September 2026 Dual-Segment PF Breakdown:
    * Segment 1 (2026-09-01 to 2026-09-16, 16 calendar days): Wage ceiling ₹15,000 until 16 Sep 2026. Pro-rated ceiling: `₹15,000 × 16 ÷ 30 = ₹8,000`.
    * Segment 2 (2026-09-17 to 2026-09-30, 14 calendar days): Wage ceiling ₹25,000 from 17 Sep 2026. Pro-rated ceiling: `₹25,000 × 14 ÷ 30 = ₹11,666.67`.
    * Total PF change across dual segments: `₹101`.
  - Human Rule Citations:
    * "PF wage ceiling: ₹15,000 until 16 Sep 2026; ₹25,000 from 17 Sep 2026"
    * "Employee PF contribution rate: 12% of PF wage"
    * "Mid-month ceiling change: Pro-rated across dated calendar segments"
    * "Rules version: Northwind demo rules v1"

---

### Scenario 3: Back-dated hike where one month's attendance is missing
- **Surface:** `CHAT-HR` (Desktop 1440 px)
- **Role:** HR Admin (`HR01`)
- **Employee Context:** Kavya Iyer (`E03`)
- **Turn 1 (User):** "Prepare hike proposal for Kavya Iyer."
- **Turn 2 (Assistant Bubble):** C07: "The required attendance record for 2026-07 is missing. I cannot explain a complete result for this scope."
- **Cards Shown in Thread:**
  1. *Incomplete Proposal Summary Card:* Employee: Kavya Iyer (`E03`); Certainty: `Incomplete`; Proposal status: `Needs HR approval; not applied`.
  2. *Number Cards Cluster:*
     - Expected net arrears: `Not available in generated data` (`H3-net_arrears` is null)
     - Gross arrears: `Not available in generated data` (`H3-gross_arrears` is null)
     - August arrears diff: `₹4,800` (`H3-diff-08`)
     - September arrears diff: `₹4,800` (`H3-diff-09`)
  3. *Approval Card:* Disabled state with notice: "Cannot approve an incomplete proposal while required records are missing."
- **PANEL-HR View:**
  - Monthly Arrears Table: 2026-07 row shows "Attendance missing: Not available in generated data"; 2026-08 shows `₹4,800`; 2026-09 shows `₹4,800`.
  - Human Rule Citations: "Calendar-month divisor: Paid days equal eligible days up to last working day minus LOP", "Rules version: Northwind demo rules v1".

---

### Scenario 4: Bonus for team with mid-year joiner and notice period
- **Surface:** `CHAT-HR` (Desktop 1440 px)
- **Role:** HR Admin (`HR01`)
- **Turn 1 (User):** "Calculate Annual and Sales bonus runs."
- **Turn 2 (Assistant Bubble):** C03: "This is a proposal for the recorded affected months."
- **Cards Shown in Thread:**
  1. *Bonus Summary Card:* Period: `FY 2025-26`; Eligible employee count: `3` (`B-AGG-eligible_count`); Ineligible count: `1` (`B-AGG-ineligible_count`); Needs input count: `1` (`B-AGG-needs_input_count`); Gross eligible total: `₹2,13,929` (`B-AGG-eligible_gross_total`).
  2. *Approval Card:* Notice C04 verbatim.
- **PANEL-HR View:**
  - Employee Eligibility Grid:
    * Priya Sharma (`E01`): Annual bonus `₹1,08,000` (`B-E01-amount`), TDS `₹27,000`, Net `₹81,000`.
    * Kavya Iyer (`E03`): Annual bonus `₹36,000` (`B-E03-amount`), TDS `null`, Net `null`.
    * Rohan Mehta (`E04`): Annual bonus `₹60,000` (`B-E04-amount`), TDS `₹15,000`, Net `₹45,000`.
    * Sneha Kulkarni (`E07`): Mid-year joiner prorated `₹9,929` (`B-E07-amount`), TDS `₹2,482`, Net `₹7,447` (Prorated: joined 2025-11-01, 151 eligible days / 365).
    * Vikram Singh (`E08`): Ineligible `₹0` (`B-E08-amount`) (Flag: "On notice at the time of calculation").
    * Meera Nair (`E09`): Needs input `Not available in generated data` (`B-E09-amount` is null) (Flag: "Performance record missing").
  - Human Rule Citations: "Annual performance bonus policy: Target percentage based on performance rating", "Notice period exclusion: Employees serving notice at bonus run are ineligible", "Rules version: Northwind demo rules v1".

---

### Scenario 5: Bonus where one employee's performance data is missing
- **Surface:** `CHAT-HR` (Desktop 1440 px)
- **Role:** HR Admin (`HR01`)
- **Employee Context:** Meera Nair (`E09`)
- **Turn 1 (User):** "Check bonus eligibility for Meera Nair (E09)."
- **Turn 2 (Assistant Bubble):** C07: "The required performance record for FY 2025-26 is missing. I cannot explain a complete result for this scope."
- **Cards Shown in Thread:**
  1. *Incomplete Bonus Card:* Employee: Meera Nair (`E09`); Period: `FY 2025-26`; Rating: `null`; Bonus amount: `Not available in generated data`; Certainty: `Incomplete`; Flag: "Performance record missing".
  2. *Approval Card:* Unavailable.
- **PANEL-HR View:** Rule citation: "Annual performance bonus policy: Requires completed performance rating for FY 2025-26 (Missing required record)", "Rules version: Northwind demo rules v1".

---

### Scenario 6: Full and final settlement for an employee eligible for gratuity
- **Surface:** `CHAT-HR` (Desktop 1440 px)
- **Role:** HR Admin (`HR01`)
- **Employee Context:** Rahul Verma (`E10`)
- **Turn 1 (User):** "Prepare full and final settlement for Rahul Verma (E10)."
- **Turn 2 (Assistant Bubble):** C03: "This is a proposal for the recorded affected months."
- **Cards Shown in Thread:**
  1. *Settlement Summary Card:* Employee: Rahul Verma (`E10`); Last working day: `2026-10-03` (`S6-lwd`); Joining date: `2019-06-01`; Service: `7 years, 4 months, 3 days`; Certainty: `Complete for this scope`.
  2. *Component List Card:*
     - Hero Final Net: `₹3,32,256` (`S6-net_amount`)
     - Gross Payables: `₹3,35,256` (`S6-gross_payables`)
     - Total Deductions: `₹1,975` (`S6-total_deductions`)
     - Earned Salary (October): `₹6,774` (`S6-earned_salary-amount`)
     - Gratuity: `₹2,01,923` (`S6-gratuity-amount`), Status: "Eligible (> 5 years service)", Applicable due date: `2026-11-03` (`S6-gratuity-date`)
     - Leave Encashment: `₹1,26,559` (`S6-leave_encashment-amount`), Applicable due date: `2026-10-10` (`S6-leave_encashment-date`)
     - Notice Shortfall Recovery: `₹0` (`S6-notice_shortfall_recovery-amount`), Applicable due date: `null`
  3. *Approval Card:* Notice C04 verbatim. Actions: Approve, Edit, Reject.
- **PANEL-HR View:**
  - Gratuity Plain-Language Formula: "Gratuity = 15 × last drawn basic salary × completed years of service ÷ 26 = 15 × ₹50,000 × 7 ÷ 26 = ₹2,01,923"
  - Human Rule Citations: "Payment of Gratuity: 15/26 days basic salary per year of service for tenure ≥ 5 years", "Leave encashment: Earned leave balance paid at daily basic rate", "Settlement due dates: Gratuity within 30 days of exit, final payables on normal payroll run", "Rules version: Northwind demo rules v1".

---

### Scenario 7: Full and final settlement for employee just below gratuity eligibility
- **Surface:** `CHAT-HR` (Desktop 1440 px)
- **Role:** HR Admin (`HR01`)
- **Employee Context:** Lakshmi Reddy (`E11`)
- **Turn 1 (User):** "Review settlement for Lakshmi Reddy (E11)."
- **Turn 2 (Assistant Bubble):** C03: "This is a proposal for the recorded affected months."
- **Cards Shown in Thread:**
  1. *Settlement Summary Card:* Employee: Lakshmi Reddy (`E11`); Last working day: `2026-10-15` (`S7-lwd`); Joining date: `2021-11-20`; Service: `4 years, 10 months, 26 days`; Certainty: `Complete for this scope`.
  2. *Component List Card:*
     - Final Net: `₹1,47,040` (`S7-net_amount`)
     - Gross Payables: `₹150,186` (`S7-gross_payables`)
     - Total Deductions: `₹3,146` (`S7-total_deductions`)
     - Earned Salary (October): `₹24,194` (`S7-earned_salary-amount`)
     - Gratuity: `₹0` (`S7-gratuity-amount`), Status: "Ineligible (Under 5 years service)", Flag: "Close to minimum service: 4 years, 8 months, 24 days" (`S7-gratuity-flag`), Applicable due date: `null` (`S7-gratuity-date`)
     - Leave Encashment: `₹1,25,992` (`S7-leave_encashment-amount`), Applicable due date: `2026-10-10` (`S7-leave_encashment-date`)
  3. *Approval Card:* Notice C04 verbatim.
- **PANEL-HR View:** Human Rule citation: "Gratuity eligibility: Minimum 5 years of continuous service required. Recorded tenure of 4 years, 10 months is ineligible", "Rules version: Northwind demo rules v1".

---

### Scenario 8: Full and final settlement with pending asset clearance and notice shortfall
- **Surface:** `CHAT-HR` (Desktop 1440 px)
- **Role:** HR Admin (`HR01`)
- **Employee Context:** Imran Khan (`E12`)
- **Turn 1 (User):** "Review exit recovery for Imran Khan (E12)."
- **Turn 2 (Assistant Bubble):** C19: "The final net is incomplete because unreturned company laptop is not yet known."
- **Cards Shown in Thread:**
  1. *Incomplete Settlement Card:* Employee: Imran Khan (`E12`); Last working day: `2026-10-05` (`S8-lwd`); Certainty: `Incomplete`.
  2. *Component List Card:*
     - Final Net: `Not available in generated data` (`S8-net_amount` is null)
     - Earned Salary: `₹8,065` (`S8-earned_salary-amount`)
     - Leave Encashment: `₹48,387` (`S8-leave_encashment-amount`)
     - Notice Shortfall Recovery: `₹56,667` (`S8-notice_shortfall_recovery-amount`) (Shortfall: 35 days, waiver: false)
     - Asset Recovery: `Unresolved` (Laptop not returned, cost pending assessment)
  3. *Approval Card:* Disabled for final net; partial approval allowed only for verified earnings per DEC-014.
- **PANEL-HR View:** Asset clearance pending notice ("Company laptop clearance unconfirmed"). Human Rule Citations: "Notice shortfall recovery: Daily basic rate × shortfall days", "Asset recovery: Pending clearance verification", "Rules version: Northwind demo rules v1".

---

### Scenario 9: Employee whose salary dropped because of LOP
- **Surface:** `CHAT-EMP` (Mobile 390 px)
- **Role:** Employee (Neha Gupta, `E05`)
- **Turn 1 (User):** "Why is my take-home pay lower in September?"
- **Turn 2 (Assistant Bubble — C30 verbatim):** "Your September take-home is ₹5,420 lower than August. The main recorded reasons are below."
- **Cards Shown in Thread:**
  1. *Hero Number Card (Indian Rupee format with real minus sign):*
     - September Take-Home Pay: `₹42,780` (Binding: `C9-after-net`)
     - Take-Home Net Change: `−₹5,420` (`C9-net_change`)
     - August Take-Home Pay: `₹48,200` (`C9-before-net`)
     - Certainty: `Complete for this scope`
  2. *Reason List Card (Ranked by effect on take-home pay):*
     - Reason 1: Loss of Pay (LOP) 3 unpaid days, effect: `−₹5,000` (Binding: `X-021`)
     - Reason 2: PF ceiling change, effect: `−₹420` (Binding: `X-024`)
     - Note: Sourced TDS change: `₹0` (`C9-tds_change`)
  3. *Action Control:* [Show calculation] (Opens `SHEET-EMP`).
- **Turn 2 Follow-up Offer (Assistant Bubble — C27 verbatim):** "Would you like the earnings and deductions breakdown?"
- **Suggestion Chips:** [Draft a query for HR] [What is LOP?] [What is PF?]
- **SHEET-EMP View (Open State):**
  - Pay Comparison Breakdown:
    * August 2026: Gross `₹50,000` (`C9-before-gross`), Deductions `₹1,800` (PF `₹1,800`, TDS `₹0`), Net `₹48,200` (`C9-before-net`), Paid days `31`
    * September 2026: Gross `₹45,000` (`C9-after-gross`), Deductions `₹2,220` (PF `₹2,220`, TDS `₹0`), Net `₹42,780` (`C9-after-net`), Paid days `27` (`C9-after-paid`), Calendar days `30` (`D09-months-2026-09-calendar_days`), Unpaid LOP days `3` (`D09-months-2026-09-lop_days`)
  - Plain-Language Formulas:
    * Earned salary: "Earned salary = monthly salary × paid days ÷ calendar days"
    * LOP deduction effect: "Earned gross decreased from ₹50,000 to ₹45,000 (−₹5,000), reducing take-home pay by ₹5,000"
    * PF statutory ceiling change: "PF deduction increased from ₹1,800 to ₹2,220 (+₹420), reducing take-home pay by ₹420"
    * Take-home net change: "Take-home pay = earned gross − total employee deductions = ₹45,000 − ₹2,220 = ₹42,780 (change: −₹5,420)"
  - Human-Readable Rule Citations (Relevant to explained numbers only):
    * "PF wage ceiling: ₹15,000 until 16 Sep 2026; ₹25,000 from 17 Sep 2026"
    * "Employee PF contribution rate: 12% of PF wage"
    * "Calendar-month divisor: Paid days equal calendar days minus LOP days"
    * "Rules version: Northwind demo rules v1"
    *(No file names, no JSON keys, no internal rule IDs shown to users)*

---

### Scenario 10: Employee whose TDS increased due to previous-employer income declaration
- **Surface:** `CHAT-EMP` (Mobile 390 px)
- **Role:** Employee (Siddharth Jain, `E06`)
- **Turn 1 (User):** "Why did my TDS deduction increase in September?"
- **Turn 2 (Assistant Bubble — C30 verbatim):** "Your September take-home is ₹13,014 lower than August. The main recorded reasons are below."
- **Cards Shown in Thread:**
  1. *Hero Number Card (Indian Rupee format with real minus sign):*
     - September Take-Home Pay: `₹1,05,186` (Binding: `C10-after-net_pay`)
     - Take-Home Net Change: `−₹13,014` (`C10-net_change`)
     - August Take-Home Pay: `₹1,18,200` (`C10-before-net_pay`)
     - September TDS: `₹12,454` (`C10-after-tds`)
     - August TDS: `₹0` (`C10-before-tds`)
     - TDS Increase: `₹12,454` (`C10-tds_change`)
     - Certainty: `Complete for this scope`
  2. *Reason List Card (Ranked by effect on take-home pay):*
     - Reason 1: TDS change (Previous-employer income declaration), effect: `−₹12,454` (Binding: `X-028`)
     - Reason 2: PF ceiling change, effect: `−₹560` (Binding: `X-031`)
  3. *Action Control:* [Show tax calculation] (Opens `SHEET-EMP`).
- **Turn 2 Cause Explanation (Assistant Bubble — C29 preview):** "Your TDS is higher because you declared income from your previous employer for Not available in generated data. That income is added to your yearly income, so your expected yearly tax is higher. The tax your previous employer already deducted is counted, so it is not deducted twice."
- **Turn 2 Follow-up Offer (Assistant Bubble — C27 verbatim):** "Would you like the earnings and deductions breakdown?"
- **Suggestion Chips:** [Draft a query for HR] [What is TDS?] [What is PF?]
- **SHEET-EMP View (Open State):**
  - Tax Calculation Detail:
    * Declared previous-employer gross: `₹4,50,000` (`D10-previous_employer_declared_gross`)
    * Declared previous-employer TDS: `₹15,000` (`D10-previous_employer_tds`)
    * Northwind TDS already deducted: `₹0` (`D10-northwind_tds_already_deducted`)
    * Remaining yearly tax: `₹87,180` (`D10-remaining_yearly_tax`) spread over remaining 7 months
    * Regime: `New tax regime FY 2026-27` (`T-regime`)
  - Assistant Sentence C22 verbatim: "The payroll calculation detail includes projected yearly income, applied deductions and exemptions, yearly tax, tax already deducted and remaining months. It identifies your recorded tax regime and applicable rule version."
  - Plain-Language Formulas:
    * Monthly TDS: "Monthly TDS = remaining yearly tax ÷ remaining months in financial year = ₹87,180 ÷ 7 = ₹12,454"
  - Human Rule Citations (Relevant to explained numbers only):
    * "Previous-employer income inclusion: Declared gross added to taxable income, declared TDS credited against tax payable"
    * "Tax regime: New tax regime FY 2026-27"
    * "Standard deduction: ₹75,000"
    * "Health and education cess: 4%"
    * "Rules version: Northwind demo rules v1"

---

### Scenario 11: Employee with no salary earning change between two months
- **Surface:** `CHAT-EMP` (Mobile 390 px)
- **Role:** Employee (Pooja Das, `E16`)
- **Turn 1 (User):** "Did my basic pay or allowance change in September?"
- **Turn 2 (Assistant Bubble — C30 verbatim):** "Your September take-home is ₹420 lower than August. The main recorded reasons are below."
- **Cards Shown in Thread:**
  1. *Hero Number Card:*
     - September Take-Home Pay: `₹37,780` (Binding: `C11-after-net`)
     - Take-Home Net Change: `−₹420` (`C11-net_change`)
     - August Take-Home Pay: `₹38,200` (`C11-before-net`)
     - Certainty: `Complete for this scope`
  2. *Informational Card:* "No salary earning component change. Gross earnings unchanged at ₹40,000."
  3. *Reason List Card:* PF ceiling change, effect: `−₹420` (Binding: `X-038`)
  4. *Action Control:* [Show calculation] (Opens `SHEET-EMP`).
- **Turn 2 Follow-up Offer (Assistant Bubble — C27 verbatim):** "Would you like the earnings and deductions breakdown?"
- **Turn 2 Boundary (Assistant Bubble — C26 verbatim):** "This explains the recorded months. I cannot promise next month's pay. It depends on that month's recorded inputs and applicable rules."
- **Suggestion Chips:** [Draft a query for HR] [What is PF?]
- **SHEET-EMP View:**
  - Proof showing basic unchanged at `₹20,000`, special allowance unchanged at `₹20,000`, gross earnings unchanged at `₹40,000`; PF deduction increased from `₹1,800` to `₹2,220` (+₹420) due to statutory ceiling revision on 17 September.
  - Plain-Language Formulas:
    * "Take-home pay = earned gross − total employee deductions = ₹40,000 − ₹2,220 = ₹37,780 (change: −₹420)"
  - Human Rule Citations (Relevant to explained numbers only):
    * "PF wage ceiling: ₹15,000 until 16 Sep 2026; ₹25,000 from 17 Sep 2026"
    * "Employee PF contribution rate: 12% of PF wage"
    * "Rules version: Northwind demo rules v1"

---

### Scenario 12: Employee trying to see another employee's salary
- **Surface:** `CHAT-EMP` (Mobile 390 px)
- **Role:** Employee (`USER-E05` / Neha Gupta)
- **Turn 1 (User):** "What is Priya Sharma's monthly salary?"
- **Turn 2 (Assistant Bubble):** C10: "I cannot provide that information. I can help with payroll records you are authorized to access."
- **Cards Shown in Thread:**
  1. *Refusal Card:* Displays C10 verbatim, red warning border, zero target details (no employee name, no ID, no salary figures rendered).
  2. *Suggestion Chips:* [Ask about my payroll] [What is LOP?] [What is PF?]
- **Resulting State:** Target employee context is wiped; access boundary enforced.

---

### Scenario 13: Unresolved settlement component alongside confirmed component
- **Surface:** `CHAT-HR` (Desktop 1440 px)
- **Role:** HR Admin (`HR01`)
- **Employee Context:** Imran Khan (`E12`)
- **Turn 1 (User):** "Review settlement breakdown for Imran Khan (E12)."
- **Turn 2 (Assistant Bubble):** C19: "The final net is incomplete because unreturned company laptop is not yet known."
- **Cards Shown in Thread:**
  1. *Incomplete Settlement Summary Card:* Employee: Imran Khan (`E12`); Certainty: `Incomplete`.
  2. *Component List Card:*
     - Final Net: `Not available in generated data` (`S13-net_amount` is null)
     - Known Recoveries Subtotal: `₹56,667` (`S13-recoveries_subtotal`)
     - Notice Shortfall Recovery: `₹56,667` (`S13-notice_shortfall_recovery-amount`), Status: "Verified"
     - Asset Recovery: `Unresolved` (Laptop clearance pending)
  3. *Partial Approval Card:* Notice (DEC-014): "Approving verified component lines only. Unresolved asset recovery remains held and excluded from net payout."

---

## 3. General Payroll FAQ Conversations (Course Dataset Format)

FAQ responses use the course dataset format (`id`, `category`, `question`, `answer`, `link_text`, `url`). Answers are taken verbatim from the approved payroll glossary in `output/06-ai-interaction/conversation-design.md`, Section 6. Citation links are hidden in UI when url is "To be defined in the payroll FAQ file".

### FAQ Conversation 1: Loss of Pay (LOP)
- **Surface:** `CHAT-EMP` (Mobile 390 px)
- **Turn 1 (User):** "What is LOP?"
- **Turn 2 (Assistant):**
  - Bubble: "Here is the recorded meaning from the payroll glossary:"
  - *FAQ Answer Card:*
    * `id`: `FAQ-PAY-01`
    * `category`: `Glossary`
    * `question`: "What is LOP?"
    * `answer`: "Unpaid leave days used to work out paid days for salary."
    * `link_text`: "To be defined in the payroll FAQ file"
    * `url`: "To be defined in the payroll FAQ file"
    * Note: Citation link is hidden when url is "To be defined in the payroll FAQ file".
  - Suggestion Chips: [Why is my take-home pay lower in September?] [What is PF?]

### FAQ Conversation 2: Provident Fund (PF)
- **Surface:** `CHAT-EMP` (Mobile 390 px)
- **Turn 1 (User):** "What is PF?"
- **Turn 2 (Assistant):**
  - Bubble: "Here is the recorded meaning from the payroll glossary:"
  - *FAQ Answer Card:*
    * `id`: `FAQ-PAY-02`
    * `category`: `Glossary`
    * `question`: "What is PF?"
    * `answer`: "Provident Fund contribution recorded in payroll, based on the applicable PF wage and rule."
    * `link_text`: "To be defined in the payroll FAQ file"
    * `url`: "To be defined in the payroll FAQ file"
    * Note: Citation link is hidden when url is "To be defined in the payroll FAQ file".
  - Suggestion Chips: [Why did my PF change in September?] [What is LOP?]

### FAQ Conversation 3: Gratuity
- **Surface:** `CHAT-HR` (Desktop 1440 px)
- **Turn 1 (User):** "What is Gratuity?"
- **Turn 2 (Assistant):**
  - Bubble: "Here is the recorded meaning from the payroll glossary:"
  - *FAQ Answer Card:*
    * `id`: `FAQ-PAY-03`
    * `category`: `Glossary`
    * `question`: "What is Gratuity?"
    * `answer`: "A settlement payment that applies only when the employee meets the configured eligibility rule."
    * `link_text`: "To be defined in the payroll FAQ file"
    * `url`: "To be defined in the payroll FAQ file"
    * Note: Citation link is hidden when url is "To be defined in the payroll FAQ file".
  - Suggestion Chips: [Prepare full and final settlement for Rahul Verma (E10)] [Review settlement for Lakshmi Reddy (E11)]

---

## 4. Fallback Handling and Agentic CrewAI Architecture

### 4.1. Prototype Intent Matching Fallback
Until real AI models are connected, typed input in the composer is matched against supported demo keywords (e.g. employee names, "hike", "bonus", "settlement", "LOP", "TDS", "query").
If the input cannot be mapped, the assistant displays:
> "I cannot answer that question in this demo. You can ask about recorded salary and tax changes, full and final settlements, bonus eligibility, or choose a topic below:"
followed by relevant suggestion chips. The prototype never hallucinates, estimates, or makes invented promises.

### 4.2. CrewAI Multi-Agent Handoff Architecture
The prototype is structured so a future CrewAI agentic crew can replace demo pattern matching without changing cards or UI bindings:
1. **Classifier Agent:** Parses natural language query, detects user role (`HR Admin` vs `Employee`), extracts intent, and performs initial RBAC routing.
2. **Retrieval Agent:** Queries the Payroll FAQ Knowledge Source (`data/faq/`) and deterministic calculation engine (`engine/payroll/`) for verified numbers, formulas, and rule IDs.
3. **Response Drafting Agent:** Selects the required approved sentence (C01–C30) and populates rich card schemas with deterministic values.
4. **Governance / Guard Agent:** Verifies epistemic certainty labels, ensures zero frontend math, blocks cross-employee data leaks, and confirms that approval never resembles payment.

---

## 5. Query Lifecycle State Machine

Employee payroll queries follow an explicit, state-machine driven lifecycle:
- **`Draft`:** Stored locally in conversation context. Not sent to HR. Can be edited or canceled. Sentence C17 applies if unsent.
- **`Sent`:** Persisted to runtime store upon user confirmation (C12/C13). Available for HR review. Sentence C15 applies.
- **`In review`:** HR administrator has taken the query into active review. Sentence C16 applies.
- **`Resolved`:** HR administrator has recorded an explicit resolution reply. Sentence C23 applies. Employee can accept or dispute.
- **`Closed`:** Explicitly acknowledged and closed. History retained. Sentence C24 applies.

---

## 6. Information Security and Epistemic Governance

1. **No "Verified" Badges:** The assistant uses standard sender labels without celebratory or unearned trust marks.
2. **No Technical Leaks:** No screen IDs (`SCR-01`), file paths (`data/generated/...`), sentence codes (`C01`), or rule pointers are shown to users. These exist solely in designer bindings and audit metadata.
3. **Strict Epistemic Certainty:** Every card carries one of the five approved certainty labels:
   - `Complete for this scope`
   - `Incomplete`
   - `Rule not verified`
   - `Needs HR decision`
   - `Cannot explain from available payroll data`
4. **Approval vs Payment Decoupling:** Proposal approval authorizes records as ready for payroll. It never triggers or implies banking disbursement.

---

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

### C30

> Your {later month} take-home is {net change amount} {lower or higher} than {earlier month}. The main recorded reasons are below.

Source: [conversation-design.md](../06-ai-interaction/conversation-design.md), Section 7, A06-07; Example B; Approved DEC-035.

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
