"""Cross-version membership and cell-level drift audits."""

from __future__ import annotations

from typing import Dict, Tuple

import pandas as pd


IDENTITY_COLUMNS = {"review_id", "user_name", "review_text"}


def _equal_values(left: pd.Series, right: pd.Series) -> pd.Series:
    both_missing = left.isna() & right.isna()
    if pd.api.types.is_numeric_dtype(left) and pd.api.types.is_numeric_dtype(right):
        difference = (pd.to_numeric(left, errors="coerce") - pd.to_numeric(right, errors="coerce")).abs()
        return both_missing | difference.le(1e-12)
    return both_missing | left.astype("string").eq(right.astype("string")).fillna(False)


def audit_dataset_drift(
    master: pd.DataFrame, compared: Dict[str, pd.DataFrame]
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Return membership, field summary, and every differing shared cell."""

    master_ids = set(master["review_id"])
    membership_records = []
    summary_records = []
    detail_records = []
    master_indexed = master.set_index("review_id", drop=False)

    for dataset_name, frame in compared.items():
        frame_ids = set(frame["review_id"])
        shared_ids = sorted(master_ids & frame_ids)
        membership_records.append(
            {
                "dataset": dataset_name,
                "rows": int(len(frame)),
                "unique_review_ids": int(frame["review_id"].nunique()),
                "shared_with_master": int(len(shared_ids)),
                "missing_from_dataset": int(len(master_ids - frame_ids)),
                "extra_vs_master": int(len(frame_ids - master_ids)),
            }
        )
        other_indexed = frame.set_index("review_id", drop=False)
        shared_columns = sorted((set(master.columns) & set(frame.columns)) - IDENTITY_COLUMNS)
        left_rows = master_indexed.loc[shared_ids]
        right_rows = other_indexed.loc[shared_ids]
        for column in shared_columns:
            equal = _equal_values(left_rows[column], right_rows[column])
            differing_ids = equal.index[~equal]
            summary_records.append(
                {
                    "dataset": dataset_name,
                    "field": column,
                    "shared_rows": int(len(shared_ids)),
                    "different_rows": int(len(differing_ids)),
                    "different_percent": round(len(differing_ids) / max(len(shared_ids), 1) * 100, 6),
                }
            )
            for review_id in differing_ids:
                detail_records.append(
                    {
                        "review_id": review_id,
                        "dataset": dataset_name,
                        "field": column,
                        "master_value": left_rows.at[review_id, column],
                        "compared_value": right_rows.at[review_id, column],
                    }
                )
    return (
        pd.DataFrame.from_records(membership_records),
        pd.DataFrame.from_records(summary_records),
        pd.DataFrame.from_records(detail_records),
    )
