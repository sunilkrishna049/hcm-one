import React from 'react';
import * as Dialog from '@radix-ui/react-dialog';
import { X, FileText, CheckCircle2 } from 'lucide-react';
import { formatINR } from '../../../utils/format';

export interface SheetEMPData {
  title?: string;
  comparison?: {
    before?: {
      month: string;
      gross?: number;
      deductions?: number;
      net?: number;
      paid_days?: number;
    };
    after?: {
      month: string;
      gross?: number;
      deductions?: number;
      net?: number;
      paid_days?: number;
      calendar_days?: number;
      lop_days?: number;
    };
  };
  formulas?: string[];
  rule_citations?: string[];
}

interface SheetEMPProps {
  isOpen: boolean;
  onClose: () => void;
  data?: SheetEMPData | null;
}

export const SheetEMP: React.FC<SheetEMPProps> = ({ isOpen, onClose, data }) => {
  const title = data?.title || 'Calculation proof';
  const comparison = data?.comparison;
  const formulas = data?.formulas || [];
  const ruleCitations = data?.rule_citations || [];

  return (
    <Dialog.Root open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <Dialog.Portal>
        <Dialog.Overlay className="hcm-sheet-overlay" />
        <Dialog.Content
          className="hcm-sheet-emp-content"
          data-testid="sheet-emp"
          aria-describedby="sheet-emp-desc"
        >
          {/* Mobile Drag Handle */}
          <div className="hcm-sheet-drag-handle" aria-hidden="true" />

          {/* Header */}
          <div className="hcm-sheet-header">
            <div>
              <Dialog.Title className="hcm-sheet-title">{title}</Dialog.Title>
              <Dialog.Description id="sheet-emp-desc" className="hcm-sheet-subtitle">
                Calculation breakdown and rule evidence
              </Dialog.Description>
            </div>
            <Dialog.Close asChild>
              <button
                type="button"
                className="hcm-sheet-close-btn"
                data-testid="sheet-close-btn"
                aria-label="Close calculation sheet"
                onClick={onClose}
              >
                <X size={20} />
              </button>
            </Dialog.Close>
          </div>

          {/* Body */}
          <div className="hcm-sheet-body">
            {/* Pay Comparison */}
            {comparison?.before && comparison?.after && (
              <section className="hcm-sheet-section">
                <h4 className="hcm-sheet-section-title">Pay comparison breakdown</h4>
                <div className="hcm-sheet-comparison-grid">
                  <div className="hcm-comparison-col">
                    <span className="hcm-comparison-month">{comparison.before.month}</span>
                    <div className="hcm-comparison-row">
                      <span>Gross:</span>
                      <strong className="hcm-tnum">{formatINR(comparison.before.gross)}</strong>
                    </div>
                    <div className="hcm-comparison-row">
                      <span>Deductions:</span>
                      <strong className="hcm-tnum">{formatINR(comparison.before.deductions)}</strong>
                    </div>
                    <div className="hcm-comparison-row hcm-comparison-net">
                      <span>Net:</span>
                      <strong className="hcm-tnum">{formatINR(comparison.before.net)}</strong>
                    </div>
                    <div className="hcm-comparison-row">
                      <span>Paid days:</span>
                      <strong className="hcm-tnum">{comparison.before.paid_days ?? '—'}</strong>
                    </div>
                  </div>

                  <div className="hcm-comparison-col">
                    <span className="hcm-comparison-month">{comparison.after.month}</span>
                    <div className="hcm-comparison-row">
                      <span>Gross:</span>
                      <strong className="hcm-tnum">{formatINR(comparison.after.gross)}</strong>
                    </div>
                    <div className="hcm-comparison-row">
                      <span>Deductions:</span>
                      <strong className="hcm-tnum">{formatINR(comparison.after.deductions)}</strong>
                    </div>
                    <div className="hcm-comparison-row hcm-comparison-net">
                      <span>Net:</span>
                      <strong className="hcm-tnum">{formatINR(comparison.after.net)}</strong>
                    </div>
                    <div className="hcm-comparison-row">
                      <span>Paid days:</span>
                      <strong className="hcm-tnum">
                        {comparison.after.paid_days ?? '—'}
                        {comparison.after.lop_days ? ` (${comparison.after.lop_days} LOP)` : ''}
                      </strong>
                    </div>
                  </div>
                </div>
              </section>
            )}

            {/* Plain-Language Formulas */}
            {formulas.length > 0 && (
              <section className="hcm-sheet-section">
                <h4 className="hcm-sheet-section-title">Plain-language formulas</h4>
                <div className="hcm-sheet-formulas-box">
                  {formulas.map((f, idx) => (
                    <div key={idx} className="hcm-sheet-formula-item">
                      <span className="hcm-formula-bullet">•</span>
                      <p className="hcm-formula-text">{f}</p>
                    </div>
                  ))}
                </div>
              </section>
            )}

            {/* Rules used (Northwind demo rules v1) */}
            {ruleCitations.length > 0 && (
              <section className="hcm-sheet-section">
                <h4 className="hcm-sheet-section-title">Rules used (Northwind demo rules v1)</h4>
                <div className="hcm-sheet-citations-box">
                  {ruleCitations.map((cite, idx) => (
                    <div key={idx} className="hcm-sheet-citation-item">
                      <FileText size={14} className="hcm-citation-icon" />
                      <p className="hcm-citation-text">{cite}</p>
                    </div>
                  ))}
                </div>
              </section>
            )}

            {/* Footer Assurance */}
            <div className="hcm-sheet-footer-note">
              <CheckCircle2 size={14} color="var(--color-primary-text)" />
              <span>Calculated with simplified demo rules. Not for real payroll.</span>
            </div>
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
};
