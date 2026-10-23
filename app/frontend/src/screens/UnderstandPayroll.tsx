import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { NumberCard } from '../design-system/components/NumberCard';
import { MessageBubble } from '../design-system/components/MessageBubble';
import { CertaintyLabel } from '../design-system/components/CertaintyLabel';
import { Sheet } from '../design-system/components/Sheet';
import { CalculationBreakdown } from '../design-system/components/CalculationBreakdown';
import { Button } from '../design-system/components/Button';
import { getAIMessage } from '../design-system/ai_messages';
import { ChevronRight, ShieldAlert, Eye, MessageSquare } from 'lucide-react';

interface UnderstandPayrollProps {
  currentUser: string;
  scenarioNum?: number;
  onNavigateToDraftQuery: (draftData: any) => void;
  onNavigateToTrackQuery?: () => void;
}

export const UnderstandPayroll: React.FC<UnderstandPayrollProps> = ({
  currentUser,
  scenarioNum = 9,
  onNavigateToDraftQuery,
  onNavigateToTrackQuery,
}) => {
  const [activeQuestion, setActiveQuestion] = useState<number>(scenarioNum);
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [proofOpen, setProofOpen] = useState(false);
  const [selectedProofData, setSelectedProofData] = useState<any>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Sync active question with scenarioNum prop
  useEffect(() => {
    setActiveQuestion(scenarioNum);
  }, [scenarioNum]);

  const loadDataForQuestion = async (qNum: number) => {
    setLoading(true);
    setErrorMsg(null);
    try {
      let backendScenarioId = "scenario-09";
      if (qNum === 9 || qNum === 7) backendScenarioId = "scenario-09"; // Neha LOP
      else if (qNum === 10) backendScenarioId = "scenario-10"; // Siddharth TDS
      else if (qNum === 11 || qNum === 8) backendScenarioId = "scenario-11"; // Pooja PF ceiling change
      else if (qNum === 12) backendScenarioId = "scenario-12"; // Permission denied

      const res = await api.getScenario(backendScenarioId);
      setData(res.scenario || res);
    } catch (err: any) {
      if (err.message && err.message.includes("Permission denied")) {
        setData({
          status: "Permission denied",
          message: getAIMessage('C10'),
          certainty: "Permission denied",
          result: { status: "Permission denied" }
        });
      } else {
        setErrorMsg(err.message || "Failed to load payroll explanation");
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDataForQuestion(activeQuestion);
  }, [activeQuestion, currentUser]);

  const result = data?.result || {};
  const isPermissionDenied = activeQuestion === 12 || result?.status === "Permission denied" || data?.status === "Permission denied";

  const handleStartQueryDraft = () => {
    const empId = currentUser.replace('USER-', '');
    let draftData: any = {
      employee_id: empId,
      employee_name: empId === 'E05' ? 'Neha Gupta' : empId === 'E06' ? 'Siddharth Jain' : empId === 'E16' ? 'Pooja Das' : empId,
      pay_period: '2026-09',
      topic: 'salary',
      description: 'Please check my September attendance.',
      evidence: [
        { type: 'attendance record', record_id: `ATT-${empId}-2026-09`, file: 'attendance.json' },
      ],
      candidate_query_id: 'QUERY-E05-SEPTEMBER',
      candidate_query_text: 'Please check my September attendance.',
    };

    if (activeQuestion === 10) {
      draftData.topic = 'tax';
      draftData.description = 'Please check my previous-employer TDS declaration.';
      draftData.evidence = [
        { type: 'tax declaration', record_id: 'DECL-E06-PREVIOUS-EMPLOYER', file: 'declarations.json' },
      ];
      draftData.candidate_query_id = null;
    }

    onNavigateToDraftQuery(draftData);
  };

  const openProof = (title: string, calcObj: any) => {
    if (!calcObj) return;
    setSelectedProofData({
      title,
      formula: calcObj.formula,
      inputs: calcObj.inputs,
      rule_ids: calcObj.rule_ids,
      certainty: calcObj.certainty,
      value: calcObj.value,
      flags: calcObj.flags,
    });
    setProofOpen(true);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)', padding: 'var(--space-4)' }}>
      {/* Screen Title */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontSize: '20px', fontWeight: 700, margin: 0, color: 'var(--color-text-primary)' }}>
            Understand my payroll
          </h2>
          <div style={{ fontSize: '13px', color: 'var(--color-text-secondary)', marginTop: '2px' }}>
            Logged in: <strong>{currentUser}</strong>
          </div>
        </div>
        {onNavigateToTrackQuery && (
          <Button variant="ghost" size="sm" onClick={onNavigateToTrackQuery}>
            Track my query <ChevronRight size={14} />
          </Button>
        )}
      </div>

      {errorMsg && (
        <div style={{ color: 'var(--color-status-danger-text)', padding: 'var(--space-2)' }}>
          {errorMsg}
        </div>
      )}

      {/* Demo Scenario Question Selector */}
      <div style={{
        backgroundColor: 'var(--color-surface)',
        padding: 'var(--space-3)',
        borderRadius: 'var(--radius-card)',
        border: '1px solid var(--color-divider)'
      }}>
        <div style={{ fontSize: '11px', fontWeight: 'bold', color: 'var(--color-text-secondary)', textTransform: 'uppercase', marginBottom: 'var(--space-2)' }}>
          Select Question (BRD Scenarios):
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
          <button
            type="button"
            onClick={() => setActiveQuestion(9)}
            style={{
              padding: 'var(--space-2) var(--space-3)',
              borderRadius: 'var(--radius-button)',
              border: `1px solid ${activeQuestion === 9 || activeQuestion === 7 ? 'var(--color-brand-accent)' : 'var(--color-divider)'}`,
              backgroundColor: activeQuestion === 9 || activeQuestion === 7 ? 'var(--color-brand-tint)' : 'var(--color-background)',
              color: activeQuestion === 9 || activeQuestion === 7 ? 'var(--color-brand-accent)' : 'var(--color-text-primary)',
              fontSize: '12px',
              textAlign: 'left',
              cursor: 'pointer',
              fontWeight: activeQuestion === 9 || activeQuestion === 7 ? 600 : 400
            }}
          >
            "Why did my September net pay drop?" (Neha Gupta E05 - LOP)
          </button>

          <button
            type="button"
            onClick={() => setActiveQuestion(10)}
            style={{
              padding: 'var(--space-2) var(--space-3)',
              borderRadius: 'var(--radius-button)',
              border: `1px solid ${activeQuestion === 10 ? 'var(--color-brand-accent)' : 'var(--color-divider)'}`,
              backgroundColor: activeQuestion === 10 ? 'var(--color-brand-tint)' : 'var(--color-background)',
              color: activeQuestion === 10 ? 'var(--color-brand-accent)' : 'var(--color-text-primary)',
              fontSize: '12px',
              textAlign: 'left',
              cursor: 'pointer',
              fontWeight: activeQuestion === 10 ? 600 : 400
            }}
          >
            "Why did my TDS increase in September?" (Siddharth Jain E06 - Prior Employer)
          </button>

          <button
            type="button"
            onClick={() => setActiveQuestion(11)}
            style={{
              padding: 'var(--space-2) var(--space-3)',
              borderRadius: 'var(--radius-button)',
              border: `1px solid ${activeQuestion === 11 || activeQuestion === 8 ? 'var(--color-brand-accent)' : 'var(--color-divider)'}`,
              backgroundColor: activeQuestion === 11 || activeQuestion === 8 ? 'var(--color-brand-tint)' : 'var(--color-background)',
              color: activeQuestion === 11 || activeQuestion === 8 ? 'var(--color-brand-accent)' : 'var(--color-text-primary)',
              fontSize: '12px',
              textAlign: 'left',
              cursor: 'pointer',
              fontWeight: activeQuestion === 11 || activeQuestion === 8 ? 600 : 400
            }}
          >
            "Why did my take-home pay drop when my gross pay didn't change?" (Pooja Das E16 - PF ceiling)
          </button>

          <button
            type="button"
            onClick={() => setActiveQuestion(12)}
            style={{
              padding: 'var(--space-2) var(--space-3)',
              borderRadius: 'var(--radius-button)',
              border: `1px solid ${activeQuestion === 12 ? 'var(--color-brand-accent)' : 'var(--color-divider)'}`,
              backgroundColor: activeQuestion === 12 ? 'var(--color-brand-tint)' : 'var(--color-background)',
              color: activeQuestion === 12 ? 'var(--color-brand-accent)' : 'var(--color-text-primary)',
              fontSize: '12px',
              textAlign: 'left',
              cursor: 'pointer',
              fontWeight: activeQuestion === 12 ? 600 : 400
            }}
          >
            "What is Priya Sharma's salary?" (Scenario 12 - Permission denied)
          </button>
        </div>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: 'var(--space-6)', color: 'var(--color-text-secondary)' }}>
          Analyzing payroll baseline...
        </div>
      ) : isPermissionDenied ? (
        /* Permission Denied View (Scenario 12): Sentence C10 verbatim, NO TARGET CONTEXT */
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
          <div style={{
            backgroundColor: 'var(--color-status-error-surface)',
            border: '1px solid var(--color-status-error-border)',
            borderRadius: 'var(--radius-card)',
            padding: 'var(--space-4)',
            display: 'flex',
            flexDirection: 'column',
            gap: 'var(--space-2)'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', color: 'var(--color-status-error-text)' }}>
              <ShieldAlert size={18} />
              <strong>Permission denied</strong>
            </div>
            <p style={{ margin: 0, fontSize: '14px', color: 'var(--color-status-error-text)', lineHeight: 1.5 }}>
              {getAIMessage('C10')}
            </p>
          </div>

          <MessageBubble
            author="HCM One Assistant"
            text={getAIMessage('C10')}
          />
        </div>
      ) : (
        /* Normal Explanation View */
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
          {/* Numbers Hero */}
          {activeQuestion === 10 ? (
            /* TDS Mode: Siddharth Jain */
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-3)' }}>
              <NumberCard
                label="September 2026 TDS Deducted"
                amount={result?.after?.deductions?.lines?.tds?.value !== undefined ? result.after.deductions.lines.tds.value : null}
                variant="hero-mobile"
                certainty={result?.certainty}
                onViewProof={() => openProof("September TDS Proof", result?.after?.deductions?.lines?.tds)}
              />
              <NumberCard
                label="TDS Change vs August"
                amount={result?.tds_change?.value !== undefined ? result.tds_change.value : null}
                variant="hero-mobile"
                certainty={result?.tds_change?.certainty}
                onViewProof={() => openProof("TDS Increase Proof", result?.tds_change)}
              />
            </div>
          ) : (
            /* Salary Mode: Neha Gupta (9) or Pooja Das (11) */
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-3)' }}>
              <NumberCard
                label="September take-home"
                amount={result?.after?.net_pay?.value !== undefined ? result.after.net_pay.value : null}
                variant="hero-mobile"
                certainty={result?.certainty}
                onViewProof={() => openProof("September Net Take-Home Proof", result?.after?.net_pay)}
              />
              <NumberCard
                label="Take-home pay change"
                amount={result?.net_change?.value !== undefined ? result.net_change.value : null}
                variant="hero-mobile"
                certainty={result?.net_change?.certainty}
                onViewProof={() => openProof("Net Change Calculation Proof", result?.net_change)}
              />
            </div>
          )}

          {/* Assistant Approved Copy Banner */}
          {activeQuestion === 10 ? (
            <MessageBubble
              author="HCM One Assistant"
              text={getAIMessage('C29', {
                declared_month_range: data?.display_inputs?.declared_month_range?.value || "2026-04 to 2026-06"
              })}
            />
          ) : activeQuestion === 11 || result?.no_earning_component_change ? (
            <div style={{
              backgroundColor: '#F0FDF4',
              border: '1px solid #BBF7D0',
              padding: 'var(--space-3)',
              borderRadius: 'var(--radius-input)',
              fontSize: '13px',
              color: '#166534',
              display: 'flex',
              alignItems: 'center',
              gap: 'var(--space-2)'
            }}>
              <strong>No salary earning component change.</strong> Take-home pay changed due to statutory PF ceiling update.
            </div>
          ) : null}

          {/* Reasons List: Ranked by effect on take-home pay */}
          <div style={{
            backgroundColor: 'var(--color-surface)',
            border: '1px solid var(--color-divider)',
            borderRadius: 'var(--radius-card)',
            padding: 'var(--space-4)',
            display: 'flex',
            flexDirection: 'column',
            gap: 'var(--space-3)'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h3 style={{ fontSize: '14px', fontWeight: 600, margin: 0, color: 'var(--color-text-primary)' }}>
                Ranked by effect on take-home pay
              </h3>
              <CertaintyLabel certainty={result?.certainty || "Complete for this scope"} />
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
              {(result?.reasons || []).map((reason: any, idx: number) => {
                const effectVal = reason?.effect_amount?.value;
                const isNegative = effectVal < 0;

                return (
                  <div
                    key={idx}
                    style={{
                      padding: 'var(--space-3)',
                      backgroundColor: 'var(--color-background)',
                      border: '1px solid var(--color-divider)',
                      borderRadius: 'var(--radius-input)',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center'
                    }}
                  >
                    <div>
                      <div style={{ fontWeight: 600, fontSize: '14px', color: 'var(--color-text-primary)' }}>
                        {idx + 1}. {reason.type}
                      </div>
                      <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', marginTop: '2px' }}>
                        Source: {reason.source_references?.[0]?.record_id || reason.type}
                      </div>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
                      <span style={{
                        fontWeight: 700,
                        fontSize: '15px',
                        color: isNegative ? 'var(--color-status-error-text)' : 'var(--color-status-success-text)'
                      }}>
                        {effectVal !== undefined ? `${isNegative ? '' : '+'}${effectVal.toLocaleString('en-IN')} INR` : '-'}
                      </span>
                      <button
                        type="button"
                        className="hcm-source-link"
                        onClick={() => openProof(`${reason.type} Calculation Proof`, reason?.effect_amount)}
                        title="View calculation proof"
                      >
                        <Eye size={14} />
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Query Initiation Button */}
          <div style={{ marginTop: 'var(--space-2)' }}>
            <Button
              variant="outline"
              onClick={handleStartQueryDraft}
              style={{ width: '100%', justifyContent: 'center' }}
            >
              <MessageSquare size={16} /> Draft a query for HR
            </Button>
          </div>
        </div>
      )}

      {/* Proof Sheet */}
      <Sheet
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
      </Sheet>
    </div>
  );
};
