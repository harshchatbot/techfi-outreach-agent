from crewai import Agent


def create_qualification_agent() -> Agent:
    return Agent(
        role="B2B Lead Qualification Specialist",
        goal="Evaluate if a lead is relevant for TechFi Labs Salesforce outreach.",
        backstory=(
            "You understand IT services, Salesforce consulting, staff augmentation, "
            "managed support, and agency partnership models. You qualify leads based "
            "on role, company type, and service relevance."
        ),
        verbose=False,
        allow_delegation=False,
    )


def create_personalization_agent() -> Agent:
    return Agent(
        role="B2B Personalization Specialist",
        goal="Create a short, relevant personalization hook for a cold email.",
        backstory=(
            "You write simple, factual personalization hooks for founder-led B2B outreach. "
            "You avoid fake praise, exaggeration, and generic marketing language."
        ),
        verbose=False,
        allow_delegation=False,
    )


def create_email_writer_agent() -> Agent:
    return Agent(
        role="Founder-Led Cold Email Writer",
        goal="Write short, calm, founder-style outreach emails for TechFi Labs.",
        backstory=(
            "You write plain-text cold emails for a Salesforce-focused delivery partner. "
            "Your emails are direct, low-pressure, and sound like a real founder wrote them."
        ),
        verbose=False,
        allow_delegation=False,
    )