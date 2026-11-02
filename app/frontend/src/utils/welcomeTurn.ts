import type { ChipItem } from '../design-system/components/chat/SuggestionChips';
import { getUserFirstName } from './userDisplay';
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

export const ALL_RECORDED_EMPLOYEES: EmployeePickerEntry[] = [
  { employee_id: 'E01', name: 'Priya Sharma', department: 'Engineering', status_tags: ['Hike pending'] },
  { employee_id: 'E02', name: 'Arjun Rao', department: 'Operations', status_tags: ['Hike pending'] },
  { employee_id: 'E03', name: 'Kavya Iyer', department: 'Engineering', status_tags: ['Needs input'] },
  { employee_id: 'E04', name: 'Rohan Mehta', department: 'Engineering', status_tags: [] },
  { employee_id: 'E05', name: 'Neha Gupta', department: 'Operations', status_tags: ['Open query'] },
  { employee_id: 'E06', name: 'Siddharth Jain', department: 'Engineering', status_tags: [] },
  { employee_id: 'E07', name: 'Sneha Kulkarni', department: 'Engineering', status_tags: [] },
  { employee_id: 'E08', name: 'Vikram Singh', department: 'Engineering', status_tags: ['Leaving November'] },
  { employee_id: 'E09', name: 'Meera Nair', department: 'Engineering', status_tags: ['Needs input'] },
  { employee_id: 'E10', name: 'Rahul Verma', department: 'Finance', status_tags: ['Leaving October'] },
  { employee_id: 'E11', name: 'Lakshmi Reddy', department: 'Finance', status_tags: ['Leaving October'] },
  { employee_id: 'E12', name: 'Imran Khan', department: 'Engineering', status_tags: ['Needs input', 'Leaving October'] },
  { employee_id: 'E13', name: 'Ankit Jain', department: 'Sales', status_tags: [] },
  { employee_id: 'E14', name: 'Fatima Sheikh', department: 'Sales', status_tags: [] },
  { employee_id: 'E15', name: 'Deepak Pillai', department: 'Sales', status_tags: [] },
  { employee_id: 'E16', name: 'Pooja Das', department: 'Operations', status_tags: [] },
];

export const SALES_EMPLOYEE_IDS = ['E13', 'E14', 'E15'];

export const HR_STARTER_CHIPS: ChipItem[] = [
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
  const isHR = userId === 'HR01' || userId === 'HR02' || userId.startsWith('HR');

  let cards: any[] = [];
  if (isHR) {
    const permittedEmployees = userId === 'HR02'
      ? ALL_RECORDED_EMPLOYEES.filter((emp) => SALES_EMPLOYEE_IDS.includes(emp.employee_id))
      : ALL_RECORDED_EMPLOYEES;

    cards = [
      {
        id: 'card-employee-picker-welcome',
        type: 'employee-picker',
        title: 'Select employee',
        data: {
          prompt: 'Pick an employee to see what you can do for them:',
          has_search: true,
          employees: permittedEmployees,
        },
      },
    ];
  }

  return {
    id: `asst-welcome-${Date.now()}`,
    type: 'assistant',
    messages: [
      {
        code: 'C31',
        text: `Hi ${firstName}. What would you like to do today?`,
      },
      {
        code: 'C01',
        text: "I am HCM One's AI payroll assistant. I explain payroll records and payroll calculation results. I can help prepare a proposal or a query for you to review. I cannot approve a change, apply it or pay it. I send a query only after you confirm.",
      },
    ],
    cards,
    chips: [],
    time: formatLocalTime(new Date()),
  };
}
