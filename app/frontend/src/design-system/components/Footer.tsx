import React from 'react';

export const Footer: React.FC = () => {
  return (
    <footer className="hcm-demo-footer">
      <div>
        <strong>HCM One Payroll Assistant Prototype</strong> &mdash; Fictional data disclaimer:
      </div>
      <div style={{ marginTop: 'var(--space-1)', fontWeight: 'var(--font-weight-medium)', color: 'var(--color-text-primary)' }}>
        Demo with fictional data. Not for real payroll.
      </div>
      <div style={{ marginTop: 'var(--space-2)', fontSize: '11px', color: 'var(--color-text-secondary)' }}>
        Zero LLM calls &bull; Approved sentences C01–C29 &bull; Deterministic engine calculations &bull; Silence is never approval
      </div>
    </footer>
  );
};
