"""Second-pass discovery in the approved CATE-derived appraisal subset.

This stage does not treat CATE categories as emotion labels. The sole approved
107-word workbook selects a broad domain-appraisal pool only after the first
fully unsupervised semantic clustering has been obtained.
"""

from __future__ import annotations

import itertools
import json
import re
from collections import Counter
from pathlib import Path
from typing import Dict, Iterable, List, Sequence

import numpy as np
import pandas as pd
from sklearn.cluster import HDBSCAN
from sklearn.decomposition import PCA

from .clustering import _group_stability, _normalize_series, _safe_silhouette, best_jaccard
from .config import ProjectConfig
from .reporting import _distinct_label_phrases, _representatives, cluster_distinctive_phrases
from .storage import (
    atomic_save_npy,
    atomic_save_npz,
    atomic_write_csv,
    atomic_write_json,
    environment_manifest,
    refuse_stale_outputs,
    sha256_file,
    sha256_json,
)


CATE_WORD_COLUMN = "英文单词 (Pure Word)"


def build_cate_pattern(terms: Sequence[str]) -> re.Pattern[str]:
    cleaned = sorted({term.strip().casefold() for term in terms if term.strip()}, key=len, reverse=True)
    if not cleaned:
        raise ValueError("Approved CATE workbook contains no usable English terms")
    return re.compile(r"\b(?:" + "|".join(re.escape(term) for term in cleaned) + r")\b", re.I)


def match_cate_terms(text: object, pattern: re.Pattern[str]) -> list[str]:
    value = text if isinstance(text, str) else ""
    return sorted({match.group(0).casefold() for match in pattern.finditer(value)})


def _load_approved_cate(path: Path) -> tuple[pd.DataFrame, re.Pattern[str]]:
    if path.name != "cate_words_curated_107_translated.xlsx":
        raise ValueError(f"Unapproved CATE source: {path.name}")
    frame = pd.read_excel(path, sheet_name="Sheet1", engine="openpyxl")
    if len(frame) != 107 or CATE_WORD_COLUMN not in frame.columns:
        raise ValueError("Approved CATE workbook must contain exactly 107 rows and the English word column")
    words = frame[CATE_WORD_COLUMN].astype(str).str.strip()
    if words.eq("").any() or words.duplicated().any():
        raise ValueError("Approved CATE English terms must be nonempty and unique")
    return frame, build_cate_pattern(words.tolist())


def _expected(config: ProjectConfig) -> Dict[str, object]:
    return {
        "stage": "focused-discovery-v1",
        "config_sha256": sha256_json(config.raw["focused_discovery"]),
        "cate_sha256": sha256_file(config.input_path("cate_workbook")),
        "spans_sha256": sha256_file(config.output_dir / "intermediate" / "analysis_spans.csv"),
        "embedding_index_sha256": sha256_file(config.output_dir / "embeddings" / "embedding_index.csv"),
        "embeddings_sha256": sha256_file(config.output_dir / "embeddings" / "span_embeddings.npy"),
    }


