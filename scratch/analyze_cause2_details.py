#!/usr/bin/env python3
"""Deep dive into Cause 2: Modern Online Tourism Colloquial Superlatives."""

import pandas as pd
from pathlib import Path
from nrclex import NRCLex

gold_path = Path("data/analyze/gold_emotion_master.csv")
df_gold = pd.read_csv(gold_path)
nrc_dict = NRCLex().__lexicon__

c2_words = ["great", "awesome", "fantastic", "incredible", "incredibly", "nice", "fabulous", "phenomenal", "unbeatable", "top-notch", "topnotch", "stellar", "prime", "primo", "epic", "mind-blowing"]

c2_details = []

for row in df_gold.itertuples():
    w = str(row.word).lower().strip()
    lemma = str(row.canonical_lemma).lower().strip()
    
    if w in c2_words or lemma in c2_words:
        nrc_tags_w = nrc_dict.get(w, [])
        nrc_tags_lemma = nrc_dict.get(lemma, [])
        
        c2_details.append({
            'word': w,
            'canonical_lemma': lemma,
            'freq': row.frequency_21215,
            'chinese': row.chinese_translation,
            'nrc_raw_status': "In NRC" if len(nrc_tags_w) > 0 else "NOT in NRC",
            'nrc_lemma_status': "In NRC" if len(nrc_tags_lemma) > 0 else "NOT in NRC"
        })

df_c2 = pd.DataFrame(c2_details).sort_values('freq', ascending=False)

print("=== 🔬 CAUSE 2 DEEP DIVE AUDIT ===")
print(f"Total Cause 2 Words: {len(df_c2)}")
print(f"Total Review Mentions: {df_c2['freq'].sum():,} across N=21,215 reviews\n")

print(df_c2.to_string(index=False))
