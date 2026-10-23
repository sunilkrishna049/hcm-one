import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import React from 'react';
import fs from 'fs';
import path from 'path';

import { ReviewProposal } from '../screens/ReviewProposal';
import { UnderstandPayroll } from '../screens/UnderstandPayroll';
import { PrepareProposal } from '../screens/PrepareProposal';
import { ReviewQueryDraft } from '../screens/ReviewQueryDraft';
import { api, setCurrentUserId } from '../services/api';

// Helper to load scenario JSON directly from data/generated/scenarios/
function loadScenarioData(scenarioNum: number) {
  const scenarioId = `scenario-${String(scenarioNum).padStart(2, '0')}`;
  const filePath = path.resolve(__dirname, `../../../../data/generated/scenarios/${scenarioId}.json`);
  if (!fs.existsSync(filePath)) {
    throw new Error(`Scenario file not found: ${filePath}`);
  }
  const raw = fs.readFileSync(filePath, 'utf-8');
  const scenarioJson = JSON.parse(raw);

  const employeesPath = path.resolve(__dirname, `../../../../data/mock/employees.json`);
  const employees = JSON.parse(fs.readFileSync(employeesPath, 'utf-8'));
  const empMap = new Map(employees.map((e: any) => [e.employee_id, e]));

  const meta: any = {
    scenario_num: scenarioNum,
    scenario_id: scenarioId,
    description: scenarioJson.description,
    employee_id: scenarioJson.result?.employee_id || null,
  };
  if (meta.employee_id && empMap.has(meta.employee_id)) {
    meta.employee = empMap.get(meta.employee_id);
  }

  return {
    meta,
    scenario: scenarioJson,
    runtime_proposal: {
      proposal_id: `PROP-SCENARIO-${scenarioNum}`,
      version: 1,
      status: scenarioJson.result?.proposal_status || 'Needs HR approval; not applied',
      certainty: scenarioJson.result?.certainty || 'Complete for this scope',
      scope: { scenario_id: scenarioId },
      data: scenarioJson.result
    }
  };
}

