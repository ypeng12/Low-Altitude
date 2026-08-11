"""Stage 4: evidence-first reports for induced transformation clusters."""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Dict, Sequence

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer

from .config import ProjectConfig
from .storage import (
    atomic_write_csv,
    atomic_write_json,
    environment_manifest,
    refuse_stale_outputs,
    sha256_file,
    sha256_json,
)


TOKEN_PATTERN = re.compile(r"[a-z0-9]+(?:'[a-z0-9]+)?", re.I)


def distinctive_phrases(
    texts: Sequence[str], labels: np.ndarray, top_n: int, max_features: int, ngram_range: tuple[int, int]
) -> Dict[int, list[tuple[str, float]]]:
    valid = labels >= 0
    if not valid.any():
        return {}
    vectorizer = CountVectorizer(
        stop_words="english",
        lowercase=True,
        ngram_range=ngram_range,
        max_features=max_features,
        token_pattern=r"(?u)\b[a-zA-Z][a-zA-Z']+\b",
    )
    matrix = vectorizer.fit_transform(np.asarray(texts, dtype=object)[valid])
    valid_labels = labels[valid]
    cluster_ids = sorted(int(label) for label in np.unique(valid_labels))
    counts = np.vstack(
        [np.asarray(matrix[valid_labels == cluster_id].sum(axis=0)).ravel() for cluster_id in cluster_ids]
    )
    term_frequency = counts / np.maximum(counts.sum(axis=1, keepdims=True), 1.0)
    inverse_document_frequency = np.log((1 + len(cluster_ids)) / (1 + (counts > 0).sum(axis=0))) + 1
    scores = term_frequency * inverse_document_frequency
    terms = vectorizer.get_feature_names_out()
    output = {}
    for row, cluster_id in enumerate(cluster_ids):
        nonzero = np.flatnonzero(counts[row] > 0)
        ranked = nonzero[np.argsort(scores[row, nonzero])[::-1]][:top_n]
        output[cluster_id] = [(str(terms[index]), float(scores[row, index])) for index in ranked]
    return output


def _short_labels(phrases: Sequence[tuple[str, float]], limit: int = 2) -> list[str]:
    output = []
    token_sets = []
    for phrase, _ in sorted(phrases, key=lambda item: (len(item[0].split()) == 1, -item[1])):
        tokens = set(phrase.split())
        if any(len(tokens & prior) / max(len(tokens | prior), 1) >= 0.6 for prior in token_sets):
            continue
        output.append(phrase)
        token_sets.append(tokens)
        if len(output) == limit:
            break
    return output


def representative_pairs(
    cluster_id: int,
    members: pd.DataFrame,
    vectors: np.ndarray,
    limit: int,
) -> pd.DataFrame:
    rows = members["pair_embedding_row"].to_numpy(dtype=np.int64)
    working = np.asarray(vectors[rows], dtype=np.float32)
    centroid = working.mean(axis=0)
    centroid = centroid / max(float(np.linalg.norm(centroid)), 1e-12)
    similarity = working @ centroid
    records = []
    seen_reviews = set()
    seen_pairs = set()
    for position in np.argsort(similarity)[::-1]:
        item = members.iloc[int(position)]
        review_id = str(item["review_id"])
        pair_signature = (
            " ".join(TOKEN_PATTERN.findall(str(item["source_span"]).casefold())),
            " ".join(TOKEN_PATTERN.findall(str(item["target_span"]).casefold())),
        )
        if review_id in seen_reviews or pair_signature in seen_pairs:
            continue
        seen_reviews.add(review_id)
        seen_pairs.add(pair_signature)
        records.append(
            {
                "cluster_id": cluster_id,
                "rank": len(records) + 1,
                "transition_id": item["transition_id"],
                "review_id": review_id,
                "sentence": item["sentence"],
                "source_span": item["source_span"],
                "source_emotion": "",
                "transition_marker": item["transition_marker"],
                "target_span": item["target_span"],
                "target_emotion": "",
                "transformation_type": "",
                "trigger_span": "",
                "actor": "",
                "mechanism": "",
                "directional_centroid_similarity": float(similarity[position]),
                "membership_probability": float(item["membership_probability"]),
                "human_annotation_status": "pending",
            }
        )
        if len(records) >= limit:
            break
    return pd.DataFrame.from_records(records)


def _expected(config: ProjectConfig) -> Dict[str, object]:
    output_dir = config.output_dir
    return {
        "stage": "transformation-cluster-reporting-v1",
        "config_sha256": sha256_json(config.raw["reporting"]),
        "assignments_sha256": sha256_file(output_dir / "clusters" / "cluster_assignments.csv"),
        "stability_sha256": sha256_file(output_dir / "clusters" / "cluster_stability.csv"),
        "candidates_sha256": sha256_file(output_dir / "candidates" / "explicit_transition_candidates.csv"),
        "vectors_sha256": sha256_file(output_dir / "pair_vectors" / "transformation_vectors.npy"),
        "stage_code_sha256": sha256_file(Path(__file__)),
    }


