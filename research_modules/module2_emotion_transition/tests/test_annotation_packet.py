import pandas as pd

from emotion_transition.annotation_packet import stratified_noise_sample


def test_stratified_noise_sample_is_deterministic_and_complete():
    frame = pd.DataFrame(
        {
            "transition_id": [f"t{i}" for i in range(20)],
            "discourse_relation_family": ["a"] * 10 + ["b"] * 6 + ["c"] * 4,
        }
    )
    first = stratified_noise_sample(frame, 10, 42)
    second = stratified_noise_sample(frame, 10, 42)
    assert first["transition_id"].tolist() == second["transition_id"].tolist()
    assert len(first) == 10
    assert first["transition_id"].nunique() == 10
    assert set(first["discourse_relation_family"]) == {"a", "b", "c"}
