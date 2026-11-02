"""Approved AI copy sentences C01 through C52 from screen-specs.md, conversation-design.md, and DEC-029.
No dynamic AI or LLM generation. Only authorized slot filling.
"""
import re
from typing import Dict, Optional

AI_MESSAGES = {
    "C01": "I am HCM One's AI payroll assistant. I explain payroll records and payroll calculation results. I can help prepare a proposal or a query for you to review. I cannot approve a change, apply it or pay it. I send a query only after you confirm.",
    "C02": "From which date should this proposed hike take effect?",
    "C03": "This is a proposal for the recorded affected months.",
    "C04": "Approving records this version and the selected scope as ready for payroll. It does not apply the change or make a payment.",
    "C05": "Your edit will create a revised proposal. HCM One will recheck the affected amounts and totals. You will need to review the new version before approving it.",
    "C06": "I am waiting for the payroll records needed for this request. The result is not ready.",
    "C07": "The required {record_type} for {period_or_component} is missing. I cannot explain a complete result for this scope.",
    "C08": "The applicable rule basis for {affected_scope} is not verified. That part cannot be calculated.",
    "C09": "The payroll calculation did not produce a usable result for {affected_scope}. I cannot give a complete amount for it.",
    "C10": "I cannot provide that information. I can help with payroll records you are authorized to access.",
    "C11": "I can explain the tax recorded in your payroll. I cannot recommend a tax regime or investment. Please consult a tax professional for personal advice.",
    "C12": "Send this query with the listed evidence to HR?",
    "C13": "Add this description and the listed evidence to your selected open query?",
    "C14": "Is this the same issue as your open query, or a different issue?",
    "C15": "Your query is Sent. HR can access it for review.",
    "C16": "Your query is In review. HR has taken it for review.",
    "C17": "Your query has not been sent. It remains a draft.",
    "C18": "This statement explains the scope approved by HR. Approval does not mean payment.",
    "C19": "The final net is incomplete because {recorded_unresolved_component} is not yet known.",
    "C20": "This is the applicable recorded due date. This assistant has not made a payment.",
    "C21": "I can use only your own payroll records. I cannot check your bank credit or give personal tax, legal or financial advice.",
    "C22": "The payroll calculation detail includes projected yearly income, applied deductions and exemptions, yearly tax, tax already deducted and remaining months. It identifies your recorded tax regime and applicable rule version.",
    "C23": "HR recorded a resolution. Here is the recorded reply. You can dispute the resolution if it does not answer your issue.",
    "C24": "Your query is Closed. Its history is retained. A new issue can be drafted separately.",
    "C25": "This proposal changed after you reviewed it. Review the current version before approving.",
    "C26": "This explains the recorded months. I cannot promise next month's pay. It depends on that month's recorded inputs and applicable rules.",
    "C27": "Would you like the earnings and deductions breakdown?",
    "C28": "The available payroll records do not explain this difference. I can help draft a query for HR.",
    "C29": "Your TDS is higher because you declared income from your previous employer for {declared_months}. That income is added to your yearly income, so your expected yearly tax is higher. The tax your previous employer already deducted is counted, so it is not deducted twice.",
    "C30": "Your {later_month} take-home is {net_change_amount} {lower_or_higher} than {earlier_month}. The main recorded reasons are below.",
    "C31": "Hi {first_name}. What would you like to do today?",
    "C32": "This is a proposal for the recorded {bonus_type} for {period}.",
    "C33": "I didn't quite get that. Here is what I can help with:",
    "C34": "I don't have a record of that in your payroll data. You can raise a query with HR.",
    "C35": "I can show your pay for {available_months} only.",
    "C36": "{n} days of loss of pay were recorded in your {month} attendance. If that's not right, you can raise a query.",
    "C37": "Your PF deduction for {month} is {amount}.",
    "C38": "Your tax deducted (TDS) for {month} is {amount}. It's worked out as your remaining yearly tax divided by the months left in the tax year.",
    "C39": "Here is your {month} payslip:",
    "C40": "Your {month} query is {status}. No reply has been recorded yet.",
    "C41": "You are on the {regime} tax regime for {tax_year}.",
    "C42": "{Name}'s {month} take-home is {amount} lower than {previous month}. The main recorded reasons are below.",
    "C43": "{Name}'s {month} query is {status}. No reply has been recorded yet.",
    "C44": "Your {month} query is {status}. Here is HR's reply:",
    "C45": "Queries can't be deleted. You can close it instead.",
    "C46": "Nothing is waiting for your approval.",
    "C47": "{n} employees have a last working day in {month}:",
    "C48": "{n} proposals are ready for your approval.",
    "C49": "{n} need input before they can be approved.",
    "C50": "Draft a reply to {Name}'s query. Nothing is sent until you confirm.",
    "C51": "Mark {Name}'s query as resolved?",
    "C52": "Did you mean one of these?",
    "C53": "Your PAN and bank details are masked and can't be shown in chat.",
    "C54": "{bonus_name}: {eligible} eligible, {not_eligible} not eligible, {waiting} waiting for input.",
    "C55": "{bonus_name}: {eligible} eligible, {not_eligible} not eligible.",
    "C56": "Can't approve yet: {Name}'s {missing item} is missing.",
    "C57": "Can't approve yet: {n} items need input.",
    "C58": "Your {month} take-home is {amount} lower than {previous month}. The main recorded reasons are below.",
    "C59": "Can't approve yet: {Name}'s {item} is pending.",
    "C60": "Your {month} take-home is the same as {previous month}.",
    "C61": "{Name}'s {month} take-home is the same as {previous month}.",
    "C62": "Your {month} TDS is {amount} higher than {previous month}. The main recorded reasons are below.",
    "C63": "{Name}'s {month} TDS is {amount} higher than {previous month}. The main recorded reasons are below.",
    "C64": "Here is the full and final settlement proposal for {Name}.",
    "C65": "{Name}'s {item} clearance is pending. I can't give a complete settlement until it's resolved.",
    "C66": "The final net will be known once the {item} recovery is resolved.",
    "C67": "No reply was recorded before this query was closed.",
    "C68": "Reason recorded. The amounts are unchanged because no recorded input was changed.",
    "C69": "Pick an employee to see what you can do for them:",
    "C70": "Here's what you can do for {Name}:",
    "C71": "I can't approve or reject from a chat message. Open the proposal and use its buttons.",
    "FAQ": "Here is the recorded meaning from the payroll glossary:",
    "REJECTED": "The proposal has been rejected.",
    "NO_QUERY": "You do not have any open payroll queries recorded.",
    "HR_NO_QUERY": "No open payroll query was found for {Name}.",
    "HR_QUERY_LIST": "Here are the recorded employee queries ({n} total):",
    "HR_QUERY_REPLY": "Reply recorded for {Name}'s query.",
}

