"""Corrected, explicitly legacy mechanism taxonomy.

This supports audit/reproduction only. It is not the AEM gold standard.
"""

from __future__ import annotations

import re
from typing import Mapping


ASPECT_PATTERNS = {
    "Scenery": re.compile(r"\b(view|views|scenery|landscape|canyon|glacier|mountain|mountains|waterfall|coast|scenic|grandeur|cliff|sea|ocean|island|wildlife)\b", re.I),
    "Pilot": re.compile(r"\b(pilot|pilots|captain|aviator)\b", re.I),
    "GroundStaff": re.compile(r"\b(staff|desk|check-in|counter|reception|office|ground|boarding|driver|shuttle|agent|team)\b", re.I),
    "CabinComfort": re.compile(r"\b(seat|seats|seating|cramped|small|tight|noise|noisy|headset|headphones|cold|wind|window|legroom|comfort|uncomfortable)\b", re.I),
    "Safety": re.compile(r"\b(safe|safety|scared|nervous|afraid|fear|terrified|anxious|worry|worried|comforting|reassured|calm|secure)\b", re.I),
    "Weather": re.compile(r"\b(weather|cloud|clouds|cloudy|wind|winds|windy|rain|fog|foggy|snow|visibility|overcast)\b", re.I),
    "PriceValue": re.compile(r"\b(price|prices|expensive|cost|costs|costly|worth|money|value|dollar|dollars|cash|cheap|affordable)\b", re.I),
    "ServiceRecovery": re.compile(r"\b(refund|refunded|reschedule|rescheduled|alternative|delay|delayed|cancel|cancelled|cancellation|accommodated|fix|fixed)\b", re.I),
    "Companion": re.compile(r"\b(husband|wife|family|kids|children|son|daughter|mom|dad|friend|friends|couple|honeymoon|anniversary)\b", re.I),
    "LifetimeExperience": re.compile(r"\b(bucket list|once in a lifetime|unforgettable|dream|experience of a lifetime|must do|highlight)\b", re.I),
}

_NEGATION = re.compile(r"\b(never felt unsafe|no problem|no problems|no delay|no delays|not dangerous|don't miss|cannot recommend enough)\b", re.I)
_FEAR = re.compile(r"\b(scared|terrified|nervous|afraid|anxious|fear)\b", re.I)
_REASSURANCE = re.compile(r"\b(safe|reassured|calm|made us feel|great pilot|smooth)\b", re.I)
_EXPENSIVE = re.compile(r"\b(expensive|costly|pricey|a bit steep|cost a lot)\b", re.I)
_WORTH = re.compile(r"\b(worth|worth it|every penny|priceless|no regrets)\b", re.I)
_SERVICE_FAIL = re.compile(r"\b(cancel|cancelled|cancellation|delay|delayed|weather change)\b", re.I)
_RECOVERY = re.compile(r"\b(refund|refunded|rescheduled|accommodated|handled well|great service)\b", re.I)
_WEATHER = re.compile(r"\b(cloud|clouds|cloudy|wind|fog|rain|weather)\b", re.I)
_ACCEPTANCE = re.compile(r"\b(pilot did best|still amazing|great view|understandable)\b", re.I)
_FRICTION = re.compile(r"\b(cramped|tight|small|noise|noisy|bumpy|cold|waiting|long wait)\b", re.I)


def extract_aspects(text: object) -> list[str]:
    value = text if isinstance(text, str) else ""
    return [name for name, pattern in ASPECT_PATTERNS.items() if pattern.search(value)]


def _number(row: Mapping[str, object], name: str, default: float) -> float:
    try:
        value = float(row.get(name, default))
        return default if value != value else value
    except (TypeError, ValueError):
        return default


def categorize_incongruence(row: Mapping[str, object]) -> str:
    """Classify only after the canonical ISO language decision is known."""

    language_status = str(row.get("analysis_language_status", "uncertain"))
    if language_status == "non_english":
        return "Type 9: Multilingual Lexicon Artifact"
    if language_status != "english":
        return "Uncertain: Language Review Required"

    text = str(row.get("review_text", ""))
    rating = _number(row, "rating", 5.0)
    compound = _number(row, "sentiment_polarity", 0.0)
    negative = _number(row, "sentiment_neg", 0.0)

    if rating >= 4 and compound >= 0.5 and negative < 0.02:
        return "Pure Positive Baseline"
    if rating <= 3:
        return "Low Rating Failure"
    if _NEGATION.search(text):
        return "Type 8: Negation Pseudo-Negative"
    if _FEAR.search(text) and _REASSURANCE.search(text):
        return "Type 3: Fear Transformation / Arousal"
    if _EXPENSIVE.search(text) and _WORTH.search(text):
        return "Type 5: Price Concession"
    if _SERVICE_FAIL.search(text) and _RECOVERY.search(text):
        return "Type 4: Service Recovery"
    if _WEATHER.search(text) and _ACCEPTANCE.search(text):
        return "Type 2: Uncontrollable Natural Factor"
    if negative >= 0.05 or _FRICTION.search(text):
        return "Type 1: Local Friction - Overall Positive"
    if rating >= 4 and compound < 0:
        return "Type 10: True Star-Text Conflict"
    return "Minor Local Noise"


def legacy_categorize_incongruence(row: Mapping[str, object]) -> str:
    """Exact decision order responsible for the historical language bug."""

    text = str(row.get("review_text", ""))
    rating = _number(row, "rating", 5.0)
    compound = _number(row, "sentiment_polarity", 0.0)
    negative = _number(row, "sentiment_neg", 0.0)
    if rating >= 4 and compound >= 0.5 and negative < 0.02:
        return "Pure Positive Baseline"
    if rating <= 3:
        return "Low Rating Failure"
    if _number(row, "legacy_is_english", 1.0) == 0 or str(row.get("legacy_language", "en")) != "en":
        return "Type 9: Multilingual Lexicon Artifact"
    return categorize_incongruence({**dict(row), "analysis_language_status": "english"})
