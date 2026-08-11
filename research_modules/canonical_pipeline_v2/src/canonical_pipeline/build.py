"""Build the immutable canonical v2 layer and all associated audits."""

from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Dict, Iterable, Tuple

import pandas as pd

from . import NRC_EMOTIONS, __version__
from .cate import validate_cate_workbook
from .config import ProjectConfig
from .drift import audit_dataset_drift
from .ids import stable_review_id
from .language import audit_languages
from .storage import atomic_write_csv, atomic_write_json, environment_manifest, sha256_file
from .taxonomy import ASPECT_PATTERNS, categorize_incongruence, extract_aspects, legacy_categorize_incongruence
from .tour_links import build_review_tour_links


NRC_COLUMNS = tuple(f"nrc_{emotion}" for emotion in NRC_EMOTIONS)
MASTER_REQUIRED = {
    "user_name",
    "review_text",
    "rating",
    "language",
    "is_english",
    "sentiment_polarity",
    "sentiment_neg",
}
LANGUAGE_REQUIRED = {
    "review_id",
    "fasttext_label",
    "fasttext_probability",
    "language_decision",
    "top_k_predictions",
}


def _with_ids(path: Path, required: Iterable[str]) -> pd.DataFrame:
    frame = pd.read_csv(path, low_memory=False)
    missing = sorted(set(required) - set(frame.columns))
    if missing:
        raise ValueError(f"Required columns missing from {path}: {missing}")
    frame.insert(
        0,
        "review_id",
        [stable_review_id(user, text) for user, text in zip(frame["user_name"], frame["review_text"])],
    )
    duplicate = frame[frame["review_id"].duplicated(keep=False)]
    if not duplicate.empty:
        raise ValueError(f"Non-unique review_id in {path}: {len(duplicate)} rows")
    return frame


