#!/usr/bin/env python3
"""Generate clean 0/1 One-Hot Encoded NRC 8 Emotion Matrix Excel files in data/analyze/."""

import pandas as pd
from pathlib import Path
from nrclex import NRCLex

analyze_dir = Path("data/analyze")
gold_path = analyze_dir / "gold_emotion_master.csv"

df_gold = pd.read_csv(gold_path)
nrc_dict = NRCLex().__lexicon__

NRC8_COLS = ["anger", "anticipation", "disgust", "fear", "joy", "sadness", "surprise", "trust"]

# Prepare Master 0/1 Matrix for all 630 Gold Words
onehot_rows = []

for row in df_gold.itertuples():
    w = str(row.word).lower().strip()
    lemma = str(row.canonical_lemma).lower().strip()
    
    nrc_tags = set(nrc_dict.get(w, [])) | set(nrc_dict.get(lemma, []))
    
    item = {
        'word': w,
        'canonical_lemma': lemma,
        'chinese_translation': row.chinese_translation,
        'frequency_21215': row.frequency_21215,
        'review_count_21215': row.review_count_21215
    }
    
    # 0/1 One-Hot for NRC 8
    for col in NRC8_COLS:
        item[col] = 1 if col in nrc_tags else 0
        
    # Polarities
    item['positive'] = 1 if 'positive' in nrc_tags else 0
    item['negative'] = 1 if 'negative' in nrc_tags else 0
    item['nrc_unmapped'] = 1 if not nrc_tags else 0
    
    onehot_rows.append(item)

df_onehot = pd.DataFrame(onehot_rows)

# Sort columns cleanly: word, canonical_lemma, chinese_translation, frequency_21215, review_count_21215, anger, anticipation, disgust, fear, joy, sadness, surprise, trust, positive, negative, nrc_unmapped
cols_order = ['word', 'canonical_lemma', 'chinese_translation', 'frequency_21215', 'review_count_21215'] + NRC8_COLS + ['positive', 'negative', 'nrc_unmapped']
df_onehot = df_onehot[cols_order].sort_values('frequency_21215', ascending=False).reset_index(drop=True)

# Save Master 0/1 Matrix for all 630 Gold Words
df_onehot.to_excel(analyze_dir / "gold_emotion_nrc8_onehot.xlsx", index=False)
df_onehot.to_csv(analyze_dir / "gold_emotion_nrc8_onehot.csv", index=False, encoding='utf-8-sig')

# Save 0/1 Matrix exclusively for the 286 Words IN NRC 8 (matching user's exact screenshot format)
df_inc_onehot = df_onehot[df_onehot[NRC8_COLS].sum(axis=1) > 0][['word', 'canonical_lemma', 'chinese_translation', 'frequency_21215'] + NRC8_COLS].reset_index(drop=True)

df_inc_onehot.to_excel(analyze_dir / "nrc8_words_included_onehot.xlsx", index=False)
df_inc_onehot.to_csv(analyze_dir / "nrc8_words_included_onehot.csv", index=False, encoding='utf-8-sig')

print(f"Successfully generated 0/1 One-Hot Excel matrices in data/analyze/:")
print(f"  1. Master 630 Gold Words 0/1 Matrix: {analyze_dir / 'gold_emotion_nrc8_onehot.xlsx'}")
print(f"  2. NRC 8 Included 286 Words 0/1 Matrix: {analyze_dir / 'nrc8_words_included_onehot.xlsx'}")
