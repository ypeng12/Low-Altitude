from emotion_discovery.language import classify_prediction


def test_language_decision_thresholds_keep_uncertainty():
    assert classify_prediction("__label__en", 0.91, "en", 0.7, 0.7).decision == "english"
    assert classify_prediction("__label__en", 0.61, "en", 0.7, 0.7).decision == "uncertain"
    assert classify_prediction("__label__es", 0.91, "en", 0.7, 0.7).decision == "non_english"
    assert classify_prediction("__label__es", 0.55, "en", 0.7, 0.7).decision == "uncertain"
