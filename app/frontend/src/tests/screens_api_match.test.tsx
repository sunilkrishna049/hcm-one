import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import React from 'react';
import fs from 'fs';
import path from 'path';

import { ChatHR } from '../design-system/components/chat/ChatHR';
import { ChatEMP } from '../design-system/components/chat/ChatEMP';
import fixturesData from './chat_scenario_fixtures.json';

const fixtures: Record<string, any> = fixturesData;

// Helper to load scenario JSON directly from data/generated/scenarios/
function loadScenarioData(scenarioNum: number) {
  const scenarioId = `scenario-${String(scenarioNum).padStart(2, '0')}`;
  const filePath = path.resolve(__dirname, `../../../../data/generated/scenarios/${scenarioId}.json`);
  if (!fs.existsSync(filePath)) {
    throw new Error(`Scenario file not found: ${filePath}`);
  }
  const raw = fs.readFileSync(filePath, 'utf-8');
  return JSON.parse(raw);
}

// Recursively gather all numbers from an API response object
function extractNumbersFromObject(obj: any, collected: Set<number> = new Set()): Set<number> {
  if (obj === null || obj === undefined) return collected;
  if (typeof obj === 'number') {
    collected.add(obj);
    return collected;
  }
  if (typeof obj === 'string') {
    // Check if it's formatted INR like "₹67,476" or "−₹5,420"
    const cleaned = obj.replace(/[₹,−-]/g, '').trim();
    const num = parseFloat(cleaned);
    if (!isNaN(num) && cleaned.length > 0 && /^\d+(?:\.\d+)?$/.test(cleaned)) {
      collected.add(num);
    }
    return collected;
  }
  if (Array.isArray(obj)) {
    for (const item of obj) {
      extractNumbersFromObject(item, collected);
    }
    return collected;
  }
  if (typeof obj === 'object') {
    for (const key of Object.keys(obj)) {
      extractNumbersFromObject(obj[key], collected);
    }
  }
  return collected;
}

// Extracts text from all text nodes separated by spaces so table cells/spans don't collide
function getSpacedText(element: HTMLElement): string {
  const walker = document.createTreeWalker(element, NodeFilter.SHOW_TEXT);
  const texts: string[] = [];
  let node: Node | null;
  while ((node = walker.nextNode())) {
    const val = node.nodeValue?.trim();
    if (val) texts.push(val);
  }
  return texts.join(' ');
}

// Setup fetch mock to return real chat responses from fixtures
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

