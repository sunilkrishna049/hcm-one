# HCM One: Visual Specification (Chat-First Architecture)

Proposed for Gate G07 re-opening. This specification defines the visual language, design tokens, layout hierarchy, and component library for HCM One's **chat-first interface with rich cards**.

It replaces the previous six standalone screens with two dedicated chat workspaces:
1. **`CHAT-HR`**: HR Admin chat workspace (desktop, 1440 px viewport) with conversation thread and collapsible right side panel (`PANEL-HR`, 480 px) for heavy calculation reviews, dense multi-month tables, and settlement ledgers.
2. **`CHAT-EMP`**: Employee chat workspace (mobile, 390 px viewport) with mobile conversation stream and interactive bottom sheets (`SHEET-EMP`, max-height 85vh) for calculation breakdowns, proofs, and glossary terms.

**Design Philosophy:** Minimalist, typography-led, enterprise-grade clarity. Uses a single deep teal brand accent (`#0F766E`), generous white space, crisp borders, and prominent tabular figures. Avoids decorative clutter, charts, unverified percentages, or celebratory animations. Every number displayed on screen originates strictly from `data/generated/scenarios/` via backend API bindings ([screen-specs.md](screen-specs.md), Section 8).

---

## 1. Typography Tokens

HCM One uses **Inter** for all UI copy, message prose, and financial figures.
- **Tabular figures (`font-feature-settings: "tnum"`)** are mandatory for all amounts, currency values, dates, percentages, and table cells to guarantee columnar alignment.
- **Monospace font (`ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace`)** is used strictly for technical identifiers (Query IDs such as `QUERY-E05-SEPTEMBER`, transaction hashes, and record pointers). Monospace must **never** be used for financial amounts.

| Token | Font Size / Line Height | Font Weight | Letter Spacing | Applied Elements |
|---|---|---|---|---|
| **Number Hero (Desktop)** | 40 px / 48 px | 600 (Semi-bold) | -0.02em | Net arrears hero in `CHAT-HR` card (`67,476`) |
| **Number Hero (Mobile)** | 32 px / 40 px | 600 (Semi-bold) | -0.02em | Take-home or TDS change hero in `CHAT-EMP` (`-5,420`) |
| **Workspace Header Title** | 20 px / 28 px | 600 (Semi-bold) | -0.01em | Top bar title ("HCM One HR Workspace", "HCM One Employee") |
| **Panel / Sheet Title** | 18 px / 26 px | 600 (Semi-bold) | -0.01em | Side panel header ("Calculation Proof", "Full Settlement Breakdown") |
| **Card Heading** | 16 px / 24 px | 600 (Semi-bold) | 0 | Card titles ("Proposal Summary", "Ranked by effect on take-home pay") |
| **Body / Message Prose** | 15 px / 22 px | 400 (Regular) | 0 | Assistant message bubbles, user bubbles, card explanatory copy |
| **Input & Composer** | 15 px / 22 px | 400 (Regular) | 0 | Chat composer textarea, edit modal input fields |
| **Secondary / Meta Text** | 13 px / 18 px | 400 (Regular) | 0 | Assistant sender tag ("HCM One Assistant"), timestamps, source notes |
| **Dense Table & Key-Value** | 13 px / 18 px | 400 (Regular) / 600 for headers | 0 | Side panel arrears table rows, formula breakdown operands |
| **Pill / Button Label** | 13 px / 18 px | 500 (Medium) | +0.01em | Suggestion chips, secondary actions, calculation trigger |
| **Status Badge Label** | 12 px / 16 px | 600 (Semi-bold) | +0.02em | Certainty labels ("Complete for this scope"), proposal status badges |
| **Technical ID (Mono)** | 12 px / 16 px | 400 (Regular) | 0 | Query IDs (`QUERY-E05-SEPTEMBER`), Rule references (`pf-rules.json#pf_wage_formula`) |

