from __future__ import annotations

import hashlib

import pandas as pd

from emotion_lexicon.annotation import write_review_workbook


def _sha256(path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_workbook_is_byte_reproducible(tmp_path) -> None:
    reviews = pd.DataFrame(
        [
            {
                "sampling_rank": 1,
                "review_id": "review_1",
                "primary_tour_name": "Tour",
                "aircraft_type": "Airplane",
                "length_bin": "[0,50)",
                "review_title": "Title",
                "review_text": "I was nervous.",
            }
        ]
    )
    inventory = pd.DataFrame([{"lemma": "nervous", "human_status": ""}])
    first = tmp_path / "first.xlsx"
    second = tmp_path / "second.xlsx"
    for path in [first, second]:
        write_review_workbook(
            path,
            reviews,
            inventory,
            stage_size=500,
            forbidden_lexicons=["NRC", "VADER"],
        )
    assert _sha256(first) == _sha256(second)
