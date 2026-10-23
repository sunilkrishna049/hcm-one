/**
 * Formatting utilities for HCM One Prototype.
 * Presentation only: never calculates, rounds, ranks or invents numbers.
 * Enforces Indian rupee format with Indian grouping and real minus sign (−).
 */

export function formatINR(val: number | null | undefined): string {
  if (val === null || val === undefined) {
    return "Not available in generated data";
  }
  const isNeg = val < 0;
  const absVal = Math.abs(val);
  const rounded = Math.round(absVal);
  const s = rounded.toString();

  let formatted = "";
  if (s.length > 3) {
    const last3 = s.slice(-3);
    let remaining = s.slice(0, -3);
    const groups: string[] = [];
    while (remaining.length > 2) {
      groups.unshift(remaining.slice(-2));
      remaining = remaining.slice(0, -2);
    }
    if (remaining.length > 0) {
      groups.unshift(remaining);
    }
    formatted = groups.join(",") + "," + last3;
  } else {
    formatted = s;
  }

  const minusSign = isNeg ? "−" : "";
  return `${minusSign}₹${formatted}`;
}

export function formatNumberPlain(val: number | null | undefined): string {
  if (val === null || val === undefined) {
    return "Not available in generated data";
  }
  const isNeg = val < 0;
  const absVal = Math.abs(val);
  const rounded = Math.round(absVal);
  const s = rounded.toString();

  let formatted = "";
  if (s.length > 3) {
    const last3 = s.slice(-3);
    let remaining = s.slice(0, -3);
    const groups: string[] = [];
    while (remaining.length > 2) {
      groups.unshift(remaining.slice(-2));
      remaining = remaining.slice(0, -2);
    }
    if (remaining.length > 0) {
      groups.unshift(remaining);
    }
    formatted = groups.join(",") + "," + last3;
  } else {
    formatted = s;
  }

  const minusSign = isNeg ? "−" : "";
  return `${minusSign}${formatted}`;
}
