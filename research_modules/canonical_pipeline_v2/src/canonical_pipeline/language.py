"""FastText ISO-language audit owned by canonical v2."""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

import pandas as pd


def classify_prediction(
    label: str,
    probability: float,
    english_label: str,
    include_probability: float,
    uncertain_probability: float,
) -> tuple[str, float, str]:
    clean_label = label.removeprefix("__label__")
    probability = float(probability)
    if clean_label == english_label and probability >= include_probability:
        decision = "english"
    elif probability < uncertain_probability:
        decision = "uncertain"
    else:
        decision = "non_english"
    return clean_label, probability, decision


def combine_text_fields(frame: pd.DataFrame, fields: Sequence[str]) -> list[str]:
    missing = [field for field in fields if field not in frame.columns]
    if missing:
        raise ValueError(f"Language text fields missing from canonical source: {missing}")
    values = []
    for row in frame.loc[:, fields].itertuples(index=False, name=None):
        parts = [str(value).strip() for value in row if pd.notna(value) and str(value).strip()]
        values.append(" ".join(parts).replace("\n", " "))
    return values


def audit_languages(
    frame: pd.DataFrame,
    model_path: Path,
    text_fields: Sequence[str],
    english_label: str,
    include_probability: float,
    uncertain_probability: float,
    top_k: int,
) -> pd.DataFrame:
    try:
        import fasttext
    except ImportError as exc:
        raise RuntimeError("fasttext-wheel is required for the canonical language audit") from exc

    model = fasttext.load_model(str(model_path))
    records = []
    for review_id, text in zip(frame["review_id"], combine_text_fields(frame, text_fields)):
        if not text.strip():
            records.append(
                {
                    "review_id": review_id,
                    "fasttext_label": "",
                    "fasttext_probability": 0.0,
                    "language_decision": "uncertain",
                    "top_k_predictions": "",
                }
            )
            continue
        labels, probabilities = model.predict(text, k=top_k)
        label, probability, decision = classify_prediction(
            str(labels[0]),
            float(probabilities[0]),
            english_label,
            include_probability,
            uncertain_probability,
        )
        records.append(
            {
                "review_id": review_id,
                "fasttext_label": label,
                "fasttext_probability": probability,
                "language_decision": decision,
                "top_k_predictions": ";".join(
                    f"{str(item).removeprefix('__label__')}:{float(score):.6f}"
                    for item, score in zip(labels, probabilities)
                ),
            }
        )
    return pd.DataFrame.from_records(records)
