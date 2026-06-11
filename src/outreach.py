import json
from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)


def generate_outreach_email(lead: dict) -> dict:
    prompt = f"""
You are an expert B2B cold email writer for a Salesforce consulting and staff augmentation company.

Company sending the email:
TechFi Labs

Founder:
Harsh Veer Nirwan

Services:
- Salesforce developers
- Salesforce QA automation
- Salesforce production support
- Salesforce managed support
- Flexible Salesforce staff augmentation
- Offshore Salesforce delivery support from India

Lead details:
First Name: {lead.get("first_name")}
Last Name: {lead.get("last_name")}
Email: {lead.get("email")}
Company: {lead.get("company_name")}
Title: {lead.get("title")}
Website: {lead.get("website")}
LinkedIn: {lead.get("linkedin_url")}
Service Angle: {lead.get("service_angle")}
Notes: {lead.get("notes")}

Task:
1. Decide if this lead is qualified.
2. Give priority: High, Medium, or Low.
3. Create one short personalization hook.
4. Write one simple cold email subject.
5. Write one plain founder-style cold email using the exact email structure below.
6. Write follow-up 1 in under 35 words.
7. Write follow-up 2 in under 35 words.

Email structure:
Hi FirstName,

Personalization hook.

I run TechFi Labs, a Salesforce-focused delivery partner from India. We support teams with Salesforce developers, QA automation, production support, managed support, and flexible staff augmentation.

Would it make sense to connect?

Best,
Harsh

Rules:
- Keep the first email between 55 and 80 words.
- Write like a real founder/operator, not a marketing or sales team.
- Use simple professional English.
- Put the personalization hook immediately after the greeting.
- Use line breaks exactly like a normal email.
- Always end the first email with:
Best,
Harsh
- Do not repeat the same idea twice.
- Subject should be simple, maximum 5 words.
- Avoid all generic cold email phrases.
- Do not say: "I hope this finds you well", "enhance your offerings", "how we can assist", "valuable support", "last check-in", "quick chat", "brief discussion", "streamline", "synergy", "impressed".
- Do not say: "we specialize", "strong track record", "enhance", "ensure smooth operations", "really benefit", "exploring a partnership", or "happy to share insights".
- Do not overpraise the prospect.
- Do not sound desperate.
- Do not make claims unless provided in the lead notes.
- Be direct and low-pressure.
- Prefer simple wording like "I run TechFi Labs" and "we support teams with".
- Mention TechFi Labs as a Salesforce-focused delivery partner from India.
- Mention practical services only: Salesforce developers, QA automation, production support, managed support, staff augmentation.
- End the first email with: "Would it make sense to connect?"

Return only valid JSON.
Do not include markdown.
Do not include explanation.
Do not wrap the JSON inside ```json.

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
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You write concise, professional B2B outreach emails and return only valid JSON."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3
    )

    content = response.choices[0].message.content.strip()

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        parsed = {
            "qualified": "Parse Error",
            "priority": "",
            "personalization_hook": "",
            "subject": "",
            "email_body": content,
            "follow_up_1": "",
            "follow_up_2": ""
        }

    return {
        "email": lead.get("email"),
        "company_name": lead.get("company_name"),
        "title": lead.get("title"),
        "service_angle": lead.get("service_angle"),
        "qualified": parsed.get("qualified"),
        "priority": parsed.get("priority"),
        "personalization_hook": parsed.get("personalization_hook"),
        "subject": parsed.get("subject"),
        "email_body": parsed.get("email_body"),
        "follow_up_1": parsed.get("follow_up_1"),
        "follow_up_2": parsed.get("follow_up_2"),
        "status": "Drafted"
    }