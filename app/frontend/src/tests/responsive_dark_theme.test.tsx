import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import React from 'react';
import fs from 'fs';
import path from 'path';

import { ChatHR } from '../design-system/components/chat/ChatHR';
import { ChatEMP } from '../design-system/components/chat/ChatEMP';
import fixturesData from './chat_scenario_fixtures.json';

const fixtures: Record<string, any> = fixturesData;

function sendChatMessage(text: string) {
  const textarea = screen.getByTestId('composer-textarea');
  const sendBtn = screen.getByTestId('composer-send-btn');
  fireEvent.change(textarea, { target: { value: text } });
  fireEvent.click(sendBtn);
}

function setViewport(width: number, height: number = 900) {

  Object.defineProperty(window, 'innerWidth', { writable: true, configurable: true, value: width });
  Object.defineProperty(window, 'innerHeight', { writable: true, configurable: true, value: height });
  window.dispatchEvent(new Event('resize'));
}

describe('Responsive Layout & Dark Theme Tests (Scenarios 1, 9, 13 at 1440px & 390px)', () => {
  beforeEach(() => {
    vi.spyOn(globalThis, 'fetch').mockImplementation((input: any, init?: any) => {
      const url = String(input);

      if (url.includes('/api/chat')) {
        let body: any = {};
        if (init?.body) {
          try {
            body = JSON.parse(String(init.body));
          } catch (e) {
            body = {};
          }
        }

        // Check if an action was dispatched
        if (body?.action === 'approve') {
          return Promise.resolve(
            new Response(
              JSON.stringify({
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
              }),
              { status: 200 }
            )
          );
        }

        const sNum = body?.context?.scenario_num || 1;
        const resp = fixtures[String(sNum)] || fixtures['1'];
        return Promise.resolve(new Response(JSON.stringify(resp), { status: 200 }));
      }

      if (url.includes('/api/reset')) {
        return Promise.resolve(new Response(JSON.stringify({ status: 'ok' }), { status: 200 }));
      }

      return Promise.resolve(new Response(JSON.stringify({}), { status: 200 }));
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('1. Dark Theme Token Verification: tokens.css defines dark palette meeting contrast rules', () => {
    const tokensPath = path.resolve(__dirname, '../design-system/tokens.css');
    const tokensContent = fs.readFileSync(tokensPath, 'utf-8');

    // Verify dark palette values
    expect(tokensContent).toContain('--color-background: #0B0F19');
    expect(tokensContent).toContain('--color-surface: #111827');
    expect(tokensContent).toContain('--color-text-primary: #F8FAFC');
    expect(tokensContent).toContain('--color-brand-accent: #14B8A6');
    expect(tokensContent).toContain('--color-status-success-text: #4ADE80');
    expect(tokensContent).toContain('--color-status-warning-text: #FBBF24');
    expect(tokensContent).toContain('--color-status-error-text: #F87171');

    // Verify responsive tokens
    expect(tokensContent).toContain('--breakpoint-mobile-max: 767px');
    expect(tokensContent).toContain('--breakpoint-tablet-min: 768px');
    expect(tokensContent).toContain('--breakpoint-desktop-min: 1024px');
    expect(tokensContent).toContain('--size-touch-target-min: 44px');
  });

  it('2. Scenario 1 at Desktop (1440 px): renders numbers, opens side panel, and approves with approver name', async () => {
    setViewport(1440);

    render(
      <ChatHR
        currentUser="HR01"
        currentScenario={1}
      />
    );
    sendChatMessage("Prepare Priya Sharma's pending back-dated hike.");

    // Verify exact numbers on cards
    await waitFor(() => {
      expect(screen.getByText('Expected net arrears')).toBeInTheDocument();
    });
    expect(screen.getByText('₹67,476')).toBeInTheDocument();
    expect(screen.getAllByText('₹71,200').length).toBeGreaterThan(0);
    expect(screen.getByText('₹3,724')).toBeInTheDocument();

    // Verify panel is initially closed
    expect(screen.queryByTestId('panel-hr')).not.toBeInTheDocument();

    // Action: click "Show calculation" chip
    const showCalcChip = screen.getByText('Show calculation');
    fireEvent.click(showCalcChip);

    // Verify side panel opens
    await waitFor(() => {
      expect(screen.getByTestId('panel-hr')).toBeInTheDocument();
    });
    expect(screen.getByText('Month-by-Month Proof')).toBeInTheDocument();

    // Check table data-labels and month cell
    expect(screen.getByText('04')).toBeInTheDocument();

    // Close panel
    const closeBtn = screen.getByTestId('panel-close-btn');
    fireEvent.click(closeBtn);
    expect(screen.queryByTestId('panel-hr')).not.toBeInTheDocument();

    // Action: Click approve
    const approveBtn = screen.getByText('Approve proposal for payroll');
    fireEvent.click(approveBtn);

    // Verify approved state shows Anita Desai and Version 1
    await waitFor(() => {
      const badge = screen.getByTestId('approval-status-badge');
      expect(badge).toBeInTheDocument();
      expect(badge).toHaveTextContent(/Approved and ready for payroll/i);
      expect(badge).toHaveTextContent(/Version 1/i);
      expect(badge).toHaveTextContent(/Anita Desai/i);
    });
  });

  it('3. Scenario 1 at Mobile (390 px): renders numbers, side panel operates as bottom sheet with stacked table', async () => {
    setViewport(390);

    render(
      <ChatHR
        currentUser="HR01"
        currentScenario={1}
      />
    );
    sendChatMessage("Prepare Priya Sharma's pending back-dated hike.");

    // Verify numbers present on mobile
    await waitFor(() => {
      expect(screen.getByText('Expected net arrears')).toBeInTheDocument();
    });
    expect(screen.getByText('₹67,476')).toBeInTheDocument();
    expect(screen.getAllByText('₹71,200').length).toBeGreaterThan(0);

    // Action: click "Show calculation" chip
    const showCalcChip = screen.getByText('Show calculation');
    fireEvent.click(showCalcChip);

    // Verify panel is open
    await waitFor(() => {
      expect(screen.getByTestId('panel-hr')).toBeInTheDocument();
    });

    // Verify table has stacked data-labels so nothing scrolls sideways
    const tableCells = screen.getByTestId('panel-hr').querySelectorAll('td[data-label]');
    expect(tableCells.length).toBeGreaterThan(0);
    expect(tableCells[0].getAttribute('data-label')).toBeTruthy();

    // Close panel
    fireEvent.click(screen.getByTestId('panel-close-btn'));
    expect(screen.queryByTestId('panel-hr')).not.toBeInTheDocument();
  });

  it('4. Scenario 9 at Desktop (1440 px): Employee chat without phone frame, numbers and detail proof work', async () => {
    setViewport(1440);

    render(
      <ChatEMP
        currentUser="USER-E01"
        currentScenario={9}
      />
    );
    sendChatMessage("Why is my September salary lower than August?");

    // Verify no fixed phone frame element exists
    expect(document.querySelector('.hcm-chat-emp-frame')).not.toBeInTheDocument();

    // Verify numbers: September Take-home (42,780), August Take-home (48,200), net change (-5,420)
    await waitFor(() => {
      expect(screen.getByText('September Take-Home')).toBeInTheDocument();
    });
    expect(screen.getByText('₹42,780')).toBeInTheDocument();
    expect(screen.getByText('₹48,200')).toBeInTheDocument();
    expect(screen.getAllByText(/5,420/).length).toBeGreaterThan(0);

    // Action: click "Show calculation" button
    const showCalcBtns = screen.getAllByText('Show calculation');
    fireEvent.click(showCalcBtns[0]);

    // Verify sheet/panel opens
    await waitFor(() => {
      expect(screen.getByTestId('sheet-emp')).toBeInTheDocument();
    });
    expect(screen.getByText('September Pay Breakdown')).toBeInTheDocument();
    expect(screen.getByText(/Loss of pay deduction/i)).toBeInTheDocument();

    // Close sheet
    fireEvent.click(screen.getByTestId('sheet-close-btn'));
    await waitFor(() => {
      expect(screen.queryByTestId('sheet-emp')).not.toBeInTheDocument();
    });
  });

  it('5. Scenario 9 at Mobile (390 px): Employee chat fills screen and bottom sheet calculation proof works', async () => {
    setViewport(390);

    render(
      <ChatEMP
        currentUser="USER-E01"
        currentScenario={9}
      />
    );
    sendChatMessage("Why is my September salary lower than August?");

    await waitFor(() => {
      expect(screen.getByText('September Take-Home')).toBeInTheDocument();
    });
    expect(screen.getByText('₹42,780')).toBeInTheDocument();

    // Open sheet
    const showCalcBtns = screen.getAllByText('Show calculation');
    fireEvent.click(showCalcBtns[0]);

    await waitFor(() => {
      expect(screen.getByTestId('sheet-emp')).toBeInTheDocument();
    });

    // Close sheet
    fireEvent.click(screen.getByTestId('sheet-close-btn'));
    await waitFor(() => {
      expect(screen.queryByTestId('sheet-emp')).not.toBeInTheDocument();
    });
  });

  it('6. Scenario 13 at Desktop (1440 px): HR settlement breakdown shows known recovery total and panel works', async () => {
    setViewport(1440);

    render(
      <ChatHR
        currentUser="HR01"
        currentScenario={13}
      />
    );
    sendChatMessage("Review settlement calculation for Imran Khan.");

    await waitFor(() => {
      expect(screen.getByText('Settlement Ledger Lines')).toBeInTheDocument();
    });

    // Known recoveries subtotal is 56,667
    expect(screen.getByText('₹56,667')).toBeInTheDocument();
    // Asset recovery is unresolved
    expect(screen.getAllByText(/Unresolved/i).length).toBeGreaterThan(0);

    // Open calculation panel
    const showCalcChip = screen.getByText('Show calculation');
    fireEvent.click(showCalcChip);

    await waitFor(() => {
      expect(screen.getByTestId('panel-hr')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByTestId('panel-close-btn'));
    expect(screen.queryByTestId('panel-hr')).not.toBeInTheDocument();
  });

  it('7. Scenario 13 at Mobile (390 px): HR settlement works with stacked table and bottom sheet', async () => {
    setViewport(390);

    render(
      <ChatHR
        currentUser="HR01"
        currentScenario={13}
      />
    );
    sendChatMessage("Review settlement calculation for Imran Khan.");

    await waitFor(() => {
      expect(screen.getByText('Settlement Ledger Lines')).toBeInTheDocument();
    });
    expect(screen.getByText('₹56,667')).toBeInTheDocument();

    // Open calculation panel
    fireEvent.click(screen.getByText('Show calculation'));

    await waitFor(() => {
      expect(screen.getByTestId('panel-hr')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByTestId('panel-close-btn'));
    expect(screen.queryByTestId('panel-hr')).not.toBeInTheDocument();
  });
});
