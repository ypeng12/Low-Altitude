#!/usr/bin/env python3
"""Audit exact coverage gap of VADER Lexicon vs. NRC Lexicon across Master Gold Emotion Codebook (632 words)."""

import pandas as pd
from pathlib import Path
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nrclex import NRCLex

gold_path = Path("data/analyze/gold_emotion_master.csv")
df_gold = pd.read_csv(gold_path)

vader_dict = SentimentIntensityAnalyzer().lexicon
nrc_dict = NRCLex().__lexicon__

vader_hits = []
vader_misses = []

nrc_hits = []
nrc_misses = []

both_misses = []

for row in df_gold.itertuples():
    w = str(row.word).lower().strip()
    lemma = str(row.canonical_lemma).lower().strip()
    
    in_vader = (w in vader_dict) or (lemma in vader_dict)
    nrc_tags = nrc_dict.get(w, []) or nrc_dict.get(lemma, [])
    in_nrc = len(nrc_tags) > 0
    
    if in_vader:
        vader_hits.append(w)
    else:
        vader_misses.append(w)
        
    if in_nrc:
        nrc_hits.append(w)
    else:
        nrc_misses.append(w)
        
    if (not in_vader) and (not in_nrc):
        both_misses.append((w, row.chinese_translation, row.frequency_21215))

print("=== 📊 Master Gold Emotion Lexicon (632 words) Lexicon Coverage Audit ===")
print(f"Total Master Gold Emotion Terms: {len(df_gold)}")

print(f"\n1. NRC Lexicon Coverage:")
print(f"   - Covered by NRC: {len(nrc_hits)} words ({len(nrc_hits)/len(df_gold)*100:.2f}%)")
print(f"   - MISSED by NRC:  {len(nrc_misses)} words ({len(nrc_misses)/len(df_gold)*100:.2f}%)")

print(f"\n2. VADER Lexicon Coverage:")
print(f"   - Covered by VADER: {len(vader_hits)} words ({len(vader_hits)/len(df_gold)*100:.2f}%)")
print(f"   - MISSED by VADER:  {len(vader_misses)} words ({len(vader_misses)/len(df_gold)*100:.2f}%)")

print(f"\n3. BOTH VADER and NRC MISSED (Dual Lexicon Blind Spot):")
print(f"   - MISSED by BOTH VADER & NRC: {len(both_misses)} words ({len(both_misses)/len(df_gold)*100:.2f}%)")

# Export breakdown to data/analyze/
df_audit = pd.DataFrame(df_gold)
df_audit['in_nrc'] = df_audit['word'].apply(lambda w: (w in nrc_dict) or (str(w) in nrc_dict))
df_audit['in_vader'] = df_audit['word'].apply(lambda w: (w in vader_dict) or (str(w) in vader_dict))

df_audit.to_excel("data/analyze/lexicon_coverage_audit_632.xlsx", index=False)
df_audit.to_csv("data/analyze/lexicon_coverage_audit_632.csv", index=False, encoding='utf-8-sig')

print("\nSample Top Frequency Words MISSED by BOTH VADER and NRC:")
df_both = pd.DataFrame(both_misses, columns=['word', 'chinese_translation', 'frequency_21215']).sort_values('frequency_21215', ascending=False)
print(df_both.head(20).to_string())
