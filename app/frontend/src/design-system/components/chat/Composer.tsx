import React, { useState, useEffect, useRef } from 'react';
import { Send } from 'lucide-react';

interface ComposerProps {
  onSendMessage: (text: string) => void;
  placeholder?: string;
  disabled?: boolean;
  isMobile?: boolean;
  prefilledText?: string;
}

export const Composer: React.FC<ComposerProps> = ({
  onSendMessage,
  placeholder = 'Ask a question about payroll or salary...',
  disabled = false,
  isMobile = false,
  prefilledText,
}) => {
  const [text, setText] = useState(prefilledText || '');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (prefilledText !== undefined) {
      setText(prefilledText);
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
        if (prefilledText) {
          textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
        }
      }
    }
  }, [prefilledText]);


  const handleSend = () => {
    const trimmed = text.trim();
    if (!trimmed || disabled) return;
    onSendMessage(trimmed);
    setText('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setText(e.target.value);
    // Auto resize
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  };

  return (
    <div
      className={`hcm-composer-container ${isMobile ? 'hcm-composer-mobile' : 'hcm-composer-desktop'}`}
      data-testid="composer-container"
    >
      <div className="hcm-composer-box">
        <textarea
          ref={textareaRef}
          value={text}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={disabled}
          rows={1}
          className="hcm-composer-input"
          data-testid="composer-textarea"
          aria-label="Chat composer input"
        />
        <button
          type="button"
          onClick={handleSend}
          disabled={disabled || !text.trim()}
          className="hcm-composer-send-btn"
          data-testid="composer-send-btn"
          aria-label="Send message"
        >
          <Send size={16} />
        </button>
      </div>
    </div>
  );
};
