# HCM One: Visual Specification

Proposed for G07. This system applies to the six screens in [screen-inventory.md](screen-inventory.md). It specifies a minimal, typography-led interface with one deep teal accent, white space and prominent numbers. It does not claim tested usability or accessibility conformance.

**High for required direction:** HR desktop is 1440 px wide. Employee mobile starts at 390 px. Accessibility targets WCAG 2.2 AA, with keyboard and screen reader support. **Proposed design choices:** The tokens, fonts, dimensions and layouts below implement that direction. Their usability remains unvalidated in AS-14, AS-16 and AS-17. Sources: [Agent 07](../../agents/07-prototype.md), Design direction; [UX principles](../04-strategy/ux-principles.md), UXP-01–UXP-07; [personas](../03-analysis/personas.md), goals and Unknowns.

Numeric tokens below are design parameters, not payroll facts. Payroll amounts, dates, counts and identifiers use only the generated bindings in [screen-specs.md](screen-specs.md), Section 8. No token authorizes rounding, arithmetic, currency abbreviation or an invented record.

## 1. Typography

Use **Inter** for all text and numbers. Use tabular figures with font-feature-settings: "tnum" for amounts, dates and tables. Use a monospace font only for technical IDs, including query IDs and record references. **Reason:** "Tabular figures align numbers in columns and feel calmer for payroll; monospace is kept for technical IDs." This typography is Approved by Project owner. Verify Inter availability in the code prototype; any temporary sans-serif fallback must be recorded. Monospace must never be the amount font.

| Token | Size and line height | Weight | Use |
|---|---|---|---|
| Number hero, desktop | 40 px / 48 px | 600 | The main sourced net arrears or change |
| Number hero, mobile | 32 px / 40 px | 600 | The main sourced take-home or TDS change |
| Page title | 24 px / 32 px | 600 | Screen purpose |
| Section title | 20 px / 28 px | 600 | Breakdown, evidence and review |
| Number card | 24 px / 32 px | 500 | Sourced secondary amounts |
| Body and input | 16 px / 24 px | 400 | AI wording, instructions, fields and mobile controls |
| Table and desktop control | 14 px / 20 px | 400 or 600 for headers | Dense HR detail; never compress below this size |
| Supporting label | 14 px / 20 px | 400 | Source, rule and flag labels |

Use sentence case. Use short labels and left-aligned prose. Align financial columns to the right. Keep signs and literal digits exactly as generated; show INR as a separate label. Wrap long flags and IDs. Do not use a minus sign as a decorative bullet beside a positive amount. Do not show compact forms such as K or lakh in place of the stored value.

Do not use heading weight to imply that a known partial total is complete. When net is unavailable, make the limitation the hero. Keep exact Agent 06 messages unchanged; shorten the layout by progressive detail, not by paraphrasing approved copy. Sources: UXP-01–UXP-04; [trust-explainability](../06-ai-interaction/trust-explainability.md), explanation layers and certainty; [content contract](screen-specs.md).

## 2. Colors

**Accent: deep teal, #0F766E.** It is the only brand accent. Use semantic status colors only for status and errors. Gray surfaces and borders support hierarchy.

| Token | Value | Use |
|---|---|---|
| Background | #FFFFFF | Page, drawer and sheet |
| Surface | #F8FAFC | Small grouped fields and source details |
| Primary text | #0F172A | Headings, values and body |
| Secondary text | #475569 | Supporting copy |
| Brand accent | #0F766E | Primary action, source link and selected control |
| Brand hover | #115E59 | Hover on enabled accent controls |
| Brand tint | #F0FDFA | Selected surface with dark text |
| Interactive border | #64748B | Input and control boundary |
| Decorative divider | #E2E8F0 | Nonessential separators |
| Disabled surface | #CBD5E1 | Disabled controls with readable dark text |
| Success text and icon | #166534 | Recorded completion status |
| Success surface | #F0FDF4 | Completion status background |
| Warning text and icon | #92400E | Missing or unresolved limitation |
| Warning surface | #FFFBEB | Limitation background |
| Error text and icon | #B91C1C | Error or refusal |
| Error surface | #FEF2F2 | Error background |
| Neutral status text | #334155 | Recorded draft or review status |
| Neutral status surface | #F1F5F9 | Neutral status background |

White text is allowed on the deep teal primary button. Links use underlining in prose and a visible focus state. Color must never be the only signal: every status has a label and a distinct icon or shape.

Do not make Complete for this scope look Approved. Do not make Approved and ready for payroll look Paid. Use an explicit scope label beside certainty and an independent workflow label. A warning badge does not mean a whole settlement is Held. Sources: UXP-04–UXP-05; [approved states](../05-architecture/edge-cases-states.md), Sections 2–4; [approval wording](../06-ai-interaction/approval-failure-handling.md).

