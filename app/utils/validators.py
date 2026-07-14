"""
TravelPlannerPro - Input Validators
Validates user input for travel planning requests.
"""

import re
import logging
from datetime import datetime
from typing import Dict, Tuple, Any

logger = logging.getLogger(__name__)

# ─── Constants ────────────────────────────────────────────────────────────────

VALID_TRANSPORT_MODES = {
    "flight", "train", "bus", "car", "cruise", "mixed", "any"
}

VALID_HOTEL_PREFS = {
    "budget", "hostel", "mid-range", "boutique", "luxury", "resort", "villa", "any"
}

VALID_TRAVEL_STYLES = {
    "solo", "couple", "family", "group", "business", "adventure",
    "luxury", "sustainable", "backpacker", "leisure"
}

VALID_BUDGET_RANGES = {
    "budget", "low", "medium", "mid", "high", "luxury", "premium"
}

MAX_TRAVELERS = 50
MIN_NAME_LEN = 2
MAX_NAME_LEN = 100
MAX_INTERESTS_LEN = 500
MAX_SPECIAL_REQUESTS_LEN = 1000


def validate_travel_form(data: Dict[str, Any]) -> Tuple[bool, Dict[str, str]]:
    """
    Validate travel planning form submission data.

    Args:
        data: Dictionary of form fields from request.

    Returns:
        Tuple of (is_valid: bool, errors: dict)
    """
    errors: Dict[str, str] = {}

    # ── Source ────────────────────────────────────────────────────────────────
    source = str(data.get("source", "")).strip()
    if not source:
        errors["source"] = "Departure city is required."
    elif len(source) < MIN_NAME_LEN:
        errors["source"] = "Departure city must be at least 2 characters."
    elif len(source) > MAX_NAME_LEN:
        errors["source"] = "Departure city is too long (max 100 characters)."

    # ── Destination ───────────────────────────────────────────────────────────
    destination = str(data.get("destination", "")).strip()
    if not destination:
        errors["destination"] = "Destination city is required."
    elif len(destination) < MIN_NAME_LEN:
        errors["destination"] = "Destination must be at least 2 characters."
    elif len(destination) > MAX_NAME_LEN:
        errors["destination"] = "Destination name is too long (max 100 characters)."
    elif source and source.lower() == destination.lower():
        errors["destination"] = "Source and destination cannot be the same."

    # ── Departure Date ────────────────────────────────────────────────────────
    departure_date_str = str(data.get("departure_date", "")).strip()
    departure_date = None
    if not departure_date_str:
        errors["departure_date"] = "Departure date is required."
    else:
        departure_date = _parse_date(departure_date_str)
        if departure_date is None:
            errors["departure_date"] = "Invalid date format. Use YYYY-MM-DD."
        elif departure_date.date() < datetime.now().date():
            errors["departure_date"] = "Departure date cannot be in the past."

    # ── Return Date ───────────────────────────────────────────────────────────
    return_date_str = str(data.get("return_date", "")).strip()
    if not return_date_str:
        errors["return_date"] = "Return date is required."
    else:
        return_date = _parse_date(return_date_str)
        if return_date is None:
            errors["return_date"] = "Invalid date format. Use YYYY-MM-DD."
        elif departure_date and return_date and return_date <= departure_date:
            errors["return_date"] = "Return date must be after departure date."

    # ── Travelers ─────────────────────────────────────────────────────────────
    travelers_raw = data.get("travelers", "1")
    try:
        travelers = int(travelers_raw)
        if travelers < 1:
            errors["travelers"] = "Number of travellers must be at least 1."
        elif travelers > MAX_TRAVELERS:
            errors["travelers"] = f"Number of travellers cannot exceed {MAX_TRAVELERS}."
    except (ValueError, TypeError):
        errors["travelers"] = "Number of travellers must be a valid integer."

    # ── Budget ────────────────────────────────────────────────────────────────
    budget = str(data.get("budget", "")).strip()
    if not budget:
        errors["budget"] = "Budget preference is required."

    # ── Interests ─────────────────────────────────────────────────────────────
    interests = str(data.get("interests", "")).strip()
    if len(interests) > MAX_INTERESTS_LEN:
        errors["interests"] = f"Interests description too long (max {MAX_INTERESTS_LEN} chars)."

    # ── Transport ─────────────────────────────────────────────────────────────
    transport = str(data.get("transport", "any")).strip().lower()
    if transport and transport not in VALID_TRANSPORT_MODES:
        # Allow freeform — just warn / sanitize
        pass

    # ── Hotel Preference ──────────────────────────────────────────────────────
    hotel_pref = str(data.get("hotel_pref", "any")).strip().lower()
    # Allow freeform hotel preferences

    # ── Special Requests ──────────────────────────────────────────────────────
    special_requests = str(data.get("special_requests", "")).strip()
    if len(special_requests) > MAX_SPECIAL_REQUESTS_LEN:
        errors["special_requests"] = (
            f"Special requests too long (max {MAX_SPECIAL_REQUESTS_LEN} chars)."
        )

    is_valid = len(errors) == 0
    return is_valid, errors


def validate_chat_message(message: str) -> Tuple[bool, str]:
    """
    Validate a chat message string.

    Returns:
        Tuple of (is_valid: bool, error_message: str)
    """
    if not message:
        return False, "Message cannot be empty."

    msg = str(message).strip()
    if not msg:
        return False, "Message cannot be blank."

    if len(msg) > 2000:
        return False, "Message is too long (max 2000 characters)."

    return True, ""


def sanitize_string(value: str, max_length: int = 200) -> str:
    """Remove potentially harmful characters and trim string."""
    if not value:
        return ""
    # Remove HTML tags
    cleaned = re.sub(r"<[^>]+>", "", str(value))
    # Remove special shell/injection characters
    cleaned = re.sub(r"[;&|`$\\]", "", cleaned)
    return cleaned.strip()[:max_length]


def _parse_date(date_str: str) -> Any:
    """Attempt to parse a date string in YYYY-MM-DD format."""
    formats = ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%m/%d/%Y"]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None
