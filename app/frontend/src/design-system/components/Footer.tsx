import React from 'react';

export const Footer: React.FC = () => {
  return (
    <footer className="hcm-demo-footer">
      <div style={{ fontWeight: 'var(--font-weight-medium)', color: 'var(--color-text-secondary)', fontSize: '13px' }}>
        Demo with fictional data. Not for real payroll.
      </div>
    </footer>
  );
};
