from emotion_discovery.ids import stable_review_id, stable_span_id


def test_review_id_normalizes_case_unicode_and_whitespace():
    left = stable_review_id(" Alice ", "Amazing\u00a0view!\nLoved it.")
    right = stable_review_id("alice", "amazing view! loved it.")
    assert left == right


def test_review_and_span_ids_are_namespaced_and_deterministic():
    review_id = stable_review_id("A", "B")
    assert review_id.startswith("review_")
    assert stable_span_id(review_id, 0, 4, "sentence") == stable_span_id(
        review_id, 0, 4, "sentence"
    )
    assert stable_span_id(review_id, 0, 4, "sentence") != stable_span_id(
        review_id, 0, 4, "clause"
    )
