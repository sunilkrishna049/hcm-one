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

interface CardRendererProps {
  card: any;
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

export const CardRenderer: React.FC<CardRendererProps> = ({
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
  onActionClick,
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
          card={card}
          onTakeIntoReview={onTakeIntoReview}
          onResolveQuery={onResolveQuery}
          onDisputeQuery={onDisputeQuery}
          onCloseQuery={onCloseQuery}
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

    default:
      return null;
  }
};
