from canonical_pipeline.taxonomy import categorize_incongruence, legacy_categorize_incongruence


def base_row(**updates):
    row = {
        "review_text": "It was nervous at first but the pilot made us feel safe.",
        "rating": 5,
        "sentiment_polarity": 0.4,
        "sentiment_neg": 0.03,
        "legacy_language": "English",
        "legacy_is_english": 1,
        "analysis_language_status": "english",
    }
    row.update(updates)
    return row


def test_iso_english_is_not_misclassified_as_multilingual():
    assert categorize_incongruence(base_row()) == "Type 3: Fear Transformation / Arousal"


def test_reproduces_historical_english_string_bug():
    assert legacy_categorize_incongruence(base_row()) == "Type 9: Multilingual Lexicon Artifact"


def test_non_english_and_uncertain_are_separate():
    assert categorize_incongruence(base_row(analysis_language_status="non_english")) == "Type 9: Multilingual Lexicon Artifact"
    assert categorize_incongruence(base_row(analysis_language_status="uncertain")) == "Uncertain: Language Review Required"


def test_language_gate_precedes_vader_baseline():
    row = base_row(
        analysis_language_status="non_english",
        sentiment_polarity=0.9,
        sentiment_neg=0.0,
    )
    assert categorize_incongruence(row) == "Type 9: Multilingual Lexicon Artifact"
