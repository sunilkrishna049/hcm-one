import React from 'react';
import { Sparkles } from 'lucide-react';
import { CardRenderer } from '../cards/CardRenderer';
import { CertaintyLabel } from '../CertaintyLabel';
import { formatLocalTime } from '../../../utils/format';

interface AssistantMessage {
  code: string;
  text: string;
}

interface AssistantTurnProps {
  messages: AssistantMessage[];
  cards?: any[];
  time?: string;
  onShowCalculation?: () => void;
  onApprove?: () => void;
  onEdit?: () => void;
  onReject?: () => void;
  onApplySelection?: (choice: string) => void;
  onSendQuery?: (description: string) => void;
  onCancelQueryDraft?: () => void;
  onTakeIntoReview?: (queryId: string) => void;
  onResolveQuery?: (queryId: string) => void;
  onDisputeQuery?: (queryId: string) => void;
  onCloseQuery?: (queryId: string) => void;
  onActionClick?: (action: string) => void;
  onSelectEmployee?: (employeeId: string, task?: string, name?: string) => void;
}

export const AssistantTurn: React.FC<AssistantTurnProps> = ({
  messages,
  cards = [],
  time,
  onShowCalculation,
  onApprove,
  onEdit,
  onReject,
  onApplySelection,
  onSendQuery,
  onCancelQueryDraft,
  onTakeIntoReview,
  onResolveQuery,
  onDisputeQuery,
  onCloseQuery,
  onActionClick,
  onSelectEmployee,
}) => {
  // Epistemic certainty shown once per assistant reply:
  // Certainty labels appear only on replies that show calculated amounts.
  const hasCalculatedAmounts = cards.some((c) =>
    ['number_hero', 'number_cards', 'month_table', 'component_list', 'reason_list', 'proposal_summary'].includes(c.type)
  );
  const turnCertainty = hasCalculatedAmounts ? cards.find((c) => c.certainty)?.certainty : undefined;

  const displayTime = time || formatLocalTime(new Date());

  // Ordering: Lead sentences (e.g. C30) first, then cards, then C27 follow-up offer
  const leadMessages = messages.filter((m) => m.code !== 'C27');
  const followUpMessages = messages.filter((m) => m.code === 'C27');

  return (
    <div className="hcm-assistant-turn-wrapper" data-testid="assistant-turn" role="region" aria-label="Assistant turn">
      <div className="hcm-assistant-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
          <div className="hcm-assistant-avatar" aria-hidden="true">
            <Sparkles size={14} />
          </div>
          <span className="hcm-assistant-sender-tag">HCM One Assistant</span>
          <span className="hcm-message-timestamp">{displayTime}</span>
        </div>
        {turnCertainty && (
          <CertaintyLabel certainty={turnCertainty} className="hcm-turn-certainty" />
        )}
      </div>

      {/* Lead Message Bubbles (C30, C01, C03 verbatim) */}
      {leadMessages.length > 0 && (
        <div className="hcm-assistant-bubbles-container">
          {leadMessages.map((m, idx) => (
            <div key={idx} className="hcm-assistant-bubble">
              <p className="hcm-assistant-bubble-text">{m.text}</p>
            </div>
          ))}
        </div>
      )}

      {/* Attached Rich Cards */}
      {cards.length > 0 && (
        <div className="hcm-cards-feed" data-testid="cards-feed">
          {cards.map((c) => (
            <CardRenderer
              key={c.id || Math.random().toString()}
              card={c}
              onShowCalculation={onShowCalculation}
              onApprove={onApprove}
              onEdit={onEdit}
              onReject={onReject}
              onApplySelection={onApplySelection}
              onSendQuery={onSendQuery}
              onCancelQueryDraft={onCancelQueryDraft}
              onTakeIntoReview={onTakeIntoReview}
              onResolveQuery={onResolveQuery}
              onDisputeQuery={onDisputeQuery}
              onCloseQuery={onCloseQuery}
              onActionClick={onActionClick}
              onSelectEmployee={onSelectEmployee}
            />
          ))}
        </div>
      )}

      {/* Follow-up Message Bubbles (e.g. C27 follow-up offer after cards) */}
      {followUpMessages.length > 0 && (
        <div className="hcm-assistant-bubbles-container" style={{ marginTop: 'var(--space-2)' }}>
          {followUpMessages.map((m, idx) => (
            <div key={idx} className="hcm-assistant-bubble">
              <p className="hcm-assistant-bubble-text">{m.text}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
