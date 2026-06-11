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
- Salesforce development
- Salesforce QA and automation testing
- Salesforce managed support
- Salesforce staff augmentation
- Offshore Salesforce delivery support

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
4. Write a short cold email subject.
5. Write a short human-sounding cold email body.
6. Write follow-up 1.
7. Write follow-up 2.

Rules:
- Keep email simple and human.
- Do not sound too salesy.
- Do not overpromise.
- Mention TechFi Labs naturally.
- Mention Salesforce consulting/staff augmentation only if relevant.
- Keep the first email under 120 words.

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
        temperature=0.4
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