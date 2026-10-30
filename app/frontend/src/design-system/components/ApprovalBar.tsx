import React from "react";
import { Button } from "./Button";
import { Info, Check, Edit3, XCircle } from "lucide-react";

import "../components.css";

export interface ApprovalBarProps {
  version: number;
  proposalId?: string;
  scopeSummary?: string;
  isApprovalDisabled?: boolean;
  isApproved?: boolean;
  isComplete?: boolean;
  onApprove: () => void;
  onEdit?: () => void;
  onReject: () => void;
  className?: string;
}

export const ApprovalBar: React.FC<ApprovalBarProps> = ({
  version,
  proposalId,
  scopeSummary = "Current reviewed scope",
  isApprovalDisabled,
  isApproved = false,
  isComplete = true,
  onApprove,
  onEdit,
  onReject,
  className = ""
}) => {
  const disabled = isApprovalDisabled !== undefined ? isApprovalDisabled : (isApproved || !isComplete);

  return (
    <div className={`hcm-approval-bar ${className}`} role="region" aria-label="Proposal Decision Actions">
      <div className="hcm-approval-disclaimer">
        <Info size={16} aria-hidden="true" style={{ flexShrink: 0 }} />
        <span>Approving records this version as ready for payroll. It does not apply the change or make a payment.</span>
      </div>

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "var(--space-3)" }}>
        <div style={{ fontSize: "var(--font-size-label)", color: "var(--color-text-secondary)" }}>
          {proposalId && <span><strong>{proposalId}</strong> (v{version})</span>}
          {!proposalId && <span>Version: <strong>{version}</strong></span>}
          <span style={{ margin: "0 var(--space-2)" }}>•</span>
          <span>Scope: <strong>{scopeSummary}</strong></span>
          {isApproved && <span style={{ marginLeft: "var(--space-2)", color: "var(--color-status-success-text)", fontWeight: "bold" }}>(Approved for Payroll)</span>}
        </div>

        <div className="hcm-approval-actions">
          <Button variant="danger" size="default" onClick={onReject} disabled={isApproved}>
            <XCircle size={16} aria-hidden="true" />
            <span>Reject</span>
          </Button>

          {onEdit && (
            <Button variant="secondary" size="default" onClick={onEdit} disabled={isApproved}>
              <Edit3 size={16} aria-hidden="true" />
              <span>Edit with a reason</span>
            </Button>
          )}

          <Button
            variant="primary"
            size="default"
            onClick={onApprove}
            disabled={disabled}
            title={disabled ? (isApproved ? "Already approved" : "Incomplete or unverified scope cannot be approved") : undefined}
          >
            <Check size={16} aria-hidden="true" />
            <span>{isApproved ? "Approved" : "Approve selected scope"}</span>
          </Button>
        </div>
      </div>
    </div>
  );
};
