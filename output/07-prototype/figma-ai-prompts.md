# HCM One: Figma AI Prompts (Chat-First Architecture)

Updated for Gate G07. These prompts are self-contained, production-grade instructions designed for AI design tools (e.g. Figma AI, Galileo AI, v0, Relume) to generate high-fidelity UI frames for HCM One's **chat-first interface with rich cards**.

The interface consists of two primary responsive surfaces:
1. **`CHAT-HR` — HR Admin Chat Workspace (Desktop 1440 px)**: Full desktop workspace featuring a primary conversation feed, rich payroll cards, and a collapsible Right Side Panel (`PANEL-HR`, 480 px) for dense calculation proofs and multi-month settlement ledgers.
2. **`CHAT-EMP` — Employee Chat Workspace (Mobile 390 px)**: Mobile conversational feed featuring structured explanation cards, suggestion chips, and an interactive Bottom Sheet (`SHEET-EMP`, max 85vh) for calculation breakdowns and statutory definitions.

---

## 1. Prompt: CHAT-HR — HR Admin Chat Workspace (Desktop 1440 px)

Paste the block below into your AI design tool to generate the desktop HR chat workspace:

```text
Design a high-fidelity enterprise HR Admin chat workspace for "HCM One", an agentic AI payroll platform.
Viewport: Desktop, 1440 px wide by 900 px high.
Color palette: Clean white (#FFFFFF) background, subtle surface fills (#F8FAFC), 1 px slate dividers (#E2E8F0), dark slate text (#0F172A), secondary slate text (#475569), and a single deep teal accent color (#0F766E). No ornamental gradients, illustrations, or celebratory confetti.
Typography: Inter font throughout. Tabular figures (tnum) for all numbers, dates, currency, and table columns. Monospace only for technical identifiers (Query IDs, record references). No "Verified" badges anywhere. No file paths or screen IDs visible to users.

Layout Structure:
1. Top App Header (Height: 64 px, sticky top):
   - Left: Brand logo "HCM One" (Deep teal mark) with workspace title "HR Payroll Workspace".
   - Center-Right: Active Session Pill "Period: October 2026", Role badge "HR Admin", and User profile avatar.
2. Two-Column Split Workspace:
   - Left / Main Chat Column (Width: 960 px): Conversational thread with sticky bottom composer.
   - Right Side Panel (Width: 480 px, border-left: 1 px #E2E8F0, full height): Dedicated review panel shown in its OPEN state titled "Calculation Proof — Priya Sharma Arrears".

Left Chat Column Content (Scenario 1: Priya Sharma Back-dated Hike Review):
- Timestamp divider: "Today, 10:14 AM"
- User Message Bubble (Right-aligned, slate background #F1F5F9, text #0F172A, max-width 560 px):
  "Prepare Priya Sharma's pending back-dated hike."
- Assistant Message Container (Left-aligned, full width):
  - Assistant Sender Header: Teal spark avatar, "HCM One Assistant", and timestamp "10:14 AM".
  - Approved AI Sentence (Exact C03): "This is a proposal for the recorded affected months."
  - Proposal Summary Card (Border 1 px #E2E8F0, radius 8 px, padding 16 px, white background):
    * Card Title: "Back-dated Hike Proposal — Priya Sharma (E01)"
    * Status Badges: Certainty pill "Complete for this scope" (green #166534 on #F0FDF4) and Workflow pill "Needs HR approval; not applied".
    * Metadata Grid (3 columns): Requested Hike: "10%", Effective Date: "2026-04-01", Affected Periods: "6 months (2026-04 to 2026-09)".
    * Salary Comparison: Old Monthly Salary Total: "₹1,20,000" → Proposed Monthly Salary Total: "₹1,32,000".
  - Number Cards Cluster (Grid of 4 cards, tabular figures):
    * Hero Card: "Expected net arrears: ₹67,476" (Large 40 px semi-bold text, tabular figures, deep teal border accent).
    * Secondary Card 1: "Gross arrears: ₹71,200".
    * Secondary Card 2: "Employee PF change: ₹0" (Capped at statutory ceiling).
    * Secondary Card 3: "Estimated TDS impact: ₹3,724" (Estimate flag: "Estimated TDS if approved and paid in October 2026 payroll", Sourced month: "2026-10").
  - Month Table Card Summary (Mini preview with link):
    * Summary line: "6 affected months (2026-04 to 2026-09) • Total Gross Arrears ₹71,200".
    * Active Trigger Button: "Show calculation & full month breakdown →" (Active state, deep teal text #0F766E with calculator icon).
  - Approval Card (Border 1 px #CBD5E1, radius 8 px, padding 16 px, background #F8FAFC):
    * Notice text (Exact C04): "Approving records this version and the selected scope as ready for payroll. It does not apply the change or make a payment."
    * Action Buttons:
      - Primary: "Approve proposal for payroll" (Deep teal button #0F766E, white text, height 40 px, radius 6 px).
      - Secondary: "Edit with reason" (White button, border 1 px #64748B, text #0F172A).
      - Tertiary: "Reject proposal" (White button, border 1 px #B91C1C, text #B91C1C).
- Suggestion Chips Row (Above composer):
  - Pill buttons: "Compare April vs June attendance", "Check PF ceiling rule basis", "Download proposal summary".
- Sticky Bottom Composer (Height: 80 px, border-top 1 px #E2E8F0, white background):
  - Textarea with placeholder: "Ask about payroll proposals, arrears, or query resolution...", Send button (Deep teal with send icon).

Right Side Panel Content ("PANEL-HR" — Open State):
- Header (Height: 64 px, sticky top, border-bottom 1 px #E2E8F0, padding: 0 20 px):
  - Title: "Calculation Proof — Priya Sharma Arrears"
  - Close button: "✕ Close" (Accessible button, top right).
- Panel Body (Scrollable, padding 20 px):
  - Section 1: Month-by-Month Breakdown Table (Tabular figures, dense 13 px font):
    * Columns: Month | Old Gross | Revised Gross | Arrears | TDS Impact
    * Row 1: 2026-04 | ₹1,20,000 | ₹1,32,000 | ₹12,000 | ₹312
    * Row 2: 2026-05 | ₹1,20,000 | ₹1,32,000 | ₹12,000 | ₹312
    * Row 3: 2026-06 | ₹1,12,000 | ₹1,23,200 | ₹11,200 | ₹292 (2 LOP days)
    * Row 4: 2026-07 | ₹1,20,000 | ₹1,32,000 | ₹12,000 | ₹312
    * Row 5: 2026-08 | ₹1,20,000 | ₹1,32,000 | ₹12,000 | ₹312
    * Row 6: 2026-09 | ₹1,20,000 | ₹1,32,000 | ₹12,000 | ₹312
    * Total Row: Gross Arrears ₹71,200 | Arrears-only TDS ₹1,852 | Recurring TDS ₹1,872 | Net Arrears ₹67,476.
  - Section 2: Calculation Formula Breakdown (Plain-language formulas):
    * Formula in words: "Net Arrears = Gross Arrears (₹71,200) − Employee PF Change (₹0) − Estimated TDS Impact (₹3,724) = ₹67,476".
  - Section 3: Statutory Rules & Metadata (Human labels only):
    * "Hike allocation rule: Proportional allocation across basic, HRA and special allowance"
    * "Rounding rule: Round each line to nearest rupee, then add rounded lines for totals (round half up)"
    * "Income tax regime: New tax regime FY 2026-27"
    * "Standard deduction: ₹75,000"
    * "Health and education cess: 4%"
    * Metadata: Rules version: "Northwind demo rules v1", Verified on: "2026-10-13", Date note: "Applies to all demo periods".
```