### Presentation Rules (Display Only, Never Calculation)
1. **Money Presentation:** Indian rupee format with Indian digit grouping, for example ₹1,20,000 and −₹5,420. Use a real minus sign (−, U+2212) for negative amounts. Never use compact forms like ₹12K or ₹1.32L. Display values strictly as generated, applying currency formatting for display only.
2. **Rule Citations:** Show human labels built from the rule's value and dates (for example "PF wage ceiling: ₹15,000 until 16 Sep 2026"), plus rules version "Northwind demo rules v1". Never show file names, JSON keys or rule IDs to users. Only show rule citations relevant to the number being explained.
3. **Formulas:** Show plain-language formulas (for example "Earned salary = monthly salary × paid days ÷ calendar days"). If the engine formula text is technical, display the plain_formula field provided by the engine display export instead of rewriting it in the frontend.
4. **Relevant Scope Only:** Only show rule citations and calculation proofs that directly relate to the specific line item, deduction, or variance being inspected.
5. **Missing Operands:** If an operand or total is unavailable in generated data, display the fallback label `Not available in generated data`.

---

## 2. Color Tokens

The visual palette relies on high contrast, slate neutrals, and a singular **deep teal brand accent (`#0F766E`)**. Semantic colors are reserved strictly for system states, verification status, and validation flags.

| Color Token | Hex Code | Purpose & Application |
|---|---|---|
| **Page Background** | `#FFFFFF` | Main background for desktop chat workspace and mobile screen |
| **Thread Surface** | `#F8FAFC` | Background for chat scroll container and panel canvas |
| **Card Background** | `#FFFFFF` | Elevated surface for rich cards, side panels, and bottom sheets |
| **Card Border** | `#E2E8F0` | Default 1 px boundary for cards, dividers, and message wrappers |
| **Card Border Hover** | `#CBD5E1` | Interactive hover state for clickable cards and table rows |
| **Primary Text** | `#0F172A` | Primary readability: headings, card text, message prose, amounts |
| **Secondary Text** | `#475569` | Secondary copy: timestamps, sublabels, inactive tab labels |
| **Muted Text** | `#64748B` | Tertiary copy: table column headers, helper notes, formula labels |
| **Brand Accent (Teal)** | `#0F766E` | Primary interactive color: primary buttons, active chips, focus outlines |
| **Brand Accent Hover** | `#115E59` | Hover state for primary buttons and interactive accents |
| **Brand Tint Surface** | `#F0FDFA` | Subtle background tint for selected cards, active chips |
| **Brand Tint Border** | `#99F6E4` | Border for active chips, focused cards, and calculation buttons |
| **User Bubble Background**| `#F1F5F9` | Slate neutral background for user message bubbles |
| **User Bubble Text** | `#0F172A` | High-contrast text within user message bubbles |
| **Assistant Bubble Surface**| `#FFFFFF` | Clean white surface for assistant response cards and containers |
| **Interactive Border** | `#94A3B8` | Normal border for inputs, textareas, and unselected radio options |
| **Focus Ring** | `#0F766E` | 3 px solid focus outline with 2 px offset for keyboard navigation |
| **Disabled Surface** | `#F1F5F9` | Disabled buttons, inactive inputs, unselected suggestion chips |
| **Disabled Text** | `#94A3B8` | Text on disabled surfaces |
| **Success Surface** | `#F0FDF4` | Background for completed actions, approved status, certainty complete |
| **Success Border** | `#BBF7D0` | 1 px border for success badges |
| **Success Text / Icon** | `#166534` | Text and icons for verified results, approved state |
| **Warning Surface** | `#FFFBEB` | Background for missing data, unverified rules, unresolved items |
| **Warning Border** | `#FDE68A` | 1 px border for warning badges |
| **Warning Text / Icon** | `#92400E` | Text and icons for limitations, holds, unverified rule warnings |
| **Error Surface** | `#FEF2F2` | Background for refusals, access denials, calculation errors |
| **Error Border** | `#FECACA` | 1 px border for error badges |
| **Error Text / Icon** | `#B91C1C` | Text and icons for validation errors, access refusals |

---

## 3. Layout, Dimensions & Elevation

HCM One uses responsive grid structures customized for the two target viewports:

