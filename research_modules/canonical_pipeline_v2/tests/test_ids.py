from canonical_pipeline.ids import stable_review_id, stable_tour_id


def test_review_id_is_stable_across_case_and_whitespace():
    left = stable_review_id(" Alice ", "A  great\nflight")
    right = stable_review_id("alice", "a great flight")
    assert left == right
    assert left.startswith("review_")


def test_review_id_depends_on_user_and_text():
    assert stable_review_id("alice", "great") != stable_review_id("bob", "great")
    assert stable_review_id("alice", "great") != stable_review_id("alice", "bad")


def test_tour_id_is_filename_stable():
    assert stable_tour_id("Tour_A.csv") == stable_tour_id("tour_a.CSV")