---

## 2. Prompt: CHAT-EMP — Employee Chat Workspace (Mobile 390 px)

Paste the block below into your AI design tool to generate the mobile Employee chat workspace:

```text
Design a high-fidelity mobile conversational interface for "HCM One", an agentic AI employee payroll app.
Viewport: Mobile, 390 px wide by 844 px high (iPhone 14/15 reference frame).
Color palette: Clean white (#FFFFFF) background, thread background (#F8FAFC), dark slate text (#0F172A), muted slate text (#475569), 1 px borders (#E2E8F0), and a single deep teal accent (#0F766E). No charts, decorative gradients, or playful mascots. No "Verified" badges anywhere. No file paths or screen IDs visible to users.
Typography: Inter font. Tabular figures (tnum) for all numbers, currency amounts, and dates. Monospace for query tracking IDs.

Layout Structure:
1. Mobile Header (Height: 56 px, sticky top):
   - Left: HCM One logo mark + "HCM One Employee".
   - Right: Help icon (?) and Employee avatar ("Neha Gupta").
2. Chat Feed Area (Scrollable, 16 px padding):
   - Conversational turn explaining September take-home pay drop (Scenario 9).
3. Sticky Mobile Composer (Height: 64 px, sticky bottom):
   - Input pill "Ask about your pay, deductions, or query...", Send button (Teal circle with arrow).
4. Interactive Bottom Sheet ("SHEET-EMP", Shown in OPEN overlay state, height 75vh, border-radius 16 px 16 px 0 0):
   - Backdrop: Darkened overlay behind sheet (#0F172A at 40% opacity).

Mobile Chat Feed Content (Scenario 9: September Salary Drop Inquiry):
- Timestamp: "Yesterday, 6:30 PM"
- User Message Bubble (Right-aligned, slate background #F1F5F9, text #0F172A, max-width 85%):
  "Why is my take-home pay lower in September?"
- Assistant Message Turn (Left-aligned):
  - Header: Assistant avatar, "HCM One Assistant", "6:30 PM".
  - Assistant Text Bubble (White background, border 1 px #E2E8F0, padding 14 px, radius 12 px):
    * Exact Approved Copy (C30): "Your September take-home is ₹5,420 lower than August. The main recorded reasons are below."
  - Hero Number Card (Full width inside thread, radius 8 px, border 1 px #E2E8F0, background #FFFFFF, padding 16 px):
    * Label: "September Take-Home Pay"
    * Amount Hero: "₹42,780" (Large 32 px semi-bold text, tabular figures).
    * Change Tag: "−₹5,420 vs August (₹48,200)" (Muted slate with down arrow).
    * Certainty Pill: "Complete for this scope" (Green #166534 on #F0FDF4).
  - Reason List Card (Border 1 px #E2E8F0, radius 8 px, background #FFFFFF, padding 14 px):
    * Card Heading: "Ranked by effect on take-home pay"
    * Item 1: "1. Loss of Pay (LOP) — 3 Unpaid Days"
      - Impact: "−₹5,000" (Right-aligned tabular figure).
      - Detail: "Based on 30 calendar days in September".
    * Item 2: "2. PF ceiling change"
      - Impact: "−₹420" (Right-aligned tabular figure).
      - Detail: "Statutory ceiling revision on 17 September".
    * Sourced Note: "TDS change: ₹0".
  - Card Action Control:
    * Secondary button: "Show calculation" (Deep teal text #0F766E, border 1 px #0F766E, background #F0FDFA, full width, height 40 px, calculator icon).
  - Follow-up Offer Bubble (White background, border 1 px #E2E8F0, padding 14 px, radius 12 px):
    * Exact Approved Copy (C27): "Would you like the earnings and deductions breakdown?"
- Horizontal Suggestion Chips Carousel:
  - Pills: "Draft a query for HR", "What is LOP?", "What is PF?".

Mobile Bottom Sheet Content ("SHEET-EMP" — Open State):
- Drag Handle: Centered gray pill (36 px by 4 px, #CBD5E1) at top.
- Sheet Header: Title "Calculation Proof — September Pay Drop", Close button (✕) at right.
- Sheet Body:
  - Section 1: Pay Breakdown Comparison:
    * August 2026: Gross ₹50,000, Deductions ₹1,800 (PF ₹1,800, TDS ₹0), Net ₹48,200, Paid days 31.
    * September 2026: Gross ₹45,000, Deductions ₹2,220 (PF ₹2,220, TDS ₹0), Net ₹42,780, Paid days 27, Calendar days 30, Unpaid LOP days 3.
  - Section 2: Formulas in Words (Plain language):
    * Earned salary: "Earned salary = monthly salary × paid days ÷ calendar days"
    * LOP Formula: "Take-home effect of LOP: Gross decreased from ₹50,000 to ₹45,000 (−₹5,000), reducing take-home pay by ₹5,000".
    * PF Formula: "Take-home effect of PF ceiling change: PF deduction increased from ₹1,800 to ₹2,220 (+₹420), reducing take-home pay by ₹420".
    * Net change: "Take-home pay = earned gross − total employee deductions = ₹45,000 − ₹2,220 = ₹42,780 (change: −₹5,420)".
  - Section 3: Statutory Rules (Human labels only):
    * "PF wage ceiling: ₹15,000 until 16 Sep 2026; ₹25,000 from 17 Sep 2026"
    * "Employee PF contribution rate: 12% of PF wage"
    * "Calendar-month divisor: Paid days equal calendar days minus LOP days"
    * "Rules version: Northwind demo rules v1"
  - Section 4: Action:
    * Button: "Draft a query for HR" (Teal button #0F766E, white text, height 44 px).
```

