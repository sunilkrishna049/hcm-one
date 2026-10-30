import React from 'react';
import { CertaintyLabel } from './CertaintyLabel';
import { SourceLink } from './SourceLink';


export interface ComponentItem {
  id?: string;
  name: string;
  amount: number | null;
  certainty?: string;
  category?: 'earning' | 'deduction' | 'settlement' | 'recovery';
  source?: string;
  dueDate?: string;
  reason?: string;
  onViewProof?: () => void;
}

interface ComponentListProps {
  title?: string;
  items: ComponentItem[];
  emptyMessage?: string;
  showDueDates?: boolean;
}

export const ComponentList: React.FC<ComponentListProps> = ({
  title,
  items,
  emptyMessage = "No line items to display.",
  showDueDates = false,
}) => {
  if (!items || items.length === 0) {
    return <div style={{ color: 'var(--color-text-secondary)', padding: 'var(--space-4)' }}>{emptyMessage}</div>;
  }

  return (
    <div className="hcm-component-list" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
      {title && (
        <div style={{
          fontSize: 'var(--font-size-label)',
          fontWeight: 'var(--font-weight-semibold)',
          color: 'var(--color-text-primary)',
          textTransform: 'uppercase',
          letterSpacing: '0.05em',
          paddingBottom: 'var(--space-1)',
          borderBottom: '1px solid var(--color-divider)'
        }}>
          {title}
        </div>
      )}

      <div className="hcm-table-container">
        <table className="hcm-table">
          <thead>
            <tr>
              <th>Component</th>
              <th className="hcm-table-num">Amount (INR)</th>
              <th>Status</th>
              {showDueDates && <th>Recorded Due Date</th>}
              <th>Source / Proof</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item, idx) => (
              <tr key={item.id || idx}>
                <td data-label="Component">
                  <div style={{ fontWeight: 'var(--font-weight-medium)' }}>{item.name}</div>
                  {item.reason && (
                    <div style={{ fontSize: 'var(--font-size-small)', color: 'var(--color-text-secondary)' }}>
                      {item.reason}
                    </div>
                  )}
                </td>
                <td className="hcm-table-num" data-label="Amount (INR)" style={{ fontWeight: 'var(--font-weight-medium)' }}>
                  {item.amount !== null && item.amount !== undefined
                    ? item.amount.toLocaleString('en-IN')
                    : <span style={{ color: 'var(--color-status-warning-text)' }}>Incomplete</span>}
                </td>
                <td data-label="Status">
                  {item.certainty ? (
                    <CertaintyLabel certainty={item.certainty} />
                  ) : null}
                </td>
                {showDueDates && (
                  <td data-label="Due Date">
                    {item.dueDate ? (
                      <div>
                        <div>{item.dueDate}</div>
                        <div style={{ fontSize: '11px', color: 'var(--color-text-secondary)', fontStyle: 'italic' }}>
                          Calculated amount
                        </div>
                      </div>
                    ) : (
                      <span style={{ color: 'var(--color-text-secondary)' }}>-</span>
                    )}
                  </td>
                )}
                <td data-label="Source / Proof">
                  {item.onViewProof ? (
                    <SourceLink source="View calculation proof" onClick={item.onViewProof} />
                  ) : item.source ? (
                    <SourceLink source={item.source} />
                  ) : (
                    <span style={{ color: 'var(--color-text-secondary)' }}>-</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
