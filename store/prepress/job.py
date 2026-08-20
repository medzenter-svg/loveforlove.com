"""Validation and normalization of customer personalization data before prepress."""

from __future__ import annotations

from copy import deepcopy

from print_package import OPTIONAL_PIECES


ALLOWED_FIELDS = {
    "coupleNames", "weddingDate", "weddingTime", "venueName", "venueAddress",
    "rsvpDate", "rsvpContact",
    "course1", "course1Desc", "course2", "course2Desc", "course3", "course3Desc", "dessert", "dessertDesc",
    "tableNumber", "guestName",
    "ceremonyTime", "cocktailsTime", "dinnerTime", "dancingTime", "thankMessage",
    "hotelName", "hotelAddress", "hotelCheckIn", "hotelCheckOut", "hotelBooking", "hotelTransport",
    "coordinatorName", "coordinatorRole", "coordinatorPhone", "coordinatorMessenger", "coordinatorEmail",
    "dressStyle", "dressDescription", "dressNote",
    "guestMailingAddress", "returnAddress", "monogram",
    "dayOneDate", "dayOneTime1", "dayOneEvent1", "dayOneTime2", "dayOneEvent2",
    "dayOneTime3", "dayOneEvent3", "dayOneTime4", "dayOneEvent4",
    "dayTwoDate", "dayTwoTime1", "dayTwoEvent1", "dayTwoTime2", "dayTwoEvent2",
    "dayTwoTime3", "dayTwoEvent3", "dayTwoTime4", "dayTwoEvent4",
}

ALLOWED_LABELS = {
    "invitation", "join_us", "details", "venue", "address", "rsvp", "reply_by", "menu",
    "first", "second", "third", "dessert", "table", "place", "program", "ceremony", "cocktails",
    "dinner", "dancing", "thank_you", "accommodation", "hotel", "check_in", "check_out", "booking",
    "transport", "guest_contact", "coordinator", "questions", "phone", "messenger", "email",
    "dress_code", "dress_note", "envelope", "to", "from", "envelope_liner",
    "weekend_program", "day_one", "day_two", "welcome", "brunch", "farewell", "activity",
}

MAX_FIELD_LENGTH = 600
MAX_LABEL_LENGTH = 120
SUPPORTED_LANGUAGES = {"en", "de", "fr", "it", "es", "pt", "nl", "pl", "el", "ru", "uk", "tr", "he"}


class PrintJobValidationError(ValueError):
    pass


def _clean_mapping(values, allowed_keys, max_length, mapping_name):
    if not isinstance(values, dict):
        raise PrintJobValidationError(f"{mapping_name} must be an object")

    unknown = sorted(set(values) - allowed_keys)
    if unknown:
        raise PrintJobValidationError(
            f"Unknown {mapping_name} keys: " + ", ".join(unknown)
        )

    cleaned = {}
    for key, value in values.items():
        if value is None:
            text = ""
        elif isinstance(value, (str, int, float)):
            text = str(value)
        else:
            raise PrintJobValidationError(f"{mapping_name}.{key} must be text")

        # Normalize browser line endings and remove NUL/control data that should
        # never reach Scribus text frames.
        text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\x00", "")
        if len(text) > max_length:
            raise PrintJobValidationError(
                f"{mapping_name}.{key} is too long ({len(text)} > {max_length})"
            )
        cleaned[key] = text
    return cleaned


def normalize_print_job(collection_slug, payload):
    if not isinstance(collection_slug, str) or not collection_slug:
        raise PrintJobValidationError("collection_slug is required")
    if not isinstance(payload, dict):
        raise PrintJobValidationError("payload must be an object")

    language = str(payload.get("language") or "en")
    if language not in SUPPORTED_LANGUAGES:
        raise PrintJobValidationError(f"Unsupported language preset: {language}")

    enabled_optional = payload.get("enabled_optional", sorted(OPTIONAL_PIECES))
    if not isinstance(enabled_optional, list):
        raise PrintJobValidationError("enabled_optional must be a list")
    enabled_optional = [str(piece) for piece in enabled_optional]
    unknown_optional = sorted(set(enabled_optional) - OPTIONAL_PIECES)
    if unknown_optional:
        raise PrintJobValidationError(
            "Unknown optional pieces: " + ", ".join(unknown_optional)
        )

    job = {
        "collection_slug": collection_slug,
        "language": language,
        "enabled_optional": sorted(set(enabled_optional)),
        "fields": _clean_mapping(
            payload.get("fields", {}), ALLOWED_FIELDS, MAX_FIELD_LENGTH, "fields"
        ),
        "labels": _clean_mapping(
            payload.get("labels", {}), ALLOWED_LABELS, MAX_LABEL_LENGTH, "labels"
        ),
    }
    return deepcopy(job)
