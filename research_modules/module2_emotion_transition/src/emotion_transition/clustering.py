"""Stage 3: unsupervised discovery of recurring source-to-target directions."""

from __future__ import annotations

import itertools
from pathlib import Path
from typing import Dict, Sequence

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
)


def best_jaccard(reference_members: np.ndarray, labels: np.ndarray) -> float:
    reference = np.asarray(reference_members, dtype=bool)
    if not reference.any():
        return 0.0
    best = 0.0
    for label in np.unique(labels):
        if label < 0:
            continue
        candidate = labels == label
        union = np.logical_or(reference, candidate).sum()
        if union:
            best = max(best, float(np.logical_and(reference, candidate).sum() / union))
    return best


def _safe_silhouette(reduced: np.ndarray, labels: np.ndarray, sample_size: int, seed: int) -> float:
    valid = np.flatnonzero(labels >= 0)
    if len(np.unique(labels[valid])) < 2:
        return float("nan")
    if len(valid) > sample_size:
        valid = np.sort(np.random.default_rng(seed).choice(valid, size=sample_size, replace=False))
    try:
        return float(silhouette_score(reduced[valid], labels[valid], metric="euclidean"))
    except ValueError:
        return float("nan")


def _normalize(series: pd.Series) -> pd.Series:
    values = series.replace([np.inf, -np.inf], np.nan)
    minimum, maximum = values.min(), values.max()
    if pd.isna(minimum) or pd.isna(maximum) or maximum <= minimum:
        return pd.Series(np.full(len(series), 0.5), index=series.index)
    return (values.fillna(minimum) - minimum) / (maximum - minimum)


def _group_ari(run_labels: Dict[str, np.ndarray], run_ids: Sequence[str]) -> float:
    scores = [
        adjusted_rand_score(run_labels[left], run_labels[right])
        for left, right in itertools.combinations(run_ids, 2)
    ]
    return float(np.mean(scores)) if scores else 1.0


def _expected(config: ProjectConfig) -> Dict[str, object]:
    output_dir = config.output_dir
    return {
        "stage": "directional-transformation-clustering-v1",
        "config_sha256": sha256_json(config.raw["clustering"]),
        "pair_index_sha256": sha256_file(output_dir / "pair_vectors" / "pair_embedding_index.csv"),
        "vectors_sha256": sha256_file(output_dir / "pair_vectors" / "transformation_vectors.npy"),
        "stage_code_sha256": sha256_file(Path(__file__)),
    }


