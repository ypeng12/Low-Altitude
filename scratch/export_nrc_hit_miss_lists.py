#!/usr/bin/env python3
"""Export clean breakdown files for words IN NRC vs words NOT IN NRC from Master Gold Lexicon (632 words)."""

import pandas as pd
from pathlib import Path
from nrclex import NRCLex

root_dir = Path("data/derived_outputs")
gold_path = Path("data/cleaned_datasets/gold_emotion_lexicon_master.csv")

df_gold = pd.read_csv(gold_path)
nrc_dict = NRCLex().__lexicon__

hits = []
misses = []

for row in df_gold.itertuples():
    w = str(row.word).lower().strip()
    lemma = str(row.canonical_lemma).lower().strip()
    
    # Exact lookup in NRC
    nrc_emotions = nrc_dict.get(w, [])
    has_nrc = len(nrc_emotions) > 0
    
    item = {
        'word': w,
        'canonical_lemma': lemma,
        'chinese_translation': row.chinese_translation,
        'emotion_category': row.emotion_category,
        'affect_type': row.affect_type,
        'frequency_21215': row.frequency_21215,
        'review_count_21215': row.review_count_21215,
        'nrc_tags': ', '.join(nrc_emotions) if has_nrc else 'Unmapped'
    }
    
    if has_nrc:
        hits.append(item)
    else:
        misses.append(item)

df_hits = pd.DataFrame(hits).sort_values(['frequency_21215', 'word'], ascending=[False, True]).reset_index(drop=True)
df_misses = pd.DataFrame(misses).sort_values(['frequency_21215', 'word'], ascending=[False, True]).reset_index(drop=True)

# Export to Excel and CSV
df_hits.to_excel(root_dir / "nrc_words_included.xlsx", index=False)
df_hits.to_csv(root_dir / "nrc_words_included.csv", index=False, encoding='utf-8-sig')

df_misses.to_excel(root_dir / "nrc_words_missed.xlsx", index=False)
df_misses.to_csv(root_dir / "nrc_words_missed.csv", index=False, encoding='utf-8-sig')

print(f"Master Gold Codebook Total Terms: {len(df_gold)}")
print(f"Words IN NRC Lexicon: {len(df_hits)} (Saved to data/derived_outputs/nrc_words_included.xlsx)")
print(f"Words NOT IN NRC Lexicon: {len(df_misses)} (Saved to data/derived_outputs/nrc_words_missed.xlsx)")
