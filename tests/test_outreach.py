import outreach


def test_deterministic_email_template_contains_required_text():
    email_body = outreach._build_email_body(
        first_name="Harsh Veer",
        personalization_hook="Noticed The Technology Fiction focuses on Salesforce staff augmentation.",
    )

    assert "plug Salesforce delivery gaps" in email_body
    assert "additional Salesforce capacity without long hiring cycles" in email_body
    assert "Thanks & Regards" in email_body
    assert "Harsh Veer" in email_body
    assert "TechFi Labs | Salesforce Registered Partner" in email_body
    assert "P.S. If this is not relevant" in email_body
    assert "Best, Harsh" not in email_body
    assert "We support teams with Salesforce developers" not in email_body
    assert "Just following up on my previous email" not in email_body


def test_clean_personalization_hook_replaces_weak_phrase_with_pain_signal_fallback():
    hook = outreach._clean_personalization_hook(
        "Noticed Acme Labs focuses on innovative tech solutions.",
        company_name="Acme Labs",
        pain_signal="Posted a Salesforce QA automation role",
        lead_type="Salesforce Consulting Agency",
        service_angle="Salesforce QA automation",
    )

    assert hook == "Noticed Acme Labs has a relevant Salesforce delivery signal."


def test_clean_personalization_hook_uses_lead_type_when_pain_signal_missing():
    hook = outreach._clean_personalization_hook(
        "Noticed Acme Labs is a leading company.",
        company_name="Acme Labs",
        pain_signal="",
        lead_type="Salesforce Consulting Agency",
        service_angle="Salesforce QA automation",
    )

    assert hook == "Noticed Acme Labs works in Salesforce Consulting Agency."


def test_clean_personalization_hook_uses_service_angle_when_higher_priority_fields_missing():
    hook = outreach._clean_personalization_hook(
        "Noticed Acme Labs has amazing work.",
        company_name="Acme Labs",
        pain_signal="",
        lead_type="",
        service_angle="Salesforce QA automation",
    )

    assert hook == "Noticed Acme Labs may be relevant for Salesforce QA automation."
