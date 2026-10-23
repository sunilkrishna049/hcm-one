import React from 'react';
import { CertaintyLabel } from '../CertaintyLabel';
import { formatINR } from '../../../utils/format';

interface NumberCardsClusterProps {
  card: {
    id: string;
    type: string;
    title: string;
    certainty: string;
    data: {
      hero_label?: string;
      hero_amount?: number | null;
      net_change?: number | null;
      previous_month_label?: string;
      previous_month_amount?: number | null;
      gross_arrears?: number | null;
      employee_pf_change?: number | null;
      estimated_tds_impact?: number | null;
      arrears_only_tds_impact?: number | null;
      recurring_salary_tds_impact?: number | null;
      tds_increase?: number | null;
      august_diff?: number | null;
      september_diff?: number | null;
      payment_month?: string;
      estimate_flag?: string;
      earnings_status?: string;
      note?: string;
    };
  };
  onShowCalculation?: () => void;
}

export const NumberCardsCluster: React.FC<NumberCardsClusterProps> = ({ card, onShowCalculation }) => {
  const d = card.data;

  return (
    <div className="hcm-rich-card hcm-card-number-cluster" data-testid={`card-${card.id}`}>
      {card.title && (
        <div className="hcm-card-header" style={{ marginBottom: 'var(--space-2)' }}>
          <h4 className="hcm-card-title">{card.title}</h4>
        </div>
      )}
      {/* Hero Number Card */}
      {d.hero_label && (
        <div className="hcm-hero-number-box">
          <div className="hcm-hero-header">
            <span className="hcm-hero-label">{d.hero_label}</span>
            <CertaintyLabel certainty={card.certainty} />
          </div>
          <div className="hcm-hero-amount-row">
            <span className="hcm-hero-amount tnum" data-testid="hero-amount">
              {formatINR(d.hero_amount)}
            </span>
          </div>

          {/* Month comparison subtitle if available */}
          {d.previous_month_label && d.previous_month_amount !== undefined && (
            <div className="hcm-hero-sublabel">
              <span>{d.previous_month_label}: </span>
              <strong className="tnum">{formatINR(d.previous_month_amount)}</strong>
              {d.net_change !== undefined && d.net_change !== null && (
                <span className="hcm-net-change-pill tnum" style={{ marginLeft: 'var(--space-2)' }}>
                  Change: {formatINR(d.net_change)}
                </span>
              )}
            </div>
          )}

          {d.tds_increase !== undefined && d.tds_increase !== null && (
            <div className="hcm-hero-sublabel">
              <span>Monthly TDS Increase: </span>
              <strong className="tnum" style={{ color: 'var(--color-status-error-text)' }}>
                +{formatINR(d.tds_increase)}
              </strong>
            </div>
          )}

          {d.earnings_status && (
            <div className="hcm-info-banner">
              <span>{d.earnings_status}</span>
            </div>
          )}
        </div>
      )}

      {/* Secondary Grid Numbers */}
      {(d.gross_arrears !== undefined || d.employee_pf_change !== undefined || d.estimated_tds_impact !== undefined) && (
        <div className="hcm-secondary-grid">
          <div className="hcm-grid-stat">
            <span className="hcm-stat-label">Gross Arrears</span>
            <span className="hcm-stat-value tnum">{formatINR(d.gross_arrears)}</span>
          </div>
          <div className="hcm-grid-stat">
            <span className="hcm-stat-label">PF Change</span>
            <span className="hcm-stat-value tnum">{formatINR(d.employee_pf_change)}</span>
          </div>
          <div className="hcm-grid-stat">
            <span className="hcm-stat-label">Estimated TDS</span>
            <span className="hcm-stat-value tnum">{formatINR(d.estimated_tds_impact)}</span>
          </div>
        </div>
      )}

      {/* Monthly diffs when incomplete */}
      {(d.august_diff !== undefined || d.september_diff !== undefined) && (
        <div className="hcm-secondary-grid">
          <div className="hcm-grid-stat">
            <span className="hcm-stat-label">August Arrears Diff</span>
            <span className="hcm-stat-value tnum">{formatINR(d.august_diff)}</span>
          </div>
          <div className="hcm-grid-stat">
            <span className="hcm-stat-label">September Arrears Diff</span>
            <span className="hcm-stat-value tnum">{formatINR(d.september_diff)}</span>
          </div>
        </div>
      )}

      {/* Footnote flag if present */}
      {d.estimate_flag && (
        <div className="hcm-card-flag-note">
          <span>ℹ {d.estimate_flag}</span>
        </div>
      )}

      {/* Action link */}
      {onShowCalculation && (
        <div className="hcm-card-action-row">
          <button
            type="button"
            className="hcm-button hcm-button-outline hcm-button-sm"
            onClick={onShowCalculation}
            aria-label="Show calculation proof"
          >
            Show calculation →
          </button>
        </div>
      )}
    </div>
  );
};
