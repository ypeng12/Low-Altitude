#!/usr/bin/env python3
"""Export exact breakdown files for words IN NRC 8 Basic Emotions vs. NOT IN NRC 8 Basic Emotions."""

import pandas as pd
from pathlib import Path
from nrclex import NRCLex

analyze_dir = Path("data/analyze")
gold_path = analyze_dir / "gold_emotion_master.csv"

df_gold = pd.read_csv(gold_path)
nrc_dict = NRCLex().__lexicon__

NRC8 = {"anger", "anticipation", "disgust", "fear", "joy", "sadness", "surprise", "trust"}

nrc8_included_rows = []
nrc8_missed_rows = []

for row in df_gold.itertuples():
    w = str(row.word).lower().strip()
    lemma = str(row.canonical_lemma).lower().strip()
    
    nrc_tags = nrc_dict.get(w, []) or nrc_dict.get(lemma, [])
    nrc8_matched = [t for t in nrc_tags if t in NRC8]
    nrc_polarities = [t for t in nrc_tags if t in ('positive', 'negative')]
    
    has_nrc8 = len(nrc8_matched) > 0
    
    item = {
        'word': w,
        'canonical_lemma': lemma,
        'chinese_translation': row.chinese_translation,
        'emotion_category': row.emotion_category,
        'affect_type': row.affect_type,
        'frequency_21215': row.frequency_21215,
        'review_count_21215': row.review_count_21215,
        'nrc8_emotions': ', '.join(nrc8_matched) if nrc8_matched else 'None (Not in NRC 8)',
        'nrc_polarities': ', '.join(nrc_polarities) if nrc_polarities else 'None',
        'nrc_all_tags': ', '.join(nrc_tags) if nrc_tags else 'Unmapped in NRC'
    }
    
    if has_nrc8:
        nrc8_included_rows.append(item)
    else:
        nrc8_missed_rows.append(item)

df_inc = pd.DataFrame(nrc8_included_rows).sort_values(['frequency_21215', 'word'], ascending=[False, True]).reset_index(drop=True)
df_miss = pd.DataFrame(nrc8_missed_rows).sort_values(['frequency_21215', 'word'], ascending=[False, True]).reset_index(drop=True)

# Export CSV and XLSX to data/analyze/
df_inc.to_excel(analyze_dir / "nrc8_words_included.xlsx", index=False)
df_inc.to_csv(analyze_dir / "nrc8_words_included.csv", index=False, encoding='utf-8-sig')

df_miss.to_excel(analyze_dir / "nrc8_words_missed.xlsx", index=False)
df_miss.to_csv(analyze_dir / "nrc8_words_missed.csv", index=False, encoding='utf-8-sig')

print(f"Master Gold Codebook Total: {len(df_gold)}")
print(f"Words IN NRC 8 Basic Emotion Categories: {len(df_inc)} (Saved to data/analyze/nrc8_words_included.xlsx)")
print(f"Words NOT IN NRC 8 Basic Emotion Categories: {len(df_miss)} (Saved to data/analyze/nrc8_words_missed.xlsx)")
