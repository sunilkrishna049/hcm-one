import React from 'react';

interface UserBubbleProps {
  text: string;
  time?: string;
}

export const UserBubble: React.FC<UserBubbleProps> = ({ text, time = 'Just now' }) => {
  return (
    <div className="hcm-user-turn-wrapper" data-testid="user-turn">
      <div className="hcm-user-bubble">
        <p className="hcm-user-bubble-text">{text}</p>
      </div>
      <span className="hcm-message-timestamp">{time}</span>
    </div>
  );
};
