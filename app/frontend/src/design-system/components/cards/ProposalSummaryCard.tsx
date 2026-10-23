import React from 'react';
import { CertaintyLabel } from '../CertaintyLabel';
import { formatINR } from '../../../utils/format';

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
          <span className="hcm-card-type-badge">{card.title || d.proposal_type}</span>
          {d.employee_name && (
            <h3 className="hcm-card-title">
              {d.employee_name}{' '}
              {d.employee_id && <span className="hcm-tech-id">({d.employee_id})</span>}
            </h3>
          )}
        </div>
        <CertaintyLabel certainty={card.certainty} />
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
              <span className="hcm-kv-value tnum">{d.effective_date}</span>
            </div>
            <div className="hcm-kv-item">
              <span className="hcm-kv-label">Affected Periods</span>
              <span className="hcm-kv-value">{d.affected_periods}</span>
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
        {d.gross_eligible_total !== undefined && (
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
              <span className="hcm-kv-label">Needs Input</span>
              <span className="hcm-kv-value tnum">{d.needs_input_count}</span>
            </div>
            <div className="hcm-kv-item">
              <span className="hcm-kv-label">Gross Eligible Total</span>
              <strong className="hcm-kv-value tnum">{formatINR(d.gross_eligible_total)}</strong>
            </div>
          </div>
        )}

        {/* Exit settlement due date if available */}
        {d.due_date && (
          <div className="hcm-due-date-row">
            <span className="hcm-kv-label">Applicable Due Date:</span>
            <strong className="tnum" style={{ color: 'var(--color-brand-accent)' }}>{d.due_date}</strong>
          </div>
        )}
      </div>
    </div>
  );
};
