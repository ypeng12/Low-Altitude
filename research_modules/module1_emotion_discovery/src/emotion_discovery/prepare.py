"""Stage 1: immutable corpus joins, language audit, and span preparation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd

from . import NRC_EMOTIONS
from .config import ProjectConfig
from .ids import stable_review_id
from .language import audit_languages
from .segmentation import segment_review
from .storage import (
    atomic_write_csv,
    atomic_write_json,
    environment_manifest,
    refuse_stale_outputs,
    sha256_file,
    sha256_json,
)


MASTER_REQUIRED = {
    "user_name",
    "review_title",
    "review_text",
    "tour_name",
    "language",
    "is_english",
    "sentiment_polarity",
    "sentiment_pos",
    "sentiment_neg",
}
NRC_COLUMNS = tuple(f"nrc_{emotion}" for emotion in NRC_EMOTIONS)


def _read_with_ids(path: Path, required: set[str]) -> pd.DataFrame:
    frame = pd.read_csv(path, low_memory=False)
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"Required columns missing from {path}: {missing}")
    frame.insert(
        0,
        "review_id",
        [stable_review_id(user, text) for user, text in zip(frame["user_name"], frame["review_text"])],
    )
    duplicate_ids = frame[frame["review_id"].duplicated(keep=False)]
    if not duplicate_ids.empty:
        raise ValueError(
            f"Stable review_id is not unique in {path}: {len(duplicate_ids)} duplicate rows"
        )
    return frame


def join_nrc_baseline(master: pd.DataFrame, nrc: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Join NRC by content identity, never by order, and return a join audit."""

    baseline = nrc.loc[:, ["review_id", *NRC_COLUMNS]].copy()
    joined = master.merge(baseline, on="review_id", how="left", validate="one_to_one", indicator=True)
    audit = joined.loc[
        joined["_merge"] != "both",
        ["review_id", "review_title", "tour_name", "_merge"],
    ].rename(columns={"_merge": "join_status"})
    joined = joined.drop(columns="_merge")
    return joined, audit


def _prepare_expected(config: ProjectConfig) -> Dict[str, object]:
    return {
        "stage_config_sha256": sha256_json(
            {
                "random_seed": config.random_seed,
                "language": config.raw["language"],
                "segmentation": config.raw["segmentation"],
            }
        ),
        "master_sha256": sha256_file(config.input_path("master_reviews")),
        "nrc_sha256": sha256_file(config.input_path("nrc_reviews")),
        "fasttext_model_sha256": sha256_file(config.input_path("fasttext_language_model")),
        "stage": "prepare-v1",
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

    master = _read_with_ids(config.input_path("master_reviews"), MASTER_REQUIRED)
    nrc = _read_with_ids(config.input_path("nrc_reviews"), {"user_name", "review_text", *NRC_COLUMNS})
    joined, nrc_audit = join_nrc_baseline(master, nrc)

    language_config = config.raw["language"]
    language_audit = audit_languages(
        joined,
        config.input_path("fasttext_language_model"),
        text_fields=language_config["text_fields"],
        english_label=language_config["english_label"],
        include_probability=float(language_config["include_probability"]),
        uncertain_probability=float(language_config["uncertain_probability"]),
        top_k=int(language_config["top_k"]),
    )
    source_language = joined.loc[:, ["review_id", "language", "is_english"]].rename(
        columns={"language": "source_language", "is_english": "source_is_english"}
    )
    language_audit = language_audit.merge(source_language, on="review_id", validate="one_to_one")
    language_audit["source_disagrees"] = (
        language_audit["source_is_english"].astype(bool)
        != (language_audit["language_decision"] == "english")
    )

    joined = joined.merge(
        language_audit.loc[:, ["review_id", "fasttext_label", "fasttext_probability", "language_decision"]],
        on="review_id",
        validate="one_to_one",
    )
    excluded_reviews = joined.loc[joined["language_decision"] != "english"].copy()
    excluded_reviews["exclusion_reason"] = excluded_reviews["language_decision"].map(
        {"non_english": "fasttext_non_english", "uncertain": "fasttext_uncertain"}
    )
    excluded_reviews["review_excerpt"] = excluded_reviews["review_text"].fillna("").str.slice(0, 500)
    excluded_reviews = excluded_reviews.loc[
        :,
        [
            "review_id",
            "exclusion_reason",
            "fasttext_label",
            "fasttext_probability",
            "language",
            "is_english",
            "review_title",
            "review_excerpt",
        ],
    ]

    included = joined.loc[joined["language_decision"] == "english"].copy()
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

    atomic_write_csv(corpus, intermediate_dir / "corpus_reviews.csv")
    atomic_write_csv(sentences_frame, intermediate_dir / "sentences.csv")
    atomic_write_csv(spans_frame, intermediate_dir / "analysis_spans.csv")
    atomic_write_csv(language_audit, audit_dir / "language_audit.csv")
    atomic_write_csv(excluded_reviews, audit_dir / "excluded_reviews.csv")
    atomic_write_csv(excluded_spans, audit_dir / "excluded_spans.csv")
    atomic_write_csv(nrc_audit, audit_dir / "nrc_join_audit.csv")

    summary = {
        "source_reviews": int(len(master)),
        "included_english_reviews": int(len(corpus)),
        "excluded_reviews": int(len(excluded_reviews)),
        "uncertain_language_reviews": int((language_audit["language_decision"] == "uncertain").sum()),
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
