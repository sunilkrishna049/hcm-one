import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent, within } from '@testing-library/react';
import React from 'react';
import { ChatHR } from '../design-system/components/chat/ChatHR';
import { ChatEMP } from '../design-system/components/chat/ChatEMP';
import { App } from '../App';
import { CardRenderer } from '../design-system/components/cards/CardRenderer';
import { AssistantTurn } from '../design-system/components/chat/AssistantTurn';
import { api } from '../services/api';
import fixtures from './chat_scenario_fixtures.json';
import { createWelcomeTurn } from '../utils/welcomeTurn';

const MOCK_PICKER_EMPLOYEES = [
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

vi.mock('../services/api', () => ({
  api: {
    chat: vi.fn(),
    resetDemo: vi.fn().mockResolvedValue({ status: 'ok' }),
    getEmployees: vi.fn().mockImplementation(() => Promise.resolve(MOCK_PICKER_EMPLOYEES)),
  },
  setCurrentUserId: vi.fn(),
}));

describe('Chat Action Click Tests (React Testing Library)', () => {
  beforeEach(() => {
    vi.resetAllMocks();
    (api.getEmployees as any) = vi.fn().mockImplementation(() => Promise.resolve(MOCK_PICKER_EMPLOYEES));
  });

  it('1. Clicking "Approve proposal for payroll" dispatches approve action and renders approved state', async () => {
    // Initial scenario 1 load
    (api.chat as any).mockResolvedValueOnce({
      messages: [{ code: 'C03', text: 'This is a proposal for the recorded affected months.' }],
      cards: [
        {
          id: 'card-approval-s1',
          type: 'approval_card',
          title: 'Approval',
          certainty: 'Complete for this scope',
          data: {
            scope_label: 'Priya Sharma · Apr–Sep 2026',
            notice: 'Approving records this version and the selected scope as ready for payroll.',
            actions: ['Approve proposal for payroll', 'Edit with reason', 'Reject proposal'],
            status: 'pending',
            proposal_id: 'PROP-SCENARIO-1',
            version: 1,
          },
        },
      ],
      chips: [{ label: 'Show calculation', action: 'show-calculation' }],
      state: { scenario_num: 1, role: 'HR' },
    });

    render(<ChatHR currentUser="HR01" currentScenario={1} />);
    fireEvent.click(screen.getByText("Prepare Priya Sharma's pending back-dated hike"));

    await waitFor(() => {
      expect(screen.getByText('Approve proposal for payroll')).toBeInTheDocument();
    });

    // Mock approval response matching polished backend contract
    (api.chat as any).mockResolvedValueOnce({
      messages: [],
      cards: [
        {
          id: 'card-approval-approved-1',
          type: 'approval_card',
          title: 'Approval',
          data: {
            scope_label: 'Approved: Priya Sharma · Apr–Sep 2026',
            actions: [],
            status: 'approved',
            proposal_id: 'PROP-SCENARIO-1',
            version: 1,
            approver: 'HR01',
            approved_at: '2026-10-24T12:00:00Z',
          },
        },
      ],
      chips: [],
      state: { proposal_status: 'approved' },
    });

    fireEvent.click(screen.getByText('Approve proposal for payroll'));

    await waitFor(() => {
      expect(api.chat).toHaveBeenCalledWith(
        expect.objectContaining({
          userId: 'HR01',
          action: 'approve',
          context: { proposal_id: 'PROP-SCENARIO-1', version: 1 },
        })
      );
    });

    await waitFor(() => {
      // 1. Proves buttons are gone after approval
      expect(screen.queryByRole('button', { name: /Approve proposal for payroll/i })).toBeNull();
      expect(screen.queryByRole('button', { name: /Edit with reason/i })).toBeNull();
      expect(screen.queryByRole('button', { name: /Reject proposal/i })).toBeNull();

      // 2. Proves recorded state is displayed
      const badges = screen.getAllByTestId('approval-status-badge');
      expect(badges.length).toBeGreaterThan(0);
      expect(badges[0]).toHaveTextContent(/Approved and ready for payroll/i);
      expect(badges[0]).toHaveTextContent(/Version 1/i);

      // 3. Proves past-tense approved card wording
      expect(screen.getByText(/Approved: Priya Sharma · Apr–Sep 2026/i)).toBeInTheDocument();

      // 4. Proves C04 sentence is not repeated after approval
      expect(screen.queryByText(/Approving records this version and the selected scope as ready for payroll/i)).toBeNull();
    });
  });

  it('2. Clicking "Edit with reason" and "Reject proposal" dispatch edit and reject actions and disable buttons', async () => {
    // 2a. Test Edit action
    (api.chat as any).mockResolvedValueOnce({
      messages: [{ code: 'C03', text: 'This is a proposal for the recorded affected months.' }],
      cards: [
        {
          id: 'card-approval-s1',
          type: 'approval_card',
          title: 'Approval',
          data: {
            scope_label: 'Priya Sharma · Apr–Sep 2026',
            notice: 'Notice text',
            actions: ['Approve proposal for payroll', 'Edit with reason', 'Reject proposal'],
            status: 'pending',
            proposal_id: 'PROP-SCENARIO-1',
            version: 1,
          },
        },
      ],
      chips: [],
      state: { scenario_num: 1, role: 'HR' },
    });

    const { unmount } = render(<ChatHR currentUser="HR01" currentScenario={1} />);
    fireEvent.click(screen.getByText("Prepare Priya Sharma's pending back-dated hike"));

    await waitFor(() => {
      expect(screen.getByText('Edit with reason')).toBeInTheDocument();
    });

    (api.chat as any).mockResolvedValueOnce({
      messages: [{ code: 'C05', text: 'Your edit will create a revised proposal.' }],
      cards: [],
      chips: [],
      state: {},
    });

    fireEvent.click(screen.getByText('Edit with reason'));

    await waitFor(() => {
      expect(api.chat).toHaveBeenCalledWith(
        expect.objectContaining({
          userId: 'HR01',
          action: 'edit',
        })
      );
      expect(screen.getByText('Your edit will create a revised proposal.')).toBeInTheDocument();
      // Proves buttons are disabled after editing
      expect(screen.getByTestId('approval-disabled-note')).toHaveTextContent(/Proposal revised. Action buttons disabled./i);
      expect(screen.queryByRole('button', { name: /Edit with reason/i })).toBeNull();
    });

    unmount();

    // 2b. Test Reject action
    (api.chat as any).mockResolvedValueOnce({
      messages: [{ code: 'C03', text: 'This is a proposal for the recorded affected months.' }],
      cards: [
        {
          id: 'card-approval-s1',
          type: 'approval_card',
          title: 'Approval',
          data: {
            scope_label: 'Priya Sharma · Apr–Sep 2026',
            notice: 'Notice text',
            actions: ['Approve proposal for payroll', 'Edit with reason', 'Reject proposal'],
            status: 'pending',
            proposal_id: 'PROP-SCENARIO-1',
            version: 1,
          },
        },
      ],
      chips: [],
      state: { scenario_num: 1, role: 'HR' },
    });

    render(<ChatHR currentUser="HR01" currentScenario={1} />);
    fireEvent.click(screen.getByText("Prepare Priya Sharma's pending back-dated hike"));

    await waitFor(() => {
      expect(screen.getByText('Reject proposal')).toBeInTheDocument();
    });

    (api.chat as any).mockResolvedValueOnce({
      messages: [{ code: 'REJECTED', text: 'Proposal rejected.' }],
      cards: [
        {
          id: 'card-reject-PROP-1',
          type: 'approval_card',
          title: 'Proposal Rejected',
          data: {
            proposal_id: 'PROP-1',
            status: 'rejected',
            status_badge: 'Rejected • Not approved for payroll',
            notice: 'This proposal has been rejected and will not be applied to payroll.',
          },
        },
      ],
      chips: [],
      state: {},
    });

    fireEvent.click(screen.getByText('Reject proposal'));

    await waitFor(() => {
      expect(api.chat).toHaveBeenCalledWith(
        expect.objectContaining({
          userId: 'HR01',
          action: 'reject',
        })
      );
      expect(screen.getByText('Proposal rejected.')).toBeInTheDocument();
      expect(screen.getByTestId('approval-disabled-note')).toHaveTextContent(/Proposal rejected. Action buttons disabled./i);
      expect(screen.queryByRole('button', { name: /Reject proposal/i })).toBeNull();
    });
  });

  it('3. Query lifecycle click tests in ChatHR: Take into review and Resolve query', async () => {
    (api.chat as any).mockResolvedValueOnce({
      messages: [{ code: 'C16', text: 'Your query is In review. HR has taken it for review.' }],
      cards: [
        {
          id: 'card-query-status',
          type: 'query_status',
          title: 'Employee Queries',
          certainty: 'Complete for this scope',
          data: {
            queries: [
              {
                query_id: 'QUERY-E05-SEPTEMBER',
                status: 'Sent',
                description: 'Please review September LOP deduction of 3 days.',
              },
            ],
          },
        },
      ],
      chips: [],
      state: { role: 'HR' },
    });

    render(<ChatHR currentUser="HR01" currentScenario={1} />);
    fireEvent.click(screen.getByText('Review payroll queries'));

    await waitFor(() => {
      expect(screen.getByText('Take into review')).toBeInTheDocument();
    });

    (api.chat as any).mockResolvedValueOnce({
      messages: [{ code: 'C16', text: 'Your query is In review. HR has taken it for review.' }],
      cards: [
        {
          id: 'card-query-status-rev',
          type: 'query_status',
          title: 'Employee Queries',
          certainty: 'Complete for this scope',
          data: {
            queries: [
              {
                query_id: 'QUERY-E05-SEPTEMBER',
                status: 'In review',
                description: 'Please review September LOP deduction of 3 days.',
              },
            ],
          },
        },
      ],
      chips: [],
      state: { role: 'HR' },
    });

    fireEvent.click(screen.getByText('Take into review'));

    await waitFor(() => {
      expect(api.chat).toHaveBeenCalledWith(
        expect.objectContaining({
          userId: 'HR01',
          action: 'take-into-review',
          context: expect.objectContaining({ query_id: 'QUERY-E05-SEPTEMBER' }),
        })
      );
    });

    // Now test resolve query
    await waitFor(() => {
      expect(screen.getByText('Resolve query')).toBeInTheDocument();
    });

    (api.chat as any).mockResolvedValueOnce({
      messages: [{ code: 'C23', text: 'HR recorded a resolution.' }],
      cards: [],
      chips: [],
      state: {},
    });

    fireEvent.click(screen.getByText('Resolve query'));

    await waitFor(() => {
      expect(api.chat).toHaveBeenCalledWith(
        expect.objectContaining({
          userId: 'HR01',
          action: 'resolve-query',
          context: expect.objectContaining({ query_id: 'QUERY-E05-SEPTEMBER' }),
        })
      );
    });
  });

  it('4. Query draft, confirm send, dispute, and close in ChatEMP', async () => {
    (api.chat as any).mockResolvedValueOnce({
      messages: [{ code: 'C12', text: 'Send this query with the listed evidence to HR?' }],
      cards: [
        {
          id: 'card-draft-1',
          type: 'query_draft',
          title: 'Payroll Query Draft',
          certainty: 'Complete for this scope',
          data: {
            draft: {
              category: 'Loss of Pay (LOP)',
              months: ['2026-09'],
              description: 'Please review September LOP deduction of 3 days.',
              evidence: [{ type: 'Biometric Log', source: 'Punch-202609' }],
            },
            notice: 'Send this query with the listed evidence to HR?',
          },
        },
      ],
      chips: [],
      state: { role: 'Employee' },
    });

    render(<ChatEMP currentUser="USER-E05" currentScenario={9} />);
    fireEvent.click(screen.getByText('Why is my take-home lower this month?'));

    await waitFor(() => {
      expect(screen.getByText('Send query with listed evidence to HR')).toBeInTheDocument();
    });

    (api.chat as any).mockResolvedValueOnce({
      messages: [{ code: 'C15', text: 'Your query is Sent. HR can access it for review.' }],
      cards: [
        {
          id: 'card-status-sent',
          type: 'query_status',
          title: 'Query Submitted to HR',
          certainty: 'Complete for this scope',
          data: {
            query_id: 'QUERY-E05-SEPTEMBER',
            status: 'Resolved',
            description: 'Please review September LOP deduction.',
            resolution: 'Manager approved 1 day regularized.',
          },
        },
      ],
      chips: [],
      state: { role: 'Employee' },
    });

    fireEvent.click(screen.getByText('Send query with listed evidence to HR'));

    await waitFor(() => {
      expect(api.chat).toHaveBeenCalledWith(
        expect.objectContaining({
          userId: 'USER-E05',
          action: 'confirm-send-query',
        })
      );
    });

    // Verify dispute resolution button click
    await waitFor(() => {
      expect(screen.getByText('Dispute resolution')).toBeInTheDocument();
      expect(screen.getByText('Acknowledge and close')).toBeInTheDocument();
    });

    (api.chat as any).mockResolvedValueOnce({
      messages: [{ code: 'C16', text: 'Your query is In review. HR has taken it for review.' }],
      cards: [],
      chips: [],
      state: {},
    });

    fireEvent.click(screen.getByText('Dispute resolution'));

    await waitFor(() => {
      expect(api.chat).toHaveBeenCalledWith(
        expect.objectContaining({
          userId: 'USER-E05',
          action: 'dispute-query',
        })
      );
    });

    (api.chat as any).mockResolvedValueOnce({
      messages: [{ code: 'C24', text: 'Your query is Closed. Its history is retained.' }],
      cards: [],
      chips: [],
      state: {},
    });

    fireEvent.click(screen.getByText('Acknowledge and close'));

    await waitFor(() => {
      expect(api.chat).toHaveBeenCalledWith(
        expect.objectContaining({
          userId: 'USER-E05',
          action: 'close-query',
        })
      );
    });
  });

  it('5. Suggestion chip "Show calculation" opens side panel in ChatHR and bottom sheet in ChatEMP', async () => {
    (api.chat as any).mockResolvedValueOnce({
      messages: [{ code: 'C03', text: 'Hike proposal ready.' }],
      cards: [],
      chips: [{ label: 'Show calculation', action: 'show-calculation' }],
      state: {
        scenario_num: 1,
        role: 'HR',
        panel: {
          title: 'Calculation proof & month breakdown',
          months: [{ month: '2026-04', old_gross: 120000, revised_gross: 132000, diff: 12000, paid_days: 30, lop_days: 0 }],
        },
      },
    });

    render(<ChatHR currentUser="HR01" currentScenario={1} />);
    fireEvent.click(screen.getByText("Prepare Priya Sharma's pending back-dated hike"));

    await waitFor(() => {
      expect(screen.getByTestId('suggestion-chip-0')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByTestId('suggestion-chip-0'));

    await waitFor(() => {
      expect(screen.getByTestId('panel-hr')).toBeInTheDocument();
      expect(screen.getByText('Calculation proof & month breakdown')).toBeInTheDocument();
    });
  });

  it('6. Non-silent failure: When API returns an error or rejects, frontend renders approved error sentence', async () => {
    (api.chat as any).mockRejectedValueOnce(new Error('Network error or server down'));

    render(<ChatHR currentUser="HR01" currentScenario={1} />);
    fireEvent.click(screen.getByText("Prepare Priya Sharma's pending back-dated hike"));

    await waitFor(() => {
      // Must not fail silently: displays approved sentence C09
      expect(
        screen.getByText(/The payroll calculation did not produce a usable result for this operation/i)
      ).toBeInTheDocument();
    });
  });
});

describe('New Chat Start Experience Tests (DEC-040)', () => {
  beforeEach(() => {
    vi.resetAllMocks();
    (api.getEmployees as any) = vi.fn().mockImplementation(() => Promise.resolve(MOCK_PICKER_EMPLOYEES));
  });

  it('7. Empty welcome state on open: shows C31 greeting with user first name followed by C01, no auto-load', () => {
    // 7a. HR Admin open
    const { unmount } = render(<ChatHR currentUser="HR01" currentScenario={1} />);

    // Shows C31 with first name "Anita"
    expect(screen.getByText('Hi Anita. What would you like to do today?')).toBeInTheDocument();
    // Followed by C01
    expect(
      screen.getByText(
        "I am HCM One's AI payroll assistant. I explain payroll records and payroll calculation results. I can help prepare a proposal or a query for you to review. I cannot approve a change, apply it or pay it. I send a query only after you confirm."
      )
    ).toBeInTheDocument();
    // No api call on mount
    expect(api.chat).not.toHaveBeenCalled();

    unmount();

    // 7b. Employee open (USER-E05 Neha Gupta)
    render(<ChatEMP currentUser="USER-E05" currentScenario={9} />);

    expect(screen.getByText('Hi Neha. What would you like to do today?')).toBeInTheDocument();
    expect(
      screen.getByText(
        "I am HCM One's AI payroll assistant. I explain payroll records and payroll calculation results. I can help prepare a proposal or a query for you to review. I cannot approve a change, apply it or pay it. I send a query only after you confirm."
      )
    ).toBeInTheDocument();
    expect(api.chat).not.toHaveBeenCalled();
  });

  it('8. Role-specific starter chips match role and tapping sends message', async () => {
    // 8a. HR starter chips
    const { unmount } = render(<ChatHR currentUser="HR01" currentScenario={1} />);

    expect(screen.getByText("Prepare Priya Sharma's pending back-dated hike")).toBeInTheDocument();
    expect(screen.getByText('Prepare a bonus proposal')).toBeInTheDocument();
    expect(screen.getByText('Review payroll queries')).toBeInTheDocument();
    expect(screen.queryByText('Why is my take-home lower this month?')).toBeNull();

    (api.chat as any).mockResolvedValueOnce({
      messages: [{ code: 'C03', text: 'This is a proposal for the recorded affected months.' }],
      cards: [],
      chips: [],
    });

    // Tapping a chip sends it as first message
    fireEvent.click(screen.getByText("Prepare Priya Sharma's pending back-dated hike"));

    await waitFor(() => {
      expect(api.chat).toHaveBeenCalledWith(
        expect.objectContaining({
          userId: 'HR01',
          message: "Prepare Priya Sharma's pending back-dated hike",
        })
      );
    });

    unmount();

    // 8b. Employee starter chips
    render(<ChatEMP currentUser="USER-E05" currentScenario={9} />);

    expect(screen.getByText('Why is my take-home lower this month?')).toBeInTheDocument();
    expect(screen.getByText('Why did my TDS change?')).toBeInTheDocument();
    expect(screen.getByText('What is LOP?')).toBeInTheDocument();
    expect(screen.getByText('Track my query')).toBeInTheDocument();
    expect(screen.queryByText("Prepare Priya Sharma's pending back-dated hike")).toBeNull();

    (api.chat as any).mockResolvedValueOnce({
      messages: [{ code: 'C30', text: 'Your September take-home is lower than August.' }],
      cards: [],
      chips: [],
    });

    fireEvent.click(screen.getByText('Why is my take-home lower this month?'));

    await waitFor(() => {
      expect(api.chat).toHaveBeenCalledWith(
        expect.objectContaining({
          userId: 'USER-E05',
          message: 'Why is my take-home lower this month?',
        })
      );
    });
  });

  it('9. "New chat" button in header clears only the conversation and returns to welcome state', async () => {
    (api.chat as any).mockResolvedValueOnce({
      messages: [{ code: 'C03', text: 'This is a proposal for the recorded affected months.' }],
      cards: [
        {
          id: 'card-proposal',
          type: 'proposal_summary',
          title: 'Proposal Summary',
          data: {
            employee_name: 'Priya Sharma',
            old_gross: 120000,
            revised_gross: 132000,
          },
        },
      ],
      chips: [],
    });

    render(<ChatHR currentUser="HR01" currentScenario={1} />);

    // Send a message first
    fireEvent.click(screen.getByText("Prepare Priya Sharma's pending back-dated hike"));

    await waitFor(() => {
      expect(screen.getByText('Proposal Summary')).toBeInTheDocument();
    });

    // Click "New chat" in header
    const newChatBtn = screen.getByTestId('new-chat-btn');
    expect(newChatBtn).toBeInTheDocument();
    fireEvent.click(newChatBtn);

    // Clears conversation and returns to welcome state
    await waitFor(() => {
      expect(screen.queryByText('Proposal Summary')).toBeNull();
      expect(screen.getByText('Hi Anita. What would you like to do today?')).toBeInTheDocument();
      expect(screen.getByText("Prepare Priya Sharma's pending back-dated hike")).toBeInTheDocument();
    });

    // Does NOT call resetDemo
    expect(api.resetDemo).not.toHaveBeenCalled();
  });

  it('10. Two-way toggle switches between HR view and Employee view with empty chat, and frontend never sends scenario_num', async () => {
    render(<App />);

    // 1. App opens to empty new chat for default HR01 (Anita Desai)
    expect(screen.getByText('Hi Anita. What would you like to do today?')).toBeInTheDocument();
    expect(screen.getByText('Anita Desai · HR Admin')).toBeInTheDocument();
    // Headers must show name and role only, never IDs
    expect(screen.queryByText(/HR01/)).not.toBeInTheDocument();
    expect(api.chat).not.toHaveBeenCalled();

    // 2. Sending a message as HR must never send scenario_num
    (api.chat as any).mockResolvedValueOnce({
      messages: [{ code: 'C03', text: 'Proposal ready.' }],
      cards: [],
      chips: [],
    });

    const composerTextarea = screen.getByTestId('composer-textarea') as HTMLTextAreaElement;
    fireEvent.change(composerTextarea, { target: { value: 'Calculate arrears' } });
    const sendBtn = screen.getByTestId('composer-send-btn');
    fireEvent.click(sendBtn);

    await waitFor(() => {
      expect(api.chat).toHaveBeenCalledWith(
        expect.objectContaining({
          userId: 'HR01',
          message: 'Calculate arrears',
        })
      );
      // Explicit proof: frontend NEVER sends scenario_num
      const callArg = (api.chat as any).mock.calls[0][0];
      expect(callArg.context?.scenario_num).toBeUndefined();
    });

    // 3. Switch to Employee view via two-way toggle
    const empToggleBtn = screen.getByTestId('toggle-emp-view');
    fireEvent.click(empToggleBtn);

    // Switching toggle opens a new empty chat for Neha Gupta (USER-E05)
    await waitFor(() => {
      expect(screen.getByText('Hi Neha. What would you like to do today?')).toBeInTheDocument();
      expect(screen.getByText('Neha Gupta · Employee')).toBeInTheDocument();
      // Never IDs in header
      expect(screen.queryByText(/USER-E05/)).not.toBeInTheDocument();
    });

    // 4. Sending a message as Employee must never send scenario_num
    (api.chat as any).mockResolvedValueOnce({
      messages: [{ code: 'C30', text: 'Your September take-home is lower.' }],
      cards: [],
      chips: [],
    });

    const empComposer = screen.getByTestId('composer-textarea') as HTMLTextAreaElement;
    fireEvent.change(empComposer, { target: { value: 'Why is my take-home pay lower in September?' } });
    const empSendBtn = screen.getByTestId('composer-send-btn');
    fireEvent.click(empSendBtn);

    await waitFor(() => {
      expect(api.chat).toHaveBeenCalledWith(
        expect.objectContaining({
          userId: 'USER-E05',
          message: 'Why is my take-home pay lower in September?',
        })
      );
      const secondCallArg = (api.chat as any).mock.calls[1][0];
      expect(secondCallArg.context?.scenario_num).toBeUndefined();
    });

    // 5. Switch back to HR view opens new empty chat
    const hrToggleBtn = screen.getByTestId('toggle-hr-view');
    fireEvent.click(hrToggleBtn);

    await waitFor(() => {
      expect(screen.getByText('Hi Anita. What would you like to do today?')).toBeInTheDocument();
      expect(screen.getByText('Anita Desai · HR Admin')).toBeInTheDocument();
    });
  });

  it('11. Ambiguous bonus request shows clarifying question card with "Which bonus type do you mean?" and choices', async () => {
    (api.chat as any).mockResolvedValueOnce({
      messages: [],
      cards: [
        {
          id: 'card-clarify-bonus',
          type: 'clarifying_question',
          title: 'Which bonus type do you mean?',
          data: {
            question: 'Which bonus type do you mean?',
            choices: [
              'Annual performance bonus, FY 2025-26, Engineering',
              'Sales incentive (Q2 2026-27) · Hyderabad Sales',
            ],
            selected_choice: null,
          },
        },
      ],
      chips: [
        { label: 'Annual performance bonus, FY 2025-26, Engineering' },
        { label: 'Sales incentive (Q2 2026-27) · Hyderabad Sales' },
      ],
    });

    render(<ChatHR currentUser="HR01" currentScenario={4} />);

    // Tap "Prepare a bonus proposal" starter chip
    fireEvent.click(screen.getByText('Prepare a bonus proposal'));

    await waitFor(() => {
      // Question shown once (no duplicate title and body text)
      expect(screen.getAllByText('Which bonus type do you mean?').length).toBe(1);
      expect(screen.getAllByText('Annual performance bonus, FY 2025-26, Engineering').length).toBeGreaterThanOrEqual(1);
      expect(screen.getAllByText('Sales incentive (Q2 2026-27) · Hyderabad Sales').length).toBeGreaterThanOrEqual(1);
      // No "Apply Selection and Recalculate" button anywhere
      expect(screen.queryByText(/Apply Selection and Recalculate/i)).not.toBeInTheDocument();
    });

    // Mock API response for immediate send on tapping option
    (api.chat as any).mockResolvedValueOnce({
      messages: [{ code: 'C32', text: 'This is a proposal for the recorded Annual performance bonus for FY 2025-26.' }],
      cards: [],
      chips: [],
    });

    const cardEl = screen.getByTestId('card-card-clarify-bonus');
    const choiceChipBtn = within(cardEl).getByRole('button', { name: 'Annual performance bonus, FY 2025-26, Engineering' });
    fireEvent.click(choiceChipBtn);

    // Tapping immediately dispatches selection
    expect(api.chat).toHaveBeenCalledWith(
      expect.objectContaining({
        action: 'apply-selection',
        context: expect.objectContaining({ choice: 'Annual performance bonus, FY 2025-26, Engineering' }),
      })
    );

    // After selection the chosen option stays highlighted and card is locked
    expect(choiceChipBtn).toHaveClass('hcm-choice-selected');
    expect(choiceChipBtn).toBeDisabled();
  });

  it('12. Bonus proposal card displays "Known Eligible Gross" with certainty, and eligible list with E03 (tax incomplete)', async () => {
    (api.chat as any).mockResolvedValueOnce({
      messages: [
        {
          code: 'C32',
          text: 'This is a proposal for the recorded Annual performance bonus for FY 2025-26.',
        },
      ],
      cards: [
        {
          id: 'card-bonus-s4',
          type: 'proposal_summary',
          title: 'Team Bonus Run Summary',
          certainty: 'Incomplete',
          data: {
            proposal_type: 'Annual performance bonus (FY 2025-26)',
            eligible_count: 4,
            ineligible_count: 1,
            needs_input_count: 1,
            known_eligible_gross: 213929,
            known_eligible_gross_certainty: 'Complete for this scope',
            eligible: ['E01', 'E03', 'E04', 'E07'],
            not_eligible: [{ employee_id: 'E08', reason: 'On notice at the time of calculation' }],
            needs_input: [{ employee_id: 'E09', reason: 'Performance record missing' }],
            status: 'Needs HR approval; not applied',
          },
        },
      ],
      chips: [],
    });

    render(<ChatHR currentUser="HR01" currentScenario={4} />);

    const textarea = screen.getByTestId('composer-textarea');
    fireEvent.change(textarea, { target: { value: 'Annual performance bonus, FY 2025-26, Engineering' } });
    fireEvent.click(screen.getByTestId('composer-send-btn'));

    await waitFor(() => {
      // Wording C32 is displayed
      expect(screen.getByText('This is a proposal for the recorded Annual performance bonus for FY 2025-26.')).toBeInTheDocument();
      // Label "Known eligible gross" is displayed
      expect(screen.getByText('Known eligible gross')).toBeInTheDocument();
      // Amount ₹2,13,929 is displayed
      expect(screen.getByText('₹2,13,929')).toBeInTheDocument();
      // Counts match engine lists
      expect(screen.getByText('4')).toBeInTheDocument(); // eligible count
      // Eligible employees list shown with E03 tax incomplete note
      expect(screen.getByText('(tax incomplete)')).toBeInTheDocument();
    });
  });

  it('14. Composer: view toggle does not pre-type, composer empty after typed message and after chip', async () => {
    render(<App />);

    const textarea = screen.getByTestId('composer-textarea') as HTMLTextAreaElement;
    expect(textarea.value).toBe('');

    // 1. Switching view with two-way toggle does NOT pre-type anything
    const empToggleBtn = screen.getByTestId('toggle-emp-view');
    fireEvent.click(empToggleBtn);

    await waitFor(() => {
      const empTextarea = screen.getByTestId('composer-textarea') as HTMLTextAreaElement;
      expect(empTextarea.value).toBe('');
    });

    // Switch back to HR view: still empty
    const hrToggleBtn = screen.getByTestId('toggle-hr-view');
    fireEvent.click(hrToggleBtn);
    await waitFor(() => {
      const hrTextarea = screen.getByTestId('composer-textarea') as HTMLTextAreaElement;
      expect(hrTextarea.value).toBe('');
    });

    // 2. After typed message is sent, composer must be empty
    (api.chat as any).mockResolvedValueOnce({
      messages: [{ code: 'C03', text: 'Proposal summary ready.' }],
      cards: [],
      chips: [{ label: 'What is LOP?', action: 'faq-lop', payload: {} }],
    });

    const composer = screen.getByTestId('composer-textarea') as HTMLTextAreaElement;
    fireEvent.change(composer, { target: { value: 'Calculate arrears' } });
    expect(composer.value).toBe('Calculate arrears');

    const sendBtn = screen.getByTestId('composer-send-btn');
    fireEvent.click(sendBtn);

    await waitFor(() => {
      const composerAfterSend = screen.getByTestId('composer-textarea') as HTMLTextAreaElement;
      expect(composerAfterSend.value).toBe('');
    });

    // 3. User types text into composer, then clicks a chip -> composer must be empty
    const composerAfter = screen.getByTestId('composer-textarea') as HTMLTextAreaElement;
    fireEvent.change(composerAfter, { target: { value: 'Some uncommitted text' } });
    expect(composerAfter.value).toBe('Some uncommitted text');

    (api.chat as any).mockResolvedValueOnce({
      messages: [{ code: 'FAQ', text: 'Loss of pay explanation' }],
      cards: [],
      chips: [],
    });

    const lopChip = await screen.findByText('What is LOP?');
    fireEvent.click(lopChip);

    await waitFor(() => {
      const composerAfterChip = screen.getByTestId('composer-textarea') as HTMLTextAreaElement;
      expect(composerAfterChip.value).toBe('');
    });
  });

  it('14. Employee picker card shows name and code on HR surfaces (Priya Sharma · E01), tapping a name sends that selection and continues the task', async () => {
    // 1. Initial chat response returns employee_picker card with candidate employees from real exported fixture
    (api.chat as any).mockResolvedValueOnce((fixtures as any)['picker_arrears']);

    render(<ChatHR currentUser="HR01" currentScenario={1} />);

    // Send query to load arrears picker
    const composer = screen.getByTestId('composer-textarea');
    fireEvent.change(composer, { target: { value: 'Calculate arrears' } });
    fireEvent.click(screen.getByTestId('composer-send-btn'));

    // Wait for employee picker card to render
    await waitFor(() => {
      expect(screen.getAllByTestId('employee-picker-card').length).toBeGreaterThanOrEqual(2);
    });

    const pickerCards = screen.getAllByTestId('employee-picker-card');
    const pickerCard = pickerCards[pickerCards.length - 1];

    // Assert card shows employee names and muted codes from the API
    expect(pickerCard).toHaveTextContent('Priya Sharma · E01');
    expect(pickerCard).toHaveTextContent('Arjun Rao · E02');
    expect(pickerCard).toHaveTextContent('Kavya Iyer · E03');

    // 2. Mock response when employee is selected (continues the task)
    (api.chat as any).mockResolvedValueOnce({
      messages: [{ code: 'C03', text: 'This is a proposal for the recorded affected months.' }],
      cards: [
        {
          id: 'card-approval-s1',
          type: 'approval_card',
          title: 'Approval',
          certainty: 'Complete for this scope',
          data: {
            scope_label: 'Priya Sharma · Apr–Sep 2026',
            status: 'pending',
            proposal_id: 'PROP-SCENARIO-1',
          },
        },
      ],
      chips: [{ label: 'Show calculation', action: 'show-calculation' }],
      state: { scenario_num: 1, role: 'HR Admin' },
    });

    // Tap Priya Sharma's button
    const priyaButtons = screen.getAllByTestId('employee-item-E01');
    const priyaButton = priyaButtons[priyaButtons.length - 1];
    fireEvent.click(priyaButton);

    // Verify tapping sends that selection (action='select-employee')
    await waitFor(() => {
      expect(api.chat).toHaveBeenCalledWith({
        userId: 'HR01',
        action: 'select-employee',
        context: {
          employee_id: 'E01',
          task: 'arrears',
          name: 'Priya Sharma',
        },
      });
    });

    // Verify task continues and renders proposal card
    await waitFor(() => {
      expect(screen.getByText(/Priya Sharma · Apr–Sep 2026/)).toBeInTheDocument();
    });
  });

  it('15. Employee surfaces never show employee codes (e.g. E01, E05)', async () => {
    (api.chat as any).mockResolvedValueOnce({
      messages: [{ code: 'C01', text: 'Your TDS for June 2026 is ₹0. Your annual taxable income remains below the tax threshold.' }],
      cards: [],
      chips: [{ label: 'Compare with May 2026' }],
      state: { certainty: 'Complete for this scope' },
    });

    const { container } = render(<ChatEMP currentUser="USER-E05" currentScenario={9} />);

    // Verify initial header and welcome text do not contain employee ID
    expect(container).toHaveTextContent('Neha Gupta');
    expect(container).not.toHaveTextContent(/\bE05\b/);
    expect(container).not.toHaveTextContent(/\bUSER-E05\b/);

    // Send inquiry
    const composer = screen.getByTestId('composer-textarea');
    fireEvent.change(composer, { target: { value: 'Why is my TDS zero?' } });
    fireEvent.click(screen.getByTestId('composer-send-btn'));

    await waitFor(() => {
      expect(screen.getByText(/Your TDS for June 2026 is ₹0/)).toBeInTheDocument();
    });

    // Verify whole employee chat container has zero employee codes
    expect(container.textContent).not.toMatch(/\bE0[1-9]\b/);
    expect(container.textContent).not.toMatch(/\bE1[0-6]\b/);
  });

  it('16. Every button inside any card uses our component class (no browser-default buttons)', () => {
    const testCards = [
      {
        id: 'card-approval',
        type: 'approval_card',
        title: 'Approval',
        data: {
          employee_name: 'Priya Sharma',
          employee_id: 'E01',
          period: 'Apr–Sep 2026',
          actions: ['Approve proposal for payroll', 'Edit with reason', 'Reject proposal'],
          status: 'pending',
        },
      },
      {
        id: 'card-clarify',
        type: 'clarifying_question',
        title: 'Which bonus type do you mean?',
        data: {
          choices: ['Annual performance bonus', 'Q2 Sales incentive'],
          selected_choice: null,
        },
      },
      {
        id: 'card-picker',
        type: 'employee_picker',
        title: 'Select employee',
        data: {
          employees: [{ employee_id: 'E01', name: 'Priya Sharma' }],
        },
      },
      {
        id: 'card-draft',
        type: 'query_draft',
        title: 'Query draft',
        data: {
          draft: {
            category: 'Discrepancy',
            months: ['2026-09'],
            description: 'Draft description',
          },
          notice: 'Send query notice',
        },
      },
      {
        id: 'card-status',
        type: 'query_status',
        title: 'Query status',
        data: {
          queries: [
            { query_id: 'Q1', status: 'Sent', description: 'Test 1' },
            { query_id: 'Q2', status: 'In review', description: 'Test 2' },
          ],
        },
      },
      {
        id: 'card-status-resolved',
        type: 'query_status',
        title: 'Query status resolved',
        data: {
          query_id: 'Q3',
          status: 'Resolved',
          description: 'Test 3',
        },
      },
      {
        id: 'card-faq',
        type: 'faq_answer',
        title: 'FAQ',
        data: {
          answer: 'Test answer',
          link_text: 'View policy',
          link_action: 'view-policy',
        },
      },
      {
        id: 'card-calc',
        type: 'show_calculation',
        title: 'Calculation',
        data: {},
      },
    ];

    const { container } = render(
      <div>
        {testCards.map((card) => (
          <CardRenderer
            key={card.id}
            card={card}
            onApprove={() => {}}
            onEdit={() => {}}
            onReject={() => {}}
            onApplySelection={() => {}}
            onSendQuery={() => {}}
            onCancelQueryDraft={() => {}}
            onTakeIntoReview={() => {}}
            onResolveQuery={() => {}}
            onDisputeQuery={() => {}}
            onCloseQuery={() => {}}
            onShowCalculation={() => {}}
            onSelectEmployee={() => {}}
          />
        ))}
      </div>
    );

    const buttons = container.querySelectorAll('button');
    expect(buttons.length).toBeGreaterThan(0);

    const allowedComponentClasses = [
      'hcm-button',
      'hcm-choice-chip',
      'hcm-suggestion-chip',
      'hcm-employee-picker-item',
    ];

    buttons.forEach((btn) => {
      const className = btn.className || '';
      expect(className.trim().length).toBeGreaterThan(0);
      const usesComponentClass = allowedComponentClasses.some((cls) => className.includes(cls));
      expect(usesComponentClass).toBe(true);
    });
  });

  describe('Approval Integrity & Exact Proposal ID Tests', () => {
    it('17. Clicking Approve on Priya\'s card sends her exact proposal_id and version', async () => {
      const mockApprove = vi.fn();
      const priyaCard = {
        id: 'card-approval-s1',
        type: 'approval_card',
        title: 'Approval',
        certainty: 'Complete for this scope',
        data: {
          employee_name: 'Priya Sharma',
          employee_id: 'E01',
          period: 'Apr–Sep 2026',
          scope_label: 'Priya Sharma · Apr–Sep 2026',
          proposal_id: 'PROP-SCENARIO-1',
          version: 1,
          actions: ['Approve proposal for payroll', 'Edit with reason', 'Reject proposal'],
          status: 'pending',
        },
      };

      render(<CardRenderer card={priyaCard} onApprove={mockApprove} />);
      const approveBtn = screen.getByRole('button', { name: /Approve proposal for payroll/i });
      expect(approveBtn).not.toBeDisabled();
      fireEvent.click(approveBtn);

      expect(mockApprove).toHaveBeenCalledTimes(1);
      expect(mockApprove).toHaveBeenCalledWith({
        proposal_id: 'PROP-SCENARIO-1',
        version: 1,
      });
    });

    it('18. Clicking Approve on the Sales incentive card sends its exact proposal_id and version', async () => {
      const mockApprove = vi.fn();
      const salesCard = {
        id: 'card-approval-s4-sales',
        type: 'approval_card',
        title: 'Approval',
        certainty: 'Complete for this scope',
        data: {
          scope_label: 'Q2 Sales incentive · Hyderabad Sales · Q2 2026-27',
          proposal_id: 'PROP-SCENARIO-4-SALES',
          version: 1,
          actions: ['Approve proposal for payroll', 'Edit with reason', 'Reject proposal'],
          status: 'pending',
        },
      };

      render(<CardRenderer card={salesCard} onApprove={mockApprove} />);
      const approveBtn = screen.getByRole('button', { name: /Approve proposal for payroll/i });
      expect(approveBtn).not.toBeDisabled();
      fireEvent.click(approveBtn);

      expect(mockApprove).toHaveBeenCalledTimes(1);
      expect(mockApprove).toHaveBeenCalledWith({
        proposal_id: 'PROP-SCENARIO-4-SALES',
        version: 1,
      });
    });

    it('19. On the Annual performance bonus card, Approve is disabled, reason is visible, and clicking it sends nothing', async () => {
      const mockApprove = vi.fn();
      const annualCard = {
        id: 'card-approval-s4-annual',
        type: 'approval_card',
        title: 'HR authorization',
        certainty: 'Incomplete',
        data: {
          scope_label: 'Annual performance bonus · Engineering · FY 2025-26',
          proposal_id: 'PROP-SCENARIO-4-ANNUAL',
          version: 1,
          disabled: true,
          blocking_reason: "2 items need input: Meera Nair's rating, Kavya Iyer's tax",
          actions: ['Approve proposal for payroll', 'Edit with reason', 'Reject proposal'],
          status: 'pending',
        },
      };

      render(<CardRenderer card={annualCard} onApprove={mockApprove} />);
      const approveBtn = screen.getByRole('button', { name: /Approve proposal for payroll/i });

      // 1. Button is disabled
      expect(approveBtn).toBeDisabled();
      expect(approveBtn).toHaveClass('hcm-button-disabled');
      expect(approveBtn).toHaveAttribute('aria-disabled', 'true');
      expect(approveBtn).toHaveAttribute('aria-describedby', 'approval-reason-card-approval-s4-annual');

      // 2. Reason is visible with matching id
      const note = screen.getByTestId('approval-disabled-note');
      expect(note).toBeInTheDocument();
      expect(note).toHaveAttribute('id', 'approval-reason-card-approval-s4-annual');
      expect(note).toHaveTextContent("2 items need input: Meera Nair's rating, Kavya Iyer's tax");

      // 3. Clicking sends nothing
      fireEvent.click(approveBtn);
      expect(mockApprove).not.toHaveBeenCalled();
    });

    it('20. If a card has no proposal_id or version, the Approve button is disabled and clicking it sends nothing', async () => {
      const mockApprove = vi.fn();

      // Case A: Missing proposal_id
      const cardNoId = {
        id: 'card-no-id',
        type: 'approval_card',
        title: 'Approval',
        certainty: 'Complete for this scope',
        data: {
          version: 1,
          actions: ['Approve proposal for payroll', 'Edit with reason', 'Reject proposal'],
          status: 'pending',
        },
      };

      const { unmount } = render(<CardRenderer card={cardNoId} onApprove={mockApprove} />);
      const btnNoId = screen.getByRole('button', { name: /Approve proposal for payroll/i });
      expect(btnNoId).toBeDisabled();
      expect(btnNoId).toHaveClass('hcm-button-disabled');
      expect(screen.getByTestId('approval-disabled-note')).toHaveTextContent(/Proposal identifier is missing/i);
      fireEvent.click(btnNoId);
      expect(mockApprove).not.toHaveBeenCalled();

      unmount();

      // Case B: Missing version
      const cardNoVersion = {
        id: 'card-no-version',
        type: 'approval_card',
        title: 'Approval',
        certainty: 'Complete for this scope',
        data: {
          proposal_id: 'PROP-SCENARIO-1',
          actions: ['Approve proposal for payroll', 'Edit with reason', 'Reject proposal'],
          status: 'pending',
        },
      };

      render(<CardRenderer card={cardNoVersion} onApprove={mockApprove} />);
      const btnNoVersion = screen.getByRole('button', { name: /Approve proposal for payroll/i });
      expect(btnNoVersion).toBeDisabled();
      expect(btnNoVersion).toHaveClass('hcm-button-disabled');
      expect(screen.getByTestId('approval-disabled-note')).toHaveTextContent(/Proposal version is missing/i);
      fireEvent.click(btnNoVersion);
      expect(mockApprove).not.toHaveBeenCalled();
    });
  });

  it('21. HR Query loop frontend test: Send on reply draft sends exact query_id and reply text only after confirm; Resolve sends exact query_id only after confirm; Cancel sends nothing', async () => {
    const mockSend = vi.fn();
    const mockCancel = vi.fn();
    const mockResolve = vi.fn();

    const replyDraftCard = {
      id: 'card-draft-QUERY-E05-SEPTEMBER',
      type: 'query_draft',
      title: "Reply to Neha Gupta's query",
      certainty: 'Complete for this scope',
      data: {
        query_id: 'QUERY-E05-SEPTEMBER',
        employee_label: 'Neha Gupta · E05',
        name_code: 'Neha Gupta · E05',
        period: 'September 2026',
        category: 'Loss of Pay (LOP)',
        description: 'Please review September LOP deduction of 3 days.',
        draft_reply: 'Attendance records reviewed and verified against biometric logs.',
        notice: 'Nothing is sent until HR clicks Send and confirms.',
      },
    };

    const { unmount } = render(
      <CardRenderer
        card={replyDraftCard}
        onSendQuery={mockSend}
        onCancelQueryDraft={mockCancel}
      />
    );

    expect(screen.getByText(/Reply to Neha Gupta's query/i)).toBeInTheDocument();
    const sendBtn = screen.getByRole('button', { name: /Send reply/i });
    const cancelBtn = screen.getByRole('button', { name: /Cancel/i });

    // 1. Cancel sends nothing to onSendQuery
    fireEvent.click(cancelBtn);
    expect(mockSend).not.toHaveBeenCalled();
    expect(mockCancel).toHaveBeenCalled();

    // 2. Click Send without confirm -> disabled, mockSend is NOT called
    expect(sendBtn).toBeDisabled();
    fireEvent.click(sendBtn);
    expect(mockSend).not.toHaveBeenCalled();

    // 3. Confirm and click Send -> starts empty, types text, and sends exact query_id and reply text
    const textarea = screen.getByRole('textbox', { name: /HR Reply Draft/i }) as HTMLTextAreaElement;
    expect(textarea.value).toBe('');
    expect(textarea.placeholder).toBe('Type your reply to Neha Gupta');
    fireEvent.change(textarea, { target: { value: 'Attendance records reviewed and verified against biometric logs.' } });

    const confirmCheckbox = screen.getByLabelText(/Confirm reply before sending/i);
    fireEvent.click(confirmCheckbox);
    expect(sendBtn).not.toBeDisabled();

    fireEvent.click(sendBtn);
    expect(mockSend).toHaveBeenCalledWith(
      'Attendance records reviewed and verified against biometric logs.',
      'QUERY-E05-SEPTEMBER'
    );

    unmount();

    // 4. Test Resolve query sends exact query_id
    const statusCard = {
      id: 'card-status-rev',
      type: 'query_status',
      title: 'Employee Queries',
      certainty: 'Complete for this scope',
      data: {
        queries: [
          {
            query_id: 'QUERY-E05-SEPTEMBER',
            status: 'In review',
            description: 'Please review September LOP deduction of 3 days.',
          },
        ],
      },
    };

    render(
      <CardRenderer
        card={statusCard}
        onResolveQuery={mockResolve}
      />
    );

    const resolveBtn = screen.getByRole('button', { name: /Resolve query/i });
    fireEvent.click(resolveBtn);
    expect(mockResolve).toHaveBeenCalledWith('QUERY-E05-SEPTEMBER');
  });

  describe('Live-test fixes F1-F10 verification', () => {
    it('F1 & R2: ComponentListCard renders non-empty proposal rows with title and recorded reasons from data', () => {
      const mockCard = {
        id: 'card-ready',
        type: 'component_list',
        title: 'Ready to approve',
        certainty: 'Complete for this scope',
        data: {
          title: 'Ready to approve',
          count: 2,
          items: [
            { label: 'Salary revision · Priya Sharma · E01', status: 'Ready' },
            { label: 'Sales incentive (Q2 2026-27) · Hyderabad Sales · FY 2025-26', status: 'Ready' },
          ],
        },
      };
      const { unmount } = render(<CardRenderer card={mockCard} />);
      expect(screen.getByText('Ready to approve')).toBeInTheDocument();
      expect(screen.getByText('Salary revision · Priya Sharma · E01')).toBeInTheDocument();
      expect(screen.getByText('Sales incentive (Q2 2026-27) · Hyderabad Sales · FY 2025-26')).toBeInTheDocument();
      unmount();

      const mockNeedsInputCard = {
        id: 'card-needs-input',
        type: 'component_list',
        title: 'Needs input first',
        certainty: 'Incomplete',
        data: {
          title: 'Needs input first',
          count: 1,
          items: [
            { label: 'Annual performance bonus · Engineering · FY 2025-26', reason: "Meera Nair's performance record is missing.", status: 'Pending input' },
          ],
        },
      };
      render(<CardRenderer card={mockNeedsInputCard} />);
      expect(screen.getByText('Needs input first')).toBeInTheDocument();
      expect(screen.getByText('Annual performance bonus · Engineering · FY 2025-26')).toBeInTheDocument();
      expect(screen.getByText("Meera Nair's performance record is missing.")).toBeInTheDocument();
    });

    it('R4: AssistantTurn renders refusal sentence exactly once when refusal card is present', () => {
      const refusalSentence = 'I cannot provide that information. I can help with payroll records you are authorized to access.';
      const messages = [{ code: 'C10', text: refusalSentence }];
      const cards = [
        {
          id: 'card-refusal',
          type: 'refusal_card',
          title: 'Access Restricted',
          certainty: 'Complete for this scope',
          data: {
            reason: refusalSentence,
          },
        },
      ];
      render(<AssistantTurn messages={messages} cards={cards} />);
      const elements = screen.getAllByText(refusalSentence);
      expect(elements).toHaveLength(1);
    });

    it('F2 Guard: Cards never render a certainty badge (.hcm-certainty-badge)', () => {
      const testCards = [
        {
          id: 'card-summary',
          type: 'proposal_summary',
          title: 'Team bonus run summary',
          certainty: 'Complete for this scope',
          data: {
            title: 'Team bonus run summary',
            metrics: [{ label: 'Eligible', value: '4' }],
          },
        },
        {
          id: 'card-ready',
          type: 'component_list',
          title: 'Ready to approve',
          certainty: 'Complete for this scope',
          data: {
            title: 'Ready to approve',
            items: [{ label: 'Salary revision · Priya Sharma · E01' }],
          },
        },
      ];
      for (const card of testCards) {
        const { container, unmount } = render(<CardRenderer card={card} />);
        const badge = container.querySelector('.hcm-certainty-badge');
        expect(badge).toBeNull();
        unmount();
      }
    });

    it('F4: ApprovalCard renders visible reason line directly above buttons when disabled', () => {
      const disabledCard = {
        id: 'card-approval-disabled',
        type: 'approval_card',
        title: 'Approval',
        certainty: 'Incomplete',
        data: {
          scope_label: 'Engineering Bonus · FY 2025-26',
          notice: 'Approving records this version.',
          actions: ['Approve proposal for payroll'],
          status: 'pending',
          proposal_id: 'PROP-BONUS-ENG',
          version: 1,
          disabled: true,
          blocking_reason: "Approval blocked: 1 item needs input.",
        },
      };
      const { container } = render(<CardRenderer card={disabledCard} />);
      const reasonEl = container.querySelector('.hcm-approval-disabled-reason');
      expect(reasonEl).not.toBeNull();
      expect(reasonEl).toHaveTextContent("Approval blocked: 1 item needs input.");
      const approveBtn = screen.getByRole('button', { name: /Approve proposal for payroll/i });
      expect(approveBtn).toBeDisabled();
      expect(approveBtn.getAttribute('aria-describedby')).toBe('approval-reason-card-approval-disabled');
    });

    it('F5 & F10: QueryDraftCard starts empty with placeholder and no duplicate notice', () => {
      const card = {
        id: 'card-draft',
        type: 'query_draft',
        title: 'Reply Draft',
        certainty: 'Incomplete',
        data: {
          query_id: 'Q-01',
          employee_label: 'Siddharth Jain · E02',
          name_code: 'Siddharth Jain · E02',
          period: 'September 2026',
          category: 'Tax deduction (TDS)',
          description: 'Why did TDS increase?',
        },
      };
      render(<CardRenderer card={card} />);
      const textarea = screen.getByRole('textbox', { name: /HR Reply Draft/i }) as HTMLTextAreaElement;
      expect(textarea.value).toBe('');
      expect(textarea.placeholder).toBe('Type your reply to Siddharth Jain');
      expect(screen.queryByText(/Nothing is sent until HR clicks Send and confirms/i)).toBeNull();
      expect(screen.getByText(/Confirm reply before sending/i)).toBeInTheDocument();
    });

    it('F10: QueryStatusCard renders HR reply for non-resolved and HR resolution reply for resolved', () => {
      const inReviewCard = {
        id: 'card-q-review',
        type: 'query_status',
        title: 'Query Status',
        certainty: 'Incomplete',
        data: {
          query_id: 'Q-02',
          status: 'In review',
          description: 'Check deduction',
          reply_text: 'Reviewing biometrics',
        },
      };
      const { unmount } = render(<CardRenderer card={inReviewCard} />);
      expect(screen.getByText('HR reply:')).toBeInTheDocument();
      expect(screen.queryByText('HR resolution reply:')).toBeNull();
      unmount();

      const resolvedCard = {
        id: 'card-q-resolved',
        type: 'query_status',
        title: 'Query Status',
        certainty: 'Complete for this scope',
        data: {
          query_id: 'Q-02',
          status: 'Resolved',
          description: 'Check deduction',
          resolution: 'Updated in October payroll',
        },
      };
      render(<CardRenderer card={resolvedCard} />);
      expect(screen.getByText('HR resolution reply:')).toBeInTheDocument();
      expect(screen.queryByText('HR reply:')).toBeNull();
    });
  });


  describe('Part B: HR Home Employee Picker Tests (B1 & B2)', () => {
    it('B1. HR01 home employee picker renders on welcome turn with 16 employees, search, departments, status tags, and scrollable container', async () => {
      const { unmount } = render(<ChatHR currentUser="HR01" />);

      // Must not call api.chat on initial mount
      expect(api.chat).not.toHaveBeenCalled();

      // Card title & prompt
      const pickerCard = await screen.findByTestId('employee-picker-card');
      expect(pickerCard).toHaveTextContent('Select employee');
      expect(pickerCard).toHaveTextContent('Pick an employee to see what you can do for them:');

      // Search box exists
      const searchInput = screen.getByTestId('employee-picker-search');
      expect(searchInput).toBeInTheDocument();

      // List container has mobile scroll constraints (max-height <= 340px, overflow-y: auto)
      const listContainer = screen.getByTestId('employee-picker-list');
      expect(listContainer).toHaveStyle({ maxHeight: '340px', overflowY: 'auto' });

      // Exactly 16 employees listed
      const employeeItems = screen.getAllByTestId(/^employee-item-E\d+/);
      expect(employeeItems).toHaveLength(16);

      // Verify specific recorded status tags
      expect(screen.getByTestId('status-tag-E01-hike-pending')).toHaveTextContent('Hike pending');
      expect(screen.getByTestId('status-tag-E02-hike-pending')).toHaveTextContent('Hike pending');
      expect(screen.getByTestId('status-tag-E03-needs-input')).toHaveTextContent('Needs input');
      expect(screen.getByTestId('status-tag-E05-open-query')).toHaveTextContent('Open query');
      expect(screen.getByTestId('status-tag-E08-leaving-november')).toHaveTextContent('Leaving November');
      expect(screen.getByTestId('status-tag-E09-needs-input')).toHaveTextContent('Needs input');
      expect(screen.getByTestId('status-tag-E10-leaving-october')).toHaveTextContent('Leaving October');
      expect(screen.getByTestId('status-tag-E11-leaving-october')).toHaveTextContent('Leaving October');
      expect(screen.getByTestId('status-tag-E12-needs-input')).toHaveTextContent('Needs input');
      expect(screen.getByTestId('status-tag-E12-leaving-october')).toHaveTextContent('Leaving October');

      // Untagged employees have no status tags
      expect(screen.queryByTestId('status-tag-E04-hike-pending')).toBeNull();
      expect(screen.queryByTestId('status-tag-E06-hike-pending')).toBeNull();
      expect(screen.queryByTestId('status-tag-E07-hike-pending')).toBeNull();
      expect(screen.queryByTestId('status-tag-E13-hike-pending')).toBeNull();
      expect(screen.queryByTestId('status-tag-E14-hike-pending')).toBeNull();
      expect(screen.queryByTestId('status-tag-E15-hike-pending')).toBeNull();
      expect(screen.queryByTestId('status-tag-E16-hike-pending')).toBeNull();

      unmount();
    });

    it('B1b. Employee picker search filters employees by name, ID, or department', async () => {
      const { unmount } = render(<ChatHR currentUser="HR01" />);
      const searchInput = await screen.findByTestId('employee-picker-search');

      // Filter by department: Sales
      fireEvent.change(searchInput, { target: { value: 'Sales' } });
      expect(screen.getByTestId('employee-item-E13')).toBeInTheDocument();
      expect(screen.getByTestId('employee-item-E14')).toBeInTheDocument();
      expect(screen.getByTestId('employee-item-E15')).toBeInTheDocument();
      expect(screen.queryByTestId('employee-item-E01')).toBeNull();

      // Filter by ID: E05
      fireEvent.change(searchInput, { target: { value: 'E05' } });
      expect(screen.getByTestId('employee-item-E05')).toBeInTheDocument();
      expect(screen.queryByTestId('employee-item-E13')).toBeNull();

      // Filter non-matching
      fireEvent.change(searchInput, { target: { value: 'NonExistent' } });
      expect(screen.getByText('No matching employees found')).toBeInTheDocument();

      unmount();
    });

    it('B1c. HR02 home employee picker renders only Sales employees (E13, E14, E15)', async () => {
      (api.getEmployees as any).mockResolvedValueOnce(
        MOCK_PICKER_EMPLOYEES.filter((emp) => ['E13', 'E14', 'E15'].includes(emp.employee_id))
      );
      const { unmount } = render(<ChatHR currentUser="HR02" />);

      const employeeItems = await screen.findAllByTestId(/^employee-item-E\d+/);
      expect(employeeItems).toHaveLength(3);
      expect(screen.getByTestId('employee-item-E13')).toBeInTheDocument();
      expect(screen.getByTestId('employee-item-E14')).toBeInTheDocument();
      expect(screen.getByTestId('employee-item-E15')).toBeInTheDocument();

      expect(screen.queryByTestId('employee-item-E01')).toBeNull();
      expect(screen.queryByTestId('employee-item-E05')).toBeNull();

      unmount();
    });

    it('B1d. Employee view (USER-E05) has empty cards on welcome turn', () => {
      const turn = createWelcomeTurn('USER-E05');
      expect(turn.cards).toEqual([]);
      expect(turn.messages?.[0].code).toBe('C31');
    });

    it('B2. Tapping employee on home picker sends "Show options for {Name}" as visible user turn and returns C70 with employee-tailored chips', async () => {
      (api.chat as any).mockResolvedValueOnce({
        messages: [{ code: 'C70', text: "Here's what you can do for Neha Gupta:" }],
        cards: [],
        chips: [
          { label: "Show Neha Gupta's September payslip" },
          { label: "Compare Neha Gupta's August and September pay" },
          { label: "Show Neha Gupta's query" },
        ],
        state: { employee_id: 'E05', intent: 'employee_options' },
      });

      const { unmount } = render(<ChatHR currentUser="HR01" />);

      // Tap Neha Gupta on home picker
      const nehaButton = await screen.findByTestId('employee-item-E05');
      fireEvent.click(nehaButton);

      // Visible user turn bubble must be rendered
      await waitFor(() => {
        expect(screen.getByText('Show options for Neha Gupta')).toBeInTheDocument();
      });

      // API must be called with message
      expect(api.chat).toHaveBeenCalledWith({
        userId: 'HR01',
        message: 'Show options for Neha Gupta',
      });

      // Assistant C70 message must be visible
      await waitFor(() => {
        expect(screen.getByText("Here's what you can do for Neha Gupta:")).toBeInTheDocument();
      });

      // Employee-scoped chips rendered
      expect(screen.getByText("Show Neha Gupta's September payslip")).toBeInTheDocument();
      expect(screen.getByText("Compare Neha Gupta's August and September pay")).toBeInTheDocument();
      expect(screen.getByText("Show Neha Gupta's query")).toBeInTheDocument();

      unmount();
    });

    it('24. V3 Resolve confirmation inside card: renders Confirm resolve and Cancel buttons, optional note input, and calls onConfirmResolve', () => {
      const mockConfirm = vi.fn();
      const mockCancel = vi.fn();

      const confirmCard = {
        id: 'card-confirm-resolve-QUERY-E05',
        type: 'query_status',
        title: 'Resolve query confirmation',
        data: {
          query_id: 'QUERY-E05-SEPTEMBER',
          employee_label: 'Neha Gupta · E05',
          status: 'In review',
          description: 'Please review September LOP deduction.',
          notice: 'Action requires confirmation.',
          is_resolve_confirmation: true,
        },
      };

      const { rerender } = render(
        <CardRenderer
          card={confirmCard}
          onConfirmResolve={mockConfirm}
          onCancelQueryDraft={mockCancel}
        />
      );

      // Verify card content
      expect(screen.getByText('Resolve query confirmation')).toBeInTheDocument();
      expect(screen.getByText('Action requires confirmation.')).toBeInTheDocument();
      expect(screen.getByLabelText(/Resolution note \(optional\)/i)).toBeInTheDocument();

      const confirmBtn = screen.getByRole('button', { name: /Confirm resolve/i });
      const cancelBtn = screen.getByRole('button', { name: /Cancel/i });
      expect(confirmBtn).toBeInTheDocument();
      expect(cancelBtn).toBeInTheDocument();

      // Type note and click Confirm resolve
      const textarea = screen.getByPlaceholderText(/Type optional resolution note/i);
      fireEvent.change(textarea, { target: { value: 'Manual swipe correction approved.' } });
      fireEvent.click(confirmBtn);

      expect(mockConfirm).toHaveBeenCalledWith('QUERY-E05-SEPTEMBER', 'Manual swipe correction approved.');

      // Test Cancel button with fresh render
      const { unmount: unmountCancel } = render(
        <CardRenderer
          card={{ ...confirmCard, id: 'card-confirm-resolve-QUERY-E05-cancel-test' }}
          onConfirmResolve={mockConfirm}
          onCancelQueryDraft={mockCancel}
        />
      );
      const cancelBtn2 = screen.getAllByRole('button', { name: /Cancel/i }).pop()!;
      fireEvent.click(cancelBtn2);
      expect(screen.getByText('Resolution cancelled.')).toBeInTheDocument();
      unmountCancel();
    });

    it('25. V2 Role exclusivity in QueryStatusCard: HR view never renders Dispute/Acknowledge; Employee view renders Dispute/Acknowledge and C72 when unreplied', () => {
      const mockDispute = vi.fn();
      const mockClose = vi.fn();

      const resolvedCard = {
        id: 'card-status-resolved',
        type: 'query_status',
        title: 'Query resolved',
        data: {
          query_id: 'QUERY-E05-SEPTEMBER',
          status: 'Resolved',
          description: 'Please check my attendance.',
          resolved_by: 'Anita Desai',
          resolved_at: '2026-11-02T12:00:00Z',
          reply_text: null,
          role: 'HR Admin',
        },
      };

      // 1. HR view: Dispute and Acknowledge buttons are NEVER present
      const { rerender } = render(
        <CardRenderer
          role="HR Admin"
          card={resolvedCard}
          onDisputeQuery={mockDispute}
          onCloseQuery={mockClose}
        />
      );

      expect(screen.queryByText('Dispute resolution')).toBeNull();
      expect(screen.queryByText('Acknowledge and close')).toBeNull();
      expect(screen.getByText('No reply was recorded before this query was resolved.')).toBeInTheDocument();
      expect(screen.getByText(/Resolved by Anita Desai on 2 Nov 2026/i)).toBeInTheDocument();

      // 2. Employee view: Dispute and Acknowledge buttons ARE present
      rerender(
        <CardRenderer
          role="Employee"
          card={{ ...resolvedCard, data: { ...resolvedCard.data, role: 'Employee' } }}
          onDisputeQuery={mockDispute}
          onCloseQuery={mockClose}
        />
      );

      expect(screen.getByText('Dispute resolution')).toBeInTheDocument();
      expect(screen.getByText('Acknowledge and close')).toBeInTheDocument();
    });
  });

});
