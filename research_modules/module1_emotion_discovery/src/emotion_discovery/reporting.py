"""Stage 4: corpus-derived labels, nearest examples, NRC references, and plots."""

from __future__ import annotations

import json
import math
import os
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer

from . import NRC_EMOTIONS
from .config import ProjectConfig
from .storage import (
    atomic_write_csv,
    atomic_write_json,
    environment_manifest,
    refuse_stale_outputs,
    sha256_file,
    sha256_json,
)


NRC_COLUMNS = tuple(f"nrc_{emotion}" for emotion in NRC_EMOTIONS)


def _minmax(values: pd.Series) -> pd.Series:
    values = values.astype(float).replace([np.inf, -np.inf], np.nan)
    minimum = values.min()
    maximum = values.max()
    if pd.isna(minimum) or pd.isna(maximum) or maximum <= minimum:
        return pd.Series(np.full(len(values), 0.5), index=values.index)
    return (values.fillna(minimum) - minimum) / (maximum - minimum)


def _distinct_label_phrases(phrases: Sequence[Tuple[str, float]], limit: int = 2) -> List[str]:
    """Select non-redundant labels directly from cluster-distinctive phrases."""

    selected: List[str] = []
    selected_tokens: List[set[str]] = []
    ordered = sorted(phrases, key=lambda item: (len(item[0].split()) == 1, -item[1]))
    for phrase, _ in ordered:
        tokens = set(phrase.split())
        if not tokens:
            continue
        if any(len(tokens & existing) / len(tokens | existing) >= 0.6 for existing in selected_tokens):
            continue
        selected.append(phrase)
        selected_tokens.append(tokens)
        if len(selected) == limit:
            break
    return selected


def cluster_distinctive_phrases(
    texts: Sequence[str],
    labels: np.ndarray,
    top_n: int,
    max_features: int,
    ngram_range: Tuple[int, int],
) -> Dict[int, List[Tuple[str, float]]]:
    """Compute class-based TF-IDF without joining text across span boundaries."""

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
    cluster_counts = np.vstack(
        [np.asarray(matrix[valid_labels == cluster_id].sum(axis=0)).ravel() for cluster_id in cluster_ids]
    )
    cluster_totals = np.maximum(cluster_counts.sum(axis=1, keepdims=True), 1.0)
    term_frequency = cluster_counts / cluster_totals
    document_frequency = (cluster_counts > 0).sum(axis=0)
    inverse_document_frequency = np.log((1.0 + len(cluster_ids)) / (1.0 + document_frequency)) + 1.0
    scores = term_frequency * inverse_document_frequency
    terms = vectorizer.get_feature_names_out()
    output: Dict[int, List[Tuple[str, float]]] = {}
    for row, cluster_id in enumerate(cluster_ids):
        nonzero = np.flatnonzero(cluster_counts[row] > 0)
        ranked = nonzero[np.argsort(scores[row, nonzero])[::-1]][:top_n]
        output[cluster_id] = [(str(terms[index]), float(scores[row, index])) for index in ranked]
    return output


def _representatives(
    cluster_id: int,
    members: pd.DataFrame,
    embeddings: np.ndarray,
    limit: int,
) -> pd.DataFrame:
    rows = members["embedding_row"].to_numpy(dtype=np.int64)
    vectors = np.asarray(embeddings[rows], dtype=np.float32)
    centroid = vectors.mean(axis=0)
    norm = np.linalg.norm(centroid)
    if norm:
        centroid = centroid / norm
    similarities = vectors @ centroid
    ranked = np.argsort(similarities)[::-1]
    records = []
    seen_reviews = set()
    for position in ranked:
        row = members.iloc[int(position)]
        review_id = str(row["review_id"])
        if review_id in seen_reviews:
            continue
        seen_reviews.add(review_id)
        records.append(
            {
                "cluster_id": cluster_id,
                "rank": len(records) + 1,
                "span_id": row["span_id"],
                "review_id": review_id,
                "span_text": row["span_text"],
                "parent_sentence": row.get("sentence_text", ""),
                "unit_type": row["unit_type"],
                "marker_before": row.get("marker_before", ""),
                "centroid_cosine_similarity": float(similarities[position]),
                "membership_probability": float(row["membership_probability"]),
            }
        )
        if len(records) >= limit:
            break
    return pd.DataFrame.from_records(records)


