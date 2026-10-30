import React, { useState, useEffect, useRef } from 'react';
import { api } from '../../../services/api';
import { UserBubble } from './UserBubble';
import { AssistantTurn } from './AssistantTurn';
import { SuggestionChips, type ChipItem } from './SuggestionChips';
import { Composer } from './Composer';
import { SheetEMP, type SheetEMPData } from './SheetEMP';
import { User, Plus } from 'lucide-react';
import { getUserDisplayName } from '../../../utils/userDisplay';
import { formatLocalTime } from '../../../utils/format';
import {
  type ChatMessageTurn,
  EMP_STARTER_CHIPS,
  createWelcomeTurn,
} from '../../../utils/welcomeTurn';

export type { ChatMessageTurn };
export { EMP_STARTER_CHIPS, createWelcomeTurn };

interface ChatEMPProps {
  currentUser: string;
  currentScenario?: number;
  initialMessage?: string;
  prefilledText?: string;
  onClearPrefill?: () => void;
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

export const ChatEMP: React.FC<ChatEMPProps> = ({
  currentUser,
  currentScenario: _currentScenario,
  prefilledText,
  onClearPrefill,
  onNewChat,
}) => {
  const [turns, setTurns] = useState<ChatMessageTurn[]>(() => [createWelcomeTurn(currentUser)]);
  const [isSheetOpen, setIsSheetOpen] = useState(false);
  const [sheetData, setSheetData] = useState<SheetEMPData | null>(null);
  const [activeChips, setActiveChips] = useState<ChipItem[]>(EMP_STARTER_CHIPS);
  const [isLoading, setIsLoading] = useState(false);
  const [clearSignal, setClearSignal] = useState(0);
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
    setActiveChips(EMP_STARTER_CHIPS);
    setIsSheetOpen(false);
    setSheetData(null);
  }, [currentUser]);

  const handleNewChat = () => {
    setIsSheetOpen(false);
    setSheetData(null);
    setTurns([createWelcomeTurn(currentUser)]);
    setActiveChips(EMP_STARTER_CHIPS);
    if (onNewChat) {
      onNewChat();
    }
  };

  const handleSendMessage = async (text: string) => {
    if (!text.trim() || isLoading) return;

    setClearSignal((s) => s + 1);
    if (onClearPrefill) onClearPrefill();

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
        setSheetData(res.state.panel);
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
    setClearSignal((s) => s + 1);
    if (onClearPrefill) onClearPrefill();
    setIsLoading(true);

    try {
      const res = await api.chat({
        userId: currentUser,
        action: actionName,
        context: actionPayload || {},
      });

      if ((res as any)?.error) {
        const errTurn = buildErrorTurn(actionName, (res as any).error);
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
        setSheetData(res.state.panel);
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
    setClearSignal((s) => s + 1);
    if (onClearPrefill) onClearPrefill();
    if (chip.action === 'show-calculation' || chip.label === 'Show calculation' || chip.label === 'Show calculation proof' || chip.label === 'Show breakdown') {
      setIsSheetOpen(true);
      if (chip.action) {
        handleAction(chip.action, chip.payload);
      }
      return;
    }
    if (chip.action) {
      handleAction(chip.action, chip.payload);
    } else {
      handleSendMessage(chip.label);
    }
  };


  return (
    <div className="hcm-chat-layout hcm-chat-emp-container" data-testid="chat-emp">
      <main className="hcm-chat-main hcm-chat-emp-main" role="main">
        {/* Header */}
        <header className="hcm-chat-top-header">
          <div className="hcm-chat-header-title-box">
            <h1 className="hcm-chat-header-title">HCM One</h1>
            <span className="hcm-chat-header-badge">Employee Assistant</span>
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
              <User size={14} color="var(--color-brand-accent)" />
              <span>{getUserDisplayName(currentUser, true)}</span>
            </div>
          </div>
        </header>

        {/* Scrollable Conversation Stream */}
        <div className="hcm-chat-feed-scroll" data-testid="chat-feed" role="region" aria-label="Conversation stream">
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
                  state={turn.state}
                  time={turn.time}
                  onShowCalculation={() => setIsSheetOpen(true)}
                  onSendQuery={(desc) => handleAction('confirm-send-query', { draft: { description: desc } })}
                  onCancelQueryDraft={() => handleAction('cancel-draft')}
                  onDisputeQuery={(qid) => handleAction('dispute-query', { query_id: qid, reason: 'Employee disputed resolution.' })}
                  onCloseQuery={(qid) => handleAction('close-query', { query_id: qid })}
                  onActionClick={(act) => handleAction(act)}
                  onSelectEmployee={(empId, task, name) => handleAction('select-employee', { employee_id: empId, task, name })}
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
          placeholder="Ask a question about your salary…"
          prefilledText={prefilledText}
          clearSignal={clearSignal}
        />
      </main>

      {/* Side Panel / Bottom Sheet Detail Proof (SHEET-EMP) */}
      <SheetEMP
        isOpen={isSheetOpen}
        onClose={() => setIsSheetOpen(false)}
        data={sheetData}
      />
    </div>
  );
};
