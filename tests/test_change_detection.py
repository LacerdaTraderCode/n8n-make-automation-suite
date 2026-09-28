"""Tests for the /api/changes/check endpoint and its underlying logic."""

from app.change_detection import check_for_change
from app.storage import get_connection, initialize_schema


def test_first_check_for_a_source_is_reported_as_changed(tmp_path):
    connection = get_connection(str(tmp_path / "test.sqlite3"))
    initialize_schema(connection)

    result = check_for_change(connection, "source-a", "hello world")

    assert result["changed"] is True


def test_identical_content_on_the_next_check_is_not_a_change(tmp_path):
    connection = get_connection(str(tmp_path / "test.sqlite3"))
    initialize_schema(connection)
    check_for_change(connection, "source-a", "hello world")

    result = check_for_change(connection, "source-a", "hello world")

    assert result["changed"] is False


def test_different_content_is_reported_as_changed(tmp_path):
    connection = get_connection(str(tmp_path / "test.sqlite3"))
    initialize_schema(connection)
    check_for_change(connection, "source-a", "hello world")

    result = check_for_change(connection, "source-a", "hello there world")

    assert result["changed"] is True


def test_endpoint_rejects_a_request_without_an_api_key(client):
    response = client.post("/api/changes/check", json={"source_id": "a", "content": "x"})

    assert response.status_code == 401


def test_endpoint_reports_a_change_for_a_new_source(client, auth_headers):
    response = client.post(
        "/api/changes/check",
        json={"source_id": "pricing-page", "content": "Plan A: $10/mo"},
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.get_json()["changed"] is True


def test_endpoint_reports_no_change_for_repeated_content(client, auth_headers):
    payload = {"source_id": "pricing-page", "content": "Plan A: $10/mo"}
    client.post("/api/changes/check", json=payload, headers=auth_headers)

    response = client.post("/api/changes/check", json=payload, headers=auth_headers)

    assert response.get_json()["changed"] is False
