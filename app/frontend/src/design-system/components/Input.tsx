import React from "react";
import "../components.css";

interface FormGroupProps {
  label: string;
  htmlFor?: string;
  error?: string;
  children: React.ReactNode;
  className?: string;
}

export const FormGroup: React.FC<FormGroupProps> = ({
  label,
  htmlFor,
  error,
  children,
  className = ""
}) => {
  return (
    <div className={`hcm-form-group ${className}`}>
      <label htmlFor={htmlFor} className="hcm-form-label">
        {label}
      </label>
      {children}
      {error && (
        <span style={{ fontSize: "var(--font-size-small)", color: "var(--color-status-error-text)", marginTop: "var(--space-1)" }}>
          {error}
        </span>
      )}
    </div>
  );
};

export const Input: React.FC<React.InputHTMLAttributes<HTMLInputElement>> = ({ className = "", ...props }) => {
  return <input className={`hcm-input ${className}`} {...props} />;
};

export const Textarea: React.FC<React.TextareaHTMLAttributes<HTMLTextAreaElement>> = ({ className = "", ...props }) => {
  return <textarea className={`hcm-textarea ${className}`} {...props} />;
};

export const Select: React.FC<React.SelectHTMLAttributes<HTMLSelectElement>> = ({ className = "", children, ...props }) => {
  return <select className={`hcm-select ${className}`} {...props}>{children}</select>;
};
