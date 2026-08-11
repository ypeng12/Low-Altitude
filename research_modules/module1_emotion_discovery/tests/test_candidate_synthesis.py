import pytest

from emotion_discovery.candidate_synthesis import validate_candidate_configuration


def test_candidate_synthesis_requires_exact_count_and_provisional_status():
    valid = {
        "required_candidate_count": 3,
        "status": "llm_assisted_provisional_not_human_validated",
        "candidate_families": [
            {"candidate_id": "a"},
            {"candidate_id": "b"},
            {"candidate_id": "c"},
        ],
    }
    validate_candidate_configuration(valid)
    invalid = {**valid, "candidate_families": valid["candidate_families"][:2]}
    with pytest.raises(ValueError, match="exactly 3"):
        validate_candidate_configuration(invalid)
    invalid = {**valid, "status": "human_validated"}
    with pytest.raises(ValueError, match="must not claim"):
        validate_candidate_configuration(invalid)
