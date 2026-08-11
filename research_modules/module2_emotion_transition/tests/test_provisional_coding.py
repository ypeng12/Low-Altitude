import pytest

from emotion_transition.provisional_coding import validate_mappings


def test_provisional_mapping_rejects_gold_claim_unknown_and_duplicate_clusters():
    valid = {
        "status": "llm_assisted_provisional_not_human_validated",
        "mappings": [{"mapping_id": "m1", "cluster_ids": [1]}],
    }
    validate_mappings(valid, {1, 2})
    with pytest.raises(ValueError, match="must not claim"):
        validate_mappings({**valid, "status": "gold"}, {1, 2})
    with pytest.raises(ValueError, match="unknown cluster"):
        validate_mappings(valid, {2})
    duplicate = {
        "status": valid["status"],
        "mappings": [
            {"mapping_id": "m1", "cluster_ids": [1]},
            {"mapping_id": "m2", "cluster_ids": [1]},
        ],
    }
    with pytest.raises(ValueError, match="two provisional mappings"):
        validate_mappings(duplicate, {1})
