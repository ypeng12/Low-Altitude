"""Stable identifiers used to join independently generated datasets."""

from __future__ import annotations

import hashlib
import re
import unicodedata


_WHITESPACE = re.compile(r"\s+")


def normalize_identity_text(value: object) -> str:
    """Normalize identity fields without changing the stored source text."""

    if value is None:
        return ""
    text = unicodedata.normalize("NFKC", str(value))
    return _WHITESPACE.sub(" ", text).strip().casefold()


def stable_review_id(user_name: object, review_text: object) -> str:
    """Match the repository's deduplication identity using a stable hash."""

    payload = (
        normalize_identity_text(user_name)
        + "\x1f"
        + normalize_identity_text(review_text)
    ).encode("utf-8")
    return "review_" + hashlib.sha256(payload).hexdigest()[:24]


def stable_span_id(
    review_id: str,
    start: int,
    end: int,
    unit_type: str,
    occurrence: int = 0,
) -> str:
    payload = f"{review_id}\x1f{start}\x1f{end}\x1f{unit_type}\x1f{occurrence}"
    return "span_" + hashlib.sha256(payload.encode("utf-8")).hexdigest()[:24]
