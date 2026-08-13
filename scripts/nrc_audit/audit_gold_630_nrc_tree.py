#!/usr/bin/env python3
"""Audit exact tree breakdown of Master Gold Emotion Codebook (630 words) against NRC Lexicon categories."""

import pandas as pd
from pathlib import Path
from nrclex import NRCLex

gold_path = Path("data/analyze/gold_emotion_master.csv")
df_gold = pd.read_csv(gold_path)

nrc_dict = NRCLex().__lexicon__
NRC8 = {"anger", "anticipation", "disgust", "fear", "joy", "sadness", "surprise", "trust"}

cnt_8_emotion = 0
cnt_polarity_only = 0
cnt_completely_missed = 0

words_8_emotion = []
words_polarity_only = []
words_completely_missed = []

for row in df_gold.itertuples():
    w = str(row.word).lower().strip()
    lemma = str(row.canonical_lemma).lower().strip()
    
    nrc_tags = nrc_dict.get(w, []) or nrc_dict.get(lemma, [])
    has_8 = len(set(nrc_tags) & NRC8) > 0
    has_any = len(nrc_tags) > 0
    
    if has_8:
        cnt_8_emotion += 1
        words_8_emotion.append((w, row.chinese_translation, row.frequency_21215))
    elif has_any:
        cnt_polarity_only += 1
        words_polarity_only.append((w, row.chinese_translation, row.frequency_21215))
    else:
        cnt_completely_missed += 1
        words_completely_missed.append((w, row.chinese_translation, row.frequency_21215))

total_in_nrc = cnt_8_emotion + cnt_polarity_only
total_gold = len(df_gold)

print("=== 📊 Master Gold Emotion Codebook (630 Words) vs. NRC Lexicon Breakdown ===")
print(f"Total Master Gold Emotion Terms: {total_gold} words\n")

print(f"1. Total Covered by NRC (在 NRC 词库里的总词数): {total_in_nrc} 个词 ({total_in_nrc/total_gold*100:.2f}%)")
print(f"   ├── 1a. 在 NRC 8 大 Emotion 分类里的词: {cnt_8_emotion} 个词 ({cnt_8_emotion/total_gold*100:.2f}%)")
print(f"   └── 1b. 只有 Positive / Negative 极性标记的词: {cnt_polarity_only} 个词 ({cnt_polarity_only/total_gold*100:.2f}%)")

print(f"\n2. Completely MISSED by NRC (完全不在 NRC 词库里的领域词): {cnt_completely_missed} 个词 ({cnt_completely_missed/total_gold*100:.2f}%)")

print("\n--- Math Check ---")
print(f"  {cnt_8_emotion} (8大Emotion) + {cnt_polarity_only} (仅Positive/Negative) + {cnt_completely_missed} (都不在NRC) = {cnt_8_emotion + cnt_polarity_only + cnt_completely_missed} (Matches {total_gold} 100%)")
