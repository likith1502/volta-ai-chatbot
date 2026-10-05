"""Helpers that make ride replies sound natural and keep prices consistent.

- format_inr / place_name: "₹520", "Jubilee Hills" instead of "INR 520.00",
  "jubilee hills".
- is_affirmative_reply / is_negative_reply: understand everyday replies
  ("yes", "ok", "haan", "avunu", "book it", "no", "wait") once a vehicle has
  been chosen. Voice input often adds punctuation ("Yes."), so text is
  normalised first.
- extract_quoted_fares: read the fare Gemini actually showed for each vehicle,
  so the booking uses the same price the customer saw.
"""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation
from typing import Any, Optional


def format_inr(amount: Any) -> str:
    """₹ with Indian digit grouping, no paise for whole rupees: ₹1,23,456."""
    try:
        value = Decimal(str(amount))
    except (InvalidOperation, ValueError, TypeError):
        return f"₹{amount}"
    n = int(value.quantize(Decimal("1")))
    s = str(abs(n))
    if len(s) > 3:
        head, tail = s[:-3], s[-3:]
        groups = []
        while len(head) > 2:
            groups.insert(0, head[-2:])
            head = head[:-2]
        if head:
            groups.insert(0, head)
        s = ",".join(groups) + "," + tail
    return ("-" if n < 0 else "") + "₹" + s


def place_name(label: Optional[str], default: str) -> str:
    """Tidy a place label for display ('jubilee hills' -> 'Jubilee Hills')."""
    if not label:
        return default
    label = label.strip()
    # Only re-case labels typed all-lowercase; keep things like "HITEC City".
    return label.title() if label == label.lower() else label


def vehicle_name(name: Optional[str]) -> str:
    name = (name or "Ride").strip()
    return name if name.lower().startswith("volta") else f"Volta {name}"


def _normalise(text: str) -> str:
    text = text.lower().replace("’", "'")
    text = re.sub(r"[^\w\s']", " ", text)  # drop punctuation ("Yes." -> "yes")
    return re.sub(r"\s+", " ", text).strip()


# Whole-message replies that mean "yes, go ahead" (English, Hinglish, Telugu).
_AFFIRMATIVE_PHRASES = {
    "yes", "yeah", "yea", "yep", "yup", "ya", "yes please", "yes sure",
    "sure", "sure thing", "ok", "okay", "okk", "ok ok", "k", "fine", "done",
    "alright", "all right", "correct", "right", "perfect", "great",
    "go ahead", "go on", "proceed", "confirm", "confirmed", "please confirm",
    "book it", "book", "book now", "book that", "book this", "book this one",
    "book that one", "please book", "please book it", "do it", "lets go",
    "let's go", "sounds good", "that's fine", "thats fine", "that works",
    # Hinglish
    "haan", "haa", "ha", "han", "haan ji", "ji", "ji haan", "theek hai",
    "thik hai", "theek", "thik", "chalo", "chalega", "kar do", "book kar do",
    "kardo", "haan book karo", "book karo",
    # Telugu (romanised)
    "avunu", "sare", "sari", "ok cheyyi", "book cheyyi", "cheyyi",
    "book cheyandi", "cheyandi", "alage",
}

# Words that, if present anywhere, mean the reply is NOT a confirmation.
_NEGATIVE_WORDS = {
    "no", "nope", "nah", "not", "don't", "dont", "wait", "stop", "cancel",
    "later", "hold", "change", "different", "another", "instead",
    "nahi", "nahin", "mat", "ruko", "vaddu", "kaadu", "aagu",
}

_NEGATIVE_PHRASES = {
    "no", "nope", "nah", "no thanks", "no thank you", "not now", "wait",
    "hold on", "don't book", "dont book", "do not book", "not this one",
    "nahi", "nahin", "mat karo", "vaddu", "kaadu", "aagu",
}


def is_affirmative_reply(text: str) -> bool:
    """True for everyday 'yes' replies, including 'yes, book it please'."""
    t = _normalise(text)
    if not t:
        return False
    words = set(t.split())
    if words & _NEGATIVE_WORDS:
        return False
    if t in _AFFIRMATIVE_PHRASES:
        return True
    # Short replies that start with a yes-word: "yes book it", "ok go ahead",
    # "haan kar do please".
    first = t.split()[0]
    return len(t.split()) <= 6 and first in {
        "yes", "yeah", "yep", "yup", "ok", "okay", "sure", "haan", "ha",
        "avunu", "sare", "confirm", "book", "please", "go",
    }


def is_negative_reply(text: str) -> bool:
    t = _normalise(text)
    if not t:
        return False
    if t in _NEGATIVE_PHRASES:
        return True
    return len(t.split()) <= 5 and t.split()[0] in {"no", "nope", "nah", "nahi", "vaddu", "wait"}


# "₹170", "~₹170", "Rs. 170", "INR 170", "₹1,200"
_PRICE = re.compile(r"(?:₹|rs\.?|inr)\s*~?\s*([0-9][0-9,]*(?:\.[0-9]{1,2})?)", re.IGNORECASE)


def extract_quoted_fares(content: str, options: list[dict[str, Any]]) -> dict[str, str]:
    """Return {tier: fare} for each vehicle whose price Gemini showed.

    Looks at the text after each vehicle name, up to the next vehicle name,
    and takes the first rupee amount there. Vehicles without a clear price
    are left out (their stored quote is kept).
    """
    if not content or not options:
        return {}
    lower = content.lower()
    found: list[tuple[int, str]] = []
    for opt in options:
        tier = str(opt.get("tier", "")).lower()
        names = {tier, str(opt.get("display_name", "")).lower()} - {""}
        best = None
        for name in names:
            m = re.search(rf"\b(?:volta\s+)?{re.escape(name)}\b", lower)
            if m and (best is None or m.start() < best):
                best = m.start()
        if best is not None:
            found.append((best, tier))
    found.sort()
    fares: dict[str, str] = {}
    for i, (start, tier) in enumerate(found):
        end = found[i + 1][0] if i + 1 < len(found) else len(content)
        m = _PRICE.search(content[start:end])
        if m:
            try:
                value = Decimal(m.group(1).replace(",", ""))
            except InvalidOperation:
                continue
            if Decimal("20") <= value <= Decimal("20000"):  # sanity bounds
                fares[tier] = f"{value.quantize(Decimal('0.01'))}"
    return fares
