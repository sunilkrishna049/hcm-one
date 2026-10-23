import React from "react";
import { ExternalLink } from "lucide-react";
import "../components.css";

export function formatHumanSourceLabel(source?: string, recordId?: string): string {
  if (recordId) {
    if (recordId.startsWith("REV-")) return `Salary revision ${recordId}`;
    if (recordId.startsWith("ATT-")) {
      const parts = recordId.split("-");
      if (parts.length >= 3) {
        return `Attendance record (${parts.slice(1).join("-")})`;
      }
      return `Attendance record ${recordId}`;
    }
    if (recordId.startsWith("SS-")) return `Salary structure ${recordId}`;
    if (recordId.startsWith("DECL-")) return `Tax declaration ${recordId}`;
    if (recordId.startsWith("PAY-")) return `Payroll record ${recordId}`;
    if (recordId.startsWith("QUERY-")) return `Query record ${recordId}`;
    return recordId;
  }
  if (!source) return "Calculation proof";
  if (source.includes("flows.py") || source.includes("engine/")) return "Calculation proof";
  if (source.includes("employment.json")) return "Employment contract";
  if (source.includes("attendance.json")) return "Attendance record";
  if (source.includes("declarations.json")) return "Employee declaration";
  if (source.includes("statutory-rates.json") || source.includes("pf-rules.json")) return "Statutory EPFO rules";
  if (source.includes("tax-rules.json")) return "Income tax rules";
  if (source.includes("company-settings.json") || source.includes("company-policies.json")) return "Company policy";
  if (source.includes("settlement-rules.json")) return "Settlement policy";
  return "Calculation source";
}

export interface SourceLinkProps {
  sourceFile?: string;
  source?: string;
  recordId?: string;
  onClick?: () => void;
  className?: string;
}

export const SourceLink: React.FC<SourceLinkProps> = ({
  sourceFile,
  source,
  recordId,
  onClick,
  className = ""
}) => {
  const file = source || sourceFile;
  if (!recordId && !file) return null;

  const label = formatHumanSourceLabel(file, recordId);

  if (onClick) {
    return (
      <button
        type="button"
        onClick={onClick}
        className={`hcm-source-link ${className}`}
        title={`View source: ${label}`}
      >
        <span>{label}</span>
        <ExternalLink size={12} aria-hidden="true" />
      </button>
    );
  }

  return (
    <span className={`text-muted ${className}`} title={label}>
      {label}
    </span>
  );
};

