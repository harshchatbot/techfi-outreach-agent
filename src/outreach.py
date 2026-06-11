import json
from crewai import Crew, Process

from agents import (
    create_email_writer_agent,
    create_personalization_agent,
    create_qualification_agent,
)
from tasks import (
    create_email_writer_task,
    create_personalization_task,
    create_qualification_task,
)


def _parse_json_safely(content: str) -> dict:
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {
            "qualified": "Parse Error",
            "priority": "",
            "personalization_hook": "",
            "subject": "",
            "email_body": content,
            "follow_up_1": "",
            "follow_up_2": "",
        }


def _get_raw_output(result) -> str:
    """
    CrewAI result object can vary slightly by version.
    This keeps our code safer across versions.
    """
    if hasattr(result, "raw"):
        return result.raw

    return str(result)


def generate_outreach_email(lead: dict) -> dict:
    qualification_agent = create_qualification_agent()
    personalization_agent = create_personalization_agent()
    email_writer_agent = create_email_writer_agent()

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
    personalization_hook = _get_raw_output(personalization_result)

    email_writer_task = create_email_writer_task(
        agent=email_writer_agent,
        lead=lead,
        qualification_context=qualification_context,
        personalization_hook=personalization_hook,
    )

    email_crew = Crew(
        agents=[email_writer_agent],
        tasks=[email_writer_task],
        process=Process.sequential,
        verbose=False,
    )

    email_result = email_crew.kickoff()
    content = _get_raw_output(email_result).strip()
    parsed = _parse_json_safely(content)

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
        "status": "Drafted",
    }