def run_clustering(config: ProjectConfig, force: bool = False) -> Dict[str, object]:
    output_dir = config.output_dir
    cluster_dir = output_dir / "clusters"
    manifest_path = output_dir / "manifests" / "stage03_clustering.json"
    required = (
        cluster_dir / "cluster_assignments.csv",
        cluster_dir / "cluster_stability.csv",
        cluster_dir / "experiment_metrics.csv",
        cluster_dir / "configuration_summary.csv",
        cluster_dir / "summary.json",
    )
    expected = _expected(config)
    if refuse_stale_outputs(manifest_path, expected, force):
        missing = [str(path) for path in required if not path.exists()]
        if missing:
            raise RuntimeError(f"Transformation clustering manifest is current but outputs are missing: {missing}")
        return {"status": "skipped"}

    pair_index = pd.read_csv(output_dir / "pair_vectors" / "pair_embedding_index.csv")
    vectors = np.load(output_dir / "pair_vectors" / "transformation_vectors.npy", allow_pickle=False)
    if vectors.ndim != 2 or len(pair_index) != len(vectors):
        raise ValueError("Pair-vector index and matrix are misaligned")
    if pair_index["transition_id"].duplicated().any() or not np.isfinite(vectors).all():
        raise ValueError("Pair-vector inputs contain duplicate IDs or non-finite values")

    cfg = config.raw["clustering"]
    components = min(int(cfg["pca_components"]), vectors.shape[1], len(vectors) - 1)
    cache_key = sha256_json(expected)[:16]
    cache_dir = cluster_dir / "cache" / cache_key
    pca_path = cache_dir / "pca.npz"
    cache_reused = {"pca": 0, "umap": 0, "hdbscan": 0}
    if pca_path.exists() and not force:
        cached = np.load(pca_path, allow_pickle=False)
        pca_vectors = cached["vectors"]
        explained = cached["explained_variance_ratio"]
        cache_reused["pca"] += 1
    else:
        pca = PCA(n_components=components, svd_solver="randomized", random_state=config.random_seed)
        pca_vectors = pca.fit_transform(vectors).astype(np.float32)
        explained = pca.explained_variance_ratio_.astype(np.float32)
        atomic_save_npz(pca_path, vectors=pca_vectors, explained_variance_ratio=explained)

    try:
        import umap
    except ImportError as exc:
        raise RuntimeError("umap-learn is required for transformation clustering") from exc

    run_labels: Dict[str, np.ndarray] = {}
    run_probabilities: Dict[str, np.ndarray] = {}
    reductions: Dict[int, np.ndarray] = {}
    run_groups: Dict[str, list[str]] = {}
    metrics = []
    for seed_value in cfg["experiment_seeds"]:
        seed = int(seed_value)
        reduction_path = cache_dir / f"umap_seed{seed}.npy"
        if reduction_path.exists() and not force:
            reduced = np.load(reduction_path, allow_pickle=False)
            cache_reused["umap"] += 1
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
            reduced = reducer.fit_transform(pca_vectors).astype(np.float32)
            atomic_save_npy(reduced, reduction_path)
        expected_shape = (len(vectors), int(cfg["umap_components"]))
        if reduced.shape != expected_shape:
            raise ValueError(f"Transformation UMAP cache has unexpected shape: {reduced.shape}")
        reductions[seed] = reduced

        for min_cluster_size, min_samples in itertools.product(cfg["min_cluster_size"], cfg["min_samples"]):
            group_id = f"mcs{int(min_cluster_size)}_ms{int(min_samples)}"
            run_id = f"{group_id}_seed{seed}"
            run_path = cache_dir / f"hdbscan_{run_id}.npz"
            if run_path.exists() and not force:
                cached = np.load(run_path, allow_pickle=False)
                labels = cached["labels"]
                probabilities = cached["probabilities"]
                cache_reused["hdbscan"] += 1
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
            metrics.append(
                {
                    "run_id": run_id,
                    "group_id": group_id,
                    "seed": seed,
                    "min_cluster_size": int(min_cluster_size),
                    "min_samples": int(min_samples),
                    "n_clusters": int(len(np.unique(labels[valid]))),
                    "noise_fraction": float((~valid).mean()),
                    "mean_membership_probability": float(probabilities[valid].mean()) if valid.any() else 0.0,
                    "silhouette": _safe_silhouette(
                        reduced, labels, int(cfg["silhouette_sample_size"]), seed
                    ),
                }
            )

    metric_frame = pd.DataFrame.from_records(metrics)
    configurations = []
    for group_id, run_ids in run_groups.items():
        group = metric_frame.loc[metric_frame["group_id"].eq(group_id)]
        first = group.iloc[0]
        configurations.append(
            {
                "group_id": group_id,
                "min_cluster_size": int(first["min_cluster_size"]),
                "min_samples": int(first["min_samples"]),
                "mean_n_clusters": float(group["n_clusters"].mean()),
                "mean_coverage": float(1 - group["noise_fraction"].mean()),
                "mean_noise_fraction": float(group["noise_fraction"].mean()),
                "mean_membership_probability": float(group["mean_membership_probability"].mean()),
                "mean_silhouette": float(group["silhouette"].mean()),
                "seed_adjusted_rand": _group_ari(run_labels, run_ids),
            }
        )
    configuration_frame = pd.DataFrame.from_records(configurations)
    configuration_frame["selection_score"] = (
        0.35 * _normalize(configuration_frame["seed_adjusted_rand"])
        + 0.20 * _normalize(configuration_frame["mean_coverage"])
        + 0.20 * _normalize(configuration_frame["mean_membership_probability"])
        + 0.25 * _normalize(configuration_frame["mean_silhouette"])
    )
    viable = configuration_frame.loc[configuration_frame["mean_n_clusters"].ge(2)]
    if viable.empty:
        raise RuntimeError("Every transformation clustering configuration produced fewer than two clusters")
    selected_group = str(viable.sort_values("selection_score", ascending=False).iloc[0]["group_id"])
    selected_runs = run_groups[selected_group]
    canonical_run = next(
        (run_id for run_id in selected_runs if run_id.endswith(f"seed{config.random_seed}")),
        selected_runs[0],
    )
    labels = run_labels[canonical_run]
    probabilities = run_probabilities[canonical_run]
    seed = int(canonical_run.rsplit("seed", 1)[1])

    stability_records = []
    for cluster_id in sorted(int(value) for value in np.unique(labels) if value >= 0):
        members = labels == cluster_id
        centroid = vectors[members].mean(axis=0)
        centroid = centroid / max(float(np.linalg.norm(centroid)), 1e-12)
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
                "directional_centroid_coherence": float(np.mean(vectors[members] @ centroid)),
            }
        )
    stability = pd.DataFrame.from_records(stability_records)
    assignments = pair_index.copy()
    assignments["cluster_id"] = labels
    assignments["membership_probability"] = probabilities
    assignments["is_noise"] = labels < 0
    assignments["umap_1"] = reductions[seed][:, 0]
    assignments["umap_2"] = reductions[seed][:, 1]

    summary = {
        "candidate_pairs": int(len(assignments)),
        "pca_components": int(components),
        "pca_explained_variance": float(explained.sum()),
        "experiment_runs": int(len(metric_frame)),
        "selected_group": selected_group,
        "canonical_run": canonical_run,
        "clusters": int(len(stability)),
        "clustered_pairs": int((labels >= 0).sum()),
        "noise_pairs": int((labels < 0).sum()),
        "restart_cache_key": cache_key,
        "restart_cache_files_reused": cache_reused,
        "labels_are_human_validated": False,
    }
    atomic_write_csv(metric_frame, cluster_dir / "experiment_metrics.csv")
    atomic_write_csv(configuration_frame, cluster_dir / "configuration_summary.csv")
    atomic_write_csv(assignments, cluster_dir / "cluster_assignments.csv")
    atomic_write_csv(stability, cluster_dir / "cluster_stability.csv")
    atomic_write_json(summary, cluster_dir / "summary.json")
    atomic_write_json(
        {"inputs": expected, "summary": summary, "environment": environment_manifest()}, manifest_path
    )
    return summary
