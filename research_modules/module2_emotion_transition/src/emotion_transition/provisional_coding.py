"""Stage 5: post-cluster LLM-assisted seed coding without claiming gold labels."""

from __future__ import annotations

from pathlib import Path
from typing import Dict

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


def validate_mappings(configuration: Dict[str, object], valid_clusters: set[int]) -> None:
    if configuration["status"] != "llm_assisted_provisional_not_human_validated":
        raise ValueError("Provisional coding must not claim human validation")
    used = []
    for mapping in configuration["mappings"]:
        clusters = [int(value) for value in mapping["cluster_ids"]]
        if not clusters or any(value not in valid_clusters for value in clusters):
            raise ValueError(f"Mapping {mapping['mapping_id']} refers to an unknown cluster")
        used.extend(clusters)
    duplicates = pd.Series(used).duplicated(keep=False)
    if duplicates.any():
        raise ValueError("A transformation cluster may not receive two provisional mappings")


def _expected(config: ProjectConfig) -> Dict[str, object]:
    output_dir = config.output_dir
    return {
        "stage": "llm-assisted-provisional-transition-coding-v1",
        "config_sha256": sha256_json(config.raw["provisional_cluster_coding"]),
        "cluster_assignments_sha256": sha256_file(output_dir / "clusters" / "cluster_assignments.csv"),
        "cluster_inventory_sha256": sha256_file(output_dir / "reports" / "transformation_cluster_inventory.csv"),
        "cluster_examples_sha256": sha256_file(output_dir / "reports" / "transformation_cluster_examples.csv"),
        "candidates_sha256": sha256_file(output_dir / "candidates" / "explicit_transition_candidates.csv"),
        "stage_code_sha256": sha256_file(Path(__file__)),
    }


