import type { ChipItem } from '../design-system/components/chat/SuggestionChips';
import { getUserFirstName, USER_NAME_MAP } from './userDisplay';
import { formatLocalTime } from './format';

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

export interface EmployeePickerEntry {
  employee_id: string;
  name: string;
  department: string;
  status_tags: string[];
}

export const HR_STARTER_CHIPS: ChipItem[] = [
  { label: "Select an employee" },
  { label: "Prepare Priya Sharma's pending back-dated hike" },
  { label: "Prepare a bonus proposal" },
  { label: "Review payroll queries" },
];

export const EMP_STARTER_CHIPS: ChipItem[] = [
  { label: "Why is my take-home lower this month?" },
  { label: "Why did my TDS change?" },
  { label: "What is LOP?" },
  { label: "Track my query" },
];

export function createWelcomeTurn(userId: string): ChatMessageTurn {
  const firstName = getUserFirstName(userId);
  const isHR = USER_NAME_MAP[userId]?.role?.includes('HR') || userId.startsWith('HR');

  const messages: Array<{ code: string; text: string }> = [
    {
      code: 'C31',
      text: `Hi ${firstName}. What would you like to do today?`,
    },
  ];

  if (!isHR) {
    messages.push({
      code: 'C01',
      text: "I am HCM One's AI payroll assistant. I explain payroll records and payroll calculation results. I can help prepare a proposal or a query for you to review. I cannot approve a change, apply it or pay it. I send a query only after you confirm.",
    });
  }

  return {
    id: `asst-welcome-${Date.now()}`,
    type: 'assistant',
    messages,
    cards: [],
    chips: [],
    time: formatLocalTime(new Date()),
  };
}
