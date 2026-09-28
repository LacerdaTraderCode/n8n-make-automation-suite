"""A minimal shared-secret check for the webhook endpoints.

Both n8n and Make can send a static header on every request, so a shared
secret is enough here — this service is meant to sit behind the automation
platforms, not be exposed as a public API.
"""

from functools import wraps

from flask import current_app, jsonify, request


def require_api_key(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        expected_key = current_app.config["WEBHOOK_API_KEY"]
        provided_key = request.headers.get("X-API-Key")
        if provided_key != expected_key:
            return jsonify({"detail": "Invalid or missing API key."}), 401
        return view(*args, **kwargs)

    return wrapped
