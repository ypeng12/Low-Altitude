"""Stage 6: blinded AEM and Emotion Transition double-coding packet."""

from __future__ import annotations

import hashlib
import os
import tempfile
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


def _stable_order(value: str, seed: int) -> str:
    return hashlib.sha256(f"{seed}\x1f{value}".encode("utf-8")).hexdigest()


def stratified_noise_sample(noise: pd.DataFrame, total: int, seed: int) -> pd.DataFrame:
    if total <= 0 or total > len(noise):
        raise ValueError("Noise sample size must be positive and no larger than the noise pool")
    counts = noise["discourse_relation_family"].value_counts().sort_index()
    raw = counts / counts.sum() * total
    quotas = raw.astype(int)
    remainder = total - int(quotas.sum())
    fractional = (raw - quotas).sort_values(ascending=False, kind="stable")
    for relation in fractional.index[:remainder]:
        quotas.loc[relation] += 1
    frames = []
    for relation, quota in quotas.items():
        group = noise.loc[noise["discourse_relation_family"].eq(relation)].copy()
        group["_order"] = group["transition_id"].astype(str).map(lambda value: _stable_order(value, seed))
        frames.append(group.sort_values("_order", kind="stable").head(int(quota)).drop(columns="_order"))
    result = pd.concat(frames, ignore_index=True)
    if len(result) != total or result["transition_id"].duplicated().any():
        raise RuntimeError("Deterministic noise stratification produced an invalid sample")
    return result


