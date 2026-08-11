import json

import numpy as np
import pandas as pd

from emotion_discovery.goemotions_reference import (
    PROBABILITY_PREFIX,
    aggregate_cluster_profiles,
    sigmoid,
    top_label_payload,
)


def test_sigmoid_is_stable_for_extreme_logits():
    result = sigmoid(np.asarray([[-1000.0, 0.0, 1000.0]]))
    assert np.allclose(result, [[0.0, 0.5, 1.0]])


def test_top_label_payload_is_descending_and_named():
    payload = json.loads(top_label_payload([0.1, 0.8, 0.2], ["a", "b", "c"], 2))
    assert [row["reference_label"] for row in payload] == ["b", "c"]


def test_aggregate_profiles_keeps_view_and_continuous_means():
    labels = ["fear", "relief"]
    frame = pd.DataFrame(
        {
            "discovery_view": ["full", "full"],
            "cluster_id": [3, 3],
            f"{PROBABILITY_PREFIX}fear": [0.8, 0.6],
            f"{PROBABILITY_PREFIX}relief": [0.1, 0.5],
        }
    )
    result = aggregate_cluster_profiles(frame, labels, 2).iloc[0]
    assert result["discovery_view"] == "full"
    assert np.isclose(result[f"{PROBABILITY_PREFIX}fear"], 0.7)
    assert np.isclose(result[f"{PROBABILITY_PREFIX}relief"], 0.3)
    assert np.isclose(result["goemotions_top_label_agreement"], 1.0)
