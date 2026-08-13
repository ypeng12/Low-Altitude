#!/usr/bin/env python3
"""Purge 16 procedural, service competence, price, and weather terms from Master Gold Codebook."""

import pandas as pd
from pathlib import Path

root_dir = Path("data/derived_outputs")

purge_16 = {
    'knowledgeable', 'informative', 'educational',
    'easy', 'courteous', 'patient', 'flexible', 'polite', 'accessible', 'attentive', 'thorough', 'prompt',
    'pricey', 'priceless', 'cloudless', 'sentiment'
}

df_gold = pd.read_csv(root_dir / "gold_emotion_lexicon_codebook.csv")
df_rem = pd.read_csv(root_dir / "removed_non_emotion_words_log.csv")

purged_rows = []
for row in df_gold.itertuples():
    w = str(row.word).lower().strip()
    if w in purge_16:
        purged_rows.append({
            'word': w,
            'chinese_translation': f"移出情绪代码本（用户指明为服务态度/技能/价格/天气属性词: {w}）",
            'stage_origin': 'User Final Procedural Purge',
            'frequency_21215': row.frequency_21215,
            'review_count_21215': row.review_count_21215,
            'example_context': row.example_context
        })

df_gold_updated = df_gold[~df_gold['word'].str.lower().isin(purge_16)].sort_values(['frequency_21215', 'word'], ascending=[False, True]).reset_index(drop=True)
df_rem_updated = pd.concat([df_rem, pd.DataFrame(purged_rows)], ignore_index=True).sort_values('frequency_21215', ascending=False).reset_index(drop=True)

cols_g = ['word', 'canonical_lemma', 'chinese_translation', 'emotion_category', 'affect_type', 'stage_origin', 'frequency_21215', 'review_count_21215', 'example_context']
cols_r = ['word', 'chinese_translation', 'stage_origin', 'frequency_21215', 'review_count_21215', 'example_context']

df_gold_updated[cols_g].to_excel(root_dir / 'gold_emotion_lexicon_codebook.xlsx', index=False)
df_gold_updated[cols_g].to_csv(root_dir / 'gold_emotion_lexicon_codebook.csv', index=False, encoding='utf-8-sig')

df_rem_updated[cols_r].to_excel(root_dir / 'removed_non_emotion_words_log.xlsx', index=False)
df_rem_updated[cols_r].to_csv(root_dir / 'removed_non_emotion_words_log.csv', index=False, encoding='utf-8-sig')

print(f"Successfully purged 16 procedural/service/attribute terms from Master Gold Codebook!")
print(f"Master Gold Codebook Total: {len(df_gold_updated)}")
print(f"Master Removed Log Total: {len(df_rem_updated)}")
