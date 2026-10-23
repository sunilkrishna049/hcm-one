# HCM One: Problem Statements and How Might We

Sources: the approved [pain points](../03-analysis/pain-points.md), [personas](../03-analysis/personas.md), [journeys](../03-analysis/journey-maps.md), [research](../02-research/secondary-research.md), [competitor analysis](../02-research/competitor-analysis.md) and [BRD](../../input/requirements/Payroll_brd.md). PP and EVD references below link to these sources. This is a proposed strategy for G04 review.

## 1. Summary
HR needs consistent inputs and a clear basis for each pay calculation. Employees need to understand changes and know which records explain the amount. The approved evidence supports these problems, but does not measure their relative effort or prove that a proposed design will increase trust. (PP-01–PP-04, PP-07–PP-13, PP-14–PP-21; EVD-03–EVD-05, EVD-15–EVD-18, EVD-49–EVD-50, EVD-57, EVD-68; AS-4, AS-10–AS-13)

## 2. Problem statements table

Confidence retains the distinctions in the approved pain points. Requirements-led means that the BRD specifies a need without direct research establishing the target-user problem. Related PP and EVD IDs in that row provide context only.

| ID | Problem statement | Persona | Pain points (PP IDs) | Evidence IDs | Type (Evidence-backed or Requirements-led) | Confidence |
|---|---|---|---|---|---|---|
| PS-01 | The Payroll Admin needs a way to establish consistent inputs for each affected person and period because pay changes depend on several records, but today inconsistent records, formula errors and missing entries can undermine the amount. | The Payroll Admin | PP-01–PP-04, PP-14, PP-15, PP-17 | EVD-01–EVD-05, EVD-46, EVD-49–EVD-51, EVD-57, EVD-61, EVD-66 | Evidence-backed | High for PP-01–PP-04 and PP-15. Medium for PP-14 and PP-17. No measured effort ranking. |
| PS-02 | The Pay-Change Employee needs a way to understand why the amount they receive changed because deductions can make the received amount differ from expectations, but today a payroll term or gross amount can leave the reason unclear. | The Pay-Change Employee | PP-07–PP-10 | EVD-09, EVD-10, EVD-13, EVD-15, EVD-27 | Evidence-backed | Medium. Qualitative complaints and interpretation, not prevalence. |
| PS-03 | The Pay-Change Employee needs a way to establish which amount and record explain their pay because reported cases contain mismatches or unexplained recoveries, but today comparing records or receiving a correction can still leave the original amount unclear. | The Pay-Change Employee | PP-11, PP-12, PP-21 | EVD-17, EVD-18, EVD-68, EVD-69 | Evidence-backed | Medium. The recovery finding is one case; EVD-69 is component context only. |
| PS-04 | The Payroll Admin needs a way to establish the applicable calculation basis because the period and company terms can change the result, but today historical rule changes, leave policy choices and notice terms complicate that basis. | The Payroll Admin | PP-06, PP-19, PP-20 | EVD-25, EVD-26, EVD-62–EVD-64 | Evidence-backed | Medium as recorded for these pain points. No verified universal policy or recovery formula. |
| PS-05 | The Payroll Admin and The Pay-Change Employee need a way to know what remains unresolved and who must act because review and explanation can remain incomplete, but today unclear approval history, pending dependencies and unanswered pay questions can prevent closure. | The Payroll Admin; The Pay-Change Employee | PP-05, PP-13, PP-16, PP-18 | EVD-06, EVD-10, EVD-16, EVD-52, EVD-58, EVD-65 | Evidence-backed | Medium for PP-05 and PP-13. High for the documented dependencies in PP-16 and PP-18. No typical delay is established. |
| PS-06 | The Payroll Admin needs a way to establish the applicable bonus eligibility and proration basis because the BRD requires different criteria for roles and eligible days, but today the project has no validated target-company policy for these cases. | The Payroll Admin | PP-14, PP-15 are related input risks, not direct evidence of this policy problem. | EVD-49–EVD-51 provide workflow context only; EG-21 is the evidence gap. Direct source: BRD 4.1, FR-2.4–FR-2.8, BR-5.1–BR-5.3. | Requirements-led | Requirements-led (provisional). High for the explicit requirement; Low for target-company policy evidence. |

## 3. How Might We questions

Each pair uses the sources and confidence of its problem statement. These questions propose directions to explore, not features.

### PS-01: Consistent inputs
- **HMW-01:** How might we help the Payroll Admin establish that the inputs for each affected person and period agree before relying on a pay amount?
- **HMW-02:** How might we help the Payroll Admin recognize an input that is missing or does not belong in the calculation?

