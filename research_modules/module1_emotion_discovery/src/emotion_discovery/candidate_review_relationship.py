"""Descriptive links between provisional emotion candidates and review outcomes.

This stage is deliberately descriptive. Cluster membership is evidence-pool
membership, not emotion intensity, and star-rating differences are not causal
effects. All links are made by stable ``review_id``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable

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


DISPLAY_LABELS = {
    "scenic_awe": "Scenic awe",
    "flight_apprehension": "Flight apprehension",
    "provider_directed_gratitude": "Provider gratitude",
}


def _selected_members(
    assignments: pd.DataFrame,
    cluster_ids: Iterable[int],
    discovery_view: str,
) -> pd.DataFrame:
    selected = assignments.loc[
        assignments["cluster_id"].isin([int(value) for value in cluster_ids]),
        ["review_id", "span_id", "cluster_id", "membership_probability"],
    ].copy()
    selected["discovery_view"] = discovery_view
    return selected


def build_candidate_review_links(
    canonical: pd.DataFrame,
    full_assignments: pd.DataFrame,
    focused_assignments: pd.DataFrame,
    candidate_configuration: Iterable[Dict[str, object]],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Create deduplicated candidate-span and candidate-review links."""

    required_canonical = {
        "review_id",
        "rating",
        "sentiment_polarity",
        "analysis_language_status",
    }
    missing = sorted(required_canonical - set(canonical.columns))
    if missing:
        raise ValueError(f"Canonical reviews are missing columns: {missing}")
    english = canonical.loc[
        canonical["analysis_language_status"].eq("english"),
        ["review_id", "rating", "sentiment_polarity"],
    ].copy()
    if english["review_id"].duplicated().any():
        raise ValueError("Canonical English review_id values must be unique")

    candidate_frames = []
    for candidate in candidate_configuration:
        candidate_id = str(candidate["candidate_id"])
        full = _selected_members(
            full_assignments,
            candidate["full_unsupervised_clusters"],
            "full_unsupervised",
        )
        focused = _selected_members(
            focused_assignments,
            candidate["cate_focused_clusters"],
            "cate_focused",
        )
        combined = pd.concat([full, focused], ignore_index=True)
        if combined.empty:
            raise ValueError(f"Candidate {candidate_id} has no evidence members")
        combined.insert(0, "candidate_id", candidate_id)
        candidate_frames.append(combined)

    memberships = pd.concat(candidate_frames, ignore_index=True)
    span_links = (
        memberships.groupby(["candidate_id", "review_id", "span_id"], as_index=False)
        .agg(
            evidence_views=("discovery_view", lambda values: "|".join(sorted(set(values)))),
            evidence_clusters=("cluster_id", lambda values: "|".join(str(value) for value in sorted(set(values)))),
            max_cluster_membership_probability=("membership_probability", "max"),
        )
        .sort_values(["candidate_id", "review_id", "span_id"], kind="stable")
        .reset_index(drop=True)
    )

    review_links = (
        span_links.groupby(["candidate_id", "review_id"], as_index=False)
        .agg(
            unique_evidence_spans=("span_id", "nunique"),
            evidence_views=("evidence_views", lambda values: "|".join(sorted(set("|".join(values).split("|"))))),
            max_cluster_membership_probability=("max_cluster_membership_probability", "max"),
            mean_cluster_membership_probability=("max_cluster_membership_probability", "mean"),
        )
        .merge(english, on="review_id", how="left", validate="many_to_one")
    )
    if review_links[["rating", "sentiment_polarity"]].isna().any().any():
        missing_ids = review_links.loc[review_links["rating"].isna(), "review_id"].nunique()
        raise ValueError(f"Candidate links contain {missing_ids} reviews absent from canonical English data")
    return span_links, review_links


