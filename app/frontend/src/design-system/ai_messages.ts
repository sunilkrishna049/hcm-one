/**
 * Approved AI sentences C01 through C52 from screen-specs.md, conversation-design.md, and DEC-029.
 * Exact approved text. No LLM generation. Only slot interpolation.
 */

export const AI_MESSAGES: Record<string, string> = {
  C01: "I am HCM One's AI payroll assistant. I explain payroll records and payroll calculation results. I can help prepare a proposal or a query for you to review. I cannot approve a change, apply it or pay it. I send a query only after you confirm.",
  C02: "From which date should this proposed hike take effect?",
  C03: "This is a proposal for the recorded affected months.",
  C04: "Approving records this version and the selected scope as ready for payroll. It does not apply the change or make a payment.",
  C05: "Your edit will create a revised proposal. HCM One will recheck the affected amounts and totals. You will need to review the new version before approving it.",
  C06: "I am waiting for the payroll records needed for this request. The result is not ready.",
  C07: "The required {record_type} for {period_or_component} is missing. I cannot explain a complete result for this scope.",
  C08: "The applicable rule basis for {affected_scope} is not verified. That part cannot be calculated.",
  C09: "The payroll calculation did not produce a usable result for {affected_scope}. I cannot give a complete amount for it.",
  C10: "I cannot provide that information. I can help with payroll records you are authorized to access.",
  C11: "I can explain the tax recorded in your payroll. I cannot recommend a tax regime or investment. Please consult a tax professional for personal advice.",
  C12: "Send this query with the listed evidence to HR?",
  C13: "Add this description and the listed evidence to your selected open query?",
  C14: "Is this the same issue as your open query, or a different issue?",
  C15: "Your query is Sent. HR can access it for review.",
  C16: "Your query is In review. HR has taken it for review.",
  C17: "Your query has not been sent. It remains a draft.",
  C18: "This statement explains the scope approved by HR. Approval does not mean payment.",
  C19: "The final net is incomplete because {recorded_unresolved_component} is not yet known.",
  C20: "This is the applicable recorded due date. This assistant has not made a payment.",
  C21: "I can use only your own payroll records. I cannot check your bank credit or give personal tax, legal or financial advice.",
  C22: "The payroll calculation detail includes projected yearly income, applied deductions and exemptions, yearly tax, tax already deducted and remaining months. It identifies your recorded tax regime and applicable rule version.",
  C23: "HR recorded a resolution. Here is the recorded reply. You can dispute the resolution if it does not answer your issue.",
  C24: "Your query is Closed. Its history is retained. A new issue can be drafted separately.",
  C25: "This proposal changed after you reviewed it. Review the current version before approving.",
  C26: "This explains the recorded months. I cannot promise next month's pay. It depends on that month's recorded inputs and applicable rules.",
  C27: "Would you like the earnings and deductions breakdown?",
  C28: "The available payroll records do not explain this difference. I can help draft a query for HR.",
  C29: "Your TDS is higher because you declared income from your previous employer for {declared_months}. That income is added to your yearly income, so your expected yearly tax is higher. The tax your previous employer already deducted is counted, so it is not deducted twice.",
  C30: "Your {later_month} take-home is {net_change_amount} {lower_or_higher} than {earlier_month}. The main recorded reasons are below.",
  C31: "Hi {first_name}. What would you like to do today?",
  C32: "This is a proposal for the recorded {bonus_type} for {period}.",
  C33: "I didn't quite get that. Here is what I can help with:",
  C34: "I don't have a record of that in your payroll data. You can raise a query with HR.",
  C35: "I can show your pay for {available_months} only.",
  C36: "{n} days of loss of pay were recorded in your {month} attendance. If that's not right, you can raise a query.",
  C37: "Your PF deduction for {month} is {amount}.",
  C38: "Your tax deducted (TDS) for {month} is {amount}. It's worked out as your remaining yearly tax divided by the months left in the tax year.",
  C39: "Here is your {month} payslip:",
  C40: "Your {month} query is {status}. No reply has been recorded yet.",
  C41: "You are on the {regime} tax regime for {tax_year}.",
  C42: "{Name}'s {month} take-home is {amount} lower than {previous month}. The main recorded reasons are below.",
  C43: "{Name}'s {month} query is {status}. No reply has been recorded yet.",
  C44: "Your {month} query is {status}. Here is HR's reply:",
  C45: "Queries can't be deleted. You can close it instead.",
  C46: "Nothing is waiting for your approval.",
  C47: "{n} employees have a last working day in {month}:",
  C48: "{n} proposals are ready for your approval.",
  C49: "{n} need input before they can be approved.",
  C50: "Draft a reply to {Name}'s query. Nothing is sent until you confirm.",
  C51: "Mark {Name}'s query as resolved?",
  C52: "Did you mean one of these?",
};

export function getAIMessage(code: string, slots?: Record<string, string>): string {
  const template = AI_MESSAGES[code] || "";
  if (!slots) return template;
  return template.replace(/\{([\w\s]+)\}/g, (_, key) => {
    const trimmed = key.trim();
    const underscoreKey = trimmed.replace(/\s+/g, '_');
    return slots[trimmed] ?? slots[underscoreKey] ?? `{${key}}`;
  });
}
