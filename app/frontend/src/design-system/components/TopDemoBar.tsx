import React from 'react';
import { RotateCcw, UserCheck, Play } from 'lucide-react';

export interface UserOption {
  id: string;
  name: string;
  role: 'HR' | 'Employee';
  dept?: string;
}

export const DEMO_USERS: UserOption[] = [
  { id: 'HR01', name: 'Anita Desai (HR Admin)', role: 'HR', dept: 'All' },
  { id: 'HR02', name: 'Kiran Patel (HR Sales)', role: 'HR', dept: 'Sales' },
  { id: 'USER-E01', name: 'Priya Sharma (Engineering)', role: 'Employee', dept: 'Engineering' },
  { id: 'USER-E02', name: 'Arjun Rao (Operations)', role: 'Employee', dept: 'Operations' },
  { id: 'USER-E03', name: 'Kavya Iyer (Engineering)', role: 'Employee', dept: 'Engineering' },
  { id: 'USER-E05', name: 'Neha Gupta (Operations)', role: 'Employee', dept: 'Operations' },
  { id: 'USER-E06', name: 'Siddharth Jain (Engineering)', role: 'Employee', dept: 'Engineering' },
  { id: 'USER-E10', name: 'Rahul Verma (Finance)', role: 'Employee', dept: 'Finance' },
  { id: 'USER-E11', name: 'Lakshmi Reddy (Finance)', role: 'Employee', dept: 'Finance' },
  { id: 'USER-E12', name: 'Imran Khan (Engineering)', role: 'Employee', dept: 'Engineering' },
  { id: 'USER-E16', name: 'Pooja Das (Operations)', role: 'Employee', dept: 'Operations' },
];

export interface ScenarioOption {
  id: number;
  title: string;
  defaultUser: string;
  screenType: 'desktop' | 'mobile';
  description: string;
  employeeId?: string;
}

export const SCENARIOS: ScenarioOption[] = [
  { id: 1, title: '1. Hike with LOP (Priya Sharma E01)', defaultUser: 'HR01', screenType: 'desktop', description: 'Back-dated hike with unpaid leave (loss of pay) across multiple months.', employeeId: 'E01' },
  { id: 2, title: '2. Hike across PF ceiling change (Arjun Rao E02)', defaultUser: 'HR01', screenType: 'desktop', description: 'Back-dated hike spanning PF ceiling change on 2026-09-17.', employeeId: 'E02' },
  { id: 3, title: '3. Hike with missing attendance (Kavya Iyer E03)', defaultUser: 'HR01', screenType: 'desktop', description: 'Back-dated hike where July attendance record is missing.', employeeId: 'E03' },
  { id: 4, title: '4. Team bonus with joiner & notice cases', defaultUser: 'HR01', screenType: 'desktop', description: 'Bonus run covering annual performance bonus and quarterly sales incentive.' },
  { id: 5, title: '5. Missing performance rating (Meera Nair E09)', defaultUser: 'HR01', screenType: 'desktop', description: 'Bonus proposal where E09 performance rating is not recorded.', employeeId: 'E09' },
  { id: 6, title: '6. Eligible gratuity settlement (Rahul Verma E10)', defaultUser: 'HR01', screenType: 'desktop', description: 'Exiting employee with > 5 years service eligible for gratuity.', employeeId: 'E10' },
  { id: 7, title: '7. Below gratuity minimum (Lakshmi Reddy E11)', defaultUser: 'HR01', screenType: 'desktop', description: 'Exiting employee with service close to but below 5-year threshold.', employeeId: 'E11' },
  { id: 8, title: '8. Asset clearance & notice shortfall (Imran Khan E12)', defaultUser: 'HR01', screenType: 'desktop', description: 'Exiting employee with notice shortfall recovery and unreturned company assets.', employeeId: 'E12' },
  { id: 9, title: '9. Salary drop with LOP (Neha Gupta E05)', defaultUser: 'USER-E05', screenType: 'mobile', description: 'Employee take-home pay dropped between August and September due to LOP.', employeeId: 'E05' },
  { id: 10, title: '10. Previous employer declaration (Siddharth Jain E06)', defaultUser: 'USER-E06', screenType: 'mobile', description: 'Employee TDS increased because of declared income from previous employer.', employeeId: 'E06' },
  { id: 11, title: '11. No salary earning change (Pooja Das E16)', defaultUser: 'USER-E16', screenType: 'mobile', description: 'Take-home dropped 420 due to PF ceiling change with no gross change.', employeeId: 'E16' },
  { id: 12, title: "12. Colleague's salary requested (Permission denied)", defaultUser: 'HR02', screenType: 'desktop', description: 'Unauthorized request returns C10 permission denied with no leaked data.' },
  { id: 13, title: '13. Known & unresolved settlement components (Imran Khan E12)', defaultUser: 'HR01', screenType: 'desktop', description: 'Settlement proposal with unverified asset clearance blocking net.', employeeId: 'E12' },
];


