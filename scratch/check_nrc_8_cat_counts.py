#!/usr/bin/env python3
"""Check how many words in official NRC lexicon and in Master Gold Lexicon map to NRC's 8 basic emotion categories."""

import pandas as pd
from nrclex import NRCLex

nrc_dict = NRCLex().__lexicon__
NRC8 = {"anger", "anticipation", "disgust", "fear", "joy", "sadness", "surprise", "trust"}

# 1. Official NRC Lexicon Statistics
official_nrc_total = len(nrc_dict)
official_nrc_8_words = 0
official_nrc_only_polarity = 0

for word, tags in nrc_dict.items():
    has_8 = len(set(tags) & NRC8) > 0
    if has_8:
        official_nrc_8_words += 1
    else:
        official_nrc_only_polarity += 1

# 2. Master Gold Emotion Lexicon (632 words) Statistics
gold_df = pd.read_csv("data/analyze/gold_emotion_master.csv")
gold_total = len(gold_df)
gold_nrc_8_words = 0
gold_nrc_only_polarity = 0
gold_nrc_missed = 0

for row in gold_df.itertuples():
    w = str(row.word).lower().strip()
    lemma = str(row.canonical_lemma).lower().strip()
    
    tags = nrc_dict.get(w, []) or nrc_dict.get(lemma, [])
    has_8 = len(set(tags) & NRC8) > 0
    has_any = len(tags) > 0
    
    if has_8:
        gold_nrc_8_words += 1
    elif has_any:
        gold_nrc_only_polarity += 1
    else:
        gold_nrc_missed += 1

print("=== 📊 NRC 8 Basic Emotion Category Vocabulary Audit ===")

print(f"\n1. Official NRC Lexicon (6,468 Total Unique Words):")
print(f"   - Words with 8 Basic Emotion Tags: {official_nrc_8_words:,} words ({official_nrc_8_words/official_nrc_total*100:.2f}%)")
print(f"   - Words with ONLY Positive/Negative Polarity: {official_nrc_only_polarity:,} words ({official_nrc_only_polarity/official_nrc_total*100:.2f}%)")

print(f"\n2. Our Master Gold Emotion Lexicon (632 Total Words):")
print(f"   - Words mapped to NRC 8 Basic Emotions: {gold_nrc_8_words} words ({gold_nrc_8_words/gold_total*100:.2f}%)")
print(f"   - Words with ONLY NRC Polarity Tag: {gold_nrc_only_polarity} words ({gold_nrc_only_polarity/gold_total*100:.2f}%)")
print(f"   - Words MISSED completely by NRC: {gold_nrc_missed} words ({gold_nrc_missed/gold_total*100:.2f}%)")

print("\n--- Detailed Breakdown of NRC 8 Basic Emotions across Master Gold Lexicon ---")
nrc8_counts = {}
for e in ["joy", "fear", "trust", "sadness", "surprise", "anticipation", "anger", "disgust"]:
    cnt = sum(1 for row in gold_df.itertuples() if e in (nrc_dict.get(str(row.word).lower().strip(), []) or nrc_dict.get(str(row.canonical_lemma).lower().strip(), [])))
    nrc8_counts[e] = cnt
    print(f"  - {e.upper():12s}: {cnt:3d} words ({cnt/gold_total*100:.2f}%)")
