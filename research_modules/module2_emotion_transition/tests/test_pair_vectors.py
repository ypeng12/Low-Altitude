import numpy as np

from emotion_transition.pair_vectors import directional_vectors


def test_directional_vectors_are_normalized_and_zero_safe():
    source = np.asarray([[1.0, 0.0], [1.0, 1.0]], dtype=np.float32)
    target = np.asarray([[1.0, 1.0], [1.0, 1.0]], dtype=np.float32)
    vectors, norms, zero = directional_vectors(source, target, 1e-12)
    assert np.allclose(vectors[0], [0.0, 1.0])
    assert np.allclose(vectors[1], [0.0, 0.0])
    assert np.allclose(norms, [1.0, 0.0])
    assert zero.tolist() == [False, True]
