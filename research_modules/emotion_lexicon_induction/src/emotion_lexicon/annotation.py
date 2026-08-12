"""Strict AI task packets and human-review workbook creation."""

from __future__ import annotations

import json
import os
import re
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


STATUS_ROWS = [
    ("E1", "Direct emotion word", "Directly names or expresses the experiencer's internal affective state."),
    ("E2", "Emotion-eliciting/appraisal word", "Describes a stimulus or appraisal that may elicit emotion, not the felt state itself."),
    ("E3", "Bodily/behavioral indicator", "A bodily reaction or behavior that can indicate emotion but is not conclusive by itself."),
    ("N", "Non-emotion", "Aspect, actor, event, attribute, evaluation, modifier, or other non-emotion use."),
    ("U", "Uncertain/context-dependent", "The occurrence cannot be decided reliably from the available context."),
]


SYSTEM_INSTRUCTION = """You are assisting open coding for a corpus-derived unigram emotion lexicon.
Use only the supplied review and exact eligible token occurrences. Do not consult or imitate NRC, VADER, CATE, GoEmotions, or another fixed emotion taxonomy. Select a token only when it may be E1, E2, E3, or U; ordinary N tokens may be omitted. Never invent, paraphrase, or output a word that is absent from eligible_tokens. Judge the occurrence in context, not the word in isolation. E1 directly names or expresses an experiencer's internal affective state. E2 is an emotion-eliciting or appraisal word. E3 is a bodily or behavioral indicator. U is genuinely uncertain. Return valid JSON conforming to the supplied schema. Categories are provisional open-coding labels and must not be forced into a predetermined inventory."""


def safe_text(value: Any) -> str:
    if value is None or pd.isna(value):
        return ""
    return str(value)


def build_ai_tasks(
    reviews: pd.DataFrame,
    occurrences: pd.DataFrame,
    *,
    instruction_version: str,
    text_field: str,
    allowed_statuses: list[str],
) -> list[dict[str, Any]]:
    eligible = occurrences[occurrences["candidate_eligible"]].copy()
    grouped = {review_id: group for review_id, group in eligible.groupby("review_id", sort=False)}
    tasks: list[dict[str, Any]] = []
    for row in reviews.sort_values("sampling_rank", kind="stable").itertuples(index=False):
        review_id = str(row.review_id)
        group = grouped.get(review_id, pd.DataFrame())
        token_rows: list[dict[str, Any]] = []
        if not group.empty:
            for item in group.sort_values("token_index", kind="stable").itertuples(index=False):
                token_rows.append(
                    {
                        "token_index": int(item.token_index),
                        "surface": str(item.surface),
                        "normalized_word": str(item.normalized_word),
                        "lemma": str(item.lemma),
                        "normalization_method": str(item.normalization_method),
                        "coarse_pos": str(item.coarse_pos),
                        "char_start": int(item.char_start),
                        "char_end": int(item.char_end),
                    }
                )
        tasks.append(
            {
                "task_id": f"emotion_unigrams_{review_id}",
                "instruction_version": instruction_version,
                "system_instruction": SYSTEM_INSTRUCTION,
                "input": {
                    "review_id": review_id,
                    "review_title_for_context_only": safe_text(row.review_title),
                    "review_text": safe_text(getattr(row, text_field)),
                    "eligible_tokens": token_rows,
                },
                "output_schema": {
                    "review_id": "string, must equal input review_id",
                    "selected_occurrences": [
                        {
                            "token_index": "integer copied from eligible_tokens",
                            "surface": "exact string copied from eligible_tokens",
                            "status": f"one of {allowed_statuses}",
                            "experiencer": "tourist|companion|staff|other|unclear",
                            "provisional_open_category": "short corpus-grounded label or empty",
                            "rationale": "brief contextual reason",
                            "confidence": "number from 0 to 1",
                        }
                    ],
                    "review_level_notes": "optional string",
                },
            }
        )
    return tasks


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def write_review_workbook(
    path: Path,
    reviews: pd.DataFrame,
    inventory: pd.DataFrame,
    *,
    stage_size: int,
    forbidden_lexicons: list[str],
) -> None:
    instructions = pd.DataFrame(
        [
            ("Purpose", "Build a corpus-derived unigram emotion lexicon; do not classify phrases at this stage."),
            ("Unit", "An exact single-word occurrence, judged using its original review context."),
            ("Discovery restriction", f"Do not use {', '.join(forbidden_lexicons)} to select or label candidates."),
            ("Human authority", "AI fields are proposals only. Human/adjudicated fields determine approval."),
            ("No forced labels", "Use U when evidence is insufficient; do not force a category or a target count."),
            ("Stage", f"Nested discovery sample of {stage_size} canonical English reviews."),
        ],
        columns=["item", "instruction"],
    )
    statuses = pd.DataFrame(STATUS_ROWS, columns=["status", "name", "definition"])
    review_columns = [
        "sampling_rank",
        "review_id",
        "primary_tour_name",
        "aircraft_type",
        "length_bin",
        "review_title",
        "review_text",
    ]
    review_sheet = reviews[review_columns].copy()
    for column in [
        "ai_emotion_words",
        "ai_uncertain_words",
        "human_emotion_words",
        "human_uncertain_words",
        "review_annotation_status",
        "review_annotation_notes",
    ]:
        review_sheet[column] = ""
    path.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        instructions.to_excel(writer, sheet_name="instructions", index=False)
        statuses.to_excel(writer, sheet_name="status_codebook", index=False)
        review_sheet.to_excel(writer, sheet_name=f"reviews_{stage_size}", index=False)
        inventory.to_excel(writer, sheet_name="unigram_candidates", index=False)
        fixed_time = datetime(2026, 1, 1, tzinfo=timezone.utc)
        writer.book.properties.created = fixed_time
        writer.book.properties.modified = fixed_time
    normalize_xlsx_archive(path)


def normalize_xlsx_archive(path: Path) -> None:
    """Remove ZIP timestamps so the same workbook content hashes identically."""

    with tempfile.NamedTemporaryFile(
        prefix=f".{path.stem}.", suffix=path.suffix, dir=path.parent, delete=False
    ) as temporary:
        temporary_path = Path(temporary.name)
    try:
        with zipfile.ZipFile(path, "r") as source, zipfile.ZipFile(
            temporary_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
        ) as target:
            for name in sorted(source.namelist()):
                original = source.getinfo(name)
                info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = original.external_attr
                info.create_system = original.create_system
                payload = source.read(name)
                if name == "docProps/core.xml":
                    payload = re.sub(
                        rb"(<dcterms:modified[^>]*>).*?(</dcterms:modified>)",
                        lambda match: match.group(1) + b"2026-01-01T00:00:00Z" + match.group(2),
                        payload,
                    )
                target.writestr(info, payload)
        os.replace(temporary_path, path)
    finally:
        temporary_path.unlink(missing_ok=True)
