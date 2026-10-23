# Deterministic payroll calculation engine

Simplified rules for a portfolio demo. Not for real payroll.

Python 3.12 and the standard library perform every calculation. There are no AI calls, network calls or runtime dependencies. Pytest is the only direct development dependency; pip installs its normal transitive dependencies. The engine reads `data/rules/` and `data/mock/` and writes proposals and calculation records to `data/generated/`. It never approves, applies or pays a change.

## Windows setup and run

Run PowerShell from the project root. Python 3.12 must be installed. This workspace already includes a Python 3.12 virtual environment in `engine/.venv/`.

```powershell
# For a fresh checkout, create the environment with an installed Python 3.12.
py -3.12 -m venv engine/.venv
& .\engine\.venv\Scripts\python.exe -m pip install -r engine/requirements.txt
& .\engine\.venv\Scripts\python.exe engine/run.py --as-of 2026-10-13
```

`--as-of` is mandatory execution context, not a hardcoded business date. It supplies the calculation date required by MR-02. The run records it in `data/generated/run-context.json`. It does not imply HR approval or a receipt date for tax. All employee, attendance, salary, bonus-request, exit and authorization inputs come from `data/mock/`. Rates, limits, calendar rules, thresholds and effective dates come from `data/rules/`. Scenario routing is read from the mock README's thirteen-row coverage table. History months come from the processed payroll runs, and comparison months are the last two processed months. The CLI works from any current directory because it resolves the project root from its own location.

The supplied undated original salary structures are used as the fixture explicitly requests. No historical salary change or pending hike is applied. Future recurring salary is projected from that original structure, through recorded employment where an exit exists, without inventing future LOP. The tax-year month count comes from the company's tax-year dates. Annual bonus operands and gratuity operands are parsed from the supplied formula strings without `eval`. Calendar identities and percentage unit conversion are arithmetic, not business rates.

## Run the tests

```powershell
& .\engine\.venv\Scripts\python.exe -m pytest engine/tests -q --junitxml=engine/test-results.xml
```

Generate the scenario files before tests. The suite has 71 tests: thirteen scenario tests, forty-three fixed owner hand-checks and fifteen invariant or display-export checks. All original hand-checks are unchanged; nineteen display checks were appended. The regression checks all 89,458 pre-export value objects across twenty generated files. Tests do not change protected inputs. Expected hand-check values must never be changed to make calculations pass.

## Modules

| Module | Responsibility |
|---|---|
| `run.py` | Requires Python 3.12, accepts the explicit calculation date and starts generation. |
| `payroll/core.py` | Loads JSON using Decimal, checks rule verification and effective bounds, builds source and rule references, rounds lines with the approved half-up convention and propagates unknown values. |
| `payroll/history.py` | Calculates paid-day salary components, PF by dated calendar segments, tax brackets, rebate, cess, previous-employer declarations, monthly TDS and payslip history. |
| `payroll/flows.py` | Builds proposals, components, bonus and recovery aggregates, comparison reasons and authorization checks. |
| `payroll/display.py` | Copies display operands with source references and wraps calculated salary totals and wage bases with provenance. |
| `payroll/scenarios.py` | Reads the mock scenario coverage, calculates all thirteen cases, writes generated files and refreshes the ambiguity list below. |
| `tests/test_scenarios.py` | Checks each BRD v1.2 scenario's behavior, including expected blocked calculations. |
| `tests/test_hand_checks.py` | Checks the owner's supplied exact amounts, dates, eligibility, flags and unresolved net. |
| `tests/test_invariants.py` | Checks provenance, complete-only payslips, rounding ties, rule changes, authorization coverage through scenario tests, repeatability and totals. |
| `tests/test_display_exports.py` | Checks source copying, null aggregates, signed ranking, authorization, rule metadata and legacy value fingerprints. |

## Results and provenance

