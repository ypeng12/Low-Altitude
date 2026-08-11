"""Stage 3: UMAP/HDBSCAN experiments and cluster stability analysis."""

from __future__ import annotations

import itertools
import json
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

import numpy as np
import pandas as pd
from sklearn.cluster import HDBSCAN
from sklearn.decomposition import PCA
from sklearn.metrics import adjusted_rand_score, silhouette_score

from .config import ProjectConfig
from .storage import (
    atomic_save_npy,
    atomic_save_npz,
    atomic_write_csv,
    atomic_write_json,
    environment_manifest,
    refuse_stale_outputs,
    sha256_file,
    sha256_json,
    sha256_strings,
)


def best_jaccard(reference_members: np.ndarray, labels: np.ndarray) -> float:
    """Best Jaccard overlap between a reference cluster and another partition."""

    if reference_members.dtype != bool:
        reference_members = reference_members.astype(bool)
    if not reference_members.any():
        return 0.0
    best = 0.0
    for candidate in np.unique(labels):
        if candidate < 0:
            continue
        candidate_members = labels == candidate
        union = np.logical_or(reference_members, candidate_members).sum()
        if union:
            overlap = np.logical_and(reference_members, candidate_members).sum() / union
            best = max(best, float(overlap))
    return best


def _safe_silhouette(
    reduced: np.ndarray,
    labels: np.ndarray,
    sample_size: int,
    seed: int,
) -> float:
    valid = np.flatnonzero(labels >= 0)
    unique = np.unique(labels[valid]) if len(valid) else np.asarray([])
    if len(unique) < 2 or len(valid) <= len(unique):
        return float("nan")
    if len(valid) > sample_size:
        rng = np.random.default_rng(seed)
        valid = np.sort(rng.choice(valid, size=sample_size, replace=False))
    try:
        return float(silhouette_score(reduced[valid], labels[valid], metric="euclidean"))
    except ValueError:
        return float("nan")


def _group_stability(run_labels: Dict[str, np.ndarray], run_ids: Sequence[str]) -> float:
    scores = [
        adjusted_rand_score(run_labels[left], run_labels[right])
        for left, right in itertools.combinations(run_ids, 2)
    ]
    return float(np.mean(scores)) if scores else 1.0


def _normalize_series(series: pd.Series) -> pd.Series:
    finite = series.replace([np.inf, -np.inf], np.nan)
    minimum = finite.min()
    maximum = finite.max()
    if pd.isna(minimum) or pd.isna(maximum) or maximum <= minimum:
        return pd.Series(np.full(len(series), 0.5), index=series.index)
    return (finite.fillna(minimum) - minimum) / (maximum - minimum)


def _cluster_expected(config: ProjectConfig) -> Dict[str, object]:
    embeddings_path = config.output_dir / "embeddings" / "span_embeddings.npy"
    index_path = config.output_dir / "embeddings" / "embedding_index.csv"
    return {
        "stage_config_sha256": sha256_json(
            {"random_seed": config.random_seed, "clustering": config.raw["clustering"]}
        ),
        "embedding_sha256": sha256_file(embeddings_path),
        "embedding_index_sha256": sha256_file(index_path),
        "stage": "clustering-v1",
    }


def _deterministic_sample_indices(total: int, maximum: int | None, seed: int) -> np.ndarray:
    if maximum is None or maximum >= total:
        return np.arange(total, dtype=np.int64)
    if maximum <= 0:
        raise ValueError("max_analysis_spans must be positive or null")
    rng = np.random.default_rng(seed)
    return np.sort(rng.choice(total, size=maximum, replace=False)).astype(np.int64)