def _save_figure(figure: object, path: Path) -> None:
    temporary = path.with_name(path.stem + ".tmp" + path.suffix)
    figure.savefig(temporary, dpi=220, bbox_inches="tight")
    os.replace(temporary, path)


def _create_plots(
    assignments: pd.DataFrame,
    inventory: pd.DataFrame,
    nrc_profile: pd.DataFrame,
    plot_dir: Path,
    seed: int,
) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plot_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)
    maximum_points = 30000
    if len(assignments) > maximum_points:
        rows = np.sort(rng.choice(len(assignments), maximum_points, replace=False))
        plotted = assignments.iloc[rows]
    else:
        plotted = assignments

    fig, axis = plt.subplots(figsize=(11, 8))
    noise = plotted["cluster_id"] < 0
    axis.scatter(
        plotted.loc[noise, "umap_1"],
        plotted.loc[noise, "umap_2"],
        s=2,
        alpha=0.12,
        color="#a7a7a7",
        label="noise / uncertain",
        rasterized=True,
    )
    clustered = plotted.loc[~noise]
    axis.scatter(
        clustered["umap_1"],
        clustered["umap_2"],
        c=clustered["cluster_id"],
        cmap="turbo",
        s=3,
        alpha=0.55,
        rasterized=True,
    )
    axis.set(title="Corpus-driven emotion/semantic span clusters", xlabel="UMAP 1", ylabel="UMAP 2")
    axis.legend(loc="best", frameon=False)
    _save_figure(fig, plot_dir / "umap_clusters.png")
    plt.close(fig)

    fig, axis = plt.subplots(figsize=(10, 7))
    sizes = np.maximum(30, np.sqrt(inventory["cluster_size"].to_numpy()) * 8)
    scatter = axis.scatter(
        inventory["seed_stability_jaccard"],
        inventory["centroid_coherence"],
        s=sizes,
        c=inventory["emotion_cluster_confidence"],
        cmap="viridis",
        vmin=0,
        vmax=1,
        alpha=0.78,
        edgecolor="white",
        linewidth=0.5,
    )
    for row in inventory.itertuples(index=False):
        axis.annotate(str(row.cluster_id), (row.seed_stability_jaccard, row.centroid_coherence), fontsize=7)
    axis.set(
        title="Cluster stability, coherence, and size",
        xlabel="Seed stability (best-match Jaccard)",
        ylabel="Embedding centroid coherence",
        xlim=(-0.02, 1.02),
    )
    fig.colorbar(scatter, ax=axis, label="Emotion-cluster confidence")
    _save_figure(fig, plot_dir / "cluster_stability.png")
    plt.close(fig)

    if not nrc_profile.empty:
        heat_columns = [f"{column}_enrichment" for column in NRC_COLUMNS]
        heat = nrc_profile.set_index("cluster_id")[heat_columns].to_numpy(dtype=float)
        heat = np.log2(np.maximum(heat, 1e-6))
        heat = np.clip(heat, -2, 2)
        fig_height = max(5, 0.33 * len(nrc_profile))
        fig, axis = plt.subplots(figsize=(11, fig_height))
        image = axis.imshow(heat, aspect="auto", cmap="coolwarm", vmin=-2, vmax=2)
        axis.set_xticks(np.arange(len(NRC_EMOTIONS)), labels=NRC_EMOTIONS, rotation=40, ha="right")
        axis.set_yticks(
            np.arange(len(nrc_profile)),
            labels=nrc_profile["cluster_id"].astype(str).tolist(),
        )
        axis.set(title="NRC baseline enrichment after clustering", xlabel="NRC parent reference", ylabel="Cluster")
        fig.colorbar(image, ax=axis, label="log2 enrichment")
        _save_figure(fig, plot_dir / "nrc_parent_enrichment.png")
        plt.close(fig)


def _report_expected(config: ProjectConfig) -> Dict[str, object]:
    paths = {
        "spans": config.output_dir / "intermediate" / "analysis_spans.csv",
        "sentences": config.output_dir / "intermediate" / "sentences.csv",
        "embeddings": config.output_dir / "embeddings" / "span_embeddings.npy",
        "assignments": config.output_dir / "clusters" / "cluster_assignments.csv",
        "stability": config.output_dir / "clusters" / "cluster_stability.csv",
    }
    return {
        "stage_config_sha256": sha256_json(
            {"random_seed": config.random_seed, "reporting": config.raw["reporting"]}
        ),
        **{f"{name}_sha256": sha256_file(path) for name, path in paths.items()},
        "stage": "reporting-v1",
    }


