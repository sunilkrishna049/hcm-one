import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { NumberCard } from '../design-system/components/NumberCard';
import { CertaintyLabel } from '../design-system/components/CertaintyLabel';
import { MessageBubble } from '../design-system/components/MessageBubble';
import { SourceLink, formatHumanSourceLabel } from '../design-system/components/SourceLink';
import { ApprovalBar } from '../design-system/components/ApprovalBar';
import { Drawer } from '../design-system/components/Drawer';
import { CalculationBreakdown } from '../design-system/components/CalculationBreakdown';
import { Button } from '../design-system/components/Button';
import { getAIMessage } from '../design-system/ai_messages';
import * as Dialog from '@radix-ui/react-dialog';
import { Check, Edit3, Eye, AlertTriangle } from 'lucide-react';

interface ReviewProposalProps {
  scenarioNum?: number;
  mode?: 'hike' | 'bonus' | 'settlement';
  employeeId?: string;
  currentUser?: string;
  onRefresh?: () => void;
}

export const ReviewProposal: React.FC<ReviewProposalProps> = ({
  scenarioNum = 1,
  mode = 'hike',
  employeeId = 'E01',
  currentUser: _currentUser,
  onRefresh: _onRefresh,
}) => {
  const [loading, setLoading] = useState(true);
  const [scenarioData, setScenarioData] = useState<any>(null);
  const [runtimeProposal, setRuntimeProposal] = useState<any>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Drawer & Edit dialog states
  const [proofOpen, setProofOpen] = useState(false);
  const [selectedProofData, setSelectedProofData] = useState<any>(null);
  const [editOpen, setEditOpen] = useState(false);
  const [editLine, setEditLine] = useState("hike_percentage");
  const [editValue, setEditValue] = useState<string>("");
  const [editReason, setEditReason] = useState("");
  const [submittingEdit, setSubmittingEdit] = useState(false);
  const [staleVersionToTest, setStaleVersionToTest] = useState<number | null>(null);

  // Bonus mode multi-employee scope state
  const [selectedScopeBonus, setSelectedScopeBonus] = useState<string[]>([]);
  const [scopeCalculation, setScopeCalculation] = useState<any>(null);

  // Statutory PF wage ceiling comparison for Scenario 2
  const [selectedOption, setSelectedOption] = useState<'standard' | 'uncapped'>('standard');

  const loadData = async () => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const scenarioId = `scenario-${String(scenarioNum).padStart(2, '0')}`;
      const res = await api.getScenario(scenarioId);
      setScenarioData(res.scenario);
      setRuntimeProposal(res.runtime_proposal);

      // Prepopulate edit value dynamically from proposed hike or salary
      if (res.scenario?.display_inputs?.requested_hike_percentage?.value) {
        setEditValue(String(res.scenario.display_inputs.requested_hike_percentage.value));
      }

      // If bonus mode, initialize selected employees
      if (res.meta?.mode === 'bonus' || mode === 'bonus') {
        const bonusEmployees = res.scenario?.result?.bonus_requests?.[0]?.employees || [];
        const eligibleIds = bonusEmployees
          .filter((e: any) => e.eligibility === 'Eligible')
          .map((e: any) => e.employee_id);
        setSelectedScopeBonus(eligibleIds);

        if (eligibleIds.length > 0) {
          const bonusRes = await api.calculateBonusScope('annual', '2026-09', eligibleIds);
          setScopeCalculation(bonusRes);
        }
      }
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to load scenario data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [scenarioNum, mode, employeeId]);

  // Handle bonus checkbox toggle
  const handleToggleBonusEmployee = async (eid: string) => {
    const nextScope = selectedScopeBonus.includes(eid)
      ? selectedScopeBonus.filter(id => id !== eid)
      : [...selectedScopeBonus, eid];
    setSelectedScopeBonus(nextScope);

    try {
      const bonusRes = await api.calculateBonusScope('annual', '2026-09', nextScope);
      setScopeCalculation(bonusRes);
    } catch (e: any) {
      console.error(e);
    }
  };

  // Handle Edit submission
  const handleSaveEdit = async () => {
    if (!runtimeProposal?.proposal_id) return;
    setSubmittingEdit(true);
    try {
      const res = await api.editProposal(
        runtimeProposal.proposal_id,
        editLine,
        editValue,
        editReason || "HR revision request"
      );
      setRuntimeProposal(res.proposal);
      setEditOpen(false);
      setEditReason("");
      loadData();
    } catch (e: any) {
      alert("Edit error: " + e.message);
    } finally {
      setSubmittingEdit(false);
    }
  };

  // Handle Approval
  const handleApprove = async () => {
    if (!runtimeProposal?.proposal_id) return;
    try {
      const versionToApprove = staleVersionToTest !== null ? staleVersionToTest : runtimeProposal.version;
      const res = await api.approveProposal(runtimeProposal.proposal_id, versionToApprove, {
        selected_scope: mode === 'bonus' ? selectedScopeBonus : [employeeId],
      });
      setRuntimeProposal(res.proposal);
      setStaleVersionToTest(null);
    } catch (e: any) {
      alert("Approval error: " + e.message);
    }
  };

  // Handle Rejection
  const handleReject = async (reason?: string) => {
    if (!runtimeProposal?.proposal_id) return;
    try {
      const res = await api.rejectProposal(runtimeProposal.proposal_id, reason);
      setRuntimeProposal(res.proposal);
    } catch (e: any) {
      alert("Rejection error: " + e.message);
    }
  };

  if (loading) {
    return (
      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: 'var(--space-8)', textAlign: 'center' }}>
        Loading proposal calculation from engine...
      </div>
    );
  }

  if (errorMsg) {
    return (
      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: 'var(--space-6)' }}>
        <div style={{ backgroundColor: 'var(--color-status-error-surface)', padding: 'var(--space-4)', borderRadius: 'var(--radius-card)', color: 'var(--color-status-error-text)' }}>
          {errorMsg}
        </div>
      </div>
    );
  }

  const result = scenarioData?.result || {};
  const currentCertainty = runtimeProposal?.certainty || result?.certainty || "Complete for this scope";
  const proposalStatus = runtimeProposal?.status || result?.proposal_status || "Needs HR approval; not applied";
  const isApproved = proposalStatus === "Approved and ready for payroll";
  const isComplete = currentCertainty === "Complete for this scope" || currentCertainty === "Complete";

  const isScenario2 = scenarioNum === 2;
  const pfComparison = result?.pf_ceiling_comparison;

  // Open Proof helper
  const openProof = (title: string, calculationObj: any) => {
    if (!calculationObj) return;
    setSelectedProofData({
      title,
      formula: calculationObj.formula,
      inputs: calculationObj.inputs,
      rule_ids: calculationObj.rule_ids,
      certainty: calculationObj.certainty,
      flags: calculationObj.flags,
      value: calculationObj.value,
    });
    setProofOpen(true);
  };

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
      {/* Top Meta Bar */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        borderBottom: '1px solid var(--color-divider)',
        paddingBottom: 'var(--space-4)'
      }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
            <h1 style={{ fontSize: '26px', fontWeight: 700, margin: 0, color: 'var(--color-text-primary)', letterSpacing: '-0.02em' }}>
              Review proposal
            </h1>
            <span style={{
              fontFamily: 'var(--font-mono)',
              fontSize: 'var(--font-size-small)',
              backgroundColor: 'var(--color-surface)',
              padding: '2px 8px',
              borderRadius: 'var(--radius-input)',
              border: '1px solid var(--color-divider)'
            }}>
              {runtimeProposal?.proposal_id || `PROP-${scenarioNum}`} (v{runtimeProposal?.version || 1})
            </span>
            <CertaintyLabel certainty={currentCertainty} />
          </div>
          <div style={{ color: 'var(--color-text-secondary)', marginTop: 'var(--space-1)', fontSize: 'var(--font-size-small)' }}>
            Status: <strong>{proposalStatus}</strong> &bull; Effective cycle: <strong>2026-10-13</strong>
          </div>
        </div>

        <div style={{ display: 'flex', gap: 'var(--space-2)' }}>
          <Button
            variant="outline"
            onClick={() => setEditOpen(true)}
            disabled={isApproved}
          >
            <Edit3 size={16} /> Edit with a reason
          </Button>

          {scenarioNum === 13 && (
            <Button
              variant="secondary"
              onClick={() => {
                setStaleVersionToTest(1);
                alert("Simulating stale submission: Next click on Approve will send v1 instead of latest v" + (runtimeProposal?.version || 1));
              }}
            >
              Simulate Stale v1 (C25 Guard)
            </Button>
          )}
        </div>
      </div>

      {/* Assistant Intro Message (Sentence C03 Verbatim) */}
      <MessageBubble
        author="HCM One Assistant"
        text={getAIMessage('C03')}
      />

      {/* Warning Banner if unverified / incomplete */}
      {!isComplete && (
        <div style={{
          backgroundColor: 'var(--color-status-warning-surface)',
          border: '1px solid var(--color-status-warning-border)',
          borderRadius: 'var(--radius-card)',
          padding: 'var(--space-4)',
          display: 'flex',
          gap: 'var(--space-3)',
          alignItems: 'flex-start'
        }}>
          <AlertTriangle color="var(--color-status-warning-text)" size={20} />
          <div>
            <strong style={{ color: 'var(--color-status-warning-text)' }}>Proposal Scope Incomplete:</strong>
            <p style={{ margin: '4px 0 0 0', fontSize: 'var(--font-size-small)', color: 'var(--color-status-warning-text)' }}>
              {scenarioNum === 3
                ? getAIMessage('C07', { record_type: "attendance record", period_or_component: "July 2026" })
                : scenarioNum === 5
                ? getAIMessage('C07', { record_type: "performance rating", period_or_component: "FY 2025-26" })
                : (scenarioNum === 8 || scenarioNum === 13)
                ? "Asset clearance pending IT sign-off. Final settlement net pay cannot be calculated until all clearances are verified."
                : "Certain components require verification before payroll approval."}
            </p>
          </div>
        </div>
      )}

      {/* Scenario 2 Special: Statutory PF Wage Ceiling Comparison */}
      {isScenario2 && pfComparison && (
        <div style={{
          backgroundColor: 'var(--color-surface)',
          border: '1px solid var(--color-divider)',
          borderRadius: 'var(--radius-card)',
          padding: 'var(--space-4)',
          display: 'flex',
          flexDirection: 'column',
          gap: 'var(--space-3)'
        }}>
          <div style={{ fontWeight: 'var(--font-weight-semibold)' }}>
            Statutory Rule Comparison: PF Wage Ceiling (Effective 2026-09-17)
          </div>
          <p style={{ fontSize: 'var(--font-size-small)', color: 'var(--color-text-secondary)', margin: 0 }}>
            Compare statutory ceiling cap against uncapped actual basic from engine.
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-4)', marginTop: 'var(--space-2)' }}>
            <div
              onClick={() => setSelectedOption('standard')}
              style={{
                padding: 'var(--space-4)',
                border: `2px solid ${selectedOption === 'standard' ? 'var(--color-brand-accent)' : 'var(--color-divider)'}`,
                borderRadius: 'var(--radius-card)',
                backgroundColor: 'var(--color-background)',
                cursor: 'pointer'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <strong>Option A: Statutory Cap (Standard)</strong>
                {selectedOption === 'standard' && <Check size={18} color="var(--color-brand-accent)" />}
              </div>
              <div style={{ marginTop: 'var(--space-2)', fontSize: '20px', fontWeight: 'bold' }}>
                Net Arrears: {pfComparison.capped?.net_arrears !== undefined ? `INR ${pfComparison.capped.net_arrears.toLocaleString('en-IN')}` : 'Not available'}
              </div>
              <div style={{ fontSize: 'var(--font-size-small)', color: 'var(--color-text-secondary)', marginTop: '4px' }}>
                PF contribution calculated up to statutory wage ceiling. Source: <SourceLink source="Statutory EPFO rules" />
              </div>
            </div>

            <div
              onClick={() => setSelectedOption('uncapped')}
              style={{
                padding: 'var(--space-4)',
                border: `2px solid ${selectedOption === 'uncapped' ? 'var(--color-brand-accent)' : 'var(--color-divider)'}`,
                borderRadius: 'var(--radius-card)',
                backgroundColor: 'var(--color-background)',
                cursor: 'pointer'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <strong>Option B: Actual Basic (Uncapped)</strong>
                {selectedOption === 'uncapped' && <Check size={18} color="var(--color-brand-accent)" />}
              </div>
              <div style={{ marginTop: 'var(--space-2)', fontSize: '20px', fontWeight: 'bold' }}>
                Net Arrears: {pfComparison.uncapped?.net_arrears !== undefined ? `INR ${pfComparison.uncapped.net_arrears.toLocaleString('en-IN')}` : 'Not available'}
              </div>
              <div style={{ fontSize: 'var(--font-size-small)', color: 'var(--color-text-secondary)', marginTop: '4px' }}>
                Higher PF deduction on entire basic. Reduces net take-home arrears.
              </div>
            </div>
          </div>
        </div>
      )}

      {/* --- HERO & SOURCED NUMBER CARDS (Strictly matching screen-specs.md) --- */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 'var(--space-4)' }}>
        {mode === 'hike' && (
          <>
            {/* Hero: Expected net arrears */}
            <NumberCard
              label="Expected net arrears"
              amount={result?.totals?.net_arrears?.value !== undefined ? result.totals.net_arrears.value : null}
              variant="hero-desktop"
              certainty={result?.totals?.net_arrears?.certainty || currentCertainty}
              source={formatHumanSourceLabel("engine/payroll/flows.py#hike", "REV-E01")}
              onViewProof={() => openProof("Expected Net Arrears Proof", result?.totals?.net_arrears)}
            />

            {/* Card 1: Gross arrears */}
            <NumberCard
              label="Gross arrears"
              amount={result?.totals?.gross_arrears?.value !== undefined ? result.totals.gross_arrears.value : null}
              source={formatHumanSourceLabel("engine/payroll/flows.py#gross_arrears", "REV-E01")}
              certainty={result?.totals?.gross_arrears?.certainty}
              onViewProof={() => openProof("Gross Arrears Proof", result?.totals?.gross_arrears)}
            />

            {/* Card 2: Employee PF change */}
            <NumberCard
              label="Employee PF change"
              amount={result?.totals?.pf_change?.employee?.value !== undefined ? result.totals.pf_change.employee.value : 0}
              source={formatHumanSourceLabel("Statutory EPFO rules")}
              certainty={result?.totals?.pf_change?.employee?.certainty}
              onViewProof={() => openProof("Employee PF Change Proof", result?.totals?.pf_change?.employee)}
            />

            {/* Card 3: Estimated TDS impact */}
            <NumberCard
              label="Estimated TDS impact"
              amount={result?.totals?.tds_impact?.value !== undefined ? result.totals.tds_impact.value : 0}
              source={formatHumanSourceLabel("Income tax rules")}
              certainty={result?.totals?.tds_impact?.certainty}
              onViewProof={() => openProof("Estimated TDS Impact Proof", result?.totals?.tds_impact)}
            />
          </>
        )}

        {mode === 'bonus' && (
          <>
            {/* Hero: Group net */}
            <NumberCard
              label="Group net"
              amount={scopeCalculation?.group_total_net !== undefined ? scopeCalculation.group_total_net : (result?.aggregates?.group_net?.value ?? null)}
              variant="hero-desktop"
              certainty={scopeCalculation?.certainty || currentCertainty}
              source="Company bonus policy"
              onViewProof={() => openProof("Bonus Group Net Proof", result?.aggregates?.group_net)}
            />

            {/* Card 1: Group gross */}
            <NumberCard
              label="Group gross"
              amount={scopeCalculation?.group_total_gross !== undefined ? scopeCalculation.group_total_gross : (result?.aggregates?.group_gross?.value ?? null)}
              source="Company bonus policy"
              onViewProof={() => openProof("Bonus Group Gross Proof", result?.aggregates?.group_gross)}
            />

            {/* Card 2: Eligible count */}
            <NumberCard
              label="Eligible employees"
              amount={result?.aggregates?.eligible_count?.value !== undefined ? result.aggregates.eligible_count.value : selectedScopeBonus.length}
              currency=""
              source="HR eligibility scope"
            />

            {/* Card 3: Not eligible count */}
            <NumberCard
              label="Not eligible"
              amount={result?.aggregates?.not_eligible_count?.value !== undefined ? result.aggregates.not_eligible_count.value : 0}
              currency=""
              source="HR eligibility scope"
            />
          </>
        )}

        {mode === 'settlement' && (
          <>
            {/* Hero: Final net */}
            <NumberCard
              label="Final net"
              amount={result?.final_net?.value !== undefined ? result.final_net.value : null}
              variant="hero-desktop"
              certainty={result?.final_net?.certainty || currentCertainty}
              source="Full and final settlement"
              onViewProof={() => openProof("Final Settlement Net Proof", result?.final_net)}
            />

            {/* Card 1: Gross payables */}
            <NumberCard
              label="Gross payables"
              amount={result?.gross_payables?.value !== undefined ? result.gross_payables.value : null}
              source="Settlement payables"
              onViewProof={() => openProof("Gross Payables Proof", result?.gross_payables)}
            />

            {/* Card 2: Total deductions */}
            <NumberCard
              label="Total deductions"
              amount={result?.total_deductions?.value !== undefined ? result.total_deductions.value : null}
              source="Settlement deductions"
              onViewProof={() => openProof("Total Deductions Proof", result?.total_deductions)}
            />

            {/* Card 3: Known recoveries subtotal */}
            <NumberCard
              label="Known recoveries subtotal"
              amount={result?.known_recoveries_subtotal?.value !== undefined ? result.known_recoveries_subtotal.value : null}
              source="Settlement recoveries"
              onViewProof={() => openProof("Known Recoveries Subtotal Proof", result?.known_recoveries_subtotal)}
            />
          </>
        )}
      </div>

      {/* --- LINE ITEMS TABLES POPULATED DIRECTLY FROM API RESULT --- */}

      {/* Hike Mode: Monthly Arrears Table */}
      {mode === 'hike' && (
        <div className="hcm-table-container">
          <div style={{ padding: 'var(--space-4)', borderBottom: '1px solid var(--color-divider)', fontWeight: 'var(--font-weight-semibold)' }}>
            Monthly Arrears Breakdown
          </div>
          <table className="hcm-table">
            <thead>
              <tr>
                <th>Period</th>
                <th className="hcm-table-num">Old earned amount</th>
                <th className="hcm-table-num">Revised earned amount</th>
                <th className="hcm-table-num">Arrears</th>
                <th className="hcm-table-num">Employee PF change</th>
                <th className="hcm-table-num">Incremental estimated arrears TDS</th>
                <th>Show calculation</th>
              </tr>
            </thead>
            <tbody>
              {(result?.months || []).map((m: any, idx: number) => {
                const isJulyMissing = scenarioNum === 3 && m.month === '2026-07';
                const oldGross = m.old?.gross?.value;
                const revGross = m.revised?.gross?.value;
                const grossDiff = m.difference?.value ?? m.gross_diff?.value;
                const pfChange = m.pf_change?.employee?.value;
                const tdsImpact = m.tds?.incremental_estimated_arrears_tds?.value ?? m.tds?.value;

                return (
                  <tr key={idx}>
                    <td><strong>{m.month}</strong></td>
                    <td className="hcm-table-num">
                      {isJulyMissing ? "Not available in generated data" : (oldGross !== undefined ? `INR ${oldGross.toLocaleString('en-IN')}` : "-")}
                    </td>
                    <td className="hcm-table-num">
                      {isJulyMissing ? "Not available in generated data" : (revGross !== undefined ? `INR ${revGross.toLocaleString('en-IN')}` : "-")}
                    </td>
                    <td className="hcm-table-num">
                      {isJulyMissing ? (
                        <span style={{ color: 'var(--color-status-warning-text)' }}>Not available in generated data</span>
                      ) : (
                        <strong>{grossDiff !== undefined ? `INR ${grossDiff.toLocaleString('en-IN')}` : "-"}</strong>
                      )}
                    </td>
                    <td className="hcm-table-num">
                      {isJulyMissing ? "Not available in generated data" : (pfChange !== undefined ? `INR ${pfChange.toLocaleString('en-IN')}` : "0")}
                    </td>
                    <td className="hcm-table-num">
                      {isJulyMissing ? "Not available in generated data" : (tdsImpact !== undefined ? `INR ${tdsImpact.toLocaleString('en-IN')}` : "0")}
                    </td>
                    <td>
                      <button
                        type="button"
                        className="hcm-source-link"
                        onClick={() => openProof(`${m.month} Arrears Calculation`, m.difference || m.gross_diff || m.revised?.gross)}
                      >
                        <Eye size={12} /> View proof
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Bonus Mode: Employee Scope Table */}
      {mode === 'bonus' && (
        <div className="hcm-table-container">
          <div style={{ padding: 'var(--space-4)', borderBottom: '1px solid var(--color-divider)', fontWeight: 'var(--font-weight-semibold)' }}>
            Bonus Run Employee Scope
          </div>
          <table className="hcm-table">
            <thead>
              <tr>
                <th style={{ width: '40px' }}>Select</th>
                <th>Employee</th>
                <th>Eligibility</th>
                <th>Reason</th>
                <th className="hcm-table-num">Gross Bonus</th>
                <th className="hcm-table-num">TDS</th>
                <th className="hcm-table-num">Net Bonus</th>
                <th>Status</th>
                <th>Calculation Proof</th>
              </tr>
            </thead>
            <tbody>
              {(result?.bonus_requests?.[0]?.employees || []).map((emp: any) => {
                const isSelected = selectedScopeBonus.includes(emp.employee_id);
                const grossBonus = emp.bonus_amount?.value;
                const tds = emp.tds?.value;
                const netBonus = emp.net_bonus?.value;

                return (
                  <tr key={emp.employee_id}>
                    <td>
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={() => handleToggleBonusEmployee(emp.employee_id)}
                        disabled={emp.eligibility !== 'Eligible'}
                      />
                    </td>
                    <td><strong>{emp.employee_id}</strong></td>
                    <td>{emp.eligibility}</td>
                    <td style={{ fontSize: '12px', color: 'var(--color-text-secondary)' }}>{emp.reason}</td>
                    <td className="hcm-table-num">
                      {grossBonus !== undefined && grossBonus !== null ? `INR ${grossBonus.toLocaleString('en-IN')}` : "Not available in generated data"}
                    </td>
                    <td className="hcm-table-num">
                      {tds !== undefined && tds !== null ? `INR ${tds.toLocaleString('en-IN')}` : "-"}
                    </td>
                    <td className="hcm-table-num">
                      {netBonus !== undefined && netBonus !== null ? (
                        <strong>INR {netBonus.toLocaleString('en-IN')}</strong>
                      ) : (
                        <span style={{ color: 'var(--color-status-warning-text)' }}>Not available in generated data</span>
                      )}
                    </td>
                    <td>
                      <CertaintyLabel certainty={emp.certainty || (emp.eligibility === 'Eligible' ? 'Complete for this scope' : 'Incomplete')} />
                    </td>
                    <td>
                      <button
                        type="button"
                        className="hcm-source-link"
                        onClick={() => openProof(`${emp.employee_id} Bonus Proof`, emp.bonus_amount)}
                      >
                        <Eye size={12} /> View proof
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Settlement Mode: Components Table */}
      {mode === 'settlement' && (
        <div className="hcm-table-container">
          <div style={{ padding: 'var(--space-4)', borderBottom: '1px solid var(--color-divider)', fontWeight: 'var(--font-weight-semibold)' }}>
            Full & Final Settlement Components
          </div>
          <table className="hcm-table">
            <thead>
              <tr>
                <th>Component</th>
                <th>Classification</th>
                <th className="hcm-table-num">Amount</th>
                <th>Applicable due date</th>
                <th>Status</th>
                <th>Show calculation</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(result?.components || {}).map(([key, comp]: [string, any]) => {
                const amountVal = comp?.amount?.value;
                const isUnresolved = comp?.certainty === 'Incomplete' || comp?.certainty === 'Unresolved' || amountVal === null;
                const rawDueDate = comp?.applicable_due_date;
                const dueDateStr = typeof rawDueDate === 'object' ? (rawDueDate?.value || 'Not applicable') : (rawDueDate || 'Not applicable');

                return (
                  <tr key={key}>
                    <td><strong>{key.replace(/_/g, ' ').toUpperCase()}</strong></td>
                    <td>{comp?.classification || '-'}</td>
                    <td className="hcm-table-num">
                      {isUnresolved ? (
                        <span style={{ color: 'var(--color-status-warning-text)' }}>Not available in generated data</span>
                      ) : (
                        <strong>{amountVal !== undefined ? `INR ${amountVal.toLocaleString('en-IN')}` : '-'}</strong>
                      )}
                    </td>
                    <td>{dueDateStr}</td>
                    <td>
                      <CertaintyLabel certainty={comp?.certainty || 'Complete for this scope'} />
                    </td>
                    <td>
                      <button
                        type="button"
                        className="hcm-source-link"
                        onClick={() => openProof(`${key} Proof`, comp?.amount || comp)}
                      >
                        <Eye size={12} /> View proof
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Calculation Proof Drawer */}
      <Drawer
        isOpen={proofOpen}
        onClose={() => setProofOpen(false)}
        title={selectedProofData?.title || "Calculation Proof"}
      >
        {selectedProofData && (
          <CalculationBreakdown
            title={selectedProofData.title}
            formula={selectedProofData.formula}
            inputs={selectedProofData.inputs}
            ruleIds={selectedProofData.rule_ids}
            certainty={selectedProofData.certainty}
            value={selectedProofData.value}
          />
        )}
      </Drawer>

      {/* Edit Proposal Dialog */}
      <Dialog.Root open={editOpen} onOpenChange={setEditOpen}>
        <Dialog.Portal>
          <Dialog.Overlay className="hcm-dialog-overlay" />
          <Dialog.Content className="hcm-dialog-content">
            <Dialog.Title style={{ fontSize: 'var(--font-size-subtitle)', fontWeight: 'var(--font-weight-semibold)', marginBottom: 'var(--space-2)' }}>
              Edit proposal parameters
            </Dialog.Title>
            <Dialog.Description style={{ fontSize: 'var(--font-size-small)', color: 'var(--color-text-secondary)', marginBottom: 'var(--space-4)' }}>
              {getAIMessage('C05')}
            </Dialog.Description>

            <div className="hcm-form-group">
              <label className="hcm-form-label" htmlFor="edit-line">Parameter to revise</label>
              <select
                id="edit-line"
                className="hcm-select"
                value={editLine}
                onChange={(e) => setEditLine(e.target.value)}
              >
                <option value="hike_percentage">Hike percentage (%)</option>
                <option value="effective_date">Effective date</option>
                <option value="gross_arrears">Gross arrears</option>
              </select>
            </div>

            <div className="hcm-form-group">
              <label className="hcm-form-label" htmlFor="edit-val">New proposed value</label>
              <input
                id="edit-val"
                className="hcm-input"
                value={editValue}
                onChange={(e) => setEditValue(e.target.value)}
                placeholder="Enter revised parameter"
              />
            </div>

            <div className="hcm-form-group">
              <label className="hcm-form-label" htmlFor="edit-reason">Reason</label>
              <input
                id="edit-reason"
                className="hcm-input"
                value={editReason}
                onChange={(e) => setEditReason(e.target.value)}
                placeholder="e.g. Revised promotion committee recommendation"
              />
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 'var(--space-3)', marginTop: 'var(--space-6)' }}>
              <Button variant="secondary" onClick={() => setEditOpen(false)}>
                Cancel
              </Button>
              <Button variant="primary" onClick={handleSaveEdit} disabled={submittingEdit}>
                {submittingEdit ? "Recalculating..." : "Apply revision & recalculate"}
              </Button>
            </div>
          </Dialog.Content>
        </Dialog.Portal>
      </Dialog.Root>

      {/* Approval Bar at Bottom with Sentence C04 */}
      <ApprovalBar
        version={runtimeProposal?.version || 1}
        isApproved={isApproved}
        isComplete={isComplete}
        onApprove={handleApprove}
        onReject={handleReject}
        proposalId={runtimeProposal?.proposal_id}
      />
    </div>
  );
};
