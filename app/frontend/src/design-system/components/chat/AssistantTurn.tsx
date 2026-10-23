import React from 'react';
import { Sparkles } from 'lucide-react';
import { CardRenderer } from '../cards/CardRenderer';

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
}

export const AssistantTurn: React.FC<AssistantTurnProps> = ({
  messages,
  cards = [],
  time = 'Just now',
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
}) => {
  return (
    <div className="hcm-assistant-turn-wrapper" data-testid="assistant-turn" role="region" aria-label="Assistant turn">
      <div className="hcm-assistant-header">
        <div className="hcm-assistant-avatar" aria-hidden="true">
          <Sparkles size={14} />
        </div>
        <span className="hcm-assistant-sender-tag">HCM One Assistant</span>
        <span className="hcm-message-timestamp">{time}</span>
      </div>

      {/* Message Bubbles (Approved copy C01-C30 verbatim) */}
      <div className="hcm-assistant-bubbles-container">
        {messages.map((m, idx) => (
          <div key={idx} className="hcm-assistant-bubble">
            <p className="hcm-assistant-bubble-text">{m.text}</p>
          </div>
        ))}
      </div>

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
            />
          ))}
        </div>
      )}
    </div>
  );
};
