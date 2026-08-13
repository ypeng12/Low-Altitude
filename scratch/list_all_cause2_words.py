#!/usr/bin/env python3
"""List all exact words assigned to Cause 2 with frequency and translation."""

import pandas as pd
from pathlib import Path

gold_path = Path("data/analyze/gold_emotion_master.csv")
df_gold = pd.read_csv(gold_path)

c2_words = {"great", "awesome", "fantastic", "incredible", "incredibly", "nice", "fabulous", "phenomenal", "unbeatable", "top-notch", "topnotch", "stellar", "prime", "primo", "epic", "mind-blowing"}

c2_list = []

for row in df_gold.itertuples():
    w = str(row.word).lower().strip()
    lemma = str(row.canonical_lemma).lower().strip()
    
    if w in c2_words or lemma in c2_words:
        c2_list.append({
            'word': w,
            'canonical_lemma': lemma,
            'frequency_21215': row.frequency_21215,
            'chinese_translation': row.chinese_translation
        })

df_c2 = pd.DataFrame(c2_list).sort_values('frequency_21215', ascending=False)
print("=== 📋 ALL CAUSE 2 WORDS LIST (TOTAL: 10 UNIQUE WORDS) ===")
print(df_c2.to_string(index=False))