def run_focused_discovery(config: ProjectConfig, force: bool = False) -> Dict[str, object]:
    output_dir = config.output_dir
    focused_dir = output_dir / "focused"
    audit_dir = output_dir / "audit"
    manifest_path = output_dir / "manifests" / "stage05_focused_discovery.json"
    required = (
        focused_dir / "candidate_spans.csv",
        focused_dir / "experiment_metrics.csv",
        focused_dir / "configuration_summary.csv",
        focused_dir / "cluster_assignments.csv",
        focused_dir / "cluster_stability.csv",
        focused_dir / "cluster_inventory.csv",
        focused_dir / "cluster_representative_examples.csv",
        audit_dir / "focused_noise_spans.csv",
    )
    expected = _expected(config)
    if refuse_stale_outputs(manifest_path, expected, force):
        missing = [str(path) for path in required if not path.exists()]
        if missing:
            raise RuntimeError(f"Focused manifest is current but outputs are missing: {missing}")
        return {"status": "skipped"}

    _, cate_pattern = _load_approved_cate(config.input_path("cate_workbook"))
    spans = pd.read_csv(output_dir / "intermediate" / "analysis_spans.csv", low_memory=False)
    matched = spans["span_text"].map(lambda text: match_cate_terms(text, cate_pattern))
    candidate = spans.loc[matched.map(bool)].copy()
    candidate["matched_cate_terms"] = matched.loc[candidate.index].map(lambda values: "|".join(values))
    if candidate.empty:
        raise RuntimeError("Approved CATE selector produced no candidate spans")

    index = pd.read_csv(output_dir / "embeddings" / "embedding_index.csv")
    candidate = candidate.merge(
        index.loc[:, ["embedding_row", "span_id", "review_id"]],
        on=["span_id", "review_id"],
        how="left",
        validate="one_to_one",
    )
    if candidate["embedding_row"].isna().any():
        raise ValueError("Focused candidate spans are missing embedding rows")
    candidate = candidate.sort_values("embedding_row", kind="stable").reset_index(drop=True)
    embeddings = np.load(output_dir / "embeddings" / "span_embeddings.npy", mmap_mode="r", allow_pickle=False)
    rows = candidate["embedding_row"].to_numpy(dtype=np.int64)
    working = np.asarray(embeddings[rows], dtype=np.float32)
    atomic_write_csv(candidate, focused_dir / "candidate_spans.csv")

    cfg = config.raw["focused_discovery"]
    components = min(int(cfg["pca_components"]), working.shape[1], len(working) - 1)
    pca = PCA(n_components=components, svd_solver="randomized", random_state=config.random_seed)
    pca_embeddings = pca.fit_transform(working).astype(np.float32)
    cache_key = sha256_json({"inputs": expected, "candidate_span_ids": candidate["span_id"].tolist()})[:16]
    cache_dir = focused_dir / "cache" / cache_key
    atomic_save_npy(pca_embeddings, cache_dir / "pca.npy")

    try:
        import umap
    except ImportError as exc:
        raise RuntimeError("umap-learn is required for focused discovery") from exc

    run_labels: Dict[str, np.ndarray] = {}
    run_probabilities: Dict[str, np.ndarray] = {}
    reductions: Dict[int, np.ndarray] = {}
    run_groups: Dict[str, List[str]] = {}
    metric_records = []
    for seed in cfg["experiment_seeds"]:
        seed = int(seed)
        reduction_path = cache_dir / f"umap_seed{seed}.npy"
        if reduction_path.exists() and not force:
            reduced = np.load(reduction_path, allow_pickle=False)
        else:
            reducer = umap.UMAP(
                n_neighbors=int(cfg["umap_n_neighbors"]),
                n_components=int(cfg["umap_components"]),
                min_dist=float(cfg["umap_min_dist"]),
                metric=str(cfg["umap_metric"]),
                random_state=seed,
                transform_seed=seed,
                n_jobs=1,
            )
            reduced = reducer.fit_transform(pca_embeddings).astype(np.float32)
            atomic_save_npy(reduced, reduction_path)
        if reduced.shape != (len(candidate), int(cfg["umap_components"])):
            raise ValueError(f"Focused UMAP cache has unexpected shape: {reduced.shape}")
        reductions[seed] = reduced

        for min_cluster_size, min_samples in itertools.product(cfg["min_cluster_size"], cfg["min_samples"]):
            group_id = f"mcs{int(min_cluster_size)}_ms{int(min_samples)}"
            run_id = f"{group_id}_seed{seed}"
            run_path = cache_dir / f"{run_id}.npz"
            if run_path.exists() and not force:
                cached = np.load(run_path, allow_pickle=False)
                labels = cached["labels"]
                probabilities = cached["probabilities"]
            else:
                estimator = HDBSCAN(
                    min_cluster_size=int(min_cluster_size),
                    min_samples=int(min_samples),
                    metric="euclidean",
                    cluster_selection_method=str(cfg["cluster_selection_method"]),
                    n_jobs=-1,
                    copy=True,
                )
                labels = estimator.fit_predict(reduced).astype(np.int32)
                probabilities = np.asarray(estimator.probabilities_, dtype=np.float32)
                atomic_save_npz(run_path, labels=labels, probabilities=probabilities)
            run_labels[run_id] = labels
            run_probabilities[run_id] = probabilities
            run_groups.setdefault(group_id, []).append(run_id)
            valid = labels >= 0
            metric_records.append(
                {
                    "run_id": run_id,
                    "group_id": group_id,
                    "seed": seed,
                    "min_cluster_size": int(min_cluster_size),
                    "min_samples": int(min_samples),
                    "n_clusters": int(len(np.unique(labels[valid]))),
                    "noise_fraction": float((~valid).mean()),
                    "mean_membership_probability": float(probabilities[valid].mean()) if valid.any() else 0.0,
                    "silhouette": _safe_silhouette(reduced, labels, int(cfg["silhouette_sample_size"]), seed),
                }
            )

    metrics = pd.DataFrame.from_records(metric_records)
    groups = []
    for group_id, run_ids in run_groups.items():
        values = metrics.loc[metrics["group_id"].eq(group_id)]
        first = values.iloc[0]
        groups.append(
            {
                "group_id": group_id,
                "min_cluster_size": int(first["min_cluster_size"]),
                "min_samples": int(first["min_samples"]),
                "mean_n_clusters": float(values["n_clusters"].mean()),
                "mean_noise_fraction": float(values["noise_fraction"].mean()),
                "mean_coverage": float(1 - values["noise_fraction"].mean()),
                "mean_membership_probability": float(values["mean_membership_probability"].mean()),
                "mean_silhouette": float(values["silhouette"].mean()),
                "seed_adjusted_rand": _group_stability(run_labels, run_ids),
            }
        )
    configurations = pd.DataFrame.from_records(groups)
    configurations["selection_score"] = (
        0.35 * _normalize_series(configurations["seed_adjusted_rand"])
        + 0.20 * _normalize_series(configurations["mean_coverage"])
        + 0.20 * _normalize_series(configurations["mean_membership_probability"])
        + 0.25 * _normalize_series(configurations["mean_silhouette"])
    )
    selected_group = str(
        configurations.loc[configurations["mean_n_clusters"].ge(2)]
        .sort_values("selection_score", ascending=False)
        .iloc[0]["group_id"]
    )
    selected_runs = run_groups[selected_group]
    canonical_run = next((run_id for run_id in selected_runs if run_id.endswith(f"seed{config.random_seed}")), selected_runs[0])
    labels = run_labels[canonical_run]
    probabilities = run_probabilities[canonical_run]
    canonical_seed = int(canonical_run.rsplit("seed", 1)[1])

    stability_records = []
    for cluster_id in sorted(int(value) for value in np.unique(labels) if value >= 0):
        members = labels == cluster_id
        stability_records.append(
            {
                "cluster_id": cluster_id,
                "cluster_size": int(members.sum()),
                "mean_membership_probability": float(probabilities[members].mean()),
                "seed_stability_jaccard": float(
                    np.mean([best_jaccard(members, run_labels[run]) for run in selected_runs if run != canonical_run])
                ),
                "grid_stability_jaccard": float(
                    np.mean([best_jaccard(members, values) for run, values in run_labels.items() if run != canonical_run])
                ),
                "centroid_coherence": float(np.mean(working[members] @ (working[members].mean(axis=0) / max(np.linalg.norm(working[members].mean(axis=0)), 1e-12)))),
            }
        )
    stability = pd.DataFrame.from_records(stability_records)

    assignments = candidate.loc[:, ["embedding_row", "span_id", "review_id", "matched_cate_terms"]].copy()
    assignments["cluster_id"] = labels
    assignments["membership_probability"] = probabilities
    assignments["is_noise"] = labels < 0
    assignments["umap_1"] = reductions[canonical_seed][:, 0]
    assignments["umap_2"] = reductions[canonical_seed][:, 1]

    valid = assignments.loc[assignments["cluster_id"].ge(0)].merge(
        candidate.loc[:, ["span_id", "review_id", "span_text", "unit_type", "marker_before"]],
        on=["span_id", "review_id"],
        validate="one_to_one",
    )
    phrases = cluster_distinctive_phrases(
        valid["span_text"].fillna("").astype(str).tolist(),
        valid["cluster_id"].to_numpy(dtype=np.int32),
        top_n=int(cfg["top_phrases"]),
        max_features=int(cfg["max_tfidf_features"]),
        ngram_range=tuple(int(value) for value in cfg["ngram_range"]),
    )
    inventory_records = []
    representatives = []
    for cluster_id in sorted(int(value) for value in valid["cluster_id"].unique()):
        members = valid.loc[valid["cluster_id"].eq(cluster_id)].copy()
        phrase_rows = phrases.get(cluster_id, [])
        label = " | ".join(_distinct_label_phrases(phrase_rows)) or "unresolved corpus cluster"
        term_counts = Counter(term for value in members["matched_cate_terms"] for term in str(value).split("|") if term)
        metric = stability.loc[stability["cluster_id"].eq(cluster_id)].iloc[0]
        inventory_records.append(
            {
                "cluster_id": cluster_id,
                "cluster_size": int(len(members)),
                "unique_reviews": int(members["review_id"].nunique()),
                "corpus_derived_phrase_label": label,
                "representative_words_phrases": json.dumps([{"phrase": p, "score": round(v, 8)} for p, v in phrase_rows], ensure_ascii=False),
                "representative_cate_terms": json.dumps(term_counts.most_common(15), ensure_ascii=False),
                "mean_membership_probability": float(metric["mean_membership_probability"]),
                "seed_stability_jaccard": float(metric["seed_stability_jaccard"]),
                "grid_stability_jaccard": float(metric["grid_stability_jaccard"]),
                "centroid_coherence": float(metric["centroid_coherence"]),
                "human_cluster_type": "",
                "possible_fine_grained_emotion_label": "",
                "human_review_status": "pending",
            }
        )
        representatives.append(_representatives(cluster_id, members, embeddings, int(cfg["representative_examples"])))
    inventory = pd.DataFrame.from_records(inventory_records)
    representative_output = pd.concat(representatives, ignore_index=True)
    noise = candidate.loc[labels < 0, ["span_id", "review_id", "span_text", "matched_cate_terms"]].copy()
    noise["audit_reason"] = "focused_hdbscan_noise_or_outlier"

    atomic_write_csv(metrics, focused_dir / "experiment_metrics.csv")
    atomic_write_csv(configurations, focused_dir / "configuration_summary.csv")
    atomic_write_csv(assignments, focused_dir / "cluster_assignments.csv")
    atomic_write_csv(stability, focused_dir / "cluster_stability.csv")
    atomic_write_csv(inventory, focused_dir / "cluster_inventory.csv")
    atomic_write_csv(representative_output, focused_dir / "cluster_representative_examples.csv")
    atomic_write_csv(noise, audit_dir / "focused_noise_spans.csv")

    summary = {
        "selector": str(cfg["selector"]),
        "cate_terms": 107,
        "source_spans": int(len(spans)),
        "candidate_spans": int(len(candidate)),
        "candidate_reviews": int(candidate["review_id"].nunique()),
        "experiment_runs": int(len(metrics)),
        "selected_group": selected_group,
        "canonical_run": canonical_run,
        "clusters": int(len(inventory)),
        "clustered_spans": int((labels >= 0).sum()),
        "noise_spans": int((labels < 0).sum()),
        "human_review_required": True,
    }
    atomic_write_json(summary, focused_dir / "summary.json")
    atomic_write_json(
        {"inputs": expected, "summary": summary, "environment": environment_manifest(config.repository_root)},
        manifest_path,
    )
    return summary
