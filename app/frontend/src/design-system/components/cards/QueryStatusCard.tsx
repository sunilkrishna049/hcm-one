import React from 'react';

interface QueryItem {
  query_id: string;
  status: 'Draft' | 'Sent' | 'In review' | 'Resolved' | 'Closed' | string;
  category?: string;
  description?: string;
  reply_text?: string;
  resolution?: string;
}

interface QueryStatusCardProps {
  card: {
    id: string;
    type: string;
    title: string;
    certainty: string;
    data: {
      query_id?: string;
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

  return (
    <div className="hcm-rich-card hcm-card-query-status" data-testid={`card-${card.id}`}>
      <div className="hcm-card-header">
        <div>
          <span className="hcm-tech-id">{d.query_id}</span>
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

        {(d.reply_text || d.resolution) && (
          <div className="hcm-query-reply-box">
            <span className="hcm-kv-label">HR Resolution Reply:</span>
            <p>{d.reply_text || d.resolution}</p>
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