def run_clustering(config: ProjectConfig, force: bool = False) -> Dict[str, object]:
    output_dir = config.output_dir
    embeddings_path = output_dir / "embeddings" / "span_embeddings.npy"
    index_path = output_dir / "embeddings" / "embedding_index.csv"
    spans_path = output_dir / "intermediate" / "analysis_spans.csv"
    for path in (embeddings_path, index_path, spans_path):
        if not path.exists():
            raise FileNotFoundError(f"Run earlier stages first; missing {path}")

    expected = _cluster_expected(config)
    cluster_dir = output_dir / "clusters"
    audit_dir = output_dir / "audit"
    manifest_path = output_dir / "manifests" / "stage03_clustering.json"
    required_outputs = (
        cluster_dir / "cluster_assignments.csv",
        cluster_dir / "cluster_stability.csv",
        cluster_dir / "experiment_metrics.csv",
        cluster_dir / "configuration_summary.csv",
        cluster_dir / "experiment_arrays.npz",
        audit_dir / "clustering_not_sampled.csv",
    )
    if refuse_stale_outputs(manifest_path, expected, force):
        missing = [str(path) for path in required_outputs if not path.exists()]
        if missing:
            raise RuntimeError(f"Clustering manifest is current but outputs are missing: {missing}")
        return {"status": "skipped"}

    embeddings = np.load(embeddings_path, allow_pickle=False)
    index = pd.read_csv(index_path)
    spans = pd.read_csv(spans_path, usecols=["span_id", "review_id"])
    if embeddings.shape[0] != len(index) or len(index) != len(spans):
        raise ValueError("Embedding, index, and span row counts do not match")
    if not index["span_id"].equals(spans["span_id"]):
        raise ValueError("Embedding index is not aligned with analysis_spans.csv")

    cluster_config = config.raw["clustering"]
    maximum = cluster_config.get("max_analysis_spans")
    maximum = int(maximum) if maximum is not None else None
    selected_rows = _deterministic_sample_indices(len(index), maximum, config.random_seed)
    selected_set = set(selected_rows.tolist())
    not_sampled = index.loc[
        [row not in selected_set for row in range(len(index))],
        ["embedding_row", "span_id", "review_id"],
    ].copy()
    not_sampled["exclusion_reason"] = "deterministic_clustering_sample_limit"
    atomic_write_csv(not_sampled, audit_dir / "clustering_not_sampled.csv")
    working = np.asarray(embeddings[selected_rows], dtype=np.float32)
    working_index = index.iloc[selected_rows].reset_index(drop=True)
    cache_key = sha256_json(
        {
            "inputs": expected,
            "selected_span_ids_sha256": sha256_strings(working_index["span_id"].astype(str)),
        }
    )[:16]
    cache_dir = cluster_dir / "cache" / cache_key
    cache_counts = {"pca": 0, "umap": 0, "hdbscan": 0}

    pca_components = min(
        int(cluster_config["pca_components"]),
        working.shape[1],
        max(1, working.shape[0] - 1),
    )
    pca_path = cache_dir / "pca.npz"
    if pca_path.exists() and not force:
        cached_pca = np.load(pca_path, allow_pickle=False)
        pca_embeddings = cached_pca["embeddings"]
        pca_explained_variance_ratio = cached_pca["explained_variance_ratio"]
        cache_counts["pca"] += 1
    else:
        pca = PCA(n_components=pca_components, svd_solver="randomized", random_state=config.random_seed)
        pca_embeddings = pca.fit_transform(working).astype(np.float32)
        pca_explained_variance_ratio = pca.explained_variance_ratio_.astype(np.float32)
        atomic_save_npz(
            pca_path,
            embeddings=pca_embeddings,
            explained_variance_ratio=pca_explained_variance_ratio,
        )
    if pca_embeddings.shape != (len(working), pca_components):
        raise ValueError(f"PCA cache has unexpected shape: {pca_embeddings.shape}")

    try:
        import umap
    except ImportError as exc:
        raise RuntimeError("umap-learn is required for clustering") from exc

    run_labels: Dict[str, np.ndarray] = {}
    run_probabilities: Dict[str, np.ndarray] = {}
    run_reductions: Dict[str, np.ndarray] = {}
    metric_records: List[dict] = []
    run_groups: Dict[str, List[str]] = {}

    for n_neighbors in cluster_config["umap_n_neighbors"]:
        for seed in cluster_config["experiment_seeds"]:
            reduction_key = f"nn{int(n_neighbors)}_seed{int(seed)}"
            reduction_path = cache_dir / f"umap__{reduction_key}.npy"
            if reduction_path.exists() and not force:
                reduced = np.load(reduction_path, allow_pickle=False)
                cache_counts["umap"] += 1
            else:
                reducer = umap.UMAP(
                    n_neighbors=int(n_neighbors),
                    n_components=int(cluster_config["umap_components"]),
                    min_dist=float(cluster_config["umap_min_dist"]),
                    metric=str(cluster_config["umap_metric"]),
                    random_state=int(seed),
                    transform_seed=int(seed),
                    n_jobs=1,
                )
                reduced = reducer.fit_transform(pca_embeddings).astype(np.float32)
                atomic_save_npy(reduced, reduction_path)
            expected_reduction_shape = (len(working), int(cluster_config["umap_components"]))
            if reduced.shape != expected_reduction_shape:
                raise ValueError(f"UMAP cache has unexpected shape: {reduced.shape}")
            run_reductions[reduction_key] = reduced
            for min_cluster_size, min_samples in itertools.product(
                cluster_config["min_cluster_size"], cluster_config["min_samples"]
            ):
                group_id = (
                    f"nn{int(n_neighbors)}_mcs{int(min_cluster_size)}_"
                    f"ms{int(min_samples)}"
                )
                run_id = f"{group_id}_seed{int(seed)}"
                run_path = cache_dir / f"hdbscan__{run_id}.npz"
                if run_path.exists() and not force:
                    cached_run = np.load(run_path, allow_pickle=False)
                    labels = cached_run["labels"]
                    probabilities = cached_run["probabilities"]
                    cache_counts["hdbscan"] += 1
                else:
                    estimator = HDBSCAN(
                        min_cluster_size=int(min_cluster_size),
                        min_samples=int(min_samples),
                        metric="euclidean",
                        cluster_selection_method=str(cluster_config["cluster_selection_method"]),
                        n_jobs=-1,
                        copy=True,
                    )
                    labels = estimator.fit_predict(reduced).astype(np.int32)
                    probabilities = np.asarray(estimator.probabilities_, dtype=np.float32)
                    atomic_save_npz(run_path, labels=labels, probabilities=probabilities)
                if labels.shape != (len(working),) or probabilities.shape != (len(working),):
                    raise ValueError(f"HDBSCAN cache has unexpected shape for {run_id}")
                run_labels[run_id] = labels
                run_probabilities[run_id] = probabilities
                run_groups.setdefault(group_id, []).append(run_id)
                non_noise = labels >= 0
                metric_records.append(
                    {
                        "run_id": run_id,
                        "group_id": group_id,
                        "seed": int(seed),
                        "n_neighbors": int(n_neighbors),
                        "min_cluster_size": int(min_cluster_size),
                        "min_samples": int(min_samples),
                        "n_clusters": int(len(np.unique(labels[non_noise]))),
                        "noise_fraction": float((~non_noise).mean()),
                        "mean_membership_probability": float(probabilities[non_noise].mean())
                        if non_noise.any()
                        else 0.0,
                        "silhouette": _safe_silhouette(
                            reduced,
                            labels,
                            int(cluster_config["silhouette_sample_size"]),
                            int(seed),
                        ),
                    }
                )

    metrics = pd.DataFrame.from_records(metric_records)
    group_records = []
    for group_id, run_ids in run_groups.items():
        group_metrics = metrics.loc[metrics["group_id"] == group_id]
        first = group_metrics.iloc[0]
        group_records.append(
            {
                "group_id": group_id,
                "n_neighbors": int(first["n_neighbors"]),
                "min_cluster_size": int(first["min_cluster_size"]),
                "min_samples": int(first["min_samples"]),
                "mean_n_clusters": float(group_metrics["n_clusters"].mean()),
                "mean_noise_fraction": float(group_metrics["noise_fraction"].mean()),
                "mean_coverage": float(1.0 - group_metrics["noise_fraction"].mean()),
                "mean_membership_probability": float(group_metrics["mean_membership_probability"].mean()),
                "mean_silhouette": float(group_metrics["silhouette"].mean()),
                "seed_adjusted_rand": _group_stability(run_labels, run_ids),
            }
        )
    configurations = pd.DataFrame.from_records(group_records)
    if configurations.empty:
        raise RuntimeError("No clustering configurations were evaluated")
    configurations["selection_score"] = (
        0.35 * _normalize_series(configurations["seed_adjusted_rand"])
        + 0.20 * _normalize_series(configurations["mean_coverage"])
        + 0.20 * _normalize_series(configurations["mean_membership_probability"])
        + 0.25 * _normalize_series(configurations["mean_silhouette"])
    )
    viable = configurations.loc[configurations["mean_n_clusters"] >= 2]
    if viable.empty:
        raise RuntimeError("All clustering configurations produced fewer than two clusters")
    selected_group = str(viable.sort_values("selection_score", ascending=False).iloc[0]["group_id"])
    preferred_seed = int(config.random_seed)
    selected_runs = run_groups[selected_group]
    canonical_run = next(
        (run_id for run_id in selected_runs if run_id.endswith(f"seed{preferred_seed}")),
        selected_runs[0],
    )
    canonical_labels = run_labels[canonical_run]
    canonical_probabilities = run_probabilities[canonical_run]
    canonical_metric = metrics.loc[metrics["run_id"] == canonical_run].iloc[0]
    canonical_reduction_key = (
        f"nn{int(canonical_metric['n_neighbors'])}_seed{int(canonical_metric['seed'])}"
    )
    canonical_reduced = run_reductions[canonical_reduction_key]

    stability_records = []
    for cluster_id in sorted(label for label in np.unique(canonical_labels) if label >= 0):
        members = canonical_labels == cluster_id
        seed_comparisons = [
            best_jaccard(members, run_labels[run_id])
            for run_id in selected_runs
            if run_id != canonical_run
        ]
        grid_comparisons = [
            best_jaccard(members, labels)
            for run_id, labels in run_labels.items()
            if run_id != canonical_run
        ]
        centroid = working[members].mean(axis=0)
        centroid_norm = np.linalg.norm(centroid)
        if centroid_norm:
            centroid = centroid / centroid_norm
        coherence = float(np.mean(working[members] @ centroid))
        stability_records.append(
            {
                "cluster_id": int(cluster_id),
                "cluster_size": int(members.sum()),
                "mean_membership_probability": float(canonical_probabilities[members].mean()),
                "seed_stability_jaccard": float(np.mean(seed_comparisons))
                if seed_comparisons
                else 1.0,
                "grid_stability_jaccard": float(np.mean(grid_comparisons))
                if grid_comparisons
                else 1.0,
                "centroid_coherence": coherence,
            }
        )
    stability = pd.DataFrame.from_records(stability_records)

    assignments = working_index.loc[:, ["embedding_row", "span_id", "review_id"]].copy()
    assignments["cluster_id"] = canonical_labels
    assignments["membership_probability"] = canonical_probabilities
    assignments["is_noise"] = canonical_labels < 0
    for coordinate in range(min(2, canonical_reduced.shape[1])):
        assignments[f"umap_{coordinate + 1}"] = canonical_reduced[:, coordinate]

    experiment_arrays: Dict[str, np.ndarray] = {
        "selected_embedding_rows": selected_rows,
        "pca_explained_variance_ratio": pca_explained_variance_ratio,
    }
    for run_id, labels in run_labels.items():
        experiment_arrays[f"labels__{run_id}"] = labels
        experiment_arrays[f"probabilities__{run_id}"] = run_probabilities[run_id]
    for reduction_key, reduction in run_reductions.items():
        experiment_arrays[f"umap__{reduction_key}"] = reduction

    atomic_write_csv(metrics, cluster_dir / "experiment_metrics.csv")
    atomic_write_csv(configurations, cluster_dir / "configuration_summary.csv")
    atomic_write_csv(assignments, cluster_dir / "cluster_assignments.csv")
    atomic_write_csv(stability, cluster_dir / "cluster_stability.csv")
    atomic_save_npz(cluster_dir / "experiment_arrays.npz", **experiment_arrays)

    selected_configuration = configurations.loc[
        configurations["group_id"] == selected_group
    ].iloc[0].to_dict()
    summary: Dict[str, object] = {
        "input_spans": int(len(index)),
        "clustered_spans": int(len(assignments)),
        "not_sampled_spans": int(len(not_sampled)),
        "pca_components": int(pca_components),
        "pca_explained_variance": float(pca_explained_variance_ratio.sum()),
        "experiment_runs": int(len(metrics)),
        "selected_group": selected_group,
        "canonical_run": canonical_run,
        "selected_configuration": selected_configuration,
        "clusters": int(len(stability)),
        "noise_spans": int((canonical_labels < 0).sum()),
        "restart_cache_key": cache_key,
        "restart_cache_files_reused": cache_counts,
    }
    manifest = {
        "inputs": expected,
        "summary": summary,
        "environment": environment_manifest(config.repository_root),
    }
    atomic_write_json(manifest, manifest_path)
    return summary
