import React from 'react';
import { CertaintyLabel } from '../CertaintyLabel';

interface ApprovalCardProps {
  card: {
    id: string;
    type: string;
    title: string;
    certainty: string;
    data: {
      scope_label: string;
      notice: string;
      actions?: string[];
      status?: 'pending' | 'approved' | 'rejected' | string;
      status_badge?: string;
      disabled?: boolean;
      proposal_id?: string;
    };
  };
  onApprove?: () => void;
  onEdit?: () => void;
  onReject?: () => void;
}

export const ApprovalCard: React.FC<ApprovalCardProps> = ({
  card,
  onApprove,
  onEdit,
  onReject,
}) => {
  const d = card.data;
  const isApproved = d.status === 'approved';
  const isRejected = d.status === 'rejected';

  return (
    <div
      className={`hcm-rich-card hcm-card-approval ${isApproved ? 'hcm-approval-approved' : ''}`}
      data-testid={`card-${card.id}`}
    >
      <div className="hcm-card-header">
        <div>
          <span className="hcm-card-type-badge">HR Governance Action</span>
          <h4 className="hcm-card-title">{card.title}</h4>
        </div>
        <CertaintyLabel certainty={card.certainty} />
      </div>

      <div className="hcm-card-body">
        <div className="hcm-approval-scope">
          <span className="hcm-kv-label">Authorized Scope:</span>
          <strong>{d.scope_label}</strong>
        </div>

        {/* Mandatory C04 Governance Notice */}
        <div className="hcm-approval-notice">
          <p>{d.notice}</p>
        </div>

        {/* Post-Action Status Badge */}
        {isApproved && (
          <div className="hcm-approval-success-banner" data-testid="approval-status-badge">
            ✓ {d.status_badge || 'Approved for payroll • Version 1 • Awaiting payroll processing'}
          </div>
        )}

        {isRejected && (
          <div className="hcm-approval-rejected-banner">
            ✕ Proposal has been rejected.
          </div>
        )}

        {/* Actions Group (explicit clicks only) */}
        {!isApproved && !isRejected && !d.disabled && (
          <div className="hcm-approval-actions">
            <button
              type="button"
              className="hcm-button hcm-button-primary"
              onClick={onApprove}
            >
              Approve proposal for payroll
            </button>
            <button
              type="button"
              className="hcm-button hcm-button-secondary"
              onClick={onEdit}
            >
              Edit with reason
            </button>
            <button
              type="button"
              className="hcm-button hcm-button-danger"
              onClick={onReject}
            >
              Reject proposal
            </button>
          </div>
        )}

        {d.disabled && (
          <div className="hcm-approval-blocked-note">
            <span>Notice: Blocked from approval while required records or clearances are incomplete.</span>
          </div>
        )}
      </div>
    </div>
  );
};
