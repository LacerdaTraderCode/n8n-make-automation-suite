# n8n + Make Automation Suite

Two no-code automation workflows — one in [n8n](https://n8n.io/), one in [Make](https://www.make.com/) — paired with a small Flask service that handles the one part neither tool is built for: state and business rules.

## What's here

- **`workflows/n8n/website-change-monitor.json`** — polls a page on a schedule, asks the Flask service whether it actually changed since last time, and notifies on Telegram only when it did.
- **`workflows/make/lead-intake-router.json`** — receives a form submission over a webhook, asks the Flask service to score and classify it, and routes it to the right Slack channel.
- **`app/`** — the Flask service both workflows call into: change detection (SQLite-backed hashing) and lead scoring (email validation plus a simple quality heuristic).
- **`docs/architecture.md`** — the reasoning behind splitting the work this way, with a diagram.

## Why pair no-code tools with a small service instead of building everything in Python

n8n and Make are genuinely fast at scheduling, HTTP calls, and branching, so there is no reason to reimplement that. What they are not a good fit for is anything that needs to remember state between runs or encode a business rule that should be tested and versioned rather than buried inside a node's configuration. This project draws that line on purpose: the workflows handle orchestration, the service handles the thinking.

## Running the service

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
flask --app app.main:create_app run
```

## Running the tests

```bash
pip install -r requirements-dev.txt
pytest
```

## Importing the workflows

Both JSON files were hand-authored to match n8n's and Make's real export shape, so they import cleanly, but credentials and connection references are always account-specific and get stripped on export. After importing, reconnect the Telegram credential in n8n and the Slack and webhook connections in Make, then point `WEBHOOK_BASE_URL` (n8n) and the HTTP module's URL (Make) at wherever this service is running.

## License

MIT — see [LICENSE](LICENSE).
