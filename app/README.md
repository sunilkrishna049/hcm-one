# HCM One Chat-First Prototype

A deterministic Indian payroll and AI assistant prototype implementing a **chat-first conversational interface with rich inline cards** across two role-specific surfaces:
- **`CHAT-HR` (Desktop Web, 1440 px):** Continuous conversational feed for HR administrators with a docked 480 px right side panel (`PANEL-HR`) for heavy calculation proof, multi-month breakdown tables, and settlement ledgers.
- **`CHAT-EMP` (Mobile First, 390 px frame):** Centered mobile conversation surface for employees explaining take-home changes and tax deductions, with accessible bottom sheets (`SHEET-EMP`, max-height 85vh) for calculation proof and evidence inspection.

---

## 3-Line Run Instructions (Windows)

```powershell
# 1. Start FastAPI backend (from project root)
app\backend\.venv\Scripts\uvicorn.exe app.backend.main:app --port 8000

# 2. Start Vite frontend (in separate terminal)
cd app\frontend; npm run dev

# 3. Open prototype in browser
Start-Process http://localhost:5173
```

---

## Core Invariants & Architectural Rules

1. **Zero LLM Calls in Prototype:** Assistant copy is strictly restricted to approved sentences C01 to C30 (`screen-specs.md` Section 7, DEC-029, DEC-035). Sentences are used verbatim with parameter slots populated directly from deterministic API responses.
2. **Zero Frontend Math:** The frontend never calculates, adds, rounds, or ranks any payroll figure. Every number is computed deterministically by the Python calculation engine. Currency formatting follows Indian digit grouping with real minus signs (`₹1,20,000`, `−₹5,420`).
3. **Single `/api/chat` Contract:** The frontend communicates strictly via `POST /api/chat` documented in `app/backend/chat_contract.md`. A deterministic intent router handles all 13 BRD v1.2 scenarios, role-based checks, and FAQ matching now. The CrewAI agentic workflow in step 4 will replace only the router implementation without changing frontend components or the API contract.
4. **Approval Never Looks Like Payment:** Silence is never approval. Every approve, edit, send, resolve, dispute, and close action requires an explicit user click. Approving marks scope as ready for payroll; it never applies payroll or triggers bank disbursements (C04).
5. **Epistemic Boundaries & FAQ Knowledge:** General payroll questions are answered strictly from `data/knowledge/payroll_faq.json` via transparent keyword overlap. If match confidence is below 0.35, the assistant provides an honest fallback ("I can't answer that yet in this demo") with suggestion chips. It never invents an answer.
6. **Server-Side RBAC & Guardrails:** Cross-department requests (e.g., Sales HR requesting Engineering employee data), prompt injection attempts, and out-of-scope personal financial advice are stopped on the server and return refusal sentence C10 without leaking confidential data.
7. **Mandatory Demo Disclaimer:** Every view prominently displays `"Demo with fictional data. Not for real payroll."` in the footer.

---

## Chat Surfaces & Components

- **`CHAT-HR` (Desktop 1440 px):** Chat thread up to 840 px wide. Renders proposal summaries, number card clusters, month table summaries, component list summaries, and approval cards.
- **`PANEL-HR` (Right Side Panel 480 px):** Opens alongside `CHAT-HR` when clicking "View full month breakdown" or "Show calculation". Displays full multi-month arrears tables, settlement ledgers, and plain-language formulas with verified rule citations.
- **`CHAT-EMP` (Mobile 390 px):** Mobile conversation thread rendering hero take-home numbers, net change cards, ranked reason cards, query drafts, and status trackers.
- **`SHEET-EMP` (Mobile Bottom Sheet, max 85vh):** Radix UI dialog sheet sliding up on mobile when clicking "Show calculation" or "Review evidence". Displays step-by-step math breakdowns (e.g., LOP divisor formulas, tax projections).
- **14 Rich Card Types:**
  1. Proposal Summary Card
  2. Hero Number Card
  3. Number Cards Cluster (Gross, PF, TDS)
  4. Month Table Summary Card
  5. Component List Summary Card
  6. Clarifying Question Card (C02)
  7. Approval Card (C04)
  8. Ranked Reason List Card (C30 causal explanations)
  9. Informational Banner Card
  10. Refusal Card (C10 security boundary)
  11. Query Draft Card (C12/C13)
  12. Query Status Card (lifecycle state tracking)
  13. Action Button / "Show Calculation" Card
  14. FAQ Answer Card (with category badge & action link)

---

## 13 Scenarios Walkthrough Guide

Use the **Scenario Picker** in the top demo bar to switch users and trigger scenarios instantly, or type the prompts directly into the composer.

