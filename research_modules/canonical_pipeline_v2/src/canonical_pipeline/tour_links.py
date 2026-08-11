"""Deterministic raw-file provenance and review-to-tour links."""

from __future__ import annotations

import hashlib
import html
import re
from pathlib import Path
from typing import Tuple

import pandas as pd

from .ids import stable_review_id, stable_tour_id


_DATE_SUFFIX = re.compile(r"[_ ]?\d{4}[-_]\d{2}[-_]\d{2}$")
_SOURCE_MARKERS = re.compile(r"_(?:attraction|product|review).*$", re.I)
_LEADING_IDS = re.compile(r"^\s*\d+(?:[\s_-]+\d+)*[\s_-]+")
_ONLY_IDS = re.compile(r"^\s*\d+(?:[\s_-]+\d+)*\s*$")
_BR = re.compile(r"<br\s*/?>", re.I)


def parse_tour_name(source_file: str) -> str:
    stem = Path(source_file).stem
    without_date = _DATE_SUFFIX.sub("", stem)
    before_markers = _SOURCE_MARKERS.sub("", without_date)
    cleaned = "" if _ONLY_IDS.fullmatch(before_markers) else _LEADING_IDS.sub("", before_markers)
    cleaned = re.sub(r"[_]+", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" -_")
    return cleaned or f"Unresolved tour ({stem})"


def clean_raw_text(value: object) -> str:
    if value is None or (isinstance(value, float) and value != value):
        return ""
    text = _BR.sub("\n", str(value))
    # Match the historical master cleaner exactly: only <br> is markup here.
    # Other angle-bracketed content can be reviewer text (for example
    # "<see photo>") and must not be silently discarded.
    return html.unescape(text)


def build_review_tour_links(raw_dir: Path, canonical_ids: set[str]) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    occurrences = []
    for path in sorted(raw_dir.glob("*.csv"), key=lambda item: item.name.casefold()):
        try:
            frame = pd.read_csv(path, encoding="utf-8-sig", low_memory=False)
        except UnicodeDecodeError:
            frame = pd.read_csv(path, encoding="latin-1", low_memory=False)
        frame.columns = [column.strip().lower().replace(" ", "_") for column in frame.columns]
        missing = {"user_name", "review_text"} - set(frame.columns)
        if missing:
            raise ValueError(f"Raw file {path.name} is missing columns: {sorted(missing)}")
        tour_id = stable_tour_id(path.name)
        tour_name = parse_tour_name(path.name)
        for row_number, row in frame.iterrows():
            review_id = stable_review_id(row["user_name"], clean_raw_text(row["review_text"]))
            occurrence_key = f"{path.name}\x1f{row_number + 2}".encode("utf-8")
            occurrences.append(
                {
                    "raw_occurrence_id": "raw_" + hashlib.sha256(occurrence_key).hexdigest()[:24],
                    "review_id": review_id,
                    "tour_id": tour_id,
                    "tour_name": tour_name,
                    "source_file": path.name,
                    "source_row_number": int(row_number + 2),
                    "in_canonical_master": review_id in canonical_ids,
                }
            )
    occurrence_frame = pd.DataFrame.from_records(occurrences)
    valid = occurrence_frame.loc[occurrence_frame["in_canonical_master"]].copy()
    links = (
        valid.groupby(["review_id", "tour_id", "tour_name", "source_file"], as_index=False)
        .size()
        .rename(columns={"size": "raw_occurrence_count"})
        .sort_values(["review_id", "tour_id"], kind="stable")
        .reset_index(drop=True)
    )
    audit = occurrence_frame.loc[~occurrence_frame["in_canonical_master"]].copy()
    return links, occurrence_frame, audit
