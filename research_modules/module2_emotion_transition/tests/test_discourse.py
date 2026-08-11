from emotion_transition.discourse import marker_relation, stable_transition_id


def test_marker_relation_separates_adversative_temporal_and_ambiguous():
    assert marker_relation("BUT") == ("adversative", 0.95)
    assert marker_relation("then")[0] == "temporal_progression"
    assert marker_relation("while")[0] == "ambiguous_contrast_or_simultaneity"


def test_transition_id_is_deterministic_and_marker_normalized():
    first = stable_transition_id("r", "s", "a", "b", "But")
    second = stable_transition_id("r", "s", "a", "b", "but")
    assert first == second
