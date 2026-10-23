import React, { useEffect, useRef } from 'react';
import { X, FileText, CheckCircle2 } from 'lucide-react';
import { formatINR } from '../../../utils/format';

export interface PanelHRData {
  title?: string;
  employee_name?: string;
  employee_id?: string;
  months?: Array<{
    month: string;
    old_gross?: number;
    revised_gross?: number;
    diff?: number;
    pf_change?: number;
    tds_impact?: number;
    paid_days?: number;
  }>;
  components?: Array<{
    label: string;
    amount?: number | null;
    status?: string;
    note?: string;
  }>;
  formulas?: string[];
  rule_citations?: string[];
  notes?: string[];
}

interface PanelHRProps {
  isOpen: boolean;
  onClose: () => void;
  data?: PanelHRData | null;
}

export const PanelHR: React.FC<PanelHRProps> = ({ isOpen, onClose, data }) => {
  const closeBtnRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (isOpen) {
      closeBtnRef.current?.focus();
    }
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const title = data?.title || 'Calculation Proof & Month Breakdown';
  const months = data?.months || [];
  const components = data?.components || [];
  const formulas = data?.formulas || [];
  const ruleCitations = data?.rule_citations || [];

  return (
    <aside
      className="hcm-panel-hr-root"
      data-testid="panel-hr"
      role="complementary"
      aria-label={title}
    >
      {/* Header */}
      <div className="hcm-panel-header">
        <div>
          <h2 className="hcm-panel-title">{title}</h2>
          {data?.employee_name && (
            <p className="hcm-panel-subtitle">
              {data.employee_name} ({data.employee_id})
            </p>
          )}
        </div>
        <button
          ref={closeBtnRef}
          type="button"
          onClick={onClose}
          className="hcm-panel-close-btn"
          data-testid="panel-close-btn"
          aria-label="Close review panel"
        >
          <X size={20} />
        </button>
      </div>

      {/* Content Body */}
      <div className="hcm-panel-body">
        {/* Multi-month Breakdown Table */}
        {months.length > 0 && (
          <section className="hcm-panel-section" aria-label="Month-by-month breakdown">
            <h3 className="hcm-panel-section-title">Month-by-Month Breakdown</h3>
            <div className="hcm-panel-table-wrapper">
              <table className="hcm-panel-table">
                <thead>
                  <tr>
                    <th>Month</th>
                    <th className="hcm-num-cell">Old Gross</th>
                    <th className="hcm-num-cell">Revised</th>
                    <th className="hcm-num-cell">Arrears</th>
                    <th className="hcm-num-cell">PF Diff</th>
                    <th className="hcm-num-cell">TDS</th>
                    <th className="hcm-num-cell">Paid</th>
                  </tr>
                </thead>
                <tbody>
                  {months.map((m, idx) => (
                    <tr key={idx}>
                      <td className="hcm-tnum" style={{ fontWeight: 500 }}>{m.month}</td>
                      <td className="hcm-num-cell hcm-tnum">{formatINR(m.old_gross)}</td>
                      <td className="hcm-num-cell hcm-tnum">{formatINR(m.revised_gross)}</td>
                      <td className="hcm-num-cell hcm-tnum" style={{ fontWeight: 600 }}>{formatINR(m.diff)}</td>
                      <td className="hcm-num-cell hcm-tnum">{formatINR(m.pf_change)}</td>
                      <td className="hcm-num-cell hcm-tnum">{formatINR(m.tds_impact)}</td>
                      <td className="hcm-num-cell hcm-tnum">{m.paid_days ?? '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        )}

        {/* Settlement Components List */}
        {components.length > 0 && (
          <section className="hcm-panel-section" aria-label="Settlement components">
            <h3 className="hcm-panel-section-title">Settlement Breakdown</h3>
            <div className="hcm-panel-components-list">
              {components.map((c, idx) => (
                <div key={idx} className="hcm-panel-comp-row">
                  <div>
                    <span className="hcm-panel-comp-label">{c.label}</span>
                    {c.note && <span className="hcm-panel-comp-note">{c.note}</span>}
                  </div>
                  <div className="hcm-panel-comp-right">
                    <span className="hcm-panel-comp-amount hcm-tnum">
                      {c.amount !== null && c.amount !== undefined ? formatINR(c.amount) : 'Pending clearance'}
                    </span>
                    {c.status && (
                      <span className={`hcm-badge hcm-badge-${c.status.toLowerCase()}`}>
                        {c.status}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Plain-Language Formulas */}
        {formulas.length > 0 && (
          <section className="hcm-panel-section" aria-label="Plain-language formulas">
            <h3 className="hcm-panel-section-title">Plain-Language Formulas</h3>
            <div className="hcm-panel-formulas-box">
              {formulas.map((f, idx) => (
                <div key={idx} className="hcm-panel-formula-item">
                  <span className="hcm-formula-bullet">•</span>
                  <p className="hcm-formula-text">{f}</p>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Human-Readable Rule Citations */}
        {ruleCitations.length > 0 && (
          <section className="hcm-panel-section" aria-label="Rule citations">
            <h3 className="hcm-panel-section-title">Statutory & Company Rule Citations</h3>
            <div className="hcm-panel-citations-box">
              {ruleCitations.map((cite, idx) => (
                <div key={idx} className="hcm-panel-citation-item">
                  <FileText size={14} className="hcm-citation-icon" />
                  <p className="hcm-citation-text">{cite}</p>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Audit / Policy Notice */}
        <div className="hcm-panel-footer-note">
          <CheckCircle2 size={14} color="var(--brand-accent)" />
          <span>Every number originates from verified rules in the engine. Display only.</span>
        </div>
      </div>
    </aside>
  );
};