def run_provisional_coding(config: ProjectConfig, force: bool = False) -> Dict[str, object]:
    output_dir = config.output_dir
    report_dir = output_dir / "reports"
    audit_dir = output_dir / "audit"
    manifest_path = output_dir / "manifests" / "stage05_provisional_coding.json"
    required = (
        report_dir / "provisional_cluster_codebook.csv",
        report_dir / "structured_transformation_candidates_provisional.csv",
        report_dir / "initial_transformation_matrix_provisional.csv",
        report_dir / "frequent_transformation_examples_provisional.csv",
        audit_dir / "uncertain_unmapped_transformation_candidates.csv",
        report_dir / "provisional_coding_summary.json",
    )
    expected = _expected(config)
    if refuse_stale_outputs(manifest_path, expected, force):
        missing = [str(path) for path in required if not path.exists()]
        if missing:
            raise RuntimeError(f"Provisional transition coding outputs are missing: {missing}")
        return {"status": "skipped"}

    assignments = pd.read_csv(output_dir / "clusters" / "cluster_assignments.csv")
    inventory = pd.read_csv(report_dir / "transformation_cluster_inventory.csv")
    candidates = pd.read_csv(output_dir / "candidates" / "explicit_transition_candidates.csv", low_memory=False)
    examples = pd.read_csv(report_dir / "transformation_cluster_examples.csv", low_memory=False)
    configuration = config.raw["provisional_cluster_coding"]
    validate_mappings(configuration, set(inventory["cluster_id"].astype(int)))

    mapping_records = []
    cluster_to_mapping = {}
    for mapping in configuration["mappings"]:
        for cluster_id in mapping["cluster_ids"]:
            cluster_id = int(cluster_id)
            cluster_to_mapping[cluster_id] = mapping
            metric = inventory.loc[inventory["cluster_id"].eq(cluster_id)].iloc[0]
            mapping_records.append(
                {
                    "mapping_id": mapping["mapping_id"],
                    "cluster_id": cluster_id,
                    "cluster_size": int(metric["cluster_size"]),
                    "corpus_derived_pair_label": metric["corpus_derived_pair_label"],
                    "aspect": mapping["aspect"],
                    "source_emotion": mapping["source_emotion"],
                    "target_emotion": mapping["target_emotion"],
                    "actor": mapping["actor"],
                    "mechanism": mapping["mechanism"],
                    "transformation_type": mapping["transformation_type"],
                    "rationale": mapping["rationale"],
                    "seed_stability_jaccard": float(metric["seed_stability_jaccard"]),
                    "directional_centroid_coherence": float(metric["directional_centroid_coherence"]),
                    "stability_warning": (
                        "low_seed_stability_requires_extra_human_scrutiny"
                        if float(metric["seed_stability_jaccard"]) < 0.50
                        else ""
                    ),
                    "coding_status": configuration["status"],
                    "human_validation_status": "pending",
                }
            )
    codebook = pd.DataFrame.from_records(mapping_records)
    joined = assignments.merge(
        candidates,
        on=["transition_id", "review_id", "source_span_id", "target_span_id", "transition_marker", "discourse_relation_family"],
        validate="one_to_one",
    )
    joined["aspect"] = ""
    joined["llm_provisional_source_emotion"] = ""
    joined["llm_provisional_target_emotion"] = ""
    joined["llm_provisional_transformation_type"] = ""
    joined["llm_provisional_actor"] = ""
    joined["llm_provisional_mechanism"] = ""
    joined["llm_provisional_mapping_id"] = ""
    joined["llm_provisional_rationale"] = ""
    joined["provisional_coding_status"] = "uncertain_unmapped"
    for cluster_id, mapping in cluster_to_mapping.items():
        mask = joined["cluster_id"].eq(cluster_id)
        joined.loc[mask, "aspect"] = mapping["aspect"]
        joined.loc[mask, "llm_provisional_source_emotion"] = mapping["source_emotion"]
        joined.loc[mask, "llm_provisional_target_emotion"] = mapping["target_emotion"]
        joined.loc[mask, "llm_provisional_transformation_type"] = mapping["transformation_type"]
        joined.loc[mask, "llm_provisional_actor"] = mapping["actor"]
        joined.loc[mask, "llm_provisional_mechanism"] = mapping["mechanism"]
        joined.loc[mask, "llm_provisional_mapping_id"] = mapping["mapping_id"]
        joined.loc[mask, "llm_provisional_rationale"] = mapping["rationale"]
        joined.loc[mask, "provisional_coding_status"] = configuration["status"]
    joined["human_validation_status"] = "pending"
    joined["gold_standard_record"] = False
    stability_lookup = inventory.set_index("cluster_id")[
        ["seed_stability_jaccard", "directional_centroid_coherence"]
    ]
    joined["cluster_seed_stability_jaccard"] = joined["cluster_id"].map(
        stability_lookup["seed_stability_jaccard"]
    )
    joined["cluster_directional_centroid_coherence"] = joined["cluster_id"].map(
        stability_lookup["directional_centroid_coherence"]
    )
    joined["stability_warning"] = ""
    joined.loc[
        joined["cluster_seed_stability_jaccard"].lt(0.50), "stability_warning"
    ] = "low_seed_stability_requires_extra_human_scrutiny"

    coded = joined.loc[joined["provisional_coding_status"].eq(configuration["status"])].copy()
    uncertain = joined.loc[~joined.index.isin(coded.index)].copy()
    uncertain["audit_reason"] = "noise_or_cluster_without_reliable_provisional_semantic_mapping"
    matrix = (
        coded.groupby(
            ["llm_provisional_source_emotion", "llm_provisional_target_emotion"], dropna=False
        )
        .agg(
            provisional_pair_count=("transition_id", "size"),
            unique_reviews=("review_id", "nunique"),
            contributing_clusters=("cluster_id", lambda values: "|".join(map(str, sorted(set(values))))),
            mapping_ids=("llm_provisional_mapping_id", lambda values: "|".join(sorted(set(values)))),
            minimum_seed_stability=("cluster_seed_stability_jaccard", "min"),
            pair_weighted_mean_seed_stability=("cluster_seed_stability_jaccard", "mean"),
        )
        .reset_index()
        .sort_values("provisional_pair_count", ascending=False, kind="stable")
    )
    matrix["human_validation_status"] = "pending"
    matrix["matrix_status"] = "provisional_not_gold"

    example_mapping = codebook.loc[:, ["cluster_id", "mapping_id", "aspect", "source_emotion", "target_emotion", "actor", "mechanism", "transformation_type", "rationale"]]
    coded_examples = examples.merge(example_mapping, on="cluster_id", how="inner", validate="many_to_one")
    coded_examples["human_validation_status"] = "pending"
    summary = {
        "mapped_clusters": int(codebook["cluster_id"].nunique()),
        "unmapped_clusters": int(len(inventory) - codebook["cluster_id"].nunique()),
        "provisionally_coded_pairs": int(len(coded)),
        "uncertain_unmapped_pairs": int(len(uncertain)),
        "provisional_matrix_cells": int(len(matrix)),
        "mapped_clusters_below_0_50_seed_stability": int(
            codebook["seed_stability_jaccard"].lt(0.50).sum()
        ),
        "status": str(configuration["status"]),
        "human_validation_complete": False,
        "gold_standard_created": False,
    }
    atomic_write_csv(codebook, report_dir / "provisional_cluster_codebook.csv")
    atomic_write_csv(joined, report_dir / "structured_transformation_candidates_provisional.csv")
    atomic_write_csv(matrix, report_dir / "initial_transformation_matrix_provisional.csv")
    atomic_write_csv(coded_examples, report_dir / "frequent_transformation_examples_provisional.csv")
    atomic_write_csv(uncertain, audit_dir / "uncertain_unmapped_transformation_candidates.csv")
    atomic_write_json(summary, report_dir / "provisional_coding_summary.json")
    atomic_write_json(
        {"inputs": expected, "summary": summary, "environment": environment_manifest()}, manifest_path
    )
    return summary