---

## 3. Supplementary Card Prompts (Component Variations)

### Prompt 3A: Full & Final Settlement Ledger Card (Scenario 6 / Rahul Verma E10)
```text
Design a desktop Component List Card for an HR chat thread reviewing a Full and Final Settlement (Scenario 6).
Container: 1 px border #E2E8F0, white background, radius 8 px, padding 20 px.
Header: "Full & Final Settlement — Rahul Verma (E10)" with Certainty Pill "Complete for this scope" (Green #166534 on #F0FDF4).
Component Ledger Table (Tabular figures):
- Earned Salary (October): 6774 INR [Eligible • Due date: 2026-10-10]
- Gratuity (Service: 7 years, 4 months): 201923 INR [Eligible • Due date: 2026-11-03]
- Leave Encashment: 126559 INR [Eligible • Due date: 2026-10-10]
- Total Deductions: 1975 INR [Due date: 2026-10-10]
Net Total Row: "Final Net Amount: 332256 INR".
Action Notice (C04): "Approving records this version and the selected scope as ready for payroll. It does not apply the change or make a payment."
Actions: [Approve proposal for payroll] [Edit with reason] [Reject proposal].
```

### Prompt 3B: Clarifying Question Card (Scenario 2 / Missing Effective Date)
```text
Design an in-thread Clarifying Question Card for CHAT-HR when a required proposal date is missing.
Container: 1 px border #0F766E, background #F0FDFA, radius 8 px, padding 16 px.
Assistant Sentence (C02): "From which date should this proposed hike take effect?"
Selectable Choice Pills (Radio card group):
- Option A: "2026-04-01"
- Option B: "2026-07-01"
- Option C: "2026-09-01" [Selected state: Teal border, checkmark]
Action Button: "Apply Selection and Recalculate" (Teal button #0F766E, height 40 px).
```

