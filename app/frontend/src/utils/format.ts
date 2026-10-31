/**
 * Formatting utilities for HCM One Prototype.
 * Presentation only: never calculates, rounds, ranks or invents numbers.
 * Enforces Indian rupee format with Indian grouping and real minus sign (−).
 */

export function formatINR(val: number | null | undefined): string {
  if (val === null || val === undefined) {
    return "";
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
    return "";
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

const MONTH_NAMES = [
  "Jan", "Feb", "Mar", "Apr", "May", "Jun",
  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
];

/**
 * Dates as people read them (presentation only):
 * "2026-04-01" -> "1 Apr 2026"
 * "2026-04" -> "Apr 2026"
 * "2026-04 to 2026-09" -> "Apr–Sep 2026"
 * "6 months (2026-04 to 2026-09)" -> "6 months (Apr–Sep 2026)"
 */
export function formatHumanDate(dateStr: string | null | undefined): string {
  if (!dateStr || typeof dateStr !== "string") return "";

  // 1. Range: "2026-04 to 2026-09" -> "Apr–Sep 2026"
  const rangeMatch = dateStr.match(/^(\d{4})-(\d{2})\s+to\s+(\d{4})-(\d{2})$/);
  if (rangeMatch) {
    const [, y1, m1, y2, m2] = rangeMatch;
    const month1 = MONTH_NAMES[parseInt(m1, 10) - 1] || m1;
    const month2 = MONTH_NAMES[parseInt(m2, 10) - 1] || m2;
    if (y1 === y2) {
      return `${month1}–${month2} ${y1}`;
    }
    return `${month1} ${y1}–${month2} ${y2}`;
  }

  // Embedded range: e.g. "6 months (2026-04 to 2026-09)" -> "6 months (Apr–Sep 2026)"
  if (dateStr.includes(" to ")) {
    return dateStr.replace(/(\d{4})-(\d{2})\s+to\s+(\d{4})-(\d{2})/g, (_, y1, m1, y2, m2) => {
      const month1 = MONTH_NAMES[parseInt(m1, 10) - 1] || m1;
      const month2 = MONTH_NAMES[parseInt(m2, 10) - 1] || m2;
      return y1 === y2 ? `${month1}–${month2} ${y1}` : `${month1} ${y1}–${month2} ${y2}`;
    });
  }

  // 2. Full date: "2026-04-01" -> "1 Apr 2026"
  const dateMatch = dateStr.match(/^(\d{4})-(\d{2})-(\d{2})$/);
  if (dateMatch) {
    const [, y, m, d] = dateMatch;
    const day = parseInt(d, 10);
    const month = MONTH_NAMES[parseInt(m, 10) - 1] || m;
    return `${day} ${month} ${y}`;
  }

  // 3. Month only: "2026-04" -> "Apr 2026"
  const monthMatch = dateStr.match(/^(\d{4})-(\d{2})$/);
  if (monthMatch) {
    const [, y, m] = monthMatch;
    const month = MONTH_NAMES[parseInt(m, 10) - 1] || m;
    return `${month} ${y}`;
  }

  return dateStr;
}

export function formatShortMonth(monthStr: string | null | undefined): string {
  if (!monthStr) return "";
  const match = monthStr.match(/^\d{4}-(\d{2})/);
  if (match) {
    const m = parseInt(match[1], 10);
    return MONTH_NAMES[m - 1] || monthStr;
  }
  return monthStr;
}

/**
 * Format timestamp into viewer's local time with timezone abbreviation.
 * Example output: "24 Oct 2026, 8:56 pm IST"
 */
export function formatLocalTime(dateInput?: Date | string | null): string {
  if (!dateInput) return "";
  const date = typeof dateInput === "string" ? new Date(dateInput) : dateInput;
  if (isNaN(date.getTime())) {
    return String(dateInput);
  }

  const formatter = new Intl.DateTimeFormat("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
    hour12: true,
    timeZoneName: "short",
  });

  return formatter.format(date);
}
