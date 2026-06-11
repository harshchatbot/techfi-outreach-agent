import os
from pathlib import Path

os.environ.setdefault(
    "CREWAI_STORAGE_DIR",
    str(Path(__file__).resolve().parents[1] / ".crewai_storage"),
)

from crewai import Crew, Process

from agents import (
    create_personalization_agent,
    create_qualification_agent,
)
from tasks import (
    create_personalization_task,
    create_qualification_task,
)


def _get_raw_output(result) -> str:
    """
    CrewAI result object can vary slightly by version.
    This keeps our code safer across versions.
    """
    if hasattr(result, "raw"):
        return result.raw

    return str(result)


def _extract_value_from_text(text: str, key: str, default: str = "") -> str:
    """
    Extracts simple values from text like:
    Qualified: Yes
    Priority: High
    Reason: ...
    """
    if not text:
        return default

    for line in text.splitlines():
        clean_line = line.strip()
        if clean_line.lower().startswith(key.lower() + ":"):
            return clean_line.split(":", 1)[1].strip()

    return default


def _clean_personalization_hook(hook: str | None, company_name: str | None) -> str:
    company_name = company_name or "your company"

    if not hook:
        return f"Noticed {company_name} is active in technology services."

    hook = hook.strip()

    if hook.startswith("I noticed"):
        hook = hook.replace("I noticed", "Noticed", 1)

    if hook.startswith("I see"):
        hook = hook.replace("I see", "Noticed", 1)

    if hook.startswith("I was impressed"):
        hook = f"Noticed {company_name} is active in technology services."

    if "innovative tech solutions" in hook.lower():
        hook = f"Noticed {company_name} is active in technology services."

    return hook


def _build_subject(service_angle: str | None) -> str:
    service_angle = (service_angle or "").lower()

    if "managed" in service_angle:
        return "Salesforce Managed Support"

    if "qa" in service_angle or "automation" in service_angle:
        return "Salesforce QA Support"

    if "staff" in service_angle or "augmentation" in service_angle:
        return "Salesforce Delivery Support"

    return "Salesforce Support"


def _build_email_body(first_name: str | None, personalization_hook: str) -> str:
    first_name = first_name or "there"

    return f"""Hi {first_name},

{personalization_hook}

I run TechFi Labs, a Salesforce-focused delivery partner from India. We help teams plug Salesforce delivery gaps with experienced Salesforce developers, QA automation support, production support, managed support, and flexible staff augmentation.

In case your team ever needs additional Salesforce capacity without long hiring cycles, would it make sense to connect?

Thanks & Regards,
Harsh Veer
TechFi Labs | Salesforce Registered Partner"""


def _build_follow_up_1(first_name: str | None) -> str:
    first_name = first_name or "there"

    return (
        f"Hi {first_name}, just checking if additional Salesforce capacity "
        f"is relevant for your team at this stage."
    )


def _build_follow_up_2(first_name: str | None) -> str:
    first_name = first_name or "there"

    return (
        f"Hi {first_name}, no worries if this is not a priority right now. "
        f"Keeping this open in case Salesforce delivery support is useful later."
    )


def generate_outreach_email(lead: dict) -> dict:
    print("DEBUG: using enforced outreach template from src/outreach.py")

    qualification_agent = create_qualification_agent()
    personalization_agent = create_personalization_agent()

    qualification_task = create_qualification_task(
        agent=qualification_agent,
        lead=lead,
    )

    qualification_crew = Crew(
        agents=[qualification_agent],
        tasks=[qualification_task],
        process=Process.sequential,
        verbose=False,
    )

    qualification_result = qualification_crew.kickoff()
    qualification_context = _get_raw_output(qualification_result)

    personalization_task = create_personalization_task(
        agent=personalization_agent,
        lead=lead,
        qualification_context=qualification_context,
    )

    personalization_crew = Crew(
        agents=[personalization_agent],
        tasks=[personalization_task],
        process=Process.sequential,
        verbose=False,
    )

    personalization_result = personalization_crew.kickoff()
    personalization_hook_from_agent = _get_raw_output(personalization_result)

    first_name = lead.get("first_name")
    company_name = lead.get("company_name")
    service_angle = lead.get("service_angle")

    qualified = _extract_value_from_text(
        qualification_context,
        "Qualified",
        default="Yes",
    )

    priority = _extract_value_from_text(
        qualification_context,
        "Priority",
        default="Medium",
    )

    personalization_hook = _clean_personalization_hook(
        personalization_hook_from_agent,
        company_name,
    )

    subject = _build_subject(service_angle)
    email_body = _build_email_body(first_name, personalization_hook)
    follow_up_1 = _build_follow_up_1(first_name)
    follow_up_2 = _build_follow_up_2(first_name)

    return {
        "email": lead.get("email"),
        "company_name": lead.get("company_name"),
        "title": lead.get("title"),
        "service_angle": service_angle,
        "qualified": qualified,
        "priority": priority,
        "personalization_hook": personalization_hook,
        "subject": subject,
        "email_body": email_body,
        "follow_up_1": follow_up_1,
        "follow_up_2": follow_up_2,
        "status": "Drafted",
    }
