import React, { useState } from 'react';
import { formatHumanDate } from '../../../utils/format';

interface QueryItem {
  query_id: string;
  status: 'Draft' | 'Sent' | 'In review' | 'Resolved' | 'Closed' | string;
  category?: string;
  description?: string;
  reply_text?: string;
  resolution?: string;
}

interface QueryStatusCardProps {
  role?: string;
  card: {
    id: string;
    type: string;
    title: string;
    certainty?: string;
    role?: string;
    data: {
      query_id?: string;
      role?: string;
      closed_by?: string;
      closed_at?: string;
      resolved_by?: string;
      resolved_at?: string;
      status?: string;
      category?: string;
      description?: string;
      reply_text?: string;
      resolution?: string;
      employee_label?: string;
      name_code?: string;
      notice?: string;
      is_resolve_confirmation?: boolean;
      queries?: QueryItem[];
    };
  };
  onTakeIntoReview?: (queryId: string) => void;
  onResolveQuery?: (queryId: string) => void;
  onDisputeQuery?: (queryId: string) => void;
  onCloseQuery?: (queryId: string) => void;
  onConfirmResolve?: (queryId: string, replyText?: string) => void;
  onCancel?: () => void;
  onActionClick?: (act: string, payload?: any) => void;
}

export const QueryStatusCard: React.FC<QueryStatusCardProps> = ({
  role: propRole,
  card,
  onTakeIntoReview,
  onResolveQuery,
  onDisputeQuery,
  onCloseQuery,
  onConfirmResolve,
  onCancel,
  onActionClick,
}) => {
  const d = card.data;

  // Render list of queries for HR review
  if (d.queries && d.queries.length > 0) {
    return (
      <div className="hcm-rich-card hcm-card-query-status" data-testid={`card-${card.id}`}>
        <div className="hcm-card-header">
          <h4 className="hcm-card-title">{card.title}</h4>
        </div>
        <div className="hcm-query-list">
          {d.queries.map((q) => (
            <div key={q.query_id} className="hcm-query-item-row">
              <div className="hcm-query-item-meta">
                <span className="hcm-tech-id">{q.query_id}</span>
                <span className={`hcm-status-tag hcm-status-${q.status.toLowerCase().replace(/\s+/g, '-')}`}>
                  {q.status}
                </span>
              </div>
              <p className="hcm-query-item-desc">{q.description}</p>
              {q.status === 'Sent' && onTakeIntoReview && (
                <button
                  type="button"
                  className="hcm-button hcm-button-secondary hcm-button-sm"
                  onClick={() => onTakeIntoReview(q.query_id)}
                >
                  Take into review
                </button>
              )}
              {q.status === 'In review' && onResolveQuery && (
                <button
                  type="button"
                  className="hcm-button hcm-button-primary hcm-button-sm"
                  onClick={() => onResolveQuery(q.query_id)}
                >
                  Resolve query
                </button>
              )}
            </div>
          ))}
        </div>
      </div>
    );
  }

  // Single query status
  const status = d.status || 'Sent';
  const viewerRole = propRole || (card as any).role || d.role;
  const isEmployee = viewerRole === 'Employee';

  const isResolveConfirmation = Boolean(
    d.is_resolve_confirmation ||
    (card as any).is_resolve_confirmation ||
    card.title?.toLowerCase().includes('resolve query confirmation') ||
    card.title === 'Resolve query confirmation' ||
    card.id?.includes('card-confirm-resolve') ||
    card.id?.includes('confirm-resolve') ||
    (!isEmployee && (card.title?.toLowerCase().includes('resolve') || card.id?.includes('resolve')) && (status === 'In review' || d.notice?.toLowerCase().includes('confirmation')))
  );
  const [resolutionNote, setResolutionNote] = useState('');
  const [isCancelled, setIsCancelled] = useState(false);
  const [isConfirmed, setIsConfirmed] = useState(false);

  if (isResolveConfirmation) {
    const qId = d.query_id || '';
    const empLabel = d.employee_label || d.name_code || '';
    return (
      <div className="hcm-rich-card hcm-card-query-status" data-testid={`card-${card.id}`}>
        <div className="hcm-card-header">
          <div>
            {!isEmployee && qId && <span className="hcm-tech-id">{qId}</span>}
            <h4 className="hcm-card-title" style={{ marginTop: '2px' }}>{card.title}</h4>
          </div>
          <span className={`hcm-status-tag hcm-status-${status.toLowerCase().replace(/\s+/g, '-')}`}>
            {status}
          </span>
        </div>

        <div className="hcm-card-body">
          {empLabel && (
            <div className="hcm-kv-item" style={{ marginBottom: 'var(--space-2)' }}>
              <span className="hcm-kv-label">Employee</span>
              <strong>{empLabel}</strong>
            </div>
          )}

          {d.description && (
            <div className="hcm-query-description-box" style={{ marginBottom: 'var(--space-2)' }}>
              <span className="hcm-kv-label">Inquiry:</span>
              <p>{d.description}</p>
            </div>
          )}

          {d.notice && (
            <div className="hcm-approval-notice" style={{ marginBottom: 'var(--space-2)' }}>
              <p>{d.notice}</p>
            </div>
          )}

          {isCancelled ? (
            <div
              className="hcm-approval-blocked-note"
              style={{
                marginTop: 'var(--space-2)',
                padding: '8px 12px',
                backgroundColor: 'var(--color-surface)',
                borderRadius: '6px',
                fontSize: '13px',
                color: 'var(--color-text-secondary)',
                border: '1px solid var(--color-divider)'
              }}
            >
              <span>Resolution cancelled.</span>
            </div>
          ) : isConfirmed ? (
            <div
              className="hcm-approval-success-banner"
              style={{ marginTop: 'var(--space-2)' }}
            >
              <span>✓ Query resolved</span>
            </div>
          ) : (
            <>
              <div className="hcm-form-group" style={{ marginTop: 'var(--space-3)' }}>
                <label className="hcm-form-label" htmlFor={`resolution-note-${card.id}`}>
                  Resolution note (optional):
                </label>
                <textarea
                  id={`resolution-note-${card.id}`}
                  className="hcm-textarea"
                  rows={3}
                  placeholder="Type optional resolution note"
                  value={resolutionNote}
                  onChange={(e) => setResolutionNote(e.target.value)}
                />
              </div>

              <div className="hcm-approval-actions" style={{ marginTop: 'var(--space-3)', display: 'flex', gap: 'var(--space-2)' }}>
                <button
                  type="button"
                  className="hcm-button hcm-button-primary"
                  onClick={() => {
                    setIsConfirmed(true);
                    const note = resolutionNote.trim() || undefined;
                    if (onConfirmResolve) {
                      onConfirmResolve(qId, note);
                    } else if (onActionClick) {
                      onActionClick('confirm-resolve-query', { query_id: qId, confirmed: true, reply_text: note || null });
                    }
                  }}
                >
                  Confirm resolve
                </button>
                <button
                  type="button"
                  className="hcm-button hcm-button-secondary"
                  onClick={() => {
                    setIsCancelled(true);
                    if (onCancel) {
                      onCancel();
                    } else if (onActionClick) {
                      onActionClick('cancel');
                    }
                  }}
                >
                  Cancel
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="hcm-rich-card hcm-card-query-status" data-testid={`card-${card.id}`}>
      <div className="hcm-card-header">
        <div>
          {!isEmployee && d.query_id && <span className="hcm-tech-id">{d.query_id}</span>}
          <h4 className="hcm-card-title" style={{ marginTop: '2px' }}>{card.title}</h4>
        </div>
        <span className={`hcm-status-tag hcm-status-${status.toLowerCase().replace(/\s+/g, '-')}`}>
          {status}
        </span>
      </div>

      <div className="hcm-card-body">
        {d.description && (
          <div className="hcm-query-description-box">
            <span className="hcm-kv-label">Inquiry:</span>
            <p>{d.description}</p>
          </div>
        )}

        {(d.reply_text || d.resolution) ? (
          <div className="hcm-query-reply-box">
            <span className="hcm-kv-label">{status === 'Resolved' ? 'HR resolution reply:' : 'HR reply:'}</span>
            <p>{d.reply_text || d.resolution}</p>
          </div>
        ) : status === 'Resolved' ? (
          <div className="hcm-query-reply-box">
            <span className="hcm-kv-label">HR resolution reply:</span>
            <p>No reply was recorded before this query was resolved.</p>
          </div>
        ) : status === 'Closed' ? (
          <div className="hcm-query-reply-box">
            <span className="hcm-kv-label">HR reply:</span>
            <p>No reply was recorded before this query was closed.</p>
          </div>
        ) : null}

        {status === 'Resolved' && (d.resolved_by || d.resolved_at) && (
          <div className="hcm-card-flag-note" style={{ marginTop: 'var(--space-2)', fontSize: '13px', color: 'var(--color-text-secondary)' }}>
            {d.resolved_by && d.resolved_at
              ? `Resolved by ${d.resolved_by} on ${formatHumanDate(d.resolved_at)}`
              : d.resolved_by
              ? `Resolved by ${d.resolved_by}`
              : `Resolved on ${formatHumanDate(d.resolved_at)}`}
          </div>
        )}

        {status === 'Closed' && (d.closed_by || d.closed_at) && (
          <div className="hcm-card-flag-note" style={{ marginTop: 'var(--space-2)', fontSize: '13px', color: 'var(--color-text-secondary)' }}>
            {d.closed_by && d.closed_at
              ? `Closed by ${d.closed_by} on ${formatHumanDate(d.closed_at)}`
              : d.closed_by
              ? `Closed by ${d.closed_by}`
              : `Closed on ${formatHumanDate(d.closed_at)}`}
          </div>
        )}

        {!isEmployee && isResolveConfirmation && (
          <div style={{ marginTop: 'var(--space-3)' }}>
            {d.notice && (
              <div className="hcm-approval-notice" style={{ marginBottom: 'var(--space-2)' }}>
                <p>{d.notice}</p>
              </div>
            )}
            {isCancelled ? (
              <div
                className="hcm-approval-blocked-note"
                style={{
                  marginTop: 'var(--space-2)',
                  padding: '8px 12px',
                  backgroundColor: 'var(--color-surface)',
                  borderRadius: '6px',
                  fontSize: '13px',
                  color: 'var(--color-text-secondary)',
                  border: '1px solid var(--color-divider)'
                }}
              >
                <span>Resolution cancelled.</span>
              </div>
            ) : isConfirmed ? (
              <div
                className="hcm-approval-success-banner"
                style={{ marginTop: 'var(--space-2)' }}
              >
                <span>✓ Query resolved</span>
              </div>
            ) : (
              <>
                <div className="hcm-form-group">
                  <label className="hcm-form-label" htmlFor={`resolution-note-main-${card.id}`}>
                    Resolution note (optional):
                  </label>
                  <textarea
                    id={`resolution-note-main-${card.id}`}
                    className="hcm-textarea"
                    rows={3}
                    placeholder="Type optional resolution note"
                    value={resolutionNote}
                    onChange={(e) => setResolutionNote(e.target.value)}
                  />
                </div>

                <div className="hcm-approval-actions" style={{ marginTop: 'var(--space-3)', display: 'flex', gap: 'var(--space-2)' }}>
                  <button
                    type="button"
                    className="hcm-button hcm-button-primary"
                    onClick={() => {
                      setIsConfirmed(true);
                      const note = resolutionNote.trim() || undefined;
                      if (onConfirmResolve) {
                        onConfirmResolve(d.query_id || '', note);
                      } else if (onActionClick) {
                        onActionClick('confirm-resolve-query', { query_id: d.query_id || '', confirmed: true, reply_text: note || null });
                      }
                    }}
                  >
                    Confirm resolve
                  </button>
                  <button
                    type="button"
                    className="hcm-button hcm-button-secondary"
                    onClick={() => {
                      setIsCancelled(true);
                      if (onCancel) {
                        onCancel();
                      } else if (onActionClick) {
                        onActionClick('cancel');
                      }
                    }}
                  >
                    Cancel
                  </button>
                </div>
              </>
            )}
          </div>
        )}

        {isEmployee && status === 'Resolved' && (
          <div className="hcm-approval-actions" style={{ marginTop: 'var(--space-3)' }}>
            {onDisputeQuery && d.query_id && (
              <button
                type="button"
                className="hcm-button hcm-button-secondary hcm-button-sm"
                onClick={() => onDisputeQuery(d.query_id!)}
              >
                Dispute resolution
              </button>
            )}
            {onCloseQuery && d.query_id && (
              <button
                type="button"
                className="hcm-button hcm-button-primary hcm-button-sm"
                onClick={() => onCloseQuery(d.query_id!)}
              >
                Acknowledge and close
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
