import React from "react";
import type { CertaintyType } from "./CertaintyLabel";
import { Button } from "./Button";
import { SourceLink } from "./SourceLink";
import { Calculator, Flag } from "lucide-react";
import "../components.css";

export interface NumberCardProps {
  label: string;
  value?: number | string | null;
  amount?: number | string | null;
  currency?: string;
  certainty?: CertaintyType | string | null;
  isHero?: boolean;
  isMobile?: boolean;
  variant?: "hero-desktop" | "hero-mobile" | "regular";
  flags?: string[];
  source?: string;
  onShowCalculation?: () => void;
  onViewProof?: () => void;
  className?: string;
}

export const NumberCard: React.FC<NumberCardProps> = ({
  label,
  value,
  amount,
  currency = "INR",
  isHero = false,
  isMobile = false,
  variant,
  flags = [],
  source,
  onShowCalculation,
  onViewProof,
  className = ""
}) => {
  const actualVal = amount !== undefined ? amount : value;
  const isAvailable = actualVal !== undefined && actualVal !== null;

  let displayAmount = "Not available in generated data";
  if (isAvailable) {
    if (typeof actualVal === "number") {
      displayAmount = actualVal.toLocaleString("en-IN");
    } else {
      displayAmount = `${actualVal}`;
    }
  }

  const effectiveHero = isHero || variant === "hero-desktop" || variant === "hero-mobile";
  const effectiveMobile = isMobile || variant === "hero-mobile";

  const cardClass = effectiveHero ? "hcm-number-card hcm-number-card-hero" : "hcm-number-card";
  const amountClass = effectiveHero
    ? effectiveMobile
      ? "hcm-amount-hero-mobile"
      : "hcm-amount-hero-desktop"
    : "hcm-amount-regular";

  const proofHandler = onViewProof || onShowCalculation;

  return (
    <div className={`${cardClass} ${className}`}>
      <div className="hcm-number-card-label">
        <span>{label}</span>
      </div>

      <div className="hcm-number-card-amount" style={{ display: 'flex', alignItems: 'baseline', gap: '8px', flexWrap: 'wrap' }}>
        <span className={`${amountClass} tnum`}>{displayAmount}</span>
        {isAvailable && currency && <span className="hcm-currency-label">{currency}</span>}
      </div>

      {source && (
        <div style={{ fontSize: "var(--font-size-small)", marginTop: "var(--space-1)" }}>
          <SourceLink source={source} />
        </div>
      )}

      {flags && flags.length > 0 && (
        <div style={{ display: "flex", flexWrap: "wrap", gap: "var(--space-1)", marginTop: "var(--space-1)" }}>
          {flags.map((flag, idx) => (
            <span key={idx} className="hcm-calc-flag-badge">
              <Flag size={12} aria-hidden="true" />
              <span>{flag}</span>
            </span>
          ))}
        </div>
      )}

      {proofHandler && (
        <div className="hcm-number-card-footer">
          <Button
            variant="ghost"
            size="sm"
            onClick={proofHandler}
            aria-label={`Show calculation for ${label}`}
          >
            <Calculator size={14} aria-hidden="true" />
            <span>Show calculation proof</span>
          </Button>
        </div>
      )}
    </div>
  );
};
