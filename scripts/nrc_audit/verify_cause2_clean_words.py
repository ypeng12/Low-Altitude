#!/usr/bin/env python3
"""Verify exact list of Cause 2 words that are 100% missed by NRC."""

import pandas as pd
from pathlib import Path
from nrclex import NRCLex

gold_path = Path("data/analyze/gold_emotion_master.csv")
df_gold = pd.read_csv(gold_path)
nrc_dict = NRCLex().__lexicon__

c2_candidates = ["great", "awesome", "fantastic", "incredible", "incredibly", "nice", "fabulous", "phenomenal", "unbeatable", "top-notch", "topnotch", "primo", "mind-blowing"]

pure_missed_c2 = []

for row in df_gold.itertuples():
    w = str(row.word).lower().strip()
    lemma = str(row.canonical_lemma).lower().strip()
    
    nrc_tags_w = nrc_dict.get(w, [])
    nrc_tags_lemma = nrc_dict.get(lemma, [])
    
    # Check if completely missed by NRC (0 tags)
    if len(nrc_tags_w) == 0 and len(nrc_tags_lemma) == 0:
        if w in c2_candidates or lemma in c2_candidates:
            pure_missed_c2.append({
                'word': w,
                'canonical_lemma': lemma,
                'frequency_21215': row.frequency_21215,
                'chinese_translation': row.chinese_translation
            })

df_pure_c2 = pd.DataFrame(pure_missed_c2).sort_values('frequency_21215', ascending=False)
print("=== 📋 PURE 100% MISSED CAUSE 2 WORDS (EXCLUDING STELLAR) ===")
print(df_pure_c2.to_string(index=False))
print(f"\nTotal Pure Cause 2 Missed Words Count: {len(df_pure_c2)}")
print(f"Total Pure Cause 2 Missed Review Mentions: {df_pure_c2['frequency_21215'].sum():,}")