- `data/generated/payslips.json` contains only fully calculated payslips. A required unknown line prevents issuance. The amount objects retain their independent certainty.
- `data/generated/payslip-failures.json` records every blocked employed month and its reasons, plus separate months before employment.
- `data/generated/calculation-ledger.json` retains complete and partial calculations. It is not a payslip. Missing earnings propagate into subsequent cumulative tax calculations rather than being replaced with zero. With the approved AMB rules, E03's missing July attendance is the only reason for blocked historical payslips; July through September remain incomplete.
- `data/generated/bonus-proposals.json` includes annual bonus and Sales incentive results, eligibility lists and reasons. Known gross awards are independent of receipt-month tax.
- `data/generated/scenarios/scenario-01.json` through `scenario-13.json` contain the scenario results. Scenario 12's result is exactly `{"status": "Permission denied"}`; it contains no target records or amounts.
- `data/generated/scenario-summary.json`, `run-context.json` and `ambiguities.json` record statuses, the explicit execution context, input hashes and detected unresolved interactions.

Every calculated amount and date is an object with `value`, `formula`, `inputs`, `rule_ids`, `certainty` and `flags`. The same format is used for calculated day counts and service duration. Rules include the entry ID, rule source file, supplied source, effective dates, verification status and original rule value. Rules also include rules_version and verified_on from their file. Both-null effective dates remain null and carry date_note: "Applies to all demo periods"; owner verification is not an effective date or independent legal verification. Inputs identify their source file and record ID. A `$` record ID denotes the entire recovery collection used to establish absence; `missing:` references explicitly identify absent required records. The runtime date references the run-context record. Totals merge the provenance of all their dependencies.

Salary earnings are separate rounded component lines. Exact half-rupee ties use the approved round-half-up rule; 1,249.50 becomes 1,250. PF wage is Basic plus DA earned after LOP. Monthly LOP is spread evenly across the month. The earned monthly PF wage and the applicable ceiling are each allocated to a dated segment by its calendar-day share, and the lower amount is used. PF contributions are separate rounded lines per dated segment. Employer EPF is the rounded employer contribution less rounded EPS, so the allocation reconciles when both are known. Tax bracket amounts and cess are rounded lines. Totals are sums of those rounded lines. A null amount is never treated as zero. A null date with complete certainty means no separate date applies, as its formula explains; no payment date is generated. Gratuity eligibility is tested on actual service before part-year rounding, and an ineligible gratuity is explicitly `Not applicable` with zero amount.

Pending hike and bonus TDS is estimated for the next open payroll month from `payroll-runs.json`. Each result records that month and the flag `Estimated TDS if approved and paid in October 2026 payroll` for this fixture. Estimates compare hypothetical monthly TDS with and without the proposal using original payroll history. A hike's proposed projection includes revised recurring salary from its effective date and its rounded arrears once. Its recurring-salary tax effect and incremental monthly arrears tax effects are shown separately and reconcile to the overall receipt-month TDS impact. The net arrears figure deducts that overall proposal TDS impact and employee PF change. A bonus estimate includes the gross award once. A later payment month triggers a fresh projection, prior-TDS count and remaining-month count; `Flows.proposal_tax` can also accept an explicit payment month. Missing intervening actual payroll blocks the estimate rather than dropping a month. These are standalone proposals; a hike and bonus for the same employee are not jointly applied. No hypothetical amount is written into historical payslips or original input records.

Settlement results show the independent amount, classification, applicable due date, status and unresolved reason for each component. Exemptions are applied once to their respective settlement components. Confirmed final salary is never held by a pending clearance. E12's recorded asset exposure is not treated as an allowed deduction while clearance is pending, and no final net is created. Component amounts remain proposals requiring HR approval.

E16 has no change in salary earning components between August and September. Its employee PF nevertheless rises when the dated ceiling changes, reducing net pay by ₹420. The explanation separates that deduction change from salary earnings. E05's gross falls by ₹5,000 and employee PF rises by ₹420, so its net falls by ₹5,420. September employee PF is ₹2,220. E01's June employee PF is ₹1,800 despite its LOP, because the earned PF wage remains above the ceiling. E06's tax calculation includes its accepted prior-employer gross and TDS once and applies one standard deduction for the tax year.

Missing input is marked `Incomplete`. Undefined rule interactions are marked `Rule not verified`. A missing waiver decision is `Needs HR decision`. The other permitted labels are `Complete for this scope` and `Cannot explain from available payroll data`. These are calculation certainty labels, not confidence scores or approvals. Overall scenario certainty may be blocked even when a specific amount is complete; tests assert that separation.

## Display data exported for screens

