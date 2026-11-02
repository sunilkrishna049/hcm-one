import React from 'react';
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
    certainty: string;
    role?: string;
    data: {
      query_id?: string;
      role?: string;
      closed_by?: string;
      closed_at?: string;
      status?: string;
      category?: string;
      description?: string;
      reply_text?: string;
      resolution?: string;
      queries?: QueryItem[];
    };
  };
  onTakeIntoReview?: (queryId: string) => void;
  onResolveQuery?: (queryId: string) => void;
  onDisputeQuery?: (queryId: string) => void;
  onCloseQuery?: (queryId: string) => void;
}

export const QueryStatusCard: React.FC<QueryStatusCardProps> = ({
  role: propRole,
  card,
  onTakeIntoReview,
  onResolveQuery,
  onDisputeQuery,
  onCloseQuery,
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
        ) : status === 'Closed' ? (
          <div className="hcm-query-reply-box">
            <span className="hcm-kv-label">HR reply:</span>
            <p>No reply was recorded before this query was closed.</p>
          </div>
        ) : null}

        {status === 'Closed' && (d.closed_by || d.closed_at) && (
          <div className="hcm-card-flag-note" style={{ marginTop: 'var(--space-2)', fontSize: '13px', color: 'var(--color-text-secondary)' }}>
            {d.closed_by && d.closed_at
              ? `Closed by ${d.closed_by} on ${formatHumanDate(d.closed_at)}`
              : d.closed_by
              ? `Closed by ${d.closed_by}`
              : `Closed on ${formatHumanDate(d.closed_at)}`}
          </div>
        )}

        {status === 'Resolved' && (
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
