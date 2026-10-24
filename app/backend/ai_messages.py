"""Approved AI copy sentences C01 through C29 from screen-specs.md Section 7 and DEC-029.
No dynamic AI or LLM generation. Only authorized slot filling.
"""

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
}


def get_message(code: str, **kwargs) -> str:
    template = AI_MESSAGES.get(code, "")
    if kwargs:
        if "first name" in kwargs and "first_name" not in kwargs:
            kwargs["first_name"] = kwargs["first name"]
        try:
            return template.format(**kwargs)
        except KeyError:
            return template
    return template

