import re
from typing import Optional

from app.schemas.ride import RideSlotStatus

# Knowledge-base / Policy query patterns that must NOT trigger ride booking
KB_POLICY_PATTERNS = [
    r"\b(?:what\s+is|what's|what\s+are|how\s+does|how\s+do|how\s+much|tell\s+me\s+about|can\s+you\s+explain|explain)\b.*\b(?:policy|policies|cancellation|refund|rate|rates|pricing|cost|fare|fleet|safety|terms|guidelines|rules|volta)\b",
    r"\b(?:cancellation\s+policy|refund\s+policy|privacy\s+policy|terms\s+of\s+service)\b",
    r"\b(?:how\s+(?:much|do\s+i|can\s+i)\s+(?:cancel|cost|charge))\b",
    r"\b(?:what\s+(?:vehicles|cars|cabs)\s+(?:do\s+you\s+have|are\s+available))\b",
    r"\bhow\s+much\b.*\b(?:cost|charge|fare|rates?|pricing)\b",
]

# Cancellation keywords indicating user wants to abort an active ride request
CANCELLATION_PATTERNS = [
    r"^(?:cancel|stop|abort|never\s*mind|forget\s*it|cancel\s+it|cancel\s+request)$",
    r"\b(?:cancel\s+(?:the|my)?\s*(?:ride|cab|trip|booking|request))\b",
    r"\b(?:never\s*mind|stop\s+(?:the)?\s*(?:ride|booking))\b",
]

# Conversational expressions with "go", "take", "home" that are NOT ride requests
NON_RIDE_FALSE_POSITIVES = [
    r"^(?:i\s+(?:just\s+)?want\s+to\s+go\s+home|going\s+home)$",
    r"^(?:take\s+care|take\s+your\s+time|take\s+it\s+easy)$",
    r"^(?:home\s+is\s+where\s+the\s+heart\s+is)$",
    r"^(?:let's\s+go|we\s+can\s+go|go\s+ahead|go\s+away)$",
    r"^(?:take\s+a\s+look|take\s+note)$",
]

# Explicit ride-booking intent patterns
RIDE_INTENT_PATTERNS = [
    r"\b(?:book|order|get|arrange|reserve|hail|call|find|need)\s+(?:me\s+)?(?:a\s+|an\s+)?(?:cab|ride|taxi|car|sedan|suv|auto|ev|electric\s+cab)\b",
    r"\b(?:i\s+need|i\s+want|can\s+you\s+(?:get|book|call|arrange)|take\s+me)\s+(?:to|from|a\s+cab|a\s+ride|a\s+car)\b",
    r"\b(?:take\s+me\s+to)\b",
    r"\b(?:take\s+me\s+from)\b",
    r"\b(?:cab|ride|taxi)\s+(?:from\s+.+\s+to\s+.+|to\s+.+\s+from\s+.+)\b",
    r"\b(?:from\s+.+\s+to\s+.+)\b",
    r"\b(?:electric\s+cab|volta\s+cab|cab\s+service)\b",
    r"\b(?:pickup\s+at\s+.+\s+going\s+to\s+.+)\b",
    r"\b(?:ride\s+home|cab\s+home)\b",
]


def is_knowledge_base_query(user_input: str) -> bool:
    """Returns True if the user query is asking about company policies, FAQs, or information."""
    text = user_input.strip().lower()
    for pattern in KB_POLICY_PATTERNS:
        if re.search(pattern, text):
            return True
    return False


def is_cancellation_intent(user_input: str) -> bool:
    """Returns True if the message expresses intent to cancel an active ride request."""
    text = user_input.strip().lower()
    # If it's a general question about the cancellation policy, it's KB, not cancellation!
    if is_knowledge_base_query(user_input):
        return False
    for pattern in CANCELLATION_PATTERNS:
        if re.search(pattern, text):
            return True
    return False


def is_ride_intent(user_input: str, has_pending_request: bool = False) -> bool:
    """Analyzes user input to determine if a ride booking or route recommendation is requested.

    Rejects false positives ('I want to go home', 'Take care') and KB policy queries.
    """
    text = user_input.strip().lower()

    # 1. Knowledge Base Queries take precedence over ride intent
    if is_knowledge_base_query(text):
        return False

    # 2. Cancellation intent is handled as cancellation, not new ride creation
    if is_cancellation_intent(text):
        return False

    # 3. Explicit false positive guard
    for fp in NON_RIDE_FALSE_POSITIVES:
        if re.search(fp, text):
            return False

    # 4. If there is already an active multi-turn request awaiting slots,
    # then location phrases or simple answers are valid ride continuations.
    if has_pending_request:
        # A single word or short phrase like "Home", "Work", "Airport", "from MG Road"
        if len(text.split()) <= 6:
            return True

    # 5. Check explicit ride booking patterns
    for pattern in RIDE_INTENT_PATTERNS:
        if re.search(pattern, text):
            return True

    return False


def is_recommendation_requested(user_input: str) -> bool:
    """Backwards-compatible interface for intent classification."""
    return is_ride_intent(user_input, has_pending_request=False)


def _clean_location_string(val: str) -> str:
    """Cleans extracted location strings from conversational noise."""
    cleaned = val.strip()
    # Strip common trailing noise
    cleaned = re.sub(
        r"\s+(?:please|now|right\s+now|today|asap|instead|immediately|for\s+me)\b.*$",
        "",
        cleaned,
        flags=re.IGNORECASE,
    ).strip()
    # Strip leading prefixes
    cleaned = re.sub(
        r"^(?:the\s+|my\s+|an\s+|a\s+|at\s+|to\s+|from\s+)",
        "",
        cleaned,
        flags=re.IGNORECASE,
    ).strip()
    # Strip trailing punctuation
    cleaned = cleaned.strip(" .,!?;:")
    return cleaned


