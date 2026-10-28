import React from 'react';
import { formatLocalTime } from '../../../utils/format';
import { getUserDisplayName } from '../../../utils/userDisplay';

interface ApprovalCardProps {
  card: {
    id: string;
    type: string;
    title: string;
    certainty?: string;
    data: {
      scope_label?: string;
      employee_name?: string | null;
      employee_id?: string | null;
      period?: string | null;
      notice?: string;
      actions?: string[];
      status?: 'pending' | 'approved' | 'rejected' | 'edited' | string;
      status_text?: string;
      status_badge?: string;
      version?: number;
      approver?: string;
      approved_at?: string;
      disabled?: boolean;
      disabled_label?: string;
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
  const isEdited = d.status === 'edited';

  // Format clean scope display:
  // When pending: "You're approving: Priya Sharma · Apr–Sep 2026"
  // When approved: "Approved: Priya Sharma · Apr–Sep 2026" (past tense)
  const rawScope = d.scope_label || '';
  const cleanScope = rawScope
    .replace(/^Authorized Scope:\s*/i, '')
    .replace(/^You're approving:\s*/i, '')
    .replace(/^Approved:\s*/i, '')
    .trim();

  const prefix = isApproved ? 'Approved:' : "You're approving:";
  const hasStructuredScope = Boolean(d.employee_name || d.employee_id || d.period);

  const approverName = d.approver ? getUserDisplayName(d.approver) : 'Anita Desai';

  // Heading: plain heading without dev labels
  const heading = card.title === 'HR Authorization' || card.title === 'HR authorization' || !card.title ? 'Approval' : card.title;

  return (
    <div
      className={`hcm-rich-card hcm-card-approval ${isApproved ? 'hcm-approval-approved' : ''}`}
      data-testid={`card-${card.id}`}
    >
      <div className="hcm-card-header">
        <h4 className="hcm-card-title">{heading}</h4>
      </div>

      <div className="hcm-card-body">
        {(hasStructuredScope || cleanScope) && (
          <div className="hcm-approval-scope">
            <strong>
              {prefix}{' '}
              {hasStructuredScope ? (
                <>
                  {d.employee_name && <span>{d.employee_name}</span>}
                  {d.employee_id && (
                    <>
                      {' · '}
                      <span style={{ color: 'var(--color-text-muted)', fontWeight: 400 }}>
                        {d.employee_id}
                      </span>
                    </>
                  )}
                  {d.period && <> · {d.period}</>}
                </>
              ) : (
                cleanScope
              )}
            </strong>
          </div>
        )}

        {/* Mandatory C04 Governance Notice - only when actively pending approval */}
        {!isApproved && !isRejected && !isEdited && !d.disabled && d.notice && (
          <div className="hcm-approval-notice">
            <p>{d.notice}</p>
          </div>
        )}

        {/* Post-Action Status Banner */}
        {isApproved && (
          <div className="hcm-approval-success-banner" data-testid="approval-status-badge">
            <div style={{ fontWeight: 600, marginBottom: '2px' }}>
              ✓ Approved and ready for payroll
            </div>
            <div style={{ fontSize: '12px', opacity: 0.9 }}>
              Version {d.version ?? 1} • Approver: {approverName} • {formatLocalTime(d.approved_at || new Date())}
            </div>
          </div>
        )}

        {isRejected && (
          <div className="hcm-approval-rejected-banner" data-testid="approval-status-badge">
            ✕ Proposal has been rejected.
          </div>
        )}

        {isEdited && (
          <div
            className="hcm-approval-edited-banner"
            data-testid="approval-status-badge"
            style={{
              padding: '8px 12px',
              backgroundColor: 'var(--color-surface-hover)',
              borderRadius: '6px',
              fontSize: '13px',
              color: 'var(--color-text-secondary)',
              border: '1px solid var(--color-divider)',
            }}
          >
            ✎ Proposal revised. An updated version has been generated.
          </div>
        )}

        {/* Actions Group (explicit clicks only - hidden once approved, rejected, edited or disabled) */}
        {!isApproved && !isRejected && !isEdited && !d.disabled && (
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

        {d.disabled && !isApproved && !isRejected && !isEdited && (
          <div className="hcm-approval-blocked-note" data-testid="approval-disabled-note">
            <span>{d.disabled_label || 'Notice: Blocked from approval while required records or clearances are incomplete.'}</span>
          </div>
        )}
      </div>
    </div>
  );
};
