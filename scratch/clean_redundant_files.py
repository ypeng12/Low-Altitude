#!/usr/bin/env python3
"""Remove redundant analysis files outside data/analyze/ to keep repository clean."""

import os
from pathlib import Path

redundant_files = [
    Path("data/derived_outputs/gold_emotion_nrc_mapped.xlsx"),
    Path("data/derived_outputs/gold_emotion_nrc_mapped.csv"),
    Path("data/derived_outputs/nrc_words_missed.xlsx"),
    Path("data/derived_outputs/nrc_words_missed.csv"),
    Path("data/derived_outputs/nrc_words_included.xlsx"),
    Path("data/derived_outputs/nrc_words_included.csv"),
    Path("data/derived_outputs/gold_emotion_categorized_by_nrc.xlsx"),
    Path("data/derived_outputs/gold_emotion_categorized_by_nrc.csv"),
    Path("data/derived_outputs/gold_emotion_lexicon_codebook_analysis.xlsx"),
    Path("data/derived_outputs/gold_emotion_lexicon_codebook_analysis.csv"),
    Path("data/cleaned_datasets/gold_emotion_lexicon_master.xlsx"),
    Path("data/cleaned_datasets/gold_emotion_lexicon_master.csv")
]

removed_count = 0
for f in redundant_files:
    if f.exists():
        f.unlink()
        print(f"Removed redundant file: {f}")
        removed_count += 1

print(f"\nSuccessfully cleaned up {removed_count} redundant files!")
print("Active analysis files are exclusively kept in: data/analyze/")
