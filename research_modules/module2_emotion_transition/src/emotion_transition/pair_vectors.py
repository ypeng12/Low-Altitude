"""Stage 2: reuse aligned BGE spans to represent source-to-target direction."""

from __future__ import annotations

from pathlib import Path
from typing import Dict

import numpy as np
import pandas as pd

from .config import ProjectConfig
from .storage import (
    atomic_save_npy,
    atomic_write_csv,
    atomic_write_json,
    environment_manifest,
    refuse_stale_outputs,
    sha256_file,
    sha256_json,
)


def directional_vectors(
    source: np.ndarray,
    target: np.ndarray,
    zero_tolerance: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if source.shape != target.shape or source.ndim != 2:
        raise ValueError("Source and target embedding matrices must have the same 2D shape")
    delta = np.asarray(target, dtype=np.float32) - np.asarray(source, dtype=np.float32)
    norms = np.linalg.norm(delta, axis=1).astype(np.float32)
    zero = norms <= zero_tolerance
    normalized = np.zeros_like(delta, dtype=np.float32)
    normalized[~zero] = delta[~zero] / norms[~zero, None]
    return normalized, norms, zero


def _expected(config: ProjectConfig) -> Dict[str, object]:
    candidates = config.output_dir / "candidates" / "explicit_transition_candidates.csv"
    return {
        "stage": "directional-pair-representation-v1",
        "config_sha256": sha256_json(config.raw["pair_representation"]),
        "candidates_sha256": sha256_file(candidates),
        "embedding_index_sha256": sha256_file(config.input_path("embedding_index")),
        "span_embeddings_sha256": sha256_file(config.input_path("span_embeddings")),
        "stage_code_sha256": sha256_file(Path(__file__)),
    }


def run_pair_vectors(config: ProjectConfig, force: bool = False) -> Dict[str, object]:
    output_dir = config.output_dir
    pair_dir = output_dir / "pair_vectors"
    audit_dir = output_dir / "audit"
    manifest_path = output_dir / "manifests" / "stage02_pair_vectors.json"
    required = (
        pair_dir / "pair_embedding_index.csv",
        pair_dir / "transformation_vectors.npy",
        audit_dir / "zero_norm_transformation_vectors.csv",
        pair_dir / "summary.json",
    )
    expected = _expected(config)
    if refuse_stale_outputs(manifest_path, expected, force):
        missing = [str(path) for path in required if not path.exists()]
        if missing:
            raise RuntimeError(f"Pair-vector manifest is current but outputs are missing: {missing}")
        return {"status": "skipped"}

    candidates = pd.read_csv(
        output_dir / "candidates" / "explicit_transition_candidates.csv", low_memory=False
    )
    if candidates.empty or candidates["transition_id"].duplicated().any():
        raise ValueError("Transition candidates must have unique, nonempty transition IDs")
    embedding_index = pd.read_csv(config.input_path("embedding_index"))
    if embedding_index["span_id"].duplicated().any() or embedding_index["embedding_row"].duplicated().any():
        raise ValueError("Module 1 embedding index is not one-to-one")
    row_by_span = embedding_index.set_index("span_id")["embedding_row"]
    source_rows = candidates["source_span_id"].map(row_by_span)
    target_rows = candidates["target_span_id"].map(row_by_span)
    missing = source_rows.isna() | target_rows.isna()
    if missing.any():
        raise ValueError(f"{int(missing.sum())} transition candidates lack aligned BGE embeddings")

    embeddings = np.load(config.input_path("span_embeddings"), mmap_mode="r", allow_pickle=False)
    if embeddings.ndim != 2 or len(embedding_index) != embeddings.shape[0]:
        raise ValueError("Module 1 embedding index and matrix are misaligned")
    source_row_values = source_rows.to_numpy(dtype=np.int64)
    target_row_values = target_rows.to_numpy(dtype=np.int64)
    vectors, norms, zero = directional_vectors(
        np.asarray(embeddings[source_row_values], dtype=np.float32),
        np.asarray(embeddings[target_row_values], dtype=np.float32),
        zero_tolerance=float(config.raw["pair_representation"]["zero_norm_tolerance"]),
    )
    if not np.isfinite(vectors).all():
        raise ValueError("Transformation vector matrix contains non-finite values")

    pair_index = candidates.loc[
        :,
        [
            "transition_id",
            "review_id",
            "source_span_id",
            "target_span_id",
            "transition_marker",
            "discourse_relation_family",
        ],
    ].copy()
    pair_index.insert(0, "pair_embedding_row", np.arange(len(pair_index), dtype=np.int64))
    pair_index["source_embedding_row"] = source_row_values
    pair_index["target_embedding_row"] = target_row_values
    pair_index["raw_delta_l2_norm"] = norms
    pair_index["is_zero_norm"] = zero
    zero_audit = candidates.loc[
        zero, ["transition_id", "review_id", "source_span_id", "target_span_id", "source_span", "target_span"]
    ].copy()
    zero_audit["audit_reason"] = "source_and_target_bge_embeddings_are_identical"

    summary = {
        "transition_candidates": int(len(candidates)),
        "vector_rows": int(vectors.shape[0]),
        "vector_dimensions": int(vectors.shape[1]),
        "representation": str(config.raw["pair_representation"]["representation"]),
        "zero_norm_vectors": int(zero.sum()),
        "source_target_embedding_rows_missing": 0,
    }
    atomic_write_csv(pair_index, pair_dir / "pair_embedding_index.csv")
    atomic_save_npy(vectors, pair_dir / "transformation_vectors.npy")
    atomic_write_csv(zero_audit, audit_dir / "zero_norm_transformation_vectors.csv")
    atomic_write_json(summary, pair_dir / "summary.json")
    atomic_write_json(
        {
            "inputs": expected,
            "outputs": {"transformation_vectors_sha256": sha256_file(pair_dir / "transformation_vectors.npy")},
            "summary": summary,
            "environment": environment_manifest(),
        },
        manifest_path,
    )
    return summary
