import numpy as np
import pandas as pd

from emotion_transition.reporting import distinctive_phrases, representative_pairs


def test_source_target_phrases_are_induced_separately():
    labels = np.asarray([0, 0, 1, 1])
    phrases = distinctive_phrases(
        ["nervous before flight", "nervous in plane", "expensive tour", "expensive price"],
        labels,
        top_n=5,
        max_features=100,
        ngram_range=(1, 2),
    )
    assert any("nervous" in phrase for phrase, _ in phrases[0])
    assert any("expensive" in phrase for phrase, _ in phrases[1])


def test_representative_pairs_deduplicate_review_and_exact_pair():
    members = pd.DataFrame(
        {
            "pair_embedding_row": [0, 1, 2],
            "transition_id": ["t0", "t1", "t2"],
            "review_id": ["r0", "r1", "r2"],
            "sentence": ["x"] * 3,
            "source_span": ["scary", "SCARY!", "expensive"],
            "transition_marker": ["but"] * 3,
            "target_span": ["exciting", "exciting", "worth it"],
            "membership_probability": [0.9] * 3,
        }
    )
    vectors = np.asarray([[1.0, 0.0], [0.99, 0.01], [0.8, 0.2]], dtype=np.float32)
    result = representative_pairs(1, members, vectors, 10)
    assert result["transition_id"].tolist() == ["t0", "t2"]
