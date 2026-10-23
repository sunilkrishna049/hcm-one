# HCM One: Pain Points

Sources: the [approved research](../02-research/secondary-research.md), the [approved brief](../01-project/project-brief.md) and the [existing assumptions](../01-project/assumptions.md). Evidence IDs below link to the research. No outside evidence was used.

These pain points describe problems. They do not propose features. High confidence refers to documented failure modes, not measured frequency or severity in target companies. Medium confidence includes qualitative complaints and interpretation. The top three lists are a synthesis for review, not a measured ranking. (Research: Evidence table and research limits; EG-01–EG-04)

## 1. Summary

### HR Admin: top three
1. **High:** Attendance and payroll inputs from different places can disagree. Reconciling them creates work and errors. (PP-02; [EVD-03](../02-research/secondary-research.md))
2. **High:** Bonus input files can contain formula errors, duplicate employees or omissions. The wrong amount or employee can reach payroll. (PP-15; [EVD-50](../02-research/secondary-research.md))
3. **Medium:** Settlement combines open items from several records. HR must reconcile them to establish the final amount. This is an interpretation of documented dependencies, not measured effort. (PP-17; [EVD-57](../02-research/secondary-research.md), [EVD-66](../02-research/secondary-research.md))

### Employee: top three
1. **Medium:** Employees can notice a take-home change without understanding its cause. (PP-07; [EVD-15](../02-research/secondary-research.md))
2. **Medium:** Conflicting pay records make it difficult to tell which number is correct. (PP-11; [EVD-17](../02-research/secondary-research.md), [EVD-18](../02-research/secondary-research.md))
3. **Medium:** A settlement recovery can be unclear when its calculation is not understood. This is supported by one reported case. (PP-21; [EVD-68](../02-research/secondary-research.md))

## 2. HR Admin pain points

### Historical inputs and calculations

| ID | Pain point | What happens because of it (impact) | Evidence IDs | Confidence | Related flow |
|---|---|---|---|---|---|
| PP-01 | Past months can have different paid days, salary components and statutory bases. A flat arrears calculation can miss these differences. | The arrears result can be wrong. Each affected period needs to be recalculated. | [EVD-01](../02-research/secondary-research.md), [EVD-02](../02-research/secondary-research.md) | High | Hike |
| PP-02 | Separately maintained attendance and payroll records can disagree. | HR must reconcile inputs. LOP inconsistencies can affect pay. | [EVD-03](../02-research/secondary-research.md) | High | Hike |
| PP-03 | Incorrect employee master data can enter payroll calculations. | Deductions or salary credits can be wrong. Reconciliation work follows. | [EVD-04](../02-research/secondary-research.md) | High | Hike |
| PP-04 | Spreadsheet formulas, versions and calculation history can be unreliable. | Calculation errors can occur. Earlier work can be difficult to trace. | [EVD-05](../02-research/secondary-research.md) | High | Hike |
| PP-06 | Company contribution policies and dated rule changes complicate historical PF calculations. | Using the wrong period or policy can change the PF result. The approved evidence does not measure the effort involved. | [EVD-25](../02-research/secondary-research.md), [EVD-26](../02-research/secondary-research.md) | Medium | Hike |

### Approval history

| ID | Pain point | What happens because of it (impact) | Evidence IDs | Confidence | Related flow |
|---|---|---|---|---|---|
| PP-05 | Email and file approvals can leave responsibility and approval history unclear. | It can be difficult to establish who reviewed or approved a change. | [EVD-06](../02-research/secondary-research.md) | Medium | Hike |

### Bonus inputs and approval dependencies

| ID | Pain point | What happens because of it (impact) | Evidence IDs | Confidence | Related flow |
|---|---|---|---|---|---|
| PP-14 | Variable-pay inputs can pass through preparation, files and payroll imports. Their source and handoff can be difficult to reconcile. | HR must work across inputs before the prepared amount reaches payroll. This is a synthesis of documented workflows, not a measured target-company problem. | [EVD-46](../02-research/secondary-research.md), [EVD-49](../02-research/secondary-research.md), [EVD-51](../02-research/secondary-research.md) | Medium | Bonus |
| PP-15 | Spreadsheet-based bonus inputs can contain formula errors, duplicate employees or omissions. | The wrong amount or employee can reach payroll. The evidence establishes the risk, not its frequency. | [EVD-50](../02-research/secondary-research.md) | High | Bonus |
| PP-16 | A pending bonus or salary approval can block further bonus actions in the documented workflow. | Processing cannot continue until the pending approval is resolved. No typical delay is established. | [EVD-52](../02-research/secondary-research.md) | High | Bonus |

### Settlement records and policy dependencies

