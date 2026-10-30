import React, { useState } from 'react';
import { formatHumanDate } from '../../../utils/format';

interface QueryDraftCardProps {
  card: {
    id: string;
    type: string;
    title: string;
    certainty?: string;
    data: {
      query_id?: string;
      employee_id?: string;
      employee_label?: string;
      name_code?: string;
      status?: string;
      period?: string;
      category?: string;
      description?: string;
      draft_reply?: string;
      reply_text?: string;
      draft?: {
        category: string;
        months: string[];
        description: string;
        evidence: Array<{ type: string; source: string; period?: string }>;
      };
      notice?: string;
      actions?: string[];
    };
  };
  onSendQuery?: (description: string, queryId?: string) => void;
  onCancel?: () => void;
}

export const QueryDraftCard: React.FC<QueryDraftCardProps> = ({
  card,
  onSendQuery,
  onCancel,
}) => {
  const d = card.data;
  const isReplyDraft = Boolean(d.query_id || d.draft_reply || card.id?.includes('card-draft-QUERY-'));
  const draft: any = (d as any).draft || {};
  const [description, setDescription] = useState(
    (d as any).draft_reply || (d as any).reply_text || draft.description || (d as any).description || ''
  );
  const [confirmed, setConfirmed] = useState(false);

  // HR Reply Draft view
  if (isReplyDraft) {
    const qId = d.query_id || 'QUERY-E05-SEPTEMBER';
    const noticeText = d.notice || 'Nothing is sent until HR clicks Send and confirms.';

    return (
      <div className="hcm-rich-card hcm-card-query-draft" data-testid={`card-${card.id}`}>
        <div className="hcm-card-header">
          <div>
            <h4 className="hcm-card-title">{card.title || "Reply to query"}</h4>
            {d.period && <span className="hcm-due-date-pill">{d.period}</span>}
          </div>
          <span className="hcm-tech-id">{qId}</span>
        </div>

        <div className="hcm-card-body">
          {(d.employee_label || d.name_code) && (
            <div className="hcm-kv-item" style={{ marginBottom: 'var(--space-2)' }}>
              <span className="hcm-kv-label">Employee</span>
              <strong>{d.employee_label || d.name_code}</strong>
            </div>
          )}
          {d.description && (
            <div className="hcm-query-description-box" style={{ marginBottom: 'var(--space-3)' }}>
              <span className="hcm-kv-label">Employee Inquiry</span>
              <p>{d.description}</p>
            </div>
          )}

          <div className="hcm-form-group">
            <label className="hcm-form-label" htmlFor="reply-text">
              HR Reply Draft:
            </label>
            <textarea
              id="reply-text"
              className="hcm-textarea"
              rows={3}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </div>

          <div className="hcm-approval-notice" style={{ marginTop: 'var(--space-3)' }}>
            <p>{noticeText}</p>
          </div>

          {/* Confirmation Checkbox */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: 'var(--space-2)',
            marginTop: 'var(--space-3)',
            padding: 'var(--space-2)',
            backgroundColor: 'var(--color-surface)',
            borderRadius: 'var(--radius-input)',
            border: `1px solid ${confirmed ? 'var(--color-status-success-border)' : 'var(--color-divider)'}`
          }}>
            <input
              type="checkbox"
              id="confirm-reply-draft"
              checked={confirmed}
              onChange={(e) => setConfirmed(e.target.checked)}
              style={{ width: '16px', height: '16px', cursor: 'pointer' }}
            />
            <label htmlFor="confirm-reply-draft" style={{ cursor: 'pointer', fontSize: 'var(--font-size-small)' }}>
              Confirm reply before sending. Nothing is sent until confirmed.
            </label>
          </div>

          <div className="hcm-approval-actions" style={{ marginTop: 'var(--space-3)', display: 'flex', gap: 'var(--space-2)' }}>
            <button
              type="button"
              className="hcm-button hcm-button-primary"
              disabled={!confirmed}
              onClick={() => {
                if (confirmed && onSendQuery) {
                  onSendQuery(description, qId);
                }
              }}
            >
              Send reply
            </button>
            {onCancel && (
              <button
                type="button"
                className="hcm-button hcm-button-secondary"
                onClick={onCancel}
              >
                Cancel
              </button>
            )}
          </div>
        </div>
      </div>
    );
  }

  // Employee query draft view
  const notice = d.notice;

  return (
    <div className="hcm-rich-card hcm-card-query-draft" data-testid={`card-${card.id}`}>
      <div className="hcm-card-header">
        <div>
          <h4 className="hcm-card-title">{card.title}</h4>
        </div>
      </div>

      <div className="hcm-card-body">
        <div className="hcm-key-value-grid">
          <div className="hcm-kv-item">
            <span className="hcm-kv-label">Category</span>
            <strong>{draft.category}</strong>
          </div>
          <div className="hcm-kv-item">
            <span className="hcm-kv-label">Target months</span>
            <span className="tnum">{(draft.months || []).map((m: string) => formatHumanDate(m)).join(', ')}</span>
          </div>
        </div>

        <div className="hcm-form-group" style={{ marginTop: 'var(--space-3)' }}>
          <label className="hcm-form-label">Employee inquiry description:</label>
          <textarea
            className="hcm-textarea"
            rows={3}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
        </div>

        {/* Attached Evidence List */}
        <div className="hcm-evidence-section" style={{ marginTop: 'var(--space-3)' }}>
          <span className="hcm-kv-label">Attached sourced evidence:</span>
          <ul className="hcm-evidence-list">
            {(draft.evidence || []).map((ev: any, i: number) => (
              <li key={i} className="hcm-evidence-item">
                <span className="hcm-tech-id">{ev.source}</span>
                <span style={{ color: 'var(--color-text-secondary)', fontSize: '13px', marginLeft: 'var(--space-2)' }}>
                  ({ev.type})
                </span>
              </li>
            ))}
          </ul>
        </div>

        {/* Notice */}
        <div className="hcm-approval-notice" style={{ marginTop: 'var(--space-3)' }}>
          <p>{notice || 'Send this query with the listed evidence to HR?'}</p>
        </div>

        <div className="hcm-approval-actions" style={{ marginTop: 'var(--space-3)', display: 'flex', gap: 'var(--space-2)' }}>
          <button
            type="button"
            className="hcm-button hcm-button-primary"
            onClick={() => {
              if (onSendQuery) {
                onSendQuery(description);
              }
            }}
          >
            Send query with listed evidence to HR
          </button>
          {onCancel && (
            <button
              type="button"
              className="hcm-button hcm-button-secondary"
              onClick={onCancel}
            >
              Cancel
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
