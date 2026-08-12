"""Restartable stage builder for corpus-derived emotion-word induction."""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
from pathlib import Path
from typing import Any

import nltk
import numpy as np
import pandas as pd

from . import __version__
from .annotation import build_ai_tasks, write_jsonl, write_review_workbook
from .config import LexiconConfig
from .sampling import make_disjoint_sample_manifest
from .words import build_candidate_inventory, extract_stage_occurrences, require_nltk_resources


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git_state(root: Path) -> dict[str, Any]:
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
        dirty = bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=root, text=True).strip())
        return {"commit": commit, "dirty": dirty}
    except (OSError, subprocess.CalledProcessError):
        return {"commit": None, "dirty": None}


def build_stage(config: LexiconConfig, stage_name: str) -> dict[str, Any]:
    raw = config.raw
    stages = list(raw["sampling"]["disjoint_stages"])
    stage_by_name = {str(stage["name"]): stage for stage in stages}
    if stage_name not in stage_by_name:
        raise ValueError(f"stage must be one of configured disjoint stages: {sorted(stage_by_name)}")
    stage_size = int(stage_by_name[stage_name]["size"])
    require_nltk_resources(raw["tokenization"]["nltk_resources"])

    canonical_path = config.input_path("canonical_reviews")
    tour_path = config.input_path("review_tour_links")
    canonical = pd.read_csv(canonical_path, low_memory=False)
    status_column = raw["corpus"]["language_status_column"]
    accepted_status = raw["corpus"]["accepted_language_status"]
    english = canonical[canonical[status_column].eq(accepted_status)].copy()
    if english.empty:
        raise ValueError("No canonical English reviews were selected")
    if english["review_id"].duplicated().any():
        raise ValueError("Canonical English reviews contain duplicate review_id values")
    empty_text = english[raw["corpus"]["text_field"]].fillna("").astype(str).str.strip().eq("")

    preserve_fields = list(dict.fromkeys(raw["corpus"]["preserve_fields"]))
    missing_preserve_fields = sorted(set(preserve_fields) - set(english.columns))
    if missing_preserve_fields:
        raise ValueError(f"Configured corpus fields do not exist: {missing_preserve_fields}")
    discovery_reviews = english[preserve_fields].copy()

    links = pd.read_csv(tour_path, low_memory=False)
    manifest = make_disjoint_sample_manifest(
        discovery_reviews,
        links,
        seed=int(raw["random_seed"]),
        stages=stages,
        balance_columns=list(raw["sampling"]["balance_columns"]),
        balance_strength_per_column=float(raw["sampling"]["balance_strength_per_column"]),
        maximum_relative_weight=float(raw["sampling"]["maximum_relative_weight"]),
        length_bin_edges=list(raw["sampling"]["length_bin_edges"]),
    )
    sample = manifest[manifest[f"in_{stage_name}"]].copy()
    sample = sample.sort_values("sampling_rank", kind="stable")

    occurrences = extract_stage_occurrences(
        sample,
        text_field=raw["corpus"]["text_field"],
        minimum_letters=int(raw["tokenization"]["minimum_letters"]),
        eligible_coarse_pos=list(raw["tokenization"]["eligible_coarse_pos"]),
        maximum_context_characters=int(raw["tokenization"]["maximum_context_characters"]),
        lemmatization_method=str(raw["tokenization"]["lemmatization_method"]),
    )
    inventory = build_candidate_inventory(
        occurrences, examples_per_word=int(raw["tokenization"]["examples_per_word"])
    )
    tasks = build_ai_tasks(
        sample,
        occurrences,
        instruction_version=raw["annotation"]["instruction_version"],
        text_field=raw["corpus"]["text_field"],
        allowed_statuses=list(raw["annotation"]["allowed_statuses"]),
    )

    output = config.output_dir
    sampling_dir = output / "sampling"
    stage_dir = output / f"stage_{stage_name}"
    audit_dir = output / "audit"
    manifest_dir = output / "manifests"
    for directory in [sampling_dir, stage_dir, audit_dir, manifest_dir]:
        directory.mkdir(parents=True, exist_ok=True)

    sample_manifest_path = sampling_dir / "disjoint_sample_manifest.csv"
    sample_path = stage_dir / f"sample_{stage_name}_reviews.csv"
    occurrences_path = stage_dir / f"unigram_occurrences_{stage_name}.csv"
    inventory_path = stage_dir / f"unigram_candidates_{stage_name}.csv"
    tasks_path = stage_dir / f"ai_tasks_{stage_name}.jsonl"
    workbook_path = stage_dir / f"emotion_word_codebook_{stage_name}.xlsx"
    exclusions_path = audit_dir / "canonical_rows_outside_english_corpus.csv"
    empty_path = audit_dir / "empty_english_review_text.csv"

    manifest.to_csv(sample_manifest_path, index=False, encoding="utf-8-sig")
    sample.to_csv(sample_path, index=False, encoding="utf-8-sig")
    occurrences.to_csv(occurrences_path, index=False, encoding="utf-8-sig")
    inventory.to_csv(inventory_path, index=False, encoding="utf-8-sig")
    write_jsonl(tasks_path, tasks)
    write_review_workbook(
        workbook_path,
        sample,
        inventory,
        stage_size=stage_size,
        forbidden_lexicons=list(raw["annotation"]["external_lexicons_forbidden_during_discovery"]),
    )
    canonical[~canonical[status_column].eq(accepted_status)].to_csv(
        exclusions_path, index=False, encoding="utf-8-sig"
    )
    english[empty_text].to_csv(empty_path, index=False, encoding="utf-8-sig")

    output_paths = [
        sample_manifest_path,
        sample_path,
        occurrences_path,
        inventory_path,
        tasks_path,
        workbook_path,
        exclusions_path,
        empty_path,
    ]
    summary = {
        "stage": "corpus-derived-emotion-unigram-induction-v1",
        "sampling_stage": stage_name,
        "stage_size": stage_size,
        "random_seed": int(raw["random_seed"]),
        "canonical_rows": int(len(canonical)),
        "canonical_english_rows": int(len(english)),
        "empty_english_review_text_rows": int(empty_text.sum()),
        "sample_rows": int(len(sample)),
        "unigram_occurrence_rows": int(len(occurrences)),
        "eligible_occurrence_rows": int(occurrences["candidate_eligible"].sum()),
        "candidate_lemmas": int(len(inventory)),
        "ai_task_rows": int(len(tasks)),
        "discovery_uses_external_emotion_lexicons": False,
        "inputs": {
            str(canonical_path): sha256_file(canonical_path),
            str(tour_path): sha256_file(tour_path),
            str(config.config_path): sha256_file(config.config_path),
        },
        "outputs": {str(path): sha256_file(path) for path in output_paths},
        "environment": {
            "module_version": __version__,
            "python": platform.python_version(),
            "pandas": pd.__version__,
            "numpy": np.__version__,
            "nltk": nltk.__version__,
            "git": git_state(config.repository_root),
        },
    }
    summary_path = manifest_dir / f"stage_{stage_name}.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    return summary