| Scenario | Surface | User / Role | Trigger Prompt / Action | Cards & Content Rendered | Side Panel / Bottom Sheet |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Hike with LOP** | `CHAT-HR` | `HR01` (HR Admin) | *"Prepare Priya Sharma's pending back-dated hike."* | Sentence C03. Proposal summary (Priya Sharma, E01), Hero Net Arrears (`₹67,476`), Gross Arrears (`₹71,200`), PF (`₹0`), TDS (`₹3,724`), Approval Card (C04). | `PANEL-HR`: April–September month-by-month table (monthly TDS 312 for full months, 292 for June), plain-language formula, real statutory rule IDs. |
| **2. Hike across PF Ceiling** | `CHAT-HR` | `HR01` (HR Admin) | *"Review back-dated hike for Arjun Rao"* | Sentence C03. Proposal summary (Arjun Rao, E02), Hero Net Arrears (`₹7,099`), Gross Arrears (`₹7,200`), PF (`₹101`), TDS (`₹0`), Approval Card. | `PANEL-HR`: September PF dual-segment ceiling proof (16 days pre-Sept 17, 14 days post-Sept 17). |
| **3. Hike with Missing Attendance** | `CHAT-HR` | `HR01` (HR Admin) | *"Prepare hike proposal for Kavya Iyer"* | Sentence C07 (*"The required attendance record for 2026-07 is missing..."*). Incomplete proposal card (Kavya Iyer, E03), Net Arrears `Not available in generated data`, missing July warning banner, Approval disabled. | `PANEL-HR`: July row marked with warning banner; approval blocked. |
| **4. Team Bonus: Joiner & Notice** | `CHAT-HR` | `HR01` (HR Admin) | *"Calculate Annual and Sales bonus runs"* | Sentence C03. Team bonus summary, Eligible count (`3`), Ineligible count (`1`), Needs input (`1`), Gross eligible total (`₹2,13,929`), Approval Card. | `PANEL-HR`: Scope table (E01 ₹1,08,000, E03 ₹36,000, E04 ₹60,000, E07 joiner proration ₹9,929, E08 notice exclusion ₹0, E09 missing rating). |
| **5. Missing Performance Rating** | `CHAT-HR` | `HR01` (HR Admin) | *"Check bonus eligibility for Meera Nair (E09)"* | Sentence C07 (*"The required performance record for FY 2025-26 is missing..."*). Incomplete bonus card (Meera Nair, E09), Rating `null`, Bonus amount `Not available in generated data`, Approval disabled. | `PANEL-HR`: Missing performance record citation. |
| **6. Eligible Gratuity Settlement** | `CHAT-HR` | `HR01` (HR Admin) | *"Prepare full and final settlement for Rahul Verma (E10)"* | Sentence C03. Settlement summary (Rahul Verma, E10), Hero Final Net (`₹3,32,256`), Gross Payables (`₹3,35,256`), Total Deductions (`₹1,975`), Gratuity Card (`₹2,01,923`), Approval Card (due date 2026-11-03). | `PANEL-HR`: Full settlement ledger with statutory due dates. |
| **7. Below Gratuity Minimum Service** | `CHAT-HR` | `HR01` (HR Admin) | *"Review settlement for Lakshmi Reddy (E11)"* | Sentence C03. Settlement summary (Lakshmi Reddy, E11), Gratuity component card (`₹0`, *"Close to minimum service: 4 years, 8 months, 24 days"*), Approval Card. | `PANEL-HR`: Gratuity 5-year statutory tenure proof. |
| **8. Asset Clearance & Notice Shortfall** | `CHAT-HR` | `HR01` (HR Admin) | *"Review exit recovery for Imran Khan (E12)"* | Sentences C07 & C19. Incomplete settlement card (Imran Khan, E12), Final Net `Not available in generated data`, Notice Shortfall Recovery (`₹56,667`), Asset Recovery `Unresolved`, Approval disabled. | `PANEL-HR`: Asset clearance pending indicator. |
| **9. Salary Drop with LOP** | `CHAT-EMP` | `USER-E05` (Neha Gupta) | *"Why is my take-home pay lower in September?"* | Sentence C30 (*"Your September 2026 take-home is −₹5,420 lower than August 2026..."*). Hero September Take-Home (`₹42,780`), Net Change (`−₹5,420`), August Take-Home (`₹48,200`), Ranked Reasons (LOP 3 days: `−₹5,000`, PF ceiling change: `−₹420`, TDS change: `₹0`), action chip "Show calculation". | `SHEET-EMP`: September pay breakdown, calendar divisor 30, unpaid leave 3, LOP deduction formula (`50,000 / 30 × 3 = 5,000`), PF ceiling change formula. |
| **10. Previous-Employer Income Declared** | `CHAT-EMP` | `USER-E06` (Siddharth Rao) | *"Why did my TDS deduction increase in September?"* | Sentences C30 & C29 (*"...declared income from your previous employer for 2026-04 to 2026-06..."*). Hero September TDS (`₹16,043`), TDS Increase (`₹12,454`), August TDS (`₹3,589`), Ranked Reasons (Prior employer declaration: `−₹12,454`, PF ceiling change: `−₹560`), Tax breakdown card. | `SHEET-EMP`: Yearly projection calculation proof, declared gross `₹4,50,000`, previous TDS `₹15,000`, remaining tax `₹87,180`. |
| **11. No Salary Earning Change** | `CHAT-EMP` | `USER-E16` (Pooja Reddy) | *"Did my basic pay or allowance change in September?"* | Sentences C30 & C26. Take-Home Net Change (`−₹420`), Informational banner (*"No salary earning component change"*), PF adjustment reason (`−₹420`). | `SHEET-EMP`: Proof of unchanged gross earnings `₹40,000`, statutory PF ceiling change from 17 Sep. |
| **12. Unauthorized Access Blocked** | `CHAT-HR` / `CHAT-EMP` | `HR02` (Sales HR) | *"What is Priya Sharma's monthly salary?"* | Sentence C10 (*"I cannot provide that information. I can help with payroll records you are authorized to access."*). Refusal Card with red warning border, zero salary data disclosed, suggested authorized queries. | Refusal terminates target employee access. Zero leaks. |
| **13. Known & Unresolved Settlement Components** | `CHAT-HR` | `HR01` (HR Admin) | *"Review settlement breakdown for Imran Khan (E12)"* | Sentence C19. Settlement summary (Imran Khan, E12), Known Recoveries Subtotal (`₹56,667`), Asset Recovery `Unresolved`, Final Net `Not available in generated data`, Partial Approval Card. | `PANEL-HR`: Resolved salary & notice shortfall beside unreturned asset clearance. |

