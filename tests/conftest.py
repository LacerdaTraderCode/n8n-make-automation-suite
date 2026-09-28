"""Shared pytest fixtures for the Flask test suite."""

import tempfile

import pytest

from app.main import create_app


@pytest.fixture
def app():
    with tempfile.NamedTemporaryFile(suffix=".sqlite3") as database_file:
        flask_app = create_app(database_path=database_file.name)
        flask_app.config["WEBHOOK_API_KEY"] = "test-key"
        yield flask_app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_headers():
    return {"X-API-Key": "test-key"}
