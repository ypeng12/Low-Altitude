import numpy as np
import pandas as pd

from emotion_discovery.reporting import _representatives, cluster_distinctive_phrases


def test_cluster_labels_are_induced_from_cluster_text():
    texts = [
        "terrified before takeoff",
        "terrified during the climb",
        "deeply grateful afterward",
        "grateful for the reassurance",
    ]
    labels = np.array([0, 0, 1, 1])
    phrases = cluster_distinctive_phrases(texts, labels, 5, 100, (1, 2))
    assert any("terrified" in phrase for phrase, _ in phrases[0])
    assert any("grateful" in phrase for phrase, _ in phrases[1])


def test_representatives_are_review_and_text_diverse():
    members = pd.DataFrame(
        {
            "embedding_row": [0, 1, 2, 3, 4],
            "span_id": ["s0", "s1", "s2", "s3", "s4"],
            "review_id": ["r0", "r1", "r2", "r3", "r4"],
            "span_text": [
                "It was worth it.",
                "IT WAS WORTH IT!",
                "The flight was absolutely worth the price today.",
                "The flight was absolutely worth the price.",
                "The pilot made us feel safe.",
            ],
            "sentence_text": ["parent"] * 5,
            "unit_type": ["clause"] * 5,
            "marker_before": [""] * 5,
            "membership_probability": [0.9] * 5,
        }
    )
    embeddings = np.asarray(
        [
            [1.00, 0.00],
            [0.99, 0.01],
            [0.98, 0.02],
            [0.97, 0.03],
            [0.80, 0.20],
        ],
        dtype=np.float32,
    )
    result = _representatives(7, members, embeddings, limit=10)
    assert result["span_id"].tolist() == ["s0", "s2", "s4"]
    assert result["rank"].tolist() == [1, 2, 3]
