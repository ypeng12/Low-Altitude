"""Post-cluster GoEmotions profiles for human review.

GoEmotions is intentionally applied only after corpus-driven clustering. Its
fixed labels are reference signals, not discovered labels, gold annotations, or
an automatic way to select the final three domain emotions.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, Iterable, Sequence

import numpy as np
import pandas as pd

from .config import ProjectConfig
from .storage import (
    atomic_write_csv,
    atomic_write_json,
    environment_manifest,
    refuse_stale_outputs,
    sha256_file,
    sha256_json,
)


PROBABILITY_PREFIX = "goemotions_probability_"


def sigmoid(logits: np.ndarray) -> np.ndarray:
    """Numerically stable independent-label probabilities."""

    clipped = np.clip(np.asarray(logits, dtype=np.float64), -50.0, 50.0)
    return (1.0 / (1.0 + np.exp(-clipped))).astype(np.float32)


def top_label_payload(probabilities: Sequence[float], labels: Sequence[str], limit: int) -> str:
    """Return a deterministic display payload without treating it as a label decision."""

    values = np.asarray(probabilities, dtype=np.float64)
    ranked = np.argsort(values, kind="stable")[::-1][:limit]
    return json.dumps(
        [{"reference_label": labels[index], "probability": round(float(values[index]), 8)} for index in ranked],
        ensure_ascii=False,
    )


def aggregate_cluster_profiles(
    linked_probabilities: pd.DataFrame,
    labels: Sequence[str],
    display_labels: int,
) -> pd.DataFrame:
    """Aggregate continuous reference probabilities by clustering view and cluster."""

    probability_columns = [f"{PROBABILITY_PREFIX}{label}" for label in labels]
    records = []
    for (view, cluster_id), group in linked_probabilities.groupby(
        ["discovery_view", "cluster_id"], sort=True
    ):
        means = group[probability_columns].mean().to_numpy(dtype=np.float64)
        top_label = labels[int(np.argmax(means))]
        row_top = group[probability_columns].to_numpy().argmax(axis=1)
        records.append(
            {
                "discovery_view": view,
                "cluster_id": int(cluster_id),
                "reference_examples": int(len(group)),
                "goemotions_profile_top_labels": top_label_payload(means, labels, display_labels),
                "goemotions_profile_max_probability": float(means.max()),
                "goemotions_top_label_agreement": float(
                    np.mean(row_top == labels.index(top_label))
                ),
                **{column: float(value) for column, value in zip(probability_columns, means)},
            }
        )
    return pd.DataFrame.from_records(records)


def collect_reference_examples(output_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Collect cluster-example links and a deduplicated inference table."""

    inputs = {
        "full_unsupervised": output_dir / "reports" / "cluster_representative_examples.csv",
        "cate_focused": output_dir / "focused" / "cluster_representative_examples.csv",
    }
    frames = []
    required = {"cluster_id", "rank", "span_id", "review_id", "span_text"}
    for view, path in inputs.items():
        frame = pd.read_csv(path, low_memory=False)
        missing = required - set(frame.columns)
        if missing:
            raise ValueError(f"Reference examples missing columns in {path}: {sorted(missing)}")
        selected = frame.loc[:, sorted(required)].copy()
        selected.insert(0, "discovery_view", view)
        frames.append(selected)
    links = pd.concat(frames, ignore_index=True)
    links["span_text"] = links["span_text"].fillna("").astype(str).str.strip()
    if links["span_id"].isna().any() or links["span_text"].eq("").any():
        raise ValueError("GoEmotions reference inputs contain missing IDs or empty span text")
    inconsistent = links.groupby("span_id")["span_text"].nunique().gt(1)
    if inconsistent.any():
        raise ValueError("The same span_id is associated with different text")
    inference = (
        links.sort_values(["span_id", "discovery_view", "cluster_id", "rank"], kind="stable")
        .drop_duplicates("span_id")
        .loc[:, ["span_id", "review_id", "span_text"]]
        .reset_index(drop=True)
    )
    return links, inference


def _expected(config: ProjectConfig) -> Dict[str, object]:
    output_dir = config.output_dir
    return {
        "stage": "goemotions-post-cluster-reference-v1",
        "config_sha256": sha256_json(config.raw["goemotions_reference"]),
        "full_examples_sha256": sha256_file(
            output_dir / "reports" / "cluster_representative_examples.csv"
        ),
        "focused_examples_sha256": sha256_file(
            output_dir / "focused" / "cluster_representative_examples.csv"
        ),
        "stage_code_sha256": sha256_file(Path(__file__)),
    }


def _load_model(configuration: Dict[str, object]):
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
    try:
        import onnxruntime as ort
        from huggingface_hub import hf_hub_download
        from transformers import AutoTokenizer
    except ImportError as exc:
        raise RuntimeError("transformers, huggingface-hub, and onnxruntime are required") from exc

    repository = str(configuration["model_name"])
    revision = str(configuration["model_revision"])
    model_path = Path(
        hf_hub_download(
            repository,
            filename=str(configuration["onnx_filename"]),
            revision=revision,
        )
    )
    config_path = Path(hf_hub_download(repository, filename="config.json", revision=revision))
    with config_path.open("r", encoding="utf-8") as handle:
        model_config = json.load(handle)
    labels_by_id = {int(key): str(value) for key, value in model_config["id2label"].items()}
    labels = [labels_by_id[index] for index in range(len(labels_by_id))]
    if len(labels) != 28 or "neutral" not in labels:
        raise ValueError("Pinned GoEmotions model does not expose the expected 28 outputs")

    tokenizer = AutoTokenizer.from_pretrained(repository, revision=revision)
    options = ort.SessionOptions()
    options.intra_op_num_threads = int(configuration["intra_op_num_threads"])
    session = ort.InferenceSession(
        str(model_path),
        sess_options=options,
        providers=[str(configuration["provider"])],
    )
    return tokenizer, session, labels, model_path


