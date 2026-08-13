#!/usr/bin/env python3
"""Export exact list of words NOT in NRC's 8 basic emotion categories (346 words)."""

import pandas as pd
from pathlib import Path
from nrclex import NRCLex

analyze_dir = Path("data/analyze")
gold_path = analyze_dir / "gold_emotion_master.csv"

df_gold = pd.read_csv(gold_path)
nrc_dict = NRCLex().__lexicon__

NRC8 = {"anger", "anticipation", "disgust", "fear", "joy", "sadness", "surprise", "trust"}

not_in_nrc8 = []

for row in df_gold.itertuples():
    w = str(row.word).lower().strip()
    lemma = str(row.canonical_lemma).lower().strip()
    
    tags = nrc_dict.get(w, []) or nrc_dict.get(lemma, [])
    nrc_8_tags = set(tags) & NRC8
    
    if len(nrc_8_tags) == 0:
        # Does not belong to NRC 8 emotions
        nrc_status = "Unmapped in NRC" if len(tags) == 0 else f"NRC Polarity Only ({', '.join(tags)})"
        not_in_nrc8.append({
            'word': w,
            'canonical_lemma': lemma,
            'chinese_translation': row.chinese_translation,
            'emotion_category': row.emotion_category,
            'affect_type': row.affect_type,
            'frequency_21215': row.frequency_21215,
            'review_count_21215': row.review_count_21215,
            'nrc_status': nrc_status,
            'example_context': row.example_context
        })

df_not_in_nrc8 = pd.DataFrame(not_in_nrc8).sort_values('frequency_21215', ascending=False).reset_index(drop=True)

# Export to Excel and CSV in data/analyze/
df_not_in_nrc8.to_excel(analyze_dir / "words_not_in_nrc8_emotions.xlsx", index=False)
df_not_in_nrc8.to_csv(analyze_dir / "words_not_in_nrc8_emotions.csv", index=False, encoding='utf-8-sig')

print(f"Total Master Gold Lexicon Terms: {len(df_gold)}")
print(f"Words NOT in NRC 8 Basic Emotion Categories: {len(df_not_in_nrc8)} words (Saved to data/analyze/words_not_in_nrc8_emotions.xlsx)")

print("\nSample Top 30 High-Frequency Words NOT in NRC 8 Emotions:")
print(df_not_in_nrc8[['word', 'chinese_translation', 'frequency_21215', 'nrc_status']].head(30).to_string())
