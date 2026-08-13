#!/usr/bin/env python3
"""Combine nrc_words_included and nrc_words_missed into one unified table gold_emotion_nrc_combined.xlsx/csv."""

import pandas as pd
from pathlib import Path
from nrclex import NRCLex

analyze_dir = Path("data/analyze")

inc_csv = analyze_dir / "nrc_words_included.csv"
miss_csv = analyze_dir / "nrc_words_missed.csv"
master_csv = analyze_dir / "gold_emotion_master.csv"

df_master = pd.read_csv(master_csv)
nrc_dict = NRCLex().__lexicon__

combined_rows = []

for row in df_master.itertuples():
    w = str(row.word).lower().strip()
    lemma = str(row.canonical_lemma).lower().strip()
    
    nrc_tags = nrc_dict.get(w, []) or nrc_dict.get(lemma, [])
    has_nrc = len(nrc_tags) > 0
    
    nrc_8 = [t for t in nrc_tags if t not in ('positive', 'negative')]
    nrc_pol = [t for t in nrc_tags if t in ('positive', 'negative')]
    
    combined_rows.append({
        'word': w,
        'canonical_lemma': lemma,
        'chinese_translation': row.chinese_translation,
        'emotion_category': row.emotion_category,
        'affect_type': row.affect_type,
        'frequency_21215': row.frequency_21215,
        'review_count_21215': row.review_count_21215,
        'nrc_status': 'Included in NRC' if has_nrc else 'Missed by NRC',
        'in_nrc_lexicon': has_nrc,
        'nrc_8_emotions': ', '.join(nrc_8) if nrc_8 else 'None',
        'nrc_polarities': ', '.join(nrc_pol) if nrc_pol else 'None',
        'nrc_all_tags': ', '.join(nrc_tags) if nrc_tags else 'Unmapped in NRC',
        'example_context': row.example_context
    })

df_combined = pd.DataFrame(combined_rows).sort_values('frequency_21215', ascending=False).reset_index(drop=True)

# Save combined outputs
df_combined.to_excel(analyze_dir / "gold_emotion_nrc_combined.xlsx", index=False)
df_combined.to_csv(analyze_dir / "gold_emotion_nrc_combined.csv", index=False, encoding='utf-8-sig')

print(f"Successfully combined NRC included (358) and missed (272) into single table:")
print(f"  - Total rows: {len(df_combined)}")
print(f"  - File: {analyze_dir / 'gold_emotion_nrc_combined.xlsx'}")
