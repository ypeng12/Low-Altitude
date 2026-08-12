import pandas as pd

from emotion_discovery.candidate_review_relationship import (
    build_candidate_review_links,
    summarize_candidate_reviews,
)


def test_candidate_review_links_deduplicate_spans_across_views():
    canonical = pd.DataFrame(
        {
            "review_id": ["r1", "r2"],
            "rating": [5, 3],
            "sentiment_polarity": [0.9, -0.2],
            "analysis_language_status": ["english", "english"],
        }
    )
    full = pd.DataFrame(
        {
            "review_id": ["r1", "r2"],
            "span_id": ["s1", "s2"],
            "cluster_id": [1, 9],
            "membership_probability": [0.8, 0.7],
        }
    )
    focused = pd.DataFrame(
        {
            "review_id": ["r1"],
            "span_id": ["s1"],
            "cluster_id": [2],
            "membership_probability": [0.9],
        }
    )
    candidates = [
        {
            "candidate_id": "scenic_awe",
            "full_unsupervised_clusters": [1],
            "cate_focused_clusters": [2],
        }
    ]
    spans, reviews = build_candidate_review_links(canonical, full, focused, candidates)
    assert len(spans) == 1
    assert spans.iloc[0]["evidence_views"] == "cate_focused|full_unsupervised"
    assert reviews.iloc[0]["unique_evidence_spans"] == 1
    assert reviews.iloc[0]["rating"] == 5


def test_candidate_review_summary_uses_review_level_outcomes():
    canonical = pd.DataFrame(
        {
            "review_id": ["r1", "r2"],
            "rating": [5, 3],
            "sentiment_polarity": [0.9, -0.2],
            "analysis_language_status": ["english", "english"],
        }
    )
    links = pd.DataFrame(
        {
            "candidate_id": ["flight_apprehension"],
            "review_id": ["r2"],
            "rating": [3],
            "sentiment_polarity": [-0.2],
        }
    )
    summary = summarize_candidate_reviews(canonical, links)
    candidate = summary.loc[summary["candidate_id"].eq("flight_apprehension")].iloc[0]
    assert candidate["mean_rating"] == 3
    assert candidate["rating_3_percent"] == 100
    assert candidate["mean_rating_difference_from_corpus"] == -1
