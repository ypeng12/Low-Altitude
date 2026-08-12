#!/usr/bin/env python3
"""Rebuild the NRC/CATE word-rating scatter from authoritative inputs.

Each plotted point is a word. Its x coordinate is the word's raw VADER
lexicon valence, its y coordinate is the mean rating of canonical English
reviews containing that word, and its area reflects the number of linked
reviews. The word-review audit table preserves every stable ``review_id``
link used in the aggregation.

This script intentionally does not overwrite the legacy plot or statistics.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
import re
import sys

import numpy as np
import pandas as pd


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
CANONICAL_PATH = REPOSITORY_ROOT / "research_modules/canonical_pipeline_v2/outputs/canonical/canonical_reviews_v2.csv"
CATE_PATH = REPOSITORY_ROOT / "data/derived_outputs/cate_words_curated_107_translated.xlsx"
STATS_PATH = REPOSITORY_ROOT / "data/derived_outputs/nrc_cate_word_review_stats_canonical_v2.csv"
LINKS_PATH = REPOSITORY_ROOT / "data/derived_outputs/nrc_cate_word_review_links_canonical_v2.csv"
FIGURE_PATH = REPOSITORY_ROOT / "figures/nrc_emotion_plots/nrc_cate_word_review_scatter_canonical_v2.png"

CATE_WORD_COLUMN = "英文单词 (Pure Word)"
MINIMUM_REVIEW_COUNT = 15
TOKEN_PATTERN = re.compile(r"\b[a-zA-Z][a-zA-Z'-]{1,}\b")
NRC8 = ("anger", "anticipation", "disgust", "fear", "joy", "sadness", "surprise", "trust")

NON_EMOTION_NOUNS = {
    "pilot", "captain", "guide", "team", "crew", "driver", "staff", "personnel", "agent", "company",
    "trip", "tour", "flight", "ride", "helicopter", "heli", "plane", "aircraft", "ship", "boat",
    "mountain", "canyon", "view", "views", "island", "airport", "ground", "time", "day", "year",
    "minute", "minutes", "hour", "hours", "money", "price", "ticket", "seat", "seats", "window",
    "headset", "photo", "photos", "video", "pictures", "words", "speech", "motion", "sickness",
    "vacation", "birthday", "anniversary", "wedding", "family", "kids", "children", "husband", "wife",
}

COLORS = {
    "JOY": "#16A34A",
    "SADNESS": "#64748B",
    "TRUST": "#1D4ED8",
    "DISGUST": "#92400E",
    "ANTICIPATION": "#EA580C",
    "SURPRISE": "#9333EA",
    "FEAR": "#DC2626",
    "ANGER": "#B91C1C",
    "CATE": "#FFE500",
}

# A word may have several NRC labels. This order is used only to select one
# color in the compact overview; every NRC label remains in the audit tables.
PRIMARY_NRC_DISPLAY_ORDER = (
    "joy", "sadness", "trust", "disgust", "anticipation", "surprise", "fear", "anger"
)


def load_approved_cate(path: Path) -> pd.DataFrame:
    if path.name != "cate_words_curated_107_translated.xlsx":
        raise ValueError(f"Unapproved CATE source: {path.name}")
    frame = pd.read_excel(path, sheet_name="Sheet1", engine="openpyxl")
    if len(frame) != 107 or CATE_WORD_COLUMN not in frame.columns:
        raise ValueError("Approved CATE workbook must have 107 rows and the English word column")
    words = frame[CATE_WORD_COLUMN].astype(str).str.strip().str.casefold()
    if words.eq("").any() or words.duplicated().any():
        raise ValueError("Approved CATE words must be nonempty and unique")
    frame = frame.copy()
    frame["cate_word"] = words
    return frame


def display_category(word: str, cate_words: set[str], nrc_labels: tuple[str, ...]) -> str:
    """Return CATE or one explicitly documented primary NRC display label."""

    if word in cate_words:
        return "CATE"
    if not nrc_labels:
        raise ValueError(f"Non-CATE word has no NRC8 association: {word}")
    return next(label.upper() for label in PRIMARY_NRC_DISPLAY_ORDER if label in nrc_labels)


def main() -> None:
    from adjustText import adjust_text
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from nltk.corpus import stopwords
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    from nrclex import NRCLex

    cate = load_approved_cate(CATE_PATH)
    cate_words = set(cate["cate_word"])
    canonical = pd.read_csv(CANONICAL_PATH, low_memory=False)
    required = {"review_id", "review_title", "review_text", "rating", "analysis_language_status"}
    missing = sorted(required - set(canonical.columns))
    if missing:
        raise ValueError(f"Canonical v2 is missing required columns: {missing}")
    reviews = canonical.loc[
        canonical["analysis_language_status"].eq("english"),
        ["review_id", "review_title", "review_text", "rating"],
    ].copy()
    if reviews["review_id"].duplicated().any():
        raise ValueError("Canonical English review_id must be unique")

    nrc_lexicon = NRCLex().__lexicon__
    vader_lexicon = SentimentIntensityAnalyzer().lexicon
    stop_words = set(stopwords.words("english"))
    review_links = []
    token_occurrences: Counter[str] = Counter()
    word_ratings: defaultdict[str, list[float]] = defaultdict(list)
    word_nrc: dict[str, tuple[str, ...]] = {}

    for review in reviews.itertuples(index=False):
        text = f"{review.review_title if pd.notna(review.review_title) else ''} {review.review_text if pd.notna(review.review_text) else ''}"
        tokens = [value.casefold() for value in TOKEN_PATTERN.findall(text)]
        token_occurrences.update(tokens)
        for word in sorted(set(tokens)):
            labels = tuple(sorted(set(nrc_lexicon.get(word, [])) & set(NRC8)))
            if word not in cate_words and (word in stop_words or word in NON_EMOTION_NOUNS or not labels):
                continue
            category = display_category(word, cate_words, labels)
            word_nrc[word] = labels
            word_ratings[word].append(float(review.rating))
            review_links.append(
                {
                    "word": word,
                    "review_id": review.review_id,
                    "rating": float(review.rating),
                    "display_category": category,
                    "nrc_labels": "|".join(labels),
                    "nrc_label_count": len(labels),
                    "is_approved_cate": word in cate_words,
                }
            )

    records = []
    for word, ratings in word_ratings.items():
        labels = word_nrc[word]
        in_vader = word in vader_lexicon
        records.append(
            {
                "word": word,
                "unique_review_count": len(ratings),
                "raw_token_occurrences": int(token_occurrences[word]),
                "mean_rating": float(np.mean(ratings)),
                "rating_standard_deviation": float(np.std(ratings, ddof=1)) if len(ratings) > 1 else 0.0,
                "raw_vader_word_score": float(vader_lexicon[word]) if in_vader else 0.0,
                "vader_lexicon_available": in_vader,
                "display_category": display_category(word, cate_words, labels),
                "nrc_labels": "|".join(labels),
                "nrc_label_count": len(labels),
                "is_approved_cate": word in cate_words,
                "included_in_plot": len(ratings) >= MINIMUM_REVIEW_COUNT,
                "plot_exclusion_reason": "" if len(ratings) >= MINIMUM_REVIEW_COUNT else "fewer_than_15_linked_reviews",
            }
        )
    stats = pd.DataFrame.from_records(records).sort_values(
        ["included_in_plot", "unique_review_count", "word"], ascending=[False, False, True], kind="stable"
    )
    links = pd.DataFrame.from_records(review_links).sort_values(["word", "review_id"], kind="stable")
    STATS_PATH.parent.mkdir(parents=True, exist_ok=True)
    FIGURE_PATH.parent.mkdir(parents=True, exist_ok=True)
    stats.to_csv(STATS_PATH, index=False)
    links.to_csv(LINKS_PATH, index=False)

    plotted = stats.loc[stats["included_in_plot"]].copy()
    plt.style.use("seaborn-v0_8-whitegrid")
    fig, axis = plt.subplots(figsize=(16, 10), dpi=240)
    legend_order = ["JOY", "SADNESS", "TRUST", "DISGUST", "ANTICIPATION", "SURPRISE", "FEAR", "ANGER", "CATE"]
    legend_names = {
        "JOY": "Joy [Pair 1]",
        "SADNESS": "Sadness [Pair 1]",
        "TRUST": "Trust [Pair 2]",
        "DISGUST": "Disgust [Pair 2]",
        "ANTICIPATION": "Anticipation [Pair 3]",
        "SURPRISE": "Surprise [Pair 3]",
        "FEAR": "Fear [Pair 4]",
        "ANGER": "Anger [Pair 4]",
        "CATE": "CATE",
    }
    for category in legend_order:
        group = plotted.loc[plotted["display_category"].eq(category)]
        if group.empty:
            continue
        sizes = 42 + 34 * np.log10(group["unique_review_count"])
        axis.scatter(
            group["raw_vader_word_score"],
            group["mean_rating"],
            s=sizes,
            color=COLORS[category],
            edgecolor="#172033",
            linewidth=0.7,
            alpha=0.90 if category == "CATE" else 0.78,
            label=f"{legend_names.get(category, category.title())} (words={len(group)})",
        )

    dataset_mean = float(reviews["rating"].mean())
    axis.axhline(dataset_mean, color="#EF4444", linestyle=":", linewidth=1.5, label=f"Canonical English mean rating ({dataset_mean:.3f})")
    axis.axvline(0.0, color="#94A3B8", linestyle="--", linewidth=1.1)
    annotate = {
        "fear", "nervous", "scared", "afraid", "anxious", "horrible", "terrible", "awful",
        "disappointing", "boring", "uncomfortable", "worth", "professional", "personable",
        "skilled", "unbelievable", "epic", "grandeur", "priceless", "calm", "grateful",
    }
    texts = []
    for row in plotted.loc[plotted["word"].isin(annotate)].itertuples(index=False):
        texts.append(axis.text(row.raw_vader_word_score, row.mean_rating, row.word, fontsize=8.5, color="#1E293B"))
    adjust_text(texts, ax=axis, arrowprops={"arrowstyle": "->", "color": "#64748B", "lw": 0.55})
    axis.set_title(
        "Word Sentiment Scatter Plot: Raw VADER Word Score (-4.0 to +4.0) vs Tourist Rating (1.0 to 5.0)\n"
        "[Canonical-v2 NRC Primary Display Colors + CATE; stable review_id links]",
        fontsize=15,
        fontweight="bold",
    )
    axis.set_xlabel("Raw VADER lexicon score of the word (-4 to +4; 0 may mean absent from VADER)", fontsize=11)
    axis.set_ylabel("Mean star rating of canonical English reviews containing the word", fontsize=11)
    axis.set_xlim(-4, 4)
    axis.set_ylim(1, 5.08)
    axis.legend(loc="lower left", fontsize=8.6, framealpha=0.96)
    fig.text(
        0.5,
        0.012,
        "Point = word; area = unique linked reviews. A review may link to many words. This is descriptive aggregation, not a review-level causal estimate.",
        ha="center",
        fontsize=9.5,
        color="#7F1D1D",
    )
    fig.tight_layout(rect=(0, 0.035, 1, 1))
    temporary = FIGURE_PATH.with_name(FIGURE_PATH.stem + ".tmp" + FIGURE_PATH.suffix)
    fig.savefig(temporary, dpi=240, bbox_inches="tight")
    plt.close(fig)
    temporary.replace(FIGURE_PATH)

    print(
        {
            "canonical_english_reviews": len(reviews),
            "approved_cate_terms": len(cate_words),
            "plotted_words": int(len(plotted)),
            "word_review_links": int(len(links)),
            "figure": str(FIGURE_PATH),
        }
    )


if __name__ == "__main__":
    sys.exit(main())