### PS-02: Reasons for the received amount
- **HMW-03:** How might we help the Pay-Change Employee understand the main reason for a change before they need to learn payroll terms?
- **HMW-04:** How might we help the Pay-Change Employee distinguish a gross change from the amount they will receive?

### PS-03: Record trust
- **HMW-05:** How might we help the Pay-Change Employee understand which amount is being explained when records disagree?
- **HMW-06:** How might we help the Pay-Change Employee understand the basis of a recovery without hiding the unresolved parts?

### PS-04: Applicable calculation basis
- **HMW-07:** How might we help the Payroll Admin establish which period and company terms apply to an amount?
- **HMW-08:** How might we help the Payroll Admin distinguish a confirmed calculation basis from a policy question that still needs a decision?

### PS-05: Unresolved work and responsibility
- **HMW-09:** How might we help both roles understand what has been decided and what still needs a response?
- **HMW-10:** How might we help the responsible person understand an unresolved pay question without asking for the same information again?

### PS-06: Bonus policy cases
- **HMW-11:** How might we help the Payroll Admin establish why a person qualifies for a bonus under the applicable company terms?
- **HMW-12:** How might we help the Payroll Admin distinguish a clear eligibility or proration case from one that still needs a policy decision?

## 4. Ranking and reasoning

**Proposed. Project owner decides.** This is a strategy ranking based on documented problems and their connection to input gathering and record trust. It is not a ranking of measured effort, commercial value or user pain. The flow build order remains the BRD order.

| Rank | Problem | Reason and evidence limit |
|---|---|---|
| 1 | PS-01 | Input inconsistencies and calculation risks have several High confidence vendor findings. They connect the hike, bonus and settlement work. Settlement effort remains an interpretation. This is the strongest connection across the HR journeys, not proof that input work always takes longest. (EVD-03–EVD-05, EVD-49–EVD-50, EVD-57, EVD-66; AS-6, AS-10, AS-12, AS-13) |
| 2 | PS-03 | Comparing records connects directly to record trust. The correction and recovery cases show why a net amount alone can remain unclear. The evidence is Medium and case-specific. (EVD-17–EVD-18, EVD-68; AS-11) |
| 3 | PS-02 | Several qualitative sources support confusion about net pay and deductions. This complements record trust and is central to the BRD's first employee flows. Preferred explanation depth remains unmeasured. (EVD-09–EVD-10, EVD-13, EVD-15; EG-04) |
| 4 | PS-04 | The evidence establishes policy and date dependencies that affect the calculation basis. It does not establish one current legal treatment or a target company's policy. (EVD-25–EVD-26, EVD-62–EVD-64; GAP-01–GAP-05) |
| 5 | PS-05 | Approval records and blocked work are documented. Employee questions can remain unresolved. These are necessary control and closure concerns, but the sources do not measure their relative burden. (EVD-06, EVD-10, EVD-16, EVD-52, EVD-58; EG-03, EG-09, EG-26) |
| 6 | PS-06 | The requirement is explicit, but dedicated user evidence about target-company eligibility and proration is missing. Retain the problem instead of treating missing evidence as a reason to remove the bonus flow. (FR-2.4–FR-2.8; EG-21) |

The Project owner approved DEC-003 and DEC-005 as provisional opportunity selections. AS-10 through AS-13 remain Low confidence and Unvalidated for Agent 08. Their approval does not establish a measured ranking. (G03 approval; [decision log](../../project-memory/design-decisions.md); [assumptions](../01-project/assumptions.md))

## 5. What these problems do not cover
- **High for scope:** They do not authorize salary payments, full monthly payroll, statutory filings, a Manager role, real payroll data or Form 26AS comparison. External records in complaints are context, not integrations to add. (BRD 5.3; FR-4.14)
- **High for requirements; Low for direct user evidence:** Privacy, identity checks, secure operation and human approval remain mandatory even where no pain point establishes a personal fear or preference. They are guardrails, not claims of observed user behavior. (GR-1.1–GR-8.1; EG-05, EG-06)
- **Low:** These problems do not resolve GAP-09 or establish that a clearance hold is legally permitted. See the proposed direction in [MVP scope](mvp-scope.md). (GAP-09; DEC-004; EVD-65, EVD-71, EVD-81; EG-25)
- **Low:** Ask Agent 02 for evidence on actual stage effort, target bonus policies, query outcomes, settlement disputes and statement detail. Existing EG-01, EG-03–EG-04, EG-20–EG-22 and EG-26–EG-28 record these limits. No research was added in this run.
- **Low:** Competitor documentation gaps do not establish an exclusive market opportunity. No time saving, error reduction or trust increase is claimed. ([Competitor analysis](../02-research/competitor-analysis.md), Sections 5–6; AS-4, AS-8)
