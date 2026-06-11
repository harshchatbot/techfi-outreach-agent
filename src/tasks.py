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

Lead:
First Name: {lead.get("first_name")}
Last Name: {lead.get("last_name")}
Email: {lead.get("email")}
Company: {lead.get("company_name")}
Title: {lead.get("title")}
Website: {lead.get("website")}
LinkedIn: {lead.get("linkedin_url")}
Service Angle: {lead.get("service_angle")}
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
Notes: {lead.get("notes")}

Qualification context:
{qualification_context}

Rules:
- Always start the hook with "Noticed".
- Mention the company name if available.
- Keep it factual.
- Maximum 15 words.
- Do not overpraise.
- Do not use "I see".
- Do not use "I was impressed".
- Do not invent facts.

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

I run TechFi Labs, a Salesforce-focused delivery partner from India. We support teams with Salesforce developers, QA automation, production support, managed support, and flexible staff augmentation.

Would it make sense to connect?

Best,
Harsh

Rules:
- Return only valid JSON.
- Do not include markdown.
- Do not wrap JSON in ```json.
- Subject must be maximum 5 words.
- First email must be 55 to 80 words.
- Follow-ups must be under 35 words each.
- Use simple professional English.
- Avoid generic sales phrases.
- Do not say: "I hope this finds you well", "enhance", "valuable support", "strong track record", "ensure smooth operations", "quick chat", "brief discussion", "synergy", "streamline", "impressed", "we specialize".
- Do not sound desperate.
- Do not make claims unless provided in notes.

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