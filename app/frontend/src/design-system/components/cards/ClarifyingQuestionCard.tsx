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
      selected_choice?: string;
    };
  };
  onApplySelection?: (choice: string) => void;
}

export const ClarifyingQuestionCard: React.FC<ClarifyingQuestionCardProps> = ({
  card,
  onApplySelection,
}) => {
  const choices = card.data.choices || ['2026-04-01', '2026-07-01', '2026-09-01'];
  const [selected, setSelected] = useState<string>(card.data.selected_choice || choices[0]);

  return (
    <div className="hcm-rich-card hcm-card-clarifying" data-testid={`card-${card.id}`}>
      <div className="hcm-card-header">
        <h4 className="hcm-card-title">{card.title}</h4>
      </div>

      <div className="hcm-card-body">
        <p className="hcm-clarifying-question">
          {card.data.question || 'From which date should this proposed hike take effect?'}
        </p>

        <div className="hcm-choice-chips-row">
          {choices.map((choice) => (
            <button
              key={choice}
              type="button"
              className={`hcm-choice-chip tnum ${selected === choice ? 'hcm-choice-selected' : ''}`}
              onClick={() => setSelected(choice)}
            >
              {choice}
            </button>
          ))}
        </div>

        {onApplySelection && (
          <div className="hcm-card-footer-action">
            <button
              type="button"
              className="hcm-button hcm-button-primary hcm-button-sm"
              onClick={() => onApplySelection(selected)}
            >
              Apply Selection and Recalculate
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
