"""Auditable unigram extraction for open emotion-word coding."""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Any

import nltk
import pandas as pd
from nltk.corpus import stopwords


TOKEN_PATTERN = re.compile(r"[A-Za-z]+(?:['’][A-Za-z]+)?")
SENTENCE_LEFT = re.compile(r"[.!?\n]\s*")


@dataclass(frozen=True)
class TokenRecord:
    review_id: str
    token_index: int
    surface: str
    normalized_word: str
    lemma: str
    normalization_method: str
    penn_pos: str
    coarse_pos: str
    char_start: int
    char_end: int
    context: str
    candidate_eligible: bool
    eligibility_reason: str


def require_nltk_resources(resources: list[str]) -> None:
    missing: list[str] = []
    for resource in resources:
        try:
            nltk.data.find(resource)
        except LookupError:
            missing.append(resource)
    if missing:
        names = " ".join(item.split("/", 1)[1] for item in missing)
        raise RuntimeError(
            "Missing required NLTK resources: "
            f"{missing}. Install them with: python -m nltk.downloader {names}"
        )


def coarse_pos(penn_tag: str) -> str:
    if penn_tag.startswith("JJ"):
        return "ADJ"
    if penn_tag.startswith("RB"):
        return "ADV"
    if penn_tag.startswith("NNP"):
        return "PROPN"
    if penn_tag.startswith("NN"):
        return "NOUN"
    if penn_tag.startswith("VB"):
        return "VERB"
    return "OTHER"


def context_window(text: str, start: int, end: int, maximum_characters: int) -> str:
    left = max(text.rfind(".", 0, start), text.rfind("!", 0, start), text.rfind("?", 0, start), text.rfind("\n", 0, start)) + 1
    right_candidates = [position for marker in ".!?\n" if (position := text.find(marker, end)) >= 0]
    right = min(right_candidates) + 1 if right_candidates else len(text)
    raw_context = text[left:right]
    context = " ".join(raw_context.split())
    if len(context) <= maximum_characters:
        return context
    half = max(maximum_characters // 2, 1)
    local_left = max(left, start - half)
    local_right = min(right, end + half)
    return " ".join(text[local_left:local_right].split())


def extract_review_tokens(
    review_id: str,
    text: str,
    *,
    minimum_letters: int,
    eligible_coarse_pos: set[str],
    maximum_context_characters: int,
    lemmatization_method: str = "lowercase_surface",
) -> list[TokenRecord]:
    matches = [match for match in TOKEN_PATTERN.finditer(text)]
    if not matches:
        return []
    raw_surfaces = [match.group(0) for match in matches]
    tag_surfaces = [surface.replace("’", "'") for surface in raw_surfaces]
    tagged = nltk.pos_tag(tag_surfaces, lang="eng")
    if lemmatization_method != "lowercase_surface":
        raise ValueError("Only the auditable lowercase_surface normalization is enabled")
    stop_words = set(stopwords.words("english"))
    records: list[TokenRecord] = []
    for token_index, (match, raw_surface, (tag_surface, penn)) in enumerate(
        zip(matches, raw_surfaces, tagged), start=1
    ):
        normalized = tag_surface.lower()
        coarse = coarse_pos(penn)
        letters = sum(character.isalpha() for character in normalized)
        lemma = normalized
        reasons: list[str] = []
        if letters < minimum_letters:
            reasons.append("below_minimum_letters")
        if normalized in stop_words:
            reasons.append("function_stopword")
        if coarse not in eligible_coarse_pos:
            reasons.append(f"ineligible_pos:{coarse}")
        eligible = not reasons
        records.append(
            TokenRecord(
                review_id=str(review_id),
                token_index=token_index,
                surface=raw_surface,
                normalized_word=normalized,
                lemma=lemma,
                normalization_method=lemmatization_method,
                penn_pos=penn,
                coarse_pos=coarse,
                char_start=match.start(),
                char_end=match.end(),
                context=context_window(text, match.start(), match.end(), maximum_context_characters),
                candidate_eligible=eligible,
                eligibility_reason="eligible_content_word" if eligible else "|".join(reasons),
            )
        )
    return records


def extract_stage_occurrences(
    reviews: pd.DataFrame,
    *,
    text_field: str,
    minimum_letters: int,
    eligible_coarse_pos: list[str],
    maximum_context_characters: int,
    lemmatization_method: str = "lowercase_surface",
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for row in reviews.sort_values("sampling_rank", kind="stable").itertuples(index=False):
        text = str(getattr(row, text_field) or "")
        tokens = extract_review_tokens(
            str(row.review_id),
            text,
            minimum_letters=minimum_letters,
            eligible_coarse_pos=set(eligible_coarse_pos),
            maximum_context_characters=maximum_context_characters,
            lemmatization_method=lemmatization_method,
        )
        for token in tokens:
            item = token.__dict__.copy()
            item["sampling_rank"] = int(row.sampling_rank)
            rows.append(item)
    columns = list(TokenRecord.__dataclass_fields__) + ["sampling_rank"]
    return pd.DataFrame(rows, columns=columns)


def build_candidate_inventory(occurrences: pd.DataFrame, examples_per_word: int) -> pd.DataFrame:
    eligible = occurrences[occurrences["candidate_eligible"]].copy()
    rows: list[dict[str, Any]] = []
    for lemma, group in eligible.groupby("lemma", sort=True, observed=True):
        group = group.sort_values(["sampling_rank", "review_id", "token_index"], kind="stable")
        contexts: list[str] = []
        seen_contexts: set[tuple[str, str]] = set()
        for item in group.itertuples(index=False):
            key = (str(item.review_id), str(item.context))
            if key in seen_contexts:
                continue
            seen_contexts.add(key)
            contexts.append(f"{item.review_id} :: {item.context}")
            if len(contexts) >= examples_per_word:
                break
        surface_counts = Counter(group["surface"].str.lower())
        pos_counts = Counter(group["coarse_pos"])
        rows.append(
            {
                "lemma": lemma,
                "surface_forms": "|".join(word for word, _ in surface_counts.most_common()),
                "coarse_pos": "|".join(tag for tag, _ in pos_counts.most_common()),
                "token_frequency_in_stage": int(len(group)),
                "review_frequency_in_stage": int(group["review_id"].nunique()),
                "representative_contexts": "\n".join(contexts),
                "human_approved_lemma": "",
                "human_word_family": "",
                "ai_status": "",
                "ai_provisional_category": "",
                "ai_rationale": "",
                "ai_confidence": "",
                "human_status": "",
                "human_category": "",
                "human_rationale": "",
                "adjudicated_status": "",
                "adjudicated_category": "",
                "annotation_notes": "",
            }
        )
    inventory = pd.DataFrame(rows)
    if inventory.empty:
        return inventory
    return inventory.sort_values(
        ["review_frequency_in_stage", "token_frequency_in_stage", "lemma"],
        ascending=[False, False, True],
        kind="stable",
    ).reset_index(drop=True)
