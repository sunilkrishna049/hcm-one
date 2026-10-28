import React from 'react';
import { formatINR } from '../../../utils/format';

interface ReasonItem {
  cause: string;
  detail: string;
  amount: number;
}

interface ReasonListCardProps {
  card: {
    id: string;
    type: string;
    title: string;
    certainty: string;
    data: {
      net_change?: number | null;
      reasons: ReasonItem[];
      tds_change?: number | null;
    };
  };
  onShowCalculation?: () => void;
}

export const ReasonListCard: React.FC<ReasonListCardProps> = ({ card }) => {
  const { net_change, reasons, tds_change } = card.data;

  return (
    <div className="hcm-rich-card hcm-card-reason-list" data-testid={`card-${card.id}`}>
      <div className="hcm-card-header">
        <h4 className="hcm-card-title">{card.title}</h4>
        {net_change !== undefined && net_change !== null && (
          <span className="hcm-net-change-pill tnum">
            Net change: {formatINR(net_change)}
          </span>
        )}
      </div>

      <div className="hcm-reasons-list">
        {reasons.map((r, idx) => (
          <div key={idx} className="hcm-reason-item">
            <div className="hcm-reason-index">{idx + 1}</div>
            <div className="hcm-reason-content">
              <strong className="hcm-reason-cause">{r.cause}</strong>
              <span className="hcm-reason-detail">{r.detail}</span>
            </div>
            <div className="hcm-reason-amount tnum" style={{ color: r.amount < 0 ? 'var(--color-status-error-text)' : 'var(--color-text-primary)' }}>
              {formatINR(r.amount)}
            </div>
          </div>
        ))}

        {tds_change !== undefined && tds_change !== null && (
          <div className="hcm-reason-footnote">
            <span>TDS change: <strong className="tnum">{formatINR(tds_change)}</strong></span>
          </div>
        )}
      </div>
    </div>
  );
};
