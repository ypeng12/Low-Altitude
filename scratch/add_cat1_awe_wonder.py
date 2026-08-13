#!/usr/bin/env python3
"""Add Category 1 (High Arousal Awe & Aesthetic Wonder) terms to Master Gold Emotion Codebook."""

import pandas as pd
import re
from pathlib import Path

root_dir = Path("data/derived_outputs")
df_eng = pd.read_csv("data/cleaned_datasets/tripadvisor_level3_english_v2.csv")

cat1_additions = [
    ('impressed', 'impressed', 'Admiration / Impression', '感到深深被折服/留下深刻印象', 'E1_State (Direct Internal Affective State)'),
    ('wonder', 'wonder', 'Amazement / Wonder', '惊奇 / 赞叹', 'E2_Appraisal (Stimulus/Service Attribute)'),
    ('wonders', 'wonder', 'Amazement / Wonder', '惊奇 / 奇观', 'E2_Appraisal (Stimulus/Service Attribute)'),
    ('magnificence', 'magnificence', 'Awe / Grandeur', '壮丽震撼感', 'E2_Appraisal (Stimulus/Service Attribute)'),
    ('surprises', 'surprise', 'Surprise', '惊喜 / 意料之外', 'E2_Appraisal (Stimulus/Service Attribute)'),
    ('marvel', 'marvel', 'Amazement / Awe', '惊叹 / 奇迹', 'E2_Appraisal (Stimulus/Service Attribute)'),
    ('wondered', 'wonder', 'Amazement / Wonder', '感到惊奇惊叹 (动词变体)', 'E1_State (Direct Internal Affective State)'),
    ('marvellous', 'marvellous', 'Amazement / Awe', '令人叹为观止的', 'E2_Appraisal (Stimulus/Service Attribute)'),
    ('wonderfull', 'wonderful', 'Joy / Wonder', '令人惊叹绝妙的 (错别字变体)', 'E2_Appraisal (Stimulus/Service Attribute)')
]

# Scan N=21,215 corpus for exact term frequencies and context
word_freq = {}
word_rev = {}
word_ctx = {}

print("Scanning N=21,215 full corpus for Cat 1 term metrics...")
for row in df_eng.itertuples():
    text = str(row.review_text)
    rid = str(row.review_id)
    tokens = re.findall(r'\b[a-zA-Z]{2,}\b', text.lower())
    seen = set()
    for tok in tokens:
        word_freq[tok] = word_freq.get(tok, 0) + 1
        if tok not in seen:
            seen.add(tok)
            word_rev[tok] = word_rev.get(tok, 0) + 1
            if tok not in word_ctx:
                word_ctx[tok] = f"{rid} :: {text[:180]}..."

df_gold = pd.read_csv(root_dir / "gold_emotion_lexicon_codebook.csv")
df_rem = pd.read_csv(root_dir / "removed_non_emotion_words_log.csv")

gold_dict = {str(r.word).lower().strip(): r for r in df_gold.itertuples()}

for word, lemma, category, trans, aff in cat1_additions:
    gold_dict[word] = pd.Series({
        'word': word,
        'canonical_lemma': lemma,
        'chinese_translation': trans,
        'emotion_category': category,
        'affect_type': aff,
        'stage_origin': 'User Category 1 Calibration',
        'frequency_21215': word_freq.get(word, 1),
        'review_count_21215': word_rev.get(word, 1),
        'example_context': word_ctx.get(word, f"Review context: {word}")
    })

gold_rows = []
for w, s in gold_dict.items():
    gold_rows.append({
        'word': w,
        'canonical_lemma': getattr(s, 'canonical_lemma', w),
        'chinese_translation': getattr(s, 'chinese_translation', ''),
        'emotion_category': getattr(s, 'emotion_category', 'General Emotion / Appraisal'),
        'affect_type': getattr(s, 'affect_type', 'E1_State (Direct Internal Affective State)'),
        'stage_origin': getattr(s, 'stage_origin', 'Stage 1/2'),
        'frequency_21215': word_freq.get(w, getattr(s, 'frequency_21215', 1)),
        'review_count_21215': word_rev.get(w, getattr(s, 'review_count_21215', 1)),
        'example_context': getattr(s, 'example_context', '')
    })

df_gold_updated = pd.DataFrame(gold_rows).sort_values(['frequency_21215', 'word'], ascending=[False, True]).reset_index(drop=True)

# Remove Category 1 additions from df_rem
additions_set = {t[0] for t in cat1_additions}
df_rem_updated = df_rem[~df_rem['word'].str.lower().isin(additions_set)].sort_values('frequency_21215', ascending=False).reset_index(drop=True)

cols_g = ['word', 'canonical_lemma', 'chinese_translation', 'emotion_category', 'affect_type', 'stage_origin', 'frequency_21215', 'review_count_21215', 'example_context']
cols_r = ['word', 'chinese_translation', 'stage_origin', 'frequency_21215', 'review_count_21215', 'example_context']

df_gold_updated[cols_g].to_excel(root_dir / 'gold_emotion_lexicon_codebook.xlsx', index=False)
df_gold_updated[cols_g].to_csv(root_dir / 'gold_emotion_lexicon_codebook.csv', index=False, encoding='utf-8-sig')

df_rem_updated[cols_r].to_excel(root_dir / 'removed_non_emotion_words_log.xlsx', index=False)
df_rem_updated[cols_r].to_csv(root_dir / 'removed_non_emotion_words_log.csv', index=False, encoding='utf-8-sig')

print(f"Successfully added Category 1 (Awe / Amazement / Wonder) to Master Gold Lexicon!")
print(f"Added terms: {len(cat1_additions)}")
print(f"Updated Master Gold Codebook Total: {len(df_gold_updated)}")
print(f"Updated Master Removed Log Total: {len(df_rem_updated)}")