def summarize_candidate_reviews(
    canonical: pd.DataFrame,
    review_links: pd.DataFrame,
) -> pd.DataFrame:
    """Summarize star ratings and review-level VADER for each evidence pool."""

    english = canonical.loc[canonical["analysis_language_status"].eq("english")].copy()
    records = []
    groups = [("all_english_reviews", english)] + list(review_links.groupby("candidate_id", sort=False))
    for candidate_id, frame in groups:
        ratings = pd.to_numeric(frame["rating"], errors="raise")
        record = {
            "candidate_id": candidate_id,
            "display_label": "All English reviews" if candidate_id == "all_english_reviews" else DISPLAY_LABELS.get(candidate_id, candidate_id),
            "unique_reviews": int(frame["review_id"].nunique()),
            "mean_rating": float(ratings.mean()),
            "median_rating": float(ratings.median()),
            "rating_standard_deviation": float(ratings.std(ddof=1)),
            "mean_review_vader_compound": float(frame["sentiment_polarity"].mean()),
            "human_validation_status": "not_applicable" if candidate_id == "all_english_reviews" else "pending",
        }
        for rating in range(1, 6):
            record[f"rating_{rating}_percent"] = float(ratings.eq(rating).mean() * 100.0)
        records.append(record)
    summary = pd.DataFrame.from_records(records)
    baseline = summary.loc[summary["candidate_id"].eq("all_english_reviews")].iloc[0]
    summary["mean_rating_difference_from_corpus"] = summary["mean_rating"] - float(baseline["mean_rating"])
    summary["mean_vader_difference_from_corpus"] = (
        summary["mean_review_vader_compound"] - float(baseline["mean_review_vader_compound"])
    )
    return summary


def _save_plot(summary: pd.DataFrame, path: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import font_manager

    chinese_font_path = Path("/System/Library/Fonts/Supplemental/Songti.ttc")
    if chinese_font_path.exists():
        font_manager.fontManager.addfont(chinese_font_path)
        chinese_font = font_manager.FontProperties(fname=chinese_font_path).get_name()
    else:
        chinese_font = "DejaVu Sans"
    plt.rcParams["font.family"] = [chinese_font, "DejaVu Sans"]
    baseline = summary.loc[summary["candidate_id"].eq("all_english_reviews")].iloc[0]
    candidates = summary.loc[summary["candidate_id"].ne("all_english_reviews")].copy()
    colors = {
        "scenic_awe": "#7C3AED",
        "flight_apprehension": "#DC2626",
        "provider_directed_gratitude": "#059669",
    }

    fig, (left, right) = plt.subplots(1, 2, figsize=(16, 7.8), gridspec_kw={"width_ratios": [1.0, 1.28]})
    for row in candidates.itertuples(index=False):
        size = 260 + 0.24 * row.unique_reviews
        left.scatter(
            row.mean_review_vader_compound,
            row.mean_rating,
            s=size,
            color=colors.get(row.candidate_id, "#475569"),
            edgecolor="white",
            linewidth=1.4,
            alpha=0.86,
        )
        left.annotate(
            f"{row.display_label}\nn={row.unique_reviews:,}",
            (row.mean_review_vader_compound, row.mean_rating),
            xytext=(7, 7),
            textcoords="offset points",
            fontsize=10,
            fontweight="semibold",
        )
    left.axhline(float(baseline["mean_rating"]), color="#EF4444", linestyle=":", linewidth=1.5)
    left.axvline(float(baseline["mean_review_vader_compound"]), color="#64748B", linestyle="--", linewidth=1.2)
    left.set_xlabel("候选证据评论的平均VADER compound（评论级）")
    left.set_ylabel("候选证据评论的平均星级")
    left.set_title("A. 候选情绪证据池与评论结果（均值放大图）", fontweight="bold")
    left.set_xlim(0.86, 0.945)
    left.set_ylim(4.74, 4.98)
    left.grid(alpha=0.22)
    left.text(
        0.862,
        4.747,
        f"虚线：全部英文评论均值\nVADER={baseline['mean_review_vader_compound']:.3f}；星级={baseline['mean_rating']:.3f}",
        fontsize=9,
        color="#475569",
        va="bottom",
    )

    ordered = summary.copy()
    labels = ordered["display_label"].tolist()
    y = np.arange(len(ordered))
    left_edge = np.zeros(len(ordered))
    rating_colors = ["#B91C1C", "#EA580C", "#EAB308", "#60A5FA", "#16A34A"]
    for rating, color in zip(range(1, 6), rating_colors):
        values = ordered[f"rating_{rating}_percent"].to_numpy(dtype=float)
        right.barh(y, values, left=left_edge, color=color, label=f"{rating}星", height=0.62)
        left_edge += values
    right.set_yticks(y, labels)
    right.invert_yaxis()
    right.set_xlim(0, 100)
    right.set_xlabel("该组评论中的星级比例（%）")
    right.set_title("B. 与每个候选相连评论的1–5星构成", fontweight="bold")
    right.legend(ncol=5, loc="lower center", bbox_to_anchor=(0.5, -0.15), frameon=False)
    right.grid(axis="x", alpha=0.2)
    for index, row in ordered.reset_index(drop=True).iterrows():
        right.text(
            99.2,
            index,
            f"均值 {row['mean_rating']:.3f}",
            ha="right",
            va="center",
            fontsize=9,
            color="#0F172A",
            bbox={"boxstyle": "round,pad=0.18", "facecolor": "white", "edgecolor": "none", "alpha": 0.78},
        )

    fig.suptitle(
        "候选 +3 与评论星级/VADER的描述性关系（按稳定review_id连接）",
        fontsize=17,
        fontweight="bold",
        y=0.98,
    )
    fig.text(
        0.5,
        0.015,
        "注意：候选证据池可重叠，尚未人工验证；聚类成员概率不是情绪强度；图中差异是描述性关联，不是因果效应。",
        ha="center",
        fontsize=10,
        color="#991B1B",
    )
    fig.tight_layout(rect=(0, 0.055, 1, 0.94))
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.stem + ".tmp" + path.suffix)
    fig.savefig(temporary, dpi=240, bbox_inches="tight")
    plt.close(fig)
    temporary.replace(path)


