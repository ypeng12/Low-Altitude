import numpy as np

from emotion_discovery.reporting import cluster_distinctive_phrases


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
