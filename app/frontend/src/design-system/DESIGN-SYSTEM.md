# HCM One Design System

## Overview
This design system provides an accessible, swappable component library and token contract for HCM One based on `output/07-prototype/visual-spec.md`.
All design values (colors, typography, spacing, radii, dimensions, focus rings) are declared as CSS variables in [tokens.css](tokens.css).
Screens import and use only these tokens and the components located in `src/design-system/components/`.

No screen or component contains hard-coded hex colors, arbitrary pixel typography, or custom ad-hoc styling.

---

## Token Reference ([tokens.css](tokens.css))

### 1. Typography
- `--font-sans`: `'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`
- `--font-mono`: `ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace` (Strictly for IDs and technical references)
- `--font-weight-regular`: `400`
- `--font-weight-medium`: `500`
- `--font-weight-semibold`: `600`
- Tabular figures (`font-feature-settings: "tnum"`) are enabled for all financial amounts, dates, and tables.

### 2. Typographic Scale
| Token | Size / Line Height | Weight | Typical Use |
|---|---|---|---|
| `--font-size-hero-desktop` | 40px / 48px | 600 | Desktop hero net arrears or primary change |
| `--font-size-hero-mobile` | 32px / 40px | 600 | Mobile hero take-home or TDS change |
| `--font-size-title-page` | 24px / 32px | 600 | Primary screen title |
| `--font-size-title-section` | 20px / 28px | 600 | Section headers |
| `--font-size-card-number` | 24px / 32px | 500 | Secondary amount cards |
| `--font-size-body` | 16px / 24px | 400 | AI assistant copy, body prose, inputs |
| `--font-size-table` | 14px / 20px | 400/600 | Dense HR data tables, controls |
| `--font-size-label` | 14px / 20px | 400 | Sourced labels, rules metadata, flags |
| `--font-size-small` | 12px / 16px | 400 | Badges, timestamps, helper labels |

### 3. Palette Tokens
- **Brand Accent:**
  - `--color-brand-accent`: `#0F766E` (Single brand accent: deep teal)
  - `--color-brand-hover`: `#115E59`
  - `--color-brand-tint`: `#F0FDFA`
  - `--color-brand-text-on-accent`: `#FFFFFF`
- **Neutrals & Surfaces:**
  - `--color-background`: `#FFFFFF`
  - `--color-surface`: `#F8FAFC`
  - `--color-text-primary`: `#0F172A`
  - `--color-text-secondary`: `#475569`
  - `--color-border-interactive`: `#64748B`
  - `--color-divider`: `#E2E8F0`
  - `--color-disabled-surface`: `#CBD5E1`
- **Semantic Statuses (Always paired with text labels and distinct icons; never color alone):**
  - **Success:** `--color-status-success-text` (`#166534`), `--color-status-success-surface` (`#F0FDF4`)
  - **Warning / Limitation:** `--color-status-warning-text` (`#92400E`), `--color-status-warning-surface` (`#FFFBEB`)
  - **Error / Refusal:** `--color-status-error-text` (`#B91C1C`), `--color-status-error-surface` (`#FEF2F2`)
  - **Neutral / Draft:** `--color-status-neutral-text` (`#334155`), `--color-status-neutral-surface` (`#F1F5F9`)

### 4. Spacing Scale
`--space-1` (4px), `--space-2` (8px), `--space-3` (12px), `--space-4` (16px), `--space-6` (24px), `--space-8` (32px), `--space-12` (48px), `--space-16` (64px)

### 5. Radii & Layout Dimensions
- `--radius-card`: 8px
- `--radius-input`: 6px
- `--radius-button`: 6px
- `--radius-pill`: 9999px (Status tags)
- `--width-hr-desktop`: 1440px
- `--width-reading-column`: 720px
- `--width-drawer-desktop`: 480px
- `--width-employee-mobile`: 390px
- `--size-min-interactive`: 44px (WCAG 2.2 target size requirement)
- `--focus-outline-width`: 3px, offset: 3px (WCAG 2.2 visible focus)

---

## Component Inventory (`src/design-system/components/`)

1. **MessageBubble (`MessageBubble.tsx`)**:
   Renders verified assistant dialogue using exact approved sentences (C01–C29) with an assistant avatar badge, polite tone, and slot interpolation.

2. **NumberCard (`NumberCard.tsx`)**:
   Renders financial metric cards with label, literal formatted amount, explicit currency (`INR`), certainty badge, and integrated "Show calculation" button.

3. **CertaintyLabel (`CertaintyLabel.tsx`)**:
   Renders the 5 approved certainty states (`Complete for this scope`, `Incomplete`, `Rule not verified`, `Needs HR decision`, `Cannot explain from available payroll data`) with dedicated icon, surface, and text.

4. **CalculationBreakdown (`CalculationBreakdown.tsx`)**:
   Displays mathematical provenance: formula in words, input record IDs, rule IDs with version and verification date, certainty, and flags.

5. **SourceLink (`SourceLink.tsx`)**:
   Renders masked source record references (file and record ID) with accessible click-to-proof behavior.

6. **ApprovalBar (`ApprovalBar.tsx`)**:
   HR proposal decision bar with `Approve selected scope`, `Edit with reason`, and `Reject`. Displays approved C04 disclaimer and enforces version/scope guards.

7. **ComponentList (`ComponentList.tsx`)**:
   Displays full settlement and component breakdowns with classification, amount, due date with C20 notice, preparation status, and proof triggers.

8. **QueryDraft (`QueryDraft.tsx`)**:
   Review interface for employee queries allowing description editing, removable evidence tags, add-or-new candidate choice, and explicit confirmation (C12/C13).

9. **Buttons (`Button.tsx`)**:
   Primary teal button, secondary outline button, danger button, and ghost buttons with minimum 44px touch targets.

10. **Inputs (`Input.tsx`, `Textarea.tsx`, `Select.tsx`)**:
    Accessible form controls bound to interactive borders with explicit labels and helper errors.

11. **Drawer & Sheet (`Drawer.tsx`, `Sheet.tsx`)**:
    Accessible sliding modals powered by Radix UI Dialog primitive (Desktop 480px side drawer on desktop; mobile bottom sheet on mobile) for calculation proof and detailed breakdowns.

12. **TopDemoBar (`TopDemoBar.tsx`)**:
    Global control bar with login switcher (HR01, HR02, Employees), scenario picker (1 to 13), and "Reset demo" trigger.
