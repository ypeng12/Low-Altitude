"""Deterministic disjoint discovery sampling without affect-lexicon inputs."""

from __future__ import annotations

import hashlib
import math
import re
from collections.abc import Iterable

import numpy as np
import pandas as pd


def stable_uniform(review_id: str, seed: int) -> float:
    """Map a stable review ID and seed to a reproducible open interval (0, 1)."""

    digest = hashlib.sha256(f"{seed}|{review_id}".encode("utf-8")).digest()
    integer = int.from_bytes(digest[:8], byteorder="big", signed=False)
    return (integer + 1.0) / (2**64 + 1.0)


def aggregate_tour_links(links: pd.DataFrame) -> pd.DataFrame:
    required = {"review_id", "tour_id", "tour_name", "source_file"}
    missing = required - set(links.columns)
    if missing:
        raise ValueError(f"Tour link table is missing columns: {sorted(missing)}")

    ordered = links.sort_values(
        ["review_id", "tour_id", "tour_name", "source_file"], kind="stable"
    ).copy()
    grouped = ordered.groupby("review_id", sort=True, observed=True)
    result = grouped.agg(
        primary_tour_id=("tour_id", "first"),
        primary_tour_name=("tour_name", "first"),
        all_tour_ids=("tour_id", lambda values: "|".join(dict.fromkeys(map(str, values)))),
        all_tour_names=("tour_name", lambda values: "|".join(dict.fromkeys(map(str, values)))),
        source_files=("source_file", lambda values: "|".join(dict.fromkeys(map(str, values)))),
    )
    return result.reset_index()


def add_length_bins(frame: pd.DataFrame, edges: Iterable[int]) -> pd.DataFrame:
    result = frame.copy()
    numeric_edges = list(edges)
    if len(numeric_edges) < 2 or numeric_edges != sorted(numeric_edges):
        raise ValueError("length_bin_edges must be an ascending list with at least two values")
    labels = [f"[{left},{right})" for left, right in zip(numeric_edges[:-1], numeric_edges[1:])]
    result["length_bin"] = pd.cut(
        pd.to_numeric(result["review_word_count"], errors="coerce").fillna(0),
        bins=numeric_edges,
        labels=labels,
        right=False,
        include_lowest=True,
    ).astype("string")
    result["length_bin"] = result["length_bin"].fillna("outside_configured_range")
    return result


def balanced_weights(
    frame: pd.DataFrame,
    columns: list[str],
    strength_per_column: float,
    maximum_relative_weight: float,
) -> pd.Series:
    if not 0 <= strength_per_column <= 1:
        raise ValueError("balance_strength_per_column must fall in [0, 1]")
    if maximum_relative_weight < 1:
        raise ValueError("maximum_relative_weight must be at least 1")

    weights = pd.Series(1.0, index=frame.index, dtype=float)
    total = float(len(frame))
    for column in columns:
        if column not in frame:
            raise ValueError(f"Sampling balance column does not exist: {column}")
        values = frame[column].astype("string").fillna("<MISSING>")
        counts = values.value_counts(dropna=False)
        category_count = max(len(counts), 1)
        factor = values.map(
            lambda value: (total / (category_count * float(counts[value]))) ** strength_per_column
        ).astype(float)
        weights *= factor

    median = float(weights.median())
    if not math.isfinite(median) or median <= 0:
        raise ValueError("Sampling weights have a non-positive or invalid median")
    weights /= median
    return weights.clip(lower=1.0 / maximum_relative_weight, upper=maximum_relative_weight)


def make_disjoint_sample_manifest(
    reviews: pd.DataFrame,
    tour_links: pd.DataFrame,
    *,
    seed: int,
    stages: list[dict[str, object]],
    balance_columns: list[str],
    balance_strength_per_column: float,
    maximum_relative_weight: float,
    length_bin_edges: list[int],
) -> pd.DataFrame:
    if reviews["review_id"].duplicated().any():
        raise ValueError("Canonical review IDs must be unique")
    if not stages:
        raise ValueError("At least one disjoint sampling stage is required")
    names = [str(stage["name"]) for stage in stages]
    sizes = [int(stage["size"]) for stage in stages]
    if len(names) != len(set(names)):
        raise ValueError("Disjoint sampling stage names must be unique")
    if any(not re.fullmatch(r"[a-z0-9_]+", name) for name in names):
        raise ValueError("Stage names may contain only lowercase letters, digits, and underscores")
    if any(size <= 0 for size in sizes) or sum(sizes) > len(reviews):
        raise ValueError("Disjoint stage sizes must be positive and their sum cannot exceed the corpus")

    tours = aggregate_tour_links(tour_links)
    result = reviews.merge(tours, on="review_id", how="left", validate="one_to_one")
    result["primary_tour_id"] = result["primary_tour_id"].fillna("unresolved_tour")
    result["primary_tour_name"] = result["primary_tour_name"].fillna("Unresolved tour")
    for column in ["all_tour_ids", "all_tour_names", "source_files"]:
        result[column] = result[column].fillna("")
    result["aircraft_type"] = result["aircraft_type"].fillna("Other/Unspecified")
    result = add_length_bins(result, length_bin_edges)

    result["sampling_weight"] = balanced_weights(
        result,
        balance_columns,
        balance_strength_per_column,
        maximum_relative_weight,
    )
    result["stable_uniform"] = result["review_id"].map(lambda value: stable_uniform(str(value), seed))
    result["selection_priority"] = -np.log(result["stable_uniform"]) / result["sampling_weight"]
    result = result.sort_values(["selection_priority", "review_id"], kind="stable").reset_index(drop=True)
    result["sampling_rank"] = np.arange(1, len(result) + 1, dtype=int)
    stage_start = 1
    for name, size in zip(names, sizes):
        stage_end = stage_start + size - 1
        result[f"in_{name}"] = result["sampling_rank"].between(
            stage_start, stage_end, inclusive="both"
        )
        stage_start = stage_end + 1
    result[f"in_manually_studied_{sum(sizes)}"] = result["sampling_rank"].lt(stage_start)
    result["in_full_english_corpus"] = True
    return result