```
+-----------------------------------------------------------------------------------------+
|                                CHAT-HR: Desktop (1440 px)                               |
+-------------------------------------------------------------+---------------------------+
| Top Bar (64 px height): Brand, Workspace, Role, Session     | Side Panel Header (64 px) |
+-------------------------------------------------------------+---------------------------+
| Chat Thread Area (Variable width, max 840 px prose):        | PANEL-HR (480 px width):  |
| - Timestamp & Assistant Intro                               | - Sticky Header & Close   |
| - User Bubble ("Prepare Priya Sharma's hike")               | - Month-by-month table    |
| - Assistant Bubble (C03) + Proposal Summary Card           | - Settlement Ledgers      |
| - Number Cards Grid (Net Arrears Hero, Gross, PF, TDS)     | - Calculation Proof       |
| - Suggestion Chips row                                      | - Real Rule IDs           |
| - Approval Card (Approve / Edit with reason / Reject)       | - Audit Flags             |
+-------------------------------------------------------------+                           |
| Sticky Composer Area (80 px height): Input + Send Button    | (Scrolls independently)   |
+-------------------------------------------------------------+---------------------------+
```

```
+------------------------------------+
|     CHAT-EMP: Mobile (390 px)      |
+------------------------------------+
| Mobile Top Bar (56 px): Brand & Nav|
+------------------------------------+
| Mobile Chat Feed (Padding: 16 px): |
| - Assistant Bubble (C27)           |
| - Number Card Hero (-5,420)        |
| - Reason List Card (LOP + PF)      |
| - "Show calculation" Button        |
| - Suggestion Chips (Swipeable)     |
+------------------------------------+
| Mobile Composer (64 px): Input+Send|
+------------------------------------+
| SHEET-EMP: Bottom Sheet (Overlay)  |
| - Drag Handle & Close (X)          |
| - LOP Day Calculation Proof        |
| - Stored Formula & Glossary        |
+------------------------------------+
```

### Dimensional Specifications

| Layout Element | Desktop (`CHAT-HR`) | Mobile (`CHAT-EMP`) | Design Constraints |
|---|---|---|---|
| **Reference Viewport** | 1440 px width (min 1280 px) | 390 px width (min 320 px) | Target responsive standards |
| **Top App Header** | Height: 64 px; Border bottom: 1 px | Height: 56 px; Border bottom: 1 px | Sticky top; z-index: 30 |
| **Chat Column Width** | Max reading width: 840 px centered | Full width (100% of 390 px) | Prevents over-stretched prose lines |
| **Outer Padding** | Left/Right: 32 px | Left/Right: 16 px | Fluid container breathing room |
| **Component Spacing** | 24 px between conversation turns | 16 px between conversation turns | Clear message demarcation |
| **Card Gap** | 16 px between nested cards | 12 px between nested cards | Compact information density |
| **Side Panel (`PANEL-HR`)** | Width: 480 px fixed; height 100vh | N/A (desktop only) | Border-left: 1 px `#E2E8F0`; z-index: 20 |
| **Bottom Sheet (`SHEET-EMP`)**| N/A (mobile only) | Width: 100%; Max-height: 85vh | Border-radius: 16 px 16 px 0 0; z-index: 50 |
| **Backdrop Overlay** | N/A (panel pushes or overlays cleanly)| `#0F172A` at 40% opacity | Dim background when sheet opens |
| **Card Corner Radius** | 8 px | 8 px | Consistent subtle rounding |
| **Pill / Chip Radius** | 9999 px (Fully rounded) | 9999 px (Fully rounded) | High affordance for taps |
| **Control Radius** | 6 px | 6 px | Buttons and textareas |
| **Minimum Touch Target** | 44 px by 44 px | 44 px by 44 px | WCAG 2.2 touch target compliance |
| **Elevation / Shadow** | `0 1px 3px rgba(0,0,0,0.05)` | `0 1px 2px rgba(0,0,0,0.05)` | Subtle, flat aesthetic; no floating cards |

---

## 4. Chat Components Specification

