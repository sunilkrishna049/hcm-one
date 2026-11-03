import React from 'react';
import { Sparkles, UserSearch } from 'lucide-react';
import { CardRenderer } from '../cards/CardRenderer';
import { CertaintyLabel } from '../CertaintyLabel';
import { formatLocalTime } from '../../../utils/format';

interface AssistantMessage {
  code: string;
  text: string;
}

export interface SelectEmployeeButtonConfig {
  onClick: () => void;
  badgeCount?: number;
}

interface AssistantTurnProps {
  messages: AssistantMessage[];
  cards?: any[];
  state?: any;
  certainty?: string;
  time?: string;
  selectEmployeeButton?: SelectEmployeeButtonConfig;
  onShowCalculation?: () => void;
  onApprove?: (payload?: any) => void;
  onEdit?: (payload?: any) => void;
  onReject?: (payload?: any) => void;
  onApplySelection?: (choice: string) => void;
  onSendQuery?: (description: string, queryId?: string) => void;
  onCancelQueryDraft?: () => void;
  onTakeIntoReview?: (queryId: string) => void;
  onResolveQuery?: (queryId: string) => void;
  onDisputeQuery?: (queryId: string) => void;
  onCloseQuery?: (queryId: string) => void;
  onConfirmResolve?: (queryId: string, replyText?: string) => void;
  onActionClick?: (action: string, payload?: any) => void;
  onSelectEmployee?: (employeeId: string, task?: string, name?: string) => void;
}

export const AssistantTurn: React.FC<AssistantTurnProps> = ({
  messages,
  cards = [],
  state,
  certainty,
  time,
  selectEmployeeButton,
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
  onConfirmResolve,
  onActionClick,
  onSelectEmployee,
}) => {
  // Epistemic certainty shown once per assistant reply:
  // Reads from reply-level state.certainty (or explicit certainty prop).
  // Replies with no payroll number (FAQ, C33, C34, greetings) show no badge.
  const turnCertainty = certainty ?? state?.certainty;

  const displayTime = time || formatLocalTime(new Date());

  // Ordering: Lead sentences (e.g. C30) first, then cards, then C27 follow-up offer
  // F8: When refusal card is present, drop the duplicate bubble text and keep the red card
  const hasRefusalCard = cards.some((c) => c.type === 'refusal_card');
  const leadMessages = messages.filter((m) => m.code !== 'C27' && (!hasRefusalCard || m.code !== 'C10'));
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
              {selectEmployeeButton && idx === leadMessages.length - 1 && (
                <div style={{ marginTop: '12px' }}>
                  <button
                    type="button"
                    data-testid="select-employee-welcome-btn"
                    aria-label="Select an employee"
                    onClick={selectEmployeeButton.onClick}
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '8px',
                      height: '36px',
                      minHeight: '36px',
                      padding: '0 16px',
                      borderRadius: '9999px',
                      backgroundColor: '#1150BF',
                      color: '#FFFFFF',
                      fontSize: '14px',
                      fontWeight: 500,
                      border: 'none',
                      cursor: 'pointer',
                      outline: 'none',
                      transition: 'background-color 0.15s ease',
                    }}
                    onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = '#1459D1')}
                    onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = '#1150BF')}
                    onFocus={(e) => (e.currentTarget.style.outline = '2px solid #5B8EE6')}
                    onBlur={(e) => (e.currentTarget.style.outline = 'none')}
                  >
                    <UserSearch size={16} />
                    <span>Select an employee</span>
                    {typeof selectEmployeeButton.badgeCount === 'number' && selectEmployeeButton.badgeCount > 0 && (
                      <span
                        data-testid="needs-attention-badge"
                        aria-label={`${selectEmployeeButton.badgeCount} need attention`}
                        style={{
                          display: 'inline-flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          minWidth: '20px',
                          height: '20px',
                          borderRadius: '9999px',
                          backgroundColor: '#E3A008',
                          color: '#111827',
                          fontSize: '11px',
                          fontWeight: 700,
                          padding: '0 5px',
                          lineHeight: 1,
                          marginLeft: '2px',
                        }}
                      >
                        {selectEmployeeButton.badgeCount}
                      </span>
                    )}
                  </button>
                </div>
              )}
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
              role={state?.role}
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
              onConfirmResolve={onConfirmResolve}
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
