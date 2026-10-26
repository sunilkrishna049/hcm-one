import React, { useState, useEffect, useRef } from 'react';
import { api } from '../../../services/api';
import { UserBubble } from './UserBubble';
import { AssistantTurn } from './AssistantTurn';
import { SuggestionChips, type ChipItem } from './SuggestionChips';
import { Composer } from './Composer';
import { PanelHR, type PanelHRData } from './PanelHR';
import { Shield, Plus } from 'lucide-react';
import { getUserDisplayName } from '../../../utils/userDisplay';
import { formatLocalTime } from '../../../utils/format';
import {
  type ChatMessageTurn,
  HR_STARTER_CHIPS,
  createWelcomeTurn,
} from '../../../utils/welcomeTurn';

export type { ChatMessageTurn };
export { HR_STARTER_CHIPS, createWelcomeTurn };

interface ChatHRProps {
  currentUser: string;
  currentScenario?: number;
  initialMessage?: string;
  prefilledText?: string;
  onNewChat?: () => void;
}

function buildErrorTurn(actionName?: string, err?: any): ChatMessageTurn {
  let code = 'C09';
  let text = 'The payroll calculation did not produce a usable result for this operation. I cannot give a complete amount for it.';

  const errMsg = String(err?.message || err?.detail || err || '');
  if (actionName === 'send-query' || actionName === 'confirm-send-query' || errMsg.includes('draft') || errMsg.includes('query')) {
    code = 'C17';
    text = 'Your query has not been sent. It remains a draft.';
  } else if (errMsg.includes('version') || errMsg.includes('stale') || errMsg.includes('conflict')) {
    code = 'C25';
    text = 'This proposal changed after you reviewed it. Review the current version before approving.';
  }

  return {
    id: `asst-err-${Date.now()}`,
    type: 'assistant',
    messages: [{ code, text }],
    cards: [],
    chips: [],
    time: formatLocalTime(new Date()),
  };
}

