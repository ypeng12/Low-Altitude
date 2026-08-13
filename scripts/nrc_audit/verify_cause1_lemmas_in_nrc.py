#!/usr/bin/env python3
"""Check how many of the 136 Cause 1 morphological words have their root lemmas in NRC."""

import pandas as pd
from pathlib import Path
import nltk
from nltk.stem import WordNetLemmatizer
from nrclex import NRCLex

gold_path = Path("data/analyze/gold_emotion_master.csv")
df_gold = pd.read_csv(gold_path)
nrc_dict = NRCLex().__lexicon__

lemmatizer = WordNetLemmatizer()

cause1_words = []

for row in df_gold.itertuples():
    w = str(row.word).lower().strip()
    lemma = str(row.canonical_lemma).lower().strip()
    
    nrc_tags = nrc_dict.get(w, [])
    has_any_raw = len(nrc_tags) > 0
    
    if not has_any_raw:
        if w.endswith("ing") or w.endswith("ed") or w.endswith("ly") or w.endswith("est") or w.endswith("er"):
            cause1_words.append(row)

df_c1 = pd.DataFrame(cause1_words)

# Manual / NLTK Root dictionary mapping for these 136 words
root_in_nrc = []
root_not_in_nrc = []

for row in df_c1.itertuples():
    w = row.word
    lemma = row.canonical_lemma
    freq = row.frequency_21215
    trans = row.chinese_translation
    
    # Try lemma, and also common manual roots (e.g. amazing -> amaze, loved -> love, best -> good/best, etc.)
    possible_roots = {lemma, w}
    if w.endswith("ing"):
        possible_roots.add(w[:-3])
        possible_roots.add(w[:-3] + "e")
    elif w.endswith("ed"):
        possible_roots.add(w[:-2])
        possible_roots.add(w[:-1])
    elif w.endswith("ly"):
        possible_roots.add(w[:-2])
        if w.endswith("ily"):
            possible_roots.add(w[:-3] + "y")
    elif w.endswith("est"):
        possible_roots.add(w[:-3])
        possible_roots.add(w[:-3] + "e")
        if w.endswith("iest"):
            possible_roots.add(w[:-4] + "y")
    elif w.endswith("er"):
        possible_roots.add(w[:-2])
        possible_roots.add(w[:-2] + "e")
        if w.endswith("ier"):
            possible_roots.add(w[:-3] + "y")
            
    # Also manual overrides
    if w in ["best", "better"]: possible_roots.add("good")
    if w in ["smoother", "smoothest"]: possible_roots.add("smooth")
    if w in ["cheaper"]: possible_roots.add("cheap")
    if w in ["safer", "safely"]: possible_roots.add("safe")
    
    found_root = None
    found_tags = []
    for r in possible_roots:
        tags = nrc_dict.get(r, [])
        if len(tags) > 0:
            found_root = r
            found_tags = tags
            break
            
    if found_root:
        root_in_nrc.append({
            'word': w,
            'canonical_lemma': lemma,
            'root_found_in_nrc': found_root,
            'nrc_tags': ', '.join(found_tags),
            'freq': freq,
            'chinese': trans
        })
    else:
        root_not_in_nrc.append({
            'word': w,
            'canonical_lemma': lemma,
            'freq': freq,
            'chinese': trans
        })

df_found = pd.DataFrame(root_in_nrc).sort_values('freq', ascending=False)
df_not_found = pd.DataFrame(root_not_in_nrc).sort_values('freq', ascending=False)

print(f"Total Cause 1 Words: {len(df_c1)}")
print(f"1. Root ACTUALLY FOUND in NRC (词根确实在 NRC 里): {len(df_found)} 个词 ({len(df_found)/len(df_c1)*100:.2f}%)")
print(f"2. Root NOT in NRC (词根也不在 NRC 里): {len(df_not_found)} 个词 ({len(df_not_found)/len(df_c1)*100:.2f}%)\n")

print("--- Top 15 Words whose roots ARE in NRC ---")
print(df_found.head(15).to_string(index=False))

print("\n--- Top 15 Words whose roots ARE ALSO NOT in NRC ---")
print(df_not_found.head(15).to_string(index=False))
