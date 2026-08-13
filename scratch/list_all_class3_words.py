#!/usr/bin/env python3
"""List all exact words in Class 3 (Low-Altitude Air Tourism Domain-Specific Lexicon)."""

import pandas as pd
from pathlib import Path
from nrclex import NRCLex

gold_path = Path("data/analyze/gold_emotion_master.csv")
df_gold = pd.read_csv(gold_path)
nrc_dict = NRCLex().__lexicon__

c3_awe_keywords = ["breathtaking", "breathtakingly", "stunning", "stunningly", "scenic", "surreal", "awe", "awed", "sublime", "mesmerizing", "spellbinding"]
c3_risk_keywords = ["airsick", "claustrophobic", "claustrophobia", "jitters", "unnerving", "phobia"]

c3_words = []

for row in df_gold.itertuples():
    w = str(row.word).lower().strip()
    lemma = str(row.canonical_lemma).lower().strip()
    
    nrc_tags = nrc_dict.get(w, []) or nrc_dict.get(lemma, [])
    has_any = len(nrc_tags) > 0
    
    if not has_any:
        if w in c3_awe_keywords or lemma in c3_awe_keywords:
            c3_words.append({
                'sub_dimension': 'A. Aerial Visual Awe (高空视觉美学惊叹)',
                'word': w,
                'canonical_lemma': lemma,
                'freq': row.frequency_21215,
                'chinese': row.chinese_translation
            })
        elif w in c3_risk_keywords or lemma in c3_risk_keywords:
            c3_words.append({
                'sub_dimension': 'B. Somatic Flight Risk (低空飞行感知风险与躯体症状)',
                'word': w,
                'canonical_lemma': lemma,
                'freq': row.frequency_21215,
                'chinese': row.chinese_translation
            })

df_c3 = pd.DataFrame(c3_words).sort_values(['sub_dimension', 'freq'], ascending=[True, False]).reset_index(drop=True)
df_c3.index += 1

print(f"=== 📋 ALL CLASS 3 WORDS LIST (TOTAL: {len(df_c3)} WORD VARIANTS) ===")
print(f"Total Frequency Sum: {df_c3['freq'].sum():,} mentions\n")
print(df_c3.to_string(index=False))
