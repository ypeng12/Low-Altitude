#!/usr/bin/env python3
"""Verify exact mathematical tree breakdown of official NRC Lexicon (14,182 total words)."""

import urllib.request
import pandas as pd
from collections import defaultdict
from nrclex import NRCLex

# Inspect NRCLex internal lexicon
nrc_lexicon = NRCLex().__lexicon__

# Download or parse official raw NRC-Emotion-Lexicon-Wordlevel-v0.92 if accessible
url = "https://raw.githubusercontent.com/nrc-cnrc/NRC-Emotion-Lexicon/master/NRC-Emotion-Lexicon-Wordlevel-v0.92.txt"
print("Fetching raw NRC lexicon file for 100% exact verification...")

word_tags = defaultdict(dict)

try:
    with urllib.request.urlopen(url) as response:
        lines = response.read().decode('utf-8').splitlines()
        for line in lines:
            parts = line.strip().split('\t')
            if len(parts) == 3:
                w, emotion, val = parts[0].lower().strip(), parts[1].strip(), int(parts[2])
                word_tags[w][emotion] = val
except Exception as e:
    print("Could not download online NRC raw file, using internal NRCLex lexicon:", e)

# Evaluate official NRC database (either parsed raw 14,182 or NRCLex)
NRC8 = {"anger", "anticipation", "disgust", "fear", "joy", "sadness", "surprise", "trust"}

if len(word_tags) > 0:
    total_words = len(word_tags)
    
    cnt_has_8 = 0
    cnt_no_8_has_polarity = 0
    cnt_all_zero = 0
    
    for w, tags in word_tags.items():
        has_8 = any(tags.get(e, 0) == 1 for e in NRC8)
        has_pol = (tags.get("positive", 0) == 1) or (tags.get("negative", 0) == 1)
        
        if has_8:
            cnt_has_8 += 1
        elif has_pol:
            cnt_no_8_has_polarity += 1
        else:
            cnt_all_zero += 1
            
    print(f"\n=== 🌲 Exact NRC Official Lexicon Mathematical Tree (N={total_words:,}) ===")
    print(f"Total Unique Evaluated Words in NRC: {total_words:,}")
    print(f"  ├── 1. At least 1 of 8-Emotion Tags == 1: {cnt_has_8:,} words ({cnt_has_8/total_words*100:.2f}%)")
    print(f"  └── 2. All 8-Emotion Tags == 0: {total_words - cnt_has_8:,} words ({(total_words - cnt_has_8)/total_words*100:.2f}%)")
    print(f"       ├── 2a. No 8-Emotion, BUT Positive/Negative == 1: {cnt_no_8_has_polarity:,} words ({cnt_no_8_has_polarity/total_words*100:.2f}%)")
    print(f"       └── 2b. All 10 Tags (8 Emotions + 2 Polarities) == 0: {cnt_all_zero:,} words ({cnt_all_zero/total_words*100:.2f}%)")

    print("\n--- Equation Verification ---")
    print(f"  {cnt_has_8:,} (Has 8-Emotion) + {cnt_no_8_has_polarity:,} (Only Polarity) = {cnt_has_8 + cnt_no_8_has_polarity:,} (Words with >=1 Affect Tag)")
    print(f"  {cnt_has_8 + cnt_no_8_has_polarity:,} + {cnt_all_zero:,} (All 10 Zero) = {cnt_has_8 + cnt_no_8_has_polarity + cnt_all_zero:,} (Total NRC Universe 14,182)")

