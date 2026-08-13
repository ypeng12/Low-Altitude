#!/usr/bin/env python3
"""Find exact 17 words that differ between Raw Match and Lemma Normalized Match."""

import pandas as pd
from pathlib import Path
from nrclex import NRCLex

gold_path = Path("data/analyze/gold_emotion_master.csv")
df_gold = pd.read_csv(gold_path)

nrc_dict = NRCLex().__lexicon__
NRC8 = {"anger", "anticipation", "disgust", "fear", "joy", "sadness", "surprise", "trust"}

raw_8_words = []
lemma_8_words = []
diff_words = []

for row in df_gold.itertuples():
    w = str(row.word).lower().strip()
    lemma = str(row.canonical_lemma).lower().strip()
    
    raw_tags = nrc_dict.get(w, [])
    lemma_tags = nrc_dict.get(lemma, [])
    
    has_raw_8 = len(set(raw_tags) & NRC8) > 0
    has_lemma_8 = len(set(lemma_tags) & NRC8) > 0
    
    if has_raw_8:
        raw_8_words.append(w)
    if (has_raw_8 or has_lemma_8):
        lemma_8_words.append(w)
        
    if (not has_raw_8) and has_lemma_8:
        diff_words.append({
            'word': w,
            'canonical_lemma': lemma,
            'chinese_translation': row.chinese_translation,
            'frequency_21215': row.frequency_21215,
            'lemma_nrc_emotions': ', '.join(set(lemma_tags) & NRC8)
        })

df_diff = pd.DataFrame(diff_words).sort_values('frequency_21215', ascending=False)

print(f"Raw 8-Emotion Match Count: {len(raw_8_words)}")
print(f"Lemma Normalized 8-Emotion Match Count: {len(lemma_8_words)}")
print(f"Difference Count: {len(df_diff)} words\n")

print("Exact 17 Words saved by Lemma Normalization (Mapped to NRC 8-Emotions via Lemma):")
print(df_diff.to_string(index=False))
