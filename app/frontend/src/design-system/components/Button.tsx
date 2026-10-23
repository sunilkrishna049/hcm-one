import React from "react";
import "../components.css";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "outline" | "danger" | "ghost";
  size?: "default" | "sm";
  children: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
  variant = "primary",
  size = "default",
  className = "",
  children,
  ...props
}) => {
  const variantClass = `hcm-button-${variant}`;
  const sizeClass = size === "sm" ? "hcm-button-sm" : "";
  return (
    <button
      className={`hcm-button ${variantClass} ${sizeClass} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
};
