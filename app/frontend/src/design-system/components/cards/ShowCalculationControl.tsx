import React from 'react';
import { Calculator } from 'lucide-react';

interface ShowCalculationControlProps {
  card?: {
    id: string;
    type: string;
    title: string;
    certainty: string;
    data: {
      button_label?: string;
    };
  };
  label?: string;
  onShowCalculation: () => void;
}

export const ShowCalculationControl: React.FC<ShowCalculationControlProps> = ({
  card,
  label,
  onShowCalculation,
}) => {
  const displayLabel = label || card?.data?.button_label || 'Show calculation';

  return (
    <div className="hcm-show-calc-control" data-testid="show-calculation-control">
      <button
        type="button"
        className="hcm-button hcm-button-outline"
        onClick={onShowCalculation}
        aria-label="Show calculation proof"
      >
        <Calculator size={16} aria-hidden="true" />
        <span>{displayLabel}</span>
      </button>
    </div>
  );
};
