import React from 'react';
import { formatINR, formatHumanDate } from '../../../utils/format';

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
      employee_names?: Record<string, string>;
      version?: number;
      edit_reason?: string;
      reason?: string;
      changes?: string;
      edited_line?: string;
      proposed_value?: any;
    };
  };
}

export const ProposalSummaryCard: React.FC<ProposalSummaryCardProps> = ({ card }) => {
  const d = card.data;

  return (
    <div className="hcm-rich-card hcm-card-proposal-summary" data-testid={`card-${card.id}`}>
      <div className="hcm-card-header">
        <div>
          <h3 className="hcm-card-title">{card.title || d.proposal_type || 'Proposal summary'}</h3>
          {d.employee_name && (
            <span className="hcm-card-subtitle" style={{ color: 'var(--color-text-secondary)', fontSize: '13px' }}>
              {d.employee_name} {d.employee_id ? <>· <span style={{ color: 'var(--color-text-muted)' }}>{d.employee_id}</span></> : ''}
            </span>
          )}
          {d.version !== undefined && (
            <div className="hcm-card-subtitle tnum" style={{ color: 'var(--color-text-secondary)', fontSize: '12px', marginTop: '2px' }}>
              Version {d.version} {d.status ? `• ${d.status}` : ''}
            </div>
          )}
        </div>
      </div>

      <div className="hcm-card-body">
        {(d.edit_reason || d.reason || d.changes || d.edited_line) && (
          <div className="hcm-card-flag-note" style={{ marginBottom: 'var(--space-3)', padding: 'var(--space-2) var(--space-3)', backgroundColor: 'var(--color-surface-hover)', borderRadius: '6px', fontSize: '13px', border: '1px solid var(--color-divider)' }}>
            {(d.edit_reason || d.reason) && (
              <div><strong>Recorded edit reason:</strong> {d.edit_reason || d.reason}</div>
            )}
            {(d.changes || d.edited_line) && (
              <div style={{ marginTop: '2px' }}><strong>What changed:</strong> {d.changes || `${d.edited_line}: ${d.proposed_value}`}</div>
            )}
          </div>
        )}
        {d.requested_hike && (
          <div className="hcm-key-value-grid">
            <div className="hcm-kv-item">
              <span className="hcm-kv-label">Requested hike</span>
              <strong className="hcm-kv-value">{d.requested_hike}</strong>
            </div>
            <div className="hcm-kv-item">
              <span className="hcm-kv-label">Effective date</span>
              <span className="hcm-kv-value tnum">{formatHumanDate(d.effective_date)}</span>
            </div>
            <div className="hcm-kv-item">
              <span className="hcm-kv-label">Affected periods</span>
              <span className="hcm-kv-value">{formatHumanDate(d.affected_periods)}</span>
            </div>
            {d.status && (
              <div className="hcm-kv-item">
                <span className="hcm-kv-label">Proposal status</span>
                <span className="hcm-status-tag">{d.status}</span>
              </div>
            )}
          </div>
        )}

        {/* Salary comparison if available */}
        {d.old_monthly_salary_total !== undefined && d.proposed_monthly_salary_total !== undefined && (
          <div className="hcm-salary-comparison">
            <div className="hcm-salary-box">
              <span className="hcm-salary-label">Old monthly salary</span>
              <span className="hcm-salary-amount tnum">{formatINR(d.old_monthly_salary_total)}</span>
            </div>
            <span className="hcm-arrow-separator">→</span>
            <div className="hcm-salary-box hcm-salary-proposed">
              <span className="hcm-salary-label">Proposed monthly salary</span>
              <span className="hcm-salary-amount tnum">{formatINR(d.proposed_monthly_salary_total)}</span>
            </div>
          </div>
        )}

        {/* Team bonus summary grid if available */}
        {(d.gross_eligible_total !== undefined || d.known_eligible_gross !== undefined) && (
          <>
            <div className="hcm-key-value-grid">
              <div className="hcm-kv-item">
                <span className="hcm-kv-label">Eligible employees</span>
                <strong className="hcm-kv-value tnum">{d.eligible_count}</strong>
              </div>
              <div className="hcm-kv-item">
                <span className="hcm-kv-label">Ineligible employees</span>
                <span className="hcm-kv-value tnum">{d.ineligible_count}</span>
              </div>
              <div className="hcm-kv-item">
                <span className="hcm-kv-label">Pending inputs</span>
                <span className="hcm-kv-value tnum">{d.needs_input_count}</span>
              </div>
              <div className="hcm-kv-item">
                <span className="hcm-kv-label">Known eligible gross</span>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                  <strong className="hcm-kv-value tnum">{formatINR(d.known_eligible_gross ?? d.gross_eligible_total)}</strong>
                </div>
              </div>
            </div>

            {/* Engine's own eligible, not-eligible and needs-input lists copied exactly */}
            {d.eligible && d.eligible.length > 0 && (
              <div className="hcm-bonus-scope-lists" style={{ marginTop: 'var(--space-3)', borderTop: '1px solid var(--color-border)', paddingTop: 'var(--space-3)' }}>
                <div style={{ fontSize: '13px', marginBottom: 'var(--space-2)' }}>
                  <span style={{ fontWeight: 600, color: 'var(--color-text-secondary)' }}>Eligible ({d.eligible.length}): </span>
                  <span>
                    {d.eligible.map((id: string, idx: number) => {
                      const name = d.employee_names?.[id];
                      return (
                        <span key={id}>
                          {idx > 0 && ', '}
                          {name ? (
                            <>
                              <span>{name}</span> · <span className="tnum" style={{ color: 'var(--color-text-muted)' }}>{id}</span>
                            </>
                          ) : (
                            <span className="tnum" style={{ color: 'var(--color-text-muted)' }}>{id}</span>
                          )}
                          {id === 'E03' && (
                            <span style={{ color: 'var(--color-status-warning-text)', marginLeft: '4px', fontSize: '12px' }}>(tax incomplete)</span>
                          )}
                        </span>
                      );
                    })}
                  </span>
                </div>
                {d.not_eligible && d.not_eligible.length > 0 && (
                  <div style={{ fontSize: '13px', marginBottom: 'var(--space-2)' }}>
                    <span style={{ fontWeight: 600, color: 'var(--color-text-secondary)' }}>Not eligible ({d.not_eligible.length}): </span>
                    <span>
                      {d.not_eligible.map((item: any, idx: number) => {
                        const id = typeof item === 'string' ? item : item.employee_id;
                        const name = d.employee_names?.[id];
                        return (
                          <span key={idx}>
                            {idx > 0 && ', '}
                            {name ? (
                              <>
                                <span>{name}</span> · <span className="tnum" style={{ color: 'var(--color-text-muted)' }}>{id}</span>
                              </>
                            ) : (
                              <span className="tnum" style={{ color: 'var(--color-text-muted)' }}>{id}</span>
                            )}
                            {typeof item === 'object' && item.reason && ` (${item.reason})`}
                          </span>
                        );
                      })}
                    </span>
                  </div>
                )}
                {d.needs_input && d.needs_input.length > 0 && (
                  <div style={{ fontSize: '13px' }}>
                    <span style={{ fontWeight: 600, color: 'var(--color-text-secondary)' }}>Needs input ({d.needs_input.length}): </span>
                    <span>
                      {d.needs_input.map((item: any, idx: number) => {
                        const id = typeof item === 'string' ? item : item.employee_id;
                        const name = d.employee_names?.[id];
                        return (
                          <span key={idx}>
                            {idx > 0 && ', '}
                            {name ? (
                              <>
                                <span>{name}</span> · <span className="tnum" style={{ color: 'var(--color-text-muted)' }}>{id}</span>
                              </>
                            ) : (
                              <span className="tnum" style={{ color: 'var(--color-text-muted)' }}>{id}</span>
                            )}
                            {typeof item === 'object' && item.reason && ` (${item.reason})`}
                          </span>
                        );
                      })}
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
              <span className="hcm-kv-label">Recorded performance rating</span>
              <strong className="hcm-kv-value">{d.rating || 'Not recorded'}</strong>
            </div>
            <div className="hcm-kv-item">
              <span className="hcm-kv-label">Bonus amount</span>
              <span className="hcm-kv-value tnum">{d.bonus_amount !== null && d.bonus_amount !== undefined ? formatINR(d.bonus_amount) : 'Cannot calculate'}</span>
            </div>
          </div>
        )}

        {d.due_date && (
          <div className="hcm-kv-item" style={{ marginTop: 'var(--space-2)' }}>
            <span className="hcm-kv-label">Applicable due date</span>
            <strong className="hcm-kv-value tnum">{formatHumanDate(d.due_date)}</strong>
          </div>
        )}
      </div>
    </div>
  );
};