### 4.1. User Message Bubble
- **Alignment:** Right-aligned (flex-end) within the chat column.
- **Surface:** `#F1F5F9` (neutral slate).
- **Text:** 15 px / 22 px Regular, color `#0F172A`.
- **Corner Radius:** 16 px top-left, 16 px top-right, 16 px bottom-left, 4 px bottom-right.
- **Max Width:** Desktop: 600 px; Mobile: 85% of viewport width.
- **Timestamp:** 12 px Regular `#64748B` positioned outside the bubble below right.

### 4.2. Assistant Message Container & Bubble
- **Alignment:** Left-aligned (flex-start) within the chat column.
- **Header:** Assistant Avatar icon (Teal badge with assistant mark), sender label `"HCM One Assistant"`, and timestamp (`"10:14 AM"`). **No "Verified" badge.**
- **Text Bubble:** 15 px / 22 px Regular `#0F172A`, surface `#FFFFFF`, border 1 px `#E2E8F0`, padding 16 px.
- **Copy Rule:** Assistant prose consists **strictly of approved sentences (C01–C29)** used verbatim. No paraphrasing, conversational filler, or unapproved copy.
- **Sub-elements:** Any accompanying rich cards appear directly below the text bubble inside the assistant turn container (gap: 12 px).

### 4.3. Suggestion Chips
- **Purpose:** Provide one-tap demo shortcuts and prompt guidance without typing.
- **Placement:** Positioned immediately below an assistant message turn or above the sticky composer.
- **Styling:** Pill container (height 36 px, border-radius 9999 px), background `#FFFFFF`, border 1 px `#94A3B8`, text 13 px Medium `#0F172A`.
- **Hover State:** Background `#F0FDFA`, border 1 px `#0F766E`, text `#0F766E`.
- **Mobile Behavior:** Horizontal scroll carousel with edge fading; no vertical line wrapping that obscures message feed.

### 4.4. Composer Area
- **Desktop (`CHAT-HR`):**
  - Sticky bottom container (height 80 px), background `#FFFFFF`, border-top 1 px `#E2E8F0`.
  - Textarea: auto-expanding (height 48 px), border 1 px `#94A3B8`, radius 6 px, placeholder: `"Ask about payroll proposals, arrears, or query resolution..."`.
  - Send Button: 40 px by 40 px square, background `#0F766E`, hover `#115E59`, white paper plane / arrow icon, radius 6 px.
  - Disabled State: When waiting for API response, textarea disabled, send button background `#CBD5E1`.
- **Mobile (`CHAT-EMP`):**
  - Sticky bottom container (height 64 px), background `#FFFFFF`, border-top 1 px `#E2E8F0`.
  - Textarea: single-line input expanding up to 3 lines, placeholder: `"Ask about your pay, deductions, or query..."`.
  - Send Button: 38 px by 38 px, deep teal with accessible icon label.
- **Demo Fallback Behavior:** If the user types an unmapped demo query, the assistant responds with approved fallback copy:
  > *"I cannot answer that question in this demo. You can ask about recorded salary and tax changes, full and final settlements, bonus eligibility, or choose a topic below:"*
  followed by relevant suggestion chips.

### 4.5. Side Panel (`PANEL-HR`) — Desktop Review Drawer
- **Purpose:** Hosts heavy payroll review surfaces without navigating away from the chat thread.
- **Width:** 480 px fixed width, docked to the right edge of viewport. Height: 100vh.
- **Header:** Sticky 64 px header with Panel Title (e.g., `"Calculation Proof"`, `"Full Settlement Breakdown"`), scope badge, and accessible Close Button (`✕` or `Esc`).
- **Body:** Scrollable vertical container (`overflow-y: auto`, padding 24 px). Contains dense month-by-month table, formula breakdowns, and real rule citations. **No raw repository file paths or internal codes.**
- **Keyboard Interaction:** Focus moves to close button upon opening; pressing `Escape` closes the panel and restores focus to the triggering "Show calculation" button.

