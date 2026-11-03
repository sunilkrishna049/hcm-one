import React from 'react';

export const Footer: React.FC = () => {
  return (
    <footer className="hcm-demo-footer">
      <div
        data-testid="bottom-composer-note"
        style={{ fontWeight: 'var(--font-weight-medium)', color: 'var(--color-text-secondary)', fontSize: '13px' }}
      >
        Demo with fictional data. HCM One never approves, applies or pays anything on its own.
      </div>
    </footer>
  );
};
