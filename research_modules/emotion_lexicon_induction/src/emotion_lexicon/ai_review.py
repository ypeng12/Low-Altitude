"""Validate exact-token AI proposals and create a human adjudication queue."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

import pandas as pd


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                row = json.loads(stripped)
            except json.JSONDecodeError as error:
                raise ValueError(f"Invalid JSON in {path} line {line_number}: {error}") from error
            if not isinstance(row, dict):
                raise ValueError(f"JSON row {line_number} in {path} must be an object")
            row["_line_number"] = line_number
            rows.append(row)
    return rows


def task_token_index(tasks_path: Path) -> dict[str, dict[int, dict[str, Any]]]:
    index: dict[str, dict[int, dict[str, Any]]] = {}
    for task in _read_jsonl(tasks_path):
        review_id = str(task["input"]["review_id"])
        if review_id in index:
            raise ValueError(f"Duplicate AI task for review_id: {review_id}")
        index[review_id] = {
            int(token["token_index"]): token for token in task["input"]["eligible_tokens"]
        }
    return index


def validate_ai_responses(
    tasks_path: Path,
    responses_path: Path,
    allowed_statuses: set[str],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Accept only proposals tied to exact task token indices and surfaces."""

    task_index = task_token_index(tasks_path)
    proposals: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    seen_reviews: set[str] = set()
    for response in _read_jsonl(responses_path):
        line_number = int(response["_line_number"])
        review_id = str(response.get("review_id", ""))
        if review_id not in task_index:
            errors.append({"line_number": line_number, "review_id": review_id, "error": "unknown_review_id"})
            continue
        if review_id in seen_reviews:
            errors.append({"line_number": line_number, "review_id": review_id, "error": "duplicate_response_review_id"})
            continue
        seen_reviews.add(review_id)
        selected = response.get("selected_occurrences", [])
        if not isinstance(selected, list):
            errors.append({"line_number": line_number, "review_id": review_id, "error": "selected_occurrences_not_list"})
            continue
        selected_indices: set[int] = set()
        for item in selected:
            if not isinstance(item, dict):
                errors.append({"line_number": line_number, "review_id": review_id, "error": "selected_occurrence_not_object"})
                continue
            try:
                token_index = int(item["token_index"])
            except (KeyError, TypeError, ValueError):
                errors.append({"line_number": line_number, "review_id": review_id, "error": "invalid_token_index"})
                continue
            token = task_index[review_id].get(token_index)
            if token is None:
                errors.append(
                    {
                        "line_number": line_number,
                        "review_id": review_id,
                        "token_index": token_index,
                        "error": "token_index_not_in_eligible_task_tokens",
                    }
                )
                continue
            if str(item.get("surface", "")) != str(token["surface"]):
                errors.append(
                    {
                        "line_number": line_number,
                        "review_id": review_id,
                        "token_index": token_index,
                        "error": "surface_does_not_exactly_match_task_token",
                    }
                )
                continue
            if token_index in selected_indices:
                errors.append(
                    {
                        "line_number": line_number,
                        "review_id": review_id,
                        "token_index": token_index,
                        "error": "duplicate_selected_token_index",
                    }
                )
                continue
            selected_indices.add(token_index)
            status = str(item.get("status", ""))
            if status not in allowed_statuses or status == "N":
                errors.append(
                    {
                        "line_number": line_number,
                        "review_id": review_id,
                        "token_index": token_index,
                        "error": "invalid_or_disallowed_ai_status",
                    }
                )
                continue
            try:
                confidence = float(item.get("confidence"))
            except (TypeError, ValueError):
                errors.append(
                    {
                        "line_number": line_number,
                        "review_id": review_id,
                        "token_index": token_index,
                        "error": "invalid_confidence",
                    }
                )
                continue
            if not 0 <= confidence <= 1:
                errors.append(
                    {
                        "line_number": line_number,
                        "review_id": review_id,
                        "token_index": token_index,
                        "error": "confidence_outside_zero_one",
                    }
                )
                continue
            proposals.append(
                {
                    "review_id": review_id,
                    "token_index": token_index,
                    "surface": str(token["surface"]),
                    "normalized_word": str(token["normalized_word"]),
                    "lemma": str(token["lemma"]),
                    "coarse_pos": str(token["coarse_pos"]),
                    "char_start": int(token["char_start"]),
                    "char_end": int(token["char_end"]),
                    "ai_status": status,
                    "ai_experiencer": str(item.get("experiencer", "unclear")),
                    "ai_provisional_category": str(item.get("provisional_open_category", "")),
                    "ai_rationale": str(item.get("rationale", "")),
                    "ai_confidence": confidence,
                    "response_line_number": line_number,
                }
            )
    proposal_columns = [
        "review_id",
        "token_index",
        "surface",
        "normalized_word",
        "lemma",
        "coarse_pos",
        "char_start",
        "char_end",
        "ai_status",
        "ai_experiencer",
        "ai_provisional_category",
        "ai_rationale",
        "ai_confidence",
        "response_line_number",
    ]
    return pd.DataFrame(proposals, columns=proposal_columns), pd.DataFrame(errors)


