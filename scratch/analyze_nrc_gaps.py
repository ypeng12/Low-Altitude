#!/usr/bin/env python3
"""Rigorously analyze linguistic & domain reasons why 272 words are missed by NRC Lexicon."""

import pandas as pd
from pathlib import Path
import re
from nrclex import NRCLex

gold_path = Path("data/analyze/gold_emotion_master.csv")
df_gold = pd.read_csv(gold_path)

nrc_dict = NRCLex().__lexicon__
NRC8 = {"anger", "anticipation", "disgust", "fear", "joy", "sadness", "surprise", "trust"}

missed_words = []

for row in df_gold.itertuples():
    w = str(row.word).lower().strip()
    lemma = str(row.canonical_lemma).lower().strip()
    
    nrc_tags = nrc_dict.get(w, []) or nrc_dict.get(lemma, [])
    has_any = len(nrc_tags) > 0
    
    if not has_any:
        missed_words.append(row)

df_missed = pd.DataFrame(missed_words)

# Categorize reasons
cat_counts = {
    "1_Adverbs_and_Superlatives (-ly, -est, -er)": 0,
    "2_Inflected_Verbs_and_Participles (-ed, -ing)": 0,
    "3_High_Arousal_Tourism_Awe_and_Scenic": 0,
    "4_Modern_Colloquial_Superlatives": 0,
    "5_Flight_Risk_and_Physiological_Sensations": 0,
    "6_Base_Words_Omitted_in_NRC_2012": 0
}

categorized_misses = []

for row in df_missed.itertuples():
    w = row.word
    lemma = row.canonical_lemma
    freq = row.frequency_21215
    trans = row.chinese_translation
    
    reason = "6_Base_Words_Omitted_in_NRC_2012"
    
    if w.endswith("ly") or w.endswith("est") or w.endswith("er"):
        reason = "1_Adverbs_and_Superlatives (-ly, -est, -er)"
    elif w.endswith("ed") or w.endswith("ing"):
        reason = "2_Inflected_Verbs_and_Participles (-ed, -ing)"
    elif any(k in w for k in ["breath", "scenic", "sublime", "stunn", "panoram", "picturesque", "surreal", "majest", "spellbind", "mesmer"]):
        reason = "3_High_Arousal_Tourism_Awe_and_Scenic"
    elif any(k in w for k in ["awesome", "fantastic", "incredible", "fabulous", "phenomen", "epic", "notch", "stellar", "unbeat"]):
        reason = "4_Modern_Colloquial_Superlatives"
    elif any(k in w for k in ["claustro", "jitter", "dizz", "nause", "sick", "phobia", "unnerv", "shake", "bumpy", "turblu", "choppy"]):
        reason = "5_Flight_Risk_and_Physiological_Sensations"
        
    cat_counts[reason] += 1
    categorized_misses.append({
        'word': w,
        'canonical_lemma': lemma,
        'chinese_translation': trans,
        'frequency_21215': freq,
        'reason_category': reason
    })

df_cat_missed = pd.DataFrame(categorized_misses).sort_values(['reason_category', 'frequency_21215'], ascending=[True, False])

print("=== 🔬 WHY ARE 272 WORDS MISSED BY NRC? LINGUISTIC & DOMAIN ANALYSIS ===")
print(f"Total Missed Words: {len(df_missed)}\n")

for reason, cnt in cat_counts.items():
    pct = (cnt / len(df_missed)) * 100
    print(f"  - {reason:50s}: {cnt:3d} words ({pct:5.2f}%)")

print("\nSample Missed Words per Category:")
for reason in cat_counts.keys():
    sub = df_cat_missed[df_cat_missed['reason_category'] == reason]
    sample = ', '.join(sub['word'].head(8).tolist())
    print(f"\n[{reason}] (Count: {len(sub)})\n  Samples: {sample}")