def _atomic_write_workbook(sheets: Dict[str, pd.DataFrame], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("wb", suffix=".xlsx", dir=path.parent, delete=False) as handle:
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


def _blank_columns(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    output = frame.copy()
    for column in columns:
        output[column] = ""
    return output


def _expected(config: ProjectConfig) -> Dict[str, object]:
    output_dir = config.output_dir
    return {
        "stage": "blinded-aem-transition-annotation-packet-v1",
        "config_sha256": sha256_json(config.raw["annotation_packet"]),
        "structured_candidates_sha256": sha256_file(
            output_dir / "reports" / "structured_transformation_candidates_provisional.csv"
        ),
        "cluster_examples_sha256": sha256_file(
            output_dir / "reports" / "transformation_cluster_examples.csv"
        ),
        "provisional_codebook_sha256": sha256_file(
            output_dir / "reports" / "provisional_cluster_codebook.csv"
        ),
        "stage_code_sha256": sha256_file(Path(__file__)),
    }


def run_annotation_packet(config: ProjectConfig, force: bool = False) -> Dict[str, object]:
    output_dir = config.output_dir
    annotation_dir = output_dir / "human_annotation"
    audit_dir = output_dir / "audit"
    manifest_path = output_dir / "manifests" / "stage06_annotation_packet.json"
    required = (
        annotation_dir / "annotation_sample_300.csv",
        annotation_dir / "aem_transition_blinded_double_coding.xlsx",
        audit_dir / "annotation_sampling_audit.csv",
        annotation_dir / "summary.json",
    )
    expected = _expected(config)
    if refuse_stale_outputs(manifest_path, expected, force):
        missing = [str(path) for path in required if not path.exists()]
        if missing:
            raise RuntimeError(f"Annotation packet manifest is current but outputs are missing: {missing}")
        return {"status": "skipped"}

    cfg = config.raw["annotation_packet"]
    if not bool(cfg["blind_llm_seed_labels"]):
        raise ValueError("Gold-candidate packet must blind LLM seed labels")
    structured = pd.read_csv(
        output_dir / "reports" / "structured_transformation_candidates_provisional.csv",
        low_memory=False,
    )
    examples = pd.read_csv(output_dir / "reports" / "transformation_cluster_examples.csv")
    codebook = pd.read_csv(output_dir / "reports" / "provisional_cluster_codebook.csv")
    mapped_clusters = set(codebook["cluster_id"].astype(int))
    mapped_examples = examples.loc[
        examples["cluster_id"].isin(mapped_clusters)
        & examples["rank"].le(int(cfg["mapped_cluster_examples_per_cluster"]))
    ].copy()
    unmapped_examples = examples.loc[
        ~examples["cluster_id"].isin(mapped_clusters)
        & examples["rank"].le(int(cfg["unmapped_cluster_examples_per_cluster"]))
    ].copy()
    noise = structured.loc[structured["cluster_id"].lt(0)].copy()
    noise_sample = stratified_noise_sample(noise, int(cfg["noise_items"]), config.random_seed)
    selected_ids = pd.concat(
        [
            mapped_examples[["transition_id"]].assign(sampling_stratum="mapped_cluster_representative"),
            unmapped_examples[["transition_id"]].assign(sampling_stratum="unmapped_cluster_representative"),
            noise_sample[["transition_id"]].assign(sampling_stratum="noise_relation_stratified"),
        ],
        ignore_index=True,
    )
    if selected_ids["transition_id"].duplicated().any():
        raise ValueError("Annotation strata overlap on transition_id")
    target = int(cfg["target_items"])
    if len(selected_ids) != target:
        raise ValueError(f"Annotation design selected {len(selected_ids)} rows; expected {target}")
    sample = selected_ids.merge(structured, on="transition_id", validate="one_to_one")
    sample["randomized_order_key"] = sample["transition_id"].astype(str).map(
        lambda value: _stable_order(value, config.random_seed)
    )
    sample = sample.sort_values("randomized_order_key", kind="stable").reset_index(drop=True)
    sample.insert(0, "annotation_order", range(1, len(sample) + 1))

    raw_columns = [
        "annotation_order",
        "transition_id",
        "review_id",
        "sentence",
        "source_span",
        "transition_marker",
        "target_span",
    ]
    aem_fields = []
    for reviewer in ("r1", "r2"):
        aem_fields.extend(
            [
                f"{reviewer}_aspect",
                f"{reviewer}_initial_emotion",
                f"{reviewer}_trigger_span_exact_quote",
                f"{reviewer}_actor",
                f"{reviewer}_mechanism",
                f"{reviewer}_final_emotion",
                f"{reviewer}_mixed_emotion_yes_no_uncertain",
                f"{reviewer}_confidence_0_to_1",
                f"{reviewer}_notes",
            ]
        )
    aem_fields += [
        "adjudicated_aspect",
        "adjudicated_initial_emotion",
        "adjudicated_trigger_span_exact_quote",
        "adjudicated_actor",
        "adjudicated_mechanism",
        "adjudicated_final_emotion",
        "aem_adjudication_notes",
    ]
    transition_fields = []
    for reviewer in ("r1", "r2"):
        transition_fields.extend(
            [
                f"{reviewer}_source_emotion",
                f"{reviewer}_target_emotion",
                f"{reviewer}_is_emotion_transition_yes_no_uncertain",
                f"{reviewer}_transformation_type_multi",
                f"{reviewer}_contextual_reinterpretation_yes_no_uncertain",
                f"{reviewer}_confidence_0_to_1",
                f"{reviewer}_notes",
            ]
        )
    transition_fields += [
        "adjudicated_source_emotion",
        "adjudicated_target_emotion",
        "adjudicated_is_emotion_transition",
        "adjudicated_transformation_type_multi",
        "transition_adjudication_notes",
    ]
    aem_sheet = _blank_columns(sample.loc[:, raw_columns], aem_fields)
    transition_sheet = _blank_columns(sample.loc[:, raw_columns], transition_fields)

    instructions = pd.DataFrame(
        [
            ("status", "These 300 rows are annotation candidates, not a Gold Standard."),
            ("blinding", "LLM provisional labels and cluster IDs are omitted from both coding sheets."),
            ("independence", "Reviewer 1 and Reviewer 2 code independently before adjudication."),
            ("exact_spans", "Trigger spans must be copied exactly from the displayed sentence; do not paraphrase in the span field."),
            ("multi_label", "Mixed emotions and multiple transformation types are allowed; separate multiple values with |."),
            ("uncertainty", "Use uncertain when evidence is insufficient; do not force an emotion or mechanism."),
            ("task_separation", "Complete AEM and Emotion Transition as separate tasks to reduce label leakage."),
            ("plus3_warning", "The three added emotions remain provisional until independent Module 1 adjudication."),
        ],
        columns=["item", "instruction"],
    )
    emotion_codebook = pd.DataFrame(
        [
            ("joy", "NRC8 baseline", "pleasure or happiness"),
            ("trust", "NRC8 baseline", "confidence, safety, or reliance"),
            ("anticipation", "NRC8 baseline", "expectation or looking forward"),
            ("surprise", "NRC8 baseline", "unexpectedness"),
            ("fear", "NRC8 baseline", "threat or danger response"),
            ("sadness", "NRC8 baseline", "loss or unhappiness"),
            ("disgust", "NRC8 baseline", "revulsion"),
            ("anger", "NRC8 baseline", "hostility or frustration"),
            ("scenic awe", "provisional +3", "wonder/vastness from aerial scenery"),
            ("flight apprehension", "provisional +3", "anticipatory aviation nervousness"),
            ("provider-directed gratitude", "provisional +3", "thankfulness toward pilot/staff/operator"),
            ("relief", "open candidate; not in provisional +3", "reduction of prior fear, concern, or discomfort"),
            ("other_open_code", "open", "record a precise corpus-grounded label in notes"),
            ("none", "control", "no experienced emotion expressed"),
            ("uncertain", "uncertainty", "insufficient evidence"),
        ],
        columns=["emotion_label", "inventory_status", "definition"],
    )
    type_codebook = pd.DataFrame(
        [
            ("lexical_polarity_shift", "A locally negative/positive expression is reversed or countered."),
            ("contextual_reinterpretation", "Context changes what a word/event means in the experience."),
            ("negation_intensification", "Negation or intensity changes the apparent emotion."),
            ("contrastive_discourse", "An explicit discourse relation contrasts source and target."),
            ("mixed_emotion", "Different emotions coexist without a simple replacement."),
            ("emotional_reappraisal", "The tourist revises the emotional meaning of an event or outcome."),
            ("negative_outcome_shift", "An expected positive outcome becomes negative."),
            ("none", "No emotion transformation is present."),
            ("uncertain", "The transformation function cannot be decided."),
        ],
        columns=["transformation_type", "definition"],
    )
    audit = structured.loc[:, ["transition_id", "review_id", "cluster_id", "discourse_relation_family"]].copy()
    stratum_by_id = selected_ids.set_index("transition_id")["sampling_stratum"]
    audit["selected_for_annotation"] = audit["transition_id"].isin(set(selected_ids["transition_id"]))
    audit["sampling_stratum"] = audit["transition_id"].map(stratum_by_id).fillna("not_selected")
    audit["audit_reason"] = audit["selected_for_annotation"].map(
        {True: "selected_by_deterministic_stratified_design", False: "retained_outside_current_300_item_packet"}
    )
    sample_export = sample.loc[:, [*raw_columns, "sampling_stratum", "cluster_id", "discourse_relation_family"]]
    summary = {
        "annotation_candidates": int(len(sample)),
        "mapped_cluster_representatives": int(selected_ids["sampling_stratum"].eq("mapped_cluster_representative").sum()),
        "unmapped_cluster_representatives": int(selected_ids["sampling_stratum"].eq("unmapped_cluster_representative").sum()),
        "noise_relation_stratified": int(selected_ids["sampling_stratum"].eq("noise_relation_stratified").sum()),
        "llm_seed_labels_visible_to_annotators": False,
        "human_decision_cells_prefilled": 0,
        "gold_standard_created": False,
    }
    atomic_write_csv(sample_export, annotation_dir / "annotation_sample_300.csv")
    atomic_write_csv(audit, audit_dir / "annotation_sampling_audit.csv")
    _atomic_write_workbook(
        {
            "instructions": instructions,
            "emotion_codebook": emotion_codebook,
            "transformation_types": type_codebook,
            "AEM_blinded": aem_sheet,
            "Transition_blinded": transition_sheet,
        },
        annotation_dir / "aem_transition_blinded_double_coding.xlsx",
    )
    atomic_write_json(summary, annotation_dir / "summary.json")
    atomic_write_json(
        {"inputs": expected, "summary": summary, "environment": environment_manifest()}, manifest_path
    )
    return summary
