#!/usr/bin/env python3
"""Execute exact audit on Cause 1 words: Check base roots in NRC vs not in NRC."""

import pandas as pd
from pathlib import Path
from nrclex import NRCLex

gold_path = Path("data/analyze/gold_emotion_master.csv")
df_gold = pd.read_csv(gold_path)
nrc_dict = NRCLex().__lexicon__

c3_awe = {"breathtaking", "breathtakingly", "stunning", "stunningly", "sublime", "scenic", "surreal", "majestic", "panoramic", "spellbinding", "mesmerizing", "awe", "awed"}
c4_risk = {"claustrophobia", "claustrophobic", "jitters", "airsick", "phobia", "unnerving", "unnerved", "shaky", "dizzy", "dizziness", "nauseated", "nauseous", "seasick"}
c2_colloquial = {"great", "awesome", "fantastic", "incredible", "incredibly", "nice", "fabulous", "phenomenal", "unbeatable", "top-notch", "topnotch", "stellar", "prime", "primo", "epic", "mind-blowing"}

cause1_words = []

for row in df_gold.itertuples():
    w = str(row.word).lower().strip()
    lemma = str(row.canonical_lemma).lower().strip()
    
    nrc_tags = nrc_dict.get(w, []) or nrc_dict.get(lemma, [])
    has_any = len(nrc_tags) > 0
    
    if not has_any:
        if w not in c3_awe and w not in c4_risk and w not in c2_colloquial:
            if w.endswith("ing") or w.endswith("ed") or w.endswith("ly") or w.endswith("est") or w.endswith("er"):
                cause1_words.append(row)

df_c1 = pd.DataFrame(cause1_words)

root_in_nrc = []
root_not_in_nrc = []

for row in df_c1.itertuples():
    w = row.word
    lemma = row.canonical_lemma
    freq = row.frequency_21215
    trans = row.chinese_translation
    
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

print(f"=== 🔬 PURE CAUSE 1 MORPHOLOGICAL AUDIT (Total: {len(df_c1)} words) ===")
print(f"1. Root ACTUALLY FOUND in NRC (词根在 NRC 里): {len(df_found)} 个词 ({len(df_found)/len(df_c1)*100:.2f}%) | Sum Freq: {df_found['freq'].sum():,}")
print(f"2. Root NOT in NRC (词根不在 NRC 里): {len(df_not_found)} 个词 ({len(df_not_found)/len(df_c1)*100:.2f}%) | Sum Freq: {df_not_found['freq'].sum():,}\n")

print("--- TOP 10 Cause 1 Words Whose Roots ARE in NRC ---")
print(df_found.head(10)[['word', 'canonical_lemma', 'root_found_in_nrc', 'nrc_tags', 'freq', 'chinese']].to_string(index=False))

print("\n--- TOP 10 Cause 1 Words Whose Roots ARE NOT in NRC ---")
print(df_not_found.head(10)[['word', 'canonical_lemma', 'freq', 'chinese']].to_string(index=False))
