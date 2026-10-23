import React, { useState } from 'react';

interface QueryDraftCardProps {
  card: {
    id: string;
    type: string;
    title: string;
    certainty: string;
    data: {
      draft: {
        category: string;
        months: string[];
        description: string;
        evidence: Array<{ type: string; source: string; period?: string }>;
      };
      notice?: string;
      actions?: string[];
    };
  };
  onSendQuery?: (description: string) => void;
  onCancel?: () => void;
}

export const QueryDraftCard: React.FC<QueryDraftCardProps> = ({
  card,
  onSendQuery,
  onCancel,
}) => {
  const { draft, notice } = card.data;
  const [description, setDescription] = useState(draft.description || '');

  return (
    <div className="hcm-rich-card hcm-card-query-draft" data-testid={`card-${card.id}`}>
      <div className="hcm-card-header">
        <div>
          <span className="hcm-card-type-badge">Flow 6 Query Draft</span>
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
            <span className="hcm-kv-label">Target Months</span>
            <span className="tnum">{draft.months.join(', ')}</span>
          </div>
        </div>

        <div className="hcm-form-group" style={{ marginTop: 'var(--space-3)' }}>
          <label className="hcm-form-label">Employee Inquiry Description:</label>
          <textarea
            className="hcm-textarea"
            rows={3}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
        </div>

        {/* Attached Evidence List */}
        <div className="hcm-evidence-section" style={{ marginTop: 'var(--space-3)' }}>
          <span className="hcm-kv-label">Attached Sourced Evidence:</span>
          <ul className="hcm-evidence-list">
            {draft.evidence.map((ev, i) => (
              <li key={i} className="hcm-evidence-item">
                <span className="hcm-tech-id">{ev.source}</span>
                <span style={{ color: 'var(--color-text-secondary)', fontSize: '13px', marginLeft: 'var(--space-2)' }}>
                  ({ev.type})
                </span>
              </li>
            ))}
          </ul>
        </div>

        {/* Sentence C12 Notice */}
        <div className="hcm-approval-notice" style={{ marginTop: 'var(--space-3)' }}>
          <p>{notice || 'Send this query with the listed evidence to HR?'}</p>
        </div>

        <div className="hcm-approval-actions" style={{ marginTop: 'var(--space-3)' }}>
          <button
            type="button"
            className="hcm-button hcm-button-primary"
            onClick={() => onSendQuery && onSendQuery(description)}
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