| ID | Pain point | What happens because of it (impact) | Evidence IDs | Confidence | Related flow |
|---|---|---|---|---|---|
| PP-17 | A settlement combines open salary, expense, bonus, loan and other amounts from several records. | HR must reconcile the items to establish the final amount. This is an interpretation of documented dependencies, not measured effort. | [EVD-57](../02-research/secondary-research.md), [EVD-61](../02-research/secondary-research.md), [EVD-66](../02-research/secondary-research.md) | Medium | Settlement |
| PP-18 | Unfinished exit sections and payroll prerequisites can prevent settlement finalization in the documented product workflow. | Monetary closure depends on completing other tasks. This does not establish that any wage component can legally be held. | [EVD-58](../02-research/secondary-research.md), [EVD-65](../02-research/secondary-research.md) | High | Settlement |
| PP-19 | Leave balance, encashment policy, rounding and overrides can produce different settlement results. | HR must establish the applicable basis before relying on the amount. Actual error incidence is unknown. | [EVD-62](../02-research/secondary-research.md), [EVD-63](../02-research/secondary-research.md) | Medium | Settlement |
| PP-20 | Notice recovery depends on employment terms. The research does not establish a universal recovery formula. | A generic basis may not explain the amount in a particular settlement. | [EVD-64](../02-research/secondary-research.md) | Medium | Settlement |

## 3. Employee pain points

### Understanding pay and deductions

| ID | Pain point | What happens because of it (impact) | Evidence IDs | Confidence | Related flow |
|---|---|---|---|---|---|
| PP-07 | An unexpected take-home change can leave its cause unclear. | The employee has to investigate why the amount changed. | [EVD-15](../02-research/secondary-research.md) | Medium | Salary explanation |
| PP-08 | Employee PF, employer PF and the PF wage can be confused with one another or with total salary. | An employee can misunderstand a deduction or the effect of a hike. | [EVD-09](../02-research/secondary-research.md), [EVD-27](../02-research/secondary-research.md) | Medium | Salary explanation |
| PP-09 | Being told that a deduction is TDS may leave its reason unclear. | An employee can continue seeking an explanation after contacting HR. | [EVD-10](../02-research/secondary-research.md) | Medium | TDS explanation |
| PP-10 | Gross arrears can be mistaken for the amount the employee will receive. | PF and tax deductions can make the received amount lower than expected. | [EVD-13](../02-research/secondary-research.md) | Medium | Salary explanation |

### Conflicting records and unresolved questions

| ID | Pain point | What happens because of it (impact) | Evidence IDs | Confidence | Related flow |
|---|---|---|---|---|---|
| PP-11 | Payslips, payroll records and bank credits can disagree. | An employee can struggle to identify the correct amount and compare several records. | [EVD-17](../02-research/secondary-research.md), [EVD-18](../02-research/secondary-research.md) | Medium | Salary explanation, Query |
| PP-12 | A later payroll correction may leave an earlier payslip inconsistent. | One reported employee worried that the record could affect background verification. This is a case-specific concern. | [EVD-18](../02-research/secondary-research.md) | Medium | Salary explanation, Query |
| PP-13 | An unclear payroll explanation can leave the original question unresolved. | Employees in the reviewed complaints asked HR and sought help in public communities. The evidence does not establish a typical response time. | [EVD-10](../02-research/secondary-research.md), [EVD-16](../02-research/secondary-research.md) | Medium | Salary explanation, TDS explanation, Query |

### Settlement statements

| ID | Pain point | What happens because of it (impact) | Evidence IDs | Confidence | Related flow |
|---|---|---|---|---|---|
| PP-21 | An employee can receive a settlement recovery figure without understanding how it was calculated. | The basis of the recovery is unclear, making it difficult to understand or challenge. This is one reported case, not a prevalence finding. | [EVD-68](../02-research/secondary-research.md), [EVD-69](../02-research/secondary-research.md) provides component context only | Medium | Settlement, Query |

## 4. Pain points with weak evidence
- **Low:** Bonus and settlement now have documented workflow evidence. Direct HR effort measurements, specific incentive-policy problems and pain severity remain unvalidated. EG-10 is partly addressed and retained. The new points distinguish documented risks from interpretations of dependencies. ([EVD-46–EVD-52](../02-research/secondary-research.md), [EVD-57–EVD-66](../02-research/secondary-research.md); EG-01, EG-10, EG-20–EG-22, EG-26)
- **Low:** The settlement statement finding is one complaint. It does not establish the most disputed item, typical delay or a distinct exiting-employee behavior group. ([EVD-68](../02-research/secondary-research.md); EG-26, EG-27)
- **Low:** The salary-restructure complaint is a single reported case. It is not used to establish a general cause or legal explanation for lower take-home pay. ([EVD-12](../02-research/secondary-research.md))
- **Low:** The wage dispute and resignation reports show serious cases. They do not establish a typical outcome for either persona. ([EVD-19](../02-research/secondary-research.md), [EVD-20](../02-research/secondary-research.md))
- **Low:** Actual effort, prevalence and severity rankings remain unknown. The existing assumption that input reconstruction takes more effort than arithmetic is still unvalidated. (Research: EG-01–EG-04; existing AS-6)

There are now 13 HR Admin pain points and eight Employee pain points. PP-01 through PP-13 are unchanged. The update adds PP-14 through PP-20 for HR and PP-21 for the Employee. Bonus and settlement remain in scope. GAP-01 through GAP-08 remain the main brief gap records. EG-11 through EG-18 are cross-references only. Proposed GAP-09 remains with Agent 04 and Agent 05; this analysis does not resolve it. (Brief: Sections 4, 5 and 9; DEC-002, DEC-004)
