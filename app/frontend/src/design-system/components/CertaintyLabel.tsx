import React from "react";
import { CheckCircle2, AlertTriangle, AlertCircle, HelpCircle, FileQuestion } from "lucide-react";
import "../components.css";

export type CertaintyType =
  | "Complete for this scope"
  | "Complete"
  | "Incomplete"
  | "Rule not verified"
  | "Needs HR decision"
  | "Cannot explain from available payroll data"
  | string;

interface CertaintyLabelProps {
  certainty?: CertaintyType | null;
  className?: string;
}

export const CertaintyLabel: React.FC<CertaintyLabelProps> = ({ certainty, className = "" }) => {
  if (!certainty) return null;

  const normalized = certainty.trim();
  let badgeClass = "hcm-certainty-incomplete";
  let Icon = AlertTriangle;

  if (normalized === "Complete for this scope" || normalized === "Complete") {
    badgeClass = "hcm-certainty-complete";
    Icon = CheckCircle2;
  } else if (normalized === "Incomplete") {
    badgeClass = "hcm-certainty-incomplete";
    Icon = AlertTriangle;
  } else if (normalized === "Rule not verified") {
    badgeClass = "hcm-certainty-unverified";
    Icon = AlertCircle;
  } else if (normalized === "Needs HR decision") {
    badgeClass = "hcm-certainty-needs-decision";
    Icon = HelpCircle;
  } else if (normalized === "Cannot explain from available payroll data") {
    badgeClass = "hcm-certainty-unexplained";
    Icon = FileQuestion;
  } else if (normalized === "Permission denied") {
    badgeClass = "hcm-certainty-unverified";
    Icon = AlertCircle;
  } else {
    // Fallback for custom or unknown statuses
    badgeClass = "hcm-certainty-incomplete";
    Icon = AlertTriangle;
  }

  return (
    <span className={`hcm-certainty-badge ${badgeClass} ${className}`}>
      <Icon size={14} aria-hidden="true" />
      <span>{certainty}</span>
    </span>
  );
};

