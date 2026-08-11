"""Stable content identifiers; never depend on input row order."""

from __future__ import annotations

import hashlib
import re
import unicodedata


_WHITESPACE = re.compile(r"\s+")


def normalize_identity_text(value: object) -> str:
    if value is None:
        return ""
    text = unicodedata.normalize("NFKC", str(value))
    return _WHITESPACE.sub(" ", text).strip().casefold()


def stable_review_id(user_name: object, review_text: object) -> str:
    payload = (
        normalize_identity_text(user_name)
        + "\x1f"
        + normalize_identity_text(review_text)
    ).encode("utf-8")
    return "review_" + hashlib.sha256(payload).hexdigest()[:24]


def stable_tour_id(source_file: str) -> str:
    normalized = unicodedata.normalize("NFKC", source_file).casefold().encode("utf-8")
    return "tour_" + hashlib.sha256(normalized).hexdigest()[:20]