def extract_ride_slots(
    user_input: str,
    pending_status: Optional[RideSlotStatus] = None,
) -> tuple[Optional[str], Optional[str], bool, bool]:
    """Deterministically extracts pickup and destination strings from user input.

    Returns:
        (pickup_raw, destination_raw, is_cancelled, is_override)
    """
    text = user_input.strip()

    # 1. Cancellation check
    if is_cancellation_intent(text):
        return None, None, True, False

    # 2. Check for explicit overrides / corrections
    # e.g., "Actually, pick me up at Work instead", "Change pickup to Work"
    pickup_override_m = re.search(
        r"(?:actually,?\s*)?(?:change\s+(?:my\s+)?pickup\s+to|update\s+(?:my\s+)?pickup\s+to|make\s+(?:my\s+)?pickup|pick\s+me\s+up\s+at)\s+([^,]+?)(?:\s+instead)?$",
        text,
        re.IGNORECASE,
    )
    if pickup_override_m:
        return _clean_location_string(pickup_override_m.group(1)), None, False, True

    dest_override_m = re.search(
        r"(?:actually,?\s*)?(?:change\s+(?:my\s+)?(?:destination|dropoff)\s+to|update\s+(?:my\s+)?(?:destination|dropoff)\s+to|make\s+(?:my\s+)?(?:destination|dropoff)|drop\s+me\s+off\s+at|go\s+to)\s+([^,]+?)(?:\s+instead)?$",
        text,
        re.IGNORECASE,
    )
    if dest_override_m:
        return None, _clean_location_string(dest_override_m.group(1)), False, True

    # 3. Check for "from X to Y" (most common full ride request)
    from_to_m = re.search(
        r"\bfrom\s+(.+?)\s+to\s+(.+?)(?:\s+(?:right\s+now|now|today|please|asap))?$",
        text,
        re.IGNORECASE,
    )
    if from_to_m:
        return (
            _clean_location_string(from_to_m.group(1)),
            _clean_location_string(from_to_m.group(2)),
            False,
            False,
        )

    # 4. Check for "to Y from X"
    to_from_m = re.search(
        r"\bto\s+(.+?)\s+from\s+(.+?)(?:\s+(?:right\s+now|now|today|please|asap))?$",
        text,
        re.IGNORECASE,
    )
    if to_from_m:
        return (
            _clean_location_string(to_from_m.group(2)),
            _clean_location_string(to_from_m.group(1)),
            False,
            False,
        )

    # 5. Check for "pickup at X going to Y" or "pickup at X to Y"
    pickup_to_m = re.search(
        r"\bpickup\s+(?:at|from)?\s*(.+?)\s+(?:going\s+to|to|dropoff\s+(?:at|to)?)\s+(.+?)(?:\s+(?:right\s+now|now|today|please|asap))?$",
        text,
        re.IGNORECASE,
    )
    if pickup_to_m:
        return (
            _clean_location_string(pickup_to_m.group(1)),
            _clean_location_string(pickup_to_m.group(2)),
            False,
            False,
        )

    # 6. Check for direct booking command to destination: "Book (a ride|a cab|an electric cab) to Y"
    # When a direct booking command is issued with a destination and no prior pending slot,
    # pickup defaults to Current Location.
    direct_book_to_m = re.search(
        r"\bbook\s+(?:me\s+)?(?:a\s+|an\s+)?(?:electric\s+)?(?:cab|ride|car|taxi)\s+to\s+(.+?)(?:\s+(?:right\s+now|now|today|please|asap))?$",
        text,
        re.IGNORECASE,
    )
    if direct_book_to_m and pending_status is None:
        return (
            "Current Location",
            _clean_location_string(direct_book_to_m.group(1)),
            False,
            False,
        )

    # 7. Check for "take me to Y" / "take me home" / "car to Y" / "ride to Y" (missing pickup -> needs_pickup)
    take_to_m = re.search(
        r"\b(?:take\s+me\s+to|going\s+to|heading\s+to|get\s+me\s+(?:a\s+)?car\s+to|car\s+to|cab\s+to|ride\s+to|i\s+need\s+a\s+ride\s+to)\s+(.+?)(?:\s+(?:right\s+now|now|today|please|asap))?$",
        text,
        re.IGNORECASE,
    )
    if take_to_m:
        return None, _clean_location_string(take_to_m.group(1)), False, False

    # Check for "ride home" / "cab home"
    if re.search(r"\b(?:ride|cab|taxi)\s+home\b", text, re.IGNORECASE):
        return None, "Home", False, False

    # 7. Check for "pickup at X" / "from X"
    pickup_only_m = re.search(
        r"\b(?:pickup\s+(?:at|from)|from)\s+(.+?)(?:\s+(?:right\s+now|now|today|please|asap))?$",
        text,
        re.IGNORECASE,
    )
    if pickup_only_m:
        return _clean_location_string(pickup_only_m.group(1)), None, False, False

    # 8. If in multi-turn state awaiting a specific slot, use the whole input as that slot
    cleaned_input = _clean_location_string(text)
    if pending_status == RideSlotStatus.NEEDS_PICKUP:
        return cleaned_input, None, False, False
    elif pending_status == RideSlotStatus.NEEDS_DESTINATION:
        return None, cleaned_input, False, False

    return None, None, False, False
