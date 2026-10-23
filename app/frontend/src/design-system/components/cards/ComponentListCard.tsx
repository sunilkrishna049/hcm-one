import React from 'react';
import { CertaintyLabel } from '../CertaintyLabel';
import { formatINR } from '../../../utils/format';

interface SettlementComponent {
  name: string;
  amount: number | null;
  status: 'Eligible' | 'Ineligible' | 'Unresolved' | 'Verified' | string;
  note?: string;
}

interface ComponentListCardProps {
  card: {
    id: string;
    type: string;
    title: string;
    certainty: string;
    data: {
      hero_label?: string;
      hero_amount?: number | null;
      gross_payables?: number | null;
      total_deductions?: number | null;
      known_recoveries_subtotal?: number | null;
      components: SettlementComponent[];
      due_date?: string;
    };
  };
  onShowCalculation?: () => void;
}

export const ComponentListCard: React.FC<ComponentListCardProps> = ({ card, onShowCalculation }) => {
  const d = card.data;

  return (
    <div className="hcm-rich-card hcm-card-component-list" data-testid={`card-${card.id}`}>
      <div className="hcm-card-header">
        <div>
          <h4 className="hcm-card-title">{card.title}</h4>
          {d.due_date && (
            <span className="hcm-due-date-pill tnum">
              Due Date: {d.due_date}
            </span>
          )}
        </div>
        <CertaintyLabel certainty={card.certainty} />
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
              <span>Gross Payables: <strong className="tnum">{formatINR(d.gross_payables)}</strong></span>
              <span style={{ margin: '0 var(--space-2)' }}>•</span>
              <span>Total Deductions: <strong className="tnum">{formatINR(d.total_deductions)}</strong></span>
            </div>
          )}
          {d.known_recoveries_subtotal !== undefined && (
            <div className="hcm-hero-sublabel">
              <span>Known Recoveries Subtotal: <strong className="tnum">{formatINR(d.known_recoveries_subtotal)}</strong></span>
            </div>
          )}
        </div>
      )}

      {/* Component Rows */}
      <div className="hcm-component-table">
        {d.components.map((comp, idx) => (
          <div key={idx} className="hcm-component-row">
            <div className="hcm-comp-name-col">
              <strong>{comp.name}</strong>
              {comp.note && <div className="hcm-comp-note">{comp.note}</div>}
            </div>
            <div className="hcm-comp-status-col">
              <span className={`hcm-comp-status-badge hcm-status-${comp.status.toLowerCase()}`}>
                {comp.status}
              </span>
            </div>
            <div className="hcm-comp-amount-col tnum">
              {formatINR(comp.amount)}
            </div>
          </div>
        ))}
      </div>

      {onShowCalculation && (
        <div className="hcm-card-footer-action">
          <button
            type="button"
            className="hcm-button hcm-button-outline hcm-button-sm"
            onClick={onShowCalculation}
          >
            Show calculation proof →
          </button>
        </div>
      )}
    </div>
  );
};