def _infer_probabilities(
    texts: Sequence[str],
    tokenizer: object,
    session: object,
    batch_size: int,
    max_length: int,
) -> tuple[np.ndarray, np.ndarray]:
    raw_lengths = np.asarray(
        [len(tokenizer(text, add_special_tokens=True, truncation=False)["input_ids"]) for text in texts],
        dtype=np.int32,
    )
    input_names = {value.name for value in session.get_inputs()}
    batches = []
    for start in range(0, len(texts), batch_size):
        encoded = tokenizer(
            list(texts[start : start + batch_size]),
            padding=True,
            truncation=True,
            max_length=max_length,
            return_tensors="np",
        )
        inputs = {
            name: np.asarray(encoded[name], dtype=np.int64)
            for name in input_names
            if name in encoded
        }
        if set(inputs) != input_names:
            raise ValueError(f"Tokenizer did not produce all ONNX inputs: {sorted(input_names - set(inputs))}")
        logits = np.asarray(session.run(None, inputs)[0])
        batches.append(sigmoid(logits))
    probabilities = np.vstack(batches)
    return probabilities, raw_lengths


def run_goemotions_reference(config: ProjectConfig, force: bool = False) -> Dict[str, object]:
    """Create a reproducible post-cluster reference view for human reviewers."""

    output_dir = config.output_dir
    reference_dir = output_dir / "reference" / "goemotions"
    audit_dir = output_dir / "audit"
    manifest_path = output_dir / "manifests" / "stage06_goemotions_reference.json"
    required = (
        reference_dir / "span_probabilities.csv",
        reference_dir / "reference_example_links.csv",
        reference_dir / "cluster_profiles.csv",
        reference_dir / "summary.json",
        audit_dir / "goemotions_truncation_audit.csv",
    )
    expected = _expected(config)
    if refuse_stale_outputs(manifest_path, expected, force):
        missing = [str(path) for path in required if not path.exists()]
        if missing:
            raise RuntimeError(f"GoEmotions manifest is current but outputs are missing: {missing}")
        return {"status": "skipped"}

    configuration = config.raw["goemotions_reference"]
    links, inference = collect_reference_examples(output_dir)
    tokenizer, session, labels, model_path = _load_model(configuration)
    probabilities, raw_lengths = _infer_probabilities(
        inference["span_text"].tolist(),
        tokenizer,
        session,
        int(configuration["batch_size"]),
        int(configuration["max_length"]),
    )
    if probabilities.shape != (len(inference), len(labels)):
        raise ValueError(f"Unexpected GoEmotions probability shape: {probabilities.shape}")

    probability_columns = [f"{PROBABILITY_PREFIX}{label}" for label in labels]
    scores = inference.copy()
    for index, column in enumerate(probability_columns):
        scores[column] = probabilities[:, index]
    display_labels = int(configuration["profile_display_labels"])
    scores["goemotions_reference_top_labels"] = [
        top_label_payload(row, labels, display_labels) for row in probabilities
    ]
    scores["goemotions_reference_max_probability"] = probabilities.max(axis=1)

    linked = links.merge(
        scores.drop(columns=["review_id", "span_text"]),
        on="span_id",
        how="left",
        validate="many_to_one",
    )
    if linked[probability_columns].isna().any().any():
        raise ValueError("Some reference examples did not receive GoEmotions probabilities")
    profiles = aggregate_cluster_profiles(linked, labels, display_labels)

    truncation = inference.loc[:, ["span_id", "review_id"]].copy()
    truncation["raw_model_tokens"] = raw_lengths
    truncation["configured_max_length"] = int(configuration["max_length"])
    truncation["was_truncated"] = raw_lengths > int(configuration["max_length"])
    truncation["audit_disposition"] = np.where(
        truncation["was_truncated"], "retained_with_model_truncation", "retained_without_truncation"
    )

    summary = {
        "role": str(configuration["role"]),
        "model_name": str(configuration["model_name"]),
        "model_revision": str(configuration["model_revision"]),
        "model_file_sha256": sha256_file(model_path),
        "fixed_reference_outputs": labels,
        "cluster_example_links": int(len(links)),
        "unique_inference_spans": int(len(inference)),
        "cluster_profiles": int(len(profiles)),
        "truncated_spans": int(truncation["was_truncated"].sum()),
        "interpretation_warning": (
            "Continuous GoEmotions probabilities are post-cluster reference signals only; "
            "they are not discovered emotions, gold labels, or automatic +3 decisions."
        ),
    }
    atomic_write_csv(scores, reference_dir / "span_probabilities.csv")
    atomic_write_csv(linked, reference_dir / "reference_example_links.csv")
    atomic_write_csv(profiles, reference_dir / "cluster_profiles.csv")
    atomic_write_csv(truncation, audit_dir / "goemotions_truncation_audit.csv")
    atomic_write_json(summary, reference_dir / "summary.json")
    atomic_write_json(
        {"inputs": expected, "summary": summary, "environment": environment_manifest(config.repository_root)},
        manifest_path,
    )
    return summary
