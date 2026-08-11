import pandas as pd
import pytest

from emotion_discovery.prepare import NRC_COLUMNS, validate_canonical_reviews


def canonical_row():
    row = {
        "review_id": "r1",
        "review_title": "title",
        "review_text": "text",
        "legacy_tour_name": "tour",
        "legacy_language": "English",
        "legacy_is_english": True,
        "language_iso": "en",
        "language_confidence": 0.99,
        "analysis_language_status": "english",
        "analysis_is_english": True,
        "top_k_predictions": "en:0.99",
        "sentiment_polarity": 0.5,
        "sentiment_pos": 0.5,
        "sentiment_neg": 0.0,
        "nrc_baseline_available": True,
    }
    row.update({column: 0.0 for column in NRC_COLUMNS})
    return row


def test_canonical_input_requires_consistent_english_status_and_nrc8():
    validate_canonical_reviews(pd.DataFrame([canonical_row()]))
    invalid = canonical_row()
    invalid["analysis_is_english"] = False
    with pytest.raises(ValueError, match="disagrees"):
        validate_canonical_reviews(pd.DataFrame([invalid]))
    invalid = canonical_row()
    invalid["nrc_baseline_available"] = False
    with pytest.raises(ValueError, match="without the NRC8"):
        validate_canonical_reviews(pd.DataFrame([invalid]))
