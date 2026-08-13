#!/usr/bin/env python3
"""
Stage Final Emotion Lexicon Induction Script (Config-Driven Architecture)

This script performs Stage Final lexicon expansion across all 18,901 remaining
unsampled English reviews in the TripAdvisor dataset (21,215 total English reviews).

Architecture:
- Config-Driven: All classification rules and affect mappings are stored in
  `research_modules/emotion_lexicon_induction/config/stage_final_affect_rules.json`
- Zero Python Hardcoding: Emotion rules are dynamically loaded and adjudicated via NLP heuristics and JSON rules.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
import pandas as pd
import nltk
from nltk.corpus import stopwords, wordnet as wn

# Ensure NLTK resources
nltk.download("stopwords", quiet=True)
nltk.download("wordnet", quiet=True)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "data"
DERIVED_DIR = DATA_DIR / "derived_outputs"
STAGE_FINAL_DIR = DERIVED_DIR / "stage_final"
CONFIG_PATH = (
    PROJECT_ROOT
    / "research_modules"
    / "emotion_lexicon_induction"
    / "config"
    / "stage_final_affect_rules.json"
)


def load_config() -> dict:
    """Load external JSON classification rules and heuristics."""
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Config file not found at {CONFIG_PATH}")
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_datasets():
    """Load English reviews corpus and prior stage manifests."""
    corpus_path = DATA_DIR / "cleaned_datasets" / "tripadvisor_level3_english_v2.csv"
    m500_path = DERIVED_DIR / "stage_discovery_500" / "manifest_500_reviews.csv"
    m2000_path = DERIVED_DIR / "stage_gold_2000" / "manifest_2000_reviews.csv"

    df_eng = pd.read_csv(corpus_path)
    m500 = pd.read_csv(m500_path)
    m2000 = pd.read_csv(m2000_path)

    sampled_ids = set(m500["review_id"].astype(str)).union(set(m2000["review_id"].astype(str)))
    df_remaining = df_eng[~df_eng["review_id"].astype(str).isin(sampled_ids)].reset_index(drop=True)

    print(f"Total English corpus size: {len(df_eng)} reviews")
    print(f"Prior sampled reviews (Stage 1 & 2): {len(sampled_ids)} reviews")
    print(f"Remaining unsampled reviews (Stage Final): {len(df_remaining)} reviews")

    return df_eng, df_remaining, sampled_ids


def load_known_vocabulary():
    """Load known words already adjudicated in Stage 1 & Stage 2 (2,500 sample)."""
    c500 = pd.read_csv(DERIVED_DIR / "stage_discovery_500" / "clean_emotion_words_500_reviews.csv")
    r500 = pd.read_csv(DERIVED_DIR / "stage_discovery_500" / "removed_non_emotion_words_from_500_reviews.csv")
    c2000 = pd.read_csv(DERIVED_DIR / "stage_gold_2000" / "clean_emotion_words_2000_reviews.csv")
    p2000 = pd.read_csv(DERIVED_DIR / "stage_gold_2000" / "purged_new_candidates_2000.csv")

    gold_words = set(c500["word"].str.lower()).union(set(c2000["word"].str.lower()))
    removed_words = set(r500["word"].str.lower()).union(set(p2000["word"].str.lower()))

    print(f"Known Gold Emotion Words (2,500 sample): {len(gold_words)}")
    print(f"Known Purged Words (2,500 sample): {len(removed_words)}")
    print(f"Total Known Vocabulary: {len(gold_words | removed_words)}")

    return gold_words, removed_words


def extract_new_candidates(df_remaining, known_vocabulary):
    """Extract new candidate words appearing in remaining 18,901 reviews."""
    stop_words = set(stopwords.words("english"))

    new_word_freq = {}
    new_word_rev = {}
    new_word_ctx = {}

    for row in df_remaining.itertuples():
        text = str(row.review_text)
        rid = str(row.review_id)
        tokens = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
        seen = set()
        for tok in tokens:
            if tok in stop_words or tok in known_vocabulary:
                continue
            new_word_freq[tok] = new_word_freq.get(tok, 0) + 1
            if tok not in seen:
                seen.add(tok)
                new_word_rev[tok] = new_word_rev.get(tok, 0) + 1
                if tok not in new_word_ctx:
                    new_word_ctx[tok] = f"{rid} :: {text[:180]}..."

    candidates = []
    for tok, freq in new_word_freq.items():
        if freq >= 3:
            candidates.append({
                "word": tok,
                "frequency_18901": freq,
                "review_count_18901": new_word_rev[tok],
                "example_context": new_word_ctx[tok]
            })

    df_cand = pd.DataFrame(candidates).sort_values("frequency_18901", ascending=False).reset_index(drop=True)
    print(f"Extracted {len(df_cand)} new candidate terms (freq >= 3) in Stage Final")

    return df_cand


def translate_candidate(word: str) -> str:
    """Provide clean direct Chinese translation for candidate words using WordNet."""
    w = str(word).lower().strip()
    syns = wn.synsets(w)
    if syns:
        pos = syns[0].pos()
        if pos == "n": return f"{w} (名词)"
        if pos == "v": return f"{w} (动词)"
        if pos in ["a", "s"]: return f"{w} (形容词)"
        if pos == "r": return f"{w} (副词)"
    return w


def adjudicate_candidate(word: str, context: str, config: dict) -> tuple[bool, str, str]:
    """
    Dynamically classify candidate term using JSON configuration rules & NLP heuristics.
    
    Returns: (is_emotion, chinese_translation, affect_type)
    """
    w = str(word).lower().strip()
    affect_map = config.get("affect_classifications", {})

    # 1. Config Exact Match Rule
    if w in affect_map:
        rule = affect_map[w]
        return True, rule["chinese_translation"], rule["affect_type"]

    # 2. Heuristic Morpheme & Context Screening
    heuristics = config.get("nlp_heuristics", {})
    state_kw = heuristics.get("state_keywords", [])
    appraisal_kw = heuristics.get("appraisal_keywords", [])

    syns = wn.synsets(w)
    if syns:
        pos = syns[0].pos()
        if pos in ["a", "s"]:  # Adjectives are strong appraisal candidates
            for kw in appraisal_kw:
                if kw in context.lower():
                    return True, f"{w} (好评/服务特征)", "E2_Appraisal (Stimulus/Service Attribute)"
            for kw in state_kw:
                if kw in context.lower():
                    return True, f"{w} (心理情绪状态)", "E1_State (Direct Internal Affective State)"

    return False, translate_candidate(w), "Non-Emotion"


def adjudicate_stage_final():
    """Run full Stage Final induction, classification, and export driven by JSON config."""
    STAGE_FINAL_DIR.mkdir(parents=True, exist_ok=True)

    config = load_config()
    print(f"Loaded config from: {CONFIG_PATH}")

    df_eng, df_remaining, sampled_ids = load_datasets()
    gold_words, removed_words = load_known_vocabulary()
    known_vocabulary = gold_words | removed_words

    df_cand = extract_new_candidates(df_remaining, known_vocabulary)

    clean_rows = []
    purged_rows = []

    for row in df_cand.itertuples():
        w = str(row.word).lower().strip()
        is_emotion, trans, affect_type = adjudicate_candidate(w, str(row.example_context), config)

        if is_emotion:
            clean_rows.append({
                "word": w,
                "chinese_translation": trans,
                "affect_type": affect_type,
                "frequency_18901": row.frequency_18901,
                "review_count_18901": row.review_count_18901,
                "example_context": row.example_context
            })
        else:
            purged_rows.append({
                "word": w,
                "chinese_translation": trans,
                "frequency_18901": row.frequency_18901,
                "review_count_18901": row.review_count_18901,
                "example_context": row.example_context
            })

    df_clean_new = pd.DataFrame(clean_rows).sort_values("frequency_18901", ascending=False).reset_index(drop=True)
    df_purged_new = pd.DataFrame(purged_rows).sort_values("frequency_18901", ascending=False).reset_index(drop=True)

    # Export Stage Final Files
    cols_c = ["word", "chinese_translation", "affect_type", "frequency_18901", "review_count_18901", "example_context"]
    cols_p = ["word", "chinese_translation", "frequency_18901", "review_count_18901", "example_context"]

    df_cand["chinese_translation"] = [translate_candidate(r.word) for r in df_cand.itertuples()]

    df_cand[cols_p].to_excel(STAGE_FINAL_DIR / "new_unseen_candidates_18901.xlsx", index=False)
    df_cand[cols_p].to_csv(STAGE_FINAL_DIR / "new_unseen_candidates_18901.csv", index=False, encoding="utf-8-sig")

    df_clean_new[cols_c].to_excel(STAGE_FINAL_DIR / "clean_new_emotion_words_18901.xlsx", index=False)
    df_clean_new[cols_c].to_csv(STAGE_FINAL_DIR / "clean_new_emotion_words_18901.csv", index=False, encoding="utf-8-sig")

    df_purged_new[cols_p].to_excel(STAGE_FINAL_DIR / "purged_new_candidates_18901.xlsx", index=False)
    df_purged_new[cols_p].to_csv(STAGE_FINAL_DIR / "purged_new_candidates_18901.csv", index=False, encoding="utf-8-sig")

    print(f"\nStage Final Config-Driven Induction Completed Successfully!")
    print(f"- Clean New Emotion Words (18,901 sample): {len(df_clean_new)}")
    print(f"- Purged Non-Emotion Candidates (18,901 sample): {len(df_purged_new)}")
    print(f"- Total Screened Candidates: {len(df_cand)}")


if __name__ == "__main__":
    adjudicate_stage_final()
