import React from 'react';
import { formatINR } from '../../../utils/format';

interface MonthRecord {
  month: string;
  old_gross: number;
  revised_gross: number;
  diff: number;
  tds_impact?: number;
  paid_days?: number;
}

interface MonthTableCardProps {
  card: {
    id: string;
    type: string;
    title: string;
    certainty: string;
    data: {
      months: MonthRecord[];
      total_gross_arrears?: number;
    };
  };
  onShowCalculation?: () => void;
}

export const MonthTableCard: React.FC<MonthTableCardProps> = ({ card, onShowCalculation }) => {
  const { months, total_gross_arrears } = card.data;

  return (
    <div className="hcm-rich-card hcm-card-month-table" data-testid={`card-${card.id}`}>
      <div className="hcm-card-header">
        <h4 className="hcm-card-title">{card.title}</h4>
        {total_gross_arrears !== undefined && (
          <span className="hcm-total-badge">
            Total Gross Arrears: <strong className="tnum">{formatINR(total_gross_arrears)}</strong>
          </span>
        )}
      </div>

      <div className="hcm-table-container">
        <table className="hcm-table">
          <thead>
            <tr>
              <th scope="col">Month</th>
              <th scope="col" style={{ textAlign: 'right' }}>Old Gross</th>
              <th scope="col" style={{ textAlign: 'right' }}>Revised Gross</th>
              <th scope="col" style={{ textAlign: 'right' }}>Arrears Diff</th>
              <th scope="col" style={{ textAlign: 'right' }}>Monthly TDS</th>
            </tr>
          </thead>
          <tbody>
            {months.map((m) => (
              <tr key={m.month}>
                <td className="tnum" style={{ fontWeight: 'var(--font-weight-medium)' }}>{m.month}</td>
                <td className="tnum" style={{ textAlign: 'right' }}>{formatINR(m.old_gross)}</td>
                <td className="tnum" style={{ textAlign: 'right' }}>{formatINR(m.revised_gross)}</td>
                <td className="tnum" style={{ textAlign: 'right', fontWeight: 'var(--font-weight-semibold)', color: 'var(--color-brand-accent)' }}>
                  {formatINR(m.diff)}
                </td>
                <td className="tnum" style={{ textAlign: 'right' }}>
                  {m.tds_impact !== undefined ? formatINR(m.tds_impact) : '—'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {onShowCalculation && (
        <div className="hcm-card-footer-action">
          <button
            type="button"
            className="hcm-button hcm-button-outline hcm-button-sm"
            onClick={onShowCalculation}
          >
            Show calculation & full month breakdown →
          </button>
        </div>
      )}
    </div>
  );
};