// Recursively gather all numbers from an API response object
function extractNumbersFromObject(obj: any, collected: Set<number> = new Set()): Set<number> {
  if (obj === null || obj === undefined) return collected;
  if (typeof obj === 'number') {
    collected.add(obj);
    return collected;
  }
  if (typeof obj === 'string') {
    const num = parseFloat(obj.replace(/,/g, ''));
    if (!isNaN(num) && String(num) === obj.trim()) {
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

// Setup fetch mock to return real scenario data
beforeEach(() => {
  vi.spyOn(globalThis, 'fetch').mockImplementation((input: any) => {
    const url = String(input);

    if (url.includes('/api/employees')) {
      const employeesPath = path.resolve(__dirname, `../../../../data/mock/employees.json`);
      const employees = JSON.parse(fs.readFileSync(employeesPath, 'utf-8'));
      return Promise.resolve(new Response(JSON.stringify(employees), { status: 200 }));
    }

    if (url.includes('/api/queries')) {
      const queriesPath = path.resolve(__dirname, `../../../../data/mock/queries.json`);
      const queries = JSON.parse(fs.readFileSync(queriesPath, 'utf-8'));
      return Promise.resolve(new Response(JSON.stringify(queries), { status: 200 }));
    }

    if (url.includes('/api/scenarios/')) {
      const match = url.match(/scenario-(\d+)/);
      if (match) {
        const scenarioNum = parseInt(match[1], 10);
        if (scenarioNum === 12) {
          return Promise.resolve(new Response(JSON.stringify({
            scenario_id: "scenario-12",
            status: "Permission denied",
            message: "I cannot provide that information. I can help with payroll records you are authorized to access.",
            certainty: "Permission denied",
            result: { status: "Permission denied" },
            display_inputs: {}
          }), { status: 200 }));
        }

        const data = loadScenarioData(scenarioNum);
        return Promise.resolve(new Response(JSON.stringify(data), { status: 200 }));
      }
    }

    return Promise.resolve(new Response(JSON.stringify({}), { status: 200 }));
  });
});

afterEach(() => {
  vi.restoreAllMocks();
});

describe('Automated checks that screens match real API responses (FIX 2)', () => {
  it('Scenario 1: ReviewProposal renders exact API numbers for Priya Sharma (gross arrears 71,200, net 67,476, PF 0, TDS 3,724)', async () => {
    const apiData = loadScenarioData(1);
    const totals = apiData.scenario.result.totals;
    expect(totals.gross_arrears.value).toBe(71200);
    expect(totals.net_arrears.value).toBe(67476);
    expect(totals.pf_change.employee.value).toBe(0);
    expect(totals.tds_impact.value).toBe(3724);

    const { container } = render(
      <ReviewProposal scenarioNum={1} mode="hike" employeeId="E01" currentUser="HR01" />
    );

    // Wait for values to appear
    await waitFor(() => {
      expect(screen.getByText('Expected net arrears')).toBeInTheDocument();
    });

    // Check exact values on screen
    expect(screen.getByText('67,476')).toBeInTheDocument();
    expect(screen.getByText('71,200')).toBeInTheDocument();

    // Assert that "New Annual CTC" is NOT on screen
    expect(screen.queryByText(/New Annual CTC/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/CTC/i)).not.toBeInTheDocument();

    // Assert fabricated 72,000 or 90,000 are NOT on screen
    expect(screen.queryByText('72,000')).not.toBeInTheDocument();
    expect(screen.queryByText('90,000')).not.toBeInTheDocument();
    expect(screen.queryByText('13,20,000')).not.toBeInTheDocument();
    expect(screen.queryByText('1,10,000')).not.toBeInTheDocument();
  });

  it('Scenario 2: ReviewProposal renders exact API numbers for Arjun Rao (net arrears 7,099, gross arrears 7,200, PF change 101, TDS impact 0)', async () => {
    const apiData = loadScenarioData(2);
    const totals = apiData.scenario.result.totals;
    expect(totals.gross_arrears.value).toBe(7200);
    expect(totals.net_arrears.value).toBe(7099);
    expect(totals.pf_change.employee.value).toBe(101);
    expect(totals.tds_impact.value).toBe(0);

    render(
      <ReviewProposal scenarioNum={2} mode="hike" employeeId="E02" currentUser="HR01" />
    );

    await waitFor(() => {
      expect(screen.getByText('Expected net arrears')).toBeInTheDocument();
    });

    expect(screen.getByText('7,099')).toBeInTheDocument();
    expect(screen.getByText('7,200')).toBeInTheDocument();
    expect(screen.getByText('101')).toBeInTheDocument();
  });

  it('Scenario 3: ReviewProposal handles Kavya missing attendance with exact C07 copy & Not available for July', async () => {
    const apiData = loadScenarioData(3);
    expect(apiData.scenario.result.certainty).toBe('Incomplete');

    render(
      <ReviewProposal scenarioNum={3} mode="hike" employeeId="E03" currentUser="HR01" />
    );

    await waitFor(() => {
      expect(screen.getByText(/Proposal Scope Incomplete/i)).toBeInTheDocument();
    });

    // July missing: "Not available in generated data" must appear in the row
    const notAvailableElements = screen.getAllByText('Not available in generated data');
    expect(notAvailableElements.length).toBeGreaterThan(0);

    // August & September arrears are 4,800 each from engine (8% on 60,000 basic)
    const fourThousandEightHundreds = screen.getAllByText('INR 4,800');
    expect(fourThousandEightHundreds.length).toBeGreaterThanOrEqual(2);
  });

  it('Scenario 6: ReviewProposal renders exact settlement for Rahul Verma (final net 332,256, gratuity 201,923, gross 335,256)', async () => {
    const apiData = loadScenarioData(6);
    expect(apiData.scenario.result.final_net.value).toBe(332256);
    expect(apiData.scenario.result.components.gratuity.amount.value).toBe(201923);
    expect(apiData.scenario.result.gross_payables.value).toBe(335256);

    render(
      <ReviewProposal scenarioNum={6} mode="settlement" employeeId="E10" currentUser="HR01" />
    );

    await waitFor(() => {
      expect(screen.getByText('Final net')).toBeInTheDocument();
    });

    expect(screen.getByText((332256).toLocaleString('en-IN'))).toBeInTheDocument();
    expect(screen.getByText((335256).toLocaleString('en-IN'))).toBeInTheDocument();
    expect(screen.getByText(`INR ${(201923).toLocaleString('en-IN')}`)).toBeInTheDocument();
  });

  it('Scenario 9: UnderstandPayroll renders exact Neha Gupta take-home (42,780, drop -5,420, LOP -5,000, PF ceiling -420)', async () => {
    const apiData = loadScenarioData(9);
    expect(apiData.scenario.result.after.net_pay.value).toBe(42780);
    expect(apiData.scenario.result.net_change.value).toBe(-5420);
    expect(apiData.scenario.result.reasons[0].effect_amount.value).toBe(-5000);
    expect(apiData.scenario.result.reasons[1].effect_amount.value).toBe(-420);

    render(
      <UnderstandPayroll currentUser="USER-E05" scenarioNum={9} onNavigateToDraftQuery={() => {}} />
    );

    await waitFor(() => {
      expect(screen.getByText('September take-home')).toBeInTheDocument();
    });

    // Check exact values
    expect(screen.getByText('42,780')).toBeInTheDocument();
    expect(screen.getByText('-5,420')).toBeInTheDocument();
    expect(screen.getByText('-5,000 INR')).toBeInTheDocument();
    expect(screen.getByText('-420 INR')).toBeInTheDocument();

    // Verify 49,800 or 5,200 do NOT appear anywhere
    expect(screen.queryByText('49,800')).not.toBeInTheDocument();
    expect(screen.queryByText('5,200')).not.toBeInTheDocument();
    expect(screen.queryByText(/medical leave/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/payroll-records\.json/i)).not.toBeInTheDocument();
  });

  it('Scenario 10: UnderstandPayroll renders exact Siddharth Jain TDS change (12,454, reason TDS -12,454, PF -560, C29)', async () => {
    const apiData = loadScenarioData(10);
    expect(apiData.scenario.result.tds_change.value).toBe(12454);
    expect(apiData.scenario.result.reasons[0].effect_amount.value).toBe(-12454);
    expect(apiData.scenario.result.reasons[1].effect_amount.value).toBe(-560);

    render(
      <UnderstandPayroll currentUser="USER-E06" scenarioNum={10} onNavigateToDraftQuery={() => {}} />
    );

    await waitFor(() => {
      expect(screen.getByText('TDS Change vs August')).toBeInTheDocument();
    });

    expect(screen.getByText('12,454')).toBeInTheDocument();
    expect(screen.getByText('-12,454 INR')).toBeInTheDocument();
    expect(screen.getByText('-560 INR')).toBeInTheDocument();
  });

  it('Scenario 11: UnderstandPayroll renders Pooja Das take-home drop of 420 with no earning change', async () => {
    const apiData = loadScenarioData(11);
    expect(apiData.scenario.result.net_change.value).toBe(-420);
    expect(apiData.scenario.result.no_earning_component_change).toBe(true);

    render(
      <UnderstandPayroll currentUser="USER-E16" scenarioNum={11} onNavigateToDraftQuery={() => {}} />
    );

    await waitFor(() => {
      expect(screen.getByText('Take-home pay change')).toBeInTheDocument();
    });

    expect(screen.getByText('-420')).toBeInTheDocument();
    expect(screen.getByText(/No salary earning component change/i)).toBeInTheDocument();
  });

  it('Scenario 12: Colleague salary requested renders C10 Permission denied with ZERO target numbers', async () => {
    render(
      <UnderstandPayroll currentUser="HR02" scenarioNum={12} onNavigateToDraftQuery={() => {}} />
    );

    await waitFor(() => {
      expect(screen.getByText('Permission denied')).toBeInTheDocument();
    });

    // Sentence C10 verbatim
    expect(screen.getAllByText('I cannot provide that information. I can help with payroll records you are authorized to access.').length).toBeGreaterThan(0);

    // No target employee salary or numbers on screen
    expect(screen.queryByText(/Priya Sharma's salary is/i)).not.toBeInTheDocument();
    expect(screen.queryByText('67,476')).not.toBeInTheDocument();
    expect(screen.queryByText('71,200')).not.toBeInTheDocument();
  });

  it('Scenario 13: Settlement with unverified asset recovery renders known recoveries 56,667 and final net Not available', async () => {
    const apiData = loadScenarioData(13);
    expect(apiData.scenario.result.known_recoveries_subtotal.value).toBe(56667);

    render(
      <ReviewProposal scenarioNum={13} mode="settlement" employeeId="E12" currentUser="HR01" />
    );

    await waitFor(() => {
      expect(screen.getByText('Final net')).toBeInTheDocument();
    });

    expect(screen.getByText('56,667')).toBeInTheDocument();
    // Final net is incomplete
    const notAvail = screen.getAllByText('Not available in generated data');
    expect(notAvail.length).toBeGreaterThan(0);
  });

  it('GUARD TEST: Fails if any payroll number on rendered screen is not present in the API response', async () => {
    // Test across scenarios 1, 6, 9, 10
    for (const sNum of [1, 6, 9, 10]) {
      const apiData = loadScenarioData(sNum);
      const allowedNumbers = extractNumbersFromObject(apiData.scenario);

      // Add allowed non-payroll UI numbers: year, month numbers, scenario ids, versions
      const standardAllowed = new Set([
        2025, 2026, 2027, // years
        1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, // dates, scenarios, indices
        30, 31, // days in month
        100, // percentage max
        390, 1440, // frame widths
      ]);

      let renderedResult;
      if (sNum <= 6) {
        renderedResult = render(
          <ReviewProposal
            scenarioNum={sNum}
            mode={sNum === 6 ? 'settlement' : 'hike'}
            employeeId={sNum === 6 ? 'E10' : 'E01'}
            currentUser="HR01"
          />
        );
      } else {
        renderedResult = render(
          <UnderstandPayroll
            currentUser={sNum === 9 ? 'USER-E05' : 'USER-E06'}
            scenarioNum={sNum}
            onNavigateToDraftQuery={() => {}}
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

        // The number MUST exist in the API response
        const isInApi = allowedNumbers.has(num) || allowedNumbers.has(-num);
        if (!isInApi) {
          throw new Error(
            `GUARD FAILED: Found payroll number '${match}' (${num}) in Scenario ${sNum} screen that does NOT exist in API response!`
          );
        }
        expect(isInApi).toBe(true);
      }

      renderedResult.unmount();
    }
  });
});