# HR variants rewrite employee-voice "Your" -> "{Name}'s", "you" -> "they/their/them"
# per DEC-029 and Prompt 2c-2c Item 2 (name at most once, then they/their/them).
AI_MESSAGES_HR = {
    "C29": "{Name}'s TDS is higher because they declared income from their previous employer for {declared_months}. That income is added to their yearly income, so their expected yearly tax is higher. The tax their previous employer already deducted is counted, so it is not deducted twice.",
    "C30": "{Name}'s {later_month} take-home is {net_change_amount} {lower_or_higher} than {earlier_month}. The main recorded reasons are below.",
    "C36": "{n} days of loss of pay were recorded in {Name}'s {month} attendance.",
    "C37": "{Name}'s PF deduction for {month} is {amount}.",
    "C38": "{Name}'s tax deducted (TDS) for {month} is {amount}. It's worked out as their remaining yearly tax divided by the months left in the tax year.",
    "C39": "Here is {Name}'s {month} payslip:",
    "C41": "{Name} is on the {regime} tax regime for {tax_year}.",
    "C42": "{Name}'s {month} take-home is {amount} lower than {previous month}. The main recorded reasons are below.",
    "C43": "{Name}'s {month} query is {status}. No reply has been recorded yet.",
    "C50": "Draft a reply to {Name}'s query. Nothing is sent until you confirm.",
    "C51": "Mark {Name}'s query as resolved?",
    "C53": "{Name}'s PAN and bank details are masked and can't be shown in chat.",
    "C56": "Can't approve yet: {Name}'s {missing item} is missing.",
    "C57": "Can't approve yet: {n} items need input.",
    "C58": "{Name}'s {month} take-home is {amount} lower than {previous month}. The main recorded reasons are below.",
    "C59": "Can't approve yet: {Name}'s {item} is pending.",
    "C60": "{Name}'s {month} take-home is the same as {previous month}.",
    "C61": "{Name}'s {month} take-home is the same as {previous month}.",
    "C62": "{Name}'s {month} TDS is {amount} higher than {previous month}. The main recorded reasons are below.",
    "C63": "{Name}'s {month} TDS is {amount} higher than {previous month}. The main recorded reasons are below.",
    "C64": "Here is the full and final settlement proposal for {Name}.",
    "C65": "{Name}'s {item} clearance is pending. I can't give a complete settlement until it's resolved.",
    "C66": "The final net will be known once the {item} recovery is resolved.",
    "C67": "No reply was recorded before this query was closed.",
    "C68": "Reason recorded. The amounts are unchanged because no recorded input was changed.",
    "C69": "Pick an employee to see what you can do for them:",
    "C70": "Here's what you can do for {Name}:",
    "C71": "I can't approve or reject from a chat message. Open the proposal and use its buttons.",
    "HR_NO_QUERY": "No open payroll query was found for {Name}.",
    "HR_QUERY_REPLY": "Reply recorded for {Name}'s query.",
}