### 4.6. Bottom Sheet (`SHEET-EMP`) — Mobile Detail Sheet
- **Purpose:** Hosts calculation proofs, LOP day breakdowns, and tax slab explainers on mobile.
- **Dimensions:** Width: 100% of mobile viewport; Max-height: 85vh; Slide-up animation (200ms ease-out).
- **Drag Handle:** 36 px by 4 px rounded bar in `#CBD5E1` centered 8 px from top.
- **Header:** Sheet Title, subtitle with scope, and Close Button (`✕`).
- **Body:** Scrollable area containing calculation cards, breakdown formulas, and glossary definitions.
- **Backdrop:** Modal scrim `#0F172A` at 40% opacity; tapping backdrop dismisses sheet.

---

## 5. Rich Card Types Specification (14 Cards)

### 1. Proposal Summary Card
- **Use:** Summarizes hike or salary revision proposals in `CHAT-HR`.
- **Elements:**
  - Header: Employee Name, Employee ID (monospace), Proposal Type badge (e.g. `"Back-dated hike proposal"`).
  - Key-Value Grid (2 columns): Requested Hike (`10%`), Effective Date (`2026-04-01`), Affected Periods (`6 months: 2026-04 to 2026-09`).
  - Salary Comparison: Old Monthly Salary Total (`120000 INR`) vs. Proposed Monthly Salary Total (`132000 INR`).
  - Status & Certainty: `Needs HR approval; not applied` and `Complete for this scope`.
- **Tokens:** Border 1 px `#E2E8F0`, background `#FFFFFF`, radius 8 px, padding 16 px.

### 2. Number Card (Hero & Secondary Grid)
- **Use:** Highlights key financial totals (Net Arrears, Monthly Take-Home, Gross Arrears, PF Change, TDS Impact).
- **Variants:**
  - **Hero Variant:** Prominent amount font (40 px desktop / 32 px mobile semi-bold `tnum`), label above, separate INR label, certainty pill (`Complete for this scope`).
  - **Secondary Grid Variant:** 3-column card cluster (Gross Arrears `71200 INR`, Employee PF Change `0 INR`, Estimated TDS Impact `3724 INR`).
- **Actions:** Includes a `"Show calculation"` link or button at the bottom right.

### 3. Month Table Card
- **Use:** In-thread summary of multi-month revisions with link to full side panel.
- **Elements:**
  - Mini summary table showing Month, Old Gross, Revised Gross, Arrears Difference, and Monthly TDS Impact.
  - Footer Action: Deep teal button or link: `"Show calculation & full month breakdown →"`.
- **Tokens:** Row border-bottom 1 px `#E2E8F0`, right-aligned tabular figures for amounts.

### 4. Component List Card
- **Use:** Full & Final Settlement line items (Scenario 6 / Rahul Verma `E10` or Scenario 8 / Imran Khan `E12`).
- **Elements:**
  - List of components: Earned Salary (`6774 INR`), Gratuity (`201923 INR`), Leave Encashment (`126559 INR`), Notice Shortfall Recovery (`0 INR`).
  - Component status tag: `"Eligible"`, `"Ineligible"`, `"Unresolved"`.
  - Applicable Due Date badge (exact C20): `"Due date: 2026-11-03"`.
- **Tokens:** Striped rows `#FFFFFF` and `#F8FAFC`, tabular figures right-aligned.

### 5. Reason List Card
- **Use:** Explains causes of pay drops or tax changes in `CHAT-EMP` (Scenario 9 / Neha Gupta `E05`).
- **Elements:**
  - Hero badge: Take-Home Net Change (`-5420 INR`).
  - Heading: "Ranked by effect on take-home pay"
  - Ranked causes list:
    1. **Loss of Pay (LOP):** `3 days` unpaid leave (`-5000 INR`) based on 30 calendar days.
    2. **PF ceiling change:** Revised statutory ceiling impact (`-420 INR`).
  - Sourced TDS change: `0 INR`.

### 6. Certainty Label
- **Use:** Mandatory epistemic label attached to every calculation card.
- **Allowed Values (Strict 5 labels from `trust-explainability.md`):**
  1. `Complete for this scope` (Green badge: surface `#F0FDF4`, border `#BBF7D0`, text `#166534`)
  2. `Incomplete` (Amber badge: surface `#FFFBEB`, border `#FDE68A`, text `#92400E`)
  3. `Rule not verified` (Amber badge: surface `#FFFBEB`, border `#FDE68A`, text `#92400E`)
  4. `Needs HR decision` (Neutral slate badge: surface `#F1F5F9`, border `#CBD5E1`, text `#334155`)
  5. `Cannot explain from available payroll data` (Red badge: surface `#FEF2F2`, border `#FECACA`, text `#B91C1C`)