def _save_english_scatter(summary: pd.DataFrame, path: Path) -> None:
    """Save the requested English-only, single-panel candidate scatter."""

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    baseline = summary.loc[summary["candidate_id"].eq("all_english_reviews")].iloc[0]
    order = ["scenic_awe", "flight_apprehension", "provider_directed_gratitude"]
    candidates = (
        summary.loc[summary["candidate_id"].isin(order)]
        .assign(_order=lambda frame: frame["candidate_id"].map({value: index for index, value in enumerate(order)}))
        .sort_values("_order", kind="stable")
    )
    colors = {
        "scenic_awe": "#7C3AED",
        "flight_apprehension": "#DC2626",
        "provider_directed_gratitude": "#059669",
    }

    fig, axis = plt.subplots(figsize=(9.2, 7.4))
    for row in candidates.itertuples(index=False):
        size = 260 + 0.24 * row.unique_reviews
        axis.scatter(
            row.mean_review_vader_compound,
            row.mean_rating,
            s=size,
            color=colors[row.candidate_id],
            edgecolor="white",
            linewidth=1.5,
            alpha=0.86,
        )
        axis.annotate(
            f"{row.display_label}\nn={row.unique_reviews:,}",
            (row.mean_review_vader_compound, row.mean_rating),
            xytext=(8, 8),
            textcoords="offset points",
            fontsize=10.5,
            fontweight="semibold",
        )
    axis.axhline(float(baseline["mean_rating"]), color="#EF4444", linestyle=":", linewidth=1.5)
    axis.axvline(float(baseline["mean_review_vader_compound"]), color="#64748B", linestyle="--", linewidth=1.25)
    axis.set_xlabel("Mean review-level VADER compound score", fontsize=11)
    axis.set_ylabel("Mean star rating of linked reviews", fontsize=11)
    axis.set_title(
        "Provisional +3 Candidate Evidence Pools and Linked Review Outcomes\n"
        "(Zoomed descriptive means; stable review_id links)",
        fontsize=14,
        fontweight="bold",
    )
    axis.set_xlim(0.86, 0.945)
    axis.set_ylim(4.74, 4.98)
    axis.grid(alpha=0.22)
    axis.text(
        0.862,
        4.747,
        "Dashed lines: all canonical English reviews\n"
        f"VADER={baseline['mean_review_vader_compound']:.3f}; rating={baseline['mean_rating']:.3f}\n"
        "Bubble area = number of linked reviews",
        fontsize=9.2,
        color="#475569",
        va="bottom",
    )
    fig.text(
        0.5,
        0.012,
        "Provisional overlapping evidence pools; not human-validated. Descriptive association, not a causal effect.",
        ha="center",
        fontsize=9.2,
        color="#991B1B",
    )
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.stem + ".tmp" + path.suffix)
    fig.savefig(temporary, dpi=240, bbox_inches="tight")
    plt.close(fig)
    temporary.replace(path)


