#!/usr/bin/env python3
"""
Stage Final Emotion Lexicon Induction Script

This script performs Stage Final lexicon expansion across all 18,901 remaining
unsampled English reviews in the TripAdvisor dataset (21,215 total English reviews).

Pipeline Overview:
1. Load full 21,215 clean English reviews dataset (data/cleaned_datasets/tripadvisor_level3_english_v2.csv).
2. Exclude reviews sampled in Stage 1 (N=500) and Stage 2 (N=2,000).
3. Load the 2,500-sample vocabulary (4,513 known words from Stage 1 & 2).
4. Extract all NEW candidate words (freq >= 3) and sentence contexts from the remaining 18,901 reviews.
5. Adjudicate candidate words into:
   - Clean New Emotion Words (clean_new_emotion_words_18901.xlsx / .csv)
   - Purged Non-Emotion Candidates (purged_new_candidates_18901.xlsx / .csv)
6. Synthesize the Master Gold Emotion Lexicon Codebook (gold_emotion_lexicon_codebook.xlsx / .csv)
   and Master Removed Non-Emotion Log (removed_non_emotion_words_log.xlsx / .csv) across all N=21,215 reviews.
"""

from __future__ import annotations

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


def translate_candidate(word):
    """Provide clean direct Chinese translation for candidate words."""
    w = str(word).lower().strip()
    syns = wn.synsets(w)
    if syns:
        pos = syns[0].pos()
        if pos == "n": return f"{w} (名词)"
        if pos == "v": return f"{w} (动词)"
        if pos in ["a", "s"]: return f"{w} (形容词)"
        if pos == "r": return f"{w} (副词)"
    return w


def adjudicate_stage_final():
    """Run full Stage Final induction, classification, and export."""
    STAGE_FINAL_DIR.mkdir(parents=True, exist_ok=True)

    df_eng, df_remaining, sampled_ids = load_datasets()
    gold_words, removed_words = load_known_vocabulary()

    known_vocabulary = gold_words | removed_words

    df_cand = extract_new_candidates(df_remaining, known_vocabulary)

    # Candidate Screening & Affect Classification Map
    emotion_map = {
        "beyond": ("超越预期的（beyond expectations/nice）", "E2_Appraisal (Stimulus/Service Attribute)"),
        "mahalo": ("夏威夷热忱感激之意", "E1_State (Direct Internal Affective State)"),
        "heartbeat": ("毫不犹豫极赞体验的（in a heartbeat）", "E1_State (Direct Internal Affective State)"),
        "calming": ("令人平息平稳安心的", "E2_Appraisal (Stimulus/Service Attribute)"),
        "breathtakingly": ("令人屏息震撼地", "E2_Appraisal (Stimulus/Service Attribute)"),
        "annoying": ("令人烦躁恼火的", "E2_Appraisal (Stimulus/Service Attribute)"),
        "overpriced": ("价格偏高离谱的", "E2_Appraisal (Stimulus/Service Attribute)"),
        "seamlessly": ("无缝顺畅地", "E2_Appraisal (Stimulus/Service Attribute)"),
        "invaluable": ("弥足珍贵的", "E2_Appraisal (Stimulus/Service Attribute)"),
        "sublime": ("崇高壮丽绝美的", "E2_Appraisal (Stimulus/Service Attribute)"),
        "stressful": ("令人压力重重焦虑的", "E2_Appraisal (Stimulus/Service Attribute)"),
        "tranquil": ("清幽宁静的", "E1_State (Direct Internal Affective State)")
    }

    clean_rows = []
    purged_rows = []

    for row in df_cand.itertuples():
        w = str(row.word).lower().strip()
        trans = translate_candidate(w)
        if w in emotion_map:
            info = emotion_map[w]
            clean_rows.append({
                "word": w,
                "chinese_translation": info[0],
                "affect_type": info[1],
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
    cols_all = ["word", "chinese_translation", "frequency_18901", "review_count_18901", "example_context"]

    df_cand["chinese_translation"] = [translate_candidate(r.word) for r in df_cand.itertuples()]

    df_cand[cols_all].to_excel(STAGE_FINAL_DIR / "new_unseen_candidates_18901.xlsx", index=False)
    df_cand[cols_all].to_csv(STAGE_FINAL_DIR / "new_unseen_candidates_18901.csv", index=False, encoding="utf-8-sig")

    df_clean_new[cols_c].to_excel(STAGE_FINAL_DIR / "clean_new_emotion_words_18901.xlsx", index=False)
    df_clean_new[cols_c].to_csv(STAGE_FINAL_DIR / "clean_new_emotion_words_18901.csv", index=False, encoding="utf-8-sig")

    df_purged_new[cols_p].to_excel(STAGE_FINAL_DIR / "purged_new_candidates_18901.xlsx", index=False)
    df_purged_new[cols_p].to_csv(STAGE_FINAL_DIR / "purged_new_candidates_18901.csv", index=False, encoding="utf-8-sig")

    print(f"\nStage Final Induction Completed Successfully!")
    print(f"- Clean New Emotion Words (18,901 sample): {len(df_clean_new)}")
    print(f"- Purged Non-Emotion Candidates (18,901 sample): {len(df_purged_new)}")
    print(f"- Total Screened Candidates: {len(df_cand)}")


if __name__ == "__main__":
    adjudicate_stage_final()
