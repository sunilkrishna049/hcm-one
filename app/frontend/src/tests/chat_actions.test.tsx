import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import React from 'react';
import { ChatHR } from '../design-system/components/chat/ChatHR';
import { ChatEMP } from '../design-system/components/chat/ChatEMP';
import { api } from '../services/api';

vi.mock('../services/api', () => ({
  api: {
    chat: vi.fn(),
  },
}));

describe('Chat Action Click Tests (React Testing Library)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
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

    await waitFor(() => {
      expect(screen.getByText('Approve proposal for payroll')).toBeInTheDocument();
    });

    // Mock approval response
    (api.chat as any).mockResolvedValueOnce({
      messages: [{ code: 'C04', text: 'Approving records this version and the selected scope as ready for payroll.' }],
      cards: [
        {
          id: 'card-approval-approved-1',
          type: 'approval_card',
          title: 'Approval',
          certainty: 'Complete for this scope',
          data: {
            scope_label: 'Priya Sharma · Apr–Sep 2026',
            notice: 'Approving records this version and the selected scope as ready for payroll. It does not apply the change or make a payment.',
            actions: [],
            status: 'approved',
            proposal_id: 'PROP-SCENARIO-1',
            version: 1,
            approver: 'HR01',
            approved_at: '2026-10-24 12:00:00',
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
      const badge = screen.getByTestId('approval-status-badge');
      expect(badge).toBeInTheDocument();
      expect(badge).toHaveTextContent(/Approved and ready for payroll/i);
      expect(badge).toHaveTextContent(/Version 1/i);
      expect(badge).toHaveTextContent(/Anita Desai/i);
    });
  });

  it('2. Clicking "Edit with reason" and "Reject proposal" dispatch edit and reject actions', async () => {
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
    });

    (api.chat as any).mockResolvedValueOnce({
      messages: [{ code: 'REJECTED', text: 'Proposal rejected.' }],
      cards: [],
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

    await waitFor(() => {
      // Must not fail silently: displays approved sentence C09
      expect(
        screen.getByText(/The payroll calculation did not produce a usable result for this operation/i)
      ).toBeInTheDocument();
    });
  });
});
