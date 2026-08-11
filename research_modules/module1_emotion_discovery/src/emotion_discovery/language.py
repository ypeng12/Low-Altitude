"""Non-destructive FastText language audit."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence

import pandas as pd


@dataclass(frozen=True)
class LanguageDecision:
    label: str
    probability: float
    decision: str


def classify_prediction(
    label: str,
    probability: float,
    english_label: str,
    include_probability: float,
    uncertain_probability: float,
) -> LanguageDecision:
    """Convert one top prediction to english/non-English/uncertain."""

    clean_label = label.removeprefix("__label__")
    probability = float(probability)
    if clean_label == english_label and probability >= include_probability:
        decision = "english"
    elif probability < uncertain_probability:
        decision = "uncertain"
    else:
        decision = "non_english"
    return LanguageDecision(clean_label, probability, decision)


def combine_text_fields(frame: pd.DataFrame, fields: Sequence[str]) -> List[str]:
    missing = [field for field in fields if field not in frame.columns]
    if missing:
        raise ValueError(f"Language text fields missing from master data: {missing}")
    combined: List[str] = []
    for values in frame.loc[:, fields].itertuples(index=False, name=None):
        parts = [str(value).strip() for value in values if pd.notna(value) and str(value).strip()]
        combined.append(" ".join(parts).replace("\n", " "))
    return combined


def audit_languages(
    frame: pd.DataFrame,
    model_path: Path,
    text_fields: Sequence[str],
    english_label: str = "en",
    include_probability: float = 0.7,
    uncertain_probability: float = 0.7,
    top_k: int = 3,
) -> pd.DataFrame:
    """Predict languages while retaining source labels and all top-k scores."""

    try:
        import fasttext
    except ImportError as exc:
        raise RuntimeError(
            "FastText is required for the language audit. Install requirements.txt "
            "inside the module's isolated environment."
        ) from exc

    model = fasttext.load_model(str(model_path))
    texts = combine_text_fields(frame, text_fields)
    records = []
    for review_id, text in zip(frame["review_id"], texts):
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
        decision = classify_prediction(
            str(labels[0]),
            float(probabilities[0]),
            english_label,
            include_probability,
            uncertain_probability,
        )
        top_predictions = ";".join(
            f"{str(label).removeprefix('__label__')}:{float(probability):.6f}"
            for label, probability in zip(labels, probabilities)
        )
        records.append(
            {
                "review_id": review_id,
                "fasttext_label": decision.label,
                "fasttext_probability": decision.probability,
                "language_decision": decision.decision,
                "top_k_predictions": top_predictions,
            }
        )
    return pd.DataFrame.from_records(records)
