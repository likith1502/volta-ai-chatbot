import re

RECOMMENDATION_KEYWORDS = [
    r"\bbook\b",
    r"\bride\b",
    r"\btaxi\b",
    r"\bcab\b",
    r"\bdrive\b",
    r"\bpickup\b",
    r"\bdropoff\b",
    r"\bdestination\b",
    r"\broute\b",
    r"\btransport\b",
    r"\bairport\b",
]


def is_recommendation_requested(user_input: str) -> bool:
    """Analyzes user input to determine if a ride or route recommendation is requested."""
    text = user_input.lower()
    for kw in RECOMMENDATION_KEYWORDS:
        if re.search(kw, text):
            return True
    return False
