# HCM One Clickable Prototype

A fully functional, deterministic Indian payroll and AI assistant prototype implementing 13 scenarios across 6 screens (3 desktop HR screens at 1440px and 3 mobile employee screens in a 390px frame).

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

## Core Invariants & Governance

1. **Zero LLM Calls:** UI assistant copy is strictly limited to approved sentences C01 to C29 (`screen-specs.md` Section 7 and DEC-029). Sentences are used verbatim with parameter slots populated directly from deterministic API responses.
2. **Zero Frontend Math:** The frontend never calculates, adds, rounds, or ranks any payroll figure. Every number is computed deterministically by the Python calculation engine.
3. **Silence Is Never Approval:** Approval is an explicit action with a recorded version. Approval marks scope as ready for payroll; it never applies payroll or triggers bank disbursements (C04).
4. **Mandatory Disclaimer:** Every view prominently displays `"Demo with fictional data. Not for real payroll."` in the footer.
5. **Server-Side RBAC:** Access control is strictly enforced on the server. Unauthorized requests return sentence C10 without leaking confidential context.
6. **Data Immutability:** `input/`, `output/`, `data/rules/`, and `data/mock/` remain strictly read-only. Runtime changes (events, proposals, queries) are stored exclusively in `data/runtime/`.

---

## Architecture

- **Backend:** FastAPI app running at `http://localhost:8000` with Python 3.12, wrapping `engine/payroll/` calculations, managing proposal lifecycle, version tracking, query dispatching, and audit logging.
- **Frontend:** React 19 + TypeScript + Vite running at `http://localhost:5173`. Uses Radix UI unstyled primitives for accessible dialogs, desktop side drawer (480px), and mobile bottom sheets.
- **Design System:** Custom CSS design tokens in `tokens.css` with Deep Teal (`#0F766E`) brand accent, slate surfaces, tabular figures (`font-feature-settings: "tnum"`), and WCAG AA contrast.
- **Screens:**
  - `SCR-01` (`PrepareProposal.tsx`): HR initiates hike, bonus, or settlement proposals with contractual baseline preview and C02 clarification.
  - `SCR-02` (`ReviewProposal.tsx`): HR proposal review across all 3 modes, with 480px calculation proof drawer, parameter revision dialog (C05), stale version guard (C25), and approval bar (C04).
  - `SCR-03` (`ReviewQuery.tsx`): HR inquiry desk to review, take into review (C16), reply to, and resolve (C23) employee queries.
  - `SCR-04` (`UnderstandPayroll.tsx`): Centered 390px mobile frame for employees explaining salary drop (LOP), unchanged salary, TDS increase (C29), and permission denied (C10).
  - `SCR-05` (`ReviewQueryDraft.tsx`): Mobile employee query draft with removable evidence badges, duplicate query check (C14), and mandatory confirmation (C12/C13).
  - `SCR-06` (`TrackQuery.tsx`): Mobile query tracker with status lifecycle (`Sent`, `In review`, `Resolved`, `Closed`), dispute option, and closure acknowledgment (C24).

---

## 13 Scenarios Walkthrough Guide

| Scenario | Screen | Role / User | Key Inputs & Description | Expected Numbers & Engine Verification | Approved Sentence |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Hike with LOP** | SCR-02 (Desktop) | HR Admin (`HR01`) | Priya Sharma (`E01`), 10% hike backdated to 2026-07-01 (Jul, Aug, Sep). | New CTC: `13,20,000`<br>Monthly Gross: `1,10,000`<br>Gross Arrears: `90,000`<br>Net Arrears: `72,000` | `C01`, `C02`, `C03`, `C04` |
| **2. Hike across PF Ceiling** | SCR-02 (Desktop) | HR Admin (`HR01`) | Arjun Patel (`E02`), hike across statutory PF wage ceiling change on 2026-09-17. | Option A (Capped): Net Arrears `78,400`<br>Option B (Uncapped): Net Arrears `75,100` | `C03`, `C04` |
| **3. Hike Edit & Recalculation** | SCR-02 (Desktop) | HR Admin (`HR01`) | Priya Sharma (`E01`), HR edits annual gross to `13,80,000` with reason. | Version advances to `v2`. Engine re-runs arrears with new monthly gross `1,15,000`. | `C05` |
| **4. Bonus with Incomplete Scope** | SCR-02 (Desktop) | HR Admin (`HR01`) | Bonus run covering annual performance bonus. Scope includes Kavya (`E03`). | Kavya gross bonus: `48,000`. Kavya net bonus: `null` (missing Jul attendance). Selected group net is `null` / Incomplete. | `C07` |
| **5. Settlement with Unverified Asset** | SCR-02 (Desktop) | HR Admin (`HR01`) | Imran Khan (`E12`), exiting employee with notice shortfall & unverified laptop. | Recoveries: `35,000` + Unverified asset clearance. Net settlement: `null` / Incomplete. | `C08`, `C19` |
| **6. Hike Approval & Scope Blocking** | SCR-02 (Desktop) | HR Admin (`HR01`) | HR attempts approval on Priya (`E01`, Complete) vs Kavya (`E03`, Incomplete). | Priya approval succeeds and records version. Kavya approval is blocked with warning. | `C04`, `C07` |
| **7. Salary Drop: Loss of Pay** | SCR-04 (Mobile) | Employee (`USER-E05`) | Neha Gupta asks why September net pay dropped. | Sep Net: `49,800` vs Aug Net: `55,000`. Ranked reason 1: 3 unpaid leave days (`-5,824`). Ranked reason 2: lower PF (`+624`). | `C22`, `C27` |
| **8. No Salary Change after Promise** | SCR-04 (Mobile) | Employee (`USER-E16`) | Pooja Reddy asks why salary is unchanged after verbal appraisal. | Gross unchanged: `45,000`. Verbal promise not in recorded inputs. | `C26`, `C28` |
| **9. Draft Query to HR** | SCR-05 (Mobile) | Employee (`USER-E05`) | Neha Gupta reviews draft query with attendance & payslip evidence badges. | Employee removes evidence or edits text. Submit disabled until confirmation box checked. | `C12`, `C13`, `C14` |
| **10. Previous Employer TDS** | SCR-04 (Mobile) | Employee (`USER-E06`) | Siddharth Rao asks why TDS increased in September. | Prior income declared for `2026-04 to 2026-06` added to yearly income. Prior tax deducted counted. | `C29` |
| **11. Query Lifecycle & Dispute** | SCR-06 / SCR-03 | Employee (`USER-E05`) & HR | Query lifecycle: Sent &rarr; In review &rarr; Resolved &rarr; Dispute / Close. | HR records resolution reply. Employee disputes resolution or acknowledges and closes query. | `C15`, `C16`, `C23`, `C24` |
| **12. Unauthorized Access Blocked** | SCR-04 / SCR-01 | HR Sales (`HR02`) | Sales HR requests data for Engineering employee Priya (`E01`). | HTTP 200/403 with `Permission denied`. Zero private data returned. | `C10` |
| **13. Stale Proposal Blocked** | SCR-02 (Desktop) | HR Admin (`HR01`) | HR tries to approve older version v1 when v2 exists. | Backend blocks approval: `"This proposal changed after you reviewed it."` | `C25` |

---

## Verifying Engine & Backend Tests

```powershell
# 1. Run calculation engine tests (74 tests)
engine\.venv\Scripts\pytest.exe engine/tests -q

# 2. Run backend API & lifecycle tests (10 tests)
app\backend\.venv\Scripts\pytest.exe app/backend/tests -q
```
