"""Stage 1: extract auditable discourse-linked source/target span candidates."""

from __future__ import annotations

from pathlib import Path
from typing import Dict

import pandas as pd

from .config import ProjectConfig
from .discourse import MARKER_RELATIONS, marker_relation, stable_transition_id
from .storage import (
    atomic_write_csv,
    atomic_write_json,
    environment_manifest,
    refuse_stale_outputs,
    sha256_file,
    sha256_json,
)


def extract_adjacent_candidates(
    spans: pd.DataFrame,
    sentences: pd.DataFrame,
    review_text_by_id: Dict[str, str],
    minimum_source_tokens: int,
    minimum_target_tokens: int,
    included_relations: set[str],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    required_spans = {
        "review_id",
        "span_id",
        "parent_sentence_id",
        "span_index_within_sentence",
        "span_start",
        "span_end",
        "span_text",
        "token_count",
        "marker_before",
    }
    missing = sorted(required_spans - set(spans.columns))
    if missing:
        raise ValueError(f"Analysis spans are missing columns: {missing}")
    if spans["span_id"].duplicated().any():
        raise ValueError("Analysis spans contain duplicate span_id values")
    required_sentences = {"review_id", "sentence_id", "sentence_text", "sentence_start", "sentence_end"}
    missing = sorted(required_sentences - set(sentences.columns))
    if missing:
        raise ValueError(f"Sentences are missing columns: {missing}")
    if sentences["sentence_id"].duplicated().any():
        raise ValueError("Sentences contain duplicate sentence_id values")

    sentence_lookup = sentences.set_index("sentence_id")
    records = []
    audit = []
    ordered = spans.sort_values(
        ["review_id", "parent_sentence_id", "span_index_within_sentence"], kind="stable"
    )
    for (_, sentence_id), group in ordered.groupby(
        ["review_id", "parent_sentence_id"], sort=False
    ):
        group = group.reset_index(drop=True)
        for position, target in group.iterrows():
            marker = str(target["marker_before"]).strip().casefold() if pd.notna(target["marker_before"]) else ""
            if not marker:
                continue
            base_audit = {
                "review_id": target["review_id"],
                "parent_sentence_id": sentence_id,
                "target_span_id": target["span_id"],
                "transition_marker": marker,
            }
            if position == 0:
                audit.append({**base_audit, "audit_reason": "marker_bearing_span_has_no_predecessor"})
                continue
            relation, structure_confidence = marker_relation(marker)
            if relation not in included_relations:
                audit.append({**base_audit, "audit_reason": "relation_family_not_configured"})
                continue
            source = group.iloc[position - 1]
            if int(source["token_count"]) < minimum_source_tokens:
                audit.append({**base_audit, "audit_reason": "source_below_minimum_tokens"})
                continue
            if int(target["token_count"]) < minimum_target_tokens:
                audit.append({**base_audit, "audit_reason": "target_below_minimum_tokens"})
                continue
            if sentence_id not in sentence_lookup.index:
                audit.append({**base_audit, "audit_reason": "parent_sentence_missing"})
                continue
            sentence = sentence_lookup.loc[sentence_id]
            review_id = str(target["review_id"])
            review_text = review_text_by_id.get(review_id)
            if review_text is None:
                audit.append({**base_audit, "audit_reason": "review_missing_from_canonical"})
                continue
            source_text = str(source["span_text"])
            target_text = str(target["span_text"])
            if review_text[int(source["span_start"]) : int(source["span_end"])] != source_text:
                raise ValueError(f"Source offset mismatch for {source['span_id']}")
            if review_text[int(target["span_start"]) : int(target["span_end"])] != target_text:
                raise ValueError(f"Target offset mismatch for {target['span_id']}")
            transition_id = stable_transition_id(
                review_id,
                str(sentence_id),
                str(source["span_id"]),
                str(target["span_id"]),
                marker,
            )
            records.append(
                {
                    "transition_id": transition_id,
                    "review_id": review_id,
                    "parent_sentence_id": sentence_id,
                    "sentence": sentence["sentence_text"],
                    "sentence_start": int(sentence["sentence_start"]),
                    "sentence_end": int(sentence["sentence_end"]),
                    "source_span_id": source["span_id"],
                    "source_span": source_text,
                    "source_start": int(source["span_start"]),
                    "source_end": int(source["span_end"]),
                    "source_emotion": "",
                    "transition_marker": marker,
                    "discourse_relation_family": relation,
                    "target_span_id": target["span_id"],
                    "target_span": target_text,
                    "target_start": int(target["span_start"]),
                    "target_end": int(target["span_end"]),
                    "target_emotion": "",
                    "transformation_type": "",
                    "trigger_span": "",
                    "actor": "",
                    "mechanism": "",
                    "candidate_structure_confidence": structure_confidence,
                    "confidence": "",
                    "extraction_method": "adjacent_segmented_clause_pair",
                    "requires_human_annotation": True,
                    "annotation_status": "unlabeled_candidate",
                    "uncertainty_reason": "emotion_mechanism_and_transformation_labels_pending",
                }
            )
    candidates = pd.DataFrame.from_records(records)
    audit_frame = pd.DataFrame.from_records(audit)
    if not candidates.empty and candidates["transition_id"].duplicated().any():
        raise ValueError("Transition extraction produced duplicate transition_id values")
    return candidates, audit_frame


def _expected(config: ProjectConfig) -> Dict[str, object]:
    return {
        "stage": "explicit-discourse-candidate-extraction-v1",
        "config_sha256": sha256_json(config.raw["candidate_extraction"]),
        "canonical_sha256": sha256_file(config.input_path("canonical_reviews")),
        "spans_sha256": sha256_file(config.input_path("analysis_spans")),
        "sentences_sha256": sha256_file(config.input_path("sentences")),
        "stage_code_sha256": sha256_file(Path(__file__)),
    }


def run_candidate_extraction(config: ProjectConfig, force: bool = False) -> Dict[str, object]:
    output_dir = config.output_dir
    candidate_dir = output_dir / "candidates"
    audit_dir = output_dir / "audit"
    manifest_path = output_dir / "manifests" / "stage01_candidates.json"
    required = (
        candidate_dir / "explicit_transition_candidates.csv",
        audit_dir / "excluded_discourse_candidates.csv",
        audit_dir / "transition_marker_inventory.csv",
        candidate_dir / "summary.json",
    )
    expected = _expected(config)
    if refuse_stale_outputs(manifest_path, expected, force):
        missing = [str(path) for path in required if not path.exists()]
        if missing:
            raise RuntimeError(f"Transition candidate manifest is current but outputs are missing: {missing}")
        return {"status": "skipped"}

    canonical = pd.read_csv(
        config.input_path("canonical_reviews"),
        usecols=["review_id", "review_text", "analysis_language_status"],
        low_memory=False,
    )
    if canonical["review_id"].duplicated().any():
        raise ValueError("Canonical reviews contain duplicate review_id values")
    english = canonical.loc[canonical["analysis_language_status"].eq("english")]
    review_text_by_id = dict(zip(english["review_id"].astype(str), english["review_text"].fillna("").astype(str)))
    spans = pd.read_csv(config.input_path("analysis_spans"), low_memory=False)
    sentences = pd.read_csv(config.input_path("sentences"), low_memory=False)
    outside = set(spans["review_id"].astype(str)) - set(review_text_by_id)
    if outside:
        raise ValueError(f"Analysis spans include {len(outside)} non-canonical-English reviews")

    settings = config.raw["candidate_extraction"]
    candidates, audit = extract_adjacent_candidates(
        spans,
        sentences,
        review_text_by_id,
        minimum_source_tokens=int(settings["minimum_source_tokens"]),
        minimum_target_tokens=int(settings["minimum_target_tokens"]),
        included_relations=set(settings["include_relation_families"]),
    )
    marker_rows = spans.loc[spans["marker_before"].notna() & spans["marker_before"].astype(str).str.strip().ne("")].copy()
    marker_rows["transition_marker"] = marker_rows["marker_before"].astype(str).str.strip().str.casefold()
    marker_rows[["discourse_relation_family", "default_structure_confidence"]] = marker_rows[
        "transition_marker"
    ].map(marker_relation).apply(pd.Series)
    inventory = (
        marker_rows.groupby(
            ["transition_marker", "discourse_relation_family", "default_structure_confidence"],
            dropna=False,
        )
        .size()
        .reset_index(name="marker_bearing_spans")
        .sort_values("marker_bearing_spans", ascending=False, kind="stable")
    )
    disposition_total = len(candidates) + len(audit)
    if disposition_total != len(marker_rows):
        raise RuntimeError(
            f"Marker disposition mismatch: markers={len(marker_rows)}, candidates+audit={disposition_total}"
        )
    summary = {
        "english_reviews": int(len(english)),
        "analysis_spans": int(len(spans)),
        "marker_bearing_spans": int(len(marker_rows)),
        "explicit_transition_candidates": int(len(candidates)),
        "audited_exclusions": int(len(audit)),
        "candidate_reviews": int(candidates["review_id"].nunique()) if not candidates.empty else 0,
        "emotion_labels_filled": 0,
        "mechanism_labels_filled": 0,
        "gold_standard_status": "not_created",
    }
    atomic_write_csv(candidates, candidate_dir / "explicit_transition_candidates.csv")
    atomic_write_csv(audit, audit_dir / "excluded_discourse_candidates.csv")
    atomic_write_csv(inventory, audit_dir / "transition_marker_inventory.csv")
    atomic_write_json(summary, candidate_dir / "summary.json")
    atomic_write_json(
        {"inputs": expected, "summary": summary, "environment": environment_manifest()},
        manifest_path,
    )
    return summary
