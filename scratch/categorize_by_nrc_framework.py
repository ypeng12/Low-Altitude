#!/usr/bin/env python3
"""Group Master Gold Emotion Lexicon (632 words) cleanly by NRC Emotion Framework."""

import pandas as pd
from pathlib import Path
from nrclex import NRCLex

root_dir = Path("data/derived_outputs")
gold_path = Path("data/cleaned_datasets/gold_emotion_lexicon_master.csv")

df_gold = pd.read_csv(gold_path)
nrc_dict = NRCLex().__lexicon__

# Primary NRC Emotion Assignment Priority
def assign_primary_nrc_category(word, lemma, our_cat):
    w_lower = str(word).lower().strip()
    l_lower = str(lemma).lower().strip()
    
    nrc_tags = nrc_dict.get(w_lower, [])
    if not nrc_tags and l_lower != w_lower:
        nrc_tags = nrc_dict.get(l_lower, [])
        
    nrc_8 = [t for t in nrc_tags if t not in ('positive', 'negative')]
    
    if nrc_8:
        # Priority mapping if word has multiple NRC tags
        priority_order = ['joy', 'fear', 'trust', 'surprise', 'anticipation', 'sadness', 'anger', 'disgust']
        for p in priority_order:
            if p in nrc_8:
                return f"NRC_{p.upper()}", ', '.join(nrc_tags)
        return f"NRC_{nrc_8[0].upper()}", ', '.join(nrc_tags)
    elif nrc_tags:
        # Positive / Negative only
        pol = nrc_tags[0].upper()
        return f"NRC_POLARITY_{pol}", ', '.join(nrc_tags)
    else:
        # NRC Missed - Domain Specific Awe / Appraisal
        return "NRC_MISSED (Low-Altitude Domain-Specific Awe / Appraisal)", "Unmapped in NRC"

categorized_rows = []

for row in df_gold.itertuples():
    w = str(row.word).lower().strip()
    lemma = str(row.canonical_lemma).lower().strip()
    
    nrc_primary_cat, nrc_all_tags = assign_primary_nrc_category(w, lemma, row.emotion_category)
    
    categorized_rows.append({
        'word': w,
        'canonical_lemma': lemma,
        'chinese_translation': row.chinese_translation,
        'nrc_primary_category': nrc_primary_cat,
        'nrc_all_raw_tags': nrc_all_tags,
        'our_original_category': row.emotion_category,
        'affect_type': row.affect_type,
        'frequency_21215': row.frequency_21215,
        'review_count_21215': row.review_count_21215,
        'example_context': row.example_context
    })

df_nrc_cat = pd.DataFrame(categorized_rows).sort_values(['nrc_primary_category', 'frequency_21215'], ascending=[True, False]).reset_index(drop=True)

# Export to Excel and CSV
df_nrc_cat.to_excel(root_dir / "gold_emotion_categorized_by_nrc.xlsx", index=False)
df_nrc_cat.to_csv(root_dir / "gold_emotion_categorized_by_nrc.csv", index=False, encoding='utf-8-sig')

# Print summary by category
print("=== Master Gold Lexicon (632 words) NRC Classification Summary ===")
cat_counts = df_nrc_cat['nrc_primary_category'].value_counts()
for cat, cnt in cat_counts.items():
    print(f"  - {cat:55s}: {cnt:4d} words ({cnt/len(df_gold)*100:.2f}%)")
