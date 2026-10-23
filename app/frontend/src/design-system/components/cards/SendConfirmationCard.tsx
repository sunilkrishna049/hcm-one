import React from 'react';
import { CheckCircle2 } from 'lucide-react';

interface SendConfirmationCardProps {
  card: {
    id: string;
    type: string;
    title: string;
    certainty: string;
    data: {
      query_id: string;
      status: string;
      status_message: string;
    };
  };
}

export const SendConfirmationCard: React.FC<SendConfirmationCardProps> = ({ card }) => {
  const d = card.data;

  return (
    <div className="hcm-rich-card hcm-card-send-conf" data-testid={`card-${card.id}`}>
      <div className="hcm-send-conf-header">
        <CheckCircle2 color="var(--color-brand-accent)" size={24} />
        <div>
          <h4 className="hcm-card-title">{card.title}</h4>
          <span className="hcm-tech-id" style={{ marginTop: '2px', display: 'inline-block' }}>
            {d.query_id}
          </span>
        </div>
      </div>
      <div className="hcm-card-body" style={{ marginTop: 'var(--space-2)' }}>
        <p style={{ margin: 0, color: 'var(--color-text-primary)' }}>{d.status_message}</p>
      </div>
    </div>
  );
};