### Prompt 3C: Query Draft Card & Status (Scenario 9/10 / Neha Gupta E05)
```text
Design a mobile Query Draft Card and subsequent Confirmation Receipt for CHAT-EMP.
Draft Card:
- Header: "Draft Payroll Query" with Sentence (C12): "Send this query with the listed evidence to HR?"
- Target Period: "2026-09"
- Category: "salary"
- Attached Evidence: "Payslip PAY-E05-2026-09 • Attendance ATT-E05-2026-09 (3 LOP days)"
- Description Field (Editable): "Please check my September attendance."
- Radio Group: "(•) Create a new query  ( ) Add to my open query"
- Actions: "Confirm and Send" (Teal button #0F766E) and "Cancel Draft" (Text link).

Submission Receipt Card (Post-action state):
- Success Icon (Green checkmark #166534).
- Text (C15): "Your query is Sent. HR can access it for review."
- Monospace Query ID: "QUERY-E05-SEPTEMBER"
- Status Tag: "Sent"
```

### Prompt 3D: FAQ Answer Card (General Payroll Knowledge)
```text
Design an in-thread FAQ Answer Card for general payroll knowledge queries in CHAT-EMP.
Container: Border 1 px #E2E8F0, background #FFFFFF, radius 8 px, padding 16 px.
Header: Category tag "Glossary" (12 px Semi-bold #0F766E on #F0FDFA badge).
Question Title: "What is LOP?" (16 px Semi-bold #0F172A).
Answer Body: "Unpaid leave days used to work out paid days for salary."
Citation Footer: "To be defined in the payroll FAQ file →" (Underlined deep teal link with external icon).
Suggestion Chips: "Why is my take-home pay lower in September?", "What is PF?".
```