def run_reporting(config: ProjectConfig, force: bool = False) -> Dict[str, object]:
    output_dir = config.output_dir
    expected = _report_expected(config)
    report_dir = output_dir / "reports"
    plot_dir = output_dir / "plots"
    audit_dir = output_dir / "audit"
    manifest_path = output_dir / "manifests" / "stage04_reporting.json"
    required_outputs = (
        report_dir / "cluster_inventory.csv",
        report_dir / "cluster_representative_examples.csv",
        report_dir / "cluster_nrc_profile.csv",
        report_dir / "uncertain_clusters.csv",
        audit_dir / "noise_spans.csv",
        plot_dir / "umap_clusters.png",
        plot_dir / "cluster_stability.png",
        plot_dir / "nrc_parent_enrichment.png",
    )
    if refuse_stale_outputs(manifest_path, expected, force):
        missing = [str(path) for path in required_outputs if not path.exists()]
        if missing:
            raise RuntimeError(f"Reporting manifest is current but outputs are missing: {missing}")
        return {"status": "skipped"}

    spans = pd.read_csv(output_dir / "intermediate" / "analysis_spans.csv", low_memory=False)
    sentences = pd.read_csv(
        output_dir / "intermediate" / "sentences.csv",
        usecols=["sentence_id", "sentence_text"],
    )
    assignments = pd.read_csv(output_dir / "clusters" / "cluster_assignments.csv")
    stability = pd.read_csv(output_dir / "clusters" / "cluster_stability.csv")
    embeddings = np.load(output_dir / "embeddings" / "span_embeddings.npy", allow_pickle=False)
    merged = assignments.merge(spans, on=["span_id", "review_id"], validate="one_to_one")
    merged = merged.merge(
        sentences,
        left_on="parent_sentence_id",
        right_on="sentence_id",
        how="left",
        validate="many_to_one",
    )
    if len(merged) != len(assignments):
        raise RuntimeError("Cluster assignments did not join one-to-one with analysis spans")

    noise = merged.loc[merged["cluster_id"] < 0].copy()
    noise["audit_reason"] = "hdbscan_noise_or_outlier"
    atomic_write_csv(
        noise.loc[
            :,
            [
                "span_id",
                "review_id",
                "span_text",
                "membership_probability",
                "audit_reason",
            ],
        ],
        audit_dir / "noise_spans.csv",
    )

    valid = merged.loc[merged["cluster_id"] >= 0].copy()
    if valid.empty:
        raise RuntimeError("Canonical clustering has no non-noise spans")
    reporting_config = config.raw["reporting"]
    phrases = cluster_distinctive_phrases(
        valid["span_text"].fillna("").astype(str).tolist(),
        valid["cluster_id"].to_numpy(dtype=np.int32),
        top_n=int(reporting_config["top_phrases"]),
        max_features=int(reporting_config["max_tfidf_features"]),
        ngram_range=tuple(int(value) for value in reporting_config["ngram_range"]),
    )

    corpus = pd.read_csv(output_dir / "intermediate" / "corpus_reviews.csv", low_memory=False)
    global_nrc = corpus.loc[:, NRC_COLUMNS].mean().fillna(0.0)
    inventory_records = []
    nrc_records = []
    representatives = []
    for cluster_id in sorted(int(value) for value in valid["cluster_id"].unique()):
        members = valid.loc[valid["cluster_id"] == cluster_id].copy()
        unique_reviews = members.drop_duplicates("review_id")
        phrase_rows = phrases.get(cluster_id, [])
        label_parts = _distinct_label_phrases(phrase_rows)
        possible_label = " | ".join(label_parts) if label_parts else "unresolved corpus cluster"
        cluster_nrc = unique_reviews.loc[:, NRC_COLUMNS].mean().fillna(0.0)
        enrichment = (cluster_nrc + 1e-8) / (global_nrc + 1e-8)
        best_column = str(enrichment.idxmax())
        best_enrichment = float(enrichment[best_column])
        parent = ""
        if (
            float(cluster_nrc[best_column]) > 0
            and best_enrichment >= float(reporting_config["minimum_nrc_parent_enrichment"])
        ):
            parent = best_column.removeprefix("nrc_")

        nrc_record: Dict[str, object] = {"cluster_id": cluster_id}
        for column in NRC_COLUMNS:
            nrc_record[f"{column}_mean"] = float(cluster_nrc[column])
            nrc_record[f"{column}_enrichment"] = float(enrichment[column])
        nrc_records.append(nrc_record)

        representative_frame = _representatives(
            cluster_id,
            members,
            embeddings,
            int(reporting_config["representative_examples"]),
        )
        representatives.append(representative_frame)
        phrase_score = float(phrase_rows[0][1]) if phrase_rows else 0.0
        inventory_records.append(
            {
                "cluster_id": cluster_id,
                "cluster_size": int(len(members)),
                "unique_reviews": int(members["review_id"].nunique()),
                "possible_fine_grained_emotion_label": possible_label,
                "representative_words_phrases": json.dumps(
                    [
                        {"phrase": phrase, "score": round(score, 8)}
                        for phrase, score in phrase_rows
                    ],
                    ensure_ascii=False,
                ),
                "nrc_parent_emotion": parent,
                "nrc_parent_enrichment": best_enrichment if parent else np.nan,
                "mean_review_vader_compound": float(members["sentiment_polarity"].mean()),
                "mean_absolute_review_vader": float(members["sentiment_polarity"].abs().mean()),
                "mean_nrc_density_sum": float(unique_reviews.loc[:, NRC_COLUMNS].sum(axis=1).mean()),
                "lexical_distinctiveness": phrase_score,
            }
        )

    inventory = pd.DataFrame.from_records(inventory_records).merge(
        stability,
        on=["cluster_id", "cluster_size"],
        how="left",
        validate="one_to_one",
    )
    inventory["cluster_quality_confidence"] = (
        0.35 * inventory["seed_stability_jaccard"].clip(0, 1)
        + 0.15 * inventory["grid_stability_jaccard"].clip(0, 1)
        + 0.25 * inventory["mean_membership_probability"].clip(0, 1)
        + 0.15 * ((inventory["centroid_coherence"].clip(-1, 1) + 1) / 2)
        + 0.10 * _minmax(inventory["lexical_distinctiveness"])
    )
    inventory["affect_evidence_score"] = (
        0.55 * _minmax(inventory["mean_nrc_density_sum"])
        + 0.45 * _minmax(inventory["mean_absolute_review_vader"])
    )
    inventory["emotion_cluster_confidence"] = (
        0.80 * inventory["cluster_quality_confidence"]
        + 0.20 * inventory["affect_evidence_score"]
    ).clip(0, 1)
    uncertain_threshold = float(reporting_config["uncertain_confidence_threshold"])
    inventory["confidence_band"] = np.select(
        [
            inventory["emotion_cluster_confidence"] >= 0.70,
            inventory["emotion_cluster_confidence"] >= uncertain_threshold,
        ],
        ["high", "medium"],
        default="uncertain",
    )
    inventory["requires_human_label_review"] = inventory["confidence_band"] != "high"
    inventory = inventory.sort_values(
        ["emotion_cluster_confidence", "cluster_size"], ascending=[False, False]
    ).reset_index(drop=True)
    nrc_profile = pd.DataFrame.from_records(nrc_records)
    representative_output = pd.concat(representatives, ignore_index=True)
    uncertain = inventory.loc[inventory["requires_human_label_review"]].copy()

    atomic_write_csv(inventory, report_dir / "cluster_inventory.csv")
    atomic_write_csv(representative_output, report_dir / "cluster_representative_examples.csv")
    atomic_write_csv(nrc_profile, report_dir / "cluster_nrc_profile.csv")
    atomic_write_csv(uncertain, report_dir / "uncertain_clusters.csv")
    _create_plots(assignments, inventory, nrc_profile, plot_dir, config.random_seed)

    summary: Dict[str, object] = {
        "clusters": int(len(inventory)),
        "high_confidence_clusters": int((inventory["confidence_band"] == "high").sum()),
        "medium_confidence_clusters": int((inventory["confidence_band"] == "medium").sum()),
        "uncertain_clusters": int((inventory["confidence_band"] == "uncertain").sum()),
        "clustered_spans": int(len(valid)),
        "noise_spans": int(len(noise)),
        "representative_examples": int(len(representative_output)),
        "label_method": "corpus c-TF-IDF phrases; no pre-specified fine-grained emotion inventory",
        "nrc_role": "post-cluster parent reference using existing review-level NRC baseline",
    }
    atomic_write_json(summary, report_dir / "module1_summary.json")
    manifest = {
        "inputs": expected,
        "summary": summary,
        "environment": environment_manifest(config.repository_root),
    }
    atomic_write_json(manifest, manifest_path)
    return summary
