"""Flask application factory and route registration."""

import os
import sqlite3

from flask import Flask, g, jsonify, request

from app.change_detection import check_for_change
from app.lead_scoring import enrich_lead
from app.security import require_api_key
from app.storage import get_connection, initialize_schema


def create_app(database_path: str | None = None) -> Flask:
    app = Flask(__name__)
    app.config["WEBHOOK_API_KEY"] = os.environ.get("WEBHOOK_API_KEY", "change-me")
    app.config["DATABASE_PATH"] = database_path or os.environ.get(
        "DATABASE_PATH", "automation_suite.sqlite3"
    )

    connection = get_connection(app.config["DATABASE_PATH"])
    initialize_schema(connection)
    connection.close()

    def get_db() -> sqlite3.Connection:
        if "db_connection" not in g:
            g.db_connection = get_connection(app.config["DATABASE_PATH"])
        return g.db_connection

    @app.teardown_appcontext
    def close_connection(exception=None):
        connection = g.pop("db_connection", None)
        if connection is not None:
            connection.close()

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    @app.post("/api/changes/check")
    @require_api_key
    def changes_check():
        payload = request.get_json(force=True)
        source_id = payload.get("source_id", "")
        content = payload.get("content", "")
        if not source_id or not content:
            return jsonify({"detail": "source_id and content are required."}), 400
        result = check_for_change(get_db(), source_id, content)
        return jsonify(result)

    @app.post("/api/leads/enrich")
    @require_api_key
    def leads_enrich():
        payload = request.get_json(force=True)
        name = payload.get("name", "")
        email = payload.get("email", "")
        message = payload.get("message", "")
        if not email or not message:
            return jsonify({"detail": "email and message are required."}), 400
        result = enrich_lead(name, email, message)
        return jsonify(result)

    return app