- **Tokens:** Height 24 px, font size 12 px Semi-bold, padding 2 px 8 px, radius 9999 px.

### 7. "Show Calculation" Control
- **Use:** Standard trigger to open calculation proof in side panel (desktop) or bottom sheet (mobile).
- **Styling:** Secondary button style. Background `#F0FDFA`, border 1 px `#0F766E`, text 13 px Medium `#0F766E`, icon: calculator / external link.
- **Accessibility:** Explicit aria-label: `"Show calculation proof for Priya Sharma net arrears"`.

### 8. Clarifying Question Card with Choices
- **Use:** Triggered when the AI detects missing parameters (e.g., missing hike effective date in Scenario 2).
- **Elements:**
  - Assistant sentence (C02): *"From which date should this proposed hike take effect?"*
  - Selectable Choice Chips / Radio Options:
    - Choice A: `2026-04-01`
    - Choice B: `2026-07-01`
    - Choice C: `2026-09-01`
  - Confirmation Action: Deep teal button: `"Apply Selection and Recalculate"`.

### 9. Approval Card (Approve / Edit with Reason / Reject)
- **Use:** HR authorization for proposals in `CHAT-HR`. Follows DEC-011–DEC-014.
- **Rules:** Never looks like payment. Never uses celebratory animations.
- **Elements:**
  - Authorized scope label: `"Priya Sharma (E01) • 6 affected months (2026-04 to 2026-09)"`.
  - Approved mandatory copy (C04): *"Approving records this version and the selected scope as ready for payroll. It does not apply the change or make a payment."*
  - Action Group:
    - Primary Action: `"Approve proposal for payroll"` (Deep teal `#0F766E`, white text).
    - Secondary Action: `"Edit with reason"` (White background, border `#64748B`, text `#0F172A`).
    - Danger Action: `"Reject proposal"` (White background, border `#B91C1C`, text `#B91C1C`).
- **Post-Action State:** After approval, card updates to show recorded event: `"Approved for payroll • Version 1 • Awaiting payroll processing"`.

### 10. Query Draft Card
- **Use:** Review of employee query draft before submission in `CHAT-EMP` (Scenario 9/10 / Neha Gupta `E05`).
- **Elements:**
  - Query category: `"salary"`.
  - Target Period: `"2026-09"`.
  - Editable Description Field: Pre-filled with employee's inquiry text ("Please check my September attendance.").
  - Attached Evidence List: Attached pay slip reference (`PAY-E05-2026-09`), attendance record (`ATT-E05-2026-09`, 3 LOP days).
  - Action Choice: `"Create a new query"` vs. `"Add to my open query"`.
  - Mandatory copy (C12): *"Send this query with the listed evidence to HR?"*

### 11. Send Confirmation Card
- **Use:** Post-submission receipt of an employee query.
- **Elements:**
  - Success Icon & Heading: `"Query Sent"`.
  - Query ID: Monospace badge `QUERY-E05-SEPTEMBER`.
  - Status Tag: Neutral badge `Sent`.
  - Approved copy (C15): *"Your query is Sent. HR can access it for review."*

### 12. Query Status Card
- **Use:** Tracking existing query lifecycle in `CHAT-HR` and `CHAT-EMP`.
- **Allowed Statuses:** Strictly `Draft`, `Sent`, `In review`, `Resolved`, `Closed`.
- **Elements:**
  - Query Reference: `QUERY-E05-SEPTEMBER` (monospace).
  - Employee: Neha Gupta (`E05`).
  - Status Indicator: `In review`.
  - Thread History: Original employee query text, HR response preview (if resolved), and action link: `"Open query details"`.