interface TopDemoBarProps {
  currentUser: string;
  onUserChange: (userId: string) => void;
  currentScenario?: number;
  onScenarioChange?: (scenarioId: number) => void;
  onResetDemo: () => void;
  isResetting?: boolean;
}

export const TopDemoBar: React.FC<TopDemoBarProps> = ({
  currentUser,
  onUserChange,
  onResetDemo,
  isResetting = false,
}) => {
  const isHR = currentUser.startsWith('HR');

  return (
    <div className="hcm-top-demo-bar">
      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)', flexWrap: 'wrap' }}>
        <strong style={{ letterSpacing: '0.05em', color: 'var(--color-brand-accent)' }}>HCM ONE</strong>
        <span style={{ color: 'var(--color-text-muted)', fontSize: '12px' }}>PROTOTYPE</span>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)', flexWrap: 'wrap' }}>
        {/* Two-way toggle: HR view · Employee view */}
        <div
          data-testid="view-toggle"
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            backgroundColor: 'var(--color-surface-sunken)',
            borderRadius: 'var(--radius-button)',
            padding: '2px 4px',
            border: '1px solid var(--color-border-card)',
            gap: 'var(--space-1)',
          }}
        >
          <button
            type="button"
            id="toggle-hr-view"
            data-testid="toggle-hr-view"
            onClick={() => onUserChange('HR01')}
            style={{
              padding: 'var(--space-1) var(--space-3)',
              fontSize: '12px',
              fontWeight: isHR ? 600 : 400,
              backgroundColor: isHR ? 'var(--color-surface)' : 'transparent',
              color: isHR ? 'var(--color-brand-accent)' : 'var(--color-text-secondary)',
              border: isHR ? '1px solid var(--color-border-interactive)' : '1px solid transparent',
              borderRadius: 'var(--radius-button)',
              boxShadow: isHR ? 'var(--shadow-card)' : 'none',
              cursor: 'pointer',
              transition: 'all 0.15s ease',
            }}
          >
            HR view
          </button>
          <span style={{ color: 'var(--color-text-muted)', fontSize: '11px', userSelect: 'none' }}>·</span>
          <button
            type="button"
            id="toggle-emp-view"
            data-testid="toggle-emp-view"
            onClick={() => onUserChange('USER-E05')}
            style={{
              padding: 'var(--space-1) var(--space-3)',
              fontSize: '12px',
              fontWeight: !isHR ? 600 : 400,
              backgroundColor: !isHR ? 'var(--color-surface)' : 'transparent',
              color: !isHR ? 'var(--color-brand-accent)' : 'var(--color-text-secondary)',
              border: !isHR ? '1px solid var(--color-border-interactive)' : '1px solid transparent',
              borderRadius: 'var(--radius-button)',
              boxShadow: !isHR ? 'var(--shadow-card)' : 'none',
              cursor: 'pointer',
              transition: 'all 0.15s ease',
            }}
          >
            Employee view
          </button>
        </div>

        <button
          onClick={onResetDemo}
          disabled={isResetting}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 'var(--space-1)',
            padding: 'var(--space-1) var(--space-3)',
            backgroundColor: 'var(--color-surface-hover)',
            color: 'var(--color-text-primary)',
            border: '1px solid var(--color-border-interactive)',
            borderRadius: 'var(--radius-button)',
            fontSize: '12px',
            minHeight: '32px',
            cursor: isResetting ? 'not-allowed' : 'pointer',
          }}
          title="Reset runtime events, proposals, and queries to fresh state"
        >
          <RotateCcw size={12} />
          {isResetting ? "Resetting..." : "Reset Demo"}
        </button>
      </div>
    </div>
  );
};