---

## 3 FAQ Questions Walkthrough Guide

HCM One answers general payroll questions from `data/knowledge/payroll_faq.json` using keyword overlap matching:

### 1. "What is LOP?"
- **How to test:** In either `CHAT-EMP` or `CHAT-HR`, type `"What is LOP?"` or click the suggestion chip.
- **Rendered Output:**
  - Assistant responds with approved text.
  - **FAQ Answer Card:**
    - Category: `Glossary`
    - Question: *"What is LOP?"*
    - Answer: *"Unpaid leave days used to work out paid days for salary."*
    - Action link chip: *"Show my latest payslip change"* (navigates to salary change explanation).
    - Source: `output/06-ai-interaction/conversation-design.md Section 6`

### 2. "What is TDS?"
- **How to test:** Type `"What is TDS?"` or click the suggestion chip.
- **Rendered Output:**
  - **FAQ Answer Card:**
    - Category: `Glossary`
    - Question: *"What is TDS?"*
    - Answer: *"Tax deducted through payroll in monthly parts toward expected yearly tax."*
    - Action link chip: *"Show my TDS change"* (navigates to TDS explanation).
    - Source: `output/06-ai-interaction/conversation-design.md Section 6`

### 3. "Does approving a proposal mean payment is made?"
- **How to test:** Type `"Does approving a proposal mean payment is made?"` or click the suggestion chip.
- **Rendered Output:**
  - **FAQ Answer Card:**
    - Category: `Approvals and payments`
    - Question: *"Does approving a proposal mean payment is made?"*
    - Answer: *"No. Approving records that version and selected items as ready for payroll. It does not apply the change or make a payment."*
    - Source: `output/06-ai-interaction/approval-failure-handling.md Section 2`

---

## Automated Verification Suite

Run all test suites across engine, backend, frontend, and knowledge validation:

```powershell
# 1. Calculation Engine Tests (74 passed)
engine\.venv\Scripts\pytest.exe engine/tests -q

# 2. Backend API, Chat Actions & Chat Provenance Tests (50 passed)
$env:PYTHONPATH="."; app\backend\.venv\Scripts\python.exe -m pytest app/backend/tests -q

# 3. Frontend Chat, Scenario Guard & Action Click Tests (16 passed)
cd app\frontend; npm run test

# 4. Frontend Clean Build Verification
cd app\frontend; npm run build

# 5. Payroll FAQ Knowledge Base Validation (30 entries verified)
app\backend\.venv\Scripts\python.exe data/knowledge/validate_faq.py
```
