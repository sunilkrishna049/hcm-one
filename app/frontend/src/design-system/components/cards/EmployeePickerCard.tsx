import React, { useState } from 'react';
import { User, ChevronRight, Briefcase, Search } from 'lucide-react';

export interface EmployeeCandidate {
  employee_id: string;
  name: string;
  department?: string;
  subtitle?: string;
  status_tags?: string[];
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
      has_search?: boolean;
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
  const showSearch = card.data?.has_search ?? employees.length > 4;
  const [searchQuery, setSearchQuery] = useState('');

  const filteredEmployees = employees.filter((emp) => {
    if (!searchQuery.trim()) return true;
    const q = searchQuery.toLowerCase().trim();
    const nameMatch = emp.name.toLowerCase().includes(q);
    const idMatch = emp.employee_id.toLowerCase().includes(q);
    const deptMatch = emp.department ? emp.department.toLowerCase().includes(q) : false;
    return nameMatch || idMatch || deptMatch;
  });

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
        boxSizing: 'border-box',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid var(--color-border-subtle)', paddingBottom: 'var(--space-2)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
          <Briefcase size={16} color="var(--color-primary-text)" />
          <h3 style={{ margin: 0, fontSize: '14px', fontWeight: 600, color: 'var(--color-text-primary)' }}>
            {card.title || 'Select employee'}
          </h3>
        </div>
        <span style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>
          {filteredEmployees.length} {filteredEmployees.length === 1 ? 'record' : 'records'}
        </span>
      </div>

      <p style={{ margin: 0, fontSize: '13px', color: 'var(--color-text-secondary)', lineHeight: 1.4 }}>
        {prompt}
      </p>

      {showSearch && (
        <div style={{ position: 'relative', width: '100%' }}>
          <Search
            size={14}
            style={{
              position: 'absolute',
              left: '10px',
              top: '50%',
              transform: 'translateY(-50%)',
              color: 'var(--color-text-muted)',
              pointerEvents: 'none',
            }}
          />
          <input
            type="text"
            data-testid="employee-picker-search"
            aria-label="Search employees by name, ID, or department"
            placeholder="Search by name, ID, or department…"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              width: '100%',
              boxSizing: 'border-box',
              padding: '8px 12px 8px 32px',
              fontSize: '12px',
              color: 'var(--color-text-primary)',
              backgroundColor: 'var(--color-surface-sunken)',
              border: '1px solid var(--color-border-subtle)',
              borderRadius: 'var(--radius-input)',
              outline: 'none',
            }}
          />
        </div>
      )}

      <div
        className="hcm-employee-picker-list"
        data-testid="employee-picker-list"
        style={{
          display: 'flex',
          flexDirection: 'column',
          gap: 'var(--space-2)',
          maxHeight: '340px',
          overflowY: 'auto',
          overflowX: 'hidden',
          paddingRight: '2px',
        }}
      >
        {filteredEmployees.length === 0 ? (
          <div style={{ padding: 'var(--space-3)', textAlign: 'center', color: 'var(--color-text-muted)', fontSize: '12px' }}>
            No matching employees found
          </div>
        ) : (
          filteredEmployees.map((emp) => (
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
                gap: 'var(--space-2)',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)', minWidth: 0, flex: 1 }}>
                <div
                  style={{
                    width: '32px',
                    height: '32px',
                    borderRadius: '50%',
                    backgroundColor: 'var(--color-surface-sunken)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'var(--color-primary-text)',
                    flexShrink: 0,
                  }}
                >
                  <User size={16} />
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', minWidth: 0, flex: 1 }}>
                  <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--color-text-primary)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {emp.name} · <span style={{ color: 'var(--color-text-muted)', fontWeight: 400 }}>{emp.employee_id}</span>
                  </span>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', flexWrap: 'wrap', marginTop: '2px' }}>
                    {emp.department && (
                      <span style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>
                        {emp.department}
                      </span>
                    )}
                    {emp.status_tags && emp.status_tags.map((tag) => {
                      let tagColor = 'var(--color-text-secondary)';
                      let tagBg = 'var(--color-surface-sunken)';
                      let tagBorder = 'var(--color-border-subtle)';

                      if (tag.includes('Hike pending') || tag.includes('Needs input')) {
                        tagColor = 'var(--color-status-warning-text)';
                        tagBg = 'var(--color-status-warning-surface)';
                        tagBorder = 'var(--color-status-warning-border)';
                      } else if (tag.includes('Open query')) {
                        tagColor = 'var(--color-status-sent-text)';
                        tagBg = 'var(--color-status-sent-surface)';
                        tagBorder = 'var(--color-status-sent-border)';
                      } else if (tag.includes('Leaving')) {
                        tagColor = 'var(--color-brand-text)';
                        tagBg = 'var(--color-brand-tint)';
                        tagBorder = 'var(--color-brand-tint-border)';
                      }

                      return (
                        <span
                          key={tag}
                          data-testid={`status-tag-${emp.employee_id}-${tag.toLowerCase().replace(/\s+/g, '-')}`}
                          style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            padding: '1px 6px',
                            fontSize: '10px',
                            fontWeight: 500,
                            borderRadius: 'var(--radius-pill)',
                            backgroundColor: tagBg,
                            border: `1px solid ${tagBorder}`,
                            color: tagColor,
                            whiteSpace: 'nowrap',
                          }}
                        >
                          {tag}
                        </span>
                      );
                    })}
                  </div>
                  {emp.subtitle && (
                    <span style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>
                      {emp.subtitle}
                    </span>
                  )}
                </div>
              </div>
              <ChevronRight size={16} color="var(--color-text-muted)" style={{ flexShrink: 0 }} />
            </button>
          ))
        )}
      </div>
    </div>
  );
};
