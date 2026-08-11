import pandas as pd

from emotion_discovery.review_packet import HUMAN_COLUMNS, combine_cluster_sources


def test_combine_cluster_sources_preserves_views_and_blank_human_fields():
    inventory = pd.DataFrame(
        {
            "cluster_id": [0],
            "cluster_size": [10],
            "corpus_derived_phrase_label": ["small plane"],
        }
    )
    profiles = pd.DataFrame(
        {
            "discovery_view": ["full_unsupervised", "cate_focused"],
            "cluster_id": [0, 0],
            "reference_examples": [1, 1],
            "goemotions_profile_top_labels": ["[]", "[]"],
            "goemotions_profile_max_probability": [0.8, 0.7],
            "goemotions_top_label_agreement": [1.0, 1.0],
        }
    )
    examples = pd.DataFrame(
        {
            "discovery_view": ["full_unsupervised", "cate_focused"],
            "cluster_id": [0, 0],
            "rank": [1, 1],
            "span_text": ["I felt nervous.", "I felt safe."],
        }
    )
    result = combine_cluster_sources(inventory, inventory, profiles, examples)
    assert set(result["discovery_view"]) == {"full_unsupervised", "cate_focused"}
    assert result["representative_example_01"].notna().all()
    assert all(result[column].eq("").all() for column in HUMAN_COLUMNS)
