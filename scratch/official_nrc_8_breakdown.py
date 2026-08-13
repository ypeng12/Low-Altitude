#!/usr/bin/env python3
"""Count exact word counts for each of the 8 basic emotion categories in official NRC lexicon database."""

from collections import Counter
from nrclex import NRCLex

nrc_dict = NRCLex().__lexicon__
total_unique_words = len(nrc_dict)

nrc8_official_counts = Counter()
polarity_official_counts = Counter()

for word, tags in nrc_dict.items():
    for tag in tags:
        if tag in ('positive', 'negative'):
            polarity_official_counts[tag] += 1
        else:
            nrc8_official_counts[tag] += 1

print("=== 📚 Official NRC Emotion Lexicon Database Breakdown (N=6,468 Unique Words) ===")
print(f"Total Unique Words in NRC: {total_unique_words:,}")

print("\n--- 1. Official Word Count per NRC 8 Basic Emotion Category ---")
for cat in ['joy', 'trust', 'fear', 'sadness', 'anger', 'surprise', 'anticipation', 'disgust']:
    cnt = nrc8_official_counts[cat]
    pct = (cnt / total_unique_words) * 100
    print(f"  - {cat.upper():13s}: {cnt:5,d} words ({pct:5.2f}%)")

print("\n--- 2. Official Word Count for Positive / Negative Polarities ---")
for pol in ['positive', 'negative']:
    cnt = polarity_official_counts[pol]
    pct = (cnt / total_unique_words) * 100
    print(f"  - {pol.upper():13s}: {cnt:5,d} words ({pct:5.2f}%)")
