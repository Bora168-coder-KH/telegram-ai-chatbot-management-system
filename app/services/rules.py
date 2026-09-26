"""Keyword / rule-based responses (no AI needed).

Each rule is (keywords, {language: response}). If any keyword appears in the
user's message, the response is sent. Add your own rules here, or move them to
the database later so admins can edit them from the dashboard.
"""

RULES: list[tuple[tuple[str, ...], dict[str, str]]] = [
    (
        ("hello", "hi", "សួស្តី", "សួស្ដី"),
        {"en": "Hello! How can I help you today?", "km": "សួស្តី! តើខ្ញុំអាចជួយអ្វីបានខ្លះ?"},
    ),
    (
        ("thank", "thanks", "អរគុណ"),
        {"en": "You are welcome!", "km": "មិនអីទេ!"},
    ),
]


def match_rule(text: str, language: str) -> str | None:
    lowered = text.lower()
    words = set(lowered.split())
    for keywords, responses in RULES:
        for keyword in keywords:
            # short latin keywords must match a whole word ("hi" must not match "this")
            hit = keyword in words if keyword.isascii() else keyword in lowered
            if hit:
                return responses.get(language) or responses["en"]
    return None
