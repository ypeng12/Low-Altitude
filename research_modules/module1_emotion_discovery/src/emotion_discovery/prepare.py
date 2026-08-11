"""Stage 1: segment the authoritative canonical-v2 English corpus."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import pandas as pd

from . import NRC_EMOTIONS
from .config import ProjectConfig
from .segmentation import segment_review
from .storage import (
    atomic_write_csv,
    atomic_write_json,
    environment_manifest,
    refuse_stale_outputs,
    sha256_file,
    sha256_json,
)


NRC_COLUMNS = tuple(f"nrc_{emotion}" for emotion in NRC_EMOTIONS)
CANONICAL_REQUIRED = {
    "review_id",
    "review_title",
    "review_text",
    "legacy_tour_name",
    "legacy_language",
    "legacy_is_english",
    "language_iso",
    "language_confidence",
    "analysis_language_status",
    "analysis_is_english",
    "top_k_predictions",
    "sentiment_polarity",
    "sentiment_pos",
    "sentiment_neg",
    "nrc_baseline_available",
    *NRC_COLUMNS,
}


def validate_canonical_reviews(frame: pd.DataFrame) -> None:
    missing = sorted(CANONICAL_REQUIRED - set(frame.columns))
    if missing:
        raise ValueError(f"Canonical v2 is missing required columns: {missing}")
    if frame.empty or frame["review_id"].isna().any() or frame["review_id"].duplicated().any():
        raise ValueError("Canonical v2 must contain unique, nonempty review_id values")
    allowed = {"english", "non_english", "uncertain"}
    unexpected = sorted(set(frame["analysis_language_status"].dropna()) - allowed)
    if unexpected or frame["analysis_language_status"].isna().any():
        raise ValueError(f"Canonical v2 contains invalid language decisions: {unexpected}")
    expected_english = frame["analysis_language_status"].eq("english")
    actual_english = frame["analysis_is_english"].astype(bool)
    if not expected_english.equals(actual_english):
        raise ValueError("Canonical v2 analysis_is_english disagrees with analysis_language_status")
    missing_nrc = ~frame["nrc_baseline_available"].astype(bool)
    if missing_nrc.any() or frame.loc[:, NRC_COLUMNS].isna().any().any():
        raise ValueError(f"Canonical v2 has {int(missing_nrc.sum())} reviews without the NRC8 baseline")


def _prepare_expected(config: ProjectConfig) -> Dict[str, object]:
    return {
        "stage_config_sha256": sha256_json(
            {"random_seed": config.random_seed, "segmentation": config.raw["segmentation"]}
        ),
        "canonical_reviews_sha256": sha256_file(config.input_path("canonical_reviews")),
        "stage": "canonical-prepare-v2",
    }


def run_prepare(config: ProjectConfig, force: bool = False) -> Dict[str, int]:
    output_dir = config.output_dir
    audit_dir = output_dir / "audit"
    intermediate_dir = output_dir / "intermediate"
    manifest_path = output_dir / "manifests" / "stage01_prepare.json"
    expected = _prepare_expected(config)
    required_outputs = (
        intermediate_dir / "corpus_reviews.csv",
        intermediate_dir / "sentences.csv",
        intermediate_dir / "analysis_spans.csv",
        audit_dir / "language_audit.csv",
        audit_dir / "excluded_reviews.csv",
        audit_dir / "excluded_spans.csv",
        audit_dir / "nrc_join_audit.csv",
    )
    if refuse_stale_outputs(manifest_path, expected, force):
        missing = [str(path) for path in required_outputs if not path.exists()]
        if missing:
            raise RuntimeError(f"Stage manifest is current but outputs are missing: {missing}")
        return {"status": "skipped"}  # type: ignore[return-value]

    canonical = pd.read_csv(config.input_path("canonical_reviews"), low_memory=False)
    validate_canonical_reviews(canonical)
    analysis = canonical.rename(
        columns={
            "legacy_tour_name": "tour_name",
            "language_iso": "fasttext_label",
            "language_confidence": "fasttext_probability",
            "analysis_language_status": "language_decision",
        }
    )
    language_audit = analysis.loc[
        :,
        [
            "review_id",
            "fasttext_label",
            "fasttext_probability",
            "language_decision",
            "top_k_predictions",
            "legacy_language",
            "legacy_is_english",
        ],
    ].rename(
        columns={"legacy_language": "source_language", "legacy_is_english": "source_is_english"}
    )
    language_audit["source_disagrees"] = (
        language_audit["source_is_english"].astype(bool)
        != language_audit["language_decision"].eq("english")
    )

    excluded_reviews = analysis.loc[analysis["language_decision"].ne("english")].copy()
    excluded_reviews["exclusion_reason"] = excluded_reviews["language_decision"].map(
        {"non_english": "canonical_non_english", "uncertain": "canonical_language_uncertain"}
    )
    excluded_reviews["review_excerpt"] = excluded_reviews["review_text"].fillna("").str.slice(0, 500)
    excluded_reviews = excluded_reviews.loc[
        :,
        [
            "review_id",
            "exclusion_reason",
            "fasttext_label",
            "fasttext_probability",
            "legacy_language",
            "legacy_is_english",
            "review_title",
            "review_excerpt",
        ],
    ].rename(columns={"legacy_language": "language", "legacy_is_english": "is_english"})

    included = analysis.loc[analysis["language_decision"].eq("english")].copy()
    corpus_columns = [
        "review_id",
        "review_title",
        "review_text",
        "tour_name",
        "trip_type",
        "published_date",
        "fasttext_label",
        "fasttext_probability",
        "sentiment_polarity",
        "sentiment_pos",
        "sentiment_neg",
        *NRC_COLUMNS,
    ]
    corpus_columns = [column for column in corpus_columns if column in included.columns]
    corpus = included.loc[:, corpus_columns].copy()

    segmentation_config = config.raw["segmentation"]
    sentence_records: List[dict] = []
    span_records: List[dict] = []
    excluded_span_records: List[dict] = []
    for review in corpus.itertuples(index=False):
        text = str(review.review_text) if pd.notna(review.review_text) else ""
        sentences, spans, exclusions = segment_review(
            review.review_id,
            text,
            min_sentence_tokens=int(segmentation_config["min_sentence_tokens"]),
            min_clause_tokens=int(segmentation_config["min_clause_tokens"]),
            max_span_words=int(segmentation_config["max_span_words"]),
            split_long_sentences=bool(segmentation_config["split_long_sentences"]),
            use_clauses_for_analysis=bool(segmentation_config["use_clauses_for_analysis"]),
        )
        sentence_records.extend(sentences)
        span_records.extend(spans)
        excluded_span_records.extend(exclusions)

    sentences_frame = pd.DataFrame.from_records(sentence_records)
    spans_frame = pd.DataFrame.from_records(span_records)
    excluded_spans = pd.DataFrame.from_records(excluded_span_records)
    if spans_frame.empty:
        raise RuntimeError("Segmentation produced no analysis spans")
    if spans_frame["span_id"].duplicated().any():
        raise RuntimeError("Segmentation produced duplicate span IDs")

    span_metadata = corpus.drop(columns=["review_title", "review_text"], errors="ignore")
    spans_frame = spans_frame.merge(span_metadata, on="review_id", how="left", validate="many_to_one")
    reviews_without_spans = corpus.loc[~corpus["review_id"].isin(spans_frame["review_id"])].copy()
    if not reviews_without_spans.empty:
        no_span_audit = reviews_without_spans.loc[:, ["review_id", "review_title"]].copy()
        no_span_audit["exclusion_reason"] = "no_analysis_span"
        excluded_reviews = pd.concat([excluded_reviews, no_span_audit], ignore_index=True, sort=False)

    nrc_audit = canonical.loc[
        ~canonical["nrc_baseline_available"].astype(bool), ["review_id"]
    ].copy()
    nrc_audit["join_issue"] = "canonical_review_missing_nrc8_baseline"
    atomic_write_csv(corpus, intermediate_dir / "corpus_reviews.csv")
    atomic_write_csv(sentences_frame, intermediate_dir / "sentences.csv")
    atomic_write_csv(spans_frame, intermediate_dir / "analysis_spans.csv")
    atomic_write_csv(language_audit, audit_dir / "language_audit.csv")
    atomic_write_csv(excluded_reviews, audit_dir / "excluded_reviews.csv")
    atomic_write_csv(excluded_spans, audit_dir / "excluded_spans.csv")
    atomic_write_csv(nrc_audit, audit_dir / "nrc_join_audit.csv")

    summary = {
        "source_reviews": int(len(canonical)),
        "included_english_reviews": int(len(corpus)),
        "excluded_reviews": int(len(excluded_reviews)),
        "uncertain_language_reviews": int(language_audit["language_decision"].eq("uncertain").sum()),
        "nrc_unmatched_reviews": int(len(nrc_audit)),
        "sentences": int(len(sentences_frame)),
        "analysis_spans": int(len(spans_frame)),
        "excluded_spans": int(len(excluded_spans)),
    }
    manifest = {
        "inputs": expected,
        "summary": summary,
        "environment": environment_manifest(config.repository_root),
    }
    atomic_write_json(manifest, manifest_path)
    return summary
