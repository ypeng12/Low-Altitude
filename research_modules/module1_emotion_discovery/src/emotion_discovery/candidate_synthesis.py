"""Reproducible LLM-assisted, post-cluster candidate-family synthesis."""

from __future__ import annotations

from pathlib import Path
from typing import Dict

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


VIEW_SOURCES = {
    "full_unsupervised": ("reports/cluster_inventory.csv", "clusters/cluster_assignments.csv"),
    "cate_focused": ("focused/cluster_inventory.csv", "focused/cluster_assignments.csv"),
}


def validate_candidate_configuration(configuration: Dict[str, object]) -> None:
    candidates = configuration["candidate_families"]
    required_count = int(configuration["required_candidate_count"])
    if len(candidates) != required_count:
        raise ValueError(f"Expected exactly {required_count} provisional candidates")
    ids = [item["candidate_id"] for item in candidates]
    if len(ids) != len(set(ids)):
        raise ValueError("Provisional candidate IDs must be unique")
    if str(configuration["status"]) != "llm_assisted_provisional_not_human_validated":
        raise ValueError("Candidate synthesis must not claim human validation")


def _expected(config: ProjectConfig) -> Dict[str, object]:
    output_dir = config.output_dir
    paths = {
        "full_inventory": output_dir / "reports" / "cluster_inventory.csv",
        "full_assignments": output_dir / "clusters" / "cluster_assignments.csv",
        "focused_inventory": output_dir / "focused" / "cluster_inventory.csv",
        "focused_assignments": output_dir / "focused" / "cluster_assignments.csv",
        "reference_links": output_dir / "reference" / "goemotions" / "reference_example_links.csv",
        "reference_profiles": output_dir / "reference" / "goemotions" / "cluster_profiles.csv",
    }
    return {
        "stage": "post-cluster-provisional-candidate-synthesis-v1",
        "config_sha256": sha256_json(config.raw["post_cluster_candidate_synthesis"]),
        "inputs": {name: sha256_file(path) for name, path in paths.items()},
        "stage_code_sha256": sha256_file(Path(__file__)),
    }


