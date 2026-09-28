"""Business logic behind the /api/leads/enrich endpoint.

Make's webhook module can receive a form submission, but deciding whether it
looks like a genuine, well-formed lead or spam needs a few concrete rules —
that judgment call lives here instead of in a no-code router's filter.
"""

import re

_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[a-zA-Z]{2,}$")
_SPAM_KEYWORDS = {"crypto giveaway", "click here now", "guaranteed profit"}
_MIN_MESSAGE_LENGTH = 20


def enrich_lead(name: str, email: str, message: str) -> dict:
    valid_email = bool(_EMAIL_PATTERN.match(email.strip()))
    normalized_message = message.strip().lower()

    looks_like_spam = any(keyword in normalized_message for keyword in _SPAM_KEYWORDS)
    is_substantial = len(normalized_message) >= _MIN_MESSAGE_LENGTH

    quality_score = 0
    if valid_email:
        quality_score += 40
    if is_substantial:
        quality_score += 40
    if name.strip():
        quality_score += 20

    if looks_like_spam:
        route = "spam"
    elif valid_email and is_substantial:
        route = "qualified"
    else:
        route = "needs_review"

    return {
        "valid_email": valid_email,
        "quality_score": quality_score,
        "route": route,
    }
