import React from 'react';
import { formatLocalTime } from '../../../utils/format';

interface UserBubbleProps {
  text: string;
  time?: string;
}

export const UserBubble: React.FC<UserBubbleProps> = ({ text, time }) => {
  const displayTime = time || formatLocalTime(new Date());
  return (
    <div className="hcm-user-turn-wrapper" data-testid="user-turn">
      <div className="hcm-user-bubble">
        <p className="hcm-user-bubble-text">{text}</p>
      </div>
      <span className="hcm-message-timestamp">{displayTime}</span>
    </div>
  );
};
