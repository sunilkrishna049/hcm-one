import React from 'react';
import { ProposalSummaryCard } from './ProposalSummaryCard';
import { NumberCardsCluster } from './NumberCardsCluster';
import { MonthTableCard } from './MonthTableCard';
import { ComponentListCard } from './ComponentListCard';
import { ReasonListCard } from './ReasonListCard';
import { ClarifyingQuestionCard } from './ClarifyingQuestionCard';
import { ApprovalCard } from './ApprovalCard';
import { QueryDraftCard } from './QueryDraftCard';
import { SendConfirmationCard } from './SendConfirmationCard';
import { QueryStatusCard } from './QueryStatusCard';
import { RefusalCard } from './RefusalCard';
import { FaqAnswerCard } from './FaqAnswerCard';
import { ShowCalculationControl } from './ShowCalculationControl';
import { EmployeePickerCard } from './EmployeePickerCard';
import { EmployeeDropdownPicker } from './EmployeeDropdownPicker';

interface CardRendererProps {
  role?: string;
  card: any;
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

export const CardRenderer: React.FC<CardRendererProps> = ({
  role,
  card,
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
  switch (card.type) {
    case 'proposal_summary':
      return <ProposalSummaryCard card={card} />;

    case 'number_hero':
    case 'number_cards':
      return <NumberCardsCluster card={card} onShowCalculation={onShowCalculation} />;

    case 'month_table':
      return <MonthTableCard card={card} onShowCalculation={onShowCalculation} />;

    case 'component_list':
      return <ComponentListCard card={card} onShowCalculation={onShowCalculation} />;

    case 'reason_list':
      return <ReasonListCard card={card} onShowCalculation={onShowCalculation} />;

    case 'clarifying_question':
      return <ClarifyingQuestionCard card={card} onApplySelection={onApplySelection} />;

    case 'approval_card':
      return (
        <ApprovalCard
          card={card}
          onApprove={onApprove}
          onEdit={onEdit}
          onReject={onReject}
        />
      );

    case 'query_draft':
      return (
        <QueryDraftCard
          card={card}
          onSendQuery={onSendQuery}
          onCancel={onCancelQueryDraft}
        />
      );

    case 'send_confirmation':
      return <SendConfirmationCard card={card} />;

    case 'query_status':
      return (
        <QueryStatusCard
          role={role}
          card={card}
          onTakeIntoReview={onTakeIntoReview}
          onResolveQuery={onResolveQuery}
          onDisputeQuery={onDisputeQuery}
          onCloseQuery={onCloseQuery}
          onConfirmResolve={onConfirmResolve}
        />
      );

    case 'refusal_card':
      return <RefusalCard card={card} />;

    case 'faq_answer':
      return <FaqAnswerCard card={card} onActionClick={onActionClick} />;

    case 'show_calculation':
      return (
        <ShowCalculationControl
          card={card}
          onShowCalculation={onShowCalculation || (() => {})}
        />
      );

    case 'employee_dropdown_picker':
      return (
        <EmployeeDropdownPicker
          employees={card.data?.employees || []}
          status={card.data?.status || 'ready'}
          isWaking={card.data?.isWaking}
          onRetry={card.data?.onRetry}
          onSelectEmployee={(emp) => {
            if (card.data?.onSelect) {
              card.data.onSelect(emp);
            } else {
              onSelectEmployee?.(emp.employee_id, 'options', emp.name);
            }
          }}
          selectedEmployee={card.data?.selectedEmployee}
          autoFocus={card.data?.autoFocus ?? true}
        />
      );

    case 'retry_action':
      return (
        <div style={{ marginTop: '8px' }}>
          <button
            type="button"
            data-testid="chat-retry-btn"
            onClick={() => onActionClick?.('retry-last-action', card.data?.retryPayload)}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              padding: '6px 14px',
              borderRadius: '9999px',
              backgroundColor: '#1150BF',
              color: '#FFFFFF',
              fontSize: '12px',
              fontWeight: 500,
              border: 'none',
              cursor: 'pointer',
            }}
          >
            Try again
          </button>
        </div>
      );

    case 'employee_picker':
    case 'employee-picker':
      return (
        <EmployeePickerCard
          card={card}
          onSelectEmployee={onSelectEmployee}
        />
      );

    default:
      return null;
  }
};
