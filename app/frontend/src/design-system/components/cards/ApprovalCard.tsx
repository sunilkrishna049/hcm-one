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
      blocking_reason?: string;
      proposal_id?: string;
    };
  };
  onApprove?: (payload?: { proposal_id?: string; version?: number }) => void;
  onEdit?: (payload?: { proposal_id?: string; version?: number; reason?: string }) => void;
  onReject?: (payload?: { proposal_id?: string; version?: number; reason?: string }) => void;
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
    .replace(/^[•·\s]+/, '')
    .trim();

  const prefix = isApproved ? 'Approved:' : "You're approving:";
  // Only structured if an individual employee_name is provided; team proposals use cleanScope
  const hasStructuredScope = Boolean(d.employee_name);

  const approverName = d.approver ? getUserDisplayName(d.approver) : 'Anita Desai';

  // Option A: "Approve proposal for payroll" is disabled when certainty is not "Complete for this scope"
  // Item 3: If a card has no proposal_id or version, the Approve button is disabled.
  const isComplete = card.certainty === 'Complete for this scope';
  const hasValidProposal = Boolean(d.proposal_id && d.version !== undefined && d.version !== null);
  const isApprovalDisabled = Boolean(d.disabled || (card.certainty && !isComplete) || !hasValidProposal);

  const missingIdentifierReason = !d.proposal_id
    ? 'Proposal identifier is missing.'
    : (d.version === undefined || d.version === null)
    ? 'Proposal version is missing.'
    : undefined;

  const blockingReason = d.blocking_reason || d.disabled_label || missingIdentifierReason || (card.certainty && !isComplete ? `Scope is ${card.certainty}; required inputs pending.` : undefined);

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
                  <span>{d.employee_name}</span>
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
        {!isApproved && !isRejected && !isEdited && (!d.actions || d.actions.length > 0) && d.notice && (
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
              Version {d.version} • Approver: {approverName} • {formatLocalTime(d.approved_at || new Date())}
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

        {/* Actions Group (explicit clicks only - hidden once approved, rejected, edited, or if actions is empty) */}
        {!isApproved && !isRejected && !isEdited && (!d.actions || d.actions.length > 0) && (
          <div>
            {isApprovalDisabled && blockingReason && (
              <div
                id={`approval-reason-${card.id}`}
                className="hcm-approval-disabled-reason"
                data-testid="approval-disabled-reason"
                style={{
                  marginBottom: 'var(--space-2)',
                  fontSize: 'var(--font-size-small)',
                  color: 'var(--color-status-error-text)',
                  fontWeight: 'var(--font-weight-medium)',
                }}
              >
                {blockingReason}
              </div>
            )}
            <div className="hcm-approval-actions">
            <button
              type="button"
              className={`hcm-button hcm-button-primary ${isApprovalDisabled ? 'hcm-button-disabled' : ''}`}
              onClick={isApprovalDisabled ? undefined : () => onApprove?.({ proposal_id: d.proposal_id, version: d.version })}
              disabled={isApprovalDisabled}
              aria-disabled={isApprovalDisabled ? 'true' : undefined}
              aria-describedby={isApprovalDisabled && blockingReason ? `approval-reason-${card.id}` : undefined}
              data-testid={isApprovalDisabled ? "approval-button-disabled" : "approval-button"}
              title={isApprovalDisabled ? blockingReason : undefined}
            >
              Approve proposal for payroll
            </button>
            <button
              type="button"
              className="hcm-button hcm-button-secondary"
              onClick={() => onEdit?.({ proposal_id: d.proposal_id, version: d.version, reason: 'Adjusted by HR' })}
            >
              Edit with reason
            </button>
            <button
              type="button"
              className="hcm-button hcm-button-danger"
              onClick={() => onReject?.({ proposal_id: d.proposal_id, version: d.version, reason: 'Rejected by HR' })}
            >
              Reject proposal
            </button>
            </div>
          </div>
        )}

        {/* Option A Note: Reason from engine data why approval is disabled */}
        {isApprovalDisabled && !isApproved && !isRejected && !isEdited && (!d.actions || d.actions.length > 0) && blockingReason && (
          <div
            id={`approval-reason-${card.id}`}
            className="hcm-approval-blocked-note"
            data-testid="approval-disabled-note"
          >
            <span>{blockingReason}</span>
          </div>
        )}

        {/* When actions have been removed after an action is taken */}
        {d.actions && d.actions.length === 0 && d.disabled_label && !isApproved && !isRejected && !isEdited && (
          <div
            id={`approval-reason-${card.id}`}
            className="hcm-approval-blocked-note"
            data-testid="approval-disabled-note"
          >
            <span>{d.disabled_label}</span>
          </div>
        )}
      </div>
    </div>
  );
};
