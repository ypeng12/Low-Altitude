"""Build a human-review packet for corpus-derived cluster adjudication."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Dict, Iterable

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


HUMAN_COLUMNS = (
    "reviewer_1_cluster_type",
    "reviewer_1_candidate_emotion_label",
    "reviewer_1_nrc_parent_if_applicable",
    "reviewer_1_emotion_evidence_fraction",
    "reviewer_1_candidate_for_plus3",
    "reviewer_1_notes",
    "reviewer_2_cluster_type",
    "reviewer_2_candidate_emotion_label",
    "reviewer_2_nrc_parent_if_applicable",
    "reviewer_2_emotion_evidence_fraction",
    "reviewer_2_candidate_for_plus3",
    "reviewer_2_notes",
    "adjudicated_cluster_type",
    "adjudicated_candidate_emotion_label",
    "adjudicated_nrc_parent_if_applicable",
    "adjudicated_candidate_for_plus3",
    "adjudication_notes",
)


def _add_missing_columns(frame: pd.DataFrame, columns: Iterable[str]) -> pd.DataFrame:
    output = frame.copy()
    for column in columns:
        if column not in output.columns:
            output[column] = ""
    return output


def combine_cluster_sources(
    full_inventory: pd.DataFrame,
    focused_inventory: pd.DataFrame,
    profiles: pd.DataFrame,
    examples: pd.DataFrame,
) -> pd.DataFrame:
    """Combine two discovery views without collapsing their cluster identities."""

    full = full_inventory.copy()
    full.insert(0, "discovery_view", "full_unsupervised")
    focused = focused_inventory.copy()
    focused.insert(0, "discovery_view", "cate_focused")
    inventories = pd.concat([full, focused], ignore_index=True, sort=False)
    if inventories.duplicated(["discovery_view", "cluster_id"]).any():
        raise ValueError("Cluster inventory keys are not unique")
    if profiles.duplicated(["discovery_view", "cluster_id"]).any():
        raise ValueError("GoEmotions profile keys are not unique")

    profile_summary = profiles.loc[
        :,
        [
            "discovery_view",
            "cluster_id",
            "reference_examples",
            "goemotions_profile_top_labels",
            "goemotions_profile_max_probability",
            "goemotions_top_label_agreement",
        ],
    ]
    review = inventories.merge(
        profile_summary,
        on=["discovery_view", "cluster_id"],
        how="left",
        validate="one_to_one",
    )
    if review["reference_examples"].isna().any():
        raise ValueError("Some clusters have no GoEmotions reference profile")

    if examples.duplicated(["discovery_view", "cluster_id", "rank"]).any():
        raise ValueError("Representative example ranks are not unique")
    pivoted = examples.pivot(
        index=["discovery_view", "cluster_id"], columns="rank", values="span_text"
    )
    pivoted.columns = [f"representative_example_{int(rank):02d}" for rank in pivoted.columns]
    pivoted = pivoted.reset_index()
    review = review.merge(
        pivoted,
        on=["discovery_view", "cluster_id"],
        how="left",
        validate="one_to_one",
    )
    if review.filter(like="representative_example_").isna().all(axis=1).any():
        raise ValueError("Some clusters have no representative examples")
    return _add_missing_columns(review, HUMAN_COLUMNS)


def _atomic_write_workbook(sheets: Dict[str, pd.DataFrame], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(suffix=".xlsx", dir=path.parent, delete=False) as handle:
        temporary = Path(handle.name)
    try:
        with pd.ExcelWriter(temporary, engine="openpyxl") as writer:
            for name, frame in sheets.items():
                frame.to_excel(writer, sheet_name=name, index=False)
                worksheet = writer.book[name]
                worksheet.freeze_panes = "A2"
                worksheet.auto_filter.ref = worksheet.dimensions
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def _expected(config: ProjectConfig) -> Dict[str, object]:
    output_dir = config.output_dir
    paths = {
        "full_inventory": output_dir / "reports" / "cluster_inventory.csv",
        "full_examples": output_dir / "reports" / "cluster_representative_examples.csv",
        "focused_inventory": output_dir / "focused" / "cluster_inventory.csv",
        "focused_examples": output_dir / "focused" / "cluster_representative_examples.csv",
        "goemotions_profiles": output_dir / "reference" / "goemotions" / "cluster_profiles.csv",
        "goemotions_links": output_dir / "reference" / "goemotions" / "reference_example_links.csv",
    }
    return {
        "stage": "module1-cluster-human-review-packet-v1",
        "inputs": {name: sha256_file(path) for name, path in paths.items()},
        "stage_code_sha256": sha256_file(Path(__file__)),
    }


def run_review_packet(config: ProjectConfig, force: bool = False) -> Dict[str, object]:
    """Create CSV and XLSX templates without fabricating human decisions."""

    output_dir = config.output_dir
    review_dir = output_dir / "human_review"
    manifest_path = output_dir / "manifests" / "stage07_review_packet.json"
    required = (
        review_dir / "cluster_review_template.csv",
        review_dir / "cluster_examples_for_review.csv",
        review_dir / "module1_cluster_review_packet.xlsx",
        review_dir / "summary.json",
    )
    expected = _expected(config)
    if refuse_stale_outputs(manifest_path, expected, force):
        missing = [str(path) for path in required if not path.exists()]
        if missing:
            raise RuntimeError(f"Review packet manifest is current but outputs are missing: {missing}")
        return {"status": "skipped"}

    full_inventory = pd.read_csv(output_dir / "reports" / "cluster_inventory.csv", low_memory=False)
    focused_inventory = pd.read_csv(output_dir / "focused" / "cluster_inventory.csv", low_memory=False)
    profiles = pd.read_csv(output_dir / "reference" / "goemotions" / "cluster_profiles.csv")
    examples = pd.read_csv(output_dir / "reference" / "goemotions" / "reference_example_links.csv")
    review = combine_cluster_sources(full_inventory, focused_inventory, profiles, examples)

    preferred = [
        "discovery_view",
        "cluster_id",
        "cluster_size",
        "unique_reviews",
        "corpus_derived_phrase_label",
        "representative_words_phrases",
        "representative_cate_terms",
        "mean_membership_probability",
        "seed_stability_jaccard",
        "grid_stability_jaccard",
        "centroid_coherence",
        "review_level_nrc_parent_reference",
        "review_level_affect_signal",
        "automated_screening_score",
        "screening_priority",
        "reference_examples",
        "goemotions_profile_top_labels",
        "goemotions_profile_max_probability",
        "goemotions_top_label_agreement",
    ]
    example_columns = sorted(column for column in review.columns if column.startswith("representative_example_"))
    ordered = [column for column in preferred if column in review.columns]
    ordered += example_columns + list(HUMAN_COLUMNS)
    review = review.loc[:, ordered]

    instructions = pd.DataFrame(
        [
            ("purpose", "Decide which corpus clusters express emotions before selecting exactly three domain candidates."),
            ("independent_review", "Reviewer 1 and Reviewer 2 code independently before adjudication."),
            ("first_decision", "Classify cluster type before naming an emotion."),
            ("do_not_force", "Topic, entity, template, appraisal, mechanism, mixed, and uncertain clusters are valid non-emotion outcomes."),
            ("corpus_phrase_role", "Corpus-derived phrases summarize wording; they are not emotion labels."),
            ("goemotions_role", "Continuous GoEmotions values are reference signals only, not gold labels or +3 decisions."),
            ("nrc_role", "NRC remains the fixed 8-emotion baseline and parent reference."),
            ("evidence_fraction", "Estimate the fraction from 0 to 1 of representative examples that support the proposed emotion."),
            ("plus3_rule", "Nominate only coherent emotions beyond NRC8; final selection follows adjudication and cross-cluster consolidation."),
            ("uncertainty", "Use uncertain and explain why; do not force a label."),
        ],
        columns=["item", "instruction"],
    )
    codebook = pd.DataFrame(
        [
            ("emotion", "A shared experienced affect is evident across the cluster."),
            ("broad_affect", "Positive/negative evaluation is present but no coherent fine-grained emotion is supported."),
            ("aspect_topic", "The cluster is mainly what tourists discuss."),
            ("evaluation_appraisal", "The cluster evaluates worth, quality, beauty, or recommendation rather than naming affect."),
            ("mechanism_trigger", "The cluster mainly describes an event, actor action, or condition causing/changing emotion."),
            ("entity_template", "The cluster is dominated by names, products, locations, or repeated phrasing."),
            ("mixed", "Several incompatible functions or emotions occur."),
            ("uncertain", "Evidence is insufficient for a reliable decision."),
        ],
        columns=["cluster_type", "definition"],
    )
    example_columns_long = [
        "discovery_view",
        "cluster_id",
        "rank",
        "span_id",
        "review_id",
        "span_text",
        "parent_sentence",
        "unit_type",
        "marker_before",
        "centroid_cosine_similarity",
        "membership_probability",
        "goemotions_reference_top_labels",
        "goemotions_reference_max_probability",
    ]
    examples_for_review = examples.loc[:, [c for c in example_columns_long if c in examples.columns]]
    profiles_for_review = profiles.copy()
    summary = {
        "clusters_for_review": int(len(review)),
        "full_unsupervised_clusters": int(review["discovery_view"].eq("full_unsupervised").sum()),
        "cate_focused_clusters": int(review["discovery_view"].eq("cate_focused").sum()),
        "representative_example_links": int(len(examples_for_review)),
        "human_decision_cells_prefilled": 0,
        "requires_independent_human_review": True,
    }
    atomic_write_csv(review, review_dir / "cluster_review_template.csv")
    atomic_write_csv(examples_for_review, review_dir / "cluster_examples_for_review.csv")
    _atomic_write_workbook(
        {
            "instructions": instructions,
            "codebook": codebook,
            "cluster_review": review,
            "representative_examples": examples_for_review,
            "reference_profiles": profiles_for_review,
        },
        review_dir / "module1_cluster_review_packet.xlsx",
    )
    atomic_write_json(summary, review_dir / "summary.json")
    atomic_write_json(
        {"inputs": expected, "summary": summary, "environment": environment_manifest(config.repository_root)},
        manifest_path,
    )
    return summary
