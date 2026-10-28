import React from 'react';
import { User, ChevronRight, Briefcase } from 'lucide-react';

export interface EmployeeCandidate {
  employee_id: string;
  name: string;
  department?: string;
  subtitle?: string;
}

interface EmployeePickerCardProps {
  card: {
    id: string;
    type: string;
    title: string;
    certainty?: string;
    data?: {
      task?: string;
      prompt?: string;
      employees?: EmployeeCandidate[];
    };
  };
  onSelectEmployee?: (employeeId: string, task?: string, name?: string) => void;
}

export const EmployeePickerCard: React.FC<EmployeePickerCardProps> = ({
  card,
  onSelectEmployee,
}) => {
  const employees = card.data?.employees || [];
  const task = card.data?.task || '';
  const prompt = card.data?.prompt || 'Select an employee to proceed:';

  return (
    <div
      className="hcm-card-interactive"
      data-testid="employee-picker-card"
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: 'var(--space-3)',
        padding: 'var(--space-4)',
        backgroundColor: 'var(--color-surface)',
        border: '1px solid var(--color-border-card)',
        borderRadius: 'var(--radius-card)',
        boxShadow: 'var(--shadow-card)',
        maxWidth: '560px',
        width: '100%',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid var(--color-border-subtle)', paddingBottom: 'var(--space-2)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
          <Briefcase size={16} color="var(--color-brand-accent)" />
          <h3 style={{ margin: 0, fontSize: '14px', fontWeight: 600, color: 'var(--color-text-primary)' }}>
            {card.title || 'Select employee'}
          </h3>
        </div>
        <span style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>
          {employees.length} {employees.length === 1 ? 'record' : 'records'}
        </span>
      </div>

      <p style={{ margin: 0, fontSize: '13px', color: 'var(--color-text-secondary)', lineHeight: 1.4 }}>
        {prompt}
      </p>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
        {employees.map((emp) => (
          <button
            key={emp.employee_id}
            type="button"
            className="hcm-employee-picker-item"
            data-testid={`employee-item-${emp.employee_id}`}
            onClick={() => onSelectEmployee?.(emp.employee_id, task, emp.name)}
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: 'var(--space-2) var(--space-3)',
              backgroundColor: 'var(--color-surface-hover)',
              border: '1px solid var(--color-border-interactive)',
              borderRadius: 'var(--radius-button)',
              cursor: 'pointer',
              textAlign: 'left',
              transition: 'all 0.15s ease',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
              <div
                style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '50%',
                  backgroundColor: 'var(--color-surface-sunken)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'var(--color-brand-accent)',
                }}
              >
                <User size={16} />
              </div>
              <div style={{ display: 'flex', flexDirection: 'column' }}>
                <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--color-text-primary)' }}>
                  {emp.name} · <span style={{ color: 'var(--color-text-muted)', fontWeight: 400 }}>{emp.employee_id}</span>
                </span>
                {emp.subtitle && (
                  <span style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>
                    {emp.subtitle}
                  </span>
                )}
              </div>
            </div>
            <ChevronRight size={16} color="var(--color-text-muted)" />
          </button>
        ))}
      </div>
    </div>
  );
};
