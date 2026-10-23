import React from 'react';
import { ExternalLink } from 'lucide-react';

interface FaqAnswerCardProps {
  card: {
    id: string;
    type: string;
    title: string;
    certainty: string;
    data: {
      id: string;
      category: string;
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
    d.url &&
    d.url.trim() !== '' &&
    d.url !== 'To be defined in the payroll FAQ file' &&
    d.link_text &&
    d.link_text.trim() !== '' &&
    d.link_text !== 'To be defined in the payroll FAQ file';

  const handleLinkClick = (e: React.MouseEvent) => {
    if (d.url && d.url.startsWith('/chat?action=')) {
      e.preventDefault();
      const actionName = d.url.split('action=')[1];
      if (onActionClick && actionName) {
        onActionClick(actionName);
      }
    }
  };

  return (
    <div className="hcm-rich-card hcm-card-faq" data-testid={`card-${card.id}`}>
      <div className="hcm-card-header">
        <div>
          <span className="hcm-card-type-badge">{d.category}</span>
          <h4 className="hcm-card-title">{d.question}</h4>
        </div>
        <span className="hcm-tech-id">{d.id}</span>
      </div>

      <div className="hcm-card-body">
        <p className="hcm-faq-answer-text">{d.answer}</p>

        {hasValidLink && (
          <div className="hcm-faq-link-row">
            <a
              href={d.url}
              onClick={handleLinkClick}
              className="hcm-faq-action-link"
            >
              <span>{d.link_text}</span>
              <ExternalLink size={14} />
            </a>
          </div>
        )}
      </div>
    </div>
  );
};