def run_candidate_synthesis(config: ProjectConfig, force: bool = False) -> Dict[str, object]:
    output_dir = config.output_dir
    report_dir = output_dir / "reports"
    manifest_path = output_dir / "manifests" / "stage08_candidate_synthesis.json"
    required = (
        report_dir / "provisional_plus3_candidates.csv",
        report_dir / "provisional_plus3_cluster_evidence.csv",
        report_dir / "provisional_plus3_representative_examples.csv",
        report_dir / "deferred_candidate_families.csv",
        report_dir / "provisional_plus3_summary.json",
    )
    expected = _expected(config)
    if refuse_stale_outputs(manifest_path, expected, force):
        missing = [str(path) for path in required if not path.exists()]
        if missing:
            raise RuntimeError(f"Candidate synthesis manifest is current but outputs are missing: {missing}")
        return {"status": "skipped"}

    configuration = config.raw["post_cluster_candidate_synthesis"]
    validate_candidate_configuration(configuration)
    profiles = pd.read_csv(output_dir / "reference" / "goemotions" / "cluster_profiles.csv")
    links = pd.read_csv(output_dir / "reference" / "goemotions" / "reference_example_links.csv")
    inventories = {}
    assignments = {}
    for view, (inventory_path, assignment_path) in VIEW_SOURCES.items():
        inventories[view] = pd.read_csv(output_dir / inventory_path, low_memory=False)
        assignments[view] = pd.read_csv(output_dir / assignment_path, low_memory=False)

    candidate_records = []
    evidence_records = []
    example_frames = []
    for candidate in configuration["candidate_families"]:
        candidate_id = str(candidate["candidate_id"])
        selected_spans = []
        selected_reviews = []
        cluster_sizes = []
        cluster_stabilities = []
        for view, config_key in (
            ("full_unsupervised", "full_unsupervised_clusters"),
            ("cate_focused", "cate_focused_clusters"),
        ):
            for cluster_id in candidate[config_key]:
                cluster_id = int(cluster_id)
                inventory = inventories[view]
                matched = inventory.loc[inventory["cluster_id"].eq(cluster_id)]
                if len(matched) != 1:
                    raise ValueError(f"Unknown or duplicate cluster {view}:{cluster_id}")
                profile = profiles.loc[
                    profiles["discovery_view"].eq(view) & profiles["cluster_id"].eq(cluster_id)
                ]
                if len(profile) != 1:
                    raise ValueError(f"Missing reference profile for {view}:{cluster_id}")
                row = matched.iloc[0]
                evidence_records.append(
                    {
                        "candidate_id": candidate_id,
                        "discovery_view": view,
                        "cluster_id": cluster_id,
                        "cluster_size": int(row["cluster_size"]),
                        "unique_reviews": int(row["unique_reviews"]),
                        "corpus_derived_phrase_label": row["corpus_derived_phrase_label"],
                        "mean_membership_probability": float(row["mean_membership_probability"]),
                        "seed_stability_jaccard": float(row["seed_stability_jaccard"]),
                        "grid_stability_jaccard": float(row["grid_stability_jaccard"]),
                        "centroid_coherence": float(row["centroid_coherence"]),
                        "goemotions_profile_top_labels": profile.iloc[0]["goemotions_profile_top_labels"],
                        "human_validation_status": "pending",
                    }
                )
                cluster_sizes.append(int(row["cluster_size"]))
                cluster_stabilities.append(float(row["seed_stability_jaccard"]))
                members = assignments[view].loc[assignments[view]["cluster_id"].eq(cluster_id)]
                selected_spans.extend(members["span_id"].astype(str))
                selected_reviews.extend(members["review_id"].astype(str))
                examples = links.loc[
                    links["discovery_view"].eq(view) & links["cluster_id"].eq(cluster_id)
                ].copy()
                examples.insert(0, "candidate_id", candidate_id)
                example_frames.append(examples)

        candidate_records.append(
            {
                "candidate_id": candidate_id,
                "possible_fine_grained_emotion_label": candidate["possible_fine_grained_emotion_label"],
                "domain_gloss": candidate["domain_gloss"],
                "nrc_parent_if_applicable": candidate["nrc_parent_if_applicable"],
                "corpus_rationale": candidate["corpus_rationale"],
                "evidence_clusters": int(len(cluster_sizes)),
                "clustered_span_memberships": int(sum(cluster_sizes)),
                "unique_evidence_spans_across_views": int(len(set(selected_spans))),
                "unique_evidence_reviews_across_views": int(len(set(selected_reviews))),
                "mean_seed_stability_across_evidence_clusters": float(np.mean(cluster_stabilities)),
                "minimum_seed_stability_across_evidence_clusters": float(np.min(cluster_stabilities)),
                "synthesis_status": configuration["status"],
                "human_validation_status": "pending",
                "eligible_as_final_plus3": False,
            }
        )

    candidates = pd.DataFrame.from_records(candidate_records)
    evidence = pd.DataFrame.from_records(evidence_records)
    examples = pd.concat(example_frames, ignore_index=True)
    deferred = pd.DataFrame.from_records(configuration["deferred_families"])
    summary = {
        "provisional_candidate_count": int(len(candidates)),
        "provisional_candidate_ids": candidates["candidate_id"].tolist(),
        "deferred_candidate_count": int(len(deferred)),
        "synthesis_status": str(configuration["status"]),
        "human_validation_complete": False,
        "final_plus3_selected": False,
    }
    atomic_write_csv(candidates, report_dir / "provisional_plus3_candidates.csv")
    atomic_write_csv(evidence, report_dir / "provisional_plus3_cluster_evidence.csv")
    atomic_write_csv(examples, report_dir / "provisional_plus3_representative_examples.csv")
    atomic_write_csv(deferred, report_dir / "deferred_candidate_families.csv")
    atomic_write_json(summary, report_dir / "provisional_plus3_summary.json")
    atomic_write_json(
        {"inputs": expected, "summary": summary, "environment": environment_manifest(config.repository_root)},
        manifest_path,
    )
    return summary
