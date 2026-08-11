"""Strict validation for the one approved CATE workbook."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple

import pandas as pd


CATE_COLUMNS = (
    "序号",
    "CATE 词汇",
    "英文单词 (Pure Word)",
    "中文释义 (Translation)",
    "出现频次 (Freq)",
    "平均星级 (Stars)",
    "VADER 得分",
    "语义类别",
)


def validate_cate_workbook(
    path: Path, sheet_name: str = "Sheet1", expected_rows: int = 107
) -> Tuple[pd.DataFrame, Dict[str, object]]:
    if path.suffix.lower() != ".xlsx":
        raise ValueError("The canonical CATE source must be the approved .xlsx workbook")
    frame = pd.read_excel(path, sheet_name=sheet_name, engine="openpyxl")
    if tuple(frame.columns) != CATE_COLUMNS:
        raise ValueError(f"Unexpected CATE schema: {list(frame.columns)}")
    if len(frame) != expected_rows:
        raise ValueError(f"Expected {expected_rows} CATE rows, found {len(frame)}")
    if frame.isna().any().any():
        missing = frame.columns[frame.isna().any()].tolist()
        raise ValueError(f"CATE workbook contains missing values in: {missing}")
    for column in ("CATE 词汇", "英文单词 (Pure Word)"):
        if frame[column].astype(str).str.strip().duplicated().any():
            raise ValueError(f"CATE workbook contains duplicate values in {column}")
    audit = {
        "source_file": path.name,
        "sheet_name": sheet_name,
        "rows": int(len(frame)),
        "columns": list(frame.columns),
        "unique_cate_terms": int(frame["CATE 词汇"].nunique()),
        "unique_english_terms": int(frame["英文单词 (Pure Word)"].nunique()),
        "status": "valid",
    }
    return frame, audit