export const ChatHR: React.FC<ChatHRProps> = ({
  currentUser,
  currentScenario = 1,
  prefilledText,
  onNewChat,
}) => {
  const [turns, setTurns] = useState<ChatMessageTurn[]>(() => [createWelcomeTurn(currentUser)]);
  const [isPanelOpen, setIsPanelOpen] = useState(false);
  const [panelData, setPanelData] = useState<PanelHRData | null>(null);
  const [activeChips, setActiveChips] = useState<ChipItem[]>(HR_STARTER_CHIPS);
  const [isLoading, setIsLoading] = useState(false);
  const feedEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    if (typeof feedEndRef.current?.scrollIntoView === 'function') {
      feedEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [turns]);

  // When user switches login, reset to empty welcome state for that user
  useEffect(() => {
    setTurns([createWelcomeTurn(currentUser)]);
    setActiveChips(HR_STARTER_CHIPS);
    setIsPanelOpen(false);
    setPanelData(null);
  }, [currentUser]);

  const handleNewChat = () => {
    setIsPanelOpen(false);
    setPanelData(null);
    setTurns([createWelcomeTurn(currentUser)]);
    setActiveChips(HR_STARTER_CHIPS);
    if (onNewChat) {
      onNewChat();
    }
  };

  const handleSendMessage = async (text: string) => {
    if (!text.trim() || isLoading) return;

    const userTurn: ChatMessageTurn = {
      id: `user-${Date.now()}`,
      type: 'user',
      text: text.trim(),
      time: formatLocalTime(new Date()),
    };
    setTurns((prev) => [...prev, userTurn]);
    setIsLoading(true);

    try {
      const res = await api.chat({
        userId: currentUser,
        message: text.trim(),
        context: { scenario_num: currentScenario },
      });

      if ((res as any)?.error) {
        const errTurn = buildErrorTurn(undefined, (res as any).error);
        setTurns((prev) => [...prev, errTurn]);
        return;
      }

      const assistantTurn: ChatMessageTurn = {
        id: `asst-${Date.now()}`,
        type: 'assistant',
        messages: res.messages || [],
        cards: res.cards || [],
        chips: res.chips || [],
        state: res.state || {},
        time: formatLocalTime(new Date()),
      };

      setTurns((prev) => [...prev, assistantTurn]);
      setActiveChips(res.chips || []);
      if (res.state?.panel) {
        setPanelData(res.state.panel);
      }
    } catch (err) {
      console.error('Failed to send message:', err);
      const errTurn = buildErrorTurn(undefined, err);
      setTurns((prev) => [...prev, errTurn]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAction = async (actionName: string, actionPayload?: any) => {
    if (isLoading) return;
    setIsLoading(true);

    try {
      const res = await api.chat({
        userId: currentUser,
        action: actionName,
        context: { scenario_num: currentScenario, ...actionPayload },
      });

      if ((res as any)?.error) {
        const errTurn = buildErrorTurn(actionName, (res as any).error);
        setTurns((prev) => [...prev, errTurn]);
        return;
      }

      // If user approved, edited, or rejected a proposal, replace action buttons on earlier cards
      // with recorded state and disable them so active Approve/Edit/Reject are not shown twice.
      if (['approve', 'edit', 'reject'].includes(actionName)) {
        setTurns((prev) =>
          prev.map((t) => {
            if (t.type !== 'assistant' || !t.cards) return t;
            const updatedCards = t.cards.map((c) => {
              if (c.type === 'approval_card') {
                const isCurrentApproved = actionName === 'approve';
                const isCurrentRejected = actionName === 'reject';
                const isCurrentEdited = actionName === 'edit';
                return {
                  ...c,
                  data: {
                    ...c.data,
                    actions: [],
                    disabled: true,
                    disabled_label: isCurrentApproved
                      ? 'Proposal approved. Action buttons disabled.'
                      : isCurrentRejected
                      ? 'Proposal rejected. Action buttons disabled.'
                      : isCurrentEdited
                      ? 'Proposal revised. Action buttons disabled.'
                      : 'Action recorded.',
                  },
                };
              }
              return c;
            });
            return { ...t, cards: updatedCards };
          })
        );
      }

      // After approval, do not repeat C04 sentence. Show only the approved state card.
      let filteredMessages = res.messages || [];
      if (actionName === 'approve') {
        filteredMessages = filteredMessages.filter((m: any) => m.code !== 'C04');
      }

      const assistantTurn: ChatMessageTurn = {
        id: `asst-${Date.now()}`,
        type: 'assistant',
        messages: filteredMessages,
        cards: res.cards || [],
        chips: res.chips || [],
        state: res.state || {},
        time: formatLocalTime(new Date()),
      };

      setTurns((prev) => [...prev, assistantTurn]);
      setActiveChips(res.chips || []);
      if (res.state?.panel) {
        setPanelData(res.state.panel);
      }
    } catch (err) {
      console.error(`Action ${actionName} failed:`, err);
      const errTurn = buildErrorTurn(actionName, err);
      setTurns((prev) => [...prev, errTurn]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleChipSelect = (chip: ChipItem) => {
    if (chip.action === 'show-calculation' || chip.label === 'Show calculation' || chip.label === 'Show calculation proof') {
      setIsPanelOpen(true);
      return;
    }
    if (chip.action) {
      handleAction(chip.action, chip.payload);
    } else {
      handleSendMessage(chip.label);
    }
  };


  return (
    <div className="hcm-chat-hr-layout" data-testid="chat-hr">
      {/* Main Conversation Workspace */}
      <main className="hcm-chat-hr-main" role="main">
        {/* Workspace Subheader */}
        <div className="hcm-chat-top-header">
          <div className="hcm-chat-header-title-box">
            <h1 className="hcm-chat-header-title">HCM One HR Workspace</h1>
          </div>
          <div className="hcm-chat-header-meta">
            <button
              type="button"
              className="hcm-btn-secondary hcm-new-chat-btn"
              onClick={handleNewChat}
              data-testid="new-chat-btn"
              aria-label="Start new chat"
            >
              <Plus size={14} />
              <span>New chat</span>
            </button>
            <div className="hcm-chat-user-badge">
              <Shield size={14} color="var(--brand-accent)" />
              <span>{getUserDisplayName(currentUser, true)}</span>
            </div>
          </div>
        </div>

        {/* Conversation Stream Container */}
        <div className="hcm-chat-feed-scroll" data-testid="chat-feed">
          <div className="hcm-chat-feed-inner">
            {turns.map((turn) => {
              if (turn.type === 'user') {
                return (
                  <UserBubble
                    key={turn.id}
                    text={turn.text || ''}
                    time={turn.time}
                  />
                );
              }
              return (
                <AssistantTurn
                  key={turn.id}
                  messages={turn.messages || []}
                  cards={turn.cards || []}
                  time={turn.time}
                  onShowCalculation={() => setIsPanelOpen(true)}
                  onApprove={() => handleAction('approve')}
                  onEdit={() => handleAction('edit', { reason: 'Adjusted by HR' })}
                  onReject={() => handleAction('reject', { reason: 'Rejected by HR' })}
                  onApplySelection={(choice) => handleAction('apply-selection', { choice })}
                  onSendQuery={(desc) => handleAction('send-query', { description: desc })}
                  onCancelQueryDraft={() => handleAction('cancel-draft')}
                  onTakeIntoReview={(qid) => handleAction('take-into-review', { query_id: qid })}
                  onResolveQuery={(qid) => handleAction('resolve-query', { query_id: qid, reply_text: 'Attendance reviewed and verified against punch records.' })}
                  onDisputeQuery={(qid) => handleAction('dispute-query', { query_id: qid, reason: 'Employee disputed resolution.' })}
                  onCloseQuery={(qid) => handleAction('close-query', { query_id: qid })}
                  onActionClick={(act) => handleAction(act)}
                />
              );
            })}
            {isLoading && (
              <div className="hcm-chat-thinking" data-testid="chat-thinking" aria-live="polite">
                <span className="hcm-thinking-dot" />
                <span className="hcm-thinking-dot" />
                <span className="hcm-thinking-dot" />
                <span className="hcm-thinking-text">Thinking…</span>
              </div>
            )}
            <div ref={feedEndRef} />
          </div>
        </div>

        {/* Suggestion Chips */}
        {activeChips.length > 0 && (
          <div className="hcm-chat-chips-area">
            <SuggestionChips
              chips={activeChips}
              onSelectChip={handleChipSelect}
              disabled={isLoading}
            />
          </div>
        )}

        {/* Sticky Composer */}
        <Composer
          onSendMessage={handleSendMessage}
          disabled={isLoading}
          placeholder="Ask a question or enter a payroll request..."
          isMobile={false}
          prefilledText={prefilledText}
        />
      </main>

      {/* Side Review Panel (PANEL-HR) */}
      <PanelHR
        isOpen={isPanelOpen}
        onClose={() => setIsPanelOpen(false)}
        data={panelData}
      />
    </div>
  );
};
