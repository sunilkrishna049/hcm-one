import React from "react";
import { Sparkles } from "lucide-react";
import "../components.css";

export interface MessageBubbleProps {
  message?: string;
  text?: string;
  author?: string;
  className?: string;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({
  message,
  text,
  author = "HCM One Assistant",
  className = ""
}) => {
  const content = text || message || "";

  return (
    <div className={`hcm-message-bubble ${className}`} role="region" aria-label="Assistant message">
      <div className="hcm-message-avatar" aria-hidden="true">
        <Sparkles size={16} />
      </div>
      <div className="hcm-message-content">
        <div className="hcm-message-author">{author}</div>
        <div className="hcm-message-text">{content}</div>
      </div>
    </div>
  );
};
