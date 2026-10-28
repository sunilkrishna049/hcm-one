import React, { useState } from 'react';
import { Button } from './Button';
import { Textarea } from './Input';
import { getAIMessage } from '../ai_messages';
import { X, FileText } from 'lucide-react';

export interface QueryDraftData {
  employee_id: string;
  employee_name: string;
  pay_period: string;
  topic: string;
  description: string;
  evidence: Array<{
    type: string;
    item?: string;
    description?: string;
    source?: string;
    [key: string]: any;
  }>;
  candidate_query_id?: string | null;
  candidate_query_text?: string | null;
}

interface QueryDraftProps {
  initialData: QueryDraftData;
  onSubmit: (data: {
    description: string;
    evidence: any[];
    confirmed: boolean;
    appendToQueryId?: string | null;
  }) => void;
  onCancel: () => void;
  isSubmitting?: boolean;
}

export const QueryDraft: React.FC<QueryDraftProps> = ({
  initialData,
  onSubmit,
  onCancel,
  isSubmitting = false,
}) => {
  const [description, setDescription] = useState(initialData.description || "");
  const [evidenceList, setEvidenceList] = useState(initialData.evidence || []);
  const [confirmed, setConfirmed] = useState(false);
  const [appendChoice, setAppendChoice] = useState<'new' | 'append'>(
    initialData.candidate_query_id ? 'new' : 'new'
  );

  const handleRemoveEvidence = (index: number) => {
    setEvidenceList(prev => prev.filter((_, i) => i !== index));
  };

  const isAppend = initialData.candidate_query_id && appendChoice === 'append';
  const confirmationSentence = isAppend ? getAIMessage('C13') : getAIMessage('C12');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!confirmed) return;
    onSubmit({
      description,
      evidence: evidenceList,
      confirmed: true,
      appendToQueryId: isAppend ? initialData.candidate_query_id : null,
    });
  };

  return (
    <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
      {/* Candidate Query Match (if any) using Sentence C14 */}
      {initialData.candidate_query_id && (
        <div style={{
          padding: 'var(--space-4)',
          backgroundColor: 'var(--color-surface)',
          borderRadius: 'var(--radius-card)',
          border: '1px solid var(--color-brand-accent)'
        }}>
          <div style={{ fontWeight: 'var(--font-weight-medium)', marginBottom: 'var(--space-2)' }}>
            {getAIMessage('C14')}
          </div>

          <div style={{ fontSize: 'var(--font-size-small)', color: 'var(--color-text-secondary)', marginBottom: 'var(--space-3)' }}>
            Existing open query: <strong>{initialData.candidate_query_id}</strong> &mdash; "{initialData.candidate_query_text}"
          </div>
          <div style={{ display: 'flex', gap: 'var(--space-4)' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', cursor: 'pointer' }}>
              <input
                type="radio"
                name="query_target"
                checked={appendChoice === 'append'}
                onChange={() => setAppendChoice('append')}
              />
              <span>Add to existing query ({initialData.candidate_query_id})</span>
            </label>
            <label style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', cursor: 'pointer' }}>
              <input
                type="radio"
                name="query_target"
                checked={appendChoice === 'new'}
                onChange={() => setAppendChoice('new')}
              />
              <span>Create new separate query</span>
            </label>
          </div>
        </div>
      )}

      {/* Query Scope / Topic */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: 'var(--space-3)',
        padding: 'var(--space-3)',
        backgroundColor: 'var(--color-surface)',
        borderRadius: 'var(--radius-input)'
      }}>
        <div>
          <span style={{ fontSize: 'var(--font-size-small)', color: 'var(--color-text-secondary)' }}>Employee: </span>
          <strong>{initialData.employee_name} · <span style={{ color: 'var(--color-text-muted)' }}>{initialData.employee_id}</span></strong>
        </div>
        <div>
          <span style={{ fontSize: 'var(--font-size-small)', color: 'var(--color-text-secondary)' }}>Pay Period: </span>
          <strong>{initialData.pay_period}</strong>
        </div>
        <div>
          <span style={{ fontSize: 'var(--font-size-small)', color: 'var(--color-text-secondary)' }}>Topic: </span>
          <strong>{initialData.topic}</strong>
        </div>
      </div>

      {/* Description Edit */}
      <div className="hcm-form-group">
        <label className="hcm-form-label" htmlFor="query-desc">
          Description (Editable)
        </label>
        <Textarea
          id="query-desc"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          rows={4}
          required
        />
      </div>

      {/* Evidence Badges with Remove */}
      <div className="hcm-form-group">
        <label className="hcm-form-label">
          Attached Evidence ({evidenceList.length})
        </label>
        {evidenceList.length === 0 ? (
          <div style={{ fontSize: 'var(--font-size-small)', color: 'var(--color-text-secondary)' }}>
            No evidence attached.
          </div>
        ) : (
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--space-2)' }}>
            {evidenceList.map((ev, index) => (
              <div
                key={index}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 'var(--space-2)',
                  padding: 'var(--space-2) var(--space-3)',
                  backgroundColor: 'var(--color-surface)',
                  border: '1px solid var(--color-border-subtle)',
                  borderRadius: 'var(--radius-pill)',
                  fontSize: 'var(--font-size-small)',
                }}
              >
                <FileText size={14} color="var(--color-brand-accent)" />
                <span>
                  {ev.item || ev.type || ev.description || `Evidence #${index + 1}`}
                  {ev.source && ` (${ev.source})`}
                </span>
                <button
                  type="button"
                  onClick={() => handleRemoveEvidence(index)}
                  style={{
                    background: 'none',
                    border: 'none',
                    cursor: 'pointer',
                    padding: 0,
                    display: 'flex',
                    alignItems: 'center',
                    color: 'var(--color-text-secondary)',
                  }}
                  title="Remove this evidence item"
                >
                  <X size={14} />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Confirmation Checkbox - Mandatory */}
      <div style={{
        padding: 'var(--space-3) var(--space-4)',
        backgroundColor: confirmed ? 'var(--color-status-success-surface)' : 'var(--color-surface)',
        border: `1px solid ${confirmed ? 'var(--color-status-success-border)' : 'var(--color-divider)'}`,
        borderRadius: 'var(--radius-input)',
        display: 'flex',
        alignItems: 'flex-start',
        gap: 'var(--space-3)'
      }}>
        <input
          type="checkbox"
          id="query-confirm"
          checked={confirmed}
          onChange={(e) => setConfirmed(e.target.checked)}
          style={{ width: '18px', height: '18px', marginTop: '2px', cursor: 'pointer' }}
        />
        <label htmlFor="query-confirm" style={{ cursor: 'pointer', fontSize: 'var(--font-size-body)', lineHeight: '1.4' }}>
          <strong>{confirmationSentence}</strong>
          <div style={{ fontSize: 'var(--font-size-small)', color: 'var(--color-text-secondary)', marginTop: '2px' }}>
            Check this box to confirm. HCM One never sends a query without explicit employee confirmation.
          </div>
        </label>
      </div>

      {/* Action Buttons */}
      <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 'var(--space-3)', marginTop: 'var(--space-2)' }}>
        <Button variant="secondary" onClick={onCancel} type="button">
          Cancel (Keep as Draft)
        </Button>
        <Button
          variant="primary"
          type="submit"
          disabled={!confirmed || isSubmitting}
        >
          {isSubmitting ? "Sending..." : isAppend ? "Add to Open Query" : "Send Query to HR"}
        </Button>
      </div>
    </form>
  );
};