Each scenario file has a top-level display_inputs beside scenario_id, description and result. Copied leaves contain value, source_file, record_id, source_field and certainty. Values are copied without rounding. Calculated leaves add a nested calculation in the existing six-field format and identify their generated scenario record. Missing operands stay null and Incomplete. A missing notice waiver is Needs HR decision. Scenario 12 exports an empty display_inputs and retains exactly {"status": "Permission denied"} as its result, with no target data.

| Scope | New fields |
|---|---|
| PQ-01; scenarios 1–3 | requested_hike_percentage, effective_date, old_monthly_salary.components and .total, proposed_monthly_salary.components and .total. Components are Basic, DA, HRA and special allowance. Old components are copied; totals and proposed components use existing allocation and rounding rules without LOP. |
| PQ-02; scenarios 6–8 and 13 | resignation_date, last_working_day, notice_period_required, notice_period_served, notice_waived, copied from the exit record. |
| PQ-04; scenarios 4–5 | bonus_requests[].employees for scenario 4; affected employees for scenario 5. Annual fields: rating, policy_rating_rate_percent, applied_rating_rate_percent. Sales fields: target, achievement. The rate selector is shared with bonus calculation. Ineligible employees can have a known policy rate, but applied rate is null with Not applied status. Missing ratings remain Incomplete. |
| PQ-05; scenarios 1–3 and 9–11 | months[month].lop_days and .calendar_days, copied from own attendance. Missing E03 July attendance exports nulls without using another employee's record. |
| PQ-06; scenario 10 | previous_employer_declared_gross, previous_employer_tds, northwind_tds_already_deducted, remaining_yearly_tax. Northwind tax excludes previous-employer tax and the current month. Remaining yearly tax is annual tax less total already deducted, before the monthly withholding rule. |
| PQ-11; scenarios 6–8 and 13 | encashable_leave_days_used, last_drawn_basic, last_drawn_da, last_drawn_basic_plus_da. Used leave is selected from the recorded days or policy cap. The combined gratuity wage base is calculated. |

Additional calculations inside result preserve existing rounded lines:

- **PQ-03:** Bonus requests have aggregates.eligible_count, not_eligible_count, needs_input_count, group_total_gross, group_total_tds and group_total_net. Totals include only known eligible employees. Unknown eligible TDS or net propagates to null and Incomplete. Annual known gross is 213929; group TDS and net are null because E03 is incomplete. Sales gross and net are 120000, TDS 0.
- **PQ-10:** Settlements have recoveries_total and known_recoveries_subtotal, excluding PF and TDS. E12's total is null and Incomplete; known subtotal is 56667 with Excludes unresolved asset recovery. No final net is created.
- **PQ-12:** Comparisons have reasons[], each with type, signed effect_amount in the calculation format and source_references. Rank by absolute take-home effect, largest first. Deduction increases have negative effects. Ties retain earnings, PF, TDS order; unknown effects follow known effects and keep their certainty. These reconcile accounting effects rather than claiming independent counterfactual estimates. The PF ceiling label identifies changed dated rules; its flag and provenance retain the earned wage after LOP interaction. E05: LOP -5000, PF ceiling change -420.

Tax details throughout payroll and proposals also expose northwind_tds_already_deducted, previous_employer_tds and remaining_yearly_tax as calculations without changing any original monthly tax, yearly tax, prior aggregate or net.

Rule files declare rules_version: "Northwind demo rules v1" and verified_on: "2026-10-13". Existing values, dates, sources and statuses are unchanged. Every rule_ids entry copies the version. Undated entries have date_note: "Applies to all demo periods", retaining null effective dates. These exports do not invent approval versions, audit events, query replies or delivery.

## Approved ambiguity resolutions

Project owner approved AMB-01 (round half up), AMB-02 (earned PF wage after evenly spread LOP and ceilings capped per dated segment), and AMB-03 (next-open-month proposal TDS estimate with the assumption shown). See [DEC-025](../project-memory/design-decisions.md) and the `rounding_ties`, `pf_wage_with_lop`, `lop_across_dated_segments` and `proposal_tds_estimate` rule records. The ambiguity list below is regenerated on each run. Missing attendance, missing performance and pending asset clearance are input or operational gaps, not unresolved rule ambiguities.

## Ambiguities found

None.
