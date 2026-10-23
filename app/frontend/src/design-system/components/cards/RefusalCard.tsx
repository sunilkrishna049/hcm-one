import React from 'react';
import { ShieldAlert } from 'lucide-react';

interface RefusalCardProps {
  card: {
    id: string;
    type: string;
    title: string;
    certainty: string;
    data: {
      message?: string;
      reason?: string;
    };
  };
}

export const RefusalCard: React.FC<RefusalCardProps> = ({ card }) => {
  const d = card.data;

  return (
    <div
      className="hcm-rich-card hcm-card-refusal"
      data-testid={`card-${card.id}`}
      style={{
        borderColor: 'var(--color-status-error-border)',
        backgroundColor: 'var(--color-status-error-surface)',
      }}
    >
      <div className="hcm-refusal-header" style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
        <ShieldAlert size={20} color="var(--color-status-error-text)" />
        <h4 className="hcm-card-title" style={{ color: 'var(--color-status-error-text)', margin: 0 }}>
          {card.title}
        </h4>
      </div>
      <div className="hcm-card-body" style={{ marginTop: 'var(--space-2)' }}>
        <p style={{ margin: 0, color: 'var(--color-text-primary)', fontWeight: 500 }}>
          {d.message ||
            'I cannot provide that information. I can help with payroll records you are authorized to access.'}
        </p>
      </div>
    </div>
  );
};