def run_candidate_review_relationship(config: ProjectConfig, force: bool = False) -> Dict[str, object]:
    output_dir = config.output_dir
    report_dir = output_dir / "reports"
    plot_path = output_dir / "plots" / "provisional_plus3_review_relationship.png"
    english_plot_path = output_dir / "plots" / "provisional_plus3_review_relationship_english.png"
    manifest_path = output_dir / "manifests" / "stage_candidate_review_relationship.json"
    canonical_path = config.input_path("canonical_reviews")
    full_path = output_dir / "clusters" / "cluster_assignments.csv"
    focused_path = output_dir / "focused" / "cluster_assignments.csv"
    expected = {
        "stage": "provisional-candidate-review-relationship-v1",
        "candidate_config_sha256": sha256_json(config.raw["post_cluster_candidate_synthesis"]),
        "canonical_sha256": sha256_file(canonical_path),
        "full_assignments_sha256": sha256_file(full_path),
        "focused_assignments_sha256": sha256_file(focused_path),
        "stage_code_sha256": sha256_file(Path(__file__)),
    }
    required = (
        report_dir / "provisional_plus3_review_links.csv",
        report_dir / "provisional_plus3_review_relationship_summary.csv",
        plot_path,
        english_plot_path,
    )
    if refuse_stale_outputs(manifest_path, expected, force):
        missing = [str(path) for path in required if not path.exists()]
        if missing:
            raise RuntimeError(f"Current manifest has missing outputs: {missing}")
        return {"status": "skipped"}

    canonical = pd.read_csv(canonical_path, low_memory=False)
    full = pd.read_csv(full_path, low_memory=False)
    focused = pd.read_csv(focused_path, low_memory=False)
    _, review_links = build_candidate_review_links(
        canonical,
        full,
        focused,
        config.raw["post_cluster_candidate_synthesis"]["candidate_families"],
    )
    summary = summarize_candidate_reviews(canonical, review_links)
    atomic_write_csv(review_links, report_dir / "provisional_plus3_review_links.csv")
    atomic_write_csv(summary, report_dir / "provisional_plus3_review_relationship_summary.csv")
    _save_plot(summary, plot_path)
    _save_english_scatter(summary, english_plot_path)
    result = {
        "candidate_review_links": int(len(review_links)),
        "candidate_count": int(summary["candidate_id"].ne("all_english_reviews").sum()),
        "human_validation_status": "pending",
        "interpretation": "descriptive_association_not_causal",
    }
    atomic_write_json(
        {"inputs": expected, "summary": result, "environment": environment_manifest(config.repository_root)},
        manifest_path,
    )
    return result