def get_message(code: str, role: str = "Employee", **kwargs) -> str:
    if code == "C57":
        if "count" not in kwargs and "n" in kwargs:
            kwargs["count"] = kwargs["n"]
        elif "n" not in kwargs and "count" in kwargs:
            kwargs["n"] = kwargs["count"]
    template = AI_MESSAGES.get(code, "")
    is_hr = role == "HR Admin" or "Name" in kwargs or "name" in kwargs or kwargs.get("role") == "HR Admin"
    if is_hr and code in AI_MESSAGES_HR:
        template = AI_MESSAGES_HR[code]

    if kwargs:
        if "first name" in kwargs and "first_name" not in kwargs:
            kwargs["first_name"] = kwargs["first name"]
        if "bonus type" in kwargs and "bonus_type" not in kwargs:
            kwargs["bonus_type"] = kwargs["bonus type"]
        if "available months" in kwargs and "available_months" not in kwargs:
            kwargs["available_months"] = kwargs["available months"]
        if "tax year" in kwargs and "tax_year" not in kwargs:
            kwargs["tax_year"] = kwargs["tax year"]
        if "Name" in kwargs and "name" not in kwargs:
            kwargs["name"] = kwargs["Name"]
        if "name" in kwargs and "Name" not in kwargs:
            kwargs["Name"] = kwargs["name"]
        if "previous month" in kwargs and "previous_month" not in kwargs:
            kwargs["previous_month"] = kwargs["previous month"]
        if "previous_month" in kwargs and "previous month" not in kwargs:
            kwargs["previous month"] = kwargs["previous_month"]
        if "later month" in kwargs and "later_month" not in kwargs:
            kwargs["later_month"] = kwargs["later month"]
        if "earlier month" in kwargs and "earlier_month" not in kwargs:
            kwargs["earlier_month"] = kwargs["earlier month"]
        if "net change amount" in kwargs and "net_change_amount" not in kwargs:
            kwargs["net_change_amount"] = kwargs["net change amount"]
        if "lower or higher" in kwargs and "lower_or_higher" not in kwargs:
            kwargs["lower_or_higher"] = kwargs["lower or higher"]
        if "declared months" in kwargs and "declared_months" not in kwargs:
            kwargs["declared_months"] = kwargs["declared months"]
        if "Bonus name" in kwargs and "bonus_name" not in kwargs:
            kwargs["bonus_name"] = kwargs["Bonus name"]
        if "bonus name" in kwargs and "bonus_name" not in kwargs:
            kwargs["bonus_name"] = kwargs["bonus name"]
        if "n_eligible" in kwargs and "eligible" not in kwargs:
            kwargs["eligible"] = kwargs["n_eligible"]
        if "n_not_eligible" in kwargs and "not_eligible" not in kwargs:
            kwargs["not_eligible"] = kwargs["n_not_eligible"]
        if "n_waiting" in kwargs and "waiting" not in kwargs:
            kwargs["waiting"] = kwargs["n_waiting"]
        if "waiting_for_input" in kwargs and "waiting" not in kwargs:
            kwargs["waiting"] = kwargs["waiting_for_input"]
        if "missing item" in kwargs and "missing_item" not in kwargs:
            kwargs["missing_item"] = kwargs["missing item"]
        if "missing_item" in kwargs and "missing item" not in kwargs:
            kwargs["missing item"] = kwargs["missing_item"]
        try:
            return template.format(**kwargs)
        except KeyError:
            return template
    return template


def template_to_regex(template: str) -> re.Pattern:
    """Converts a format template like '{Name}'s query is {status}.' to a matching regex pattern."""
    pat = re.escape(template)
    pat = re.sub(r'\\\{.*?\\\}', r'.+?', pat)
    return re.compile(f'^{pat}$')


def validate_message_text(code: str, text: str) -> bool:
    """Validates that a message code exists and its text equals the filled template."""
    candidate_templates = []
    if code in AI_MESSAGES:
        candidate_templates.append(AI_MESSAGES[code])
    if code in AI_MESSAGES_HR:
        candidate_templates.append(AI_MESSAGES_HR[code])

    if not candidate_templates:
        return False

    for tmpl in candidate_templates:
        reg = template_to_regex(tmpl)
        if reg.match(text):
            return True
    return False
