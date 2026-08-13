#!/usr/bin/env python3
"""Deep dive into Cause 1: Morphological Variants (-ing, -ed, -ly, -est, -er) in NRC missed words."""

import pandas as pd
from pathlib import Path

gold_path = Path("data/analyze/gold_emotion_master.csv")
df_gold = pd.read_csv(gold_path)

from nrclex import NRCLex
nrc_dict = NRCLex().__lexicon__

ing_ed_list = []
ly_est_er_list = []

for row in df_gold.itertuples():
    w = str(row.word).lower().strip()
    lemma = str(row.canonical_lemma).lower().strip()
    
    nrc_tags = nrc_dict.get(w, []) or nrc_dict.get(lemma, [])
    has_any = len(nrc_tags) > 0
    
    if not has_any:
        freq = row.frequency_21215
        trans = row.chinese_translation
        
        if w.endswith("ing") or w.endswith("ed"):
            ing_ed_list.append({'word': w, 'canonical_lemma': lemma, 'freq': freq, 'chinese': trans, 'suffix': '-ing' if w.endswith('ing') else '-ed'})
        elif w.endswith("ly") or w.endswith("est") or w.endswith("er"):
            suf = '-ly' if w.endswith('ly') else ('-est' if w.endswith('est') else '-er')
            ly_est_er_list.append({'word': w, 'canonical_lemma': lemma, 'freq': freq, 'chinese': trans, 'suffix': suf})

df_participle = pd.DataFrame(ing_ed_list).sort_values('freq', ascending=False)
df_adverb_superlative = pd.DataFrame(ly_est_er_list).sort_values('freq', ascending=False)

print("=== 🔬 CAUSE 1 DEEP DIVE AUDIT ===")
print(f"Total Participles (-ing / -ed): {len(df_participle)} words (Sum Frequency: {df_participle['freq'].sum():,} mentions)")
print(f"Total Adverbs & Superlatives (-ly, -est, -er): {len(df_adverb_superlative)} words (Sum Frequency: {df_adverb_superlative['freq'].sum():,} mentions)")

print("\n--- Top 15 Participle Emotion Adjectives (-ing / -ed) ---")
print(df_participle.head(15).to_string(index=False))

print("\n--- Top 15 Adverbs & Superlatives (-ly, -est, -er) ---")
print(df_adverb_superlative.head(15).to_string(index=False))
