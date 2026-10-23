import React from 'react';

export interface ChipItem {
  label: string;
  action?: string;
  payload?: any;
}

interface SuggestionChipsProps {
  chips: ChipItem[];
  onSelectChip: (chip: ChipItem) => void;
  disabled?: boolean;
}

export const SuggestionChips: React.FC<SuggestionChipsProps> = ({
  chips,
  onSelectChip,
  disabled = false,
}) => {
  if (!chips || chips.length === 0) return null;

  return (
    <div
      className="hcm-suggestion-chips-container"
      role="group"
      aria-label="Suggested follow-up actions"
      data-testid="suggestion-chips"
    >
      <div className="hcm-suggestion-chips-track">
        {chips.map((chip, idx) => (
          <button
            key={idx}
            type="button"
            className="hcm-suggestion-chip"
            data-testid={`suggestion-chip-${idx}`}
            disabled={disabled}
            onClick={() => onSelectChip(chip)}
          >
            {chip.label}
          </button>
        ))}
      </div>
    </div>
  );
};
