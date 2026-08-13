#!/usr/bin/env python3
"""Deep dive into Cause 3 and Cause 4 exact word lists and frequencies."""

import pandas as pd
from pathlib import Path
from nrclex import NRCLex

gold_path = Path("data/analyze/gold_emotion_master.csv")
df_gold = pd.read_csv(gold_path)
nrc_dict = NRCLex().__lexicon__

c3_keywords = {"breathtaking", "breathtakingly", "stunning", "stunningly", "sublime", "scenic", "surreal", "panoramic", "spellbinding", "mesmerizing", "awe", "awed"}
c4_keywords = {"claustrophobia", "claustrophobic", "jitters", "airsick", "phobia", "unnerving", "unnerved"}

c3_list = []
c4_list = []

for row in df_gold.itertuples():
    w = str(row.word).lower().strip()
    lemma = str(row.canonical_lemma).lower().strip()
    
    if w in c3_keywords or lemma in c3_keywords:
        c3_list.append({
            'word': w,
            'canonical_lemma': lemma,
            'freq': row.frequency_21215,
            'chinese': row.chinese_translation,
            'nrc_tags': len(nrc_dict.get(w, []))
        })
    elif w in c4_keywords or lemma in c4_keywords:
        c4_list.append({
            'word': w,
            'canonical_lemma': lemma,
            'freq': row.frequency_21215,
            'chinese': row.chinese_translation,
            'nrc_tags': len(nrc_dict.get(w, []))
        })

df_c3 = pd.DataFrame(c3_list).sort_values('freq', ascending=False)
df_c4 = pd.DataFrame(c4_list).sort_values('freq', ascending=False)

print("=== 🔬 CAUSE 3: AERIAL VISUAL AWE WORDS (TOTAL: {} WORDS) ===".format(len(df_c3)))
print(f"Total Frequency Sum: {df_c3['freq'].sum():,} mentions")
print(df_c3.to_string(index=False))

print("\n=== 🔬 CAUSE 4: FLIGHT PERCEIVED RISK WORDS (TOTAL: {} WORDS) ===".format(len(df_c4)))
print(f"Total Frequency Sum: {df_c4['freq'].sum():,} mentions")
print(df_c4.to_string(index=False))
