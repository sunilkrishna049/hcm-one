import React, { useState, useEffect } from 'react';
import { Button } from '../design-system/components/Button';
import { MessageBubble } from '../design-system/components/MessageBubble';
import { SourceLink } from '../design-system/components/SourceLink';
import { getAIMessage } from '../design-system/ai_messages';
import { api } from '../services/api';
import { ArrowRight, Edit3, Sparkles } from 'lucide-react';

interface PrepareProposalProps {
  onProceedToReview: (mode: 'hike' | 'bonus' | 'settlement', employeeId?: string, extraParams?: any) => void;
  currentUser?: string;
}

export const PrepareProposal: React.FC<PrepareProposalProps> = ({
  onProceedToReview,
  currentUser: _currentUser,
}) => {
  const [proposalType, setProposalType] = useState<'hike' | 'bonus' | 'settlement'>('hike');
  const [requestText, setRequestText] = useState<string>("Prepare Priya Sharma's pending back-dated hike");
  const [selectedEmployeeId, setSelectedEmployeeId] = useState<string>('E01');
  const [employees, setEmployees] = useState<any[]>([]);
  const [scenarioData, setScenarioData] = useState<any>(null);
  const [isEditing, setIsEditing] = useState<boolean>(false);
  const [effectiveDateInput, setEffectiveDateInput] = useState<string>('2026-04-01');
  const [loading, setLoading] = useState<boolean>(true);

  // Fetch employees list from API (data/mock/employees.json)
  useEffect(() => {
    const fetchEmployees = async () => {
      try {
        const empList = await api.getEmployees();
        setEmployees(empList || []);
      } catch (err) {
        console.error("Failed to load employees", err);
      }
    };
    fetchEmployees();
  }, []);

  // Fetch proposal scenario data from API based on type
  useEffect(() => {
    const fetchProposalData = async () => {
      setLoading(true);
      try {
        let scenarioId = 'scenario-01';
        if (proposalType === 'bonus') scenarioId = 'scenario-04';
        if (proposalType === 'settlement') scenarioId = 'scenario-06';

        const res = await api.getScenario(scenarioId);
        setScenarioData(res.scenario);
        if (res.scenario?.display_inputs?.effective_date?.value) {
          setEffectiveDateInput(res.scenario.display_inputs.effective_date.value);
        }
      } catch (err) {
        console.error("Failed to fetch scenario", err);
      } finally {
        setLoading(false);
      }
    };
    fetchProposalData();
  }, [proposalType]);

  const handleSelectDemoRequest = (type: 'hike' | 'bonus' | 'settlement', text: string, empId: string) => {
    setProposalType(type);
    setRequestText(text);
    setSelectedEmployeeId(empId);
    setIsEditing(false);
  };

  const handleConfirmAndProceed = () => {
    onProceedToReview(proposalType, selectedEmployeeId, {
      effectiveDate: effectiveDateInput,
    });
  };

  const currentEmp = employees.find(e => e.employee_id === selectedEmployeeId);
  const displayInputs = scenarioData?.display_inputs || {};

  // Formatted display values strictly from API
  const requestedHikePct = displayInputs.requested_hike_percentage?.value;
  const effectiveDate = displayInputs.effective_date?.value || effectiveDateInput;
  const oldContractualSalary = displayInputs.old_monthly_salary?.total?.value;
  const proposedContractualSalary = displayInputs.proposed_monthly_salary?.total?.value;

  return (
    <div style={{ maxWidth: '960px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
      {/* Page Header: Title must be larger than assistant message text */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: 700, color: 'var(--color-text-primary)', margin: 0, letterSpacing: '-0.02em' }}>
            Prepare a proposal
          </h1>
          <p style={{ color: 'var(--color-text-secondary)', marginTop: 'var(--space-1)', fontSize: '15px' }}>
            Initiate and confirm authorized salary revisions, bonus allocations, or exit settlements.
          </p>
        </div>
        <div style={{
          backgroundColor: 'var(--color-surface)',
          border: '1px solid var(--color-divider)',
          padding: 'var(--space-2) var(--space-4)',
          borderRadius: 'var(--radius-pill)',
          fontSize: 'var(--font-size-small)',
          fontWeight: 'var(--font-weight-medium)',
          color: 'var(--color-brand-accent)'
        }}>
          As of 2026-10-13 (Cycle baseline)
        </div>
      </div>

      {/* Assistant Intro Banner (Approved Copy C01 Verbatim) */}
      <MessageBubble
        author="HCM One Assistant"
        text={getAIMessage('C01')}
      />

      {/* Conversation-first Request Composer */}
      <div style={{
        backgroundColor: 'var(--color-surface)',
        border: '1px solid var(--color-divider)',
        borderRadius: 'var(--radius-card)',
        padding: 'var(--space-5)',
        display: 'flex',
        flexDirection: 'column',
        gap: 'var(--space-4)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
          <Sparkles size={18} color="var(--color-brand-accent)" />
          <label htmlFor="request-composer" style={{ fontWeight: 'var(--font-weight-semibold)', fontSize: '16px' }}>
            Your payroll request
          </label>
        </div>

        <div style={{ display: 'flex', gap: 'var(--space-2)' }}>
          <input
            id="request-composer"
            type="text"
            className="hcm-input"
            value={requestText}
            onChange={(e) => setRequestText(e.target.value)}
            style={{ fontSize: '15px', padding: '12px 16px' }}
            readOnly={!isEditing}
          />
          {isEditing ? (
            <Button variant="primary" onClick={() => setIsEditing(false)}>
              Done
            </Button>
          ) : (
            <Button variant="outline" onClick={() => setIsEditing(true)}>
              <Edit3 size={15} /> Edit request
            </Button>
          )}
        </div>

        {/* Demo Quick Request Buttons */}
        <div>
          <div style={{ fontSize: '12px', fontWeight: 'bold', color: 'var(--color-text-secondary)', textTransform: 'uppercase', marginBottom: 'var(--space-2)' }}>
            Quick Demo Requests:
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--space-2)' }}>
            <button
              type="button"
              className="hcm-button hcm-button-secondary"
              style={{ fontSize: '13px' }}
              onClick={() => handleSelectDemoRequest('hike', "Prepare Priya Sharma's pending back-dated hike", 'E01')}
            >
              "Prepare Priya Sharma's pending back-dated hike"
            </button>
            <button
              type="button"
              className="hcm-button hcm-button-secondary"
              style={{ fontSize: '13px' }}
              onClick={() => handleSelectDemoRequest('bonus', "Prepare Annual Performance Bonus run", 'E01')}
            >
              "Prepare Annual Performance Bonus run"
            </button>
            <button
              type="button"
              className="hcm-button hcm-button-secondary"
              style={{ fontSize: '13px' }}
              onClick={() => handleSelectDemoRequest('settlement', "Prepare Rahul Verma's full and final settlement", 'E10')}
            >
              "Prepare Rahul Verma's full and final settlement"
            </button>
          </div>
        </div>
      </div>

      {/* Clarifying Question (Sentence C02 Verbatim) */}
      {proposalType === 'hike' && (
        <div style={{
          backgroundColor: '#F0FDFA',
          borderLeft: '4px solid var(--color-brand-accent)',
          padding: 'var(--space-4) var(--space-5)',
          borderRadius: 'var(--radius-input)',
          display: 'flex',
          flexDirection: 'column',
          gap: 'var(--space-3)'
        }}>
          <div style={{ fontSize: '15px', fontWeight: 600, color: 'var(--color-text-primary)' }}>
            {getAIMessage('C02')}
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
            <span style={{ fontSize: '14px', color: 'var(--color-text-secondary)' }}>
              Recorded effective date:
            </span>
            <span style={{
              fontWeight: 600,
              fontFamily: 'var(--font-mono)',
              backgroundColor: '#FFFFFF',
              padding: '4px 10px',
              borderRadius: 'var(--radius-input)',
              border: '1px solid var(--color-divider)'
            }}>
              {effectiveDate}
            </span>
            <span style={{ fontSize: 'var(--font-size-small)', color: 'var(--color-text-secondary)' }}>
              (Back-dated across recorded attendance cycle)
            </span>
          </div>
        </div>
      )}

      {/* Confirmation Panel populated strictly from API display_inputs */}
      <div style={{
        backgroundColor: '#FFFFFF',
        border: '1px solid var(--color-divider)',
        borderRadius: 'var(--radius-card)',
        padding: 'var(--space-6)',
        display: 'flex',
        flexDirection: 'column',
        gap: 'var(--space-4)',
        boxShadow: 'var(--shadow-card)'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h2 style={{ fontSize: '18px', fontWeight: 600, margin: 0, color: 'var(--color-text-primary)' }}>
            Request Confirmation Details
          </h2>
          <span style={{ fontSize: '13px', color: 'var(--color-text-secondary)' }}>
            Source: <SourceLink recordId={displayInputs.revision_id?.value || "REV-E01"} />
          </span>
        </div>

        {loading ? (
          <div style={{ padding: 'var(--space-4)', textAlign: 'center', color: 'var(--color-text-secondary)' }}>
            Loading request parameters from payroll engine...
          </div>
        ) : proposalType === 'hike' ? (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 'var(--space-4)' }}>
            <div className="hcm-confirmation-item">
              <span className="hcm-form-label">Employee</span>
              <div style={{ fontSize: '16px', fontWeight: 600, color: 'var(--color-text-primary)' }}>
                {currentEmp?.name || "Priya Sharma"} ({selectedEmployeeId})
              </div>
              <span style={{ fontSize: '12px', color: 'var(--color-text-secondary)' }}>
                {currentEmp?.department || "Engineering"}
              </span>
            </div>

            <div className="hcm-confirmation-item">
              <span className="hcm-form-label">Requested Hike</span>
              <div style={{ fontSize: '16px', fontWeight: 600, color: 'var(--color-brand-accent)' }}>
                {requestedHikePct !== undefined ? `${requestedHikePct}%` : "10%"}
              </div>
              <span style={{ fontSize: '12px', color: 'var(--color-text-secondary)' }}>
                Contractual revision rate
              </span>
            </div>

            <div className="hcm-confirmation-item">
              <span className="hcm-form-label">Effective Date</span>
              <div style={{ fontSize: '16px', fontWeight: 600, fontFamily: 'var(--font-mono)' }}>
                {effectiveDate}
              </div>
              <span style={{ fontSize: '12px', color: 'var(--color-text-secondary)' }}>
                Cycle start
              </span>
            </div>

            <div className="hcm-confirmation-item">
              <span className="hcm-form-label">Old Monthly Salary</span>
              <div style={{ fontSize: '16px', fontWeight: 600 }}>
                {oldContractualSalary !== undefined ? `INR ${oldContractualSalary.toLocaleString('en-IN')}` : "-"}
              </div>
              <span style={{ fontSize: '12px', color: 'var(--color-text-secondary)' }}>
                Contractual baseline
              </span>
            </div>

            <div className="hcm-confirmation-item">
              <span className="hcm-form-label">Proposed Monthly Salary</span>
              <div style={{ fontSize: '16px', fontWeight: 600, color: '#166534' }}>
                {proposedContractualSalary !== undefined ? `INR ${proposedContractualSalary.toLocaleString('en-IN')}` : "-"}
              </div>
              <span style={{ fontSize: '12px', color: 'var(--color-text-secondary)' }}>
                Revised baseline
              </span>
            </div>
          </div>
        ) : proposalType === 'bonus' ? (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 'var(--space-4)' }}>
            <div>
              <span className="hcm-form-label">Bonus Category</span>
              <div style={{ fontSize: '16px', fontWeight: 600 }}>Annual Performance Bonus</div>
            </div>
            <div>
              <span className="hcm-form-label">Pay Period</span>
              <div style={{ fontSize: '16px', fontWeight: 600 }}>2026-09</div>
            </div>
            <div>
              <span className="hcm-form-label">Policy Basis</span>
              <div style={{ fontSize: '14px', color: 'var(--color-text-secondary)' }}>Company bonus policy rules</div>
            </div>
          </div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 'var(--space-4)' }}>
            <div>
              <span className="hcm-form-label">Exiting Employee</span>
              <div style={{ fontSize: '16px', fontWeight: 600 }}>Rahul Verma (E10)</div>
            </div>
            <div>
              <span className="hcm-form-label">Tenure</span>
              <div style={{ fontSize: '16px', fontWeight: 600 }}>&gt; 5 years (Gratuity eligible)</div>
            </div>
            <div>
              <span className="hcm-form-label">Statutory Basis</span>
              <div style={{ fontSize: '14px', color: 'var(--color-text-secondary)' }}>Payment of Gratuity Act 1972</div>
            </div>
          </div>
        )}

        {/* Action Controls */}
        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 'var(--space-3)', marginTop: 'var(--space-4)', borderTop: '1px solid var(--color-divider)', paddingTop: 'var(--space-4)' }}>
          <Button
            variant="outline"
            onClick={() => setIsEditing(true)}
          >
            <Edit3 size={15} /> Edit request
          </Button>

          <Button
            variant="primary"
            onClick={handleConfirmAndProceed}
          >
            Confirm request and review calculation <ArrowRight size={16} />
          </Button>
        </div>
      </div>
    </div>
  );
};
