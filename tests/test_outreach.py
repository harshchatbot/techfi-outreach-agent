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
