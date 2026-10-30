import React from 'react';
import { formatINR, formatHumanDate } from '../../../utils/format';

interface SettlementComponent {
  name?: string;
  label?: string;
  name_code?: string;
  amount?: number | null;
  status?: 'Eligible' | 'Ineligible' | 'Unresolved' | 'Verified' | string;
  note?: string;
  reason?: string;
  blocked_reason?: string;
}

interface ComponentListCardProps {
  card: {
    id: string;
    type: string;
    title: string;
    certainty?: string;
    data: {
      hero_label?: string;
      hero_amount?: number | null;
      gross_payables?: number | null;
      total_deductions?: number | null;
      known_recoveries_subtotal?: number | null;
      known_recoveries?: number | null;
      components?: SettlementComponent[];
      items?: SettlementComponent[];
      due_date?: string;
    };
  };
  onShowCalculation?: () => void;
}

export const ComponentListCard: React.FC<ComponentListCardProps> = ({ card }) => {
  const d = card.data;
  const rawRows = (d.items && d.items.length > 0) ? d.items : (d.components || []);

  const displayRows = rawRows.map((r) => ({
    name: r.label || r.name_code || r.name || '',
    note: r.note || r.reason || r.blocked_reason || '',
    status: r.status || '',
    amount: r.amount,
  }));

  return (
    <div className="hcm-rich-card hcm-card-component-list" data-testid={`card-${card.id}`}>
      <div className="hcm-card-header">
        <div>
          <h4 className="hcm-card-title">{card.title}</h4>
          {d.due_date && (
            <span className="hcm-due-date-pill tnum">
              Due date: {formatHumanDate(d.due_date)}
            </span>
          )}
        </div>
      </div>

      {/* Hero Final Net Settlement if applicable */}
      {d.hero_label && (
        <div className="hcm-hero-number-box" style={{ marginBottom: 'var(--space-3)' }}>
          <span className="hcm-hero-label">{d.hero_label}</span>
          <div className="hcm-hero-amount tnum" data-testid="hero-amount">
            {formatINR(d.hero_amount)}
          </div>
          {(d.gross_payables !== undefined || d.total_deductions !== undefined) && (
            <div className="hcm-hero-sublabel">
              <span>Gross payables: <strong className="tnum">{formatINR(d.gross_payables)}</strong></span>
              <span style={{ margin: '0 var(--space-2)' }}>•</span>
              <span>Total deductions: <strong className="tnum">{formatINR(d.total_deductions)}</strong></span>
            </div>
          )}
          {(d.known_recoveries !== undefined || d.known_recoveries_subtotal !== undefined) && (
            <div className="hcm-hero-sublabel">
              <span>Known recoveries: <strong className="tnum">{formatINR(d.known_recoveries ?? d.known_recoveries_subtotal)}</strong></span>
            </div>
          )}
        </div>
      )}

      {/* Component Rows */}
      <div className="hcm-component-table">
        {displayRows.map((comp, idx) => (
          <div key={idx} className="hcm-component-row">
            <div className="hcm-comp-name-col">
              <strong>{comp.name}</strong>
              {comp.note && <div className="hcm-comp-note">{comp.note}</div>}
            </div>
            {comp.status && (
              <div className="hcm-comp-status-col">
                <span className={`hcm-comp-status-badge hcm-status-${comp.status.toLowerCase().replace(/\s+/g, '-')}`}>
                  {comp.status}
                </span>
              </div>
            )}
            {comp.amount !== null && comp.amount !== undefined && (
              <div className="hcm-comp-amount-col tnum">
                {formatINR(comp.amount)}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
