"""Discourse marker typing and stable transformation candidate identity."""

from __future__ import annotations

import hashlib


MARKER_RELATIONS = {
    "but": ("adversative", 0.95),
    "however": ("adversative", 0.95),
    "yet": ("adversative", 0.92),
    "nevertheless": ("adversative", 0.95),
    "nonetheless": ("adversative", 0.95),
    "although": ("concessive", 0.92),
    "though": ("concessive", 0.88),
    "even though": ("concessive", 0.94),
    "despite": ("concessive", 0.88),
    "whereas": ("adversative", 0.90),
    "then": ("temporal_progression", 0.78),
    "still": ("continuity_or_reappraisal", 0.72),
    "while": ("ambiguous_contrast_or_simultaneity", 0.62),
    ";": ("punctuation_boundary", 0.45),
    "—": ("punctuation_boundary", 0.45),
}


def marker_relation(marker: object) -> tuple[str, float]:
    value = str(marker).strip().casefold() if marker is not None else ""
    return MARKER_RELATIONS.get(value, ("unknown", 0.0))


def stable_transition_id(
    review_id: str,
    sentence_id: str,
    source_span_id: str,
    target_span_id: str,
    marker: str,
) -> str:
    payload = "\x1f".join(
        [review_id, sentence_id, source_span_id, target_span_id, marker.casefold()]
    ).encode("utf-8")
    return "transition_" + hashlib.sha256(payload).hexdigest()[:24]