describe('Automated checks that chat surfaces match real API responses (STEP 3)', () => {
  it('Scenario 1: ChatHR renders exact API numbers for Priya Sharma (gross arrears 71,200, net 67,476, PF 0, TDS 3,724)', async () => {
    const sc = loadScenarioData(1);
    const totals = sc.result.totals;
    expect(totals.gross_arrears.value).toBe(71200);
    expect(totals.net_arrears.value).toBe(67476);
    expect(totals.pf_change.employee.value).toBe(0);
    expect(totals.tds_impact.value).toBe(3724);

    render(
      <ChatHR
        currentUser="HR01"
        currentScenario={1}
        initialMessage="Prepare Priya Sharma's pending back-dated hike."
      />
    );

    await waitFor(() => {
      expect(screen.getByText('Expected net arrears')).toBeInTheDocument();
    });

    expect(screen.getByText('₹67,476')).toBeInTheDocument();
    expect(screen.getAllByText('₹71,200').length).toBeGreaterThan(0);

    expect(screen.queryByText(/New Annual CTC/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/CTC/i)).not.toBeInTheDocument();

    expect(screen.queryByText('72,000')).not.toBeInTheDocument();
    expect(screen.queryByText('90,000')).not.toBeInTheDocument();
  });

  it('Scenario 2: ChatHR renders exact API numbers for Arjun Rao (net arrears 7,099, gross arrears 7,200, PF change 101, TDS impact 0)', async () => {
    const sc = loadScenarioData(2);
    const totals = sc.result.totals;
    expect(totals.gross_arrears.value).toBe(7200);
    expect(totals.net_arrears.value).toBe(7099);
    expect(totals.pf_change.employee.value).toBe(101);
    expect(totals.tds_impact.value).toBe(0);

    render(
      <ChatHR
        currentUser="HR01"
        currentScenario={2}
        initialMessage="Prepare Arjun Rao's pending back-dated hike."
      />
    );

    await waitFor(() => {
      expect(screen.getByText('Expected net arrears')).toBeInTheDocument();
    });

    expect(screen.getByText('₹7,099')).toBeInTheDocument();
    expect(screen.getByText('₹7,200')).toBeInTheDocument();
    expect(screen.getByText('₹101')).toBeInTheDocument();
  });

  it('Scenario 3: ChatHR handles Kavya missing attendance with exact C07 copy & Not available for July', async () => {
    const sc = loadScenarioData(3);
    expect(sc.result.certainty).toBe('Incomplete');

    render(
      <ChatHR
        currentUser="HR01"
        currentScenario={3}
        initialMessage="Prepare Kavya Iyer's pending back-dated hike."
      />
    );

    await waitFor(() => {
      expect(screen.getByText('Known Monthly Differences')).toBeInTheDocument();
    });

    expect(screen.getAllByText(/Kavya Iyer/).length).toBeGreaterThan(0);
    expect(screen.getAllByText('Incomplete').length).toBeGreaterThan(0);

    const notAvailableElements = screen.getAllByText('Not available in generated data');
    expect(notAvailableElements.length).toBeGreaterThan(0);

    const fourThousandEightHundreds = screen.getAllByText('₹4,800');
    expect(fourThousandEightHundreds.length).toBeGreaterThanOrEqual(2);
  });

  it('Scenario 6: ChatHR renders exact settlement for Rahul Verma (final net 332,256, gratuity 201,923, gross 335,256)', async () => {
    const sc = loadScenarioData(6);
    expect(sc.result.final_net.value).toBe(332256);
    expect(sc.result.components.gratuity.amount.value).toBe(201923);
    expect(sc.result.gross_payables.value).toBe(335256);

    render(
      <ChatHR
        currentUser="HR01"
        currentScenario={6}
        initialMessage="Prepare settlement proposal for Rahul Verma."
      />
    );

    await waitFor(() => {
      expect(screen.getByText('Final net settlement')).toBeInTheDocument();
    });

    expect(screen.getByText('₹3,32,256')).toBeInTheDocument();
    expect(screen.getByText('₹3,35,256')).toBeInTheDocument();
    expect(screen.getByText('₹2,01,923')).toBeInTheDocument();
  });

  it('Scenario 9: ChatEMP renders exact Neha Gupta take-home (drop −5,420, August 48,200, LOP −5,000, PF ceiling −420)', async () => {
    const sc = loadScenarioData(9);
    expect(sc.result.after.net_pay.value).toBe(42780);
    expect(sc.result.net_change.value).toBe(-5420);
    expect(sc.result.reasons[0].effect_amount.value).toBe(-5000);
    expect(sc.result.reasons[1].effect_amount.value).toBe(-420);

    render(
      <ChatEMP
        currentUser="USER-E05"
        currentScenario={9}
        initialMessage="Why is my September salary lower than August?"
      />
    );

    await waitFor(() => {
      expect(screen.getByText('September Take-Home')).toBeInTheDocument();
    });

    expect(screen.getByText('₹42,780')).toBeInTheDocument();
    expect(screen.getAllByText(/5,420/).length).toBeGreaterThan(0);
    expect(screen.getByText('₹48,200')).toBeInTheDocument();
    expect(screen.getByText('−₹5,000')).toBeInTheDocument();
    expect(screen.getByText('−₹420')).toBeInTheDocument();

    expect(screen.queryByText('49,800')).not.toBeInTheDocument();
    expect(screen.queryByText('5,200')).not.toBeInTheDocument();
  });

  it('Scenario 10: ChatEMP renders exact Siddharth Jain TDS change (12,454, reason TDS −12,454, PF −560)', async () => {
    const sc = loadScenarioData(10);
    expect(sc.result.tds_change.value).toBe(12454);
    expect(sc.result.reasons[0].effect_amount.value).toBe(-12454);
    expect(sc.result.reasons[1].effect_amount.value).toBe(-560);

    render(
      <ChatEMP
        currentUser="USER-E06"
        currentScenario={10}
        initialMessage="Why did my TDS increase in September?"
      />
    );

    await waitFor(() => {
      expect(screen.getByText('September TDS Deduction')).toBeInTheDocument();
    });

    expect(screen.getByText('+₹12,454')).toBeInTheDocument();
    expect(screen.getByText('−₹12,454')).toBeInTheDocument();
    expect(screen.getByText('−₹560')).toBeInTheDocument();
  });

  it('Scenario 11: ChatEMP renders Pooja Das take-home drop of −420 with no earning change', async () => {
    const sc = loadScenarioData(11);
    expect(sc.result.net_change.value).toBe(-420);
    expect(sc.result.no_earning_component_change).toBe(true);

    render(
      <ChatEMP
        currentUser="USER-E16"
        currentScenario={11}
        initialMessage="Why did my take-home pay decrease in September when my gross did not change?"
      />
    );

    await waitFor(() => {
      expect(screen.getByText('Take-Home Net Change')).toBeInTheDocument();
    });

    expect(screen.getAllByText('−₹420').length).toBeGreaterThan(0);
    expect(screen.getByText(/No salary earning component change/i)).toBeInTheDocument();
  });

  it('Scenario 12: Colleague salary requested renders C10 Permission denied with ZERO target numbers', async () => {
    render(
      <ChatHR
        currentUser="HR02"
        currentScenario={12}
        initialMessage="Show me Priya Sharma's salary breakdown."
      />
    );

    await waitFor(() => {
      expect(screen.getByText('Permission Denied')).toBeInTheDocument();
    });

    expect(
      screen.getAllByText('I cannot provide that information. I can help with payroll records you are authorized to access.').length
    ).toBeGreaterThan(0);

    expect(screen.queryByText(/Priya Sharma's salary is/i)).not.toBeInTheDocument();
    expect(screen.queryByText('₹67,476')).not.toBeInTheDocument();
    expect(screen.queryByText('₹71,200')).not.toBeInTheDocument();
  });

  it('Scenario 13: Settlement with unverified asset recovery renders known recoveries 56,667 and final net Not available', async () => {
    const sc = loadScenarioData(13);
    expect(sc.result.known_recoveries_subtotal.value).toBe(56667);

    render(
      <ChatHR
        currentUser="HR01"
        currentScenario={13}
        initialMessage="Review settlement calculation for Imran Khan."
      />
    );

    await waitFor(() => {
      expect(screen.getByText('Settlement Breakdown (Unresolved Component)')).toBeInTheDocument();
    });

    expect(screen.getAllByText('₹56,667').length).toBeGreaterThan(0);
    const notAvail = screen.getAllByText('Not available in generated data');
    expect(notAvail.length).toBeGreaterThan(0);
  });

  it('GUARD TEST: Fails if any payroll number on rendered chat cards is not present in the API response', async () => {
    // Test across scenarios 1, 2, 3, 6, 9, 10, 11, 12, 13
    for (const sNum of [1, 2, 3, 6, 9, 10, 11, 12, 13]) {
      const sc = loadScenarioData(sNum);
      const fixture = fixtures[String(sNum)];
      const allowedNumbers = extractNumbersFromObject(sc);
      extractNumbersFromObject(fixture, allowedNumbers);

      // Add allowed non-payroll UI numbers: year, month numbers, scenario ids, versions, calendar dates, clock hours/minutes
      const standardAllowed = new Set([
        2025, 2026, 2027, // years
        ...Array.from({ length: 31 }, (_, i) => i + 1), // dates / days 1..31
        ...Array.from({ length: 60 }, (_, i) => i), // clock hours / minutes 0..59
        100, // percentage max
        390, 1440, // frame widths
      ]);

      let renderedResult;
      if ([1, 2, 3, 6, 12, 13].includes(sNum)) {
        renderedResult = render(
          <ChatHR
            currentUser={sNum === 12 ? 'HR02' : 'HR01'}
            currentScenario={sNum}
            initialMessage="Test"
          />
        );
      } else {
        const empUser = sNum === 9 ? 'USER-E05' : sNum === 10 ? 'USER-E06' : 'USER-E16';
        renderedResult = render(
          <ChatEMP
            currentUser={empUser}
            currentScenario={sNum}
            initialMessage="Test"
          />
        );
      }

      await waitFor(() => {
        expect(renderedResult.container).toBeInTheDocument();
      });

      // Extract all numeric text content from the rendered HTML using spaced text to prevent cell concatenation
      const text = getSpacedText(renderedResult.container);
      const matches = text.match(/-?\b\d[\d,]*(?:\.\d+)?\b/g) || [];

      for (const match of matches) {
        const cleanStr = match.replace(/,/g, '');
        const num = Math.abs(parseFloat(cleanStr));
        if (isNaN(num)) continue;
        if (standardAllowed.has(num)) continue;

        // The number MUST exist in the API response or fixture
        const isInApi = allowedNumbers.has(num) || allowedNumbers.has(-num);
        if (!isInApi) {
          throw new Error(
            `GUARD FAILED: Found payroll number '${match}' (${num}) in Scenario ${sNum} chat screen that does NOT exist in API response!`
          );
        }
        expect(isInApi).toBe(true);
      }

      renderedResult.unmount();
    }
  });
});
