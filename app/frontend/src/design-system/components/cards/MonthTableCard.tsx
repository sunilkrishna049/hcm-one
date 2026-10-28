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
      months?: MonthRecord[];
      total_gross_arrears?: number;
      gross_pay?: number;
      basic?: number;
      hra?: number;
      special_allowance?: number;
      da?: number;
      pf?: number;
      tds?: number;
      total_deductions?: number;
      net_pay?: number;
      [key: string]: any;
    };
  };
  onShowCalculation?: () => void;
}

export const MonthTableCard: React.FC<MonthTableCardProps> = ({ card }) => {
  const d = card.data || {};
  const { months, total_gross_arrears } = d;

  if (!months || !Array.isArray(months)) {
    return (
      <div className="hcm-rich-card hcm-card-month-table" data-testid={`card-${card.id}`}>
        <div className="hcm-card-header">
          <h4 className="hcm-card-title">{card.title}</h4>
        </div>
        <div className="hcm-table-container">
          <table className="hcm-table hcm-payslip-table">
            <tbody>
              {/* Earnings Section */}
              <tr className="hcm-payslip-section-row">
                <td colSpan={2} className="hcm-payslip-section-title">Earnings</td>
              </tr>
              {d.basic !== undefined && (
                <tr className="hcm-payslip-row">
                  <td className="hcm-payslip-label">Basic pay</td>
                  <td className="hcm-payslip-val tnum">{formatINR(d.basic)}</td>
                </tr>
              )}
              {d.hra !== undefined && (
                <tr className="hcm-payslip-row">
                  <td className="hcm-payslip-label">HRA</td>
                  <td className="hcm-payslip-val tnum">{formatINR(d.hra)}</td>
                </tr>
              )}
              {d.special_allowance !== undefined && (
                <tr className="hcm-payslip-row">
                  <td className="hcm-payslip-label">Special allowance</td>
                  <td className="hcm-payslip-val tnum">{formatINR(d.special_allowance)}</td>
                </tr>
              )}
              {d.da !== undefined && (
                <tr className="hcm-payslip-row">
                  <td className="hcm-payslip-label">DA</td>
                  <td className="hcm-payslip-val tnum">{formatINR(d.da)}</td>
                </tr>
              )}
              {d.gross_pay !== undefined && (
                <tr className="hcm-payslip-subtotal-row">
                  <td className="hcm-payslip-label-bold">Gross pay</td>
                  <td className="hcm-payslip-val-bold tnum">{formatINR(d.gross_pay)}</td>
                </tr>
              )}

              {/* Deductions Section */}
              <tr className="hcm-payslip-section-row">
                <td colSpan={2} className="hcm-payslip-section-title">Deductions</td>
              </tr>
              {d.pf !== undefined && (
                <tr className="hcm-payslip-row">
                  <td className="hcm-payslip-label">PF</td>
                  <td className="hcm-payslip-val tnum">{formatINR(d.pf)}</td>
                </tr>
              )}
              {d.tds !== undefined && (
                <tr className="hcm-payslip-row">
                  <td className="hcm-payslip-label">TDS</td>
                  <td className="hcm-payslip-val tnum">{formatINR(d.tds)}</td>
                </tr>
              )}
              {d.total_deductions !== undefined && (
                <tr className="hcm-payslip-subtotal-row">
                  <td className="hcm-payslip-label-bold">Total deductions</td>
                  <td className="hcm-payslip-val-bold tnum">{formatINR(d.total_deductions)}</td>
                </tr>
              )}

              {/* Net Pay */}
              {d.net_pay !== undefined && (
                <tr className="hcm-payslip-net-row">
                  <td className="hcm-payslip-net-label">Net pay</td>
                  <td className="hcm-payslip-net-val tnum">{formatINR(d.net_pay)}</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    );
  }

  return (
    <div className="hcm-rich-card hcm-card-month-table" data-testid={`card-${card.id}`}>
      <div className="hcm-card-header">
        <h4 className="hcm-card-title">{card.title}</h4>
        {total_gross_arrears !== undefined && (
          <span className="hcm-total-badge">
            Total gross arrears: <strong className="tnum">{formatINR(total_gross_arrears)}</strong>
          </span>
        )}
      </div>

      <div className="hcm-table-container">
        <table className="hcm-table">
          <thead>
            <tr>
              <th scope="col">Month</th>
              <th scope="col" className="hcm-text-right">Old gross</th>
              <th scope="col" className="hcm-text-right">Revised gross</th>
              <th scope="col" className="hcm-text-right">Arrears</th>
              <th scope="col" className="hcm-text-right">Monthly TDS</th>
            </tr>
          </thead>
          <tbody>
            {months.map((m) => {
              const formattedMonth = formatHumanDate(m.month);
              const hasLop = m.lop_days !== undefined && m.lop_days > 0;
              return (
                <tr key={m.month}>
                  <td className="tnum hcm-month-cell" data-label="Month">
                    <span>{formattedMonth}</span>
                    {hasLop && (
                      <span className="hcm-lop-badge">
                        · {m.lop_days} LOP days
                      </span>
                    )}
                  </td>
                  <td className="tnum hcm-text-right" data-label="Old gross">{formatINR(m.old_gross)}</td>
                  <td className="tnum hcm-text-right" data-label="Revised gross">{formatINR(m.revised_gross)}</td>
                  <td className="tnum hcm-cell-arrears" data-label="Arrears">
                    {formatINR(m.diff)}
                  </td>
                  <td className="tnum hcm-text-right" data-label="Monthly TDS">
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
