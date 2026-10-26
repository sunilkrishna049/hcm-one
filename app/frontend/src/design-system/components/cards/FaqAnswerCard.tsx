import React from 'react';
import { ArrowRight } from 'lucide-react';

interface FaqAnswerCardProps {
  card: {
    id: string;
    type: string;
    title: string;
    certainty: string;
    data: {
      id?: string;
      category?: string;
      question: string;
      answer: string;
      link_text?: string;
      url?: string;
      confidence?: number;
    };
  };
  onActionClick?: (action: string) => void;
}

export const FaqAnswerCard: React.FC<FaqAnswerCardProps> = ({ card, onActionClick }) => {
  const d = card.data;
  const hasValidLink =
    Boolean(d.url) &&
    d.url!.trim() !== '' &&
    d.url !== 'To be defined in the payroll FAQ file' &&
    Boolean(d.link_text) &&
    d.link_text!.trim() !== '' &&
    d.link_text !== 'To be defined in the payroll FAQ file';

  const handleAction = (e: React.MouseEvent) => {
    e.preventDefault();
    if (d.url && d.url.includes('action=')) {
      const actionName = d.url.split('action=')[1];
      if (onActionClick && actionName) {
        onActionClick(actionName);
        return;
      }
    }
    if (onActionClick) {
      if (d.link_text?.toLowerCase().includes('payslip') || d.link_text?.toLowerCase().includes('salary')) {
        onActionClick('explain-salary');
      } else if (d.link_text?.toLowerCase().includes('tds')) {
        onActionClick('explain-tds');
      }
    }
  };

  return (
    <div className="hcm-rich-card hcm-card-faq" data-testid={`card-${card.id}`}>
      <div className="hcm-card-header">
        <div>
          <span className="hcm-card-type-badge">{d.category || 'Payroll Glossary'}</span>
          <h4 className="hcm-card-title">{d.question}</h4>
        </div>
      </div>

      <div className="hcm-card-body">
        <p className="hcm-faq-answer-text">{d.answer}</p>

        {hasValidLink && (
          <div className="hcm-faq-action-row" style={{ marginTop: 'var(--space-3)' }}>
            <button
              type="button"
              onClick={handleAction}
              className="hcm-suggestion-chip hcm-faq-action-chip"
              data-testid="faq-action-button"
            >
              <span>{d.link_text}</span>
              <ArrowRight size={14} style={{ marginLeft: 'var(--space-1)' }} />
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
