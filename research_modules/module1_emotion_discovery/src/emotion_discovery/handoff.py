"""Hard validation that cached Module 1 inputs match canonical v2."""

from __future__ import annotations

from typing import Dict

import numpy as np
import pandas as pd

from . import NRC_EMOTIONS
from .config import ProjectConfig
from .storage import atomic_write_json, sha256_file


NRC_COLUMNS = tuple(f"nrc_{emotion}" for emotion in NRC_EMOTIONS)


def validate_canonical_handoff(config: ProjectConfig) -> Dict[str, object]:
    canonical_path = config.input_path("canonical_reviews")
    corpus_path = config.output_dir / "intermediate" / "corpus_reviews.csv"
    spans_path = config.output_dir / "intermediate" / "analysis_spans.csv"
    index_path = config.output_dir / "embeddings" / "embedding_index.csv"
    embeddings_path = config.output_dir / "embeddings" / "span_embeddings.npy"
    for path in (canonical_path, corpus_path, spans_path, index_path, embeddings_path):
        if not path.exists():
            raise FileNotFoundError(f"Canonical handoff input is missing: {path}")

    canonical = pd.read_csv(
        canonical_path,
        usecols=["review_id", "analysis_language_status", *NRC_COLUMNS],
        low_memory=False,
    )
    corpus = pd.read_csv(corpus_path, usecols=["review_id", *NRC_COLUMNS], low_memory=False)
    canonical_english = canonical.loc[canonical["analysis_language_status"].eq("english")].copy()
    canonical_ids = set(canonical_english["review_id"])
    corpus_ids = set(corpus["review_id"])
    if canonical_ids != corpus_ids:
        raise ValueError(
            "Module 1 corpus does not match canonical English reviews: "
            f"missing={len(canonical_ids - corpus_ids)}, extra={len(corpus_ids - canonical_ids)}"
        )
    if corpus["review_id"].duplicated().any():
        raise ValueError("Module 1 corpus contains duplicate review_id values")

    compared = corpus.merge(
        canonical_english.loc[:, ["review_id", *NRC_COLUMNS]],
        on="review_id",
        suffixes=("_module1", "_canonical"),
        validate="one_to_one",
    )
    nrc_differences = {}
    for column in NRC_COLUMNS:
        equal = np.isclose(
            compared[f"{column}_module1"],
            compared[f"{column}_canonical"],
            equal_nan=True,
        )
        nrc_differences[column] = int((~equal).sum())
    if any(nrc_differences.values()):
        raise ValueError(f"Module 1 NRC values differ from canonical v2: {nrc_differences}")

    spans = pd.read_csv(spans_path, usecols=["span_id", "review_id"], low_memory=False)
    index = pd.read_csv(index_path, usecols=["embedding_row", "span_id", "review_id"], low_memory=False)
    embeddings = np.load(embeddings_path, mmap_mode="r", allow_pickle=False)
    if len(spans) != len(index) or len(index) != embeddings.shape[0]:
        raise ValueError("Span, embedding index, and embedding matrix row counts differ")
    if not spans["span_id"].equals(index["span_id"]):
        raise ValueError("Embedding index order differs from analysis span order")
    if spans["span_id"].duplicated().any() or index["span_id"].duplicated().any():
        raise ValueError("Duplicate span_id found in Module 1 handoff")
    outside = set(spans["review_id"]) - canonical_ids
    if outside:
        raise ValueError(f"Analysis spans include {len(outside)} non-canonical reviews")

    result = {
        "status": "valid",
        "canonical_english_reviews": int(len(canonical_ids)),
        "module1_corpus_reviews": int(len(corpus)),
        "analysis_spans": int(len(spans)),
        "embedding_rows": int(embeddings.shape[0]),
        "embedding_dimensions": int(embeddings.shape[1]),
        "nrc_differences": nrc_differences,
        "canonical_sha256": sha256_file(canonical_path),
        "corpus_sha256": sha256_file(corpus_path),
        "spans_sha256": sha256_file(spans_path),
        "embedding_index_sha256": sha256_file(index_path),
        "embeddings_sha256": sha256_file(embeddings_path),
    }
    atomic_write_json(result, config.output_dir / "audit" / "canonical_handoff_v2.json")
    return result
