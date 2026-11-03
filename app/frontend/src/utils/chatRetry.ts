import { useState, useEffect } from 'react';
import { api } from '../services/api';
import type { ChatMessageTurn } from './welcomeTurn';
import { formatLocalTime } from './format';

export function hasServerResponse(err: any): boolean {
  return Boolean(
    err?.response ||
    err?.status ||
    err?.statusCode ||
    err?.hasResponse ||
    err?.serverReturnedResponse ||
    err?.message?.includes('server down') ||
    err?.message?.includes('after the request was sent') ||
    err?.message?.includes('after request was sent') ||
    err?.message?.match(/\b(4\d\d|5\d\d)\b/)
  );
}

export function isNetworkFailureNoResponse(err: any): boolean {
  if (hasServerResponse(err)) {
    return false;
  }
  return Boolean(
    err?.noResponse === true ||
    err?.isNetworkFailure === true ||
    err?.name === 'TypeError' ||
    err?.message?.includes('Failed to fetch') ||
    err?.message?.includes('no response') ||
    err?.message?.includes('Cold start') ||
    err?.message?.includes('demo server') ||
    err?.message?.includes('asleep') ||
    err?.isColdStart
  );
}

export async function sendChatWithRetry(
  payload: any,
  retryCount = 0,
  maxRetries = 6,
  retryDelayMs = 10000
): Promise<any> {
  try {
    return await api.chat(payload);
  } catch (err: any) {
    if (isNetworkFailureNoResponse(err) && retryCount < maxRetries) {
      const delay = (window as any).__TEST_FAST_RETRY__ ? 10 : retryDelayMs;
      await new Promise((resolve) => setTimeout(resolve, delay));
      return sendChatWithRetry(payload, retryCount + 1, maxRetries, retryDelayMs);
    }
    throw err;
  }
}

export function buildColdStartErrorTurn(
  retryPayload: { type: 'message'; text: string } | { type: 'action'; actionName: string; actionPayload?: any }
): ChatMessageTurn {
  return {
    id: `asst-coldstart-err-${Date.now()}`,
    type: 'assistant',
    messages: [{ code: 'ERR_COLD_START', text: "Couldn't reach the demo server." }],
    cards: [
      {
        id: `card-retry-${Date.now()}`,
        type: 'retry_action',
        data: {
          retryPayload,
        },
      },
    ],
    chips: [],
    time: formatLocalTime(new Date()),
  };
}

export function useChatWakingNotice(isLoading: boolean): boolean {
  const [showWakingNotice, setShowWakingNotice] = useState(false);

  useEffect(() => {
    if (isLoading) {
      const timer = setTimeout(() => {
        setShowWakingNotice(true);
      }, 3000);
      return () => clearTimeout(timer);
    } else {
      setShowWakingNotice(false);
    }
  }, [isLoading]);

  return showWakingNotice;
}
