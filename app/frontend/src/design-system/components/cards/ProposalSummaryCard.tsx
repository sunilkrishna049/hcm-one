import React from 'react';
import { formatINR, formatHumanDate } from '../../../utils/format';
import { CertaintyLabel } from '../CertaintyLabel';

interface ProposalSummaryCardProps {
  card: {
    id: string;
    type: string;
    title: string;
    certainty: string;
    data: {
      employee_name?: string;
      employee_id?: string;
      proposal_type?: string;
      requested_hike?: string;
      effective_date?: string;
      affected_periods?: string;
      old_monthly_salary_total?: number;
      proposed_monthly_salary_total?: number;
      status?: string;
      eligible_count?: number;
      ineligible_count?: number;
      needs_input_count?: number;
      gross_eligible_total?: number;
      known_eligible_gross?: number;
      known_eligible_gross_certainty?: string;
      eligible?: string[];
      not_eligible?: Array<{ employee_id: string; reason: string }>;
      needs_input?: Array<{ employee_id: string; reason: string }>;
      rating?: string | null;
      bonus_amount?: number | null;
      due_date?: string;
    };
  };
}

export const ProposalSummaryCard: React.FC<ProposalSummaryCardProps> = ({ card }) => {
  const d = card.data;

  return (
    <div className="hcm-rich-card hcm-card-proposal-summary" data-testid={`card-${card.id}`}>
      <div className="hcm-card-header">
        <div>
          <h3 className="hcm-card-title">{card.title || d.proposal_type || 'Proposal Summary'}</h3>
          {d.employee_name && (
            <span className="hcm-card-subtitle" style={{ color: 'var(--color-text-secondary)', fontSize: '13px' }}>
              {d.employee_name} {d.employee_id ? `(${d.employee_id})` : ''}
            </span>
          )}
        </div>
      </div>

      <div className="hcm-card-body">
        {d.requested_hike && (
          <div className="hcm-key-value-grid">
            <div className="hcm-kv-item">
              <span className="hcm-kv-label">Requested Hike</span>
              <strong className="hcm-kv-value">{d.requested_hike}</strong>
            </div>
            <div className="hcm-kv-item">
              <span className="hcm-kv-label">Effective Date</span>
              <span className="hcm-kv-value tnum">{formatHumanDate(d.effective_date)}</span>
            </div>
            <div className="hcm-kv-item">
              <span className="hcm-kv-label">Affected Periods</span>
              <span className="hcm-kv-value">{formatHumanDate(d.affected_periods)}</span>
            </div>
            {d.status && (
              <div className="hcm-kv-item">
                <span className="hcm-kv-label">Proposal Status</span>
                <span className="hcm-status-tag">{d.status}</span>
              </div>
            )}
          </div>
        )}

        {/* Salary comparison if available */}
        {d.old_monthly_salary_total !== undefined && d.proposed_monthly_salary_total !== undefined && (
          <div className="hcm-salary-comparison">
            <div className="hcm-salary-box">
              <span className="hcm-salary-label">Old Monthly Salary</span>
              <span className="hcm-salary-amount tnum">{formatINR(d.old_monthly_salary_total)}</span>
            </div>
            <span className="hcm-arrow-separator">→</span>
            <div className="hcm-salary-box hcm-salary-proposed">
              <span className="hcm-salary-label">Proposed Monthly Salary</span>
              <span className="hcm-salary-amount tnum">{formatINR(d.proposed_monthly_salary_total)}</span>
            </div>
          </div>
        )}

        {/* Team bonus summary grid if available */}
        {(d.gross_eligible_total !== undefined || d.known_eligible_gross !== undefined) && (
          <>
            <div className="hcm-key-value-grid">
              <div className="hcm-kv-item">
                <span className="hcm-kv-label">Eligible Employees</span>
                <strong className="hcm-kv-value tnum">{d.eligible_count}</strong>
              </div>
              <div className="hcm-kv-item">
                <span className="hcm-kv-label">Ineligible Employees</span>
                <span className="hcm-kv-value tnum">{d.ineligible_count}</span>
              </div>
              <div className="hcm-kv-item">
                <span className="hcm-kv-label">Pending Inputs</span>
                <span className="hcm-kv-value tnum">{d.needs_input_count}</span>
              </div>
              <div className="hcm-kv-item">
                <span className="hcm-kv-label">Known Eligible Gross</span>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                  <strong className="hcm-kv-value tnum">{formatINR(d.known_eligible_gross ?? d.gross_eligible_total)}</strong>
                  {(d.known_eligible_gross_certainty || card.certainty) && (
                    <CertaintyLabel certainty={d.known_eligible_gross_certainty || card.certainty} />
                  )}
                </div>
              </div>
            </div>

            {/* Engine's own eligible, not-eligible and needs-input lists copied exactly */}
            {d.eligible && d.eligible.length > 0 && (
              <div className="hcm-bonus-scope-lists" style={{ marginTop: 'var(--space-3)', borderTop: '1px solid var(--color-border)', paddingTop: 'var(--space-3)' }}>
                <div style={{ fontSize: '13px', marginBottom: 'var(--space-2)' }}>
                  <span style={{ fontWeight: 600, color: 'var(--color-text-secondary)' }}>Eligible ({d.eligible.length}): </span>
                  <span>
                    {d.eligible.map((id: string, idx: number) => (
                      <span key={id}>
                        {idx > 0 && ', '}
                        <strong className="tnum">{id}</strong>
                        {id === 'E03' && (
                          <span style={{ color: 'var(--color-status-warning-text)', marginLeft: '4px', fontSize: '12px' }}>(tax incomplete)</span>
                        )}
                      </span>
                    ))}
                  </span>
                </div>
                {d.not_eligible && d.not_eligible.length > 0 && (
                  <div style={{ fontSize: '13px', marginBottom: 'var(--space-2)' }}>
                    <span style={{ fontWeight: 600, color: 'var(--color-text-secondary)' }}>Not eligible ({d.not_eligible.length}): </span>
                    <span>
                      {d.not_eligible.map((item: any, idx: number) => (
                        <span key={idx}>
                          {idx > 0 && ', '}
                          <strong className="tnum">{typeof item === 'string' ? item : item.employee_id}</strong>
                          {typeof item === 'object' && item.reason && ` (${item.reason})`}
                        </span>
                      ))}
                    </span>
                  </div>
                )}
                {d.needs_input && d.needs_input.length > 0 && (
                  <div style={{ fontSize: '13px' }}>
                    <span style={{ fontWeight: 600, color: 'var(--color-text-secondary)' }}>Needs input ({d.needs_input.length}): </span>
                    <span>
                      {d.needs_input.map((item: any, idx: number) => (
                        <span key={idx}>
                          {idx > 0 && ', '}
                          <strong className="tnum">{typeof item === 'string' ? item : item.employee_id}</strong>
                          {typeof item === 'object' && item.reason && ` (${item.reason})`}
                        </span>
                      ))}
                    </span>
                  </div>
                )}
              </div>
            )}
          </>
        )}

        {/* Missing input or individual bonus summary */}
        {d.rating !== undefined && (
          <div className="hcm-key-value-grid">
            <div className="hcm-kv-item">
              <span className="hcm-kv-label">Recorded Performance Rating</span>
              <strong className="hcm-kv-value">{d.rating || 'Not recorded'}</strong>
            </div>
            <div className="hcm-kv-item">
              <span className="hcm-kv-label">Bonus Amount</span>
              <span className="hcm-kv-value tnum">{d.bonus_amount !== null && d.bonus_amount !== undefined ? formatINR(d.bonus_amount) : 'Cannot calculate'}</span>
            </div>
          </div>
        )}

        {d.due_date && (
          <div className="hcm-kv-item" style={{ marginTop: 'var(--space-2)' }}>
            <span className="hcm-kv-label">Applicable Due Date</span>
            <strong className="hcm-kv-value tnum">{formatHumanDate(d.due_date)}</strong>
          </div>
        )}
      </div>
    </div>
  );
};
