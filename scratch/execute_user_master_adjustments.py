#!/usr/bin/env python3
"""Execute user explicit adjustments on Master Gold Emotion Codebook and Removed Log."""

import pandas as pd
import re
from pathlib import Path

root_dir = Path("data/derived_outputs")
df_eng = pd.read_csv("data/cleaned_datasets/tripadvisor_level3_english_v2.csv")

# 1. Words explicitly specified by user to PURGE from Gold Lexicon
purge_words = {
    'enjoyed', 'enjoy', 'enjoying', 'enjoys',
    'safe', 'safety', 'secure', 'security',
    'splurge',
    'hesitation',
    'stuck',
    'wondering',
    'shame',
    'privilege',
    'rewarded',
    'suffer',
    'seasick', 'dizziness', 'nauseated',
    'shaking', 'screaming'
}

# 2. Category 2 Words explicitly specified by user to ADD to Gold Lexicon
cat2_additions = [
    ('memorable', 'memorable', 'Memorability / Joy', '令人终生难忘的', 'E1_State (Direct Internal Affective State)'),
    ('lucky', 'lucky', 'Good Fortune / Joy', '感到幸运的', 'E1_State (Direct Internal Affective State)'),
    ('lucked', 'lucky', 'Good Fortune / Joy', '幸运地 (动词变体)', 'E1_State (Direct Internal Affective State)'),
    ('entertained', 'entertained', 'Joy / Amusement', '感到深受愉悦娱乐的', 'E1_State (Direct Internal Affective State)'),
    ('considerate', 'considerate', 'Kindness / Reassurance', '体贴周到的', 'E2_Appraisal (Stimulus/Service Attribute)'),
    ('caring', 'caring', 'Warmth / Kindness', '体贴入微关怀的', 'E2_Appraisal (Stimulus/Service Attribute)'),
    ('gladly', 'gladly', 'Joy / Eagerness', '乐意地 / 高兴地', 'E1_State (Direct Internal Affective State)'),
    ('warmth', 'warmth', 'Warmth / Comfort', '温暖安心感', 'E1_State (Direct Internal Affective State)'),
    ('admire', 'admire', 'Admiration', '钦佩赞赏', 'E1_State (Direct Internal Affective State)')
]

# Scan N=21,215 corpus for exact term frequencies and context
word_freq = {}
word_rev = {}
word_ctx = {}

print("Scanning N=21,215 full corpus for term metrics...")
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

# Identify rows in df_gold that need to be purged
gold_dict = {str(r.word).lower().strip(): r for r in df_gold.itertuples()}

purged_from_gold = []
for w in list(gold_dict.keys()):
    if w in purge_words:
        s = gold_dict.pop(w)
        purged_from_gold.append({
            'word': w,
            'chinese_translation': f"移出情绪词典（用户指明为概念/动作/体感/行为状态: {w}）",
            'stage_origin': 'User Adjustment Purge',
            'frequency_21215': word_freq.get(w, getattr(s, 'frequency_21215', 1)),
            'review_count_21215': word_rev.get(w, getattr(s, 'review_count_21215', 1)),
            'example_context': word_ctx.get(w, getattr(s, 'example_context', ''))
        })

# Add Category 2 additions to gold_dict
for word, lemma, category, trans, aff in cat2_additions:
    gold_dict[word] = pd.Series({
        'word': word,
        'canonical_lemma': lemma,
        'chinese_translation': trans,
        'emotion_category': category,
        'affect_type': aff,
        'stage_origin': 'User Category 2 Calibration',
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
        'example_context': word_ctx.get(w, getattr(s, 'example_context', ''))
    })

df_gold_updated = pd.DataFrame(gold_rows).sort_values(['frequency_21215', 'word'], ascending=[False, True]).reset_index(drop=True)

# Remove cat2_additions from df_rem and append purged_from_gold to df_rem
additions_set = {t[0] for t in cat2_additions}
df_rem_filtered = df_rem[~df_rem['word'].str.lower().isin(additions_set)].reset_index(drop=True)

if purged_from_gold:
    df_rem_updated = pd.concat([df_rem_filtered, pd.DataFrame(purged_from_gold)], ignore_index=True)
else:
    df_rem_updated = df_rem_filtered

df_rem_updated = df_rem_updated.sort_values('frequency_21215', ascending=False).reset_index(drop=True)

cols_g = ['word', 'canonical_lemma', 'chinese_translation', 'emotion_category', 'affect_type', 'stage_origin', 'frequency_21215', 'review_count_21215', 'example_context']
cols_r = ['word', 'chinese_translation', 'stage_origin', 'frequency_21215', 'review_count_21215', 'example_context']

df_gold_updated[cols_g].to_excel(root_dir / 'gold_emotion_lexicon_codebook.xlsx', index=False)
df_gold_updated[cols_g].to_csv(root_dir / 'gold_emotion_lexicon_codebook.csv', index=False, encoding='utf-8-sig')

df_rem_updated[cols_r].to_excel(root_dir / 'removed_non_emotion_words_log.xlsx', index=False)
df_rem_updated[cols_r].to_csv(root_dir / 'removed_non_emotion_words_log.csv', index=False, encoding='utf-8-sig')

print(f"Successfully applied all user adjustments!")
print(f"Purged from Gold Lexicon: {len(purged_from_gold)} terms")
print(f"Added to Gold Lexicon (Category 2): {len(cat2_additions)} terms")
print(f"Updated Master Gold Codebook Total: {len(df_gold_updated)}")
print(f"Updated Master Removed Log Total: {len(df_rem_updated)}")
