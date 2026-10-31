import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import React from 'react';
import fs from 'fs';
import path from 'path';

import { ChatHR } from '../design-system/components/chat/ChatHR';
import { ChatEMP } from '../design-system/components/chat/ChatEMP';
import { AssistantTurn } from '../design-system/components/chat/AssistantTurn';
import { MonthTableCard } from '../design-system/components/cards/MonthTableCard';
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

        const effectiveUserId = body?.user_id || body?.userId;
        let sNum = body?.context?.scenario_num;
        if (!sNum) {
          const msg = (body?.message || '').toLowerCase();
          if (msg.includes('priya') || msg.includes('sharma')) sNum = effectiveUserId === 'HR02' ? 12 : 1;
          else if (msg.includes('arjun') || msg.includes('rao')) sNum = 2;
          else if (msg.includes('kavya') || msg.includes('iyer')) sNum = 3;
          else if (msg.includes('meera') || msg.includes('nair')) sNum = 5;
          else if (msg.includes('annual') || msg.includes('sales') || msg.includes('bonus')) sNum = 4;
          else if (msg.includes('rahul') || msg.includes('verma')) sNum = 6;
          else if (msg.includes('lakshmi') || msg.includes('reddy')) sNum = 7;
          else if (msg.includes('imran') || msg.includes('khan')) {
            sNum = (msg.includes('calculation') || msg.includes('review') || msg.includes('breakdown')) ? 13 : 8;
          } else if (msg.includes('september') && (msg.includes('lower') || msg.includes('salary') || msg.includes('pay'))) sNum = 9;
          else if (msg.includes('tds')) sNum = 10;
          else if (msg.includes('gross') || msg.includes('decrease') || msg.includes('basic pay')) sNum = 11;
          else if (effectiveUserId === 'USER-E05' || effectiveUserId === 'USER-E01') sNum = 9;
          else if (effectiveUserId === 'USER-E06') sNum = 10;
          else if (effectiveUserId === 'USER-E16') sNum = 11;
          else if (effectiveUserId === 'HR02') sNum = 12;
          else sNum = 1;
        }
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
    expect(tokensContent).toContain('--color-background: #050505');
    expect(tokensContent).toContain('--color-surface: #0D0D0D');
    expect(tokensContent).toContain('--color-text-primary: #F2F2F2');
    expect(tokensContent).toContain('--color-brand-accent: #1150BF');
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
    expect(screen.getByText('Month-by-month proof')).toBeInTheDocument();

    // Check table data-labels and month cell
    expect(screen.getByText('Apr')).toBeInTheDocument();

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
      expect(screen.getByText('September take-home')).toBeInTheDocument();
    });
    expect(screen.getByText('₹42,780')).toBeInTheDocument();
    expect(screen.getByText('₹48,200')).toBeInTheDocument();
    expect(screen.getAllByText(/5,420/).length).toBeGreaterThan(0);

    // Action: click "Show calculation" or "Show breakdown" button
    const showCalcBtns = screen.getAllByText(/Show (breakdown|calculation)/i);
    fireEvent.click(showCalcBtns[0]);

    // Verify sheet/panel opens
    await waitFor(() => {
      expect(screen.getByTestId('sheet-emp')).toBeInTheDocument();
    });
    expect(screen.getByText('September pay breakdown')).toBeInTheDocument();
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
      expect(screen.getByText('September take-home')).toBeInTheDocument();
    });
    expect(screen.getByText('₹42,780')).toBeInTheDocument();

    // Open sheet
    const showCalcBtns = screen.getAllByText(/Show (breakdown|calculation)/i);
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
      expect(screen.getByText('Settlement ledger lines')).toBeInTheDocument();
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
      expect(screen.getByText('Settlement ledger lines')).toBeInTheDocument();
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

  it('8. Scrollbar styles use tokens without white default browser scrollbars', () => {
    const tokensPath = path.resolve(__dirname, '../design-system/tokens.css');
    const tokensContent = fs.readFileSync(tokensPath, 'utf-8');

    expect(tokensContent).toContain('--scrollbar-track-color: transparent');
    expect(tokensContent).toContain('--scrollbar-thumb-color: var(--color-divider)');
    expect(tokensContent).toContain('--scrollbar-thumb-hover-color: var(--color-border-interactive)');
    expect(tokensContent).toContain('--scrollbar-width: 6px');
    expect(tokensContent).toContain('--scrollbar-width-firefox: thin');

    expect(tokensContent).toContain('scrollbar-width: var(--scrollbar-width-firefox)');
    expect(tokensContent).toContain('scrollbar-color: var(--scrollbar-thumb-color) var(--scrollbar-track-color)');
    expect(tokensContent).toContain('*::-webkit-scrollbar');
    expect(tokensContent).toContain('background-color: var(--scrollbar-thumb-color)');

    const componentsPath = path.resolve(__dirname, '../design-system/components.css');
    const componentsContent = fs.readFileSync(componentsPath, 'utf-8');
    expect(componentsContent).not.toMatch(/#[0-9a-fA-F]{3,8}/);
  });

  it('9. Suggestion chips wrap at desktop width and scroll horizontally at mobile width with fade', () => {
    const componentsPath = path.resolve(__dirname, '../design-system/components.css');
    const componentsContent = fs.readFileSync(componentsPath, 'utf-8');

    // Desktop/tablet wrapping rule
    expect(componentsContent).toContain('.hcm-suggestion-chips-track {');
    expect(componentsContent).toContain('flex-wrap: wrap;');

    // Mobile swipe sideways rule & hidden scrollbar & fade
    expect(componentsContent).toContain('scrollbar-width: none;');
    expect(componentsContent).toContain('flex-wrap: nowrap;');
    expect(componentsContent).toContain('background: linear-gradient(to right, transparent, var(--color-surface))');
  });

  it('10. Composer placeholder differs by role: employee vs HR', () => {
    const { unmount: unmountEmp } = render(<ChatEMP currentUser="USER-E05" currentScenario={9} />);
    const empInput = screen.getByTestId('composer-textarea');
    expect(empInput).toHaveAttribute('placeholder', 'Ask a question about your salary…');
    unmountEmp();

    const { unmount: unmountHr } = render(<ChatHR currentUser="HR01" currentScenario={1} />);
    const hrInput = screen.getByTestId('composer-textarea');
    expect(hrInput).toHaveAttribute('placeholder', 'Ask about payroll, arrears or settlements…');
    unmountHr();

    expect(empInput.getAttribute('placeholder')).not.toEqual(hrInput.getAttribute('placeholder'));
  });

  it('11. Payslip card section order, sentence case labels, and tokens layout in MonthTableCard', () => {
    const singleMonthCard = {
      id: 'card-payslip-2026-06',
      type: 'month_table',
      title: 'Payslip · June 2026',
      certainty: 'Complete for this scope',
      data: {
        employee_id: 'E05',
        employee_name: 'Neha Gupta',
        month: '2026-06',
        basic: 25000,
        hra: 10000,
        special_allowance: 8000,
        da: 2000,
        gross_pay: 45000,
        pf: 2220,
        tds: 0,
        total_deductions: 2220,
        net_pay: 42780,
      },
    };

    const { container, unmount } = render(<MonthTableCard card={singleMonthCard} />);

    // Verify card title
    expect(screen.getByText('Payslip · June 2026')).toBeInTheDocument();

    // Verify section titles
    expect(screen.getByText('Earnings')).toBeInTheDocument();
    expect(screen.getByText('Deductions')).toBeInTheDocument();

    // Verify sentence case labels
    expect(screen.getByText('Basic pay')).toBeInTheDocument();
    expect(screen.getByText('Gross pay')).toBeInTheDocument();
    expect(screen.getByText('Total deductions')).toBeInTheDocument();
    expect(screen.getByText('Net pay')).toBeInTheDocument();

    // Verify section order: Earnings -> Basic pay -> Gross pay -> Deductions -> PF -> Total deductions -> Net pay
    const allText = container.textContent || '';
    const idxEarnings = allText.indexOf('Earnings');
    const idxBasicPay = allText.indexOf('Basic pay');
    const idxGrossPay = allText.indexOf('Gross pay');
    const idxDeductions = allText.indexOf('Deductions');
    const idxPF = allText.indexOf('PF');
    const idxTotalDeductions = allText.indexOf('Total deductions');
    const idxNetPay = allText.indexOf('Net pay');

    expect(idxEarnings).toBeLessThan(idxBasicPay);
    expect(idxBasicPay).toBeLessThan(idxGrossPay);
    expect(idxGrossPay).toBeLessThan(idxDeductions);
    expect(idxDeductions).toBeLessThan(idxPF);
    expect(idxPF).toBeLessThan(idxTotalDeductions);
    expect(idxTotalDeductions).toBeLessThan(idxNetPay);

    // Verify CSS classes are used instead of inline styles
    const table = container.querySelector('table');
    expect(table).toHaveClass('hcm-payslip-table');
    expect(table?.innerHTML).not.toContain('style=');

    unmount();
  });

  it('12. Certainty badge from reply level: render e05_tds fixture (no cards) and assert "Complete for this scope" is visible', () => {
    const fixture = fixtures['e05_tds'];
    expect(fixture.cards).toHaveLength(0);
    render(
      <AssistantTurn
        messages={fixture.messages}
        cards={fixture.cards}
        state={fixture.state}
      />
    );
    const badge = screen.getByText('Complete for this scope');
    expect(badge).toBeInTheDocument();
    expect(badge).toBeVisible();
  });

  it('13. Contrast test: token values meet WCAG AA minimum 4.5:1 contrast requirements', () => {
    const tokensPath = path.resolve(__dirname, '../design-system/tokens.css');
    const tokensContent = fs.readFileSync(tokensPath, 'utf-8');

    function extractToken(varName: string): string {
      const match = tokensContent.match(new RegExp(varName + ':\\s*([^;]+);'));
      if (!match) throw new Error('Token ' + varName + ' not found in tokens.css');
      return match[1].trim();
    }

    function hexToRgb(hex: string): [number, number, number] {
      const clean = hex.replace('#', '').trim();
      return [
        parseInt(clean.substring(0, 2), 16),
        parseInt(clean.substring(2, 4), 16),
        parseInt(clean.substring(4, 6), 16),
      ];
    }

    function relativeLuminance(r: number, g: number, b: number): number {
      const a = [r, g, b].map((v) => {
        v /= 255;
        return v <= 0.04045 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
      });
      return a[0] * 0.2126 + a[1] * 0.7152 + a[2] * 0.0722;
    }

    function contrastRatio(hex1: string, hex2: string): number {
      const [r1, g1, b1] = hexToRgb(hex1);
      const [r2, g2, b2] = hexToRgb(hex2);
      const l1 = relativeLuminance(r1, g1, b1);
      const l2 = relativeLuminance(r2, g2, b2);
      const lighter = Math.max(l1, l2);
      const darker = Math.min(l1, l2);
      return (lighter + 0.05) / (darker + 0.05);
    }

    const primary = extractToken('--color-brand-accent');
    const primaryText = extractToken('--color-primary-text');
    const pageBg = extractToken('--color-background');
    const surface = extractToken('--color-surface');
    const mutedText = extractToken('--color-text-muted');
    const mainText = extractToken('--color-text-primary');

    // 1. white on Primary >= 4.5:1
    const whiteOnPrimary = contrastRatio('#FFFFFF', primary);
    expect(whiteOnPrimary).toBeGreaterThanOrEqual(4.5);

    // 2. Primary text on Page background >= 4.5:1
    const primaryTextOnPage = contrastRatio(primaryText, pageBg);
    expect(primaryTextOnPage).toBeGreaterThanOrEqual(4.5);

    // 3. Primary text on Surface >= 4.5:1
    const primaryTextOnSurface = contrastRatio(primaryText, surface);
    expect(primaryTextOnSurface).toBeGreaterThanOrEqual(4.5);

    // 4. Muted text on Surface >= 4.5:1
    const mutedTextOnSurface = contrastRatio(mutedText, surface);
    expect(mutedTextOnSurface).toBeGreaterThanOrEqual(4.5);

    // 5. Main text on Surface >= 4.5:1
    const mainTextOnSurface = contrastRatio(mainText, surface);
    expect(mainTextOnSurface).toBeGreaterThanOrEqual(4.5);
  });
});
