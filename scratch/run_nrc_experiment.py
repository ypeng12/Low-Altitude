#!/usr/bin/env python3
"""Map Master Gold Emotion Lexicon (632 words) against NRC Emotion Lexicon (nrclex)."""

import pandas as pd
from pathlib import Path
from nrclex import NRCLex

root_dir = Path("data/derived_outputs")
gold_path = Path("data/cleaned_datasets/gold_emotion_lexicon_master.csv")

df_gold = pd.read_csv(gold_path)
nrc_dict = NRCLex().__lexicon__

mapped_rows = []

nrc_cat_counts = {
    'joy': 0, 'trust': 0, 'fear': 0, 'surprise': 0,
    'anticipation': 0, 'sadness': 0, 'anger': 0, 'disgust': 0,
    'positive': 0, 'negative': 0
}

missed_count = 0
hit_count = 0

for row in df_gold.itertuples():
    w = str(row.word).lower().strip()
    lemma = str(row.canonical_lemma).lower().strip()
    
    # Lookup word or lemma in NRC lexicon
    nrc_emotions = nrc_dict.get(w, [])
    if not nrc_emotions and lemma != w:
        nrc_emotions = nrc_dict.get(lemma, [])
        
    has_nrc = len(nrc_emotions) > 0
    if has_nrc:
        hit_count += 1
        for e in nrc_emotions:
            if e in nrc_cat_counts:
                nrc_cat_counts[e] += 1
    else:
        missed_count += 1

    # Format NRC emotion tags string
    nrc_8_emotions = [e for e in nrc_emotions if e not in ('positive', 'negative')]
    nrc_polarities = [e for e in nrc_emotions if e in ('positive', 'negative')]
    
    mapped_rows.append({
        'word': w,
        'canonical_lemma': lemma,
        'chinese_translation': row.chinese_translation,
        'our_emotion_category': row.emotion_category,
        'affect_type': row.affect_type,
        'frequency_21215': row.frequency_21215,
        'in_nrc_lexicon': has_nrc,
        'nrc_8_emotions': ', '.join(nrc_8_emotions) if nrc_8_emotions else 'Unmapped in NRC',
        'nrc_polarities': ', '.join(nrc_polarities) if nrc_polarities else 'Unmapped in NRC',
        'nrc_raw_list': str(nrc_emotions)
    })

df_mapped = pd.DataFrame(mapped_rows)

# Save mapped outputs
df_mapped.to_excel(root_dir / "gold_emotion_nrc_mapped.xlsx", index=False)
df_mapped.to_csv(root_dir / "gold_emotion_nrc_mapped.csv", index=False, encoding='utf-8-sig')

# Display summary report
print("=== NRC Emotion Lexicon Mapping Experiment Results ===")
print(f"Total Master Gold Emotion Terms: {len(df_gold)}")
print(f"Terms Covered by NRC Lexicon: {hit_count} ({hit_count/len(df_gold)*100:.2f}%)")
print(f"Terms Missed by NRC (Domain-Specific): {missed_count} ({missed_count/len(df_gold)*100:.2f}%)")
print("\n--- NRC 8 Basic Emotions Distribution across Gold Lexicon ---")
for cat in ['joy', 'trust', 'fear', 'surprise', 'anticipation', 'sadness', 'anger', 'disgust', 'positive', 'negative']:
    cnt = nrc_cat_counts[cat]
    print(f"  - {cat.upper():12s}: {cnt:4d} words ({cnt/len(df_gold)*100:.2f}%)")

print("\nSample Missed Domain-Specific High-Frequency Emotion Words (NRC Gaps):")
print(df_mapped[~df_mapped['in_nrc_lexicon']][['word', 'chinese_translation', 'our_emotion_category', 'frequency_21215']].head(20).to_string())
