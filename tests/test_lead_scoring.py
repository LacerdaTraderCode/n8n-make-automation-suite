"""Tests for the /api/leads/enrich endpoint and its underlying logic."""

from app.lead_scoring import enrich_lead


def test_a_well_formed_lead_is_qualified():
    result = enrich_lead(
        name="Ana Silva",
        email="ana@example.com",
        message="Hi, I would like a quote for your consulting services.",
    )

    assert result["valid_email"] is True
    assert result["route"] == "qualified"
    assert result["quality_score"] == 100


def test_an_invalid_email_is_flagged():
    result = enrich_lead(
        name="Ana", email="not-an-email", message="A reasonably long message here."
    )

    assert result["valid_email"] is False
    assert result["route"] == "needs_review"


def test_a_short_message_needs_review():
    result = enrich_lead(name="Ana", email="ana@example.com", message="Hi")

    assert result["route"] == "needs_review"


def test_spam_keywords_are_flagged_regardless_of_other_signals():
    result = enrich_lead(
        name="Bot",
        email="bot@example.com",
        message="This is a guaranteed profit crypto giveaway, click here now.",
    )

    assert result["route"] == "spam"


def test_endpoint_returns_enrichment_for_a_valid_payload(client, auth_headers):
    response = client.post(
        "/api/leads/enrich",
        json={
            "name": "Ana Silva",
            "email": "ana@example.com",
            "message": "Hi, I would like a quote for your consulting services.",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.get_json()["route"] == "qualified"


def test_endpoint_rejects_a_request_without_an_api_key(client):
    response = client.post(
        "/api/leads/enrich",
        json={"name": "A", "email": "a@example.com", "message": "hello there"},
    )

    assert response.status_code == 401
