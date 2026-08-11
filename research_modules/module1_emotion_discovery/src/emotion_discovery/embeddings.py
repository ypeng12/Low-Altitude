"""Stage 2: contextual transformer embeddings with an auditable cache."""

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
    sha256_strings,
)


def choose_device(requested: str) -> str:
    if requested != "auto":
        return requested
    try:
        import torch
    except ImportError as exc:
        raise RuntimeError("PyTorch is required to build embeddings") from exc
    if torch.cuda.is_available():
        return "cuda"
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def _embedding_expected(config: ProjectConfig, spans: pd.DataFrame) -> Dict[str, object]:
    embedding_config = config.raw["embedding"]
    identity_hash = sha256_strings(
        f"{span_id}\x1f{text}" for span_id, text in zip(spans["span_id"], spans["span_text"])
    )
    return {
        "stage_config_sha256": sha256_json(embedding_config),
        "span_identity_sha256": identity_hash,
        "model_name": embedding_config["model_name"],
        "model_revision": embedding_config["model_revision"],
        "normalize_embeddings": bool(embedding_config["normalize_embeddings"]),
        "stage": "embedding-v1",
    }


def _token_lengths(tokenizer: object, texts: list[str], batch_size: int) -> list[int]:
    lengths: list[int] = []
    for start in range(0, len(texts), batch_size):
        encoded = tokenizer(
            texts[start : start + batch_size],
            add_special_tokens=True,
            truncation=False,
            padding=False,
            return_length=True,
        )
        batch_lengths = encoded.get("length")
        if batch_lengths is None:
            batch_lengths = [len(ids) for ids in encoded["input_ids"]]
        lengths.extend(int(length) for length in batch_lengths)
    return lengths


def run_embeddings(config: ProjectConfig, force: bool = False) -> Dict[str, object]:
    output_dir = config.output_dir
    spans_path = output_dir / "intermediate" / "analysis_spans.csv"
    if not spans_path.exists():
        raise FileNotFoundError("Run stage 01 before embeddings: analysis_spans.csv is missing")
    spans = pd.read_csv(spans_path, low_memory=False)
    if spans.empty or spans["span_id"].duplicated().any():
        raise ValueError("analysis_spans.csv must contain unique, non-empty span IDs")

    embedding_dir = output_dir / "embeddings"
    manifest_path = output_dir / "manifests" / "stage02_embeddings.json"
    embeddings_path = embedding_dir / "span_embeddings.npy"
    index_path = embedding_dir / "embedding_index.csv"
    truncation_path = output_dir / "audit" / "embedding_truncation_audit.csv"
    expected = _embedding_expected(config, spans)
    if refuse_stale_outputs(manifest_path, expected, force):
        if not embeddings_path.exists() or not index_path.exists() or not truncation_path.exists():
            raise RuntimeError("Embedding manifest is current but one or more cache files are missing")
        return {"status": "skipped"}

    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        raise RuntimeError(
            "sentence-transformers is required. Install requirements.txt in an isolated environment."
        ) from exc

    embedding_config = config.raw["embedding"]
    device = choose_device(str(embedding_config["device"]))
    backend = str(embedding_config.get("backend", "torch"))
    model_kwargs = {}
    if backend == "onnx":
        model_kwargs = {
            "provider": str(embedding_config.get("onnx_provider", "CPUExecutionProvider")),
        }
    model = SentenceTransformer(
        str(embedding_config["model_name"]),
        revision=str(embedding_config["model_revision"]),
        device=device,
        backend=backend,
        model_kwargs=model_kwargs,
    )
    texts = spans["span_text"].fillna("").astype(str).tolist()
    batch_size = int(embedding_config["batch_size"])
    token_lengths = _token_lengths(model.tokenizer, texts, batch_size)
    maximum_tokens = int(model.max_seq_length)
    truncation_mask = np.asarray(token_lengths) > maximum_tokens
    truncation_audit = spans.loc[truncation_mask, ["span_id", "review_id", "span_text"]].copy()
    truncation_audit["original_model_tokens"] = np.asarray(token_lengths)[truncation_mask]
    truncation_audit["model_max_tokens"] = maximum_tokens

    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=bool(embedding_config["show_progress_bar"]),
        convert_to_numpy=True,
        normalize_embeddings=bool(embedding_config["normalize_embeddings"]),
    )
    embeddings = np.asarray(embeddings, dtype=np.float32)
    if embeddings.ndim != 2 or embeddings.shape[0] != len(spans):
        raise RuntimeError(
            f"Unexpected embedding shape {embeddings.shape}; expected ({len(spans)}, dimensions)"
        )
    if not np.isfinite(embeddings).all():
        raise RuntimeError("Embedding array contains non-finite values")

    index = spans.loc[:, ["span_id", "review_id"]].copy()
    index.insert(0, "embedding_row", np.arange(len(index), dtype=np.int64))
    atomic_save_npy(embeddings, embeddings_path)
    atomic_write_csv(index, index_path)
    atomic_write_csv(truncation_audit, truncation_path)

    summary: Dict[str, object] = {
        "spans": int(len(spans)),
        "dimensions": int(embeddings.shape[1]),
        "dtype": str(embeddings.dtype),
        "device": device,
        "backend": backend,
        "onnx_provider": embedding_config.get("onnx_provider") if backend == "onnx" else None,
        "model_name": embedding_config["model_name"],
        "model_revision": embedding_config["model_revision"],
        "model_max_tokens": maximum_tokens,
        "truncated_spans": int(truncation_mask.sum()),
    }
    manifest = {
        "inputs": expected,
        "outputs": {
            "embedding_sha256": sha256_file(embeddings_path),
            "index_sha256": sha256_file(index_path),
        },
        "summary": summary,
        "environment": environment_manifest(config.repository_root),
    }
    atomic_write_json(manifest, manifest_path)
    return summary
