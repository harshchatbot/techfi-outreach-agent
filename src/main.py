import os
import pandas as pd
from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

INPUT_FILE = "data/test_leads.csv"
OUTPUT_FILE = "data/outreach_output.csv"


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
5. Write one plain founder-style cold email.
6. Write follow-up 1 in under 45 words.
7. Write follow-up 2 in under 45 words.

Rules:
- Keep the first email between 55 and 80 words.
- Write like a real founder/operator, not a marketing or sales team.
- Use simple Indian founder-style English, but professional.
- Avoid all generic cold email phrases.
- Do not say: "I hope this finds you well", "enhance your offerings", "how we can assist", "valuable support", "last check-in", "quick chat", "brief discussion", "streamline", "synergy", "impressed".
- Do not overpraise the prospect.
- Do not sound desperate.
- Be direct and low-pressure.
- Mention TechFi Labs as a Salesforce-focused delivery partner.
- Mention practical services only: Salesforce developers, QA automation, production support, managed support, staff augmentation.
- End with: "Would it make sense to connect?"
- Do not use phrases like "we specialize", "strong track record", "enhance", "ensure smooth operations", "valuable support", "really benefit", "exploring a partnership", or "happy to share insights".
- Do not make claims unless provided in the lead notes.
- Prefer simple wording like "I run TechFi Labs" and "we support teams with".
- The email should feel like a calm founder note, not a marketing email.
- First email must be maximum 75 words.
- Follow-ups must be maximum 35 words each.

Return the response in this exact format:

Qualified:
Priority:
Personalization Hook:
Subject:
Email Body:
Follow Up 1:
Follow Up 2:
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You write concise, professional B2B outreach emails."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3
    )

    content = response.choices[0].message.content

    return {
        "email": lead.get("email"),
        "company_name": lead.get("company_name"),
        "title": lead.get("title"),
        "service_angle": lead.get("service_angle"),
        "ai_output": content,
        "status": "Drafted"
    }


def main():
    if not os.path.exists(INPUT_FILE):
        raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

    leads_df = pd.read_csv(INPUT_FILE)

    results = []

    for _, row in leads_df.iterrows():
        lead = row.to_dict()
        print(f"Generating outreach for: {lead.get('first_name')} {lead.get('last_name')} - {lead.get('company_name')}")
        result = generate_outreach_email(lead)
        results.append(result)

    output_df = pd.DataFrame(results)
    output_df.to_csv(OUTPUT_FILE, index=False)

    print(f"\nDone. Outreach output saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()