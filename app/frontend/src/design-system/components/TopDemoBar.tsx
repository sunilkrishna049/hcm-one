import React from 'react';
import { RotateCcw, Sparkles } from 'lucide-react';

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
    <header className="hcm-top-demo-bar">
      {/* Left: 30x30 logo tile, radius 8px, Primary background, white icon, then HCM One in bold 16px Main text */}
      <div className="hcm-header-brand">
        <div className="hcm-header-logo-tile" aria-hidden="true">
          <Sparkles size={16} color="var(--color-brand-text-on-accent)" />
        </div>
        <span className="hcm-header-title">HCM One</span>
      </div>

      {/* Centre: HR view / Employee view toggle as a pill segmented control */}
      <div className="hcm-header-toggle-container">
        <div
          role="tablist"
          aria-label="Role view selector"
          data-testid="view-toggle"
          className="hcm-header-view-toggle"
        >
          <button
            type="button"
            role="tab"
            id="toggle-hr-view"
            data-testid="toggle-hr-view"
            aria-selected={isHR}
            aria-pressed={isHR}
            tabIndex={0}
            onClick={() => onUserChange('HR01')}
            className={`hcm-header-toggle-btn ${isHR ? 'active' : ''}`}
          >
            HR view
          </button>
          <button
            type="button"
            role="tab"
            id="toggle-emp-view"
            data-testid="toggle-emp-view"
            aria-selected={!isHR}
            aria-pressed={!isHR}
            tabIndex={0}
            onClick={() => onUserChange('USER-E05')}
            className={`hcm-header-toggle-btn ${!isHR ? 'active' : ''}`}
          >
            Employee view
          </button>
        </div>
      </div>

      {/* Right: Reset Demo button */}
      <div className="hcm-header-actions">
        <button
          type="button"
          onClick={onResetDemo}
          disabled={isResetting}
          className="hcm-header-reset-btn"
          title="Reset runtime events, proposals, and queries to fresh state"
        >
          <RotateCcw size={13} />
          <span>{isResetting ? 'Resetting...' : 'Reset Demo'}</span>
        </button>
      </div>
    </header>
  );
};
