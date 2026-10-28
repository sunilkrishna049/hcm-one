import React, { useState } from 'react';

interface ClarifyingQuestionCardProps {
  card: {
    id: string;
    type: string;
    title: string;
    certainty: string;
    data: {
      question?: string;
      choices?: string[];
      selected_choice?: string | null;
    };
  };
  onApplySelection?: (choice: string) => void;
}

export const ClarifyingQuestionCard: React.FC<ClarifyingQuestionCardProps> = ({
  card,
  onApplySelection,
}) => {
  const choices = card.data.choices || ['2026-04-01', '2026-07-01', '2026-09-01'];
  const initialChoice = card.data.selected_choice || null;
  const [selected, setSelected] = useState<string | null>(initialChoice);
  const [isLocked, setIsLocked] = useState<boolean>(Boolean(initialChoice));

  const handleSelect = (choice: string) => {
    if (isLocked) return;
    setSelected(choice);
    setIsLocked(true);
    onApplySelection?.(choice);
  };

  // Show question once in header; no duplicate title and body text
  const questionText = card.title || card.data.question || 'From which date should this proposed hike take effect?';

  return (
    <div className="hcm-rich-card hcm-card-clarifying" data-testid={`card-${card.id}`}>
      <div className="hcm-card-header">
        <h4 className="hcm-card-title">{questionText}</h4>
      </div>

      <div className="hcm-card-body">
        <div className="hcm-choice-chips-row">
          {choices.map((choice) => (
            <button
              key={choice}
              type="button"
              className={`hcm-choice-chip tnum ${selected === choice ? 'hcm-choice-selected' : ''}`}
              onClick={() => handleSelect(choice)}
              disabled={isLocked}
              aria-pressed={selected === choice}
            >
              {choice}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
