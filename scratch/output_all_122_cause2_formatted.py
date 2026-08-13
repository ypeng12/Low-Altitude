#!/usr/bin/env python3
"""Format and print all 122 Cause 2 words clearly."""

import pandas as pd
from pathlib import Path
from nrclex import NRCLex

gold_path = Path("data/analyze/gold_emotion_master.csv")
df_gold = pd.read_csv(gold_path)
nrc_dict = NRCLex().__lexicon__

c3_awe = {"breathtaking", "stunning", "sublime", "scenic", "surreal", "majestic", "panoramic", "spellbinding", "mesmerizing", "awe"}
c4_risk = {"claustrophobia", "jitters", "airsick", "phobia", "unnerving"}

cause2_all_words = []

for row in df_gold.itertuples():
    w = str(row.word).lower().strip()
    lemma = str(row.canonical_lemma).lower().strip()
    
    nrc_tags = nrc_dict.get(w, []) or nrc_dict.get(lemma, [])
    has_any = len(nrc_tags) > 0
    
    if not has_any:
        if w not in c3_awe and w not in c4_risk:
            if not (w.endswith("ing") or w.endswith("ed") or w.endswith("ly") or w.endswith("est") or w.endswith("er")):
                cause2_all_words.append({
                    'word': w,
                    'canonical_lemma': lemma,
                    'frequency_21215': row.frequency_21215,
                    'chinese_translation': row.chinese_translation
                })

df_c2_all = pd.DataFrame(cause2_all_words).sort_values('frequency_21215', ascending=False).reset_index(drop=True)
df_c2_all.index += 1

print("Rank | Word | Canonical Lemma | Frequency | Chinese Translation")
for idx, r in df_c2_all.iterrows():
    print(f"{idx:3d} | {r['word']:18s} | {r['canonical_lemma']:18s} | {r['frequency_21215']:5d} | {r['chinese_translation']}")
