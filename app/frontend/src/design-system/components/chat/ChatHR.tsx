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
  type EmployeePickerEntry,
  HR_STARTER_CHIPS,
  createWelcomeTurn,
} from '../../../utils/welcomeTurn';
import {
  sendChatWithRetry,
  isNetworkFailureNoResponse,
  buildColdStartErrorTurn,
  useChatWakingNotice,
} from '../../../utils/chatRetry';

export type { ChatMessageTurn, EmployeePickerEntry };
export { HR_STARTER_CHIPS, createWelcomeTurn };

interface ChatHRProps {
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

export const ChatHR: React.FC<ChatHRProps> = ({
  currentUser,
  currentScenario: _currentScenario,
  prefilledText,
  onClearPrefill,
  onNewChat,
}) => {
  const [turns, setTurns] = useState<ChatMessageTurn[]>(() => [createWelcomeTurn(currentUser)]);
  const [isPanelOpen, setIsPanelOpen] = useState(false);
  const [panelData, setPanelData] = useState<PanelHRData | null>(null);
  const [activeChips, setActiveChips] = useState<ChipItem[]>(HR_STARTER_CHIPS);
  const [isLoading, setIsLoading] = useState(false);
  const showChatWakingNotice = useChatWakingNotice(isLoading);
  const [clearSignal, setClearSignal] = useState(0);

  // Employee picker data & cold start state
  const [employees, setEmployees] = useState<EmployeePickerEntry[]>([]);
  const [employeesStatus, setEmployeesStatus] = useState<'loading' | 'ready' | 'error'>('loading');

  const feedEndRef = useRef<HTMLDivElement>(null);
  const retryTimeoutRef = useRef<any>(null);

  const scrollToBottom = () => {
    if (typeof feedEndRef.current?.scrollIntoView === 'function') {
      feedEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [turns]);



  // Calculate badge count from live API data:
  // Needs attention = live tags include "Needs input" or "Open query"
  const needsAttentionCount = employees.filter((emp) =>
    (emp.status_tags || []).some((t) => t.includes('Needs input') || t.includes('Open query'))
  ).length;

  // Cold start employee fetch with up to 6 retries ~10s apart (B1)
  const fetchEmployeesWithRetry = (retryCount = 0) => {
    setEmployeesStatus('loading');
    if (retryTimeoutRef.current) {
      clearTimeout(retryTimeoutRef.current);
    }

    const empCall = typeof api.getEmployees === 'function' ? api.getEmployees() : Promise.resolve([]);
    Promise.resolve(empCall)
      .then((data) => {
        if (Array.isArray(data)) {
          setEmployees(data);
          setEmployeesStatus('ready');
        } else {
          throw new Error('Invalid employees data');
        }
      })
      .catch((err) => {
        console.warn(`[ColdStart] GET /api/employees attempt ${retryCount + 1} failed:`, err);
        if (retryCount < 6) {
          const delay = (window as any).__TEST_FAST_RETRY__ ? 10 : 10000;
          retryTimeoutRef.current = setTimeout(() => {
            fetchEmployeesWithRetry(retryCount + 1);
          }, delay);
        } else {
          setEmployeesStatus('error');
        }
      });
  };

  useEffect(() => {
    setTurns([createWelcomeTurn(currentUser)]);
    setActiveChips(HR_STARTER_CHIPS);
    setIsPanelOpen(false);
    setPanelData(null);
    setEmployees([]);
    fetchEmployeesWithRetry(0);

    return () => {
      if (retryTimeoutRef.current) {
        clearTimeout(retryTimeoutRef.current);
      }
    };
  }, [currentUser]);

  // Keep any open unselected picker in `turns` in sync with employees / employeesStatus
  useEffect(() => {
    setTurns((prevTurns) => {
      let modified = false;
      const updated = prevTurns.map((t) => {
        if (!t.cards) return t;
        const hasUnused = t.cards.some(
          (c) => c.type === 'employee_dropdown_picker' && !c.data?.selectedEmployee
        );
        if (!hasUnused) return t;
        modified = true;
        return {
          ...t,
          cards: t.cards.map((c) =>
            c.type === 'employee_dropdown_picker' && !c.data?.selectedEmployee
              ? {
                  ...c,
                  data: {
                    ...c.data,
                    employees,
                    status: employeesStatus,
                    onRetry: () => fetchEmployeesWithRetry(0),
                  },
                }
              : c
          ),
        };
      });
      return modified ? updated : prevTurns;
    });
  }, [employees, employeesStatus]);

  // Open / Focus Searchable Employee Picker (A3)
  const handleOpenEmployeePicker = () => {
    // If a dropdown from an earlier click is still open and unused, focus it instead of duplicating
    const unusedPickerCard = turns
      .flatMap((t) => t.cards || [])
      .find((c) => c.type === 'employee_dropdown_picker' && !c.data?.selectedEmployee);

    if (unusedPickerCard) {
      const inputEl = document.getElementById('employee-picker-search-input');
      if (inputEl) {
        inputEl.focus();
      }
      return;
    }

    const pickerCardId = `card-picker-${Date.now()}`;
    const userTurn: ChatMessageTurn = {
      id: `user-select-emp-${Date.now()}`,
      type: 'user',
      text: 'Select an employee',
      time: formatLocalTime(new Date()),
    };

    const assistantTurn: ChatMessageTurn = {
      id: `asst-picker-${Date.now()}`,
      type: 'assistant',
      messages: [{ code: 'C69', text: 'Pick an employee to see what you can do for them:' }],
      cards: [
        {
          id: pickerCardId,
          type: 'employee_dropdown_picker',
          data: {
            employees,
            status: employeesStatus,
            onRetry: () => fetchEmployeesWithRetry(0),
            onSelect: (emp: EmployeePickerEntry) => handlePickEmployee(pickerCardId, emp),
            selectedEmployee: null,
            autoFocus: true,
          },
        },
      ],
      chips: [],
      time: formatLocalTime(new Date()),
    };

    setTurns((prev) => [...prev, userTurn, assistantTurn]);
  };

  // Picking an employee collapses dropdown into pill, then runs "Show options for {Name}" (A5)
  const handlePickEmployee = (pickerCardId: string, emp: EmployeePickerEntry) => {
    setTurns((prevTurns) =>
      prevTurns.map((t) => {
        if (!t.cards) return t;
        const matchingCard = t.cards.find(
          (c) => c.type === 'employee_dropdown_picker' && (!pickerCardId || c.id === pickerCardId)
        );
        if (!matchingCard) return t;

        return {
          ...t,
          cards: t.cards.map((c) =>
            c.type === 'employee_dropdown_picker' && (!pickerCardId || c.id === pickerCardId)
              ? {
                  ...c,
                  data: {
                    ...c.data,
                    selectedEmployee: emp,
                  },
                }
              : c
          ),
        };
      })
    );

    // Run existing flow: user turn "Show options for {Name}", then C70 assistant reply
    handleSendMessage(`Show options for ${emp.name}`);
  };

  // Global keydown "/" to trigger employee picker if no text box is focused (A3)
  useEffect(() => {
    const handleGlobalKeyDown = (e: KeyboardEvent) => {
      if (e.key === '/') {
        const activeTag = document.activeElement?.tagName?.toLowerCase();
        const isEditable =
          activeTag === 'input' ||
          activeTag === 'textarea' ||
          (document.activeElement as HTMLElement)?.isContentEditable;
        if (!isEditable) {
          e.preventDefault();
          handleOpenEmployeePicker();
        }
      }
    };
    window.addEventListener('keydown', handleGlobalKeyDown);
    return () => window.removeEventListener('keydown', handleGlobalKeyDown);
  }, [turns, employees, employeesStatus]);

  const handleNewChat = () => {
    setIsPanelOpen(false);
    setPanelData(null);
    setTurns([createWelcomeTurn(currentUser)]);
    setActiveChips(HR_STARTER_CHIPS);
    fetchEmployeesWithRetry(0);
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
      const res = await sendChatWithRetry({
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
        setPanelData(res.state.panel);
      }
    } catch (err: any) {
      console.error('Failed to send message:', err);
      if (isNetworkFailureNoResponse(err)) {
        setTurns((prev) => [...prev, buildColdStartErrorTurn({ type: 'message', text: text.trim() })]);
      } else {
        const errTurn = buildErrorTurn(undefined, err);
        setTurns((prev) => [...prev, errTurn]);
      }
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
      const res = await sendChatWithRetry({
        userId: currentUser,
        action: actionName,
        context: actionPayload || {},
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
                    notice: undefined,
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
    } catch (err: any) {
      console.error(`Action ${actionName} failed:`, err);
      if (isNetworkFailureNoResponse(err)) {
        setTurns((prev) => [
          ...prev,
          buildColdStartErrorTurn({ type: 'action', actionName, actionPayload }),
        ]);
      } else {
        const errTurn = buildErrorTurn(actionName, err);
        setTurns((prev) => [...prev, errTurn]);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleChipSelect = (chip: ChipItem) => {
    setClearSignal((s) => s + 1);
    if (onClearPrefill) onClearPrefill();
    if (chip.label === 'Select an employee') {
      handleOpenEmployeePicker();
      return;
    }
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
              <Shield size={14} color="var(--color-primary-text)" />
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

              const isWelcomeTurn = turn.id.startsWith('asst-welcome-');

              return (
                <AssistantTurn
                  key={turn.id}
                  messages={turn.messages || []}
                  cards={turn.cards || []}
                  state={turn.state}
                  time={turn.time}
                  selectEmployeeButton={
                    isWelcomeTurn
                      ? {
                          onClick: handleOpenEmployeePicker,
                          badgeCount: employeesStatus === 'ready' ? needsAttentionCount : 0,
                        }
                      : undefined
                  }
                  onShowCalculation={() => setIsPanelOpen(true)}
                  onApprove={(payload) => handleAction('approve', payload)}
                  onEdit={(payload) => handleAction('edit', { reason: 'Adjusted by HR', ...payload })}
                  onReject={(payload) => handleAction('reject', { reason: 'Rejected by HR', ...payload })}
                  onApplySelection={(choice) => handleAction('apply-selection', { choice })}
                  onSendQuery={(desc, qid) => {
                    if (qid) {
                      handleAction('confirm-reply-query', { query_id: qid, reply_text: desc });
                    } else {
                      handleAction('send-query', { description: desc });
                    }
                  }}
                  onCancelQueryDraft={() => {}}
                  onTakeIntoReview={(qid) => handleAction('take-into-review', { query_id: qid })}
                  onResolveQuery={(qid) => handleAction('resolve-query', { query_id: qid })}
                  onConfirmResolve={(qid, replyText) =>
                    handleAction('confirm-resolve-query', {
                      query_id: qid,
                      confirmed: true,
                      reply_text: replyText || null,
                    })
                  }
                  onActionClick={(act, payload) => {
                    if (act === 'retry-last-action') {
                      if (payload?.type === 'message') {
                        handleSendMessage(payload.text);
                      } else if (payload?.type === 'action') {
                        handleAction(payload.actionName, payload.actionPayload);
                      }
                      return;
                    }
                    handleAction(act, payload);
                  }}
                  onSelectEmployee={(empId, task, name) => {
                    if (task === 'options' || !task) {
                      handleSendMessage(`Show options for ${name || empId}`);
                    } else {
                      handleAction('select-employee', { employee_id: empId, task, name });
                    }
                  }}
                />
              );
            })}
            {isLoading && (
              <div className="hcm-chat-thinking" data-testid="chat-thinking" aria-live="polite">
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <span className="hcm-thinking-dot" />
                  <span className="hcm-thinking-dot" />
                  <span className="hcm-thinking-dot" />
                  <span className="hcm-thinking-text">Thinking…</span>
                </div>
                {showChatWakingNotice && (
                  <div
                    className="hcm-chat-waking-notice"
                    data-testid="chat-waking-notice"
                    style={{ marginTop: '6px', fontSize: '12px', color: 'var(--color-text-muted)' }}
                  >
                    Waking up the demo server. This can take up to a minute.
                  </div>
                )}
              </div>
            )}
            <div ref={feedEndRef} />
          </div>
        </div>

        {/* Bottom Dock: Suggestion Chips + Composer */}
        <div className="hcm-chat-bottom-dock">
          {activeChips.length > 0 && (
            <div className="hcm-chat-chips-area">
              <SuggestionChips
                chips={activeChips}
                onSelectChip={handleChipSelect}
                disabled={isLoading}
              />
            </div>
          )}

          <Composer
            onSendMessage={handleSendMessage}
            disabled={isLoading}
            placeholder="Ask about payroll, arrears or settlements…"
            isMobile={false}
            prefilledText={prefilledText}
            clearSignal={clearSignal}
          />
        </div>
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