def join_nrc(master: pd.DataFrame, nrc: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    baseline = nrc.loc[:, ["review_id", *NRC_COLUMNS]].copy()
    joined = master.merge(baseline, on="review_id", how="left", validate="one_to_one", indicator=True)
    missing_from_nrc = joined.loc[joined["_merge"] == "left_only", ["review_id"]].copy()
    missing_from_nrc["join_issue"] = "master_review_missing_from_nrc"
    extra = nrc.loc[~nrc["review_id"].isin(master["review_id"]), ["review_id"]].copy()
    extra["join_issue"] = "nrc_review_missing_from_master"
    audit = pd.concat([missing_from_nrc, extra], ignore_index=True)
    joined = joined.drop(columns="_merge")
    joined["nrc_baseline_available"] = joined.loc[:, NRC_COLUMNS].notna().all(axis=1)
    joined["nrc_all_zero"] = joined.loc[:, NRC_COLUMNS].fillna(0).eq(0).all(axis=1)
    return joined, audit


def join_language(master: pd.DataFrame, language: pd.DataFrame) -> pd.DataFrame:
    missing = sorted(LANGUAGE_REQUIRED - set(language.columns))
    if missing:
        raise ValueError(f"Language audit missing columns: {missing}")
    if language["review_id"].duplicated().any():
        raise ValueError("Language audit contains duplicate review_id values")
    selected = language.loc[:, sorted(LANGUAGE_REQUIRED)].copy()
    joined = master.merge(selected, on="review_id", how="left", validate="one_to_one")
    if joined["language_decision"].isna().any():
        raise ValueError(f"Language audit is missing {int(joined['language_decision'].isna().sum())} master reviews")
    allowed = {"english", "non_english", "uncertain"}
    unexpected = sorted(set(joined["language_decision"]) - allowed)
    if unexpected:
        raise ValueError(f"Unexpected language decisions: {unexpected}")
    joined = joined.rename(
        columns={
            "fasttext_label": "language_iso",
            "fasttext_probability": "language_confidence",
            "language_decision": "analysis_language_status",
        }
    )
    joined["analysis_is_english"] = joined["analysis_language_status"].eq("english")
    return joined


def _input_fingerprints(config: ProjectConfig) -> Dict[str, object]:
    raw_files = sorted(config.input_path("raw_reviews_dir").glob("*.csv"), key=lambda path: path.name.casefold())
    return {
        "pipeline_version": __version__,
        "config_sha256": sha256_file(config.config_path),
        "master_sha256": sha256_file(config.input_path("master_reviews")),
        "level1_sha256": sha256_file(config.input_path("level1_reviews")),
        "level2_sha256": sha256_file(config.input_path("level2_reviews")),
        "nrc_sha256": sha256_file(config.input_path("nrc_reviews")),
        "fasttext_language_model_sha256": sha256_file(config.input_path("fasttext_language_model")),
        "cate_workbook_sha256": sha256_file(config.input_path("cate_workbook")),
        "raw_files": [{"name": path.name, "sha256": sha256_file(path)} for path in raw_files],
    }


def _required_outputs(output_dir: Path) -> list[Path]:
    return [
        output_dir / "canonical" / "canonical_reviews_v2.csv",
        output_dir / "provenance" / "review_tour_links_v2.csv",
        output_dir / "provenance" / "raw_review_occurrences_v2.csv",
        output_dir / "legacy_rebuild" / "deep_research_quintuple_extracted_v2.csv",
        output_dir / "legacy_rebuild" / "incongruence_taxonomy_summary_v2.csv",
        output_dir / "audit" / "language_disagreements_v2.csv",
        output_dir / "audit" / "language_audit_v2.csv",
        output_dir / "audit" / "uncertain_language_reviews_v2.csv",
        output_dir / "audit" / "nrc_join_issues_v2.csv",
        output_dir / "audit" / "taxonomy_corrections_v2.csv",
        output_dir / "audit" / "raw_occurrences_not_in_master_v2.csv",
        output_dir / "audit" / "dataset_membership_v2.csv",
        output_dir / "audit" / "dataset_field_drift_summary_v2.csv",
        output_dir / "audit" / "dataset_field_drift_details_v2.csv",
        output_dir / "manifests" / "canonical_v2.json",
    ]


def _is_current(manifest_path: Path, fingerprints: Dict[str, object], outputs: list[Path]) -> bool:
    if not manifest_path.exists() or any(not path.exists() for path in outputs):
        return False
    with manifest_path.open(encoding="utf-8") as handle:
        manifest = json.load(handle)
    return manifest.get("inputs") == fingerprints


def run_build(config: ProjectConfig, force: bool = False) -> Dict[str, object]:
    random.seed(int(config.raw["random_seed"]))
    output_dir = config.output_dir
    manifest_path = output_dir / "manifests" / "canonical_v2.json"
    required_outputs = _required_outputs(output_dir)
    fingerprints = _input_fingerprints(config)
    if not force and _is_current(manifest_path, fingerprints, required_outputs):
        return {"status": "skipped", "reason": "all inputs and outputs are current"}

    _, cate_audit = validate_cate_workbook(
        config.input_path("cate_workbook"),
        sheet_name=config.raw["cate"]["sheet_name"],
        expected_rows=int(config.raw["cate"]["expected_rows"]),
    )

    master_source = _with_ids(config.input_path("master_reviews"), MASTER_REQUIRED)
    level1 = _with_ids(config.input_path("level1_reviews"), {"user_name", "review_text"})
    level2 = _with_ids(config.input_path("level2_reviews"), {"user_name", "review_text"})
    nrc = _with_ids(config.input_path("nrc_reviews"), {"user_name", "review_text", *NRC_COLUMNS})
    membership_audit, drift_summary, drift_details = audit_dataset_drift(
        master_source,
        {"level1_cleaned": level1, "level2_features": level2, "level3_econometrics": nrc},
    )
    master = master_source.rename(
        columns={"language": "legacy_language", "is_english": "legacy_is_english", "tour_name": "legacy_tour_name"}
    )
    language_config = config.raw["language"]
    language = audit_languages(
        master_source,
        config.input_path("fasttext_language_model"),
        text_fields=language_config["text_fields"],
        english_label=str(language_config["english_label"]),
        include_probability=float(language_config["include_probability"]),
        uncertain_probability=float(language_config["uncertain_probability"]),
        top_k=int(language_config["top_k"]),
    )
    source_language = master_source.loc[:, ["review_id", "language", "is_english"]].rename(
        columns={"language": "source_language", "is_english": "source_is_english"}
    )
    language = language.merge(source_language, on="review_id", validate="one_to_one")
    language["source_disagrees"] = (
        language["source_is_english"].astype(bool) != language["language_decision"].eq("english")
    )
    canonical = join_language(master, language)
    canonical, nrc_audit = join_nrc(canonical, nrc)

    language_disagreements = canonical.loc[
        canonical["legacy_is_english"].astype(bool) != canonical["analysis_is_english"],
        [
            "review_id",
            "legacy_language",
            "legacy_is_english",
            "language_iso",
            "language_confidence",
            "analysis_language_status",
            "review_title",
            "review_text",
        ],
    ].copy()
    uncertain_language = canonical.loc[
        canonical["analysis_language_status"].eq("uncertain"),
        ["review_id", "language_iso", "language_confidence", "top_k_predictions", "review_title", "review_text"],
    ].copy()

    canonical_ids = set(canonical["review_id"])
    links, occurrences, raw_audit = build_review_tour_links(config.input_path("raw_reviews_dir"), canonical_ids)
    link_counts = links.groupby("review_id").size().rename("linked_tour_count")
    canonical = canonical.merge(link_counts, on="review_id", how="left", validate="one_to_one")
    canonical["linked_tour_count"] = canonical["linked_tour_count"].fillna(0).astype(int)

    rebuilt = canonical.copy()
    rebuilt["aspects_found"] = rebuilt["review_text"].map(lambda value: "|".join(extract_aspects(value)))
    rebuilt["aspect_count"] = rebuilt["aspects_found"].map(lambda value: 0 if not value else len(value.split("|")))
    for aspect in ASPECT_PATTERNS:
        rebuilt[f"aspect_{aspect}"] = rebuilt["aspects_found"].map(lambda value, name=aspect: int(name in value.split("|")))
    records = rebuilt.to_dict("records")
    rebuilt["legacy_incongruence_type"] = [legacy_categorize_incongruence(row) for row in records]
    rebuilt["incongruence_type_v2"] = [categorize_incongruence(row) for row in records]
    rebuilt["classification_changed"] = rebuilt["legacy_incongruence_type"] != rebuilt["incongruence_type_v2"]
    corrections = rebuilt.loc[
        rebuilt["classification_changed"],
        [
            "review_id",
            "legacy_language",
            "language_iso",
            "language_confidence",
            "analysis_language_status",
            "legacy_incongruence_type",
            "incongruence_type_v2",
            "review_title",
            "review_text",
        ],
    ].copy()
    taxonomy_summary = (
        rebuilt["incongruence_type_v2"].value_counts(dropna=False).rename_axis("Incongruence_Mechanism").reset_index(name="Review_Count")
    )
    taxonomy_summary["Percentage"] = (taxonomy_summary["Review_Count"] / len(rebuilt) * 100).round(2)

    atomic_write_csv(canonical, output_dir / "canonical" / "canonical_reviews_v2.csv")
    atomic_write_csv(links, output_dir / "provenance" / "review_tour_links_v2.csv")
    atomic_write_csv(occurrences, output_dir / "provenance" / "raw_review_occurrences_v2.csv")
    atomic_write_csv(rebuilt, output_dir / "legacy_rebuild" / "deep_research_quintuple_extracted_v2.csv")
    atomic_write_csv(taxonomy_summary, output_dir / "legacy_rebuild" / "incongruence_taxonomy_summary_v2.csv")
    atomic_write_csv(language_disagreements, output_dir / "audit" / "language_disagreements_v2.csv")
    atomic_write_csv(language, output_dir / "audit" / "language_audit_v2.csv")
    atomic_write_csv(uncertain_language, output_dir / "audit" / "uncertain_language_reviews_v2.csv")
    atomic_write_csv(nrc_audit, output_dir / "audit" / "nrc_join_issues_v2.csv")
    atomic_write_csv(corrections, output_dir / "audit" / "taxonomy_corrections_v2.csv")
    atomic_write_csv(raw_audit, output_dir / "audit" / "raw_occurrences_not_in_master_v2.csv")
    atomic_write_csv(membership_audit, output_dir / "audit" / "dataset_membership_v2.csv")
    atomic_write_csv(drift_summary, output_dir / "audit" / "dataset_field_drift_summary_v2.csv")
    atomic_write_csv(drift_details, output_dir / "audit" / "dataset_field_drift_details_v2.csv")

    legacy_type9 = rebuilt["legacy_incongruence_type"].eq("Type 9: Multilingual Lexicon Artifact")
    revised_type9 = rebuilt["incongruence_type_v2"].eq("Type 9: Multilingual Lexicon Artifact")
    summary = {
        "canonical_reviews": int(len(canonical)),
        "english_reviews": int(canonical["analysis_is_english"].sum()),
        "non_english_reviews": int(canonical["analysis_language_status"].eq("non_english").sum()),
        "uncertain_language_reviews": int(len(uncertain_language)),
        "language_disagreements": int(len(language_disagreements)),
        "nrc_join_issues": int(len(nrc_audit)),
        "nrc_all_zero_reviews": int(canonical["nrc_all_zero"].sum()),
        "raw_occurrences": int(len(occurrences)),
        "review_tour_links": int(len(links)),
        "reviews_linked_to_multiple_tours": int(link_counts.gt(1).sum()),
        "raw_occurrences_not_in_master": int(len(raw_audit)),
        "dataset_drift_cells": int(len(drift_details)),
        "legacy_type9_reviews": int(legacy_type9.sum()),
        "corrected_type9_reviews": int(revised_type9.sum()),
        "legacy_type9_reclassified": int((legacy_type9 & ~revised_type9).sum()),
        "all_taxonomy_changes": int(rebuilt["classification_changed"].sum()),
    }
    manifest = {
        "stage": "canonical-v2",
        "random_seed": int(config.raw["random_seed"]),
        "inputs": fingerprints,
        "cate_validation": cate_audit,
        "summary": summary,
        "environment": environment_manifest(),
    }
    atomic_write_json(manifest, manifest_path)
    return summary
