from crewai import Task


def create_qualification_task(agent, lead: dict) -> Task:
    return Task(
        description=f"""
Evaluate this lead for TechFi Labs outreach.

TechFi Labs services:
- Salesforce developers
- Salesforce QA automation
- Salesforce production support
- Salesforce managed support
- Flexible Salesforce staff augmentation
- Offshore Salesforce delivery support from India

Ideal leads:
- Founders, CTOs, Delivery Managers, Salesforce Managers, RevOps leaders, Partner Managers
- Companies using Salesforce
- IT agencies serving US/UK/EU clients
- Salesforce consulting firms needing extra delivery capacity
- Businesses hiring Salesforce developers, admins, QA, or support resources
- Teams that may need managed support, production support, staff augmentation, or implementation support

Lead:
First Name: {lead.get("first_name")}
Last Name: {lead.get("last_name")}
Email: {lead.get("email")}
Company: {lead.get("company_name")}
Title: {lead.get("title")}
Website: {lead.get("website")}
LinkedIn: {lead.get("linkedin_url")}
Service Angle: {lead.get("service_angle")}
Lead Source: {lead.get("lead_source")}
Country: {lead.get("country")}
Lead Type: {lead.get("lead_type")}
Pain Signal: {lead.get("pain_signal")}
Notes: {lead.get("notes")}

Return:
Qualified: Yes or No
Priority: High, Medium, or Low
Reason: one short reason
""",
        expected_output="Qualified status, priority, and one short reason.",
        agent=agent,
    )


def create_personalization_task(agent, lead: dict, qualification_context: str) -> Task:
    return Task(
        description=f"""
Create one short personalization hook for this lead.

Use only the lead details and qualification context. Do not invent facts.

Lead:
First Name: {lead.get("first_name")}
Company: {lead.get("company_name")}
Title: {lead.get("title")}
Service Angle: {lead.get("service_angle")}
Lead Source: {lead.get("lead_source")}
Country: {lead.get("country")}
Lead Type: {lead.get("lead_type")}
Pain Signal: {lead.get("pain_signal")}
Notes: {lead.get("notes")}

Qualification context:
{qualification_context}

Rules:
- Always start the hook with "Noticed".
- Mention the company name if available.
- Keep it factual.
- Maximum 15 words.
- Use pain_signal as the strongest input whenever it is available and relevant.
- If pain_signal is blank or weak, use lead_type plus company_name.
- If lead_type is blank or weak, use service_angle.
- Do not overpraise.
- Do not use "I see".
- Do not use "I noticed".
- Do not use "I was impressed".
- Do not invent facts.
- Do not use generic phrases like "innovative tech solutions", "amazing work", "impressed by", or "leading company".
- If pain_signal mentions Salesforce hiring, delivery support, QA automation, staff augmentation, managed support, or US Salesforce clients, prefer that signal directly.
- If notes are weak or generic, keep the hook simple and company-based.

Good examples:
- Noticed ABC Consulting recently posted a Salesforce QA automation role.
- Noticed ABC Consulting works with US Salesforce clients.
- Noticed ABC Consulting may need Salesforce staff augmentation support.
- Noticed ABC Consulting is hiring Salesforce talent.
- Noticed ABC Consulting is active in Salesforce delivery support.

Bad examples:
- I noticed ABC Consulting focuses on innovative tech solutions.
- I was impressed by ABC Consulting.
- Noticed your amazing work.

Return only the personalization hook.
""",
        expected_output="One short personalization hook.",
        agent=agent,
    )


def create_email_writer_task(
    agent,
    lead: dict,
    qualification_context: str,
    personalization_hook: str,
) -> Task:
    return Task(
        description=f"""
Write a structured JSON outreach draft for TechFi Labs.

Lead:
First Name: {lead.get("first_name")}
Last Name: {lead.get("last_name")}
Email: {lead.get("email")}
Company: {lead.get("company_name")}
Title: {lead.get("title")}
Service Angle: {lead.get("service_angle")}
Notes: {lead.get("notes")}

Qualification context:
{qualification_context}

Personalization hook:
{personalization_hook}

Email structure:
Hi FirstName,

Personalization hook.

I run TechFi Labs, a Salesforce-focused delivery partner from India. We help teams plug Salesforce delivery gaps with experienced Salesforce developers, QA automation support, production support, managed support, and flexible staff augmentation.

In case your team ever needs additional Salesforce capacity without long hiring cycles, would it make sense to connect?

Thanks & Regards,
Harsh Veer
TechFi Labs | Salesforce Registered Partner

Rules:
- Return only valid JSON.
- Do not include markdown.
- Do not wrap JSON in ```json.
- Subject must be maximum 5 words.
- First email must follow the email structure above.
- First email should be around 80 to 110 words.
- Use simple professional English.
- Use the provided personalization hook immediately after greeting.
- Keep the tone founder-led, calm, direct, and low-pressure.
- Use "additional Salesforce capacity" instead of "support options".
- Mention "Salesforce delivery gaps" when the service angle is staffing, managed support, production support, or implementation support.
- Do not ask directly "Are you understaffed?"
- Do not mention "15 minutes" in the first email.
- Avoid generic sales phrases.
- Do not say: "I hope this finds you well", "enhance", "valuable support", "strong track record", "ensure smooth operations", "quick chat", "brief discussion", "synergy", "streamline", "impressed", "we specialize".
- Do not sound desperate.
- Do not make claims unless provided in notes.
- Keep the text "TechFi Labs" exactly as written because email_sender.py will hyperlink it in HTML email.
- Signature must be:
Thanks & Regards,
Harsh Veer
TechFi Labs | Salesforce Registered Partner

Follow-up rules:
- Follow-up 1 must include the first name.
- Follow-up 1 must mention "additional Salesforce capacity".
- Follow-up 1 must be under 40 words.
- Follow-up 1 should not say "checking if you received my previous email".
- Follow-up 1 should not say "checking in again".
- Follow-up 2 must include the first name.
- Follow-up 2 must be polite and low-pressure.
- Follow-up 2 must be under 40 words.
- Follow-up 2 should not say "last message" or "previous email".
- Follow-up 2 should keep the door open for future Salesforce delivery support.

Good follow-up 1 example:
Hi FirstName, just checking if additional Salesforce capacity is relevant for your team at this stage.

Good follow-up 2 example:
Hi FirstName, no worries if this is not a priority right now. Keeping this open in case Salesforce delivery support is useful later.

JSON format:
{{
  "qualified": "Yes or No",
  "priority": "High, Medium, or Low",
  "personalization_hook": "short personalization hook",
  "subject": "email subject",
  "email_body": "full first email body",
  "follow_up_1": "first follow-up email body",
  "follow_up_2": "second follow-up email body"
}}
""",
        expected_output="Valid JSON outreach draft.",
        agent=agent,
    )
