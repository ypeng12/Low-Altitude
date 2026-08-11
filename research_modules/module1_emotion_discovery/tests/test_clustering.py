import numpy as np

from emotion_discovery.clustering import best_jaccard


def test_best_jaccard_aligns_clusters_without_reusing_numeric_labels():
    reference = np.array([True, True, False, False, False])
    other_labels = np.array([7, 7, 2, 2, -1])
    assert best_jaccard(reference, other_labels) == 1.0


def test_best_jaccard_treats_noise_as_unmatched():
    reference = np.array([True, True, False])
    other_labels = np.array([-1, -1, 0])
    assert best_jaccard(reference, other_labels) == 0.0