## 3. Spacing, grid and surfaces

| Token | Value | Use |
|---|---|---|
| Spacing scale | 4, 8, 12, 16, 24, 32, 48, 64 px | Consistent internal gaps and section separation |
| HR reference frame | 1440 px | Required desktop starting frame |
| HR grid | 12 columns; 64 px outer margins; 24 px gutters | Review table and supporting panel |
| Desktop reading width | Maximum 720 px | AI wording, request composer and confirmation |
| Desktop proof drawer | 480 px; bounded by available viewport | Amount detail within SCR-02 or SCR-03 |
| Employee reference frame | 390 px | Required mobile starting frame |
| Employee grid | One column; 20 px outer padding; 16 px component gaps | Reading and actions without side-by-side cards |
| Mobile detail sheet | Available viewport width | Amount detail within SCR-04–SCR-06 |
| Card radius | 8 px | Number and evidence cards |
| Input and button radius | 6 px | Controls |
| Label radius | Fully rounded | Short status labels; never clipped text |
| Minimum interactive target | 44 by 44 px | Touch and keyboard controls |
| Focus outline | 3 px, with 3 px offset | Visible teal focus on white |

Use flat surfaces with subtle dividers. Avoid ornamental shadows, gradients, illustrations and charts. Blank space separates scope, summary, reasons and proof. HR uses a wide review table with a reading panel where needed. Employee puts the change first, then reasons, then detail actions. On narrow desktop viewports, stack the panels rather than reducing text or hiding blockers.

Tables may scroll inside a labeled region when necessary, but the page must reflow without horizontal page scrolling. The mobile breakdown uses labeled rows rather than shrinking a desktop table. Keep primary actions visible without covering content or keyboard focus. Sticky approval controls need reserved content space.

Source: Agent 07 Design direction; UXP-02–UXP-04; [screen specifications](screen-specs.md), Sections 1–6.

## 4. Core components

### Message bubble
Use a light surface, an explicit assistant label and the exact approved sentence from screen-specs Section 7. Employee bubbles are short reading blocks; HR explanations sit beside scope and proof. Long introductions can use an accessible disclosure without changing their text. Loading, missing data and refusal are distinct messages. Never use internal actor terms in user-facing sentences. Do not pretend a pending action succeeded.

### Number card
Contain a plain label, literal generated amount, INR label, period or component scope, certainty and Show calculation. Source access is available from the summary through the same drawer or sheet. Never show a missing value as zero or a skeleton with invented digits. The default emphasis is expected net arrears for HR and take-home or TDS change for Employee. An incomplete result uses a limitation headline instead of a fabricated net.

### Calculation breakdown
Display the stored value, formula in words, input source file and record IDs, rule IDs, sources, effective dates, certainty and flags. Do not evaluate the formula. Missing required operands use Not available in generated data. Undated rules show their exact date_note, Applies to all demo periods; retain actual effective dates where present and show rules_version separately from verified_on. The PF detail keeps dated segments; the tax detail keeps the actual stored scope. Distinguish employee deductions from employer contributions. Totals lead to their stored contributing lines without a newly calculated subtotal.

### Source link
Use View source or the readable file and record label. Keep the path and exact JSON pointer in design annotations and the detail layer, not in an AI sentence. The source must inherit authorization and the selected scope. Never link an Employee to a full dataset containing colleagues. A future implementation should expose only the authorized record, not make the repository file publicly downloadable.

### Certainty label
Use only the five approved result labels: Complete for this scope; Incomplete; Rule not verified; Needs HR decision; Cannot explain from available payroll data. Pair the label with its scope and recorded limitation. Use generated certainty where it exists; derive no confidence score. Needs input is an existing proposal state, not a sixth certainty label. Loading has no final result certainty. Sources: [trust-explainability](../06-ai-interaction/trust-explainability.md), certainty states; generated result contract in screen-specs.

### Approval bar
Show authorized selected scope, Approve selected scope, Edit with a reason and Reject. Include exact C04 and keep it readable beside the action. Without a current stored version and valid scope, approval remains unavailable. An edit clears prior eligibility for approval and uses C05. Changed version uses C25. Successful approval is shown only after an actual persisted event; it is ready for payroll, never payment. No bulk or partial approval bypasses the approved guards. Sources: DEC-011–DEC-014; approval-failure-handling Sections 2–4.

