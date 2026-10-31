import React from "react";
import { CertaintyLabel } from "./CertaintyLabel";
import { Flag } from "lucide-react";
import "../components.css";

export interface CalculationObject {
  value?: any;
  formula?: string;
  inputs?: Array<{
    source_file?: string;
    record_id?: string;
    name?: string;
    value?: any;
    source?: string;
    fields?: string[];
  }>;
  rule_ids?: Array<any>;
  certainty?: string;
  flags?: string[];
  intermediate_steps?: string[];
}

export interface CalculationBreakdownProps {
  calculation?: CalculationObject | null;
  title?: string;
  formula?: string;
  inputs?: Array<{
    name?: string;
    value?: any;
    source?: string;
    source_file?: string;
    record_id?: string;
  }>;
  ruleIds?: Array<any>;
  intermediateSteps?: string[];
  certainty?: string;
  value?: any;
  className?: string;
}

export const CalculationBreakdown: React.FC<CalculationBreakdownProps> = ({
  calculation,
  title = "Calculation Proof",
  formula: directFormula,
  inputs: directInputs,
  ruleIds: directRuleIds,
  intermediateSteps: directSteps,
  certainty: directCertainty,
  value: directValue,
  className = ""
}) => {
  const effectiveFormula = directFormula || calculation?.formula;
  const effectiveInputs = directInputs || calculation?.inputs || [];
  const effectiveRules = directRuleIds || calculation?.rule_ids || [];
  const effectiveSteps = directSteps || calculation?.intermediate_steps || [];
  const effectiveCertainty = directCertainty || calculation?.certainty;
  const effectiveValue = directValue !== undefined ? directValue : calculation?.value;
  const flags = calculation?.flags || [];

  return (
    <div className={`hcm-calc-breakdown ${className}`}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h4 style={{ fontSize: "var(--font-size-title-section)", fontWeight: "var(--font-weight-semibold)", margin: 0 }}>
          {title}
        </h4>
        {effectiveCertainty && <CertaintyLabel certainty={effectiveCertainty} />}
      </div>

      {effectiveValue !== undefined && (
        <div className="hcm-calc-section">
          <span className="hcm-calc-section-title">Result Value</span>
          <div style={{ fontSize: "var(--font-size-card-number)", fontWeight: "var(--font-weight-medium)" }} className="tnum">
            {effectiveValue === null ? "" : `${effectiveValue} INR`}
          </div>
        </div>
      )}

      {effectiveFormula && (
        <div className="hcm-calc-section">
          <span className="hcm-calc-section-title">Formula</span>
          <div className="hcm-calc-formula">{effectiveFormula}</div>
        </div>
      )}

      {flags && flags.length > 0 && (
        <div className="hcm-calc-section">
          <span className="hcm-calc-section-title">Flags</span>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "var(--space-2)" }}>
            {flags.map((flag, idx) => (
              <span key={idx} className="hcm-calc-flag-badge">
                <Flag size={12} aria-hidden="true" />
                <span>{flag}</span>
              </span>
            ))}
          </div>
        </div>
      )}

      {effectiveInputs && effectiveInputs.length > 0 && (
        <div className="hcm-calc-section">
          <span className="hcm-calc-section-title">Inputs Provenance</span>
          <ul style={{ listStyle: "none", padding: 0, margin: 0, display: "flex", flexDirection: "column", gap: "var(--space-2)" }}>
            {effectiveInputs.map((inp, idx) => (
              <li key={idx} style={{ display: "flex", justifyContent: "space-between", fontSize: "var(--font-size-small)" }}>
                <span>{inp.name || inp.record_id || `Input #${idx + 1}`}: <strong>{inp.value !== undefined ? String(inp.value) : ""}</strong></span>
                <span className="record-id font-mono" style={{ color: "var(--color-text-secondary)" }}>
                  {inp.source || inp.source_file || ""}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {effectiveRules && effectiveRules.length > 0 && (
        <div className="hcm-calc-section">
          <span className="hcm-calc-section-title">Applicable Rules</span>
          <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-2)" }}>
            {effectiveRules.map((rule, idx) => {
              const ruleIdStr = typeof rule === 'string' ? rule : (rule.rule_id || JSON.stringify(rule));
              const ruleSource = typeof rule === 'object' ? rule.source : undefined;
              return (
                <div key={idx} className="hcm-calc-rule-item">
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <span className="hcm-calc-rule-id">{ruleIdStr}</span>
                    {ruleSource && <span style={{ fontSize: "11px", color: "var(--color-text-secondary)" }}>{ruleSource}</span>}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {effectiveSteps && effectiveSteps.length > 0 && (
        <div className="hcm-calc-section">
          <span className="hcm-calc-section-title">Calculation Steps</span>
          <ul style={{ paddingLeft: "var(--space-4)", margin: 0, fontSize: "var(--font-size-small)", display: "flex", flexDirection: "column", gap: "var(--space-1)" }}>
            {effectiveSteps.map((step, idx) => (
              <li key={idx} style={{ color: "var(--color-text-secondary)" }}>{step}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};
