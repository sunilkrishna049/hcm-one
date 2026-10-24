import React from 'react';
import { formatHumanDate } from '../../../utils/format';
import { getUserDisplayName } from '../../../utils/userDisplay';

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
      status_text?: string;
      status_badge?: string;
      version?: number;
      approver?: string;
      approved_at?: string;
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

  // Format clean scope display: "You're approving: Priya Sharma · Apr–Sep 2026"
  const rawScope = d.scope_label || '';
  const cleanScope = rawScope.replace(/^Authorized Scope:\s*/i, '');
  const scopeDisplay = cleanScope
    ? (cleanScope.startsWith("You're approving:") ? cleanScope : `You're approving: ${cleanScope}`)
    : '';

  const approverName = d.approver ? getUserDisplayName(d.approver) : 'Anita Desai';

  // Heading: plain heading without dev labels
  const heading = card.title === 'HR Authorization' || !card.title ? 'Approval' : card.title;

  return (
    <div
      className={`hcm-rich-card hcm-card-approval ${isApproved ? 'hcm-approval-approved' : ''}`}
      data-testid={`card-${card.id}`}
    >
      <div className="hcm-card-header">
        <h4 className="hcm-card-title">{heading}</h4>
      </div>

      <div className="hcm-card-body">
        {scopeDisplay && (
          <div className="hcm-approval-scope">
            <strong>{scopeDisplay}</strong>
          </div>
        )}

        {/* Mandatory C04 Governance Notice */}
        <div className="hcm-approval-notice">
          <p>{d.notice}</p>
        </div>

        {/* Post-Action Status Badge */}
        {isApproved && (
          <div className="hcm-approval-success-banner" data-testid="approval-status-badge">
            <div style={{ fontWeight: 600, marginBottom: '2px' }}>
              ✓ Approved and ready for payroll
            </div>
            <div style={{ fontSize: '12px', opacity: 0.9 }}>
              Version {d.version ?? 1} • Approver: {approverName} • {d.approved_at ? formatHumanDate(d.approved_at) : 'Just now'}
            </div>
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