### Component list
A settlement row has component name, classification, amount, applicable due date, preparation status, approval status, certainty, hold or unresolved reason and Show calculation. Known lines remain visible when the final net is incomplete. Not applicable is not an unknown amount. A null unresolved asset remains unavailable. Do not turn pending clearance into a hold on salary. A due date uses exact C20; it is not a payment date. Sources: DEC-008, DEC-019, DEC-024; Flow 3; UXP-05; generated settlement bindings.

### Query draft
Use category, generated period, the Employee's editable description, removable relevant evidence and an explicit add-or-new choice when a genuine own open candidate exists. Show exact C12 or C13 before the corresponding send or append action. Changes invalidate confirmation. Draft remains unsent after cancel, silence or failure. The current fixture never creates a new ID, timestamp or success state. Sources: DEC-014, DEC-017; Flow 6; UXP-06–UXP-07.

### Shared detail and controls
A desktop drawer and mobile sheet belong to their parent screen. They inherit its role and scope. Give them a heading and Close control. Restore focus to the triggering amount. Provide text labels with every icon. Use a proper labeled input for the request or reply, not an unlabeled chat placeholder. Selected period and proposal type are explicit. Errors name the affected scope and keep valid data visible when safe.

## 5. Screen composition

| Screen | Main hierarchy | Secondary detail |
|---|---|---|
| SCR-01 Prepare a proposal | Request, employee, clarification, confirmation | Existing calculation is separately labeled; sourced contractual inputs and explicit confirmation are visible |
| SCR-02 Review a proposal | Scope and blocker, net hero, flags, rounded-line source table, approval bar | Proof drawer and edit panel; later bonus and component modes reuse the frame |
| SCR-03 Review a payroll query | Recorded query status, employee words, evidence, reply | Authorized proof and explicit resolution action |
| SCR-04 Understand my payroll | Own scope, take-home or TDS change, reasons, approved message | Breakdown, glossary and proof sheet; later statement needs approved snapshot |
| SCR-05 Review my query draft | Unsent state, employee words, evidence, add-or-new choice, confirmation | Source sheet; no successful-send record invented |
| SCR-06 Track my payroll query | Own ID and recorded status, original words, actual reply | Recorded history only; no response-time promise |

“Rounded-line source table” means already rounded values copied from the engine. The prototype never rounds them. All payroll bindings are in screen-specs Section 8. This hierarchy follows Agent 06's explanation layers: outcome, reason, component detail, calculation proof, next action. Sources: DEC-016; UXP-01–UXP-07.

## 6. Accessibility and implementation checks

Target WCAG 2.2 AA. Normal text must reach 4.5:1 contrast. Large text and essential control boundaries must reach 3:1. Test every actual pairing, including focus, hover, status and disabled treatment where applicable. Decorative dividers do not identify an input boundary. These are design acceptance criteria; a Markdown spec is not proof of an accessible implementation.

Use semantic headings, buttons, form labels and tables. Give tables a caption and column headers. Associate inline errors with the affected field. Read a negative amount as a decrease through its visible field label and accessible description; retain its exact value. Announce loading and completion politely once. Announce blocking errors clearly without repeatedly reading every table cell.

Support the complete task by keyboard. Keep visible focus, logical reading order and no keyboard trap. Drawers and modal sheets move focus to the heading or first appropriate control, contain focus only while modal, close with Escape, and restore focus. Status updates must not move focus unexpectedly. An approval confirmation names its current scope and consequence.

At 200% text zoom and a 320 px viewport, wrap labels, flags and sources without clipping. Keep controls at least 44 px high and generous separation between reject and approve. Do not make hover the only way to open calculation proof. Do not hide a missing amount behind a tooltip. Keep the sticky action area from obscuring focused content.

Respect reduced motion. No pulsing amount, typing performance, celebratory approval animation or payment-like success animation. Loading can use a static placeholder and the exact approved loading message.

Check authorization before displaying a record, source or cached detail. Permission denial clears private context. Screen reader output must not expose hidden target amounts. Statement access and query follow-up stop at the DEC-019 access boundary.

Sources: Agent 07 Design direction; BRD v1.2 GR-2.1–GR-2.6; UXP-04, UXP-07; approved access and failure handling. Actual contrast, keyboard, assistive-technology and comprehension checks belong to the later designed and implemented artifact.

## 7. Open questions

- Font availability and final component contrast need verification in the code prototype. Figma is optional later for visual polish and case study images; figma-ai-prompts.md is retained as a bonus. This run updates specifications, not an implemented interface or a Figma file.
- The remaining operational input gaps and unexported declaration month range are listed in screen-specs Section 9. DEC-029 resolves the TDS wording; no declaration months may be invented.
- Existing AS-14, AS-16 and AS-17 cover component comprehension, certainty understanding and wording usefulness. No user benefit is asserted from this visual direction.
