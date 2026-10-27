import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import React from 'react';
import { ChatHR } from '../design-system/components/chat/ChatHR';
import { ChatEMP } from '../design-system/components/chat/ChatEMP';
import { App } from '../App';
import { api } from '../services/api';

vi.mock('../services/api', () => ({
  api: {
    chat: vi.fn(),
    resetDemo: vi.fn().mockResolvedValue({ status: 'ok' }),
  },
  setCurrentUserId: vi.fn(),
}));

describe('Chat Action Click Tests (React Testing Library)', () => {
  beforeEach(() => {
    vi.resetAllMocks();
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
                query_id: 'QUERY-E05-20260901',
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
                query_id: 'QUERY-E05-20260901',
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
          context: expect.objectContaining({ query_id: 'QUERY-E05-20260901' }),
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
          context: expect.objectContaining({ query_id: 'QUERY-E05-20260901' }),
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
            query_id: 'QUERY-E05-20260901',
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
          title: 'Calculation Proof & Month Breakdown',
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
      expect(screen.getByText('Calculation Proof & Month Breakdown')).toBeInTheDocument();
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
          certainty: 'Needs HR decision',
          data: {
            question: 'Which bonus type do you mean?',
            choices: [
              'Annual performance bonus, FY 2025-26, Engineering',
              'Q2 Sales incentive, Hyderabad Sales',
            ],
            selected_choice: 'Annual performance bonus, FY 2025-26, Engineering',
          },
        },
      ],
      chips: [
        { label: 'Annual performance bonus, FY 2025-26, Engineering' },
        { label: 'Q2 Sales incentive, Hyderabad Sales' },
      ],
    });

    render(<ChatHR currentUser="HR01" currentScenario={4} />);

    // Tap "Prepare a bonus proposal" starter chip
    fireEvent.click(screen.getByText('Prepare a bonus proposal'));

    await waitFor(() => {
      expect(screen.getAllByText('Which bonus type do you mean?').length).toBeGreaterThanOrEqual(1);
      expect(screen.getAllByText('Annual performance bonus, FY 2025-26, Engineering').length).toBeGreaterThanOrEqual(1);
      expect(screen.getAllByText('Q2 Sales incentive, Hyderabad Sales').length).toBeGreaterThanOrEqual(1);
    });
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
          certainty: 'Complete for this scope',
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
            status: 'Needs HR decision',
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
      // Label "Known Eligible Gross" is displayed
      expect(screen.getByText('Known Eligible Gross')).toBeInTheDocument();
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

});

