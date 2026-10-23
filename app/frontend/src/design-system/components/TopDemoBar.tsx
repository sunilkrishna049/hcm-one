import React from 'react';
import { RotateCcw, UserCheck, Play } from 'lucide-react';

export interface UserOption {
  id: string;
  name: string;
  role: 'HR' | 'Employee';
  dept?: string;
}

export interface UserOption {
  id: string;
  name: string;
  role: 'HR' | 'Employee';
  dept?: string;
}

export const DEMO_USERS: UserOption[] = [
  { id: 'HR01', name: 'HR Admin (All Depts)', role: 'HR', dept: 'All' },
  { id: 'HR02', name: 'HR Sales (Sales Only)', role: 'HR', dept: 'Sales' },
  { id: 'USER-E01', name: 'Priya Sharma (E01)', role: 'Employee', dept: 'Engineering' },
  { id: 'USER-E02', name: 'Arjun Rao (E02)', role: 'Employee', dept: 'Operations' },
  { id: 'USER-E03', name: 'Kavya Iyer (E03)', role: 'Employee', dept: 'Engineering' },
  { id: 'USER-E05', name: 'Neha Gupta (E05)', role: 'Employee', dept: 'Operations' },
  { id: 'USER-E06', name: 'Siddharth Jain (E06)', role: 'Employee', dept: 'Engineering' },
  { id: 'USER-E10', name: 'Rahul Verma (E10)', role: 'Employee', dept: 'Finance' },
  { id: 'USER-E11', name: 'Lakshmi Reddy (E11)', role: 'Employee', dept: 'Finance' },
  { id: 'USER-E12', name: 'Imran Khan (E12)', role: 'Employee', dept: 'Engineering' },
  { id: 'USER-E16', name: 'Pooja Das (E16)', role: 'Employee', dept: 'Operations' },
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
  { id: 2, title: '2. Hike across PF ceiling change (Arjun Rao E02)', defaultUser: 'HR01', screenType: 'desktop', description: 'Back-dated hike spanning statutory PF ceiling change on 2026-09-17.', employeeId: 'E02' },
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
  currentScenario: number;
  onScenarioChange: (scenarioId: number) => void;
  onResetDemo: () => void;
  isResetting?: boolean;
}

export const TopDemoBar: React.FC<TopDemoBarProps> = ({
  currentUser,
  onUserChange,
  currentScenario,
  onScenarioChange,
  onResetDemo,
  isResetting = false,
}) => {
  return (
    <div className="hcm-top-demo-bar">
      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
        <strong style={{ letterSpacing: '0.05em', color: '#5EEAD4' }}>HCM ONE</strong>
        <span style={{ color: '#94A3B8', fontSize: '12px' }}>PROTOTYPE</span>

        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', marginLeft: 'var(--space-4)' }}>
          <Play size={14} color="#5EEAD4" />
          <label htmlFor="scenario-select" style={{ fontSize: '13px', color: '#E2E8F0' }}>Scenario:</label>
          <select
            id="scenario-select"
            value={currentScenario}
            onChange={(e) => onScenarioChange(Number(e.target.value))}
            style={{ fontWeight: 500 }}
          >
            {SCENARIOS.map(s => (
              <option key={s.id} value={s.id}>
                {s.title}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-4)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
          <UserCheck size={14} color="#5EEAD4" />
          <label htmlFor="user-select" style={{ fontSize: '13px', color: '#E2E8F0' }}>Logged in as:</label>
          <select
            id="user-select"
            value={currentUser}
            onChange={(e) => onUserChange(e.target.value)}
          >
            {DEMO_USERS.map(u => (
              <option key={u.id} value={u.id}>
                {u.id} - {u.name} ({u.role})
              </option>
            ))}
          </select>
        </div>

        <button
          onClick={onResetDemo}
          disabled={isResetting}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 'var(--space-1)',
            padding: 'var(--space-1) var(--space-3)',
            backgroundColor: '#334155',
            color: '#FFFFFF',
            border: '1px solid #475569',
            borderRadius: 'var(--radius-button)',
            fontSize: '12px',
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
