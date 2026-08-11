import numpy as np

from emotion_transition.clustering import best_jaccard


def test_best_jaccard_ignores_numeric_cluster_identity_and_noise():
    reference = np.asarray([True, True, False, False])
    assert best_jaccard(reference, np.asarray([9, 9, -1, 2])) == 1.0
    assert best_jaccard(reference, np.asarray([-1, -1, 3, 3])) == 0.0
