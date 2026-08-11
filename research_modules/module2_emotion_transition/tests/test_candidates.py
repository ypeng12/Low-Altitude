import pandas as pd

from emotion_transition.candidates import extract_adjacent_candidates


def test_adjacent_candidate_preserves_offsets_and_leaves_labels_blank():
    text = "I was nervous, but the pilot made me calm."
    spans = pd.DataFrame(
        [
            {
                "review_id": "r1",
                "span_id": "s1",
                "parent_sentence_id": "p1",
                "span_index_within_sentence": 0,
                "span_start": 0,
                "span_end": 13,
                "span_text": "I was nervous",
                "token_count": 3,
                "marker_before": "",
            },
            {
                "review_id": "r1",
                "span_id": "s2",
                "parent_sentence_id": "p1",
                "span_index_within_sentence": 1,
                "span_start": 19,
                "span_end": 42,
                "span_text": "the pilot made me calm.",
                "token_count": 5,
                "marker_before": "but",
            },
        ]
    )
    sentences = pd.DataFrame(
        [
            {
                "review_id": "r1",
                "sentence_id": "p1",
                "sentence_text": text,
                "sentence_start": 0,
                "sentence_end": len(text),
            }
        ]
    )
    candidates, audit = extract_adjacent_candidates(
        spans,
        sentences,
        {"r1": text},
        minimum_source_tokens=3,
        minimum_target_tokens=3,
        included_relations={"adversative"},
    )
    assert audit.empty
    assert len(candidates) == 1
    row = candidates.iloc[0]
    assert row["source_span"] == "I was nervous"
    assert row["target_span"] == "the pilot made me calm."
    assert row["source_emotion"] == ""
    assert row["target_emotion"] == ""
    assert row["annotation_status"] == "unlabeled_candidate"