def build_human_adjudication_queue(
    candidates: pd.DataFrame, proposals: pd.DataFrame
) -> pd.DataFrame:
    """Aggregate valid AI proposals without turning them into human decisions."""

    result = candidates.copy()
    if proposals.empty:
        result["ai_proposal_count"] = 0
        result["ai_e1_count"] = 0
        result["ai_e2_count"] = 0
        result["ai_e3_count"] = 0
        result["ai_u_count"] = 0
        result["ai_mean_confidence"] = ""
        result["ai_proposed_categories"] = ""
        result["adjudication_priority"] = "unreviewed_no_ai_proposal"
        return result

    grouped = proposals.groupby("lemma", sort=False, observed=True)
    aggregates: list[dict[str, Any]] = []
    for lemma, group in grouped:
        counts = Counter(group["ai_status"])
        categories = "|".join(
            sorted(value for value in group["ai_provisional_category"].unique() if value)
        )
        aggregates.append(
            {
                "lemma": lemma,
                "ai_proposal_count": int(len(group)),
                "ai_e1_count": int(counts["E1"]),
                "ai_e2_count": int(counts["E2"]),
                "ai_e3_count": int(counts["E3"]),
                "ai_u_count": int(counts["U"]),
                "ai_mean_confidence": float(group["ai_confidence"].mean()),
                "ai_proposed_categories": categories,
            }
        )
    summary = pd.DataFrame(aggregates)
    result = result.drop(
        columns=[
            "ai_status",
            "ai_provisional_category",
            "ai_rationale",
            "ai_confidence",
        ],
        errors="ignore",
    ).merge(summary, on="lemma", how="left", validate="one_to_one")
    count_columns = ["ai_proposal_count", "ai_e1_count", "ai_e2_count", "ai_e3_count", "ai_u_count"]
    for column in count_columns:
        result[column] = result[column].fillna(0).astype(int)
    result["ai_mean_confidence"] = result["ai_mean_confidence"].fillna("")
    result["ai_proposed_categories"] = result["ai_proposed_categories"].fillna("")
    result["adjudication_priority"] = "unreviewed_no_ai_proposal"
    result.loc[result["ai_e1_count"].gt(0), "adjudication_priority"] = "review_direct_emotion_proposal"
    result.loc[
        result["ai_e1_count"].eq(0) & result["ai_u_count"].gt(0), "adjudication_priority"
    ] = "review_uncertain_proposal"
    sort_columns = ["adjudication_priority", "ai_e1_count", "ai_u_count", "lemma"]
    ascending = [True, False, False, True]
    if "review_frequency_in_stage" in result:
        sort_columns.insert(3, "review_frequency_in_stage")
        ascending.insert(3, False)
    return result.sort_values(sort_columns, ascending=ascending, kind="stable").reset_index(drop=True)


def ingest_stage_responses(
    stage_dir: Path,
    stage_name: str,
    responses_path: Path,
    allowed_statuses: set[str],
) -> dict[str, int]:
    tasks_path = stage_dir / f"ai_tasks_{stage_name}.jsonl"
    candidates_path = stage_dir / f"unigram_candidates_{stage_name}.csv"
    if not tasks_path.is_file() or not candidates_path.is_file():
        raise FileNotFoundError(f"Stage files are missing in {stage_dir}")
    proposals, errors = validate_ai_responses(tasks_path, responses_path, allowed_statuses)
    candidates = pd.read_csv(candidates_path, keep_default_na=False)
    queue = build_human_adjudication_queue(candidates, proposals)
    proposals.to_csv(stage_dir / f"ai_proposals_{stage_name}.csv", index=False, encoding="utf-8-sig")
    errors.to_csv(stage_dir / f"ai_response_errors_{stage_name}.csv", index=False, encoding="utf-8-sig")
    queue.to_csv(stage_dir / f"human_adjudication_queue_{stage_name}.csv", index=False, encoding="utf-8-sig")
    return {
        "valid_ai_proposals": int(len(proposals)),
        "response_validation_errors": int(len(errors)),
        "human_queue_rows": int(len(queue)),
    }