### 13. Refusal Card
- **Use:** System boundaries, permission denials, and uncalculated requests.
- **Styling:** Border 1 px `#FECACA`, background `#FEF2F2`, text `#0F172A`.
- **Elements:**
  - Error / Shield Icon in `#B91C1C`.
  - Approved Refusal Copy (C10): *"I cannot provide that information. I can help with payroll records you are authorized to access."*
  - Available alternatives: Suggestion chips for authorized tasks.

### 14. FAQ Answer Card
- **Use:** General payroll policy and statutory rule queries (e.g., "What is LOP?", "What is PF?", "What is Gratuity?").
- **Knowledge Source Schema:** Matches course dataset format:
  - `id`: Knowledge ID (e.g., `FAQ-PAY-01`)
  - `category`: `Glossary`
  - `question`: Canonical question title ("What is LOP?")
  - `answer`: Sourced strictly from approved glossary in `output/06-ai-interaction/conversation-design.md`, Section 6 ("Unpaid leave days used to work out paid days for salary.")
  - `link_text`: "To be defined in the payroll FAQ file"
  - `url`: "To be defined in the payroll FAQ file"
- **Card Styling:**
  - Category tag in top right: 12 px Semi-bold `#0F766E` on `#F0FDFA` badge.
  - Question Title: 16 px Semi-bold `#0F172A`.
  - Answer Body: 14 px / 22 px Regular `#334155`.
  - Citation Link: Hidden when url is "To be defined in the payroll FAQ file". When a valid URL is provided, renders as an underlined deep teal link with an external link icon.

---

## 6. Accessibility and Compliance Specifications

1. **Contrast Standards (WCAG 2.2 AA):**
   - Normal text (`< 18 px`) meets or exceeds `4.5:1` contrast ratio against its background.
   - Large text (`>= 18 px` or bold `>= 14 px`) meets or exceeds `3:1`.
   - Essential borders and interactive controls (buttons, chips, inputs) meet `3:1` against adjacent surfaces.
   - Deep teal `#0F766E` against `#FFFFFF` achieves `4.54:1` (compliant for AA text and icons).
   - Primary text `#0F172A` against `#FFFFFF` achieves `15.8:1`.
2. **Keyboard Navigation & Focus Management:**
   - All interactive elements (composer textarea, send button, suggestion chips, card action buttons, "Show calculation") have visible 3 px teal focus outlines with 2 px offset.
   - When the Side Panel (`PANEL-HR`) opens, focus is trapped inside the panel and placed on the Close button. Pressing `Escape` closes the panel and returns focus to the triggering element.
   - When the Mobile Bottom Sheet (`SHEET-EMP`) opens, focus is directed to the sheet title or drag handle; `Escape` closes the sheet.
3. **Screen Reader Accessibility:**
   - Live regions (`aria-live="polite"`) announce incoming assistant messages and card completions.
   - Negative amounts include an explicit `aria-label` (e.g., `aria-label="Decrease of 5,420 INR"`).
   - Table rows in side panels include proper `scope="row"` and `scope="col"` headers.
4. **Reduced Motion:**
   - Respects `prefers-reduced-motion: reduce`. Side panel transitions and bottom sheet animations snap instantly without sliding effects.
   - No celebratory confetti, pulsing numbers, or payment-like animations.

---

## 7. Design Acceptance Checklist

- [x] Two dedicated chat surfaces specified (`CHAT-HR` at 1440 px desktop, `CHAT-EMP` at 390 px mobile).
- [x] Heavy reviews decoupled from chat thread into `PANEL-HR` (480 px) and `SHEET-EMP` (max 85vh).
- [x] Inter typography specified with tabular figures (`tnum`) for all amounts, dates, and tables.
- [x] Deep teal `#0F766E` maintained as the sole brand accent color.
- [x] All 14 rich card types specified in detail with tokens, hierarchy, and actions.
- [x] Query statuses strictly: `Draft`, `Sent`, `In review`, `Resolved`, `Closed`.
- [x] FAQ Answer Card matches course dataset schema with answers strictly from approved glossary.
- [x] No "Verified" badges; no file paths, screen IDs, or sentence codes visible to users.
- [x] Approval card explicitly decoupled from payment semantics (C04 verbatim).