def run_reporting(config: ProjectConfig, force: bool = False) -> Dict[str, object]:
    output_dir = config.output_dir
    report_dir = output_dir / "reports"
    audit_dir = output_dir / "audit"
    manifest_path = output_dir / "manifests" / "stage04_reporting.json"
    required = (
        report_dir / "transformation_cluster_inventory.csv",
        report_dir / "transformation_cluster_examples.csv",
        report_dir / "transformation_cluster_review_template.csv",
        report_dir / "transformation_matrix_status.json",
        audit_dir / "noise_transition_candidates.csv",
        report_dir / "summary.json",
    )
    expected = _expected(config)
    if refuse_stale_outputs(manifest_path, expected, force):
        missing = [str(path) for path in required if not path.exists()]
        if missing:
            raise RuntimeError(f"Transformation report manifest is current but outputs are missing: {missing}")
        return {"status": "skipped"}

    assignments = pd.read_csv(output_dir / "clusters" / "cluster_assignments.csv")
    stability = pd.read_csv(output_dir / "clusters" / "cluster_stability.csv")
    candidates = pd.read_csv(output_dir / "candidates" / "explicit_transition_candidates.csv", low_memory=False)
    vectors = np.load(output_dir / "pair_vectors" / "transformation_vectors.npy", mmap_mode="r", allow_pickle=False)
    joined = assignments.merge(candidates, on=["transition_id", "review_id", "source_span_id", "target_span_id", "transition_marker", "discourse_relation_family"], validate="one_to_one")
    if len(joined) != len(assignments) or len(vectors) != len(assignments):
        raise ValueError("Transformation report inputs are misaligned")
    valid = joined.loc[joined["cluster_id"].ge(0)].copy()
    cfg = config.raw["reporting"]
    phrase_arguments = {
        "top_n": int(cfg["top_phrases"]),
        "max_features": int(cfg["max_tfidf_features"]),
        "ngram_range": tuple(int(value) for value in cfg["ngram_range"]),
    }
    source_phrases = distinctive_phrases(
        valid["source_span"].fillna("").astype(str).tolist(),
        valid["cluster_id"].to_numpy(dtype=np.int32),
        **phrase_arguments,
    )
    target_phrases = distinctive_phrases(
        valid["target_span"].fillna("").astype(str).tolist(),
        valid["cluster_id"].to_numpy(dtype=np.int32),
        **phrase_arguments,
    )

    inventory_records = []
    example_frames = []
    for cluster_id in sorted(int(value) for value in valid["cluster_id"].unique()):
        members = valid.loc[valid["cluster_id"].eq(cluster_id)].copy()
        metric = stability.loc[stability["cluster_id"].eq(cluster_id)].iloc[0]
        source = source_phrases.get(cluster_id, [])
        target = target_phrases.get(cluster_id, [])
        source_label = " | ".join(_short_labels(source)) or "unresolved source"
        target_label = " | ".join(_short_labels(target)) or "unresolved target"
        relation_counts = Counter(members["discourse_relation_family"].astype(str))
        marker_counts = Counter(members["transition_marker"].astype(str))
        dominant_relation, relation_count = relation_counts.most_common(1)[0]
        dominant_marker, marker_count = marker_counts.most_common(1)[0]
        inventory_records.append(
            {
                "cluster_id": cluster_id,
                "cluster_size": int(len(members)),
                "unique_reviews": int(members["review_id"].nunique()),
                "corpus_derived_pair_label": f"{source_label} -> {target_label}",
                "source_representative_phrases": json.dumps(source, ensure_ascii=False),
                "target_representative_phrases": json.dumps(target, ensure_ascii=False),
                "dominant_discourse_relation": dominant_relation,
                "dominant_relation_share": float(relation_count / len(members)),
                "dominant_transition_marker": dominant_marker,
                "dominant_marker_share": float(marker_count / len(members)),
                "mean_membership_probability": float(metric["mean_membership_probability"]),
                "seed_stability_jaccard": float(metric["seed_stability_jaccard"]),
                "grid_stability_jaccard": float(metric["grid_stability_jaccard"]),
                "directional_centroid_coherence": float(metric["directional_centroid_coherence"]),
                "possible_source_emotion": "",
                "possible_target_emotion": "",
                "possible_transformation_label": "",
                "possible_mechanism": "",
                "human_cluster_type": "",
                "human_review_status": "pending",
                "requires_human_review": True,
            }
        )
        example_frames.append(
            representative_pairs(cluster_id, members, vectors, int(cfg["representative_examples"]))
        )
    inventory = pd.DataFrame.from_records(inventory_records)
    examples = pd.concat(example_frames, ignore_index=True)
    review_template = inventory.copy()
    noise = joined.loc[joined["cluster_id"].lt(0)].copy()
    noise["audit_reason"] = "directional_hdbscan_noise_or_outlier"
    matrix_status = {
        "status": "pending_human_validated_emotion_labels",
        "matrix_created": False,
        "reason": "A source-emotion to target-emotion matrix cannot be validly created from unlabeled candidate clusters.",
        "candidate_pairs_retained": int(len(joined)),
    }
    summary = {
        "transformation_clusters": int(len(inventory)),
        "clustered_pairs": int(len(valid)),
        "noise_pairs": int(len(noise)),
        "representative_examples": int(len(examples)),
        "emotion_labels_filled": 0,
        "transformation_labels_filled": 0,
        "gold_standard_status": "not_created",
    }
    atomic_write_csv(inventory, report_dir / "transformation_cluster_inventory.csv")
    atomic_write_csv(examples, report_dir / "transformation_cluster_examples.csv")
    atomic_write_csv(review_template, report_dir / "transformation_cluster_review_template.csv")
    atomic_write_csv(noise, audit_dir / "noise_transition_candidates.csv")
    atomic_write_json(matrix_status, report_dir / "transformation_matrix_status.json")
    atomic_write_json(summary, report_dir / "summary.json")
    atomic_write_json(
        {"inputs": expected, "summary": summary, "environment": environment_manifest()}, manifest_path
    )
    return summary
