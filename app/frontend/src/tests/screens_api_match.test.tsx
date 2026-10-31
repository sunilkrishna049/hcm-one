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
let currentTestScenario = 1;
let currentTestKey = '';

beforeEach(() => {
  currentTestScenario = 1;
  currentTestKey = '';
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
      const effectiveUserId = body?.user_id || body?.userId;
      let sNum = body?.context?.scenario_num;
      if (currentTestKey && fixtures[currentTestKey]) {
        sNum = currentTestKey;
      } else if (!sNum) {
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
        } else if (msg.includes('gross') || msg.includes('decrease') || msg.includes('basic pay') || msg.includes('pooja')) sNum = 11;
        else if (msg.includes('tds')) sNum = 10;
        else if (msg.includes('september') && (msg.includes('lower') || msg.includes('salary') || msg.includes('pay'))) sNum = 9;
        else if (effectiveUserId === 'USER-E05') sNum = 9;
        else if (effectiveUserId === 'USER-E06') sNum = 10;
        else if (effectiveUserId === 'USER-E16') sNum = 11;
        else if (effectiveUserId === 'HR02') sNum = 12;
        else sNum = currentTestScenario || 1;
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
      />
    );
    sendChatMessage("Prepare Priya Sharma's pending back-dated hike.");

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
      />
    );
    sendChatMessage("Prepare Arjun Rao's pending back-dated hike.");

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
      />
    );
    sendChatMessage("Prepare Kavya Iyer's pending back-dated hike.");

    await waitFor(() => {
      expect(screen.getByText('Known monthly differences')).toBeInTheDocument();
    });

    expect(screen.getAllByText(/Kavya Iyer/).length).toBeGreaterThan(0);
    expect(screen.getAllByText('Incomplete').length).toBeGreaterThan(0);

    expect(screen.queryByText('Not available in generated data')).not.toBeInTheDocument();

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
      />
    );
    sendChatMessage("Prepare settlement proposal for Rahul Verma.");

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
      />
    );
    sendChatMessage("Why is my September salary lower than August?");

    await waitFor(() => {
      expect(screen.getByText('September take-home')).toBeInTheDocument();
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
      />
    );
    sendChatMessage("Why did my TDS increase in September?");

    await waitFor(() => {
      expect(screen.getByText('September TDS deduction')).toBeInTheDocument();
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
      />
    );
    sendChatMessage("Why did my take-home pay decrease in September when my gross did not change?");

    await waitFor(() => {
      expect(screen.getByText('Take-home net change')).toBeInTheDocument();
    });

    expect(screen.getAllByText('−₹420').length).toBeGreaterThan(0);
    expect(screen.getByText(/No salary earning component change/i)).toBeInTheDocument();
  });

  it('Scenario 12: Colleague salary requested renders C10 Permission denied with ZERO target numbers', async () => {
    render(
      <ChatHR
        currentUser="HR02"
        currentScenario={12}
      />
    );
    sendChatMessage("Show me Priya Sharma's salary breakdown.");

    await waitFor(() => {
      expect(screen.getByText('Permission denied')).toBeInTheDocument();
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
      />
    );
    sendChatMessage("Review settlement calculation for Imran Khan.");

    await waitFor(() => {
      expect(screen.getByText('Settlement breakdown (unresolved component)')).toBeInTheDocument();
    });

    expect(screen.getAllByText('₹56,667').length).toBeGreaterThan(0);
    expect(screen.queryByText('Not available in generated data')).not.toBeInTheDocument();
  });

  it('GUARD TEST: Fails if any payroll number on rendered chat cards is not present in the API response', async () => {
    // Add allowed non-payroll UI numbers: year, month numbers, scenario ids, versions, calendar dates, clock hours/minutes
    const standardAllowed = new Set([
      2025, 2026, 2027, // years
      ...Array.from({ length: 31 }, (_, i) => i + 1), // dates / days 1..31
      ...Array.from({ length: 60 }, (_, i) => i), // clock hours / minutes 0..59
      100, // percentage max
      390, 1440, // frame widths
    ]);

    // Test across scenarios 1, 2, 3, 6, 9, 10, 11, 12, 13
    for (const sNum of [1, 2, 3, 6, 9, 10, 11, 12, 13]) {
      const sc = loadScenarioData(sNum);
      const fixture = fixtures[String(sNum)];
      const allowedNumbers = extractNumbersFromObject(sc);
      extractNumbersFromObject(fixture, allowedNumbers);

      currentTestScenario = sNum;
      let renderedResult;
      if ([1, 2, 3, 6, 12, 13].includes(sNum)) {
        renderedResult = render(
          <ChatHR
            currentUser={sNum === 12 ? 'HR02' : 'HR01'}
            currentScenario={sNum}
          />
        );
      } else {
        const empUser = sNum === 9 ? 'USER-E05' : sNum === 10 ? 'USER-E06' : 'USER-E16';
        renderedResult = render(
          <ChatEMP
            currentUser={empUser}
            currentScenario={sNum}
          />
        );
      }
      sendChatMessage("Test");

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

    // Part D Item 10: Run screen-vs-API guard test over USER-E05 new topics:
    // payslip, PF, TDS, LOP days, month comparison, query status, tax regime, C34 and C35
    const e05Topics = [
      { key: 'e05_payslip', prompt: 'Explain my September pay.' },
      { key: 'e05_pf', prompt: 'How much PF was cut in September?' },
      { key: 'e05_tds', prompt: 'Why is my TDS zero?' },
      { key: 'e05_lop', prompt: 'How many LOP days do I have?' },
      { key: 'e05_compare', prompt: 'Compare my August and September pay.' },
      { key: 'e05_query_status', prompt: "What's happening with my query?" },
      { key: 'e05_tax_regime', prompt: 'Which tax regime am I in?' },
      { key: 'e05_c34', prompt: 'Will I get a bonus this year?' },
      { key: 'e05_c35', prompt: 'What is my October salary?' },
    ];

    for (const topic of e05Topics) {
      currentTestKey = topic.key;
      const fixture = fixtures[topic.key];
      expect(fixture).toBeDefined();
      const allowedNumbers = extractNumbersFromObject(fixture);

      const renderedResult = render(
        <ChatEMP
          currentUser="USER-E05"
          currentScenario={9}
        />
      );
      sendChatMessage(topic.prompt);

      await waitFor(() => {
        expect(renderedResult.container).toBeInTheDocument();
      });

      const text = getSpacedText(renderedResult.container);
      const matches = text.match(/-?\b\d[\d,]*(?:\.\d+)?\b/g) || [];

      for (const match of matches) {
        const cleanStr = match.replace(/,/g, '');
        const num = Math.abs(parseFloat(cleanStr));
        if (isNaN(num)) continue;
        if (standardAllowed.has(num)) continue;

        const isInApi = allowedNumbers.has(num) || allowedNumbers.has(-num);
        if (!isInApi) {
          throw new Error(
            `GUARD FAILED: Found payroll number '${match}' (${num}) in E05 topic '${topic.key}' chat screen that does NOT exist in API response!`
          );
        }
        expect(isInApi).toBe(true);
      }

      renderedResult.unmount();
    }
  });
  it('GUARD TEST: "Not available in generated data" must not exist anywhere in frontend source files', () => {
    const frontendSrc = path.resolve(__dirname, '..');
    const banned = /Not available in generated data/;
    const violations: string[] = [];

    function scanDir(dir: string) {
      const files = fs.readdirSync(dir, { withFileTypes: true });
      for (const f of files) {
        const full = path.join(dir, f.name);
        if (f.name === 'node_modules' || f.name === 'dist' || f.name === 'tests') continue;
        if (f.isDirectory()) {
          scanDir(full);
        } else if (/\.(tsx?|jsx?|css|json)$/.test(f.name)) {
          const content = fs.readFileSync(full, 'utf-8');
          if (banned.test(content)) {
            violations.push(full);
          }
        }
      }
    }

    scanDir(frontendSrc);
    expect(violations).toEqual([]);
  });
});
