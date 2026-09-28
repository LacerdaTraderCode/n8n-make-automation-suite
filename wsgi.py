"""WSGI entrypoint for running the app with a production server such as gunicorn."""

from app.main import create_app

app = create_app()
