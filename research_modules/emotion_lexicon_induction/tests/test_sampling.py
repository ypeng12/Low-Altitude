from __future__ import annotations

import pandas as pd

from emotion_lexicon.sampling import make_disjoint_sample_manifest, stable_uniform


def _reviews(size: int = 20) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "review_id": [f"review_{index:03d}" for index in range(size)],
            "rating": [(index % 5) + 1 for index in range(size)],
            "aircraft_type": ["plane" if index % 2 else "helicopter" for index in range(size)],
            "review_word_count": [10 + index * 10 for index in range(size)],
        }
    )


def _links(size: int = 20) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "review_id": [f"review_{index:03d}" for index in range(size)],
            "tour_id": [f"tour_{index % 3}" for index in range(size)],
            "tour_name": [f"Tour {index % 3}" for index in range(size)],
            "source_file": [f"source_{index % 3}.csv" for index in range(size)],
        }
    )


def test_stable_uniform_is_deterministic_and_open() -> None:
    first = stable_uniform("review_abc", 42)
    assert first == stable_uniform("review_abc", 42)
    assert first != stable_uniform("review_abc", 43)
    assert 0 < first < 1


def test_disjoint_samples_are_reproducible_and_nonoverlapping() -> None:
    arguments = dict(
        seed=42,
        stages=[{"name": "discovery_5", "size": 5}, {"name": "gold_12", "size": 12}],
        balance_columns=["rating", "primary_tour_id", "aircraft_type", "length_bin"],
        balance_strength_per_column=0.35,
        maximum_relative_weight=12.0,
        length_bin_edges=[0, 50, 100, 200, 1_000_000],
    )
    first = make_disjoint_sample_manifest(_reviews(), _links(), **arguments)
    second = make_disjoint_sample_manifest(_reviews(), _links(), **arguments)
    pd.testing.assert_frame_equal(first, second)
    five = set(first.loc[first["in_discovery_5"], "review_id"])
    twelve = set(first.loc[first["in_gold_12"], "review_id"])
    assert len(five) == 5
    assert len(twelve) == 12
    assert five.isdisjoint(twelve)
    assert int(first["in_manually_studied_17"].sum()) == 17


def test_duplicate_review_ids_are_rejected() -> None:
    reviews = _reviews()
    reviews.loc[1, "review_id"] = reviews.loc[0, "review_id"]
    try:
        make_disjoint_sample_manifest(
            reviews,
            _links(),
            seed=42,
            stages=[{"name": "discovery_5", "size": 5}],
            balance_columns=["rating"],
            balance_strength_per_column=0.35,
            maximum_relative_weight=12.0,
            length_bin_edges=[0, 100, 1_000_000],
        )
    except ValueError as error:
        assert "unique" in str(error)
    else:
        raise AssertionError("duplicate review IDs were accepted")
