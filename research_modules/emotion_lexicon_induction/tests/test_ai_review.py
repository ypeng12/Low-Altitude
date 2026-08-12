from __future__ import annotations

import json

import pandas as pd

from emotion_lexicon.ai_review import build_human_adjudication_queue, validate_ai_responses


def _write_jsonl(path, rows) -> None:
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")


def test_ai_proposals_must_match_exact_task_tokens(tmp_path) -> None:
    tasks = tmp_path / "tasks.jsonl"
    responses = tmp_path / "responses.jsonl"
    _write_jsonl(
        tasks,
        [
            {
                "input": {
                    "review_id": "review_1",
                    "eligible_tokens": [
                        {
                            "token_index": 3,
                            "surface": "nervous",
                            "normalized_word": "nervous",
                            "lemma": "nervous",
                            "coarse_pos": "ADJ",
                            "char_start": 6,
                            "char_end": 13,
                        }
                    ],
                }
            }
        ],
    )
    _write_jsonl(
        responses,
        [
            {
                "review_id": "review_1",
                "selected_occurrences": [
                    {
                        "token_index": 3,
                        "surface": "nervous",
                        "status": "E1",
                        "experiencer": "tourist",
                        "provisional_open_category": "nervousness",
                        "rationale": "The reviewer states an internal state.",
                        "confidence": 0.9,
                    },
                    {
                        "token_index": 3,
                        "surface": "afraid",
                        "status": "E1",
                        "confidence": 0.9,
                    },
                ],
            }
        ],
    )
    proposals, errors = validate_ai_responses(tasks, responses, {"E1", "E2", "E3", "N", "U"})
    assert len(proposals) == 1
    assert proposals.iloc[0]["lemma"] == "nervous"
    assert len(errors) == 1
    assert errors.iloc[0]["error"] == "surface_does_not_exactly_match_task_token"


def test_human_queue_does_not_turn_ai_proposal_into_approval() -> None:
    candidates = pd.DataFrame(
        [
            {"lemma": "nervous", "ai_status": "", "ai_provisional_category": "", "ai_rationale": "", "ai_confidence": ""},
            {"lemma": "pilot", "ai_status": "", "ai_provisional_category": "", "ai_rationale": "", "ai_confidence": ""},
        ]
    )
    proposals = pd.DataFrame(
        [
            {
                "lemma": "nervous",
                "ai_status": "E1",
                "ai_confidence": 0.9,
                "ai_provisional_category": "nervousness",
            }
        ]
    )
    queue = build_human_adjudication_queue(candidates, proposals)
    nervous = queue.loc[queue["lemma"].eq("nervous")].iloc[0]
    assert nervous["adjudication_priority"] == "review_direct_emotion_proposal"
    assert nervous["human_status"] == "" if "human_status" in nervous else True
