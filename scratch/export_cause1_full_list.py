#!/usr/bin/env python3
"""Export full list of Cause 1 pure morphological words sorted by frequency."""

import pandas as pd
from pathlib import Path
from nrclex import NRCLex

gold_path = Path("data/analyze/gold_emotion_master.csv")
df_gold = pd.read_csv(gold_path)
nrc_dict = NRCLex().__lexicon__

c3_awe = {"breathtaking", "breathtakingly", "stunning", "stunningly", "sublime", "scenic", "surreal", "majestic", "panoramic", "spellbinding", "mesmerizing", "awe", "awed"}
c4_risk = {"claustrophobia", "claustrophobic", "jitters", "airsick", "phobia", "unnerving", "unnerved", "shaky", "dizzy", "dizziness", "nauseated", "nauseous", "seasick"}
c2_colloquial = {"great", "awesome", "fantastic", "incredible", "incredibly", "nice", "fabulous", "phenomenal", "unbeatable", "top-notch", "topnotch", "stellar", "prime", "primo", "epic", "mind-blowing"}

c1_participles = []
c1_adverbs_superlatives = []

for row in df_gold.itertuples():
    w = str(row.word).lower().strip()
    lemma = str(row.canonical_lemma).lower().strip()
    
    nrc_tags = nrc_dict.get(w, []) or nrc_dict.get(lemma, [])
    has_any = len(nrc_tags) > 0
    
    if not has_any:
        if w not in c3_awe and w not in c4_risk and w not in c2_colloquial:
            if w.endswith("ing") or w.endswith("ed"):
                c1_participles.append({
                    'word': w,
                    'canonical_lemma': lemma,
                    'frequency_21215': row.frequency_21215,
                    'chinese_translation': row.chinese_translation
                })
            elif w.endswith("ly") or w.endswith("est") or w.endswith("er"):
                c1_adverbs_superlatives.append({
                    'word': w,
                    'canonical_lemma': lemma,
                    'frequency_21215': row.frequency_21215,
                    'chinese_translation': row.chinese_translation
                })

df_part = pd.DataFrame(c1_participles).sort_values('frequency_21215', ascending=False)
df_adv = pd.DataFrame(c1_adverbs_superlatives).sort_values('frequency_21215', ascending=False)

print(f"=== 📋 CAUSE 1 PARTICIPLES (-ing / -ed): TOTAL {len(df_part)} WORDS ===")
print(df_part.to_string(index=False))

print(f"\n=== 📋 CAUSE 1 ADVERBS & SUPERLATIVES (-ly, -est, -er): TOTAL {len(df_adv)} WORDS ===")
print(df_adv.to_string(index=False))
