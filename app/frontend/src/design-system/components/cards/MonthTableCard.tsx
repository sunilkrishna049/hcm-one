import React from 'react';
import { formatINR, formatHumanDate } from '../../../utils/format';

interface MonthRecord {
  month: string;
  old_gross: number;
  revised_gross: number;
  diff: number;
  tds_impact?: number;
  paid_days?: number;
  lop_days?: number;
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

export const MonthTableCard: React.FC<MonthTableCardProps> = ({ card }) => {
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
            {months.map((m) => {
              const formattedMonth = formatHumanDate(m.month);
              const hasLop = m.lop_days !== undefined && m.lop_days > 0;
              return (
                <tr key={m.month}>
                  <td className="tnum" data-label="Month" style={{ fontWeight: 'var(--font-weight-medium)' }}>
                    <span>{formattedMonth}</span>
                    {hasLop && (
                      <span style={{ fontSize: '12px', color: 'var(--color-status-warning-text)', marginLeft: '6px', fontWeight: 'var(--font-weight-semibold)' }}>
                        · {m.lop_days} LOP days
                      </span>
                    )}
                  </td>
                  <td className="tnum" data-label="Old Gross" style={{ textAlign: 'right' }}>{formatINR(m.old_gross)}</td>
                  <td className="tnum" data-label="Revised Gross" style={{ textAlign: 'right' }}>{formatINR(m.revised_gross)}</td>
                  <td className="tnum" data-label="Arrears Diff" style={{ textAlign: 'right', fontWeight: 'var(--font-weight-semibold)', color: 'var(--color-brand-accent)' }}>
                    {formatINR(m.diff)}
                  </td>
                  <td className="tnum" data-label="Monthly TDS" style={{ textAlign: 'right' }}>
                    {m.tds_impact !== undefined ? formatINR(m.tds_impact) : '—'}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};
