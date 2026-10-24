import React, { useState, useEffect, useRef } from 'react';
import { api } from '../../../services/api';
import { UserBubble } from './UserBubble';
import { AssistantTurn } from './AssistantTurn';
import { SuggestionChips, type ChipItem } from './SuggestionChips';
import { Composer } from './Composer';
import { SheetEMP, type SheetEMPData } from './SheetEMP';
import { User } from 'lucide-react';
import { getUserDisplayName } from '../../../utils/userDisplay';

export interface ChatMessageTurn {
  id: string;
  type: 'user' | 'assistant';
  text?: string;
  messages?: Array<{ code: string; text: string }>;
  cards?: any[];
  chips?: ChipItem[];
  state?: any;
  time?: string;
}

interface ChatEMPProps {
  currentUser: string;
  currentScenario: number;
  initialMessage?: string;
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
    time: 'Just now',
  };
}

export const ChatEMP: React.FC<ChatEMPProps> = ({
  currentUser,
  currentScenario,
  initialMessage,
}) => {
  const [turns, setTurns] = useState<ChatMessageTurn[]>([]);
  const [isSheetOpen, setIsSheetOpen] = useState(false);
  const [sheetData, setSheetData] = useState<SheetEMPData | null>(null);
  const [activeChips, setActiveChips] = useState<ChipItem[]>([]);
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

  // Load opening turn when scenario or initialMessage changes
  useEffect(() => {
    let isCancelled = false;
    const loadScenarioTurn = async () => {
      setIsLoading(true);
      setTurns([]);
      setActiveChips([]);
      setIsSheetOpen(false);

      const msg = initialMessage || 'Why is my September salary lower than August?';
      const userTurn: ChatMessageTurn = {
        id: `user-${Date.now()}`,
        type: 'user',
        text: msg,
        time: 'Just now',
      };

      try {
        const res = await api.chat({
          userId: currentUser,
          message: msg,
          context: { scenario_num: currentScenario },
        });

        if (isCancelled) return;

        if ((res as any)?.error) {
          const errTurn = buildErrorTurn(undefined, (res as any).error);
          setTurns([userTurn, errTurn]);
          return;
        }

        const assistantTurn: ChatMessageTurn = {
          id: `asst-${Date.now()}`,
          type: 'assistant',
          messages: res.messages || [],
          cards: res.cards || [],
          chips: res.chips || [],
          state: res.state || {},
          time: 'Just now',
        };

        setTurns([userTurn, assistantTurn]);
        setActiveChips(res.chips || []);
        if (res.state?.panel) {
          setSheetData(res.state.panel);
        }
      } catch (err) {
        if (!isCancelled) {
          console.error('Chat error:', err);
          const errTurn = buildErrorTurn(undefined, err);
          setTurns([userTurn, errTurn]);
        }
      } finally {
        if (!isCancelled) setIsLoading(false);
      }
    };

    loadScenarioTurn();
    return () => {
      isCancelled = true;
    };
  }, [currentScenario, currentUser, initialMessage]);

  const handleSendMessage = async (text: string) => {
    if (!text.trim() || isLoading) return;

    const userTurn: ChatMessageTurn = {
      id: `user-${Date.now()}`,
      type: 'user',
      text: text.trim(),
      time: 'Just now',
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
        time: 'Just now',
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

      const assistantTurn: ChatMessageTurn = {
        id: `asst-${Date.now()}`,
        type: 'assistant',
        messages: res.messages || [],
        cards: res.cards || [],
        chips: res.chips || [],
        state: res.state || {},
        time: 'Just now',
      };

      setTurns((prev) => [...prev, assistantTurn]);
      setActiveChips(res.chips || []);
      if (res.state?.panel) {
        setSheetData(res.state.panel);
      }
    } catch (err) {
      console.error('Failed to execute action:', err);
      const errTurn = buildErrorTurn(actionName, err);
      setTurns((prev) => [...prev, errTurn]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleChipSelect = (chip: ChipItem) => {
    if (chip.action === 'show-calculation' || chip.label === 'Show calculation' || chip.label === 'Show tax calculation') {
      setIsSheetOpen(true);
      return;
    }
    if (chip.action) {
      handleAction(chip.action, chip.payload);
    } else {
      handleSendMessage(chip.label);
    }
  };

  return (
    <div className="hcm-chat-emp-container" data-testid="chat-emp">
      <div className="hcm-chat-emp-frame">
        {/* Mobile Header (56 px) */}
        <header className="hcm-chat-emp-header">
          <div className="hcm-chat-emp-header-info">
            <h1 className="hcm-chat-emp-title">HCM One</h1>
            <span className="hcm-chat-emp-role-tag">Employee Assistant</span>
          </div>
          <div className="hcm-chat-emp-user-tag">
            <User size={14} />
            <span>{getUserDisplayName(currentUser)}</span>
          </div>
        </header>

        {/* Scrollable Conversation Stream */}
        <main className="hcm-chat-emp-feed-scroll" data-testid="chat-feed" role="main">
          <div className="hcm-chat-emp-feed-inner">
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
                  onShowCalculation={() => setIsSheetOpen(true)}
                  onSendQuery={(desc) => handleAction('confirm-send-query', { draft: { description: desc } })}
                  onCancelQueryDraft={() => handleAction('cancel-draft')}
                  onDisputeQuery={(qid) => handleAction('dispute-query', { query_id: qid, reason: 'Employee disputed resolution.' })}
                  onCloseQuery={(qid) => handleAction('close-query', { query_id: qid })}
                  onActionClick={(act) => handleAction(act)}
                />
              );
            })}
            <div ref={feedEndRef} />
          </div>
        </main>

        {/* Suggestion Chips */}
        {activeChips.length > 0 && (
          <div className="hcm-chat-emp-chips-area">
            <SuggestionChips
              chips={activeChips}
              onSelectChip={handleChipSelect}
              disabled={isLoading}
            />
          </div>
        )}

        {/* Sticky Mobile Composer (64 px) */}
        <Composer
          onSendMessage={handleSendMessage}
          disabled={isLoading}
          placeholder="Ask a question about your salary..."
          isMobile={true}
        />

        {/* Bottom Sheet Detail Proof (SHEET-EMP) */}
        <SheetEMP
          isOpen={isSheetOpen}
          onClose={() => setIsSheetOpen(false)}
          data={sheetData}
        />
      </div>
    </div>
  );
};
